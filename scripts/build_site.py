#!/opt/anaconda3/bin/python3
"""Build the static CILS Exam Factory site."""

from __future__ import annotations

import argparse
import html
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


class PdfPrinter:
    def __init__(self, force: bool) -> None:
        self.force = force
        self._warned_missing = False

    def render(self, html_path: Path, pdf_path: Path, source_md: Path) -> None:
        if pdf_path.exists() and not self.force:
            if pdf_path.stat().st_mtime >= source_md.stat().st_mtime:
                return

        if not CHROME.exists():
            if not self._warned_missing:
                warn(f"Chrome not found at {CHROME}; skipping PDF generation.")
                self._warned_missing = True
            return

        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            str(CHROME),
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path.resolve()}",
            html_path.resolve().as_uri(),
        ]
        completed = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip()
            if detail:
                warn(f"Chrome failed for {html_path}: {detail}")
            else:
                warn(f"Chrome failed for {html_path} with exit code {completed.returncode}.")


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
    rendered = markdown_lib.markdown(body, extensions=MARKDOWN_EXTENSIONS)
    return front_matter, rendered


def render_page(path: Path, paper: Paper, kind: str) -> str:
    front_matter, content = render_markdown(path)
    level = str(front_matter.get("level") or paper.level)
    level_name = str(front_matter.get("level_name") or paper.title)
    session = str(front_matter.get("session") or paper.session)
    kind_label = "Fascicolo" if kind == "paper" else "Chiavi e commenti"
    title = f"{kind_label} · {level} · {session}"
    counterpart_label = "Apri chiavi" if kind == "paper" else "Apri fascicolo"
    counterpart_href = "answers.html" if kind == "paper" else "paper.html"

    return f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="../../../assets/paper.css">
</head>
<body>
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
    for css_file in sorted(source_dir.glob("*.css")):
        shutil.copy2(css_file, target_dir / css_file.name)


def build_paper_outputs(paper: Paper, out_root: Path, pdf_printer: PdfPrinter | None) -> None:
    out_dir = out_root / "papers" / paper.date / paper.level
    out_dir.mkdir(parents=True, exist_ok=True)

    for kind in ("paper", "answers"):
        md_source = paper.root / f"{kind}.md"
        md_target = out_dir / f"{kind}.md"
        html_target = out_dir / f"{kind}.html"
        pdf_target = out_dir / f"{kind}.pdf"

        shutil.copy2(md_source, md_target)
        html_target.write_text(render_page(md_source, paper, kind), encoding="utf-8")

        if pdf_printer is not None:
            pdf_printer.render(html_target, pdf_target, md_source)


def artifact_link(out_root: Path, href: str, label: str, primary: bool = False) -> str:
    if (out_root / href).exists():
        classes = "download-button download-button-primary" if primary else "download-button"
        return f'<a class="{classes}" href="{html.escape(href, quote=True)}">{html.escape(label)}</a>'
    return ""


def link_group(out_root: Path, base: str, stem: str, label: str) -> str:
    candidates = [
        (f"{base}/{stem}.pdf", "PDF"),
        (f"{base}/{stem}.html", "HTML"),
        (f"{base}/{stem}.md", "MD"),
    ]
    available = [(href, text) for href, text in candidates if (out_root / href).exists()]
    links = [
        artifact_link(out_root, href, text, primary=index == 0)
        for index, (href, text) in enumerate(available)
    ]
    rendered_links = " ".join(link for link in links if link)
    return (
        f'<div class="download-group">'
        f'<div class="download-label">{html.escape(label)}</div>'
        f'<div class="download-links">{rendered_links}</div>'
        "</div>"
    )


