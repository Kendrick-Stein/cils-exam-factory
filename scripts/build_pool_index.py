#!/usr/bin/env python3
"""Build factory/corpus/pool-index.yaml from factory/corpus/pool/*.md, report coverage.

Run at S1 to refresh the queryable catalogue. `--prune` deletes pool files that are
consumed (their URL is in the used-source blacklist) or stale-perishable. Never runs
automatically. Does not gate publishing.
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from corpus_pool import (
    POOL_DIR, is_stale, load_freshness, normalize_url, parse_pool_file, read_blacklist,
)

INDEX_FIELDS = ["url", "title", "publisher", "published", "fetched", "genre", "cefr",
                "usable_levels", "words", "perishable", "perishable_until",
                "fetch_intent", "source_file"]


def to_index_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {k: entry.get(k) for k in INDEX_FIELDS}


def collect(pool_dir: Path) -> list[dict[str, Any]]:
    return [parse_pool_file(p) for p in sorted(pool_dir.glob("*.md"))]


def parse_today(value: str | None) -> date:
    return date.fromisoformat(value) if value else date.today()


def write_index(entries: list[dict[str, Any]], out_index: Path) -> None:
    ordered = sorted(entries, key=lambda e: (str(e.get("fetched") or ""), str(e.get("url") or "")))
    doc = {
        "generated_by": "scripts/build_pool_index.py",
        "note": "Derived from factory/corpus/pool/*.md. Do not edit by hand — regenerate.",
        "count": len(ordered),
        "sources": [to_index_entry(e) for e in ordered],
    }
    out_index.parent.mkdir(parents=True, exist_ok=True)
    out_index.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")


def report(entries, blacklist, freshness, today) -> None:
    depth: dict[tuple[str, str], int] = defaultdict(int)
    consumed = stale = 0
    for e in entries:
        url_consumed = normalize_url(str(e.get("url", ""))) in blacklist
        entry_stale = is_stale(e, freshness, today)
        if url_consumed:
            consumed += 1
        if entry_stale:
            stale += 1
        if url_consumed or entry_stale:
            continue
        for level in e.get("usable_levels") or []:
            depth[(str(level), str(e.get("genre")))] += 1
    print(f"pool entries : {len(entries)}  (available: {len(entries) - consumed - stale}, "
          f"consumed: {consumed}, stale: {stale})")
    print("available depth per level x genre:")
    for (level, genre), n in sorted(depth.items()):
        print(f"  {level:<4} {genre:<24} {n}")


def prune(entries, blacklist, freshness, today) -> int:
    removed = 0
    for e in entries:
        if normalize_url(str(e.get("url", ""))) in blacklist or is_stale(e, freshness, today):
            Path(e["source_file"]).unlink(missing_ok=True)
            removed += 1
    return removed


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pool-dir", type=Path, default=POOL_DIR)
    p.add_argument("--out-index", type=Path, default=Path("factory/corpus/pool-index.yaml"))
    p.add_argument("--blacklist", type=Path, default=Path("factory/corpus/used-sources.txt"))
    p.add_argument("--sources", type=Path, default=Path("factory/corpus/sources.yaml"))
    p.add_argument("--today", default=None, help="YYYY-MM-DD override for freshness (tests)")
    p.add_argument("--prune", action="store_true", help="delete consumed/stale pool files")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if not args.pool_dir.is_dir():
        args.pool_dir.mkdir(parents=True, exist_ok=True)
    today = parse_today(args.today)
    blacklist = read_blacklist(args.blacklist)
    freshness = load_freshness(args.sources)
    entries = collect(args.pool_dir)
    if args.prune:
        removed = prune(entries, blacklist, freshness, today)
        print(f"pruned {removed} file(s)")
        entries = collect(args.pool_dir)
    write_index(entries, args.out_index)
    report(entries, blacklist, freshness, today)
    print(f"\nwrote {args.out_index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
