# Build Scripts
Usage: `python3 scripts/build_site.py` rebuilds published papers into `docs/`.
Fast preview: add `--no-pdf` to skip Chrome PDF generation.
Force PDFs: add `--force` to regenerate PDFs even when cached files are newer.
Input root: use `--papers-root <dir>` to read a different papers tree.
Output root: use `--out <dir>` to write static files somewhere other than `docs`.
Dependencies: only `markdown` and `pyyaml` beyond the Python standard library.
Install into a virtual environment: `python3 -m venv .venv`, then `.venv/bin/python -m pip install --index-url https://pypi.org/simple -r requirements-build.txt`. Run the builder with `.venv/bin/python`.
PDFs require installed Chrome or Chromium. The builder checks the standard macOS Chrome path, then `google-chrome`, `google-chrome-stable`, `chromium`, and `chromium-browser` on PATH. Set `CILS_CHROME=/absolute/path/to/browser` to override discovery. No browser sandbox is disabled.
Missing browsers, browser errors/timeouts, and absent/invalid PDF outputs fail the build with exit code 1. Successful output replaces a PDF atomically; failed regeneration preserves the previous PDF. A private temporary profile prevents conflicts with interactive Chrome. `--no-pdf` is preview-only and does not prove publication readiness. Restricted containers must permit Chromium to create its local sockets and sandbox; an installed binary alone is not sufficient.
Checks: `python3 scripts/test_pdf_printer.py` and `python3 scripts/test_build_site.py`. Run a real PDF smoke test in the target environment before publishing; verify both PDFs and visually inspect rendered pages.

Blind validation:
- `python3 scripts/blind_validation.py prepare --paper-dir papers/<date>/<LEVEL>` creates the isolated `/tmp/cils-blind-<date>-<LEVEL>/paper.md` copy for S3.
- After saving solver output, `python3 scripts/blind_validation.py reconcile --paper-dir papers/<date>/<LEVEL> --blind-output <blind-output.txt> --report papers/<date>/<LEVEL>/blind-validation.json --write-manifest` compares it with `key.json`, writes failing items, and updates `manifest.yaml`.

Quality audit:
- `python3 scripts/paper_quality_audit.py --session <date> --levels A1,A2,B1,B2,C1 --report papers/<date>/quality-audit.json --write-manifest` checks official-style student-paper separation, manifest quality/source metadata, reading and structure length bands, C1 P4 continuous-text shape, B2/C1 item depth, and cross-level source reuse.

Format audit:
- `python3 scripts/format_audit.py --session <date> --levels A1,A2,B1,B2,C1 --report papers/<date>/format-audit.json --write-manifest` checks required files, front matter consistency, official-style section order and prova headings, answer-sheet markers, source-attribution leakage, study-aid leakage, and valid `key.json`.

Publish gate: `build_site.py` only accepts `status: published` papers whose manifest validation block proves 100% blind agreement, zero flags, zero mismatches, pass result, latest `quality_audit` result pass, and latest `format_audit` result pass.
Status audit: `python3 scripts/paper_status.py --session <date> --levels A1,A2,B1,B2,C1` reports which levels are publishable and which next pipeline stage is missing.

## Browser-free cloud rendering

Use `python3 scripts/build_site.py --pdf-engine mupdf` with PyMuPDF 1.26.6 or later in the 1.26 series. A fresh environment can install `requirements-pdf-mupdf.txt`; an existing runtime with PyMuPDF only needs the base build dependencies. This engine uses MuPDF Story and its bundled CJK font support, without browsers, sockets, a GPU, external APIs, or a separate coding task. It uses a dedicated printable stylesheet (`assets/mupdf.css`) rather than reproducing every Chrome CSS detail. Long tables can span pages; visually inspect all new PDFs before publication.

The default build preserves complete existing PDF pairs byte-for-byte, independent of checkout timestamps. Incomplete or invalid existing pairs fail. `--force` is for isolated preview directories only: published corrections must use a new revision session. Both engines use temporary outputs and fail closed on errors. A pair interrupted after the first PDF requires removal only from the unpublished staging area before retry, never overwriting historical docs.

For safe daily publication, copy current `docs/` into a fresh staging directory and build with `--out <staging> --pdf-engine mupdf`. Check unchanged hashes for every historical PDF, run format/quality audits for new levels, render new pages to images, and inspect them. Copy only new PDF pairs and the updated index to `docs/`, then commit the passed source levels and docs together. Confirm the exact commit's Pages deployment; a build or push alone is not publication verification.

Tests: `python3 scripts/test_pdf_printer.py`, `python3 scripts/test_build_site.py`, and `python3 scripts/test_mupdf_renderer.py`. The MuPDF test renders actual Italian/CJK fixture PDFs; it is not a mocked renderer test.
