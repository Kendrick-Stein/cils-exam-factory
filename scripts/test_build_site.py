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
validation:
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
        assert_not_contains(index, "Fixture Draft Paper")
        assert_not_contains(index, "papers/2000-01-01/FD/")


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
