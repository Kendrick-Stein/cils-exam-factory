#!/usr/bin/env python3
"""Bank one graded, cleaned text into factory/corpus/pool/<id>.md.

Called during S1 over-fetch to store every fetched+graded candidate not immediately
used, so cross-level-usable fetches are never wasted. The id is sha1 of the normalized
URL, making banking idempotent and dedup-safe. A URL already consumed (in the used-source
blacklist) or already pooled is skipped.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Any

import yaml

from corpus_pool import POOL_DIR, load_freshness, normalize_url, read_blacklist

FRONT_ORDER = ["url", "title", "publisher", "published", "fetched", "genre", "cefr",
               "usable_levels", "words", "perishable", "perishable_until", "fetch_intent"]


def pool_id(url: str) -> str:
    return hashlib.sha1(normalize_url(url).encode("utf-8")).hexdigest()[:12]


def resolve_perishable(mode: str, genre: str, freshness: dict[str, int]) -> bool:
    if mode == "yes":
        return True
    if mode == "no":
        return False
    return genre in freshness  # auto: a genre with a window is perishable by default


def build_meta(args: argparse.Namespace, freshness: dict[str, int]) -> dict[str, Any]:
    levels = [s for s in (args.usable_levels or "").split(",") if s] or [args.cefr]
    return {
        "url": args.url.strip(),
        "title": args.title,
        "publisher": args.publisher,
        "published": args.published,
        "fetched": args.fetched,
        "genre": args.genre,
        "cefr": args.cefr,
        "usable_levels": levels,
        "words": args.words,
        "perishable": resolve_perishable(args.perishable, args.genre, freshness),
        "perishable_until": args.perishable_until,
        "fetch_intent": args.fetch_intent,
    }


def render(meta: dict[str, Any], body: str) -> str:
    ordered = {k: meta.get(k) for k in FRONT_ORDER}
    front = yaml.safe_dump(ordered, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{front}\n---\n\n{body.strip()}\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pool-dir", type=Path, default=POOL_DIR)
    p.add_argument("--sources", type=Path, default=Path("factory/corpus/sources.yaml"))
    p.add_argument("--blacklist", type=Path, default=Path("factory/corpus/used-sources.txt"))
    p.add_argument("--url", required=True)
    p.add_argument("--title", default=None)
    p.add_argument("--publisher", default=None)
    p.add_argument("--published", default=None)
    p.add_argument("--fetched", required=True)
    p.add_argument("--genre", required=True)
    p.add_argument("--cefr", required=True)
    p.add_argument("--usable-levels", default=None, help="comma-separated, e.g. B1,B2")
    p.add_argument("--words", type=int, default=None)
    p.add_argument("--perishable", choices=["auto", "yes", "no"], default="auto")
    p.add_argument("--perishable-until", default=None)
    p.add_argument("--fetch-intent", default=None)
    p.add_argument("--text-file", type=Path, default=None, help="body file; omit to read stdin")
    p.add_argument("--overwrite", action="store_true")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if normalize_url(args.url) in read_blacklist(args.blacklist):
        print(f"skip (already consumed): {args.url}")
        return 0
    out = args.pool_dir / f"{pool_id(args.url)}.md"
    if out.exists() and not args.overwrite:
        print(f"skip (already pooled): {out}")
        return 0
    body = args.text_file.read_text(encoding="utf-8") if args.text_file else sys.stdin.read()
    meta = build_meta(args, load_freshness(args.sources))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(meta, body), encoding="utf-8")
    print(f"banked {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
