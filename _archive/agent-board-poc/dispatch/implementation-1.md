# Dispatch: agent-board-poc implementation cycle 1

Dispatched: 3ece141a8dd5f2320373b682546207b2820d10c5
Model: sonnet
Worker: spacedock-ensign-agent-board-poc-implementation (spacedock:ensign)

## Checklist

1. AC-1: an idle Claude Code session launched with Conductor's flags starts a new turn after a board post with no user input between, reads and replies through the MCP server, and waits again; evidence is its stream-json output with timestamps, for each wake candidate tried, naming which worked
2. AC-2: a `codex exec` session with the board MCP configured posts a question, waits with bounded `wait_for_messages` calls, and prints the woken Claude's answer; evidence is the Codex output plus the board log
3. AC-3: one command prints every message of the AC-1/AC-2 exchange with sender, harness, time and text; evidence is that output, plus the cleanup done and what the POC does not prove

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: poc. Follow the task's Scope, non-goals, budget and stop condition exactly; they are Captain rulings from 2026-10-13. If neither wake candidate starts a new Claude turn, stop and report — do not build AC-2/AC-3 on top of a failed AC-1.

Facts the FO verified on 2026-10-13 (re-check any you rely on):
- Conductor launches Claude Code as: `claude --output-format stream-json --verbose --input-format stream-json --thinking adaptive --thinking-display summarized --effort high --max-turns 1000 --model <model> --permission-prompt-tool stdio --disallowedTools AskUserQuestion --setting-sources=user,project,local --permission-mode bypassPermissions --session-mirror --plugin-dir <dir> --session-id=<uuid> --settings '{...}'` (read from `ps`). It loads plugins with `--plugin-dir`, so the replica can load the POC plugin the same way. Use a cheap model (sonnet or haiku) for the replica and the answering turn; the wake behaviour is what is under test, not the model.
- Claude Code hooks docs (https://code.claude.com/docs/en/hooks): `asyncRewake: true` on a command hook "runs in the background and wakes Claude on exit code 2"; its stderr (or stdout if stderr is empty) reaches Claude as a system reminder. The docs do not say whether this works in stream-json/SDK mode — that is exactly what AC-1 measures.
- Claude Code Channels are out of scope (docs: the development-channels flag is ignored in non-interactive/SDK mode).
- Codex: `codex exec` waits on stdin unless stdin is closed — run it with `< /dev/null`. Register the board MCP server per run with `-c` overrides (see `codex exec --help` and `codex mcp --help`), not by editing `~/.codex/config.toml`. A Codex session cannot be woken while idle (Codex's own read of its runtime, 2026-10-13, kept at /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/agent-board/codex-wake-answer.md); Codex is the asker only.
- Verify every CLI flag against `<tool> --help` before using it; do not trust docs, READMEs or memory for flag names.

Repository constraints:
- Put the POC under a path that is NOT `<top-level-dir>/.claude-plugin/plugin.json`: `scripts/version-parity-check.sh` fails closed on any top-level plugin directory without a marketplace entry, and marketplace registration is a non-goal. Confirm your chosen path passes `bash scripts/version-parity-check.sh` and `bash scripts/skill-frontmatter-lint.sh`.
- Prefer zero or minimal dependencies; if you add one, pin a version you verified exists in its registry.
- Comments: run `python3 <package>/scripts/comment_ratio.py` as the implementation skill directs; no comment narrates the change or cites a file:line, task or PR.
- Leave no user-level MCP server, hook or settings change installed. Test stores live under the worktree or /tmp and are deleted at the end; record the cleanup.
- Commit format: `feat(<scope>): …` Conventional Commits; stage files explicitly, never `git add .`.

Prior art to borrow designs from (do not vendor code; licences differ): agent-inbox (PyPI, `asyncRewake` Stop-hook wake), claude-message-mcp (github.com/aeriondyseti/claude-message-mcp, `wait_for_messages` + idle command), agent-mailbox-mcp (github.com/lleontor705/agent-mailbox-mcp, SQLite schema/tool shapes, MIT), Agent Intercom (github.com/ctliz/agent-intercom-codex, bounded-wait loop).
