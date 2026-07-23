#!/usr/bin/env python3
"""Select available pool texts for a slot: level + genre + length, minus consumed/stale.

S1 calls this first; only slots it can't fill fall back to a live corpus-hunter fetch.
Ranks perishable-newer first, then closeness of word count to the band centre.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

from corpus_pool import is_stale, load_freshness, load_yaml, normalize_url, read_blacklist


def parse_today(value: str | None) -> date:
    return date.fromisoformat(value) if value else date.today()


def parse_band(spec: str | None) -> tuple[int, int] | None:
    if not spec:
        return None
    lo, _, hi = spec.partition("-")
    return int(lo), int(hi)


def in_band(words: Any, band: tuple[int, int] | None) -> bool:
    if band is None:
        return True
    if not isinstance(words, int):
        return False
    return band[0] <= words <= band[1]


def rank_key(entry: dict[str, Any], band: tuple[int, int] | None):
    centre = (band[0] + band[1]) / 2 if band else 0
    words = entry.get("words") if isinstance(entry.get("words"), int) else centre
    return (str(entry.get("published") or entry.get("fetched") or ""),
            -abs(words - centre))


def select(index: dict[str, Any], *, level, genre, band, blacklist, freshness, today, include_stale):
    out = []
    for entry in index.get("sources") or []:
        if level and level not in (entry.get("usable_levels") or []):
            continue
        if genre and str(entry.get("genre")) != genre:
            continue
        if not in_band(entry.get("words"), band):
            continue
        if normalize_url(str(entry.get("url", ""))) in blacklist:
            continue
        if not include_stale and is_stale(entry, freshness, today):
            continue
        out.append(entry)
    out.sort(key=lambda e: rank_key(e, band), reverse=True)
    return out


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pool-index", type=Path, default=Path("factory/corpus/pool-index.yaml"))
    p.add_argument("--blacklist", type=Path, default=Path("factory/corpus/used-sources.txt"))
    p.add_argument("--sources", type=Path, default=Path("factory/corpus/sources.yaml"))
    p.add_argument("--level", default=None)
    p.add_argument("--genre", default=None)
    p.add_argument("--words", default=None, help="band 'min-max'")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--include-stale", action="store_true")
    p.add_argument("--today", default=None)
    p.add_argument("--json", action="store_true")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if not args.pool_index.exists():
        print("[]" if args.json else "pool index not found (empty pool)")
        return 0
    index = load_yaml(args.pool_index)
    results = select(
        index, level=args.level, genre=args.genre, band=parse_band(args.words),
        blacklist=read_blacklist(args.blacklist), freshness=load_freshness(args.sources),
        today=parse_today(args.today), include_stale=args.include_stale,
    )[: args.limit]
    if args.json:
        print(json.dumps(results, ensure_ascii=False))
        return 0
    if not results:
        print("no available pool candidate for this slot")
        return 0
    for entry in results:
        print(f"{entry.get('cefr','?'):<3} {entry.get('words','?'):>4}w  "
              f"{entry.get('genre','?'):<22} {entry.get('source_file','?')}")
        print(f"     {entry.get('title') or ''}  <{entry.get('url')}>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
