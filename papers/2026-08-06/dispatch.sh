#!/bin/bash
# dispatch.sh <stage-dir> <filter-regex>   e.g. dispatch.sh s1-prompts '.' | dispatch.sh s2-prompts '^A1 '
COMPANION="$(ls -d ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs | tail -1)"
CD=/Users/kendrickstein/Code/CILS_Exam_AUTOGEN
DIR="$CD/papers/2026-08-06/$1"
FILTER="${2:-.}"
while read -r A B C; do
  case "$1" in
    s1-prompts) NAME="$A"; EFFORT="$B" ;;
    *)          NAME="$A-$B"; EFFORT="$C" ;;
  esac
  echo "$A $B" | grep -qE "$FILTER" || continue
  PF="$DIR/$NAME.txt"
  [ -f "$PF" ] || { echo "MISSING PROMPT $PF" >&2; continue; }
  OUT=$(node "$COMPANION" task --background --write --effort "$EFFORT" --prompt-file "$PF" 2>&1)
  JOB=$(echo "$OUT" | grep -oE 'task-[a-z0-9-]+' | head -1)
  echo "$NAME $EFFORT ${JOB:-DISPATCH_FAILED}"
  [ -z "$JOB" ] && echo "$OUT" >&2
  sleep 2.5
done < "$DIR/_index.txt"
