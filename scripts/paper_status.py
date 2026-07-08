#!/usr/bin/env python3
"""Report generation and publish status for paper sessions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from build_site import BuildError, load_yaml, validate_publish_gate


REQUIRED_FILES = ("paper.md", "answers.md", "key.json", "sources.md")
REQUIRED_STAGES = ("corpus", "authoring", "blind_validation", "format_audit")


class StatusError(Exception):
    """A user-facing status error."""


def parse_levels(raw: str) -> list[str]:
    return [level.strip() for level in raw.split(",") if level.strip()]


def stage_names(manifest: dict[str, Any]) -> list[str]:
    pipeline = manifest.get("pipeline") or {}
    stages = pipeline.get("stages") if isinstance(pipeline, dict) else []
    if not isinstance(stages, list):
        return []
    names: list[str] = []
    for stage in stages:
        if isinstance(stage, dict) and stage.get("stage"):
            names.append(str(stage["stage"]))
    return names


def next_stage_for(issues: list[str]) -> str | None:
    for stage in REQUIRED_STAGES:
        if f"missing stage: {stage}" in issues:
            return stage
    for file_name, stage in (
        ("sources.md", "corpus"),
        ("paper.md", "authoring"),
        ("answers.md", "authoring"),
        ("key.json", "authoring"),
    ):
        if f"missing file: {file_name}" in issues:
            return stage
    return None


def level_status(papers_root: Path, session: str, level: str) -> dict[str, Any]:
    level_dir = papers_root / session / level
    manifest_path = level_dir / "manifest.yaml"
    if not manifest_path.exists():
        return {
            "level": level,
            "path": str(level_dir),
            "status": "missing",
            "publishable": False,
            "next_stage": "scaffold",
            "issues": ["missing manifest.yaml"],
        }

    manifest = load_yaml(manifest_path)
    issues: list[str] = []
    for file_name in REQUIRED_FILES:
        if not (level_dir / file_name).exists():
            issues.append(f"missing file: {file_name}")

    stages = stage_names(manifest)
    for stage in REQUIRED_STAGES:
        if stage not in stages:
            issues.append(f"missing stage: {stage}")

    publishable = False
    publish_gate_error = None
    if manifest.get("status") == "published":
        try:
            validate_publish_gate(manifest_path, manifest)
            publishable = True
        except BuildError as exc:
            publish_gate_error = str(exc)
            issues.append(str(exc))
    else:
        validation = manifest.get("validation")
        if not isinstance(validation, dict) or validation.get("result") != "pass":
            issues.append("validation not pass")

    return {
        "level": level,
        "path": str(level_dir),
        "status": str(manifest.get("status") or "draft"),
        "publishable": publishable,
        "next_stage": None if publishable else next_stage_for(issues),
        "issues": issues,
        "publish_gate_error": publish_gate_error,
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    levels = parse_levels(args.levels)
    if not levels:
        raise StatusError("at least one level is required")
    level_reports = [level_status(args.papers_root, args.session, level) for level in levels]
    summary = {
        "publishable": sum(1 for report in level_reports if report["publishable"]),
        "draft": sum(1 for report in level_reports if report["status"] == "draft"),
        "missing": sum(1 for report in level_reports if report["status"] == "missing"),
    }
    return {
        "session": args.session,
        "papers_root": str(args.papers_root),
        "summary": summary,
        "levels": level_reports,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report paper pipeline status by level.")
    parser.add_argument("--papers-root", type=Path, default=Path("papers"), help="papers root")
    parser.add_argument("--session", required=True, help="session date YYYY-MM-DD")
    parser.add_argument("--levels", default="A1,A2,B1,B2,C1", help="comma-separated levels")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = build_report(args)
    except (BuildError, StatusError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
