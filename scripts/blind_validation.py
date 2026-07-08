#!/usr/bin/env python3
"""Prepare and reconcile blind-solver validation for generated papers."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("python3 -m pip install --user pyyaml", file=sys.stderr)
    raise SystemExit(2)


class ValidationError(Exception):
    """A user-facing validation error."""


SAFE_SESSION = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SAFE_LEVEL = re.compile(r"^[A-Za-z0-9_-]+$")
ANSWER_ID_ALIASES = (
    (re.compile(r"^lettura_p(\d+)_(\d+)$", re.IGNORECASE), "L"),
    (re.compile(r"^lettura_prova_(\d+)_(\d+)$", re.IGNORECASE), "L"),
    (re.compile(r"^comprensione_p(\d+)_(\d+)$", re.IGNORECASE), "L"),
    (re.compile(r"^strutture_p(\d+)_(\d+)$", re.IGNORECASE), "S"),
    (re.compile(r"^strutture_prova_(\d+)_(\d+)$", re.IGNORECASE), "S"),
    (re.compile(r"^analisi_p(\d+)_(\d+)$", re.IGNORECASE), "S"),
)
WRITING_ID = re.compile(r"^(?:scrittura|writing)_p?\d+$|^W\d+$", re.IGNORECASE)


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValidationError(f"malformed YAML in {path}: {exc}") from exc
    except OSError as exc:
        raise ValidationError(f"cannot read {path}: {exc}") from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValidationError(f"malformed YAML in {path}: expected a mapping")
    return data


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def load_key(path: Path) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"malformed JSON in {path}: {exc}") from exc
    except OSError as exc:
        raise ValidationError(f"cannot read {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValidationError(f"malformed key in {path}: expected an object")
    return {str(item_id): str(answer).strip() for item_id, answer in data.items()}


def json_after_marker(text: str, marker: str, expected_type: type) -> Any:
    marker_index = text.find(marker)
    if marker_index < 0:
        raise ValidationError(f"blind output is missing {marker} section")

    start_candidates = [index for index in (text.find("{", marker_index), text.find("[", marker_index)) if index >= 0]
    if not start_candidates:
        raise ValidationError(f"blind output {marker} section has no JSON payload")
    start = min(start_candidates)

    decoder = json.JSONDecoder()
    try:
        payload, _ = decoder.raw_decode(text[start:])
    except json.JSONDecodeError as exc:
        raise ValidationError(f"blind output {marker} section is not valid JSON: {exc}") from exc

    if not isinstance(payload, expected_type):
        raise ValidationError(f"blind output {marker} section has wrong JSON type")
    return payload


def first_json_payload(text: str) -> Any:
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char not in "[{":
            continue
        try:
            payload, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        return payload
    raise ValidationError("blind output has no JSON payload")


def normalize_answers(raw_answers: dict[str, Any]) -> dict[str, str]:
    answers: dict[str, str] = {}
    for item_id, value in raw_answers.items():
        if isinstance(value, dict):
            answer = value.get("answer")
        else:
            answer = value
        if answer is None:
            continue
        answers[str(item_id)] = str(answer).strip()
    return answers


def normalize_item_id(item_id: str) -> str | None:
    cleaned = item_id.strip()
    if WRITING_ID.fullmatch(cleaned):
        return None
    for pattern, prefix in ANSWER_ID_ALIASES:
        match = pattern.fullmatch(cleaned)
        if match:
            return f"{prefix}{int(match.group(1))}.{int(match.group(2))}"
    return cleaned


def normalize_flags(raw_flags: list[Any]) -> list[dict[str, str]]:
    flags: list[dict[str, str]] = []
    for raw_flag in raw_flags:
        if isinstance(raw_flag, str):
            flags.append({"item_id": raw_flag, "reason": "flagged by blind solver"})
            continue
        if not isinstance(raw_flag, dict):
            raise ValidationError("blind output FLAGS entries must be strings or objects")
        item_id = raw_flag.get("item_id") or raw_flag.get("item")
        reason = raw_flag.get("reason") or "flagged by blind solver"
        if not item_id:
            raise ValidationError("blind output FLAGS entry is missing item/item_id")
        flags.append({"item_id": str(item_id), "reason": str(reason)})
    return flags


def parse_blind_output(path: Path) -> tuple[dict[str, str], list[dict[str, str]]]:
    text = path.read_text(encoding="utf-8")
    if "FLAGS" in text and ("ANSWERS" in text or "ANSWER" in text):
        answer_marker = "ANSWERS" if "ANSWERS" in text else "ANSWER"
        answers = normalize_answers(json_after_marker(text, answer_marker, dict))
        flags = normalize_flags(json_after_marker(text, "FLAGS", list))
        return answers, flags

    payload = first_json_payload(text)
    if not isinstance(payload, dict):
        raise ValidationError("blind output JSON payload must be an object")

    raw_answers = payload.get("answers", payload.get("ANSWERS"))
    if raw_answers is None:
        raw_answers = payload
        raw_flags: list[Any] = []
    else:
        raw_flags = payload.get("flags", payload.get("FLAGS", []))
    if not isinstance(raw_answers, dict):
        raise ValidationError("blind output answers must be an object")
    if not isinstance(raw_flags, list):
        raise ValidationError("blind output flags must be a list")
    answers = normalize_answers(raw_answers)
    flags = normalize_flags(raw_flags)
    return answers, flags


def collapse_split_sequence_answers(key: dict[str, str], blind_answers: dict[str, str]) -> dict[str, str]:
    collapsed = dict(blind_answers)
    for item_id, expected in key.items():
        if item_id in collapsed or "-" not in expected:
            continue

        expected_parts = [part.strip() for part in expected.split("-") if part.strip()]
        if not expected_parts:
            continue

        pattern = re.compile(rf"^{re.escape(item_id)}\.(\d+)$")
        split_items: list[tuple[int, str, str]] = []
        for blind_item_id, answer in blind_answers.items():
            match = pattern.fullmatch(blind_item_id)
            if match:
                split_items.append((int(match.group(1)), blind_item_id, answer))
        split_items.sort()

        positions = [position for position, _, _ in split_items]
        expected_positions = list(range(1, len(expected_parts) + 1))
        if positions != expected_positions:
            continue

        collapsed[item_id] = "-".join(answer for _, _, answer in split_items)
        for _, blind_item_id, _ in split_items:
            collapsed.pop(blind_item_id, None)
    return collapsed


def answers_match(expected: str, actual: str | None) -> bool:
    if actual is None:
        return False
    if actual.casefold() == expected.casefold():
        return True
    if "-" in expected:
        expected_parts = [part.casefold() for part in re.split(r"\s*-\s*", expected.strip()) if part]
        actual_parts = [part.casefold() for part in re.split(r"[\s,-]+", actual.strip()) if part]
        if expected_parts and expected_parts == actual_parts:
            return True
    if not expected.endswith("'"):
        return False
    return actual.casefold().startswith(expected.casefold()) and len(actual) > len(expected)


def compare_answers(key: dict[str, str], blind_answers: dict[str, str], flags: list[dict[str, str]]) -> dict[str, Any]:
    blind_answers = {
        normalized_item_id: answer
        for item_id, answer in blind_answers.items()
        if (normalized_item_id := normalize_item_id(item_id)) is not None
    }
    blind_answers = collapse_split_sequence_answers(key, blind_answers)
    mismatches: list[dict[str, Any]] = []
    matches = 0
    for item_id, expected in key.items():
        actual = blind_answers.get(item_id)
        if answers_match(expected, actual):
            matches += 1
        else:
            mismatches.append({"item_id": item_id, "expected": expected, "actual": actual})

    key_items = set(key)
    extra_answers = sorted(item_id for item_id in blind_answers if item_id not in key_items)

    failing_by_id: dict[str, dict[str, Any]] = {}
    for mismatch in mismatches:
        failing_by_id[mismatch["item_id"]] = {
            "item_id": mismatch["item_id"],
            "reason": "key_mismatch",
            "expected": mismatch["expected"],
            "actual": mismatch["actual"],
        }
    for flag in flags:
        item_id = flag["item_id"]
        failing_by_id[item_id] = {
            **failing_by_id.get(item_id, {"item_id": item_id}),
            "flag": flag["reason"],
        }

    total = len(key)
    result = "pass" if matches == total and not flags and not extra_answers else "fail"
    return {
        "result": result,
        "objective_items": total,
        "final_agreement": matches,
        "agreement": f"{matches}/{total}",
        "mismatches": mismatches,
        "flags": flags,
        "extra_answers": extra_answers,
        "failing_items": list(failing_by_id.values()),
    }


def command_prepare(args: argparse.Namespace) -> int:
    paper_dir = args.paper_dir
    paper_path = paper_dir / "paper.md"
    manifest_path = paper_dir / "manifest.yaml"
    if not paper_path.exists():
        raise ValidationError(f"missing paper.md: {paper_path}")

    manifest = load_yaml(manifest_path) if manifest_path.exists() else {}
    session = str(manifest.get("session") or paper_dir.parent.name)
    level = str(manifest.get("level") or paper_dir.name)
    if not SAFE_SESSION.fullmatch(session):
        raise ValidationError(f"unsafe session value for blind directory: {session!r}")
    if not SAFE_LEVEL.fullmatch(level):
        raise ValidationError(f"unsafe level value for blind directory: {level!r}")
    isolated_dir = args.tmp_root / f"cils-blind-{session}-{level}"
    tmp_root = args.tmp_root.resolve()
    resolved_isolated_dir = isolated_dir.resolve()
    if not resolved_isolated_dir.is_relative_to(tmp_root):
        raise ValidationError(f"unsafe blind directory outside tmp root: {isolated_dir}")

    if isolated_dir.exists():
        shutil.rmtree(isolated_dir)
    isolated_dir.mkdir(parents=True)
    isolated_paper = isolated_dir / "paper.md"
    shutil.copy2(paper_path, isolated_paper)

    prompt = (
        "You are a candidate taking a CILS exam. Solve the paper at "
        f"{isolated_paper} using ONLY that file. Return: (1) ANSWERS as JSON "
        'object {"item_id": {"answer": "...", "confidence": "hi|med|lo"}}, '
        "(2) FLAGS as JSON array for ambiguous or unanswerable items, "
        "(3) WRITING checks. Use item IDs by section: L<prova>.<n> for "
        "Comprensione della lettura, S<prova>.<n> for Analisi delle strutture, "
        "and W<prova> only for writing checks. For reading reconstruction, either "
        "return the whole sequence as L3 or each slot as L3.<n>. Do not open any "
        "other file or the web."
    )
    print(
        json.dumps(
            {
                "isolated_paper": str(isolated_paper),
                "prompt": prompt,
                "codex_args": ["codex", "exec", "--sandbox", "read-only", prompt],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def update_manifest(paper_dir: Path, report: dict[str, Any]) -> None:
    manifest_path = paper_dir / "manifest.yaml"
    manifest = load_yaml(manifest_path)
    pipeline = manifest.setdefault("pipeline", {})
    if not isinstance(pipeline, dict):
        raise ValidationError(f"manifest pipeline must be a mapping: {manifest_path}")
    stages = pipeline.setdefault("stages", [])
    if not isinstance(stages, list):
        raise ValidationError(f"manifest pipeline.stages must be a list: {manifest_path}")

    stages.append(
        {
            "stage": "blind_validation",
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "agreement": report["agreement"],
            "flags": len(report["flags"]),
            "result": report["result"],
        }
    )
    manifest["validation"] = {
        "objective_items": report["objective_items"],
        "final_agreement": report["final_agreement"],
        "agreement": report["agreement"],
        "flags": len(report["flags"]),
        "mismatches": len(report["mismatches"]),
        "result": report["result"],
    }
    if report["result"] != "pass":
        manifest["status"] = "draft"
        manifest["reason"] = "validation"
    elif manifest.get("reason") == "validation":
        manifest.pop("reason")
    write_yaml(manifest_path, manifest)


def command_reconcile(args: argparse.Namespace) -> int:
    paper_dir = args.paper_dir
    key = load_key(paper_dir / "key.json")
    blind_answers, flags = parse_blind_output(args.blind_output)
    report = compare_answers(key, blind_answers, flags)

    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.write_manifest:
        update_manifest(paper_dir, report)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare and reconcile blind validation.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="copy paper.md into an isolated blind directory")
    prepare.add_argument("--paper-dir", type=Path, required=True, help="papers/<date>/<LEVEL> directory")
    prepare.add_argument("--tmp-root", type=Path, default=Path("/tmp"), help="root for isolated blind dir")
    prepare.set_defaults(func=command_prepare)

    reconcile = subparsers.add_parser("reconcile", help="compare blind-solver output with key.json")
    reconcile.add_argument("--paper-dir", type=Path, required=True, help="papers/<date>/<LEVEL> directory")
    reconcile.add_argument("--blind-output", type=Path, required=True, help="file containing ANSWERS and FLAGS JSON")
    reconcile.add_argument("--report", type=Path, help="optional JSON report output path")
    reconcile.add_argument("--write-manifest", action="store_true", help="append manifest blind_validation stage")
    reconcile.set_defaults(func=command_reconcile)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        return args.func(args)
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
