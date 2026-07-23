#!/usr/bin/env python3
"""Fixture tests for scripts/build_pool_index.py."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

SCRIPT = Path(__file__).resolve().parent / "build_pool_index.py"


def pool_file(pool: Path, name: str, **fm) -> None:
    pool.mkdir(parents=True, exist_ok=True)
    front = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False).strip()
    (pool / name).write_text(f"---\n{front}\n---\n\nCorpo.\n", encoding="utf-8")


def run(pool, index, blacklist, sources, extra=()):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--pool-dir", str(pool), "--out-index", str(index),
         "--blacklist", str(blacklist), "--sources", str(sources), "--today", "2026-07-23", *extra],
        capture_output=True, text=True)


def seed(tmp_path):
    pool = tmp_path / "pool"
    pool_file(pool, "aaa.md", url="https://a.it/x", genre="news_general", cefr="B2",
              usable_levels=["B1", "B2"], words=300, perishable=True, published="2026-07-10", fetched="2026-07-23")
    pool_file(pool, "bbb.md", url="https://b.it/y", genre="literature_public_domain", cefr="C1",
              usable_levels=["C1"], words=600, perishable=False, published="1920-01-01", fetched="2026-07-23")
    idx, bl, src = tmp_path / "pool-index.yaml", tmp_path / "used.txt", tmp_path / "sources.yaml"
    bl.write_text("# none\n", encoding="utf-8")
    src.write_text("freshness:\n  news_general: 12\n", encoding="utf-8")
    return pool, idx, bl, src


def test_index_lists_all_entries_without_body(tmp_path):
    pool, idx, bl, src = seed(tmp_path)
    res = run(pool, idx, bl, src)
    assert res.returncode == 0, res.stderr
    doc = yaml.safe_load(idx.read_text())
    assert doc["count"] == 2
    assert {e["url"] for e in doc["sources"]} == {"https://a.it/x", "https://b.it/y"}
    assert "body" not in doc["sources"][0]


def test_index_is_idempotent(tmp_path):
    pool, idx, bl, src = seed(tmp_path)
    run(pool, idx, bl, src)
    first = idx.read_text()
    run(pool, idx, bl, src)
    assert idx.read_text() == first


def test_coverage_report_mentions_depth(tmp_path):
    pool, idx, bl, src = seed(tmp_path)
    res = run(pool, idx, bl, src)
    assert "news_general" in res.stdout and "literature_public_domain" in res.stdout


def test_prune_removes_consumed_entry(tmp_path):
    pool, idx, bl, src = seed(tmp_path)
    bl.write_text("https://a.it/x\n", encoding="utf-8")   # a.it now consumed
    res = run(pool, idx, bl, src, extra=["--prune"])
    assert not (pool / "aaa.md").exists()
    assert (pool / "bbb.md").exists()
    assert "pruned" in res.stdout.lower()
