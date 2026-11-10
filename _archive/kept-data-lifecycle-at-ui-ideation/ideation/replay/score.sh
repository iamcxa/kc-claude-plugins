#!/bin/bash
# usage: score.sh <scored text file> <out json>   (blind: the file name is not shown to the scorer)
txt=$1; out=$2
{ cat <<'P'
You score one design text against a fixed rubric. Use only the rubric and the text below; you have no tools.
For each check C1..C9, decide hit 1 or 0 by the rubric's rule: 1 only when the text states BOTH the condition AND what happens to the kept data or the late reply under it. Partial or implied = 0.
For a hit, give one verbatim quote (a contiguous span, at most 300 characters, copied exactly) that shows it.
Reply with JSON only, no prose, no code fence: {"C1":{"hit":0|1,"quote":"..."}, ..., "C9":{...}}

=== RUBRIC ===
P
sed -n '/^| #/,/^$/p' rubric.md
echo "=== TEXT ==="
cat "$txt"; } > "$out.prompt"
claude -p --model sonnet --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence --output-format text < "$out.prompt" > "$out" 2> "$out.err"
python3 /Users/kent/.local/state/kc-dev-flow-2-replays/kept-data-lifecycle-at-ui-ideation/parse.py "$txt" "$out"
