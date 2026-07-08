#!/usr/bin/env python3
"""Deterministic format audit for generated CILS papers."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("python3 -m pip install --user pyyaml", file=sys.stderr)
    raise SystemExit(2)


SAFE_SESSION_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:-r[1-9]\d*)?$")
SAFE_LEVEL_RE = re.compile(r"^[A-Za-z0-9_-]+$")
FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
READING_HEADING_RE = re.compile(
    r"^##\s+Comprensione della lettura\s+[—-]\s+Prova n\.\s+(\d+)\s*$",
    re.MULTILINE,
)
STRUCTURE_HEADING_RE = re.compile(
    r"^##\s+Analisi delle strutture di comunicazione\s+[—-]\s+Prova n\.\s+(\d+)\s*$",
    re.MULTILINE,
)
WRITING_HEADING_RE = re.compile(
    r"^##\s+Produzione scritta\s+[—-]\s+Prova n\.\s+(\d+)\s*$",
    re.MULTILINE,
)
ATTRIBUTION_RE = re.compile(r"\*Testo adattato da:", re.IGNORECASE)
SOURCE_FOOTER_RE = re.compile(r"Fonti citate sotto ogni testo", re.IGNORECASE)
STUDY_AID_MARKERS = (
    "Glossario da ricordare",
    "Chiavi",
    "Spiegazione",
    "中文",
    "范文",
    "Espressioni utili",
)
INLINE_POINT_LEVELS = {"B2", "C1"}
REQUIRED_FILES = ("manifest.yaml", "paper.md", "answers.md", "key.json", "sources.md")
ORDERED_MARKERS = (
    ("answer_sheet", "ESEMPIO DI FOGLIO DELLE RISPOSTE"),
    ("reading_section", "# Test di comprensione della lettura"),
    ("structure_section", "# Test di analisi delle strutture di comunicazione"),
    ("writing_section", "# Test di produzione scritta"),
    ("answer_sheet_final", "# Foglio delle risposte"),
)


class FormatAuditError(Exception):
    """User-facing format audit error."""


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise FormatAuditError(f"cannot read {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise FormatAuditError(f"malformed YAML in {path}: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise FormatAuditError(f"malformed YAML in {path}: expected mapping")
    return data


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def issue(level: str, issue_id: str, message: str, path: Path | None = None) -> dict[str, str]:
    payload = {"level": level, "id": issue_id, "message": message}
    if path is not None:
        payload["path"] = str(path)
    return payload


def parse_levels(raw: str) -> list[str]:
    levels = [level.strip() for level in raw.split(",") if level.strip()]
    if not levels:
        raise FormatAuditError("at least one level is required")
    for level in levels:
        if not SAFE_LEVEL_RE.fullmatch(level):
            raise FormatAuditError(f"unsafe level value: {level!r}")
    return levels


def front_matter(path: Path, text: str) -> dict[str, Any]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        raise FormatAuditError(f"malformed YAML front matter in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise FormatAuditError(f"malformed YAML front matter in {path}: expected mapping")
    return data


def level_spec(exam: dict[str, Any], level: str) -> dict[str, Any]:
    levels = exam.get("levels")
    if not isinstance(levels, dict):
        return {}
    spec = levels.get(level)
    return spec if isinstance(spec, dict) else {}


def expected_prove(spec: dict[str, Any], section_id: str) -> list[int]:
    for section in spec.get("sections") or []:
        if not isinstance(section, dict) or section.get("id") != section_id:
            continue
        numbers: list[int] = []
        for prova in section.get("prove") or []:
            if not isinstance(prova, dict):
                continue
            try:
                numbers.append(int(prova["n"]))
            except (KeyError, TypeError, ValueError):
                continue
        return numbers
    return []


def found_prove(text: str, pattern: re.Pattern[str]) -> list[int]:
    return [int(match.group(1)) for match in pattern.finditer(text)]


def audit_required_files(level: str, level_dir: Path) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for name in REQUIRED_FILES:
        path = level_dir / name
        if not path.exists():
            issues.append(issue(level, f"file.missing_{Path(name).stem}", f"missing {name}", path))
    return issues


def audit_front_matter(
    level: str,
    session: str,
    manifest_path: Path,
    manifest: dict[str, Any],
    paper_path: Path,
    paper_text: str,
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if str(manifest.get("level") or level) != level:
        issues.append(issue(level, "manifest.level_mismatch", "manifest level must match directory level", manifest_path))
    if str(manifest.get("session") or session) != session:
        issues.append(issue(level, "manifest.session_mismatch", "manifest session must match requested session", manifest_path))
    fm = front_matter(paper_path, paper_text)
    if fm:
        if str(fm.get("level") or level) != level:
            issues.append(issue(level, "paper.level_mismatch", "paper front matter level must match directory level", paper_path))
        if str(fm.get("session") or session) != session:
            issues.append(issue(level, "paper.session_mismatch", "paper front matter session must match requested session", paper_path))
    else:
        issues.append(issue(level, "paper.front_matter_missing", "paper.md should have YAML front matter", paper_path))
    return issues


def audit_marker_order(level: str, paper_path: Path, paper_text: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    positions: list[int] = []
    for marker_id, marker in ORDERED_MARKERS:
        position = paper_text.find(marker)
        if position < 0:
            issues.append(issue(level, f"format.missing_{marker_id}", f"missing marker: {marker}", paper_path))
        else:
            positions.append(position)
    if len(positions) == len(ORDERED_MARKERS) and positions != sorted(positions):
        issues.append(issue(level, "format.section_order", "answer-sheet example, tests, writing, and final answer sheet are out of order", paper_path))
    return issues


def audit_prova_counts(level: str, paper_path: Path, paper_text: str, spec: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    checks = (
        ("reading", "lettura", READING_HEADING_RE),
        ("structure", "strutture", STRUCTURE_HEADING_RE),
        ("writing", "scritta", WRITING_HEADING_RE),
    )
    for label, section_id, pattern in checks:
        expected = expected_prove(spec, section_id)
        if not expected:
            continue
        found = found_prove(paper_text, pattern)
        if found != expected:
            issues.append(
                issue(
                    level,
                    f"format.{label}_prove",
                    f"{label} prova headings are {found}; expected {expected}",
                    paper_path,
                )
            )
    return issues


def audit_paper_style(level: str, paper_path: Path, paper_text: str) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if "Quaderno di esame" not in paper_text:
        issues.append(issue(level, "format.quaderno_heading", "missing Quaderno di esame cover signal", paper_path))
    if "ESEMPIO DI FOGLIO DELLE RISPOSTE" not in paper_text:
        issues.append(issue(level, "format.answer_sheet_example", "missing official-style answer-sheet example", paper_path))
    if ATTRIBUTION_RE.search(paper_text) or SOURCE_FOOTER_RE.search(paper_text):
        issues.append(issue(level, "format.visible_source_attribution", "student paper should keep source attribution out of paper.md", paper_path))
    if level in INLINE_POINT_LEVELS and "Punteggio massimo:" in paper_text:
        issues.append(issue(level, "format.inline_points", "B2/C1 student booklets should not print inline per-prova point statements", paper_path))
    for marker in STUDY_AID_MARKERS:
        if marker in paper_text:
            issues.append(issue(level, "format.study_aid_in_paper", f"study aid marker {marker!r} belongs in answers.md", paper_path))
    return issues


def audit_key_json(level: str, key_path: Path) -> list[dict[str, str]]:
    try:
        data = json.loads(key_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return [issue(level, "key.unreadable", f"cannot read key.json: {exc}", key_path)]
    except json.JSONDecodeError as exc:
        return [issue(level, "key.malformed", f"malformed key.json: {exc}", key_path)]
    if not isinstance(data, dict) or not data:
        return [issue(level, "key.empty", "key.json must be a non-empty JSON object", key_path)]
    return []


def append_format_stage(manifest_path: Path, manifest: dict[str, Any], level_issues: list[dict[str, str]]) -> None:
    pipeline = manifest.setdefault("pipeline", {})
    if not isinstance(pipeline, dict):
        pipeline = {}
        manifest["pipeline"] = pipeline
    stages = pipeline.setdefault("stages", [])
    if not isinstance(stages, list):
        stages = []
        pipeline["stages"] = stages
    stages.append(
        {
            "stage": "format_audit",
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "result": "pass" if not level_issues else "fail",
            "issues": len(level_issues),
        }
    )
    if level_issues:
        manifest["status"] = "draft"
        manifest["reason"] = "format_audit"
    write_yaml(manifest_path, manifest)


def audit(args: argparse.Namespace) -> dict[str, Any]:
    if not SAFE_SESSION_RE.fullmatch(args.session):
        raise FormatAuditError(f"unsafe session value: {args.session!r}")
    levels = parse_levels(args.levels)
    exam = load_yaml(args.exam)
    session_root = args.papers_root / args.session

    issues: list[dict[str, str]] = []
    manifests: dict[str, dict[str, Any]] = {}
    manifest_paths: dict[str, Path] = {}

    for level in levels:
        level_dir = session_root / level
        file_issues = audit_required_files(level, level_dir)
        issues.extend(file_issues)
        if file_issues:
            continue

        manifest_path = level_dir / "manifest.yaml"
        paper_path = level_dir / "paper.md"
        key_path = level_dir / "key.json"
        manifest = load_yaml(manifest_path)
        paper_text = paper_path.read_text(encoding="utf-8")
        spec = level_spec(exam, level)

        manifests[level] = manifest
        manifest_paths[level] = manifest_path
        issues.extend(audit_front_matter(level, args.session, manifest_path, manifest, paper_path, paper_text))
        issues.extend(audit_marker_order(level, paper_path, paper_text))
        issues.extend(audit_prova_counts(level, paper_path, paper_text, spec))
        issues.extend(audit_paper_style(level, paper_path, paper_text))
        issues.extend(audit_key_json(level, key_path))

    if args.write_manifest:
        issues_by_level: dict[str, list[dict[str, str]]] = defaultdict(list)
        for found in issues:
            issues_by_level[str(found["level"])].append(found)
        for level, manifest in manifests.items():
            append_format_stage(manifest_paths[level], manifest, issues_by_level.get(level, []))

    return {
        "session": args.session,
        "levels": levels,
        "result": "pass" if not issues else "fail",
        "issues": issues,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit generated CILS papers for official-style formatting.")
    parser.add_argument("--papers-root", type=Path, default=Path("papers"), help="papers root")
    parser.add_argument("--session", required=True, help="session date YYYY-MM-DD or revision YYYY-MM-DD-rN")
    parser.add_argument("--levels", default="A1,A2,B1,B2,C1", help="comma-separated levels")
    parser.add_argument("--exam", type=Path, default=Path("factory/exams/cils/exam.yaml"), help="exam.yaml path")
    parser.add_argument("--report", type=Path, help="write JSON report to this path")
    parser.add_argument("--write-manifest", action="store_true", help="append format_audit stage to manifests")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = audit(args)
    except FormatAuditError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
