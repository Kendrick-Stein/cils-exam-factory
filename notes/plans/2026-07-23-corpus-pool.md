# Corpus Pool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standing pool of cleaned, CEFR-graded texts that `/genpapers` selects from at build time, so cross-level-usable fetches are never wasted and live search becomes the fallback.

**Architecture:** A `factory/corpus/pool/<id>.md` store (YAML front-matter + cleaned body), a shared `scripts/corpus_pool.py` schema/helper module, a `pool_add.py` banker, a `build_pool_index.py` cataloguer, and a `pool_select.py` querier. Consumption is derived from the existing `used-sources.txt` (built by `build_used_index.py`), so the pool and the consumed-blacklist can never drift. corpus-hunter consults the pool first and banks over-fetched, graded leftovers.

**Tech Stack:** Python 3 (stdlib + PyYAML), pytest 9.x. Scripts live in `scripts/`, tests as `scripts/test_<name>.py`, invoked with `python3 -m pytest`.

**Spec:** `notes/specs/2026-07-23-corpus-pool-design.md`

---

## File structure

**Create:**
- `scripts/corpus_pool.py` — shared pool-file schema, `normalize_url`, blacklist reader, freshness rule (single source of truth for both index-builder and selector).
- `scripts/pool_add.py` — bank one graded text into `factory/corpus/pool/<id>.md` (deterministic id, dedup + consumed skip).
- `scripts/build_pool_index.py` — scan `pool/*.md` → `pool-index.yaml` + coverage report; `--prune`.
- `scripts/pool_select.py` — query `pool-index.yaml` + `used-sources.txt` → ranked available candidates.
- `scripts/test_corpus_pool.py`, `scripts/test_pool_add.py`, `scripts/test_build_pool_index.py`, `scripts/test_pool_select.py` — fixture tests.
- `factory/corpus/pool/.gitkeep` — keep the empty pool dir tracked.

**Modify:**
- `factory/corpus/sources.yaml` — whitelist backfill + new `freshness:` block.
- `.claude/agents/corpus-hunter.md`, `.codex/agents/corpus-hunter.toml` — pool-first + over-fetch + bank.
- `factory/PIPELINE.md`, `.claude/skills/genpapers/SKILL.md` — S1 data flow.
- `CLAUDE.md` — Map rows.

**Note on imports:** the CLI scripts import the shared module as `from corpus_pool import ...`. When run as `python3 scripts/<x>.py` (cwd = repo root) or under pytest, `scripts/` is on `sys.path[0]`, so the bare import resolves. Tests pass explicit `--pool-dir/--pool-index/--blacklist/--sources/--today` so nothing depends on cwd-relative defaults.

---

### Task 1: Shared pool module `scripts/corpus_pool.py`

**Files:**
- Create: `scripts/corpus_pool.py`
- Test: `scripts/test_corpus_pool.py`

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest scripts/test_corpus_pool.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'corpus_pool'`.

- [ ] **Step 3: Write minimal implementation**

Create `scripts/corpus_pool.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest scripts/test_corpus_pool.py -q`
Expected: PASS (8 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/corpus_pool.py scripts/test_corpus_pool.py
git commit -m "feat(cils): shared corpus-pool schema/freshness module"
```

---

### Task 2: Bank a text — `scripts/pool_add.py`

**Files:**
- Create: `scripts/pool_add.py`
- Test: `scripts/test_pool_add.py`

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest scripts/test_pool_add.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'pool_add'`.

- [ ] **Step 3: Write minimal implementation**

Create `scripts/pool_add.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest scripts/test_pool_add.py -q`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/pool_add.py scripts/test_pool_add.py
git commit -m "feat(cils): pool_add banks graded texts into the corpus pool"
```

---

### Task 3: Catalogue + coverage — `scripts/build_pool_index.py`

**Files:**
- Create: `scripts/build_pool_index.py`
- Test: `scripts/test_build_pool_index.py`

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest scripts/test_build_pool_index.py -q`
Expected: FAIL — script does not exist (nonzero return / import error).

- [ ] **Step 3: Write minimal implementation**

Create `scripts/build_pool_index.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest scripts/test_build_pool_index.py -q`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/build_pool_index.py scripts/test_build_pool_index.py
git commit -m "feat(cils): build_pool_index catalogues the pool + coverage/prune"
```

---

### Task 4: Query available texts — `scripts/pool_select.py`

