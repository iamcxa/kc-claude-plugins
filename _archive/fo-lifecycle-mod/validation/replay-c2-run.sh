#!/bin/bash
# usage: run.sh <run-name> <merged|open> <cue>
RUN=$1; MODE=$2; CUE=$3; D=/tmp/replay-c2/$RUN; cd $D/relay
date -u +%FT%TZ > $D/started.txt
export PATH="/tmp/replay-c2/bin:$PATH" GH_STUB_LOG="$D/gh-calls.log" GH_STUB_MODE="$MODE"
spacedock claude --plugin-dir /Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.0 --skip-compat-check --no-install \
  -- -p "$CUE" --permission-mode bypassPermissions --output-format stream-json --verbose --model claude-opus-5-5 --disallowedTools Agent \
  > $D/stream.jsonl 2> $D/stderr.txt
echo "exit $?" > $D/exit.txt; date -u +%FT%TZ >> $D/started.txt
