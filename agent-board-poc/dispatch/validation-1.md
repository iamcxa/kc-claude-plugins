# Dispatch: agent-board-poc validation cycle 1

Dispatched: 44e8de6db9fa75ac40569f630cef54f46b52e2c1
Model: sonnet
Worker: spacedock-ensign-agent-board-poc-validation (spacedock:ensign, fresh)

## Checklist

1. Independent verdict on AC-1, AC-2 and AC-3 at candidate 44e8de6d, from your own re-run of the wake exchange (both wake candidates), not from the implementation report's numbers
2. A minimal acceptance script of three to six steps the Captain can run himself, each with its expected output, including one step that checks the wake inside a real Conductor-app Claude session (the part the replica does not prove)
3. `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0/scripts/adr_lint.py docs/adr --since <merge-base>` run with its exit code, plus any `boundary-crossed:` marker this POC's state or seams warrant, with one sentence of evidence

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Candidate: branch spacedock-ensign/agent-board-poc at 44e8de6d, worktree /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/.worktrees/spacedock-ensign-agent-board-poc. The diff against its merge base is five files under scripts/agent-board-poc/.

You are the fresh, independent validator for a POC. Check the exact artifact against the task's accepted outcome, scope, non-goals and stop condition. Do not take over implementation: a defect goes in your report as a finding with evidence, not a fix.

Re-run, do not re-read: start the replica yourself with both wake candidates and a codex exec asker, and record your own timestamps. Run codex exec with stdin closed (< /dev/null). Use a cheap model for the Claude replica.

Check the implementation report's claims you can falsify cheaply, including: the cleanup it describes (no leftover /tmp stores, processes or ~/.codex/config.toml trust entries after YOUR runs too — clean up after yourself the same way, by captured PID, never pkill -f or a pattern); the "exactly once" delivery claim with several waiters, and whether that is the right behaviour for a board several sessions read; and the SessionStart-hook blocking finding.

Never edit user-level settings, MCP or hook registrations. If codex exec -C <dir> adds trust entries to ~/.codex/config.toml, remove only the lines your run added and show the diff in your report.

Goal sufficiency and minimal necessity: say whether the five files are enough for the Captain's decision (is cross-harness wake viable) and whether anything in them is unneeded for it.