def render_index(papers: list[Paper], out_root: Path) -> str:
    papers_by_date: dict[str, list[Paper]] = {}
    for paper in papers:
        papers_by_date.setdefault(paper.date, []).append(paper)

    sessions = sorted(papers_by_date, key=session_sort_key, reverse=True)
    latest_session = sessions[0] if sessions else ""
    total_papers = len(papers)
    total_sources = sum(paper.source_count for paper in papers)
    session_nav = ""
    if sessions:
        session_links = "\n".join(
            f'        <a href="#session-{html.escape(slug(session), quote=True)}">{html.escape(session)}</a>'
            for session in sessions
        )
        session_nav = f"""    <nav class="session-nav" aria-label="Sessioni pubblicate">
      <span>Sessioni</span>
{session_links}
    </nav>"""

    session_cards: list[str] = []
    for session in sessions:
        cards: list[str] = []
        for paper in sorted(papers_by_date[session], key=level_sort_key):
            base = f"papers/{paper.date}/{paper.level}"
            cards.append(
                f"""      <article class="level-card">
        <div class="level-card-header">
          {badge(paper.level)}
          <div>
            <h3>{html.escape(paper.title)}</h3>
            <p>{paper.source_count} testi autentici verificati</p>
          </div>
        </div>
        <div class="level-card-downloads">
          {link_group(out_root, base, "paper", "Fascicolo")}
          {link_group(out_root, base, "answers", "Chiavi e commenti")}
        </div>
      </article>"""
            )

        level_cards = "\n".join(cards)
        latest_badge = '\n      <span class="session-label">Ultima sessione</span>' if session == latest_session else ""
        session_cards.append(
            f"""  <section class="session-card" id="session-{html.escape(slug(session), quote=True)}">
    <div class="session-heading">
      <div>
        <p class="session-kicker">Sessione</p>
        <h2>{html.escape(session)}</h2>
      </div>{latest_badge}
    </div>
    <div class="level-grid">
{level_cards}
    </div>
  </section>"""
        )

    if not session_cards:
        session_cards.append('  <section class="empty-state">Nessun fascicolo pubblicato.</section>')

    cards_html = "\n".join(session_cards)
    return f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CILS Exam Factory</title>
  <link rel="stylesheet" href="assets/site.css">
</head>
<body>
  <main class="site">
    <header class="hero">
      <p class="eyebrow">Esercitazioni CILS non ufficiali</p>
      <h1>CILS Exam Factory</h1>
      <p class="tagline">Materiali di pratica in italiano, con chiavi commentate. Practice papers for Italian learners, with answer keys and notes.</p>
      <p class="intro">Cos'è: una raccolta statica di fascicoli CILS simulati, generati da testi autentici adattati, controllati con risoluzione alla cieca e pubblicati solo dopo audit di formato.</p>
      <div class="hero-stats" aria-label="Statistiche pubblicazione">
        <div><strong>{total_papers}</strong><span>fascicoli pubblicati</span></div>
        <div><strong>{len(sessions)}</strong><span>sessioni</span></div>
        <div><strong>{total_sources}</strong><span>fonti autentiche</span></div>
      </div>
    </header>
{session_nav}

{cards_html}

    <section class="methodology">
      <h2>Metodologia</h2>
      <ul>
        <li>Selezione di testi autentici adatti al livello.</li>
        <li>Generazione su template ufficiale del formato CILS.</li>
        <li>Risoluzione alla cieca indipendente degli item oggettivi.</li>
        <li>Audit di formato su conteggi, sezioni, consegne e attribuzioni.</li>
        <li>Pubblicazione statica di HTML, Markdown e PDF.</li>
      </ul>
    </section>
  </main>
  <footer class="site-footer">
    <p>{html.escape(DISCLAIMER)}</p>
  </footer>
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
    pdf_printer = None if args.no_pdf else PdfPrinter(force=args.force)

    for paper in papers:
        build_paper_outputs(paper, out_root, pdf_printer)

    write_index(papers, out_root)
    print(f"Built {len(papers)} published paper(s) into {out_root}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the CILS Exam Factory static site.")
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
