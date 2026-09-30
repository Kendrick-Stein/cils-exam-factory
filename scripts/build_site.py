#!/opt/anaconda3/bin/python3
"""Build the static CILS Exam Factory site."""

from __future__ import annotations

import argparse
import html
from html.parser import HTMLParser
import unicodedata
import os
import tempfile
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import markdown as markdown_lib
    import yaml
except ImportError:
    print("python3 -m pip install --user markdown pyyaml")
    raise SystemExit(2)


CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
DISCLAIMER = (
    "Materiale di esercitazione non ufficiale — non affiliato all'Università "
    "per Stranieri di Siena. Testi adattati dalle fonti citate."
)
LEVEL_ORDER = ["A1", "A2", "B1", "B2", "C1"]
MARKDOWN_EXTENSIONS = ["tables", "attr_list", "md_in_html", "sane_lists"]
SAFE_LEVEL_RE = re.compile(r"^[A-Za-z0-9_-]+$")
SESSION_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:-r([1-9]\d*))?$")
# answers.md ends with a pointer to the manifest; the rendered page replaces it
# with the actual source list, so the pointer paragraph is dropped.
FONTI_POINTER_RE = re.compile(r"<p><em>Fonti dei testi:[^<]*</em></p>\s*")
ISO_DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
# Manifests annotate publishers with internal corpus-selection notes
# ("(whitelist: …)", "— off-whitelist: …", "; fonte whitelisted"); those are
# pipeline provenance, not attribution, and stay out of the published credits.
PUBLISHER_NOTE_RES = [
    re.compile(r"\s*\([^()]*whitelist[^()]*\)", re.IGNORECASE),
    re.compile(r"\s*[—–-]\s*off-whitelist:.*$", re.IGNORECASE),
    re.compile(r"[;,]\s*fonte whitelisted\s*$", re.IGNORECASE),
]


class BuildError(Exception):
    """A user-facing build error."""


@dataclass(frozen=True)
class Paper:
    date: str
    level: str
    root: Path
    manifest: dict[str, Any]

    @property
    def title(self) -> str:
        return str(self.manifest.get("title") or f"{self.level} · Esercitazione")

    @property
    def session(self) -> str:
        return str(self.manifest.get("session") or self.date)

    @property
    def source_count(self) -> int:
        sources = self.manifest.get("sources") or []
        return len(sources) if isinstance(sources, list) else 0


def find_chrome() -> Path:
    """Use an explicit executable override, then macOS or PATH discovery."""
    override = os.environ.get("CILS_CHROME")
    if override:
        candidate = Path(override).expanduser()
        if not candidate.is_file() or not os.access(candidate, os.X_OK):
            raise BuildError(f"CILS_CHROME is not an executable file: {candidate}")
        return candidate
    if CHROME.is_file() and os.access(CHROME, os.X_OK):
        return CHROME
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        executable = shutil.which(name)
        if executable:
            return Path(executable)
    raise BuildError("Chrome/Chromium not found; install a supported browser or set CILS_CHROME. "
                     "Use --no-pdf only for a preview, never publication.")


def valid_pdf(path: Path) -> bool:
    try:
        with path.open("rb") as stream:
            return stream.read(5) == b"%PDF-"
    except OSError:
        return False


class PdfPrinter:
    def __init__(self, force: bool) -> None:
        self.force = force

    def render(self, html_path: Path, pdf_path: Path, source_paths: list[Path]) -> None:
        if valid_pdf(pdf_path) and not self.force:
            newest = max(
                (path.stat().st_mtime for path in source_paths if path.exists()),
                default=0.0,
            )
            if pdf_path.stat().st_mtime >= newest:
                return

        chrome = find_chrome()
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        # Fresh output prevents a stale PDF from disguising a failed print.
        # A private browser profile avoids conflicts with an interactive browser.
        with tempfile.TemporaryDirectory(prefix="cils-print-", dir=pdf_path.parent) as tmp:
            output = Path(tmp) / "output.pdf"
            cmd = [
                str(chrome), "--headless=new", "--disable-gpu",
                "--no-pdf-header-footer",
                f"--user-data-dir={Path(tmp) / 'profile'}",
                f"--print-to-pdf={output.resolve()}",
                html_path.resolve().as_uri(),
            ]
            try:
                completed = subprocess.run(cmd, text=True, capture_output=True,
                                           check=False, timeout=120)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise BuildError(f"Chrome could not print {html_path}: {exc}") from exc
            if completed.returncode != 0:
                detail = (completed.stderr or completed.stdout or "").strip()
                raise BuildError(f"Chrome failed for {html_path} (exit {completed.returncode}): {detail}")
            if not valid_pdf(output):
                raise BuildError(f"Chrome did not produce a valid PDF for {html_path}")
            output.replace(pdf_path)


def expand_blank_writing_tables(body: str) -> str:
    """Give empty Markdown writing boxes real block width in MuPDF.

    MuPDF shrink-wraps an otherwise empty table. Only a single empty header
    and a single blank body cell are converted; content tables are untouched.
    Preserve the original number of blank lines rather than inventing space.
    """
    def replace(match: re.Match) -> str:
        table = match.group(0)
        headers = re.findall(r"<th\b[^>]*>(.*?)</th>", table, re.S | re.I)
        cells = re.findall(r"<td\b[^>]*>(.*?)</td>", table, re.S | re.I)
        if len(headers) != 1 or len(cells) != 1:
            return table
        text = html.unescape(re.sub(r"<[^>]+>", "", headers[0] + cells[0]))
        if text.strip():
            return table
        lines = len(re.findall(r"<br\s*/?>", cells[0], re.I)) + 1
        return '<div class="writing-space">' + (
            '<p class="writing-line">&#160;</p>' * lines
        ) + '</div>'
    return re.sub(r"<table\b[^>]*>.*?</table>", replace, body, flags=re.S | re.I)


