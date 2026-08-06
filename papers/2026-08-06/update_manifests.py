#!/usr/bin/env python3
"""Fill each level manifest's `sources:` block from sources.md + fragment word counts.

Orchestrator-owned (fragment writers never touch manifest.yaml). Run after S2 assembly.
"""
import json
import pathlib
import re

import yaml

SESSION = "2026-08-06"
LEVELS = ["A1", "A2", "B1", "B2", "C1"]
WORD = re.compile(r"\b[\wÀ-ÿ']+\b")
SLOT_FRAGMENT = {"T1": "L1", "T2": "L2", "T3": "L3", "T4": "S1", "T5": "S2", "T6": "S3", "T7": "S4"}
SLOT_TEXTSLOTS = {
    "T1": ["T1_TEXT"], "T2": ["T2_TEXT"],
    "T3": ["L3_ITEMS"] + [f"T3_PART_{c}" for c in "ABCDEFGHIJKLMNOP"],
    "T4": ["S1_TEXT_WITH_GAPS"], "T5": ["S2_TEXT_WITH_GAPS"],
    "T6": ["S3_TEXT_WITH_GAPS"], "T7": ["T7_TEXT"],
}


def words_used(paper_dir, slot):
    frag = paper_dir / "fragments" / f"{SLOT_FRAGMENT[slot]}.json"
    if not frag.exists():
        return None
    slots = json.loads(frag.read_text()).get("slots", {})
    text = " ".join(slots[k] for k in SLOT_TEXTSLOTS[slot] if k in slots)
    return len(WORD.findall(text)) or None


def main():
    exam = yaml.safe_load(open("factory/exams/cils/exam.yaml"))
    for lv in LEVELS:
        pdir = pathlib.Path(f"papers/{SESSION}/{lv}")
        man = yaml.safe_load((pdir / "manifest.yaml").read_text())

        used_in = {}
        for sec in exam["levels"][lv]["sections"]:
            label = {"lettura": "Comprensione della lettura",
                     "strutture": "Analisi delle strutture di comunicazione"}.get(sec["id"])
            if not label:
                continue
            for p in sec.get("prove", []):
                slot = (p.get("testo") or {}).get("slot")
                if slot:
                    used_in[slot] = f"{label}, Prova n. {p['n']}"

        body = (pdir / "sources.md").read_text().split("## Coverage")[0]
        sources = []
        for sec in re.split(r"^## Slot ", body, flags=re.M)[1:]:
            slot = sec.split(" ")[0].strip()

            def field(name):
                m = re.search(rf"^- {name}:\s*(.+)$", sec, re.M)
                return m.group(1).strip() if m else None

            published = field("published")
            if published in ("unknown", "n/d", "none", "-"):
                published = None
            entry = {
                "id": slot,
                "url": field("url"),
                "title": field("title"),
                "publisher": field("publisher"),
                "published": published,
                "accessed": field("accessed") or SESSION,
                "used_in": used_in[slot],
                "adapted": True,
                "words_used": words_used(pdir, slot),
            }
            origin = field("origin")
            if origin:
                entry["origin"] = origin
            sources.append(entry)

        man["sources"] = sources
        quality = man.setdefault("quality", {})
        quality.setdefault("variant_profile", "cils-2024-standard")
        quality.setdefault("source_policy", "excerpt-first")
        quality.setdefault("source_attribution", "manifest-only")
        quality.setdefault("max_rewrite", "level_simplification")
        stages = man.setdefault("pipeline", {}).setdefault("stages", [])
        if not any(s.get("stage") == "corpus" for s in stages):
            stages.append({"stage": "corpus", "at": SESSION})
        if not any(s.get("stage") == "authoring" for s in stages):
            stages.append({"stage": "authoring", "at": SESSION})
        (pdir / "manifest.yaml").write_text(
            yaml.safe_dump(man, allow_unicode=True, sort_keys=False))
        missing = [s["id"] for s in sources if not s["words_used"]]
        print(f"{lv}: {len(sources)} sources" + (f"  MISSING words_used: {missing}" if missing else ""))


if __name__ == "__main__":
    main()
