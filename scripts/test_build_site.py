#!/usr/bin/env python3
"""Self-contained fixture test for scripts/build_site.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture(root: Path) -> tuple[Path, Path]:
    papers = root / "papers"
    docs = root / "docs"

    published = papers / "2000-01-01" / "FX"
    write_text(
        published / "manifest.yaml",
        """exam: cils
level: FX
session: "2000-01-01"
title: "Fixture Published Paper"
status: published
sources:
  - id: T1
    url: "https://example.com/testo"
    title: "Testo autentico"
    publisher: "Example"
    accessed: "2000-01-01"
    used_in: "Fixture"
    adapted: true
    words_used: 42
quality:
  variant_profile: cils-2024-standard
  source_policy: excerpt-first
  source_attribution: manifest-only
  max_rewrite: light
validation:
  objective_items: 1
  final_agreement: 1
  flags: 0
  result: pass
pipeline:
  stages:
    - stage: blind_validation
      agreement: 1/1
      flags: 0
      result: pass
    - stage: quality_audit
      result: pass
    - stage: format_audit
      result: pass
""",
    )
    write_text(
        published / "paper.md",
        """---
exam: CILS
level: FX
level_name: "Fixture Level"
session: "2000-01-01"
kind: paper
---

# Fascicolo fixture

> Leggi il testo e scegli la risposta corretta.

## Comprensione della lettura

| Item | Risposta |
| --- | --- |
| FX.1 | A |
""",
    )
    write_text(
        published / "answers.md",
        """---
exam: CILS
level: FX
level_name: "Fixture Level"
session: "2000-01-01"
kind: answers
---

# Chiavi fixture

| Item | Chiave |
| --- | --- |
| FX.1 | A |
""",
    )

    draft = papers / "2000-01-01" / "FD"
    write_text(
        draft / "manifest.yaml",
        """exam: cils
level: FD
session: "2000-01-01"
title: "Fixture Draft Paper"
status: draft
sources: []
validation:
  result: fail
""",
    )
    write_text(
        draft / "paper.md",
        """---
exam: CILS
level: FD
level_name: "Fixture Draft"
session: "2000-01-01"
kind: paper
---

# Draft paper
""",
    )
    write_text(
        draft / "answers.md",
        """---
exam: CILS
level: FD
level_name: "Fixture Draft"
session: "2000-01-01"
kind: answers
---

# Draft answers
""",
    )
    return papers, docs


def assert_contains(path: Path, needle: str) -> None:
    text = path.read_text(encoding="utf-8")
    if needle not in text:
        raise AssertionError(f"{path} does not contain expected text: {needle!r}")


def assert_not_contains(path: Path, needle: str) -> None:
    text = path.read_text(encoding="utf-8")
    if needle in text:
        raise AssertionError(f"{path} unexpectedly contains text: {needle!r}")


def run_test() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    build_script = repo_root / "scripts" / "build_site.py"

    with tempfile.TemporaryDirectory(prefix="cils-build-site-") as tmp:
        tmp_root = Path(tmp)
        papers, docs = make_fixture(tmp_root)

        cmd = [
            sys.executable,
            str(build_script),
            "--papers-root",
            str(papers),
            "--out",
            str(docs),
            "--no-pdf",
        ]
        completed = subprocess.run(
            cmd,
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise AssertionError(
                "build_site.py exited with "
                f"{completed.returncode}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )

        paper_dir = docs / "papers" / "2000-01-01" / "FX"
        draft_dir = docs / "papers" / "2000-01-01" / "FD"
        index = docs / "index.html"

        for name in ("paper.html", "answers.html", "paper.md", "answers.md"):
            if not (paper_dir / name).exists():
                raise AssertionError(f"missing expected output: {paper_dir / name}")

        assert_contains(paper_dir / "paper.html", "Fascicolo fixture")
        assert_contains(paper_dir / "paper.html", "Fixture Level")
        assert_contains(paper_dir / "answers.html", "Chiavi fixture")
        assert_contains(paper_dir / "paper.md", "Fascicolo fixture")
        assert_contains(paper_dir / "answers.md", "Chiavi fixture")

        if draft_dir.exists():
            raise AssertionError(f"draft output directory should be absent: {draft_dir}")

        assert_contains(index, "Fixture Published Paper")
        assert_contains(index, "papers/2000-01-01/FX/paper.html")
        assert_contains(index, "papers/2000-01-01/FX/paper.md")
        assert_contains(index, 'class="session-nav"')
        assert_contains(index, 'href="#session-2000-01-01"')
        assert_contains(index, 'class="level-card"')
        assert_contains(index, 'class="download-button download-button-primary"')
        assert_contains(paper_dir / "paper.html", 'class="paper-actions"')
        assert_contains(paper_dir / "paper.html", "Torna all'indice")
        assert_contains(paper_dir / "paper.html", "Scarica Markdown")
        assert_not_contains(index, "Fixture Draft Paper")
        assert_not_contains(index, "papers/2000-01-01/FD/")

    with tempfile.TemporaryDirectory(prefix="cils-build-site-legacy-gate-") as tmp:
        tmp_root = Path(tmp)
        papers, docs = make_fixture(tmp_root)
        manifest = papers / "2000-01-01" / "FX" / "manifest.yaml"
        manifest.write_text(
            manifest.read_text(encoding="utf-8")
            .replace(
                """quality:
  variant_profile: cils-2024-standard
  source_policy: excerpt-first
  source_attribution: manifest-only
  max_rewrite: light