class PrintableBlocks(HTMLParser):
    """Split generated body HTML at top-level boundaries, retaining text nodes."""
    VOID = {"br", "hr", "img", "meta", "input", "link"}

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.depth, self.current, self.blocks, self.text_nodes = 0, [], [], []

    def flush(self):
        if self.current:
            self.blocks.append("".join(self.current))
            self.current = []

    def handle_starttag(self, tag, attrs):
        self.current.append(self.get_starttag_text())
        if tag not in self.VOID:
            self.depth += 1
        if not self.depth:
            self.flush()

    def handle_endtag(self, tag):
        self.current.append(f"</{tag}>")
        self.depth -= 1
        if not self.depth:
            self.flush()

    def handle_startendtag(self, tag, attrs):
        self.current.append(self.get_starttag_text())
        if not self.depth:
            self.flush()

    def handle_data(self, data):
        if self.depth or data.strip():
            self.current.append(data)
        self.text_nodes.append(data)

    def handle_entityref(self, name):
        self.current.append(f"&{name};")
        self.text_nodes.append(html.unescape(f"&{name};"))

    def handle_charref(self, name):
        self.current.append(f"&#{name};")
        self.text_nodes.append(html.unescape(f"&#{name};"))


def group_writing_tasks(blocks: list[str]) -> list[str]:
    """Keep each writing prompt and its answer lines in one placeable Story."""
    grouped, index = [], 0
    while index < len(blocks):
        if re.match(r"<h[23]\b[^>]*>Produzione scritta.*Prova n\.", blocks[index]):
            end = index + 1
            while end < len(blocks) and not re.match(r"<h[123]\b", blocks[end]):
                if blocks[end].startswith('<div class="writing-space">'):
                    grouped.append('<section class="writing-task">' +
                                   "".join(blocks[index:end+1]) + '</section>')
                    index = end + 1
                    break
                end += 1
            else:
                grouped.append(blocks[index])
                index += 1
            continue
        grouped.append(blocks[index])
        index += 1
    return grouped


def bounded_table_blocks(block: str):
    """Avoid MuPDF's lossy table continuation by repeating headers in small groups."""
    if not re.match(r"<table\b", block):
        return [block]
    header = re.search(r"<thead\b[^>]*>.*?</thead>", block, re.S)
    body = re.search(r"<tbody\b[^>]*>(.*?)</tbody>", block, re.S)
    if not body:
        return [block]
    rows = re.findall(r"<tr\b[^>]*>.*?</tr>", body.group(1), re.S)
    opening = block[:block.index(">")+1]
    return [opening + (header.group(0) if header else "") + "<tbody>" +
            "".join(rows[i:i+8]) + "</tbody></table>" for i in range(0,len(rows),8)] or [block]


