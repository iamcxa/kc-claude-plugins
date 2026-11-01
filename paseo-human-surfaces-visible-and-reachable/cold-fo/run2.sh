#!/bin/bash
# usage: run2.sh <name> <repo dir> <package> <prompt>
export PATH=/tmp/cold-fo/bin:$PATH GH_MODE=down GH_LOG=/tmp/cold-fo/$1.ghlog; cd $2
printf "%s" "$4" | claude -p --add-dir $3 --setting-sources project --strict-mcp-config --plugin-dir $3 --model sonnet --no-session-persistence --max-budget-usd 3 --output-format stream-json --verbose --allowedTools "Skill Read Glob Grep Bash(gh:*) Bash(spacedock:*) Bash(python3:*) Bash(git:*) Bash(ls:*)" > /tmp/cold-fo/$1.jsonl 2>/tmp/cold-fo/$1.err
