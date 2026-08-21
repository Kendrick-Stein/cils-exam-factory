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

        # The site ships PDFs only: the rendered page and the markdown copy are
        # print intermediates and are unlinked once the PDF exists, so with
        # --no-pdf a published level leaves no per-paper artifact at all.
        leftovers = sorted(path.name for path in paper_dir.glob("*")) if paper_dir.exists() else []
        if leftovers:
            raise AssertionError(f"render intermediates should not survive the build: {leftovers}")

        if draft_dir.exists():
            raise AssertionError(f"draft output directory should be absent: {draft_dir}")

        assert_contains(index, 'class="chip chip-FX"')
        assert_contains(index, 'id="sessione-2000-01-01"')
        assert_contains(index, 'class="paper-card reveal"')
        assert_contains(index, 'class="arch-row"')
        assert_not_contains(index, "Fixture Draft Paper")
        assert_not_contains(index, "papers/2000-01-01/FD/")
        assert_not_contains(index, 'chip-FD')

    with tempfile.TemporaryDirectory(prefix="cils-build-site-pdf-links-") as tmp:
        # The index only offers a download once the PDF is on disk; seeding the PDFs
        # pins that wiring without needing Chrome in the test environment.
        tmp_root = Path(tmp)
        papers, docs = make_fixture(tmp_root)
        paper_dir = docs / "papers" / "2000-01-01" / "FX"
        paper_dir.mkdir(parents=True, exist_ok=True)
        for stem in ("paper", "answers"):
            (paper_dir / f"{stem}.pdf").write_bytes(b"%PDF-1.4 fixture\n")

        completed = subprocess.run(
            [
                sys.executable,
                str(build_script),
                "--papers-root",
                str(papers),
                "--out",
                str(docs),
                "--no-pdf",
            ],
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

        for stem in ("paper", "answers"):
            if not (paper_dir / f"{stem}.pdf").exists():
                raise AssertionError(f"published {stem}.pdf should survive the build")
        index = docs / "index.html"
        assert_contains(index, 'href="papers/2000-01-01/FX/paper.pdf"')
        assert_contains(index, 'href="papers/2000-01-01/FX/answers.pdf"')
        assert_not_contains(index, "papers/2000-01-01/FD/answers.pdf")

    with tempfile.TemporaryDirectory(prefix="cils-build-site-rendered-page-") as tmp:
        # paper.html never ships, but it is what Chrome prints, so its shape still matters.
        tmp_root = Path(tmp)
        papers, _ = make_fixture(tmp_root)
        sys.path.insert(0, str(repo_root / "scripts"))
        import build_site

        paper_root = papers / "2000-01-01" / "FX"
        paper = build_site.Paper(
            date="2000-01-01",
            level="FX",
            root=paper_root,
            manifest=build_site.load_yaml(paper_root / "manifest.yaml"),
        )
        page = build_site.render_page(paper_root / "paper.md", paper, "paper")
        for needle in ("Fascicolo fixture", "Fixture Level", 'class="paper-actions"', "Torna all'indice"):
            if needle not in page:
                raise AssertionError(f"rendered paper page is missing {needle!r}")
        answers_page = build_site.render_page(paper_root / "answers.md", paper, "answers")
        if "Chiavi fixture" not in answers_page:
            raise AssertionError("rendered answers page is missing its body")

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
        assert_contains(docs / "index.html", 'class="chip chip-FX"')

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
        if 'id="sessione-2000-01-01-r10"' not in index:
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
