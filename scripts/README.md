# Build Scripts
Usage: `/opt/anaconda3/bin/python3 scripts/build_site.py` rebuilds published papers into `docs/`.
Fast preview: add `--no-pdf` to skip Chrome PDF generation.
Force PDFs: add `--force` to regenerate PDFs even when cached files are newer.
Input root: use `--papers-root <dir>` to read a different papers tree.
Output root: use `--out <dir>` to write static files somewhere other than `docs`.
Dependencies: only `markdown` and `pyyaml` beyond the Python standard library.
Install hint: `python3 -m pip install --user markdown pyyaml`.
PDFs require Google Chrome at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`.
If Chrome is missing or PDF export fails, the build warns and keeps HTML/MD outputs.

Blind validation:
- `python3 scripts/blind_validation.py prepare --paper-dir papers/<date>/<LEVEL>` creates the isolated `/tmp/cils-blind-<date>-<LEVEL>/paper.md` copy for S3.
- After saving solver output, `python3 scripts/blind_validation.py reconcile --paper-dir papers/<date>/<LEVEL> --blind-output <blind-output.txt> --report papers/<date>/<LEVEL>/blind-validation.json --write-manifest` compares it with `key.json`, writes failing items, and updates `manifest.yaml`.

Quality audit:
- `python3 scripts/paper_quality_audit.py --session <date> --levels A1,A2,B1,B2,C1 --report papers/<date>/quality-audit.json --write-manifest` checks official-style student-paper separation, manifest quality/source metadata, reading and structure length bands, C1 P4 continuous-text shape, B2/C1 item depth, and cross-level source reuse.

Format audit:
- `python3 scripts/format_audit.py --session <date> --levels A1,A2,B1,B2,C1 --report papers/<date>/format-audit.json --write-manifest` checks required files, front matter consistency, official-style section order and prova headings, answer-sheet markers, source-attribution leakage, study-aid leakage, and valid `key.json`.

Publish gate: `build_site.py` only accepts `status: published` papers whose manifest validation block proves 100% blind agreement, zero flags, zero mismatches, pass result, latest `quality_audit` result pass, and latest `format_audit` result pass.
Status audit: `python3 scripts/paper_status.py --session <date> --levels A1,A2,B1,B2,C1` reports which levels are publishable and which next pipeline stage is missing.
