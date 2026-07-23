#!/usr/bin/env python3
"""Fixture tests for scripts/pool_select.py."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

SCRIPT = Path(__file__).resolve().parent / "pool_select.py"


def make_index(tmp_path, entries):
    idx = tmp_path / "pool-index.yaml"
    idx.write_text(yaml.safe_dump({"count": len(entries), "sources": entries}, allow_unicode=True), encoding="utf-8")
    return idx


def entry(url, genre, levels, words, **extra):
    base = {"url": url, "genre": genre, "usable_levels": levels, "words": words,
            "perishable": False, "perishable_until": None, "published": "2026-07-10",
            "fetched": "2026-07-23", "source_file": f"pool/{url[-3:]}.md"}
    base.update(extra)
    return base


def run(idx, bl, src, args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--pool-index", str(idx), "--blacklist", str(bl),
         "--sources", str(src), "--today", "2026-07-23", *args],
        capture_output=True, text=True)


def scaffold(tmp_path, entries, blacklist=""):
    idx = make_index(tmp_path, entries)
    bl = tmp_path / "used.txt"; bl.write_text(blacklist, encoding="utf-8")
    src = tmp_path / "sources.yaml"; src.write_text("freshness:\n  news_general: 12\n", encoding="utf-8")
    return idx, bl, src


def test_filters_by_level_genre_and_words(tmp_path):
    entries = [
        entry("https://a.it/1", "news_general", ["B1", "B2"], 400),
        entry("https://a.it/2", "news_general", ["C1"], 400),      # wrong level
        entry("https://a.it/3", "literature_public_domain", ["B2"], 400),  # wrong genre
        entry("https://a.it/4", "news_general", ["B2"], 900),      # out of band
    ]
    idx, bl, src = scaffold(tmp_path, entries)
    res = run(idx, bl, src, ["--level", "B2", "--genre", "news_general", "--words", "300-450", "--json"])
    got = json.loads(res.stdout)
    assert [e["url"] for e in got] == ["https://a.it/1"]


def test_excludes_consumed_urls(tmp_path):
    entries = [entry("https://a.it/1", "news_general", ["B2"], 400)]
    idx, bl, src = scaffold(tmp_path, entries, blacklist="https://a.it/1\n")
    res = run(idx, bl, src, ["--level", "B2", "--json"])
    assert json.loads(res.stdout) == []


def test_excludes_stale_perishable(tmp_path):
    old = entry("https://a.it/old", "news_general", ["B2"], 400,
                perishable=True, published="2024-01-01", fetched="2024-01-02")
    idx, bl, src = scaffold(tmp_path, [old])
    res = run(idx, bl, src, ["--level", "B2", "--json"])
    assert json.loads(res.stdout) == []
    res2 = run(idx, bl, src, ["--level", "B2", "--include-stale", "--json"])
    assert len(json.loads(res2.stdout)) == 1
