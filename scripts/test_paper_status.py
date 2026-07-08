#!/usr/bin/env python3
"""Fixture tests for scripts/paper_status.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_level(root: Path, level: str, manifest: str, files: tuple[str, ...] = ()) -> None:
    level_dir = root / "papers" / "2000-01-03" / level
    write_text(level_dir / "manifest.yaml", manifest)
    for name in files:
        write_text(level_dir / name, f"{name} fixture\n")


def run_test() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "paper_status.py"

    with tempfile.TemporaryDirectory(prefix="cils-paper-status-") as tmp:
        tmp_root = Path(tmp)
        papers_root = tmp_root / "papers"
        make_level(
            tmp_root,
            "A1",
            """exam: cils
level: A1
session: "2000-01-03"
status: published
sources: [{id: T1}]
pipeline:
  stages:
    - stage: corpus
    - stage: authoring
    - stage: blind_validation
      agreement: 1/1
      flags: 0
      result: pass
    - stage: quality_audit
      result: pass
    - stage: format_audit
      result: pass
validation:
  objective_items: 1
  final_agreement: 1
  flags: 0
  mismatches: 0
  result: pass
""",
            ("paper.md", "answers.md", "key.json", "sources.md"),
        )
        make_level(
            tmp_root,
            "A2",
            """exam: cils
level: A2
session: "2000-01-03"
status: published
sources: [{id: T1}]
pipeline:
  stages:
    - stage: corpus
    - stage: authoring
    - stage: blind_validation
      agreement: 1/1
      flags: 0
      result: pass
    - stage: format_audit
      result: pass
validation:
  objective_items: 1
  final_agreement: 1
  flags: 0
  mismatches: 0
  result: pass
""",
            ("paper.md", "answers.md", "key.json", "sources.md"),
        )
        make_level(
            tmp_root,
            "B1",
            """exam: cils
level: B1
session: "2000-01-03"
status: draft
sources: [{id: T1}]
quality:
  variant_profile: cils-2024-standard
  source_policy: excerpt-first
  source_attribution: manifest-only
  max_rewrite: light
pipeline:
  stages:
    - stage: corpus
    - stage: authoring
validation:
  result: fail
""",
            ("paper.md", "answers.md", "key.json", "sources.md"),
        )
        make_level(
            tmp_root,
            "B2",
            """exam: cils
level: B2
session: "2000-01-03"
status: draft
sources: []
pipeline: {stages: []}
""",
            (),
        )
        make_level(
            tmp_root,
            "C1",
            """exam: cils
level: C1
session: "2000-01-03"
status: published
sources: [{id: T1}]
quality:
  variant_profile: cils-2024-standard
  source_policy: excerpt-first
  source_attribution: manifest-only
  max_rewrite: light
pipeline:
  stages:
    - stage: corpus
    - stage: authoring
    - stage: blind_validation
      agreement: 1/1
      flags: 0
      result: pass
    - stage: format_audit
      result: pass
validation:
  objective_items: 1
  final_agreement: 1
  flags: 0
  mismatches: 0
  result: pass
""",
            ("paper.md", "answers.md", "key.json", "sources.md"),
        )

        completed = subprocess.run(
            [
                sys.executable,
                str(script),
                "--papers-root",
                str(papers_root),
                "--session",
                "2000-01-03",
                "--levels",
                "A1,A2,B1,B2,C1",
            ],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise AssertionError(
                f"paper_status.py failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )
        report = json.loads(completed.stdout)
        by_level = {entry["level"]: entry for entry in report["levels"]}

        if by_level["A1"]["publishable"] is not True:
            raise AssertionError(f"A1 should be publishable: {by_level['A1']}")
        if by_level["A2"]["publishable"] is not True:
            raise AssertionError(f"A2 legacy paper should remain publishable: {by_level['A2']}")
        if any("quality_audit" in issue for issue in by_level["A2"]["issues"]):
            raise AssertionError(f"A2 legacy paper should not require quality audit: {by_level['A2']}")
        if by_level["B1"]["next_stage"] != "blind_validation":
            raise AssertionError(f"B1 should need blind validation: {by_level['B1']}")
        if "missing stage: blind_validation" not in by_level["B1"]["issues"]:
            raise AssertionError(f"B1 should report missing blind validation: {by_level['B1']}")
        if by_level["B2"]["next_stage"] != "corpus":
            raise AssertionError(f"B2 should need corpus: {by_level['B2']}")
        if "missing file: paper.md" not in by_level["B2"]["issues"]:
            raise AssertionError(f"B2 should report missing files: {by_level['B2']}")
        if by_level["C1"]["publishable"] is not False:
            raise AssertionError(f"C1 should not be publishable without quality audit: {by_level['C1']}")
        if by_level["C1"]["next_stage"] != "quality_audit":
            raise AssertionError(f"C1 should need quality audit: {by_level['C1']}")
        if "missing stage: quality_audit" not in by_level["C1"]["issues"]:
            raise AssertionError(f"C1 should report missing quality audit: {by_level['C1']}")
        if report["summary"] != {"publishable": 2, "draft": 2, "missing": 0}:
            raise AssertionError(f"unexpected summary: {report['summary']}")

    with tempfile.TemporaryDirectory(prefix="cils-paper-status-unsafe-") as tmp:
        tmp_root = Path(tmp)
        papers_root = tmp_root / "papers"
        completed = subprocess.run(
            [
                sys.executable,
                str(script),
                "--papers-root",
                str(papers_root),
                "--session",
                "../escape",
                "--levels",
                "A1",
            ],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            raise AssertionError("paper_status.py accepted unsafe session")
        if "unsafe session" not in completed.stderr:
            raise AssertionError(f"expected unsafe session error, got:\n{completed.stderr}")

        completed = subprocess.run(
            [
                sys.executable,
                str(script),
                "--papers-root",
                str(papers_root),
                "--session",
                "2000-01-03",
                "--levels",
                "../escape",
            ],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            raise AssertionError("paper_status.py accepted unsafe level")
        if "unsafe level" not in completed.stderr:
            raise AssertionError(f"expected unsafe level error, got:\n{completed.stderr}")


def main() -> int:
    try:
        run_test()
    except Exception as exc:  # noqa: BLE001 - keep script dependency-free.
        print(f"FAIL: {exc}")
        return 1
    print("PASS: paper status fixture test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
