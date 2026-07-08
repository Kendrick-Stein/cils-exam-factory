#!/usr/bin/env python3
"""Fixture tests for scripts/paper_quality_audit.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def words(prefix: str, count: int) -> str:
    return " ".join(f"{prefix}{index}" for index in range(1, count + 1))


def structure_counts(level: str) -> list[tuple[int, int]]:
    return {
        "A2": [(1, 100), (2, 100), (3, 100)],
        "B2": [(1, 240), (2, 230), (3, 200)],
        "C1": [(1, 260), (2, 250), (3, 220), (4, 150)],
    }.get(level, [])


def source_slots(level: str) -> list[str]:
    return {
        "A2": ["T1", "T2", "T3", "T4", "T5", "T6"],
        "B2": ["T1", "T2", "T3", "T4", "T5", "T6"],
        "C1": ["T1", "T2", "T3", "T4", "T5", "T6", "T7"],
    }.get(level, ["T1"])


def structure_section(level: str) -> str:
    blocks = [
        """
# Test di analisi delle strutture di comunicazione
"""
    ]
    for number, count in structure_counts(level):
        blocks.append(
            f"""
## Analisi delle strutture di comunicazione — Prova n. {number}

> *Completa la prova secondo le istruzioni. DEVI SCRIVERE LE RISPOSTE NEL "FOGLIO DELLE RISPOSTE".*

### STRUTTURA {number}

{words(f"struttura{number}", count)}
"""
        )
        if number == 3:
            blocks.append(
                """
| n. | A | B | C | D |
|---|---|---|---|---|
| 1. | una | due | tre | quattro |
"""
            )
        if level == "C1" and number == 4:
            blocks.append(
                """
**0. Il Dipartimento pubblica l'avviso.**

→ L'AVVISO VIENE PUBBLICATO DAL DIPARTIMENTO.

**1. Il Comune verifica le domande.**

→ LE DOMANDE …………………………………
"""
            )
    return "".join(blocks)


def manifest(level: str, url: str, with_quality: bool = True, variant_profile: str = "cils-2024-standard") -> str:
    quality = """
quality:
  variant_profile: {variant_profile}
  source_policy: excerpt-first
  source_attribution: manifest-only
  max_rewrite: light
""".format(variant_profile=variant_profile) if with_quality else ""
    sources = "\n".join(
        f"""  - id: {slot}
    url: "{url if index == 1 else f"https://example.com/{level.lower()}/{slot.lower()}"}"
    title: "Fonte {level} {slot}"
    publisher: "Fixture"
    accessed: "2000-01-04"
    used_in: "{slot}"
    adapted: true
    words_used: 100"""
        for index, slot in enumerate(source_slots(level), start=1)
    )
    return f"""exam: cils
level: {level}
session: "2000-01-04"
title: "{level} fixture"
status: draft
sources:
{sources}
{quality}pipeline:
  stages: []
validation:
  result: fail
"""


def paper(level: str, p1: int, p2: int, p3: int, inline_points: bool = False) -> str:
    point_line = "\n> *Punteggio massimo: punti 7 — punti 1 per ogni risposta esatta.*\n" if inline_points else ""
    attribution_line = (
        f"\n*Testo adattato da: Fonte tre, Fixture, https://example.com/{level}/tre, consultato il 04/01/2000*\n"
        if inline_points else ""
    )
    return f"""---
exam: CILS
level: {level}
level_name: "{level} fixture"
session: "2000-01-04"
kind: paper
---

# Quaderno di esame

## ESEMPIO DI FOGLIO DELLE RISPOSTE

# Test di comprensione della lettura

## Comprensione della lettura — Prova n. 1

> *Leggi il testo.*

### TESTO UNO

{words("uno", p1)}

> *Completa le frasi. Scegli una delle quattro proposte di completamento che ti diamo per ogni frase. DEVI SCRIVERE LE RISPOSTE NEL "FOGLIO DELLE RISPOSTE".*{point_line}

1. **Secondo il testo, la funzione principale del progetto è**
   A) una risposta.
   B) un distrattore.
   C) un distrattore.
   D) un distrattore.

2. **Dal testo emerge che la scelta dipende soprattutto**
   A) una risposta.
   B) un distrattore.
   C) un distrattore.
   D) un distrattore.

3. **Lo scopo del testo è**
   A) una risposta.
   B) un distrattore.
   C) un distrattore.
   D) un distrattore.

## Comprensione della lettura — Prova n. 2

