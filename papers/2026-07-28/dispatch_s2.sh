#!/bin/bash
# dispatch S2 fragment tasks to codex-companion, staggered. Usage: dispatch_s2.sh <filter-regex>
# e.g. dispatch_s2.sh '.' (all non-GLOSSARIO), dispatch_s2.sh '^A1 GLOSSARIO'
COMPANION="$(ls -d ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs | tail -1)"
CD=/Users/kendrickstein/Code/CILS_Exam_AUTOGEN
FILTER="${1:-.}"
while read -r LEVEL FRAG EFFORT; do
  echo "$LEVEL $FRAG" | grep -qE "$FILTER" || continue
  PF="$CD/papers/2026-07-28/s2-prompts/$LEVEL-$FRAG.txt"
  [ -f "$PF" ] || { echo "MISSING PROMPT $PF" >&2; continue; }
  OUT=$(node "$COMPANION" task --background --write --effort "$EFFORT" --prompt-file "$PF" 2>&1)
  JOB=$(echo "$OUT" | grep -oE 'task-[a-z0-9-]+' | head -1)
  echo "$LEVEL $FRAG $EFFORT ${JOB:-DISPATCH_FAILED}"
  [ -z "$JOB" ] && echo "$OUT" >&2
  sleep 2.5
done < "$CD/papers/2026-07-28/s2-prompts/_index.txt"
