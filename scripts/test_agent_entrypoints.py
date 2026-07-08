#!/usr/bin/env python3
"""Validate local agent entrypoints for paper generation."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_required(relative_path: str) -> str:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise AssertionError(f"missing required entrypoint: {relative_path}")
    return path.read_text(encoding="utf-8")


def assert_contains(path: str, text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"{path} must mention {needle!r}")


def test_claude_slash_command() -> None:
    path = ".claude/commands/genpapers.md"
    text = read_required(path)
    delegated_skill = read_required(".claude/skills/genpapers/SKILL.md")
    assert_contains(".claude/skills/genpapers/SKILL.md", delegated_skill, "name: genpapers")
    for needle in (
        ".claude/skills/genpapers/SKILL.md",
        "factory/PIPELINE.md",
        "S0",
        "S7",
        "blind",
        "paper.md",
        "only",
        "--no-publish",
        "YYYY-MM-DD-rN",
    ):
        assert_contains(path, text, needle)


def test_codex_make_paper_skill() -> None:
    path = ".codex/skills/make-paper/SKILL.md"
    text = read_required(path)
    for needle in (
        "name: make-paper",
        "Make Paper",
        "genpapers",
        "factory/PIPELINE.md",
        "AGENTS.md",
        "A1,A2,B1,B2,C1",
        "/tmp/cils-blind",
        "paper.md",
        "ONLY",
        "scripts/blind_validation.py prepare",
        "scripts/blind_validation.py reconcile",
        "scripts/paper_status.py",
        "scripts/format_audit.py",
        "scripts/paper_quality_audit.py",
        "codex exec --sandbox read-only",
        "scripts/build_site.py",
        "YYYY-MM-DD-rN",
    ):
        assert_contains(path, text, needle)


def test_docs_point_to_both_entrypoints() -> None:
    docs = {
        "README.md": read_required("README.md"),
        "CLAUDE.md": read_required("CLAUDE.md"),
        "AGENTS.md": read_required("AGENTS.md"),
    }
    for path, text in docs.items():
        assert_contains(path, text, "/genpapers")
        assert_contains(path, text, "Make Paper")
        assert_contains(path, text, "YYYY-MM-DD-rN")


def test_script_docs_cover_validation_helpers() -> None:
    path = "scripts/README.md"
    text = read_required(path)
    for needle in (
        "scripts/blind_validation.py prepare",
        "scripts/blind_validation.py reconcile",
        "Publish gate",
        "zero flags",
        "scripts/paper_quality_audit.py",
        "scripts/format_audit.py",
    ):
        assert_contains(path, text, needle)


def test_pipeline_mentions_deterministic_validation_helpers() -> None:
    path = "factory/PIPELINE.md"
    text = read_required(path)
    for needle in (
        "scripts/blind_validation.py prepare",
        "scripts/blind_validation.py reconcile",
        "publish gate",
        "zero flags",
        "quality_audit",
        "scripts/paper_quality_audit.py",
        "format_audit",
        "git add papers/<date>/<published-levels> docs",
        "scripts/paper_status.py",
    ):
        assert_contains(path, text, needle)


def run_test() -> None:
    test_claude_slash_command()
    test_codex_make_paper_skill()
    test_docs_point_to_both_entrypoints()
    test_script_docs_cover_validation_helpers()
    test_pipeline_mentions_deterministic_validation_helpers()


def main() -> int:
    try:
        run_test()
    except Exception as exc:  # noqa: BLE001 - keep script dependency-free.
        print(f"FAIL: {exc}")
        return 1
    print("PASS: agent entrypoint test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
