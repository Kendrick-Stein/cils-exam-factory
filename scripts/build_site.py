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

    if kind == "paper":
        # Wrap the booklet cover (everything before the answer-sheet example,
        # or before the first test for pre-2026-07-08-r2 papers without one)
        # so print styles can render it as a full standalone cover page.
        marker = content.find("<h2>ESEMPIO DI FOGLIO")
        if marker == -1:
            marker = content.find("<h1>", 1)
        if marker != -1:
            content = f'<section class="cover">\n{content[:marker]}</section>\n{content[marker:]}'

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


def build_paper_outputs(paper: Paper, out_root: Path, pdf_printer: PdfPrinter | None) -> None:
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
            pdf_printer.render(html_target, pdf_target, md_source)
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
     "Gli item nascono una prova alla volta: comprensione della lettura, analisi delle strutture, produzione scritta con tracce e testi modello."),
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
    return f"""    <section class="section section-alt" id="sessione">
      <header class="section-head reveal">
        <p class="kicker">Ultima sessione</p>
        <h2><span class="num">{html.escape(session)}</span></h2>
        <p class="section-sub">Cinque fascicoli pubblicati dopo verifica alla cieca e audit editoriale. Le sessioni precedenti sono nell'<a href="#archivio">archivio</a>.</p>
      </header>
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
        ultima = render_ultima(latest_session, papers_by_date[latest_session], out_root)
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
