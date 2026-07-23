#!/usr/bin/env python3
"""Fixture tests for scripts/pool_add.py."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "pool_add.py"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from corpus_pool import normalize_url, parse_pool_file
from pool_add import pool_id


def run(args, cwd):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, cwd=cwd)


def base_args(pool_dir, sources, blacklist, url, body_file):
    return ["--pool-dir", str(pool_dir), "--sources", str(sources),
            "--blacklist", str(blacklist), "--url", url, "--title", "T",
            "--publisher", "P", "--published", "2026-07-13", "--fetched", "2026-07-23",
            "--genre", "news_general", "--cefr", "B2", "--usable-levels", "B1,B2",
            "--words", "244", "--fetch-intent", "A2/L3", "--text-file", str(body_file)]


def test_bank_writes_file_named_by_url_hash(tmp_path):
    pool, src, bl = tmp_path / "pool", tmp_path / "sources.yaml", tmp_path / "used.txt"
    src.write_text("freshness:\n  news_general: 12\n", encoding="utf-8")
    bl.write_text("# none\n", encoding="utf-8")
    body = tmp_path / "body.txt"
    body.write_text("Testo pulito.", encoding="utf-8")
    url = "https://www.ansa.it/foo/"
    res = run(base_args(pool, src, bl, url, body), tmp_path)
    assert res.returncode == 0, res.stderr
    out = pool / f"{pool_id(url)}.md"
    assert out.exists()
    entry = parse_pool_file(out)
    assert entry["cefr"] == "B2" and entry["usable_levels"] == ["B1", "B2"]
    assert entry["perishable"] is True          # news_general has a window -> perishable
    assert entry["body"] == "Testo pulito."


def test_bank_skips_when_already_pooled(tmp_path):
    pool, src, bl = tmp_path / "pool", tmp_path / "sources.yaml", tmp_path / "used.txt"
    src.write_text("freshness: {}\n", encoding="utf-8")
    bl.write_text("", encoding="utf-8")
    body = tmp_path / "b.txt"; body.write_text("x", encoding="utf-8")
    a = base_args(pool, src, bl, "https://www.ansa.it/foo/", body)
    run(a, tmp_path)
    res = run(a, tmp_path)
    assert "skip (already pooled)" in res.stdout


def test_bank_skips_when_consumed(tmp_path):
    pool, src, bl = tmp_path / "pool", tmp_path / "sources.yaml", tmp_path / "used.txt"
    src.write_text("freshness: {}\n", encoding="utf-8")
    bl.write_text(f"{normalize_url('https://www.ansa.it/foo/')}\n", encoding="utf-8")
    body = tmp_path / "b.txt"; body.write_text("x", encoding="utf-8")
    res = run(base_args(pool, src, bl, "https://www.ansa.it/foo/", body), tmp_path)
    assert "skip (already consumed)" in res.stdout
    assert not (pool / f"{pool_id('https://www.ansa.it/foo/')}.md").exists()
