#!/bin/bash
# usage: extract.sh <run dir> <start sha> <out txt>  -> lines the run added or changed in the task file
git -C "$1/wf/.spacedock-state" diff "$2" -- owner-vehicle-kept-after-name.md | grep -E '^\+' | grep -v '^+++' | sed 's/^+//' > "$3"
echo "$(wc -w < "$3") words; kept-data heading: $(grep -c '^### Kept data' "$3")"
