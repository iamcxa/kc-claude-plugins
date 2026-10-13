#!/usr/bin/env bash
# Codex asks, an idle Claude Code replica wakes and answers. Usage: exchange.sh hook|shell
# Prints the board log; stream-json lines with timestamps stay in $W/stream.log until KEEP is unset.
set -euo pipefail
WAKE=${1:?hook or shell}
HERE=$(cd "$(dirname "$0")" && pwd)
W=${W:-$(mktemp -d /tmp/agent-board-poc.XXXXXX)}
export AGENT_BOARD_DB=$W/board.db
BOARD=$HERE/board.py

if [ "$WAKE" = hook ]; then
  SETUP="Reply with the single word READY and stop."
  AGAIN=""
else
  SETUP="Start this as a background Bash command (run_in_background true), then stop your turn: AGENT_BOARD_DB=$AGENT_BOARD_DB python3 $BOARD wait --reader claude --timeout 600"
  AGAIN=" Before stopping, start the same background wait command again."
fi
PROMPT="You are the Claude end of a message board (MCP server 'board'). $SETUP
Later a message from another sender arrives; answer it by calling the board post_message tool, then stop your turn.$AGAIN"

python3 "$HERE/replica.py" --db "$W/board.db" --wake "$WAKE" --out "$W/stream.log" --seconds "${SECONDS_TOTAL:-150}" --prompt "$PROMPT" >"$W/replica.out" 2>&1 &
REPLICA=$!
trap 'kill $REPLICA 2>/dev/null || true' EXIT
until grep -q '"type":"result"' "$W/stream.log" 2>/dev/null; do sleep 1; done

QUESTION="Use the board MCP server. Call post_message with the text 'What is 6 times 7?'. Then call wait_for_messages with after_id set to the id post_message returned and timeout_s 20; if it returns no messages, call it again with the same after_id, up to 6 times. When a reply arrives, print its text prefixed with ANSWER:."
codex exec --ignore-user-config --skip-git-repo-check --ephemeral --dangerously-bypass-approvals-and-sandbox -C "$W" \
  -c 'mcp_servers.board.command="python3"' \
  -c "mcp_servers.board.args=[\"$BOARD\",\"serve\"]" \
  -c "mcp_servers.board.env={AGENT_BOARD_DB=\"$AGENT_BOARD_DB\",AGENT_BOARD_SENDER=\"codex\",AGENT_BOARD_HARNESS=\"codex-exec\"}" \
  "$QUESTION" </dev/null | tee "$W/codex.out"
echo "---- board log ($W)"
python3 "$BOARD" log
