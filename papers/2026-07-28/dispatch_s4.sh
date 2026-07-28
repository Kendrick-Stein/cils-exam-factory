#!/bin/bash
COMPANION="$(ls -d ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs | tail -1)"
CD=/Users/kendrickstein/Code/CILS_Exam_AUTOGEN
while read -r LEVEL FRAG EFFORT; do
  PF="$CD/papers/2026-07-28/s4-prompts/$LEVEL-$FRAG.txt"
  OUT=$(node "$COMPANION" task --background --write --effort "$EFFORT" --prompt-file "$PF" 2>&1)
  JOB=$(echo "$OUT" | grep -oE 'task-[a-z0-9-]+' | head -1)
  echo "$LEVEL $FRAG $EFFORT ${JOB:-DISPATCH_FAILED}"
  sleep 2.5
done < "$CD/papers/2026-07-28/s4-prompts/_index.txt"