**Files:**
- Create: `scripts/pool_select.py`
- Test: `scripts/test_pool_select.py`

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest scripts/test_pool_select.py -q`
Expected: FAIL — script does not exist.

- [ ] **Step 3: Write minimal implementation**

Create `scripts/pool_select.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest scripts/test_pool_select.py -q`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/pool_select.py scripts/test_pool_select.py
git commit -m "feat(cils): pool_select queries available pool texts per slot"
```

---

### Task 5: Whitelist backfill + freshness map — `factory/corpus/sources.yaml`

**Files:**
- Modify: `factory/corpus/sources.yaml`

- [ ] **Step 1: Add the `freshness:` block** after the `length_bands_words` block (inside `rules:` is wrong — add it as a new top-level key after `rules:`). Insert before `sources:`:

```yaml
# Perishability windows (months) per genre — pool_select drops perishable texts past
# their window (or their explicit perishable_until). Genres absent here are evergreen.
freshness:
  news_general: 12
  news_easy: 12
  practical_realia: 6
```

- [ ] **Step 2: Backfill recurring off-whitelist domains** into the `sources:` block. Under `news_general` add nothing; add the new/expanded entries to the matching categories:

In `culture_science:` add:
```yaml
    - {site: media.inaf.it, note: "astrofisica INAF — divulgazione scientifica B2/C1"}
    - {site: cnr.it, note: "comunicati di ricerca CNR — B2/C1"}
```
In `blogs_lifestyle:` add:
```yaml
    - {site: turistipercaso.it, note: "diari di viaggio — B1/B2"}
    - {site: camminiditalia.org, note: "racconti di cammini/trekking — B1/B2"}
    - {site: bimbieviaggi.it, note: "viaggi in famiglia — B1/B2"}
    - {site: mountainblog.it, note: "montagna/outdoor — B1/B2"}
    - {site: gamberorosso.it, note: "cibo/gastronomia — B1/B2"}
```
In `practical_realia:` replace the `comune.bologna.it / comune.milano.it / altri comuni` line with a generalized entry and add the culture/biblioteche realia:
```yaml
    - {site: "comune.<città>.it (torino, modena, parma, genova, roma, firenze, venezia, como, ravenna…)", note: "avvisi/servizi/comunicati comunali — regolativo A2/B1"}
    - {site: "biblioteche comunali (bibliotecasalaborsa.it, biblioteche.comune.verona.it)", note: "orari/servizi/prestito — realia A2/B1"}
    - {site: "musei e cultura (museiincomuneroma.it, cultura.gov.it, italia.it, visittrentino.info)", note: "orari/biglietti/eventi culturali A2/B1"}
```

- [ ] **Step 3: Verify the YAML still parses**

Run: `python3 -c "import yaml; d=yaml.safe_load(open('factory/corpus/sources.yaml')); assert d['freshness']['news_general']==12; assert any('turistipercaso' in x['site'] for x in d['sources']['blogs_lifestyle']); print('sources.yaml OK')"`
Expected: `sources.yaml OK`

- [ ] **Step 4: Commit**

```bash
git add factory/corpus/sources.yaml
git commit -m "feat(cils): backfill off-whitelist domains + freshness windows"
```

---

### Task 6: Wire S1 (agents, pipeline, skill, map) + pool scaffold + full verify

**Files:**
- Create: `factory/corpus/pool/.gitkeep`
- Modify: `.claude/agents/corpus-hunter.md`, `.codex/agents/corpus-hunter.toml`, `factory/PIPELINE.md`, `.claude/skills/genpapers/SKILL.md`, `CLAUDE.md`

- [ ] **Step 1: Scaffold the pool dir + initial index**

```bash
mkdir -p factory/corpus/pool
touch factory/corpus/pool/.gitkeep
python3 scripts/build_pool_index.py
```
Expected: prints `pool entries : 0 ...` and writes `factory/corpus/pool-index.yaml`.

- [ ] **Step 2: Update `.claude/agents/corpus-hunter.md`** — add a pool-first step and a bank step. After the `## Method, per slot` intro, insert as step 0 and extend the fetch step:

