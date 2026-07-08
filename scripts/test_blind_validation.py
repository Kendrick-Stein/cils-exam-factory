#!/usr/bin/env python3
"""Fixture tests for scripts/blind_validation.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_paper(root: Path, session: str = "2000-01-02") -> Path:
    paper_dir = root / "papers" / session / "B1"
    write_text(
        paper_dir / "paper.md",
        f"""---
exam: CILS
level: B1
level_name: "CILS UNO — B1"
session: "{session}"
kind: paper
---

# Paper fixture
""",
    )
    write_text(
        paper_dir / "answers.md",
        "# Answers fixture\n",
    )
    write_text(
        paper_dir / "sources.md",
        "# Sources fixture\n",
    )
    write_text(
        paper_dir / "key.json",
        json.dumps(
            {
                "L1.1": "A",
                "L1.2": "B",
                "S1.1": "il",
            },
            ensure_ascii=False,
            indent=2,
        ),
    )
    write_text(
        paper_dir / "manifest.yaml",
        f"""exam: cils
level: B1
session: "{session}"
title: "Fixture"
status: draft
sources: []
pipeline:
  generator: fixture
  template: factory/exams/cils/templates/B1.md
  stages: []
""",
    )
    return paper_dir


def run_cmd(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"command failed: {' '.join(args)}\n"
            f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return completed


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_contains(path: Path, needle: str) -> None:
    if needle not in path.read_text(encoding="utf-8"):
        raise AssertionError(f"{path} does not contain {needle!r}")


def run_test() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "blind_validation.py"

    with tempfile.TemporaryDirectory(prefix="cils-blind-validation-") as tmp:
        tmp_root = Path(tmp)
        paper_dir = make_paper(tmp_root)
        blind_root = tmp_root / "blind-root"

        prepare = run_cmd(
            [
                str(script),
                "prepare",
                "--paper-dir",
                str(paper_dir),
                "--tmp-root",
                str(blind_root),
            ],
            cwd=repo_root,
        )
        prepare_report = json.loads(prepare.stdout)
        isolated_paper = Path(prepare_report["isolated_paper"])
        isolated_dir = isolated_paper.parent
        if not isolated_paper.exists():
            raise AssertionError("prepare did not copy paper.md")
        if prepare_report["codex_args"][:4] != ["codex", "exec", "--sandbox", "read-only"]:
            raise AssertionError(f"unexpected codex argv: {prepare_report['codex_args']}")
        isolated_files = sorted(path.name for path in isolated_dir.iterdir() if path.is_file())
        if isolated_files != ["paper.md"]:
            raise AssertionError(f"blind directory must contain only paper.md, got: {isolated_files}")
        assert_contains(isolated_paper, "Paper fixture")
        if str(isolated_paper) not in prepare_report["prompt"]:
            raise AssertionError("prepare prompt does not reference isolated paper")
        for needle in ("L<prova>.<n>", "S<prova>.<n>", "return the whole sequence as L3"):
            if needle not in prepare_report["prompt"]:
                raise AssertionError(f"prepare prompt is missing item-id guidance {needle!r}")

        blind_output = tmp_root / "blind-output.txt"
        write_text(
            blind_output,
            """ANSWERS
{
  "L1.1": {"answer": "A", "confidence": "hi"},
  "L1.2": {"answer": "C", "confidence": "med"},
  "S1.1": {"answer": "il", "confidence": "hi"}
}
FLAGS
[
  {"item": "S1.1", "reason": "two defensible forms"}
]
WRITING
W1: ok
""",
        )
        report_path = tmp_root / "report.json"
        reconcile = run_cmd(
            [
                str(script),
                "reconcile",
                "--paper-dir",
                str(paper_dir),
                "--blind-output",
                str(blind_output),
                "--report",
                str(report_path),
                "--write-manifest",
            ],
            cwd=repo_root,
        )
        inline_report = json.loads(reconcile.stdout)
        saved_report = load_json(report_path)
        for report in (inline_report, saved_report):
            if report["result"] != "fail":
                raise AssertionError(f"expected failing validation report: {report}")
            if report["agreement"] != "2/3":
                raise AssertionError(f"unexpected agreement: {report}")
            if report["mismatches"] != [{"item_id": "L1.2", "expected": "B", "actual": "C"}]:
                raise AssertionError(f"unexpected mismatches: {report['mismatches']}")
            if sorted(item["item_id"] for item in report["failing_items"]) != ["L1.2", "S1.1"]:
                raise AssertionError(f"unexpected failing items: {report['failing_items']}")

        manifest = (paper_dir / "manifest.yaml").read_text(encoding="utf-8")
        for needle in (
            "stage: blind_validation",
            "agreement: 2/3",
            "flags: 1",
            "result: fail",
            "reason: validation",
        ):
            if needle not in manifest:
                raise AssertionError(f"manifest missing {needle!r}:\n{manifest}")

    with tempfile.TemporaryDirectory(prefix="cils-blind-validation-revision-") as tmp:
        tmp_root = Path(tmp)
        paper_dir = make_paper(tmp_root, session="2000-01-02-r2")
        blind_root = tmp_root / "blind-root"

        prepare = run_cmd(
            [
                str(script),
                "prepare",
                "--paper-dir",
                str(paper_dir),
                "--tmp-root",
                str(blind_root),
            ],
            cwd=repo_root,
        )
        prepare_report = json.loads(prepare.stdout)
        isolated_paper = Path(prepare_report["isolated_paper"])
        if isolated_paper != blind_root / "cils-blind-2000-01-02-r2-B1" / "paper.md":
            raise AssertionError(f"unexpected revision blind path: {isolated_paper}")
        if not isolated_paper.exists():
            raise AssertionError("revision prepare did not copy paper.md")

    with tempfile.TemporaryDirectory(prefix="cils-blind-validation-unsafe-") as tmp:
        tmp_root = Path(tmp)
        paper_dir = make_paper(tmp_root)
        manifest = paper_dir / "manifest.yaml"
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace('session: "2000-01-02"', 'session: "2000/../../escape"'),
            encoding="utf-8",
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(script),
                "prepare",
                "--paper-dir",
                str(paper_dir),
                "--tmp-root",
                str(tmp_root / "blind-root"),
            ],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            raise AssertionError("prepare accepted unsafe session value")
        if "unsafe" not in completed.stderr:
            raise AssertionError(f"expected unsafe path error, got:\n{completed.stderr}")

    with tempfile.TemporaryDirectory(prefix="cils-blind-validation-fenced-") as tmp:
        tmp_root = Path(tmp)
        paper_dir = make_paper(tmp_root)
        blind_output = tmp_root / "blind-output.md"
        write_text(
            blind_output,
            """Here is the result:

