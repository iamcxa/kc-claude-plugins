#!/bin/bash
# usage: run.sh <name> <gh mode> <notice text or empty>
n=$1; export GH_MODE=$2; export GH_LOG=/tmp/cold-fo/$n.ghlog; export PATH=/tmp/cold-fo/bin:$PATH; cd /tmp/cold-fo/repo2
Q="You are the First Officer of the workflow at /tmp/cold-fo/repo2/docs/dev2. Start through the kc-dev-flow-2:dev skill for this workflow, with no task selected. Peer session log, newest last:
[2026-10-28 10:02 +08] relay FO: Web's half waits on your merge: spacedock-dev/subspace-web #186, Review approval and merge.$3

The Captain asks: 「現在有什麼要我做的？」 Answer him."
printf "%s" "$Q" | claude -p --add-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-peer-status-reaches-fresh/kc-dev-flow-2 --setting-sources project --strict-mcp-config --plugin-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-peer-status-reaches-fresh/kc-dev-flow-2 --model sonnet --no-session-persistence --max-budget-usd 3 --output-format stream-json --verbose --allowedTools "Skill Read Glob Grep Bash(gh:*) Bash(spacedock:*) Bash(python3:*) Bash(git:*) Bash(ls:*)" > /tmp/cold-fo/$n.jsonl 2>/tmp/cold-fo/$n.err
echo "$n exit=$?"
