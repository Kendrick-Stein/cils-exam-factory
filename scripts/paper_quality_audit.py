#!/usr/bin/env python3
"""Audit generated papers for CILS fidelity beyond blind-answer agreement."""

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


WORD_RE = re.compile(r"\b[\wÀ-ÿ']+\b", re.UNICODE)
HEADING_RE = re.compile(r"^#{1,2}\s+", re.MULTILINE)
PROVA_HEADING_RE = re.compile(
    r"^##\s+Comprensione della lettura\s+[—-]\s+Prova n\.\s+(\d+)\s*$",
    re.MULTILINE,
)
STRUCTURE_HEADING_RE = re.compile(
    r"^##\s+Analisi delle strutture di comunicazione\s+[—-]\s+Prova n\.\s+(\d+)\s*$",
    re.MULTILINE,
)
TEXT_TITLE_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
ATTRIBUTION_RE = re.compile(r"\*Testo adattato da:", re.IGNORECASE)
DEPTH_MARKERS = (
    "secondo il testo",
    "emerge",
    "scopo",
    "funzione",
    "principale",
    "dipende",
    "perché",
    "causa",
    "intenzione",
    "si afferma",
    "si deduce",
    "presenta",
    "viene ricondotta",
    "quale informazione",
)
STUDY_AID_MARKERS = (
    "Glossario da ricordare",
    "Chiavi",
    "Spiegazione",
    "中文",
    "范文",
    "Espressioni utili",
)
INLINE_POINT_LEVELS = {"B2", "C1"}
SAFE_SESSION_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:-r[1-9]\d*)?$")
SAFE_LEVEL_RE = re.compile(r"^[A-Za-z0-9_-]+$")


