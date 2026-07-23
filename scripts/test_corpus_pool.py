#!/usr/bin/env python3
"""Unit tests for scripts/corpus_pool.py."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from corpus_pool import (
    add_months, is_stale, normalize_url, parse_pool_file, read_blacklist,
)


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


POOL_FILE = """---
url: https://www.ansa.it/Canale/Foo/
title: Topi di quota
publisher: ANSA
published: '2026-07-13'
fetched: '2026-07-23'
genre: news_general
cefr: B2
usable_levels: [B1, B2]
words: 244
perishable: true
perishable_until: null
fetch_intent: A2/L3
---

Corpo del testo pulito su due righe.
Seconda riga.
"""


def test_normalize_url_strips_trailing_slash_and_lowercases():
    assert normalize_url("https://Www.Ansa.it/Canale/Foo/") == "https://www.ansa.it/canale/foo"


def test_parse_pool_file_splits_front_matter_and_body(tmp_path):
    entry = parse_pool_file(write(tmp_path / "x.md", POOL_FILE))
    assert entry["cefr"] == "B2"
    assert entry["usable_levels"] == ["B1", "B2"]
    assert entry["body"].startswith("Corpo del testo")
    assert entry["source_file"].endswith("x.md")


def test_read_blacklist_ignores_comments_and_blank_lines(tmp_path):
    bl = write(tmp_path / "used.txt", "# header\n\nhttps://A.com/x/\nhttps://b.com/y\n")
    assert read_blacklist(bl) == {"https://a.com/x", "https://b.com/y"}


def test_read_blacklist_missing_file_is_empty(tmp_path):
    assert read_blacklist(tmp_path / "nope.txt") == set()


def test_add_months_rolls_year_and_clamps_day():
    assert add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)
    assert add_months(date(2026, 12, 15), 1) == date(2027, 1, 15)


def test_is_stale_evergreen_never_stale():
    entry = {"perishable": False, "genre": "literature_public_domain"}
    assert is_stale(entry, {"news_general": 12}, date(2030, 1, 1)) is False


def test_is_stale_perishable_past_window():
    entry = {"perishable": True, "genre": "news_general", "published": "2026-01-01", "fetched": "2026-01-02"}
    fresh = {"news_general": 12}
    assert is_stale(entry, fresh, date(2026, 6, 1)) is False   # within 12 months
    assert is_stale(entry, fresh, date(2027, 3, 1)) is True    # past 12 months


def test_is_stale_explicit_perishable_until_wins():
    entry = {"perishable": True, "genre": "practical_realia", "perishable_until": "2026-08-01"}
    assert is_stale(entry, {"practical_realia": 6}, date(2026, 7, 31)) is False
    assert is_stale(entry, {"practical_realia": 6}, date(2026, 8, 2)) is True