def normalized_pdf_text(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKC", text) if c.isalnum())


def require_pdf_coverage(document, source_nodes, source):
    # Remove footer numbering before joining page text, so a paragraph split
    # over pages still compares continuously. NFKC expands typography ligatures.
    actual = normalized_pdf_text("".join(
        page.get_text(clip=(0, 0, 595, 800)) for page in document
    ))
    missing = [node for node in source_nodes
               if (normalized := normalized_pdf_text(node)) and normalized not in actual]
    if missing:
        preview = "; ".join(repr(node[:90]) for node in missing[:3])
        raise BuildError(f"PDF text coverage failed for {source}: {len(missing)} missing source text nodes: {preview}")


def repair_story_tounicode(document):
    """Correct MuPDF's non-BMP scalar values in direct ToUnicode mappings."""
    def utf16_mapping(match):
        codepoint = int(match[2], 16)
        if not 0x10000 <= codepoint <= 0x10FFFF:
            return match[0]
        encoded = chr(codepoint).encode("utf-16-be").hex().encode("ascii")
        return match[1] + b"<" + encoded + b">" + match[3]

    for xref in range(1, document.xref_length()):
        kind, reference = document.xref_get_key(xref, "ToUnicode")
        if kind != "xref":
            continue
        cmap_xref = int(reference.split()[0])
        original = document.xref_stream(cmap_xref)
        # Only two-token bfchar entries; preserve ranges and valid UTF-16.
        corrected = re.sub(
            rb"(?m)^([ \t]*<[0-9a-fA-F]{4}>[ \t]+)<([0-9a-fA-F]{5,6})>([ \t]*$)",
            utf16_mapping, original,
        )
        if corrected != original:
            document.update_stream(cmap_xref, corrected)


class MuPdfPrinter:
    """Browser-free printable layout with MuPDF's bundled CJK fonts."""
    def render(self, html_path: Path, pdf_path: Path, source_paths: list[Path]) -> None:
        try:
            import pymupdf as fitz
        except ImportError as exc:
            raise BuildError("MuPDF renderer requires PyMuPDF; install requirements-pdf-mupdf.txt") from exc
        source, manifest_path = source_paths
        manifest = load_yaml(manifest_path)
        paper = Paper(str(manifest["session"]), str(manifest["level"]), source.parent, manifest)
        _, body = render_markdown(source)
        body = expand_blank_writing_tables(body)
        if source.stem == "answers":
            body += render_fonti(paper)
        css = Path(__file__).with_name("assets").joinpath("mupdf.css").read_text(encoding="utf-8")
        blocks = PrintableBlocks()
        blocks.feed(body)
        blocks.flush()
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with tempfile.TemporaryDirectory(prefix="cils-mupdf-", dir=pdf_path.parent) as tmp:
                raw, final = Path(tmp)/"raw.pdf", Path(tmp)/"final.pdf"
                page_count, y, device = 0, 48, None
                writer = fitz.DocumentWriter(str(raw))
                def new_page():
                    nonlocal page_count, y, device
                    if device is not None:
                        writer.end_page()
                    page_count += 1
                    if page_count > 100:
                        raise BuildError("MuPDF pagination exceeded 100 pages; check oversized content")
                    device = writer.begin_page(fitz.Rect(0, 0, 595, 842))
                    y = 48
                try:
                    for block in [part for original in group_writing_tasks(blocks.blocks) for part in bounded_table_blocks(original)]:
                        # A monolithic Story can silently skip prose following a
                        # split table. Isolate each top-level block and retain an
                        # explicit page cursor, then verify every source text node.
                        if re.match(r"<hr\b", block) and y > 690:
                            continue  # Do not create a page containing only a separator.
                        section_break = source.stem == "paper" and re.match(r"<h1[^>]*>Test di", block)
                        if device is None or y > 720 or (re.match(r"<h[123]", block) and y > 660) or (section_break and y > 48):
                            new_page()
                        story = fitz.Story(html=block, user_css=css)
                        while True:
                            more, filled = story.place(fitz.Rect(51, y, 544, 785))
                            if more and block.startswith('<section class="writing-task">') and y > 48:
                                # Move the entire prompt and writing space before
                                # drawing; only oversized tasks may span pages.
                                story.reset()
                                new_page()
                                more, filled = story.place(fitz.Rect(51, y, 544, 785))
                            if more and re.match(r"<table\b", block):
                                # Never draw a partially placed table. Restart this
                                # bounded group on a fresh page or fail explicitly.
                                if y <= 48:
                                    raise BuildError("A table group exceeds one page; split its rows/text before publication")
                                story.reset()
                                new_page()
                                more, filled = story.place(fitz.Rect(51, y, 544, 785))
                                if more:
                                    raise BuildError("A table group exceeds one page; split its rows/text before publication")
                            story.draw(device)
                            if not more:
                                y = max(y + 1, filled[3])
                                break
                            new_page()
                    if device is not None:
                        writer.end_page()
                        device = None
                finally:
                    writer.close()
                with fitz.open(raw) as document:
                    repair_story_tounicode(document)
                    if not len(document):
                        raise BuildError(f"MuPDF produced no pages for {source}")
                    for number, page in enumerate(document):
                        page.insert_text((285, 813), f"{number+1} / {len(document)}",
                                         fontsize=9, color=(.3, .3, .3))
                    require_pdf_coverage(document, blocks.text_nodes, source)
                    # Use MuPDF's native subsetter, without the fontTools fallback.
                    document.subset_fonts()
                    document.save(final, garbage=4, deflate=True)
                with fitz.open(final) as document:
                    if not len(document) or any(not page.get_text().strip() for page in document):
                        raise BuildError(f"MuPDF produced empty pages for {source}")
                    require_pdf_coverage(document, blocks.text_nodes, source)
                final.replace(pdf_path)
        except BuildError:
            raise
        except Exception as exc:
            raise BuildError(f"MuPDF could not render {source}: {exc}") from exc


def warn(message: str) -> None:
    print(f"WARNING: {message}", file=sys.stderr)


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BuildError(f"malformed YAML in {path}: {exc}") from exc
    except OSError as exc:
        raise BuildError(f"cannot read {path}: {exc}") from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise BuildError(f"malformed YAML in {path}: expected a mapping at top level")
    return data


def split_front_matter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            raw_front_matter = "".join(lines[1:index])
            body = "".join(lines[index + 1 :])
            try:
                front_matter = yaml.safe_load(raw_front_matter) or {}
            except yaml.YAMLError as exc:
                raise BuildError(f"malformed YAML front matter in {path}: {exc}") from exc
            if not isinstance(front_matter, dict):
                raise BuildError(f"malformed YAML front matter in {path}: expected a mapping")
            return front_matter, body.lstrip("\n")

    raise BuildError(f"unterminated YAML front matter in {path}")


def scan_papers(papers_root: Path) -> list[Paper]:
    if not papers_root.exists():
        return []

    papers: list[Paper] = []
    for manifest_path in sorted(papers_root.glob("*/*/manifest.yaml")):
        relative_parts = manifest_path.relative_to(papers_root).parts
        if any(part.startswith("_") for part in relative_parts):
            continue

        manifest = load_yaml(manifest_path)
        if manifest.get("status") != "published":
            continue
        validate_publish_gate(manifest_path, manifest)

        paper_root = manifest_path.parent
        paper_md = paper_root / "paper.md"
        answers_md = paper_root / "answers.md"
        if not paper_md.exists():
            raise BuildError(f"missing paper.md for published manifest: {manifest_path}")
        if not answers_md.exists():
            raise BuildError(f"missing answers.md for published manifest: {manifest_path}")

        date, level, _ = relative_parts
        if not SAFE_LEVEL_RE.fullmatch(level):
            raise BuildError(f"unsafe level directory in published paper path: {manifest_path}")
        manifest_level = str(manifest.get("level") or level)
        if not SAFE_LEVEL_RE.fullmatch(manifest_level):
            raise BuildError(f"unsafe level in published manifest {manifest_path}: {manifest_level!r}")
        if manifest_level != level:
            raise BuildError(f"level mismatch in published manifest {manifest_path}: {manifest_level!r} != {level!r}")
        papers.append(Paper(date=date, level=manifest_level, root=paper_root, manifest=manifest))

    return papers


def validate_publish_gate(manifest_path: Path, manifest: dict[str, Any]) -> None:
    validation = manifest.get("validation")
    if not isinstance(validation, dict):
        raise BuildError(f"publish gate failed for {manifest_path}: missing validation block")

    result = validation.get("result")
    if result != "pass":
        raise BuildError(f"publish gate failed for {manifest_path}: validation result is not pass")

    objective_items = validation.get("objective_items", validation.get("objective_total"))
    final_agreement = validation.get("final_agreement", validation.get("blind_matched"))
    if objective_items is None or final_agreement is None:
        agreement = str(validation.get("agreement") or validation.get("blind_agreement") or "")
        if "/" not in agreement:
            raise BuildError(f"publish gate failed for {manifest_path}: missing blind agreement")
        final_agreement, objective_items = agreement.split("/", 1)

    try:
        objective_count = int(objective_items)
        matched_count = int(final_agreement)
    except (TypeError, ValueError) as exc:
        raise BuildError(f"publish gate failed for {manifest_path}: malformed blind agreement") from exc
    if objective_count <= 0 or matched_count != objective_count:
        raise BuildError(f"publish gate failed for {manifest_path}: blind agreement is not 100%")

    flags = validation.get("flags", 0)
    flag_count = len(flags) if isinstance(flags, list) else int(flags or 0)
    if flag_count != 0:
        raise BuildError(f"publish gate failed for {manifest_path}: validation flags remain open")

    mismatches = validation.get("mismatches", 0)
    mismatch_count = len(mismatches) if isinstance(mismatches, list) else int(mismatches or 0)
    if mismatch_count != 0:
        raise BuildError(f"publish gate failed for {manifest_path}: validation mismatches remain open")

    pipeline = manifest.get("pipeline")
    if not isinstance(pipeline, dict):
        raise BuildError(f"publish gate failed for {manifest_path}: missing pipeline block")
    stages = pipeline.get("stages")
    if not isinstance(stages, list):
        raise BuildError(f"publish gate failed for {manifest_path}: missing pipeline stages")
    format_results = [
        str(stage.get("result", "")).lower()
        for stage in stages
        if isinstance(stage, dict) and stage.get("stage") == "format_audit"
    ]
    quality_results = [
        str(stage.get("result", "")).lower()
        for stage in stages
        if isinstance(stage, dict) and stage.get("stage") == "quality_audit"
    ]
    quality_required = isinstance(manifest.get("quality"), dict)
    if not quality_results and quality_required:
        raise BuildError(f"publish gate failed for {manifest_path}: missing quality audit")
    if quality_results and quality_results[-1] != "pass":
        raise BuildError(f"publish gate failed for {manifest_path}: quality audit is not pass")
    if not format_results:
        raise BuildError(f"publish gate failed for {manifest_path}: missing format audit")
    if format_results[-1] != "pass":
        raise BuildError(f"publish gate failed for {manifest_path}: format audit is not pass")


def level_sort_key(paper: Paper) -> tuple[int, str]:
    try:
        rank = LEVEL_ORDER.index(paper.level)
    except ValueError:
        rank = len(LEVEL_ORDER)
    return rank, paper.level


def badge(level: str) -> str:
    safe_level = html.escape(level, quote=True)
    return f'<span class="badge badge-{safe_level}">{safe_level}</span>'


def slug(value: str) -> str:
    return "".join(char if char.isalnum() or char == "-" else "-" for char in value).strip("-").lower()


def render_markdown(path: Path) -> tuple[dict[str, Any], str]:
    front_matter, body = split_front_matter(path)
    parser = markdown_lib.Markdown(extensions=MARKDOWN_EXTENSIONS)
    # Python-Markdown has no built-in strikethrough extension. Parse worked
    # examples after code/escapes/links, but before emphasis, in both renderers.
    parser.ESCAPED_CHARS.append("~")
    parser.inlinePatterns.register(
        markdown_lib.inlinepatterns.SimpleTagInlineProcessor(
            r"(?<!~)(~~)(?!~)(?=\S)(.+?)(?<=\S)(?<!~)\1(?!~)", "del"
        ),
        "strikethrough", 65,
    )
    rendered = parser.convert(body)
    return front_matter, rendered


def format_date_it(value: str) -> str:
    match = ISO_DATE_RE.fullmatch(value.strip())
    if not match:
        return value.strip()
    year, month, day = match.groups()
    return f"{day}/{month}/{year}"


def normalize_used_in(value: str) -> str:
    """Map the manifest's heterogeneous used_in values (labels, slugs like
    'lettura.prova1', shorthands like 'L3.2' or 'S1') to the official label."""
    text = value.strip()
    lowered = text.lower()
    if lowered.startswith(("comprensione", "lettura")) or re.match(r"l\d", lowered):
        section = "Comprensione della lettura"
    elif lowered.startswith(("analisi", "strutture")) or re.match(r"s\d", lowered):
        section = "Analisi delle strutture"
    else:
        return text
    match = re.search(r"\d+", text)
    if not match:
        return text
    return f"{section}, Prova n. {match.group(0)}"


def clean_credit(value: str) -> str:
    text = value
    for pattern in PUBLISHER_NOTE_RES:
        text = pattern.sub("", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    return re.sub(r"\s{2,}", " ", text).strip(" ,;")


def used_in_labels(raw: Any) -> list[str]:
    values = raw if isinstance(raw, list) else [raw]
    labels: list[str] = []
    for value in values:
        if value is None:
            continue
        label = normalize_used_in(str(value))
        if label and label not in labels:
            labels.append(label)
    return labels


def render_fonti(paper: Paper) -> str:
    sources = paper.manifest.get("sources")
    if not isinstance(sources, list):
        return ""

    items: list[str] = []
    for source in sources:
        if not isinstance(source, dict):
            continue
        detail_parts = [clean_credit(str(source.get(key) or "")) for key in ("title", "publisher")]
        detail = html.escape(", ".join(part for part in detail_parts if part))
        url = str(source.get("url") or "").strip()
        if url:
            detail += f', <a href="{html.escape(url, quote=True)}" rel="noopener">{html.escape(url)}</a>'
        accessed = format_date_it(str(source.get("accessed") or ""))
        if accessed:
            detail += f", consultato il {html.escape(accessed)}"
        labels = "; ".join(used_in_labels(source.get("used_in")))
        prova = f"<strong>{html.escape(labels)}</strong> — " if labels else ""
        items.append(f"  <li>{prova}Testo adattato da: {detail}</li>")

    if not items:
        return ""
    joined = "\n".join(items)
    return f"""<section class="fonti">
<h2>Fonti dei testi</h2>
<p>Ogni testo del fascicolo è l'adattamento di un testo italiano autentico e pubblicato. Tagli e semplificazioni sono documentati nel manifest della sessione; i diritti sui testi originali restano ai rispettivi autori.</p>
<ol>
{joined}
</ol>
</section>"""


def render_page(path: Path, paper: Paper, kind: str) -> str:
    front_matter, content = render_markdown(path)
    level = str(front_matter.get("level") or paper.level)
    level_name = str(front_matter.get("level_name") or paper.title)
    session = str(front_matter.get("session") or paper.session)
    kind_label = "Fascicolo" if kind == "paper" else "Chiavi e commenti"
    title = f"{kind_label} · {level} · {session}"
    counterpart_label = "Apri chiavi" if kind == "paper" else "Apri fascicolo"
    counterpart_href = "answers.html" if kind == "paper" else "paper.html"

    if kind == "paper":
        # Wrap the booklet cover (everything before the answer-sheet example,
        # or before the first test for pre-2026-07-08-r2 papers without one)
        # so print styles can render it as a full standalone cover page.
        marker = content.find("<h2>ESEMPIO DI FOGLIO")
        if marker == -1:
            marker = content.find("<h1>", 1)
        if marker != -1:
            content = f'<section class="cover">\n{content[:marker]}</section>\n{content[marker:]}'

    if kind == "answers":
        fonti = render_fonti(paper)
        if fonti:
            content = FONTI_POINTER_RE.sub("", content)
            content = f"{content}\n{fonti}"

    return f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="../../../assets/paper.css">
</head>
<body class="kind-{html.escape(kind, quote=True)}">
  <header class="paper-header">
    <div class="paper-header-inner">
      <div>
        <div class="site-name">CILS Exam Factory · esercitazione non ufficiale</div>
        <div class="paper-meta">
          {badge(level)}
          <span>{html.escape(level_name)}</span>
          <span>Sessione {html.escape(session)}</span>
          <span>{html.escape(kind_label)}</span>
        </div>
      </div>
      <nav class="paper-actions" aria-label="Azioni documento">
        <a href="../../../index.html">Torna all'indice</a>
        <a href="{html.escape(counterpart_href, quote=True)}">{html.escape(counterpart_label)}</a>
        <a href="{html.escape(kind, quote=True)}.md">Scarica Markdown</a>
      </nav>
    </div>
  </header>
  <main class="paper">
{content}
  </main>
  <footer class="paper-footer">
    <p>{html.escape(DISCLAIMER)}</p>
  </footer>
</body>
</html>
"""


def copy_assets(out_root: Path) -> None:
    source_dir = Path(__file__).resolve().parent / "assets"
    target_dir = out_root / "assets"
    target_dir.mkdir(parents=True, exist_ok=True)
    for pattern in ("*.css", "*.js", "*.svg", "*.png"):
        for asset in sorted(source_dir.glob(pattern)):
            shutil.copy2(asset, target_dir / asset.name)


def build_paper_outputs(paper: Paper, out_root: Path, pdf_printer: PdfPrinter | MuPdfPrinter | None) -> None:
    out_dir = out_root / "papers" / paper.date / paper.level
    out_dir.mkdir(parents=True, exist_ok=True)

    for kind in ("paper", "answers"):
        md_source = paper.root / f"{kind}.md"
        html_target = out_dir / f"{kind}.html"
        pdf_target = out_dir / f"{kind}.pdf"

        # The site publishes PDFs only; HTML is a render intermediate (written
        # next to the PDF so relative asset links resolve) and md stays in papers/.
        html_target.write_text(render_page(md_source, paper, kind), encoding="utf-8")
        if pdf_printer is not None:
            pdf_printer.render(html_target, pdf_target, [md_source, paper.root / "manifest.yaml"])
        html_target.unlink(missing_ok=True)
        (out_dir / f"{kind}.md").unlink(missing_ok=True)


SITE_URL = "https://kendrick-stein.github.io/cils-exam-factory/"
GITHUB_URL = "https://github.com/Kendrick-Stein/cils-exam-factory"

LEVEL_META = {
    "A1": ("CILS A1", "Primi passi in italiano: messaggi brevi, avvisi pubblici e descrizioni essenziali."),
    "A2": ("CILS A2", "Vita quotidiana: annunci, istruzioni, ricette e brevi articoli di servizio."),
    "B1": ("CILS UNO", "Verso l'autonomia: cronaca, testi regolativi, racconti e interviste."),
    "B2": ("CILS DUE", "Padronanza operativa: articoli di approfondimento, divulgazione e opinione."),
    "C1": ("CILS TRE", "Competenza avanzata: saggistica, letteratura e testi istituzionali."),
}

METODO_STEPS = [
    ("Raccolta delle fonti",
     "Testi italiani autentici e pubblicati — agenzie di stampa, enti pubblici, letteratura di pubblico dominio — selezionati per genere, livello e banda di parole. Nessuna frase è inventata."),
    ("Adattamento al formato CILS",
     "Ogni testo viene ridotto alla banda del livello e montato sui template dei quaderni d'esame, con consegne e punteggi nel formato ufficiale."),
    ("Generazione degli esercizi",
     "Gli item nascono una prova alla volta: comprensione della lettura, analisi delle strutture, produzione scritta e produzione orale, con tracce e testi modello da memorizzare."),
    ("Risoluzione e verifica alla cieca",
     "Un risolutore indipendente riceve soltanto il fascicolo, senza chiavi né fonti: si pubblica solo con il 100% di accordo sugli item oggettivi e zero ambiguità."),
    ("Audit e pubblicazione",
     "Controlli deterministici su struttura, lunghezze, riuso e attribuzioni. Poi il fascicolo entra nell'archivio e non cambia più: le correzioni diventano nuove sessioni."),
]


def pdf_link(out_root: Path, base: str, stem: str, label: str, classes: str) -> str:
    href = f"{base}/{stem}.pdf"
    if not (out_root / href).exists():
        return ""
    return f'<a class="{classes}" href="{html.escape(href, quote=True)}">{html.escape(label)}</a>'


def level_chip(level: str) -> str:
    safe = html.escape(level, quote=True)
    return f'<span class="chip chip-{safe}">{safe}</span>'


def render_topbar() -> str:
    return f"""  <a class="skip-link" href="#contenuto">Salta al contenuto</a>
  <header class="topbar" id="top">
    <div class="topbar-inner">
      <a class="brand" href="#top" aria-label="CILS Exam Factory — torna all'inizio">
        <span class="brand-mark" aria-hidden="true">CF</span>
        <span class="brand-name">CILS <em>Exam Factory</em></span>
      </a>
      <nav class="topnav" id="topnav" aria-label="Sezioni della pagina">
        <a href="#livelli">Livelli</a>
        <a href="#sessione">Ultima sessione</a>
        <a href="#archivio">Archivio</a>
        <a href="#metodo">Metodo</a>
        <a href="#informazioni">Informazioni</a>
        <a class="topnav-github" href="{GITHUB_URL}" rel="noopener">GitHub</a>
      </nav>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="topnav">Menu</button>
    </div>
  </header>"""


def render_hero(total_papers: int, total_sessions: int, total_sources: int, latest_session: str) -> str:
    return f"""    <section class="hero">
      <div class="hero-inner">
        <div class="hero-copy">
          <p class="kicker">Archivio di esercitazioni · A1–C1 · non ufficiale</p>
          <h1>Esercitazioni CILS costruite da testi italiani autentici.</h1>
          <p class="hero-sub">Practice papers from A1 to C1, with verified sources, solutions and editorial notes.</p>
          <div class="hero-actions">
            <a class="btn btn-primary" href="#livelli">Trova il tuo livello</a>
            <a class="btn btn-ghost" href="#archivio">Esplora le sessioni</a>
          </div>
          <div class="hero-stats" role="group" aria-label="Statistiche del progetto">
            <div><p class="stat-num" data-count="{total_papers}">{total_papers}</p><p class="stat-label">fascicoli</p></div>
            <div><p class="stat-num" data-count="{total_sessions}">{total_sessions}</p><p class="stat-label">sessioni</p></div>
            <div><p class="stat-num" data-count="{total_sources}">{total_sources}</p><p class="stat-label">fonti autentiche</p></div>
          </div>
        </div>
        <div class="hero-visual" aria-hidden="true">
          <div class="sheet-stack" id="sheet-stack">
            <div class="sheet sheet-chiavi" data-depth="0.4">
              <span class="sheet-tag">Chiavi e commenti</span>
              <span class="sheet-grid"></span>
            </div>
            <div class="sheet sheet-fonte" data-depth="0.7">
              <span class="sheet-tag sheet-tag-red">Fonte verificata</span>
              <span class="sheet-lines"></span>
            </div>
            <div class="sheet sheet-fascicolo" data-depth="1">
              <span class="cover-rule"></span>
              <span class="cover-title">CILS — Certificazione di Italiano come Lingua Straniera</span>
              <span class="cover-rule"></span>
              <span class="cover-sub">Quaderno di esame</span>
              <span class="cover-level">Livello UNO — B1</span>
              <span class="cover-session">Sessione {html.escape(latest_session)}</span>
              <span class="cover-note">Esercitazione non ufficiale<br>da testi autentici</span>
            </div>
            <div class="stamp" data-depth="1.25"><span>Verificato<br>alla cieca<br>·100%·</span></div>
          </div>
        </div>
      </div>
    </section>"""


def render_livelli(level_counts: dict[str, int]) -> str:
    cards: list[str] = []
    for level in LEVEL_ORDER:
        cils_name, desc = LEVEL_META[level]
        count = level_counts.get(level, 0)
        plural = "fascicoli" if count != 1 else "fascicolo"
        cards.append(f"""        <article class="level-card reveal">
          <p class="level-code">{html.escape(level)}</p>
          <p class="level-cils">{html.escape(cils_name)}</p>
          <p class="level-desc">{html.escape(desc)}</p>
          <p class="level-count"><span class="num">{count}</span> {plural} disponibili</p>
          <a class="btn btn-small btn-ghost" href="?level={html.escape(level, quote=True)}#archivio" data-level-link="{html.escape(level, quote=True)}">Inizia<span class="visually-hidden"> con il livello {html.escape(level)}</span></a>
        </article>""")
    joined = "\n".join(cards)
    return f"""    <section class="section" id="livelli">
      <header class="section-head reveal">
        <p class="kicker">Livelli</p>
        <h2>Scegli il tuo livello</h2>
        <p class="section-sub">Cinque livelli del Quadro comune europeo, ognuno sul modello del quaderno d'esame CILS corrispondente.</p>
      </header>
      <div class="level-grid">
{joined}
      </div>
    </section>"""


def render_ultima(session: str, papers: list[Paper], out_root: Path) -> str:
    cards: list[str] = []
    for paper in sorted(papers, key=level_sort_key):
        base = f"papers/{paper.date}/{paper.level}"
        cils_name, _ = LEVEL_META.get(paper.level, (paper.level, ""))
        plural = "testi autentici" if paper.source_count != 1 else "testo autentico"
        fascicolo = pdf_link(out_root, base, "paper", "Apri il fascicolo", "btn btn-primary")
        chiavi = pdf_link(out_root, base, "answers", "Chiavi e commenti", "link-quiet")
        cards.append(f"""        <article class="paper-card reveal">
          <p class="paper-card-head">{level_chip(paper.level)}<span class="paper-card-name">{html.escape(cils_name)}</span></p>
          <p class="paper-card-sources"><span class="num">{paper.source_count}</span> {plural}</p>
          <p class="paper-card-actions">{fascicolo}</p>
          <p class="paper-card-secondary">{chiavi}</p>
        </article>""")
    joined = "\n".join(cards)
    missing = [level for level in LEVEL_ORDER if level not in {p.level for p in papers}]
    availability = ""
    if missing:
        availability = (f"<p class=\"section-sub\">{html.escape(', '.join(missing))}: "
                        "per questa data non è disponibile un fascicolo che abbia superato tutti i controlli. "
                        "Le edizioni precedenti restano nell'<a href=\"#archivio\">archivio</a>.</p>")
    noun = "fascicolo pubblicato" if len(papers) == 1 else "fascicoli pubblicati"
    return f"""    <section class="section section-alt" id="sessione">
      <header class="section-head reveal">
        <p class="kicker">Ultima sessione</p>
        <h2><span class="num">{html.escape(session)}</span></h2>
        <p class="section-sub">{len(papers)} {noun} dopo verifica alla cieca e audit editoriale. Per ogni livello è mostrata la versione più recente della giornata. Le sessioni precedenti sono nell'<a href="#archivio">archivio</a>.</p>
      </header>
      {availability}
      <p class="section-sub">C2 non è incluso nella configurazione attuale della raccolta (A1–C1).</p>
      <div class="session-grid">
{joined}
      </div>
    </section>"""


def render_metodo() -> str:
    steps: list[str] = []
    for index, (title, body) in enumerate(METODO_STEPS, start=1):
        steps.append(f"""          <li class="metodo-step reveal">
            <p class="step-no" aria-hidden="true">{index:02d}</p>
            <div><h3>{html.escape(title)}</h3>
            <p>{html.escape(body)}</p></div>
          </li>""")
    joined = "\n".join(steps)
    return f"""    <section class="section" id="metodo">
      <div class="metodo-grid">
        <header class="metodo-head reveal">
          <p class="kicker">Metodo</p>
          <h2>Come nasce un fascicolo</h2>
          <p class="section-sub">Una filiera editoriale in cinque passaggi, dal testo autentico al PDF pubblicato. Tutto il processo è documentato nel repository.</p>
        </header>
        <ol class="metodo-steps">
{joined}
        </ol>
      </div>
    </section>"""


def render_archivio(
    sessions: list[str],
    papers_by_date: dict[str, list[Paper]],
    out_root: Path,
    latest_session: str,
    years: list[str],
) -> str:
    level_buttons = ['<button class="filter-btn" type="button" data-level-filter="tutti" aria-pressed="true">Tutti</button>']
    for level in LEVEL_ORDER:
        safe = html.escape(level, quote=True)
        level_buttons.append(
            f'<button class="filter-btn" type="button" data-level-filter="{safe}" aria-pressed="false">{safe}</button>'
        )
    year_options = ['<option value="tutti">Tutti gli anni</option>'] + [
        f'<option value="{html.escape(year, quote=True)}">{html.escape(year)}</option>' for year in years
    ]

    blocks: list[str] = []
    for session in sessions:
        papers = sorted(papers_by_date[session], key=level_sort_key)
        levels = " ".join(paper.level for paper in papers)
        year = session[:4]
        chips = "".join(level_chip(paper.level) for paper in papers)
        latest_tag = '<span class="arch-tag">ultima</span>' if session == latest_session else ""
        plural = "fascicoli" if len(papers) != 1 else "fascicolo"
        rows: list[str] = []
        for paper in papers:
            base = f"papers/{paper.date}/{paper.level}"
            cils_name, _ = LEVEL_META.get(paper.level, (paper.level, ""))
            fascicolo = pdf_link(out_root, base, "paper", "Fascicolo", "btn btn-primary btn-small")
            chiavi = pdf_link(out_root, base, "answers", "Chiavi e commenti", "link-quiet")
            rows.append(f"""            <li class="arch-row" data-level="{html.escape(paper.level, quote=True)}">
              {level_chip(paper.level)}
              <span class="arch-row-name">{html.escape(cils_name)}<span class="arch-row-sub"><span class="num">{paper.source_count}</span> testi autentici</span></span>
              <span class="arch-row-actions">{fascicolo}{chiavi}</span>
            </li>""")
        rows_joined = "\n".join(rows)
        blocks.append(f"""        <details class="arch-session" id="sessione-{html.escape(slug(session), quote=True)}" data-session="{html.escape(session, quote=True)}" data-year="{html.escape(year, quote=True)}" data-levels="{html.escape(levels, quote=True)}">
          <summary>
            <span class="arch-no">N. <span class="num">{html.escape(session)}</span></span>
            <span class="arch-chips">{chips}{latest_tag}</span>
            <span class="arch-count">{len(papers)} {plural}</span>
            <span class="arch-chev" aria-hidden="true"></span>
          </summary>
          <ul class="arch-rows">
{rows_joined}
          </ul>
        </details>""")
    blocks_joined = "\n".join(blocks)
    return f"""    <section class="section section-alt" id="archivio">
      <header class="section-head reveal">
        <p class="kicker">Archivio</p>
        <h2>Tutte le sessioni</h2>
        <p class="section-sub">Ogni sessione è una data di pubblicazione. I fascicoli pubblicati non cambiano mai: le correzioni diventano nuove sessioni.</p>
      </header>
      <div class="archive-controls reveal">
        <div class="filter-group" role="group" aria-label="Filtra per livello">
          {' '.join(level_buttons)}
        </div>
        <div class="filter-side">
          <label class="filter-select">Anno
            <select id="year-filter">{''.join(year_options)}</select>
          </label>
          <button class="filter-btn" type="button" id="sort-toggle" data-sort="recenti">Più recenti prima</button>
        </div>
      </div>
      <div class="archive-list" id="archive-list">
{blocks_joined}
      </div>
      <p class="archive-empty" id="archive-empty" hidden>Nessuna sessione corrisponde ai filtri selezionati.</p>
    </section>"""


def render_informazioni() -> str:
    return f"""    <section class="section" id="informazioni">
      <header class="section-head reveal">
        <p class="kicker">Informazioni</p>
        <h2>Un progetto indipendente</h2>
      </header>
      <div class="info-grid">
        <article class="info-card reveal">
          <p class="info-no" aria-hidden="true">§ 01</p>
          <h3>Non ufficiale, dichiaratamente</h3>
          <p>Questo è materiale di esercitazione non ufficiale. Il progetto non è affiliato all'Università per Stranieri di Siena né all'esame CILS, il cui marchio appartiene ai rispettivi titolari. Per la preparazione conviene consultare anche i materiali ufficiali.</p>
        </article>
        <article class="info-card reveal">
          <p class="info-no" aria-hidden="true">§ 02</p>
          <h3>Fonti e adattamento</h3>
          <p>Ogni testo proviene da una fonte italiana reale e pubblicata: stampa, enti pubblici, siti di servizio, letteratura di pubblico dominio. I testi sono adattati alla banda del livello — tagli e semplificazioni, mai fatti inventati — e ogni fonte è accreditata nei manifest del repository.</p>
        </article>
        <article class="info-card reveal">
          <p class="info-no" aria-hidden="true">§ 03</p>
          <h3>Soluzioni e verifica</h3>
          <p>Le chiavi sono verificate da una risoluzione indipendente alla cieca: il fascicolo si pubblica solo con il 100% di accordo sugli item oggettivi e zero segnalazioni di ambiguità, dopo audit deterministici di formato e qualità. Ogni chiave è accompagnata da spiegazioni e note di studio.</p>
        </article>
        <article class="info-card reveal">
          <p class="info-no" aria-hidden="true">§ 04</p>
          <h3>Codice, uso e citazione</h3>
          <p>La filiera di generazione è open source. I PDF sono liberi per lo studio personale e l'uso in classe; i testi originali restano dei rispettivi autori — citare la fonte quando si riusa. Errori e proposte si segnalano nel repository.</p>
          <p><a class="btn btn-ghost btn-small" href="{GITHUB_URL}" rel="noopener">Apri il repository</a></p>
        </article>
      </div>
    </section>"""


def render_footer(total_papers: int) -> str:
    return f"""  <footer class="footer">
    <div class="footer-inner">
      <p class="footer-brand">CILS <em>Exam Factory</em></p>
      <p class="footer-tricolore" aria-hidden="true"><span></span><span></span><span></span></p>
      <p class="footer-note">{html.escape(DISCLAIMER)}</p>
      <p class="footer-meta"><span class="num">{total_papers}</span> fascicoli pubblicati · <a href="{GITHUB_URL}" rel="noopener">Codice su GitHub</a></p>
    </div>
  </footer>"""


def render_index(papers: list[Paper], out_root: Path) -> str:
    papers_by_date: dict[str, list[Paper]] = {}
    for paper in papers:
        papers_by_date.setdefault(paper.date, []).append(paper)

    sessions = sorted(papers_by_date, key=session_sort_key, reverse=True)
    latest_session = sessions[0] if sessions else ""
    total_papers = len(papers)
    total_sources = sum(paper.source_count for paper in papers)
    level_counts: dict[str, int] = {}
    for paper in papers:
        level_counts[paper.level] = level_counts.get(paper.level, 0) + 1
    years = sorted({session[:4] for session in sessions}, reverse=True)

    description = (
        "Fascicoli di esercitazione CILS non ufficiali (A1–C1) generati da testi italiani autentici: "
        "lettura, strutture e produzione scritta con chiavi commentate, fonti verificate e audit editoriale."
    )

    if sessions:
        latest_day = session_sort_key(latest_session)[0]
        latest_by_level: dict[str, Paper] = {}
        for session in sessions:  # numeric revision order, newest first
            if session_sort_key(session)[0] == latest_day:
                for paper in papers_by_date[session]:
                    latest_by_level.setdefault(paper.level, paper)
        ultima = render_ultima(latest_day, list(latest_by_level.values()), out_root)
        archivio = render_archivio(sessions, papers_by_date, out_root, latest_session, years)
    else:
        ultima = '    <section class="section" id="sessione"><p class="archive-empty">Nessun fascicolo pubblicato.</p></section>'
        archivio = '    <section class="section" id="archivio"></section>'

    return f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CILS Exam Factory · Esercitazioni CILS da testi autentici (A1–C1)</title>
  <meta name="description" content="{html.escape(description, quote=True)}">
  <link rel="canonical" href="{SITE_URL}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="it_IT">
  <meta property="og:site_name" content="CILS Exam Factory">
  <meta property="og:title" content="CILS Exam Factory · Esercitazioni CILS da testi autentici">
  <meta property="og:description" content="{html.escape(description, quote=True)}">
  <meta property="og:url" content="{SITE_URL}">
  <meta property="og:image" content="{SITE_URL}assets/og.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#f6f2e8">
  <link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
  <link rel="stylesheet" href="assets/site.css">
  <script defer src="assets/site.js"></script>
</head>
<body>
{render_topbar()}
  <main id="contenuto">
{render_hero(total_papers, len(sessions), total_sources, latest_session)}
{render_livelli(level_counts)}
{ultima}
{render_metodo()}
{archivio}
{render_informazioni()}
  </main>
{render_footer(total_papers)}
</body>
</html>
"""


def session_sort_key(session: str) -> tuple[str, int]:
    match = SESSION_RE.fullmatch(session)
    if not match:
        return (session, 0)
    base, revision = match.groups()
    return (base, int(revision or "0"))


def write_index(papers: list[Paper], out_root: Path) -> None:
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "index.html").write_text(render_index(papers, out_root), encoding="utf-8")


def build(args: argparse.Namespace) -> int:
    papers_root = args.papers_root
    out_root = args.out
    papers = scan_papers(papers_root)

    copy_assets(out_root)
    pdf_printer = (None if args.no_pdf else MuPdfPrinter()
                   if args.pdf_engine == "mupdf" else PdfPrinter(force=args.force))

    for paper in papers:
        pair = [out_root/"papers"/paper.date/paper.level/f"{kind}.pdf"
                for kind in ("paper", "answers")]
        if not args.no_pdf and not args.force:
            if all(valid_pdf(path) for path in pair):
                continue  # Published PDF bytes are immutable, regardless of checkout mtimes.
            if any(path.exists() for path in pair):
                raise BuildError(f"Incomplete/invalid existing PDF pair: {pair[0].parent}; use a revision session")
        build_paper_outputs(paper, out_root, pdf_printer)

    write_index(papers, out_root)
    print(f"Built {len(papers)} published paper(s) into {out_root}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the CILS Exam Factory static site.")
    parser.add_argument("--pdf-engine", choices=("chrome", "mupdf"), default="chrome", help="PDF renderer; mupdf needs no browser")
    parser.add_argument("--no-pdf", action="store_true", help="skip PDF generation")
    parser.add_argument("--force", action="store_true", help="regenerate PDFs even if cached")
    parser.add_argument("--papers-root", type=Path, default=Path("papers"), help="papers root")
    parser.add_argument("--out", type=Path, default=Path("docs"), help="output docs root")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        return build(args)
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