```json
{
  "answers": {
    "L1.1": "A",
    "L1.2": {"answer": "B", "confidence": "hi"},
    "S1.1": "il"
  },
  "flags": ["L1.2"]
}
```
""",
        )
        reconcile = run_cmd(
            [
                str(script),
                "reconcile",
                "--paper-dir",
                str(paper_dir),
                "--blind-output",
                str(blind_output),
            ],
            cwd=repo_root,
        )
        report = json.loads(reconcile.stdout)
        if report["agreement"] != "3/3":
            raise AssertionError(f"unexpected fenced JSON agreement: {report}")
        if report["flags"] != [{"item_id": "L1.2", "reason": "flagged by blind solver"}]:
            raise AssertionError(f"unexpected fenced JSON flags: {report['flags']}")
        if report["result"] != "fail":
            raise AssertionError("flags from fenced JSON should fail validation")

    with tempfile.TemporaryDirectory(prefix="cils-blind-validation-answer-singular-") as tmp:
        tmp_root = Path(tmp)
        paper_dir = make_paper(tmp_root)
        blind_output = tmp_root / "blind-output.md"
        write_text(
            blind_output,
            """ANSWER:
```json
{
  "L1.1": "A",
  "L1.2": "B",
  "S1.1": "il"
}
```

FLAGS:
```json
[
  {"item_id": "S1.1", "reason": "still ambiguous"}
]
```
""",
        )
        reconcile = run_cmd(
            [
                str(script),
                "reconcile",
                "--paper-dir",
                str(paper_dir),
                "--blind-output",
                str(blind_output),
            ],
            cwd=repo_root,
        )
        report = json.loads(reconcile.stdout)
        if report["agreement"] != "3/3" or report["result"] != "fail":
            raise AssertionError(f"singular ANSWER with FLAGS should parse flags and fail: {report}")
        if report["flags"] != [{"item_id": "S1.1", "reason": "still ambiguous"}]:
            raise AssertionError(f"singular ANSWER flags were not parsed: {report['flags']}")

    with tempfile.TemporaryDirectory(prefix="cils-blind-validation-sequence-") as tmp:
        tmp_root = Path(tmp)
        paper_dir = make_paper(tmp_root)
        write_text(
            paper_dir / "key.json",
            json.dumps({"L3": "A-D-H"}, ensure_ascii=False, indent=2),
        )
        blind_output = tmp_root / "blind-output.txt"
        write_text(
            blind_output,
            """ANSWERS
{
  "L3.1": {"answer": "A", "confidence": "hi"},
  "L3.2": {"answer": "D", "confidence": "hi"},
  "L3.3": {"answer": "H", "confidence": "hi"}
}
FLAGS
[]
""",
        )
        reconcile = run_cmd(
            [
                str(script),
                "reconcile",
                "--paper-dir",
                str(paper_dir),
                "--blind-output",
                str(blind_output),
            ],
            cwd=repo_root,
        )
        report = json.loads(reconcile.stdout)
        if report["result"] != "pass":
            raise AssertionError(f"sequence item should pass when split answers match key: {report}")
        if report["agreement"] != "1/1":
            raise AssertionError(f"unexpected sequence agreement: {report}")
        if report["extra_answers"] != []:
            raise AssertionError(f"split sequence answers should not be extra: {report}")

    with tempfile.TemporaryDirectory(prefix="cils-blind-validation-sequence-separators-") as tmp:
        tmp_root = Path(tmp)
        paper_dir = make_paper(tmp_root)
        write_text(
            paper_dir / "key.json",
            json.dumps({"L3": "A-D-H"}, ensure_ascii=False, indent=2),
        )
        blind_output = tmp_root / "blind-output.txt"
        write_text(
            blind_output,
            """ANSWERS
{
  "L3": {"answer": "A, D, H", "confidence": "hi"}
}
FLAGS
[]
""",
        )
        reconcile = run_cmd(
            [
                str(script),
                "reconcile",
                "--paper-dir",
                str(paper_dir),
                "--blind-output",
                str(blind_output),
            ],
            cwd=repo_root,
        )
        report = json.loads(reconcile.stdout)
        if report["result"] != "pass":
            raise AssertionError(f"comma-separated sequence answer should match hyphenated key: {report}")

    with tempfile.TemporaryDirectory(prefix="cils-blind-validation-elision-") as tmp:
        tmp_root = Path(tmp)
        paper_dir = make_paper(tmp_root)
        write_text(
            paper_dir / "key.json",
            json.dumps({"S1.1": "all'", "S1.2": "dell'"}, ensure_ascii=False, indent=2),
        )
        blind_output = tmp_root / "blind-output.txt"
        write_text(
            blind_output,
            """ANSWERS
{
  "S1.1": {"answer": "all'Esposizione", "confidence": "hi"},
  "S1.2": {"answer": "dell'allevatore", "confidence": "hi"}
}
FLAGS
[]
""",
        )
        reconcile = run_cmd(
            [
                str(script),
                "reconcile",
                "--paper-dir",
                str(paper_dir),
                "--blind-output",
                str(blind_output),
            ],
            cwd=repo_root,
        )
        report = json.loads(reconcile.stdout)
        if report["result"] != "pass":
            raise AssertionError(f"elided article answers should pass with following noun included: {report}")
        if report["agreement"] != "2/2":
            raise AssertionError(f"unexpected elision agreement: {report}")

    with tempfile.TemporaryDirectory(prefix="cils-blind-validation-case-") as tmp:
        tmp_root = Path(tmp)
        paper_dir = make_paper(tmp_root)
        write_text(
            paper_dir / "key.json",
            json.dumps({"S1.1": "nonostante"}, ensure_ascii=False, indent=2),
        )
        blind_output = tmp_root / "blind-output.txt"
        write_text(
            blind_output,
            """ANSWERS
{
  "S1.1": {"answer": "Nonostante", "confidence": "hi"}
}
FLAGS
[]
""",
        )
        reconcile = run_cmd(
            [
                str(script),
                "reconcile",
                "--paper-dir",
                str(paper_dir),
                "--blind-output",
                str(blind_output),
            ],
            cwd=repo_root,
        )
        report = json.loads(reconcile.stdout)
        if report["result"] != "pass":
            raise AssertionError(f"capitalization-only differences should pass: {report}")

    with tempfile.TemporaryDirectory(prefix="cils-blind-validation-alternatives-") as tmp:
        tmp_root = Path(tmp)
        paper_dir = make_paper(tmp_root)
        write_text(
            paper_dir / "key.json",
            json.dumps(
                {
                    "S1.1": "in particolare || soprattutto",
                    "S1.2": "ma || bensì",
                    "S1.3": "UNA CONVENZIONE SARÀ FIRMATA DAI SOGGETTI SELEZIONATI CON IL COMUNE. || UNA CONVENZIONE CON IL COMUNE SARÀ FIRMATA DAI SOGGETTI SELEZIONATI.",
                },
                ensure_ascii=False,
                indent=2,
            ),
        )
        blind_output = tmp_root / "blind-output.txt"
        write_text(
            blind_output,
            """ANSWERS
{
  "S1.1": {"answer": "soprattutto", "confidence": "hi"},
  "S1.2": {"answer": "BENSÌ", "confidence": "hi"},
  "S1.3": {"answer": "UNA CONVENZIONE CON IL COMUNE SARÀ FIRMATA DAI SOGGETTI SELEZIONATI.", "confidence": "hi"}
}
FLAGS
[]
""",
        )
        reconcile = run_cmd(
            [
                str(script),
                "reconcile",
                "--paper-dir",
                str(paper_dir),
                "--blind-output",
                str(blind_output),
            ],
            cwd=repo_root,
        )
        report = json.loads(reconcile.stdout)
        if report["result"] != "pass":
            raise AssertionError(f"declared alternative answers should pass: {report}")
        if report["agreement"] != "3/3":
            raise AssertionError(f"unexpected alternative-answer agreement: {report}")

    with tempfile.TemporaryDirectory(prefix="cils-blind-validation-aliases-") as tmp:
        tmp_root = Path(tmp)
        paper_dir = make_paper(tmp_root)
        blind_output = tmp_root / "blind-output.txt"
        write_text(
            blind_output,
            """ANSWERS
{
  "lettura_p1_1": {"answer": "A", "confidence": "hi"},
  "lettura_prova_1_2": {"answer": "B", "confidence": "hi"},
  "strutture_p1_1": {"answer": "il", "confidence": "hi"},
  "scrittura_p1": {"answer": "short sample essay", "confidence": "hi"}
}
FLAGS
[]
""",
        )
        reconcile = run_cmd(
            [
                str(script),
                "reconcile",
                "--paper-dir",
                str(paper_dir),
                "--blind-output",
                str(blind_output),
            ],
            cwd=repo_root,
        )
        report = json.loads(reconcile.stdout)
        if report["result"] != "pass":
            raise AssertionError(f"common blind-solver item aliases should pass: {report}")
        if report["extra_answers"] != []:
            raise AssertionError(f"writing answers should not be counted as objective extras: {report}")

    with tempfile.TemporaryDirectory(prefix="cils-blind-validation-reason-") as tmp:
        tmp_root = Path(tmp)
        paper_dir = make_paper(tmp_root)
        manifest_path = paper_dir / "manifest.yaml"
        manifest_path.write_text(
            manifest_path.read_text(encoding="utf-8") + "reason: validation\n",
            encoding="utf-8",
        )
        blind_output = tmp_root / "blind-output.txt"
        write_text(
            blind_output,
            """ANSWERS
{
  "L1.1": {"answer": "A", "confidence": "hi"},
  "L1.2": {"answer": "B", "confidence": "hi"},
  "S1.1": {"answer": "il", "confidence": "hi"}
}
FLAGS
[]
""",
        )
        run_cmd(
            [
                str(script),
                "reconcile",
                "--paper-dir",
                str(paper_dir),
                "--blind-output",
                str(blind_output),
                "--write-manifest",
            ],
            cwd=repo_root,
        )
        manifest = manifest_path.read_text(encoding="utf-8")
        if "reason: validation" in manifest:
            raise AssertionError(f"passing validation should clear stale validation reason:\n{manifest}")


def main() -> int:
    try:
        run_test()
    except Exception as exc:  # noqa: BLE001 - keep script dependency-free.
        print(f"FAIL: {exc}")
        return 1
    print("PASS: blind validation fixture test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