""",
                "",
            )
            .replace(
                "    - stage: quality_audit\n      result: pass\n",
                "",
            ),
            encoding="utf-8",
        )

        cmd = [
            sys.executable,
            str(build_script),
            "--papers-root",
            str(papers),
            "--out",
            str(docs),
            "--no-pdf",
        ]
        completed = subprocess.run(
            cmd,
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise AssertionError(
                "build_site.py should keep building legacy published papers without quality_audit\n"
                f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )
        assert_contains(docs / "index.html", "Fixture Published Paper")

    with tempfile.TemporaryDirectory(prefix="cils-build-site-invalid-") as tmp:
        tmp_root = Path(tmp)
        papers, docs = make_fixture(tmp_root)
        manifest = papers / "2000-01-01" / "FX" / "manifest.yaml"
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace("flags: 0", "flags: 1"),
            encoding="utf-8",
        )

        cmd = [
            sys.executable,
            str(build_script),
            "--papers-root",
            str(papers),
            "--out",
            str(docs),
            "--no-pdf",
        ]
        completed = subprocess.run(
            cmd,
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            raise AssertionError("build_site.py accepted a published paper with validation flags")
        if "publish gate" not in completed.stderr:
            raise AssertionError(
                "expected publish-gate error for invalid published manifest\n"
                f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )

    with tempfile.TemporaryDirectory(prefix="cils-build-site-fail-result-") as tmp:
        tmp_root = Path(tmp)
        papers, docs = make_fixture(tmp_root)
        manifest = papers / "2000-01-01" / "FX" / "manifest.yaml"
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace("result: pass", "result: fail\n  blind_pass: true", 1),
            encoding="utf-8",
        )

        cmd = [
            sys.executable,
            str(build_script),
            "--papers-root",
            str(papers),
            "--out",
            str(docs),
            "--no-pdf",
        ]
        completed = subprocess.run(
            cmd,
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            raise AssertionError("build_site.py accepted result: fail with blind_pass: true")
        if "validation result is not pass" not in completed.stderr:
            raise AssertionError(
                "expected validation result gate error\n"
                f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )

    with tempfile.TemporaryDirectory(prefix="cils-build-site-missing-result-") as tmp:
        tmp_root = Path(tmp)
        papers, docs = make_fixture(tmp_root)
        manifest = papers / "2000-01-01" / "FX" / "manifest.yaml"
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace("  result: pass\n", "  blind_pass: true\n", 1),
            encoding="utf-8",
        )

        cmd = [
            sys.executable,
            str(build_script),
            "--papers-root",
            str(papers),
            "--out",
            str(docs),
            "--no-pdf",
        ]
        completed = subprocess.run(
            cmd,
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            raise AssertionError("build_site.py accepted missing validation.result with blind_pass: true")
        if "validation result is not pass" not in completed.stderr:
            raise AssertionError(
                "expected missing validation result gate error\n"
                f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )

    with tempfile.TemporaryDirectory(prefix="cils-build-site-escape-level-") as tmp:
        tmp_root = Path(tmp)
        papers, docs = make_fixture(tmp_root)
        manifest = papers / "2000-01-01" / "FX" / "manifest.yaml"
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace("level: FX", "level: ../ESCAPE"),
            encoding="utf-8",
        )

        cmd = [
            sys.executable,
            str(build_script),
            "--papers-root",
            str(papers),
            "--out",
            str(docs),
            "--no-pdf",
        ]
        completed = subprocess.run(
            cmd,
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            raise AssertionError("build_site.py accepted a manifest level that escapes output paths")
        if "unsafe level" not in completed.stderr and "level mismatch" not in completed.stderr:
            raise AssertionError(
                "expected unsafe level error\n"
                f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )

    with tempfile.TemporaryDirectory(prefix="cils-build-site-revision-sort-") as tmp:
        tmp_root = Path(tmp)
        papers, docs = make_fixture(tmp_root)
        for revision in ("2000-01-01-r2", "2000-01-01-r9", "2000-01-01-r10"):
            source = papers / "2000-01-01" / "FX"
            target = papers / revision / "FX"
            target.mkdir(parents=True, exist_ok=True)
            for name in ("manifest.yaml", "paper.md", "answers.md"):
                text = (source / name).read_text(encoding="utf-8").replace("2000-01-01", revision)
                write_text(target / name, text)

        cmd = [
            sys.executable,
            str(build_script),
            "--papers-root",
            str(papers),
            "--out",
            str(docs),
            "--no-pdf",
        ]
        completed = subprocess.run(
            cmd,
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise AssertionError(
                "build_site.py failed revision sort fixture\n"
                f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )
        index = (docs / "index.html").read_text(encoding="utf-8")
        if index.find(">2000-01-01-r10<") > index.find(">2000-01-01-r9<"):
            raise AssertionError("revision session r10 should sort before r9")
        if '<h2>2000-01-01-r10</h2>' not in index:
            raise AssertionError("latest revision session r10 should be rendered")

    with tempfile.TemporaryDirectory(prefix="cils-build-site-missing-audit-") as tmp:
        tmp_root = Path(tmp)
        papers, docs = make_fixture(tmp_root)
        manifest = papers / "2000-01-01" / "FX" / "manifest.yaml"
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace(
                "    - stage: format_audit\n      result: pass\n",
                "",
            ),
            encoding="utf-8",
        )

        cmd = [
            sys.executable,
            str(build_script),
            "--papers-root",
            str(papers),
            "--out",
            str(docs),
            "--no-pdf",
        ]
        completed = subprocess.run(
            cmd,
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            raise AssertionError("build_site.py accepted a published paper without format_audit")
        if "format audit" not in completed.stderr:
            raise AssertionError(
                "expected format-audit gate error\n"
                f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )

    with tempfile.TemporaryDirectory(prefix="cils-build-site-missing-quality-audit-") as tmp:
        tmp_root = Path(tmp)
        papers, docs = make_fixture(tmp_root)
        manifest = papers / "2000-01-01" / "FX" / "manifest.yaml"
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace(
                "    - stage: quality_audit\n      result: pass\n",
                "",
            ),
            encoding="utf-8",
        )

        cmd = [
            sys.executable,
            str(build_script),
            "--papers-root",
            str(papers),
            "--out",
            str(docs),
            "--no-pdf",
        ]
        completed = subprocess.run(
            cmd,
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            raise AssertionError("build_site.py accepted a published paper without quality_audit")
        if "quality audit" not in completed.stderr:
            raise AssertionError(
                "expected quality-audit gate error\n"
                f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )

    with tempfile.TemporaryDirectory(prefix="cils-build-site-failed-quality-audit-") as tmp:
        tmp_root = Path(tmp)
        papers, docs = make_fixture(tmp_root)
        manifest = papers / "2000-01-01" / "FX" / "manifest.yaml"
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace(
                "- stage: quality_audit\n      result: pass",
                "- stage: quality_audit\n      result: fail",
            ),
            encoding="utf-8",
        )

        cmd = [
            sys.executable,
            str(build_script),
            "--papers-root",
            str(papers),
            "--out",
            str(docs),
            "--no-pdf",
        ]
        completed = subprocess.run(
            cmd,
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            raise AssertionError("build_site.py accepted a failed quality_audit")
        if "quality audit" not in completed.stderr:
            raise AssertionError(
                "expected failed quality-audit gate error\n"
                f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )

    with tempfile.TemporaryDirectory(prefix="cils-build-site-failed-audit-") as tmp:
        tmp_root = Path(tmp)
        papers, docs = make_fixture(tmp_root)
        manifest = papers / "2000-01-01" / "FX" / "manifest.yaml"
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace(
                "- stage: format_audit\n      result: pass",
                "- stage: format_audit\n      result: fail",
            ),
            encoding="utf-8",
        )

        cmd = [
            sys.executable,
            str(build_script),
            "--papers-root",
            str(papers),
            "--out",
            str(docs),
            "--no-pdf",
        ]
        completed = subprocess.run(
            cmd,
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            raise AssertionError("build_site.py accepted a failed format_audit")
        if "format audit" not in completed.stderr:
            raise AssertionError(
                "expected failed format-audit gate error\n"
                f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )


def main() -> int:
    try:
        run_test()
    except Exception as exc:  # noqa: BLE001 - keep this script stdlib and compact.
        print(f"FAIL: {exc}")
        return 1
    print("PASS: build_site fixture test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
