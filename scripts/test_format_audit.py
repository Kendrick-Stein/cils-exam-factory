#!/usr/bin/env python3
"""Fixture tests for scripts/format_audit.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    print("python3 -m pip install --user pyyaml", file=sys.stderr)
    raise SystemExit(2)


REPO_ROOT = Path(__file__).resolve().parents[1]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def exam_yaml() -> str:
    return """
exam: cils
levels:
  A1:
    sections:
      - id: lettura
        prove:
          - {n: 1}
          - {n: 2}
      - id: strutture
        prove:
          - {n: 1}
      - id: scritta
        prove:
          - {n: 1}
          - {n: 2}
"""


def manifest() -> str:
    return """
exam: cils
level: A1
session: "2000-01-04"
title: "A1 fixture"
status: draft
pipeline:
  stages: []
validation:
  result: pass
"""


def paper(with_answer_sheet: bool = True, with_attribution: bool = False) -> str:
    answer_sheet = "## ESEMPIO DI FOGLIO DELLE RISPOSTE\n" if with_answer_sheet else ""
    attribution = "\n*Testo adattato da: Fonte, Sito, https://example.com, consultato il 04/01/2000*\n" if with_attribution else ""
    return f"""---
exam: CILS
level: A1
session: "2000-01-04"
kind: paper
---

# CILS
## Quaderno di esame
{answer_sheet}
# Test di comprensione della lettura

## Comprensione della lettura — Prova n. 1

> *Leggi il testo.*

### TESTO UNO

Uno due tre.
{attribution}
## Comprensione della lettura — Prova n. 2

> *Leggi il testo.*

### TESTO DUE

Quattro cinque sei.

# Test di analisi delle strutture di comunicazione

## Analisi delle strutture di comunicazione — Prova n. 1

> *Completa il testo.*

### TESTO TRE

Sette otto nove.

# Test di produzione scritta

## Produzione scritta — Prova n. 1

> *Scrivi un testo.*

## Produzione scritta — Prova n. 2

> *Scrivi un messaggio.*

# Foglio delle risposte
"""


def write_fixture(root: Path, *, with_answer_sheet: bool = True, with_attribution: bool = False) -> tuple[Path, Path]:
    papers_root = root / "papers"
    level_dir = papers_root / "2000-01-04" / "A1"
    write_text(root / "exam.yaml", exam_yaml())
    write_text(level_dir / "manifest.yaml", manifest())
    write_text(level_dir / "paper.md", paper(with_answer_sheet=with_answer_sheet, with_attribution=with_attribution))
    write_text(level_dir / "answers.md", "# Soluzioni\n")
    write_text(level_dir / "sources.md", "# Fonti\n")
    write_text(level_dir / "key.json", json.dumps({"L1.1": "A"}, ensure_ascii=False))
    return papers_root, root / "exam.yaml"


def run_format_audit(root: Path, *, write_manifest: bool = True) -> subprocess.CompletedProcess[str]:
    papers_root, exam_path = write_fixture(root)
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "format_audit.py"),
        "--papers-root",
        str(papers_root),
        "--session",
        "2000-01-04",
        "--levels",
        "A1",
        "--exam",
        str(exam_path),
        "--report",
        str(root / "format-audit.json"),
    ]
    if write_manifest:
        cmd.append("--write-manifest")
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def test_passing_fixture_appends_format_stage() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        completed = run_format_audit(root)
        if completed.returncode != 0:
            raise AssertionError(completed.stderr or completed.stdout)
        report = json.loads((root / "format-audit.json").read_text(encoding="utf-8"))
        if report["result"] != "pass":
            raise AssertionError(report)
        manifest_data = yaml.safe_load(
            (root / "papers" / "2000-01-04" / "A1" / "manifest.yaml").read_text(encoding="utf-8")
        )
        stages = manifest_data["pipeline"]["stages"]
        if stages[-1]["stage"] != "format_audit" or stages[-1]["result"] != "pass":
            raise AssertionError(stages)


def test_missing_answer_sheet_and_visible_attribution_fail() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        papers_root, exam_path = write_fixture(root, with_answer_sheet=False, with_attribution=True)
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "format_audit.py"),
                "--papers-root",
                str(papers_root),
                "--session",
                "2000-01-04",
                "--levels",
                "A1",
                "--exam",
                str(exam_path),
                "--report",
                str(root / "format-audit.json"),
                "--write-manifest",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            raise AssertionError("format audit should fail")
        report = json.loads((root / "format-audit.json").read_text(encoding="utf-8"))
        issue_ids = {issue["id"] for issue in report["issues"]}
        for expected in ("format.answer_sheet_example", "format.visible_source_attribution"):
            if expected not in issue_ids:
                raise AssertionError(report)
        manifest_data = yaml.safe_load(
            (root / "papers" / "2000-01-04" / "A1" / "manifest.yaml").read_text(encoding="utf-8")
        )
        stages = manifest_data["pipeline"]["stages"]
        if stages[-1]["stage"] != "format_audit" or stages[-1]["result"] != "fail":
            raise AssertionError(stages)
        if manifest_data.get("status") != "draft" or manifest_data.get("reason") != "format_audit":
            raise AssertionError(manifest_data)


def run_test() -> None:
    test_passing_fixture_appends_format_stage()
    test_missing_answer_sheet_and_visible_attribution_fail()


def main() -> int:
    try:
        run_test()
    except Exception as exc:  # noqa: BLE001 - keep script dependency-free.
        print(f"FAIL: {exc}")
        return 1
    print("PASS: format audit tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