> *Leggi il testo.*

### TESTO DUE

{words("due", p2)}

> *Leggi le informazioni. Indica se le informazioni sono vere o false. DEVI SCRIVERE LE RISPOSTE NEL "FOGLIO DELLE RISPOSTE".*

1. L'informazione principale è presente nel testo. Vero ○ Falso ○

## Comprensione della lettura — Prova n. 3

> *Leggi il testo. Il testo è diviso in parti. Le parti non sono in ordine. Ricostruisci il testo.*

### TESTO TRE

{words("tre", p3)}
{attribution_line}
{structure_section(level)}
"""


def matching_microtext_paper() -> str:
    text_one = words("annuncio", 35)
    text_two = words("servizio", 35)
    text_three = words("orario", 35)
    text_four = words("biglietto", 35)
    return f"""---
exam: CILS
level: A2
level_name: "A2 fixture"
session: "2000-01-04"
kind: paper
---

# Quaderno di esame

## ESEMPIO DI FOGLIO DELLE RISPOSTE

# Test di comprensione della lettura

## Comprensione della lettura — Prova n. 1

> *Leggi il testo.*

### TESTO UNO

{words("uno", 190)}

## Comprensione della lettura — Prova n. 2

> *Leggi il testo.*

### TESTO DUE

{words("due", 170)}

## Comprensione della lettura — Prova n. 3

> *Leggi i testi da 1 a 6. Scegli per ogni testo la risposta adatta.*

**1. Il nuovo sportello**

{text_one}

**2. Una visita speciale**

{text_two}

**3. Cambia l'orario**

{text_three}

**4. Una nuova tessera**

{text_four}

---

