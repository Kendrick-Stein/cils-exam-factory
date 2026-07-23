#!/usr/bin/env python3
"""Build the central used-source index from every published/draft manifest.

Cross-date source de-duplication used to rely on a hand-maintained
`papers/<date>/used-sources.txt` that the orchestrator remembered to seed into
the S1 prompt. Nothing enforced or regenerated it. This script derives the
registry deterministically from the authoritative record — the `sources:`
blocks of every `papers/<session>/<LEVEL>/manifest.yaml` — and emits:

  * factory/corpus/used-index.yaml  — rich, queryable: url -> {title, publisher,
    genre, first_used, times_used, uses:[{date, level, prova, words, status}]}
  * factory/corpus/used-sources.txt — flat sorted URL blacklist for S1 injection

Run at the start of S1 to refresh the blacklist from all prior sessions. It does
not gate publishing (per user directive 2026-07-23); it is an aggregation +
injection aid, not an audit.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - environment guard
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    raise

SAFE_SESSION_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:-r[1-9]\d*)?$")
DOMAIN_TOKEN_RE = re.compile(r"[a-z0-9.-]+\.[a-z]{2,}")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"malformed YAML in {path}: expected mapping")
    return data


def normalize_url(url: str) -> str:
    """Match paper_quality_audit.normalize_url so the two agree on identity."""
    return url.strip().rstrip("/").lower()


def clean_str(value: Any) -> str | None:
    """Coerce a manifest field to a trimmed string. Lists (e.g. a used_in that
    feeds several prove) are joined; None/empty become None."""
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        parts = [clean_str(item) for item in value]
        joined = "; ".join(part for part in parts if part)
        return joined or None
    text = str(value).strip()
    return text or None


def url_domain(url: str) -> str:
    host = urlsplit(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def build_genre_map(sources_yaml: Path) -> dict[str, str]:
    """Map whitelist domain token -> genre category from sources.yaml.

    `site` fields can be messy ("comune.bologna.it / comune.milano.it / altri
    comuni"), so we harvest every domain-shaped token from each entry.
    """
    if not sources_yaml.exists():
        return {}
    data = load_yaml(sources_yaml)
    domain_to_genre: dict[str, str] = {}
    for category, entries in (data.get("sources") or {}).items():
        for entry in entries or []:
            site = str(entry.get("site", "")) if isinstance(entry, dict) else ""
            for token in DOMAIN_TOKEN_RE.findall(site.lower()):
                domain_to_genre.setdefault(token, category)
    return domain_to_genre


def classify(url: str, domain_to_genre: dict[str, str]) -> str:
    domain = url_domain(url)
    if not domain:
        return "off-whitelist"
    for token, genre in domain_to_genre.items():
        if domain == token or domain.endswith("." + token) or token in domain:
            return genre
    return "off-whitelist"


def iter_manifests(papers_root: Path):
    for manifest_path in sorted(papers_root.glob("*/*/manifest.yaml")):
        session = manifest_path.parent.parent.name
        if not SAFE_SESSION_RE.fullmatch(session):
            continue
        yield session, manifest_path.parent.name, manifest_path


def collect(papers_root: Path, domain_to_genre: dict[str, str]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for session, level, manifest_path in iter_manifests(papers_root):
        manifest = load_yaml(manifest_path)
        status = str(manifest.get("status", "unknown"))
        for source in manifest.get("sources") or []:
            if not isinstance(source, dict) or not source.get("url"):
                continue
            key = normalize_url(str(source["url"]))
            entry = index.get(key)
            if entry is None:
                entry = {
                    "url": str(source["url"]).strip(),
                    "title": clean_str(source.get("title")),
                    "publisher": clean_str(source.get("publisher")),
                    "genre": classify(str(source["url"]), domain_to_genre),
                    "first_used": session,
                    "times_used": 0,
                    "uses": [],
                }
                index[key] = entry
            entry["times_used"] += 1
            entry["first_used"] = min(entry["first_used"], session)
            if not entry["title"]:
                entry["title"] = clean_str(source.get("title"))
            entry["uses"].append(
                {
                    "date": session,
                    "level": level,
                    "prova": clean_str(source.get("used_in")),
                    "words": source.get("words_used"),
                    "status": status,
                }
            )
    return index


def base_date(session: str) -> str:
    """Collapse a same-day revision (YYYY-MM-DD-rN) to its base date; reusing a
    source in a revision of the same paper is legitimate, not cross-date reuse."""
    return session.split("-r", 1)[0] if re.search(r"-r[1-9]\d*$", session) else session


def cross_date_reuse(index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    reused = []
    for entry in index.values():
        dates = sorted({base_date(use["date"]) for use in entry["uses"]})
        if len(dates) > 1:
            reused.append({"url": entry["url"], "dates": dates})
    return sorted(reused, key=lambda item: item["url"])


def write_outputs(index: dict[str, dict[str, Any]], out_index: Path, out_blacklist: Path) -> None:
    ordered = sorted(index.values(), key=lambda entry: (entry["first_used"], entry["url"]))
    doc = {
        "generated_by": "scripts/build_used_index.py",
        "note": "Derived from every papers/<session>/<LEVEL>/manifest.yaml sources block. "
        "Do not edit by hand — regenerate.",
        "unique_sources": len(ordered),
        "sources": ordered,
    }
    out_index.parent.mkdir(parents=True, exist_ok=True)
    out_index.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")

    urls = sorted({entry["url"] for entry in index.values()})
    header = (
        "# Auto-generated by scripts/build_used_index.py — do NOT edit.\n"
        "# Every URL already used in a generated paper; S1/corpus-hunter must avoid these.\n"
    )
    out_blacklist.write_text(header + "\n".join(urls) + ("\n" if urls else ""), encoding="utf-8")


def summarize(index: dict[str, dict[str, Any]]) -> None:
    total_uses = sum(entry["times_used"] for entry in index.values())
    reused = cross_date_reuse(index)
    by_genre: dict[str, int] = defaultdict(int)
    for entry in index.values():
        by_genre[entry["genre"]] += 1
    print(f"unique sources : {len(index)}")
    print(f"total uses     : {total_uses}")
    print(f"cross-date reuse: {len(reused)} URL(s) used on >1 date")
    print("by genre:")
    for genre, count in sorted(by_genre.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {genre:<24} {count}")
    if reused:
        print("cross-date reused URLs:")
        for item in reused:
            print(f"  {item['url']}  <- {', '.join(item['dates'])}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--papers-root", type=Path, default=Path("papers"), help="papers root")
    parser.add_argument(
        "--sources", type=Path, default=Path("factory/corpus/sources.yaml"), help="whitelist for genre tagging"
    )
    parser.add_argument(
        "--out-index", type=Path, default=Path("factory/corpus/used-index.yaml"), help="rich index output"
    )
    parser.add_argument(
        "--out-blacklist",
        type=Path,
        default=Path("factory/corpus/used-sources.txt"),
        help="flat URL blacklist for S1 injection",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if not args.papers_root.is_dir():
        print(f"papers root not found: {args.papers_root}", file=sys.stderr)
        return 2
    domain_to_genre = build_genre_map(args.sources)
    index = collect(args.papers_root, domain_to_genre)
    write_outputs(index, args.out_index, args.out_blacklist)
    summarize(index)
    print(f"\nwrote {args.out_index}")
    print(f"wrote {args.out_blacklist}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
