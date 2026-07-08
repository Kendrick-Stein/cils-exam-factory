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