A. Il servizio apre prima.
B. Serve un documento.
C. Il museo chiude tardi.
D. Il biglietto costa meno.
E. La biblioteca cambia sede.
F. Un corso e' cancellato.
{structure_section("A2")}
"""


def run_audit(repo_root: Path, papers_root: Path, report: Path, levels: str = "B2,C1") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "paper_quality_audit.py"),
            "--papers-root",
            str(papers_root),
            "--session",
            "2000-01-04",
            "--levels",
            levels,
            "--report",
            str(report),
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )


def run_test() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    with tempfile.TemporaryDirectory(prefix="cils-quality-audit-bad-") as tmp:
        tmp_root = Path(tmp)
        papers_root = tmp_root / "papers"
        write_text(papers_root / "2000-01-04" / "B2" / "manifest.yaml", manifest("B2", "https://example.com/shared", True))
        write_text(papers_root / "2000-01-04" / "B2" / "paper.md", paper("B2", 480, 430, 360))
        write_text(papers_root / "2000-01-04" / "C1" / "manifest.yaml", manifest("C1", "https://example.com/shared", False))
        write_text(papers_root / "2000-01-04" / "C1" / "paper.md", paper("C1", 300, 300, 300, inline_points=True))

        report = tmp_root / "quality.json"
        completed = run_audit(repo_root, papers_root, report)
        if completed.returncode == 0:
            raise AssertionError("quality audit accepted a short C1 paper with duplicated source URL")
        data = json.loads(report.read_text(encoding="utf-8"))
        issue_ids = {issue["id"] for issue in data["issues"]}
        expected = {
            "manifest.variant_profile",
            "manifest.source_attribution",
            "source.cross_level_duplicate",
            "length.reading_text",
            "format.inline_points",
            "format.visible_source_attribution",
        }
        missing = expected - issue_ids
        if missing:
            raise AssertionError(f"quality audit missed expected issues {missing}; saw {issue_ids}")

    with tempfile.TemporaryDirectory(prefix="cils-quality-audit-good-") as tmp:
        tmp_root = Path(tmp)
        papers_root = tmp_root / "papers"
        write_text(papers_root / "2000-01-04" / "B2" / "manifest.yaml", manifest("B2", "https://example.com/b2", True))
        write_text(papers_root / "2000-01-04" / "B2" / "paper.md", paper("B2", 500, 450, 380))
        write_text(papers_root / "2000-01-04" / "C1" / "manifest.yaml", manifest("C1", "https://example.com/c1", True))
        write_text(papers_root / "2000-01-04" / "C1" / "paper.md", paper("C1", 600, 560, 460))

        report = tmp_root / "quality.json"
        completed = run_audit(repo_root, papers_root, report)
        if completed.returncode != 0:
            raise AssertionError(
                "quality audit rejected valid fixtures\n"
                f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )
        data = json.loads(report.read_text(encoding="utf-8"))
        if data["result"] != "pass" or data["issues"]:
            raise AssertionError(f"expected clean pass report, got {data}")

    with tempfile.TemporaryDirectory(prefix="cils-quality-audit-microtext-") as tmp:
        tmp_root = Path(tmp)
        papers_root = tmp_root / "papers"
        write_text(papers_root / "2000-01-04" / "A2" / "manifest.yaml", manifest("A2", "https://example.com/a2", True))
        write_text(papers_root / "2000-01-04" / "A2" / "paper.md", matching_microtext_paper())

        report = tmp_root / "quality.json"
        completed = run_audit(repo_root, papers_root, report, levels="A2")
        if completed.returncode != 0:
            raise AssertionError(
                "quality audit rejected valid A2 matching microtexts\n"
                f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )
        data = json.loads(report.read_text(encoding="utf-8"))
        if data["result"] != "pass" or data["issues"]:
            raise AssertionError(f"expected clean A2 microtext pass report, got {data}")

    with tempfile.TemporaryDirectory(prefix="cils-quality-audit-variant-") as tmp:
        tmp_root = Path(tmp)
        papers_root = tmp_root / "papers"
        write_text(
            papers_root / "2000-01-04" / "A2" / "manifest.yaml",
            manifest("A2", "https://example.com/a2", True, variant_profile="cils-2024-b1-cittadinanza"),
        )
        write_text(papers_root / "2000-01-04" / "A2" / "paper.md", matching_microtext_paper())

        report = tmp_root / "quality.json"
        completed = run_audit(repo_root, papers_root, report, levels="A2")
        if completed.returncode == 0:
            raise AssertionError("quality audit accepted a B1-only variant profile for A2")
        data = json.loads(report.read_text(encoding="utf-8"))
        issue_ids = {issue["id"] for issue in data["issues"]}
        if "manifest.variant_profile_level" not in issue_ids:
            raise AssertionError(f"expected variant profile level failure, got {data}")

    with tempfile.TemporaryDirectory(prefix="cils-quality-audit-unsafe-") as tmp:
        tmp_root = Path(tmp)
        papers_root = tmp_root / "papers"
        report = tmp_root / "quality.json"
        completed = run_audit(repo_root, papers_root, report, levels="../escape")
        if completed.returncode == 0:
            raise AssertionError("quality audit accepted unsafe level")
        if "unsafe level" not in completed.stderr:
            raise AssertionError(f"expected unsafe level error, got:\n{completed.stderr}")

        completed = subprocess.run(
            [
                sys.executable,
                str(repo_root / "scripts" / "paper_quality_audit.py"),
                "--papers-root",
                str(papers_root),
                "--session",
                "../escape",
                "--levels",
                "A2",
                "--report",
                str(report),
            ],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            raise AssertionError("quality audit accepted unsafe session")
        if "unsafe session" not in completed.stderr:
            raise AssertionError(f"expected unsafe session error, got:\n{completed.stderr}")

    with tempfile.TemporaryDirectory(prefix="cils-quality-audit-draft-on-fail-") as tmp:
        tmp_root = Path(tmp)
        papers_root = tmp_root / "papers"
        manifest_path = papers_root / "2000-01-04" / "C1" / "manifest.yaml"
        write_text(manifest_path, manifest("C1", "https://example.com/c1", True).replace("status: draft", "status: published"))
        write_text(papers_root / "2000-01-04" / "C1" / "paper.md", paper("C1", 300, 300, 300, inline_points=True))

        report = tmp_root / "quality.json"
        completed = subprocess.run(
            [
                sys.executable,
                str(repo_root / "scripts" / "paper_quality_audit.py"),
                "--papers-root",
                str(papers_root),
                "--session",
                "2000-01-04",
                "--levels",
                "C1",
                "--report",
                str(report),
                "--write-manifest",
            ],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            raise AssertionError("quality audit should fail the bad C1 fixture")
        manifest_after = manifest_path.read_text(encoding="utf-8")
        if "status: draft" not in manifest_after:
            raise AssertionError(f"quality failure should keep manifest draft:\n{manifest_after}")


def main() -> int:
    try:
        run_test()
    except Exception as exc:  # noqa: BLE001 - dependency-free fixture test.
        print(f"FAIL: {exc}")
        return 1
    print("PASS: paper quality audit fixture test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
