#!/usr/bin/env python3
"""Shared helpers for the corpus text pool (pool_add / build_pool_index / pool_select).

The pool is `factory/corpus/pool/<id>.md`: a YAML front-matter block + cleaned body.
This module is the single source of truth for the pool-file schema, the consumed-URL
blacklist reader, and the per-text freshness rule, so the banker, index-builder and
selector cannot disagree.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - environment guard
    raise SystemExit("PyYAML is required: pip install pyyaml")

POOL_DIR = Path("factory/corpus/pool")
FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

# Fallback windows (months) if sources.yaml has no `freshness:` block.
DEFAULT_FRESHNESS = {"news_general": 12, "news_easy": 12, "practical_realia": 6}


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"malformed YAML in {path}: expected mapping")
    return data


def normalize_url(url: str) -> str:
    """Match build_used_index / paper_quality_audit so URL identity agrees everywhere."""
    return url.strip().rstrip("/").lower()


def parse_pool_file(path: Path) -> dict[str, Any]:
    """Parse a pool markdown file into {**front_matter, body, source_file}."""
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_RE.match(text)
    if not match:
        raise ValueError(f"{path}: missing YAML front matter")
    meta = yaml.safe_load(match.group(1)) or {}
    if not isinstance(meta, dict):
        raise ValueError(f"{path}: front matter is not a mapping")
    meta = dict(meta)
    meta["body"] = match.group(2).strip()
    meta["source_file"] = str(path)
    return meta


def read_blacklist(path: Path) -> set[str]:
    """Normalized URLs already consumed (used-sources.txt). Missing file -> empty set."""
    if not path.exists():
        return set()
    urls: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            urls.add(normalize_url(stripped))
    return urls


def load_freshness(sources_yaml: Path) -> dict[str, int]:
    """Genre -> perishable window (months) from sources.yaml `freshness:` block."""
    if not sources_yaml.exists():
        return dict(DEFAULT_FRESHNESS)
    fresh = load_yaml(sources_yaml).get("freshness")
    if not isinstance(fresh, dict):
        return dict(DEFAULT_FRESHNESS)
    return {str(k): int(v) for k, v in fresh.items() if v is not None}


def parse_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if not value:
        return None
    match = _DATE_RE.search(str(value))
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(0))
    except ValueError:
        return None


def add_months(base: date, months: int) -> date:
    index = base.month - 1 + months
    year = base.year + index // 12
    month = index % 12 + 1
    leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    days_in_month = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return date(year, month, min(base.day, days_in_month[month - 1]))


def is_stale(entry: dict[str, Any], freshness: dict[str, int], today: date) -> bool:
    """A perishable entry past its explicit expiry or genre window is stale.
    Evergreen entries (perishable falsey) are never stale."""
    if not entry.get("perishable"):
        return False
    explicit = parse_date(entry.get("perishable_until"))
    if explicit is not None:
        return today > explicit
    window = freshness.get(str(entry.get("genre")))
    if window is None:
        return False
    base = parse_date(entry.get("published")) or parse_date(entry.get("fetched"))
    if base is None:
        return False
    return today > add_months(base, window)
