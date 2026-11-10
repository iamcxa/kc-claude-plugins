#!/bin/bash
# usage: run-codex.sh <run id>
id=$1; R=${RUN_ROOT:-/tmp/p3r/runs}/$id
code=$(python3 -c "import json;print(json.load(open('$R/replay.json'))['code'])")
start=$(date +%s)
codex exec -m gpt-6-astra -c model_reasoning_effort=xhigh -s workspace-write -C "$R" --add-dir "$code" --skip-git-repo-check \
  -o "$R/last-message.txt" "\$spacedock:ensign; then Read $R/dispatch.md and treat its content as your assignment." > "$R/codex.log" 2>&1
echo "exit=$? seconds=$(( $(date +%s) - start ))" > "$R/done.txt"