class AuditError(Exception):
    """User-facing audit error."""


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise AuditError(f"cannot read {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise AuditError(f"malformed YAML in {path}: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise AuditError(f"malformed YAML in {path}: expected mapping")
    return data


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def split_front_matter(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[index + 1 :]).lstrip("\n")
    return text


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def normalize_url(url: str) -> str:
    return url.strip().rstrip("/").lower()


def issue(level: str, issue_id: str, message: str, path: Path | None = None) -> dict[str, str]:
    payload = {"level": level, "id": issue_id, "message": message}
    if path is not None:
        payload["path"] = str(path)
    return payload


def level_spec(exam: dict[str, Any], level: str) -> dict[str, Any]:
    levels = exam.get("levels")
    if not isinstance(levels, dict) or level not in levels:
        return {}
    spec = levels[level]
    return spec if isinstance(spec, dict) else {}


def variant_profiles(exam: dict[str, Any]) -> dict[str, dict[str, Any]]:
    profiles = exam.get("variant_profiles")
    if not isinstance(profiles, dict):
        return {}
    normalized: dict[str, dict[str, Any]] = {}
    for name, profile in profiles.items():
        if isinstance(name, str) and isinstance(profile, dict):
            normalized[name] = profile
    return normalized


def section_prove(spec: dict[str, Any], section_id: str) -> dict[int, dict[str, Any]]:
    for section in spec.get("sections") or []:
        if isinstance(section, dict) and section.get("id") == section_id:
            prove: dict[int, dict[str, Any]] = {}
            for prova in section.get("prove") or []:
                if isinstance(prova, dict) and "n" in prova:
                    try:
                        prove[int(prova["n"])] = prova
                    except (TypeError, ValueError):
                        continue
            return prove
    return {}


def reading_prove(spec: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return section_prove(spec, "lettura")


def structure_prove(spec: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return section_prove(spec, "strutture")


def expected_source_slots(spec: dict[str, Any]) -> set[str]:
    slots: set[str] = set()
    for section in spec.get("sections") or []:
        if not isinstance(section, dict):
            continue
        for prova in section.get("prove") or []:
            if not isinstance(prova, dict):
                continue
            testo = prova.get("testo")
            if isinstance(testo, dict) and isinstance(testo.get("slot"), str):
                slots.add(testo["slot"])
    return slots


def slot_is_covered(slot: str, source_ids: set[str]) -> bool:
    if slot in source_ids:
        return True
    return any(re.fullmatch(re.escape(slot) + r"[a-z][a-z0-9_-]*", source_id) for source_id in source_ids)


def prova_block(body: str, prova_number: int, heading_re: re.Pattern[str] = PROVA_HEADING_RE) -> str:
    matches = list(heading_re.finditer(body))
    for index, match in enumerate(matches):
        if int(match.group(1)) != prova_number:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        analysis_start = re.search(r"^#\s+Test di analisi", body[start:end], re.MULTILINE)
        if analysis_start:
            end = start + analysis_start.start()
        return body[start:end]
    return ""


def adapted_text_from_block(block: str, stop_table: bool = False) -> str:
    title_match = TEXT_TITLE_RE.search(block)
    if title_match:
        text_start = title_match.end()
        end_candidates = [len(block)]
        patterns = [ATTRIBUTION_RE, re.compile(r"^>\s*", re.MULTILINE), re.compile(r"^---\s*$", re.MULTILINE)]
        if stop_table:
            patterns.append(re.compile(r"^\|", re.MULTILINE))
            patterns.append(re.compile(r"^\*\*\d+\.", re.MULTILINE))
        for pattern in patterns:
            found = pattern.search(block, text_start)
            if found:
                end_candidates.append(found.start())
        text_end = min(end_candidates)
        text = block[text_start:text_end]
    else:
        text = re.split(r"(?m)^---\s*$", block, maxsplit=1)[0]
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    text = re.sub(r"^>\s*.*$", " ", text, flags=re.MULTILINE)
    text = re.sub(r"^\*Testo adattato da:.*$", " ", text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r"\|", " ", text)
    return text.strip()


def text_length_issues(
    level: str,
    paper_path: Path,
    body: str,
    prove: dict[int, dict[str, Any]],
    heading_re: re.Pattern[str],
    issue_id: str,
    label: str,
    stop_table: bool = False,
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for prova_number, prova in sorted(prove.items()):
        testo = prova.get("testo") if isinstance(prova, dict) else None
        if not isinstance(testo, dict) or "parole" not in testo or testo["parole"] is None:
            continue
        try:
            minimum, maximum = [int(value) for value in testo["parole"]]
        except (TypeError, ValueError):
            continue
        block = prova_block(body, prova_number, heading_re)
        if not block:
            issues.append(issue(level, f"format.missing_{issue_id}", f"missing {label} prova {prova_number}", paper_path))
            continue
        count = word_count(adapted_text_from_block(block, stop_table=stop_table))
        if count < minimum or count > maximum:
            issues.append(
                issue(
                    level,
                    f"length.{issue_id}",
                    f"{label} prova {prova_number} has {count} words; expected {minimum}-{maximum}",
                    paper_path,
                )
            )
    return issues


def l1_item_stems(block: str) -> list[str]:
    stems = re.findall(r"^\s*\d+\.\s+\*\*(.+?)\*\*", block, flags=re.MULTILINE)
    if stems:
        return stems
    stems = []
    for line in block.splitlines():
        if re.match(r"^\s*\d+\.\s+", line):
            stems.append(re.sub(r"^\s*\d+\.\s+", "", line).strip("* "))
    return stems


def audit_manifest(level: str, manifest_path: Path, manifest: dict[str, Any], exam: dict[str, Any], spec: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    quality = manifest.get("quality")
    profile_name = quality.get("variant_profile") if isinstance(quality, dict) else None
    profiles = variant_profiles(exam)
    if not isinstance(profile_name, str) or not profile_name:
        issues.append(
            issue(
                level,
                "manifest.variant_profile",
                "manifest must declare quality.variant_profile for the selected official/variant profile",
                manifest_path,
            )
        )
    elif profiles and profile_name not in profiles:
        issues.append(
            issue(
                level,
                "manifest.variant_profile_unknown",
                f"quality.variant_profile {profile_name!r} is not defined in exam.yaml",
                manifest_path,
            )
        )
    elif profiles:
        allowed_levels = profiles[profile_name].get("levels")
        if isinstance(allowed_levels, list) and level not in {str(value) for value in allowed_levels}:
            issues.append(
                issue(
                    level,
                    "manifest.variant_profile_level",
                    f"quality.variant_profile {profile_name!r} is not valid for level {level}",
                    manifest_path,
                )
            )
    if not isinstance(quality, dict) or quality.get("source_policy") != "excerpt-first":
        issues.append(
            issue(
                level,
                "manifest.source_policy",
                "manifest must declare quality.source_policy: excerpt-first",
                manifest_path,
            )
        )
    if not isinstance(quality, dict) or quality.get("source_attribution") != "manifest-only":
        issues.append(
            issue(
                level,
                "manifest.source_attribution",
                "manifest must declare quality.source_attribution: manifest-only",
                manifest_path,
            )
        )
    if isinstance(quality, dict) and quality.get("max_rewrite") not in {"none", "light", "level_simplification"}:
        issues.append(
            issue(
                level,
                "manifest.max_rewrite",
                "manifest quality.max_rewrite must bound rewriting to none, light, or level_simplification",
                manifest_path,
            )
        )
    elif not isinstance(quality, dict):
        issues.append(
            issue(
                level,
                "manifest.max_rewrite",
                "manifest must declare quality.max_rewrite",
                manifest_path,
            )
        )

    sources = manifest.get("sources")
    source_ids: set[str] = set()
    if isinstance(sources, list):
        for source in sources:
            if not isinstance(source, dict):
                continue
            if isinstance(source.get("id"), str):
                source_ids.add(source["id"])
            if "words_used" not in source:
                issues.append(
                    issue(
                        level,
                        "manifest.source_words_used",
                        f"source {source.get('id', '<unknown>')} must declare words_used after authoring",
                        manifest_path,
                    )
                )
    else:
        issues.append(issue(level, "manifest.sources", "manifest must list source entries", manifest_path))
    missing_slots = sorted(slot for slot in expected_source_slots(spec) if not slot_is_covered(slot, source_ids))
    for slot in missing_slots:
        issues.append(
            issue(
                level,
                "manifest.source_slot_missing",
                f"manifest sources must include slot {slot} required by exam.yaml",
                manifest_path,
            )
        )
    return issues


def audit_paper(level: str, paper_path: Path, paper_text: str, spec: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    body = split_front_matter(paper_text)
    if "Quaderno di esame" not in body:
        issues.append(issue(level, "format.quaderno_heading", "paper should expose an official-style Quaderno di esame cover signal", paper_path))
    if "ESEMPIO DI FOGLIO DELLE RISPOSTE" not in body:
        issues.append(issue(level, "format.answer_sheet_example", "paper should include an official-style answer-sheet example before tests", paper_path))
    for marker in STUDY_AID_MARKERS:
        if marker in body:
            issues.append(issue(level, "format.study_aid_in_paper", f"study aid marker {marker!r} belongs in answers.md, not paper.md", paper_path))
    if ATTRIBUTION_RE.search(body):
        issues.append(issue(level, "format.visible_source_attribution", "student paper should not print source attribution lines; keep sources in manifest.yaml", paper_path))
    if level in INLINE_POINT_LEVELS and "Punteggio massimo:" in body:
        issues.append(issue(level, "format.inline_points", "B2/C1 official-style student booklets should not print inline per-prova point statements", paper_path))

    issues.extend(
        text_length_issues(
            level,
            paper_path,
            body,
            reading_prove(spec),
            PROVA_HEADING_RE,
            "reading_text",
            "reading",
        )
    )
    issues.extend(
        text_length_issues(
            level,
            paper_path,
            body,
            structure_prove(spec),
            STRUCTURE_HEADING_RE,
            "structure_text",
            "structure",
            stop_table=True,
        )
    )

    if level in {"B2", "C1"}:
        block = prova_block(body, 1)
        stems = l1_item_stems(block)
        marked = 0
        for stem in stems:
            lowered = stem.casefold()
            if any(marker in lowered for marker in DEPTH_MARKERS):
                marked += 1
        if len(stems) >= 4 and marked < 3:
            issues.append(
                issue(
                    level,
                    "depth.reading_items",
                    f"reading prova 1 has only {marked}/{len(stems)} interpretive stems; use more purpose, cause, inference, and author's-framing questions",
                    paper_path,
                )
            )
    return issues


def audit_cross_level_sources(session_root: Path, manifests: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    by_url: dict[str, list[str]] = defaultdict(list)
    for level, manifest in manifests.items():
        for source in manifest.get("sources") or []:
            if not isinstance(source, dict) or not source.get("url"):
                continue
            if source.get("allow_cross_level_reuse") is True:
                continue
            by_url[normalize_url(str(source["url"]))].append(level)

    issues: list[dict[str, str]] = []
    for url, levels in sorted(by_url.items()):
        unique_levels = sorted(set(levels))
        if len(unique_levels) > 1:
            issues.append(
                {
                    "level": ",".join(unique_levels),
                    "id": "source.cross_level_duplicate",
                    "message": f"source URL reused across levels {', '.join(unique_levels)}: {url}",
                    "path": str(session_root),
                }
            )
    return issues


def append_quality_stage(manifest_path: Path, manifest: dict[str, Any], level_issues: list[dict[str, str]]) -> None:
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
            "stage": "quality_audit",
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "result": "pass" if not level_issues else "fail",
            "issues": len(level_issues),
        }
    )
    quality = manifest.setdefault("quality", {})
    if isinstance(quality, dict):
        quality["audit_result"] = "pass" if not level_issues else "fail"
        quality["audit_issues"] = len(level_issues)
    if level_issues:
        manifest["status"] = "draft"
        manifest["reason"] = "quality_audit"
    write_yaml(manifest_path, manifest)


def audit(args: argparse.Namespace) -> dict[str, Any]:
    exam = load_yaml(args.exam)
    if not SAFE_SESSION_RE.fullmatch(args.session):
        raise AuditError(f"unsafe session value: {args.session!r}")
    levels = [level.strip() for level in args.levels.split(",") if level.strip()]
    if not levels:
        raise AuditError("at least one level is required")
    for level in levels:
        if not SAFE_LEVEL_RE.fullmatch(level):
            raise AuditError(f"unsafe level value: {level!r}")

    session_root = args.papers_root / args.session
    manifests: dict[str, dict[str, Any]] = {}
    manifest_paths: dict[str, Path] = {}
    issues: list[dict[str, str]] = []

    for level in levels:
        level_dir = session_root / level
        manifest_path = level_dir / "manifest.yaml"
        paper_path = level_dir / "paper.md"
        if not manifest_path.exists():
            issues.append(issue(level, "manifest.missing", "missing manifest.yaml", manifest_path))
            continue
        if not paper_path.exists():
            issues.append(issue(level, "paper.missing", "missing paper.md", paper_path))
            continue
        manifest = load_yaml(manifest_path)
        manifests[level] = manifest
        manifest_paths[level] = manifest_path
        spec = level_spec(exam, level)
        issues.extend(audit_manifest(level, manifest_path, manifest, exam, spec))
        paper_text = paper_path.read_text(encoding="utf-8")
        issues.extend(audit_paper(level, paper_path, paper_text, spec))

    issues.extend(audit_cross_level_sources(session_root, manifests))

    if args.write_manifest:
        issues_by_level: dict[str, list[dict[str, str]]] = defaultdict(list)
        for found in issues:
            for level in str(found["level"]).split(","):
                issues_by_level[level].append(found)
        for level, manifest in manifests.items():
            append_quality_stage(manifest_paths[level], manifest, issues_by_level.get(level, []))

    return {
        "session": args.session,
        "levels": levels,
        "result": "pass" if not issues else "fail",
        "issues": issues,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit generated CILS papers for quality and official-style fidelity.")
    parser.add_argument("--papers-root", type=Path, default=Path("papers"), help="papers root")
    parser.add_argument("--session", required=True, help="session date YYYY-MM-DD or revision YYYY-MM-DD-rN")
    parser.add_argument("--levels", default="A1,A2,B1,B2,C1", help="comma-separated levels")
    parser.add_argument("--exam", type=Path, default=Path("factory/exams/cils/exam.yaml"), help="exam.yaml path")
    parser.add_argument("--report", type=Path, help="write JSON report to this path")
    parser.add_argument("--write-manifest", action="store_true", help="append quality_audit stage to manifests")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = audit(args)
    except AuditError as exc:
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
