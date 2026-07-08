# CILS Exam Factory 🇮🇹

**Fresh, free CILS-style Italian practice papers (A1–C1), generated from authentic Italian texts and validated automatically.**

📄 **Download papers:** https://kendrick-stein.github.io/cils-exam-factory/ *(sessions are added regularly)*

Each practice session includes, per level (A1, A2, B1, B2, C1):

- **Fascicolo** — reading comprehension, structures of communication (grammar & vocabulary), and written production, following the structure, instructions and scoring of recent official CILS papers. *(No listening/oral sections.)*
- **Chiavi e commenti** — full answer key with short explanations (with 中文 notes), a model essay (范文) for every writing task, and a **Glossario da ricordare**: the words and phrases worth memorizing from that paper.

## How papers are made

```
authentic web texts ──► corpus hunter (search, clean, CEFR-grade)
                        ──► item writer (fills the official-style template)
                        ──► blind solver (independent agent solves the paper cold)
                        ──► reconcile & fix (any disagreement ⇒ item regenerated)
                        ──► format audit (structure/points/wording vs. real-exam template)
                        ──► HTML + PDF build ──► published here
```

- Texts are **authentic** (news, blogs, institutional sites, public-domain literature), abridged and adapted with credit — «Testo adattato da …» — exactly as real CILS papers do. Every source URL and access date is recorded in the paper's `manifest.yaml`.
- A paper is published only if an independent "blind solver" agent, given the student copy alone, reproduces the answer key exactly and flags no ambiguity.
- Templates were derived from official December 2024 CILS papers (structure, item counts, points, timing, instruction wording). Official papers are **not** redistributed here.

## Run it yourself

Open this repo in Claude Code and run `/genpapers` (see `CLAUDE.md`), or ask Codex for `Make Paper` / `genpapers` and follow `AGENTS.md`. Requirements: Python 3.10+, Google Chrome (for PDF rendering), `pip install markdown pyyaml`.

Published papers are built into `docs/`. The GitHub Actions workflow in `.github/workflows/pages.yml` deploys that directory to GitHub Pages after a push to `main`.

## Disclaimer

This is an independent study project. It is **not affiliated with, nor endorsed by, the Università per Stranieri di Siena** (owner of the CILS certification). Generated papers are practice material only and do not guarantee equivalence with real exam difficulty or content. Adapted text excerpts remain © their original publishers, credited in each paper; practice materials are free for personal, non-commercial study.
