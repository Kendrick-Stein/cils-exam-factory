#!/bin/bash
# blind.sh <LEVEL> <PROVA_IDS|ALL> <outfile>
# Fresh read-only solver on an isolated paper.md copy (S3). Hard rule: paper.md only.
set -e
CD=/Users/kendrickstein/Code/CILS_Exam_AUTOGEN
LV=$1; PR=$2; OUT=$3
cd "$CD"
if [ "$PR" = "ALL" ]; then
  JSON=$(python3 scripts/blind_validation.py prepare --paper-dir "papers/2026-08-06/$LV")
else
  JSON=$(python3 scripts/blind_validation.py prepare --paper-dir "papers/2026-08-06/$LV" --prova "$PR")
fi
PROMPT=$(printf '%s' "$JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["prompt"])')
PROMPT="$PROMPT For every multiple-choice item answer with the option LETTER ONLY (A, B, C or D) exactly as labelled in the paper, never with the word itself."
FILE=$(printf '%s' "$JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["isolated_paper"])')
test -s "$FILE" || { echo "[$LV] EMPTY EXTRACT $FILE" >&2; exit 1; }
echo "[$LV $PR] $(wc -c <"$FILE") bytes -> $OUT" >&2
codex exec --skip-git-repo-check --sandbox read-only -c model_reasoning_effort=low "$PROMPT" < /dev/null > "$OUT" 2>"$OUT.log"
echo "[$LV $PR] done" >&2
