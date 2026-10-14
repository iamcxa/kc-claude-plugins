#!/bin/bash
# usage: run.sh <run-name> <merged|open> <control|mod> <cue>
RUN=$1; MODE=$2; ARM=$3; CUE=$4; D=/tmp/val643-replay/$RUN; cd $D/relay
echo $$ > $D/pid.txt; date -u +%FT%TZ > $D/started.txt
export PATH="/tmp/val643-replay/bin:$PATH" GH_STUB_LOG="$D/gh-calls.log" GH_STUB_MODE="$MODE" PYTHONDONTWRITEBYTECODE=1
EXTRA=()
[ "$ARM" = mod ] && EXTRA=(--plugin-dir /tmp/val643-replay/pkg/kc-dev-flow-2)
spacedock claude --plugin-dir /Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.0 --skip-compat-check --no-install \
  -- -p "$CUE" --permission-mode bypassPermissions --output-format stream-json --verbose --model claude-opus-5-5 --disallowedTools Agent,SendMessage "${EXTRA[@]}" \
  > $D/stream.jsonl 2> $D/stderr.txt < /dev/null
echo "exit $?" > $D/exit.txt; date -u +%FT%TZ >> $D/started.txt
