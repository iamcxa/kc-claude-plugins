#!/bin/bash
# usage: run_pass.sh <name> <model> <prompt file> <outdir>
WT=${WT:?set WT to the code worktree}
cd /tmp/ac8
claude -p --plugin-dir "$WT/kc-dev-flow-2" --agent kc-dev-flow-2:design-director --add-dir /tmp/ac8 --allowedTools Read --output-format json --no-session-persistence --model "$2" < "$3" > "$4/$1.raw" 2> "$4/$1.err"
echo "$1 exit $?" >> "$4/status.txt"
