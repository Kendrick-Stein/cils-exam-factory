#!/usr/bin/env python3
"""Assemble paper.md, answers.md and key.json from per-prova fragment files.

Fragments live in papers/<date>/<LEVEL>/fragments/*.json, one per prova/task:

    {
      "prova": "L1",
      "slots":        {"T1_TITLE": "...", "T1_TEXT": "...", "L1_ITEMS": "..."},
      "answer_slots": {"ANS_L1_ROWS": "| L1.1 | B | ... |"},
      "key":          {"L1.1": "B", "L1.2": "C"}
    }

The template supplies everything immutable (cover, consegne, answer sheets,
section skeletons); the LLM only ever produces fragment content. This script
substitutes all {{SLOTS}}, splits at <!-- ANSWERS -->, strips template
comments, merges keys, and fails loudly on missing slots or duplicate IDs.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("python3 -m pip install --user pyyaml", file=sys.stderr)
    raise SystemExit(2)

SLOT_RE = re.compile(r"\{\{([A-Za-z0-9_]+)\}\}")
COMMENT_RE = re.compile(r"<!--.*?-->[ \t]*\n?", re.DOTALL)
BLANKS_RE = re.compile(r"\n{3,}")
ANSWERS_MARKER = "<!-- ANSWERS -->"
DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")
KEY_ORDER_RE = re.compile(r"^([LSW])(\d+)(?:\.(\d+))?$")
ITALIAN_MONTHS = [
    "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
    "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre",
]


class AssembleError(Exception):
    """User-facing assembly error."""


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise AssembleError(f"cannot read {path}: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise AssembleError(f"malformed YAML in {path}: expected mapping")
    return data


def session_human(session: str) -> str:
    match = DATE_RE.match(session)
    if not match:
        raise AssembleError(f"cannot derive human date from session {session!r}")
    year, month, day = match.groups()
    return f"{int(day)} {ITALIAN_MONTHS[int(month) - 1]} {year}"


def key_sort(item_id: str) -> tuple[int, int, int, str]:
    match = KEY_ORDER_RE.match(item_id)
    if not match:
        return (9, 99, 9999, item_id)
    section = {"L": 0, "S": 1, "W": 2}[match.group(1)]
    return (section, int(match.group(2)), int(match.group(3) or 0), item_id)


def load_fragments(fragments_dir: Path) -> tuple[dict[str, str], dict[str, str], list[str]]:
    if not fragments_dir.is_dir():
        raise AssembleError(f"missing fragments dir: {fragments_dir}")
    paths = sorted(fragments_dir.glob("*.json"))
    if not paths:
        raise AssembleError(f"no fragment *.json files in {fragments_dir}")

    substitutions: dict[str, str] = {}
    slot_origin: dict[str, str] = {}
    key: dict[str, str] = {}
    names: list[str] = []
    for path in paths:
        try:
            fragment = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AssembleError(f"malformed fragment {path}: {exc}") from exc
        if not isinstance(fragment, dict):
            raise AssembleError(f"fragment {path} must be a JSON object")
        names.append(path.stem)
        for field in ("slots", "answer_slots"):
            slots = fragment.get(field) or {}
            if not isinstance(slots, dict):
                raise AssembleError(f"fragment {path} field {field} must be an object")
            for name, value in slots.items():
                if name in substitutions:
                    raise AssembleError(
                        f"slot {name} defined by both {slot_origin[name]} and {path.name}"
                    )
                substitutions[name] = str(value)
                slot_origin[name] = path.name
        fragment_key = fragment.get("key") or {}
        if not isinstance(fragment_key, dict):
            raise AssembleError(f"fragment {path} field key must be an object")
        for item_id, answer in fragment_key.items():
            if item_id in key:
                raise AssembleError(f"duplicate key id {item_id} (fragment {path.name})")
            key[str(item_id)] = str(answer)
    return substitutions, key, names


def substitute(text: str, substitutions: dict[str, str]) -> tuple[str, set[str]]:
    missing: set[str] = set()

    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in substitutions:
            return substitutions[name]
        missing.add(name)
        return match.group(0)

    return SLOT_RE.sub(repl, text), missing


def clean(part: str) -> str:
    part = COMMENT_RE.sub("", part)
    part = BLANKS_RE.sub("\n\n", part)
    return part.strip("\n") + "\n"


def assemble(args: argparse.Namespace) -> int:
    paper_dir: Path = args.paper_dir
    manifest = load_yaml(paper_dir / "manifest.yaml")
    session = str(manifest.get("session") or paper_dir.parent.name)

    template_path = args.template
    if template_path is None:
        declared = (manifest.get("pipeline") or {}).get("template")
        if not declared:
            raise AssembleError("no --template and manifest has no pipeline.template")
        template_path = Path(declared)
    template = template_path.read_text(encoding="utf-8")
    if ANSWERS_MARKER not in template:
        raise AssembleError(f"template {template_path} lacks {ANSWERS_MARKER}")

    substitutions, key, fragment_names = load_fragments(args.fragments_dir or paper_dir / "fragments")
    substitutions.setdefault("SESSION", session)
    substitutions.setdefault("SESSION_HUMAN", session_human(session))

    substituted, missing = substitute(template, substitutions)
    if missing:
        raise AssembleError(
            "unfilled template slots: " + ", ".join(sorted(missing))
            + f" (fragments present: {', '.join(fragment_names)})"
        )
    if not key:
        raise AssembleError("fragments define no key entries")

    paper_part, answers_part = substituted.split(ANSWERS_MARKER, 1)
    (paper_dir / "paper.md").write_text(clean(paper_part), encoding="utf-8")
    (paper_dir / "answers.md").write_text(clean(answers_part), encoding="utf-8")
    ordered_key = {item_id: key[item_id] for item_id in sorted(key, key=key_sort)}
    (paper_dir / "key.json").write_text(
        json.dumps(ordered_key, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "paper": str(paper_dir / "paper.md"),
                "answers": str(paper_dir / "answers.md"),
                "key_items": len(ordered_key),
                "fragments": fragment_names,
                "slots_filled": len(substitutions),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assemble a paper from per-prova fragments.")
    parser.add_argument("--paper-dir", type=Path, required=True, help="papers/<date>/<LEVEL> directory")
    parser.add_argument("--template", type=Path, help="template path (default: manifest pipeline.template)")
    parser.add_argument("--fragments-dir", type=Path, help="fragments dir (default: <paper-dir>/fragments)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        return assemble(parse_args(sys.argv[1:] if argv is None else argv))
    except AssembleError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