Add before current step 1:
```markdown
0. **Consult the pool first.** For the slot, run
   `python3 scripts/pool_select.py --level <LEVEL> --genre <genre> --words <min>-<max>`.
   If it returns a candidate, read that `pool/<id>.md` body and use it — do NOT fetch. Only
   if the pool has nothing for the slot do you fetch (steps 1–5 below).
```
Append to step 2 (fetch):
```markdown
   When you do fetch, **over-fetch**: grab 1–2 extra candidates from neighbouring levels/genres
   while you are here. You will grade and bank them (step 6) even if this paper does not use them.
```
Add a new step 6 after step 5:
```markdown
6. **Bank every graded candidate** you fetched (used or not) into the pool:
   `python3 scripts/pool_add.py --url <url> --title <t> --publisher <p> --published <d> --fetched <today> --genre <genre> --cefr <primary> --usable-levels <L1,L2> --words <n> --fetch-intent <LEVEL>/<slot> --text-file <cleaned.txt>`.
   Already-consumed or already-pooled URLs are skipped automatically. This is how a text
   fetched under one level's hunt becomes available to another level later.
```

- [ ] **Step 3: Mirror the same three edits into `.codex/agents/corpus-hunter.toml`** (identical wording inside the `developer_instructions` string).

- [ ] **Step 4: Update `factory/PIPELINE.md` S1** — replace the current de-dup-refresh bullet block with the pool-aware flow:

Change the S1 "Refresh de-dup registry first" + "Work" bullets to:
```markdown
- **Refresh registries first:** `python3 scripts/build_used_index.py` (consumed blacklist) then
  `python3 scripts/build_pool_index.py` (available pool catalogue + coverage).
- **Pool-first:** for each slot, `scripts/pool_select.py --level <L> --genre <g> --words <min>-<max>`;
  use a returned pooled text with zero fetching. Only unfilled slots go to a live fetch.
- **Work (live fallback):** fetch up to 2 candidates (over-fetching 1–2 neighbouring ones),
  clean, CEFR-grade, and **bank every graded text** via `scripts/pool_add.py`. Reject any URL in
  `used-sources.txt`.
```

- [ ] **Step 5: Update `.claude/skills/genpapers/SKILL.md` S1 QC gate** — replace the S1 QC line to mention the pool:
```markdown
1. **S1 QC:** before dispatching corpus-hunter, run `python3 scripts/build_used_index.py` then
   `python3 scripts/build_pool_index.py`; pass the blacklist + `pool_select` to every S1 prompt.
   Slots fill from the pool first; live fetches must over-fetch and bank leftovers via `pool_add.py`.
   Every slot has an accepted candidate (genre, CEFR verdict, length band); no accepted URL is in
   `used-sources.txt`. Reject skimpy metadata.
```

- [ ] **Step 6: Add CLAUDE.md Map rows** after the `build_used_index.py` row:
```markdown
| `scripts/pool_add.py` | Banks one graded, cleaned text into `factory/corpus/pool/<id>.md` (S1 over-fetch) |
| `scripts/build_pool_index.py` | Catalogues `pool/*.md` → `pool-index.yaml` + coverage; `--prune` |
| `scripts/pool_select.py` | Queries the pool for a slot (level+genre+length, minus consumed/stale) |
| `factory/corpus/pool/` | Standing pool of graded authentic texts (full text + front-matter) |
```

- [ ] **Step 7: Run the whole script test-suite + audits to confirm nothing regressed**

Run:
```bash
python3 -m pytest scripts/ -q
python3 -c "import yaml; yaml.safe_load(open('factory/corpus/pool-index.yaml')); yaml.safe_load(open('factory/corpus/sources.yaml')); print('yaml OK')"
```
Expected: all tests pass; `yaml OK`.

- [ ] **Step 8: Commit**

```bash
git add factory/corpus/pool/.gitkeep factory/corpus/pool-index.yaml \
        .claude/agents/corpus-hunter.md .codex/agents/corpus-hunter.toml \
        factory/PIPELINE.md .claude/skills/genpapers/SKILL.md CLAUDE.md
git commit -m "feat(cils): wire S1 to pool-first selection + over-fetch banking"
```

---

## Notes for the implementer

- **Do not** add a publish-gate on cross-date reuse — de-dup stays an S1-side preventive (user directive 2026-07-23).
- **Do not** re-fetch at build time — the pool stores full text on purpose.
- Keep `normalize_url` identical across `corpus_pool.py`, `build_used_index.py`, and `paper_quality_audit.py`; they must agree on URL identity.
- The pool grows monotonically; consumed entries stay on disk until `build_pool_index.py --prune` is run manually.
- **Deferred (spec §Bootstrap):** seeding the pool from historical `papers/*/*/sources.md` is intentionally out of scope for this plan — the pool starts empty and fills as `/genpapers` over-fetches. Add it later only if the initial pool feels too thin.
