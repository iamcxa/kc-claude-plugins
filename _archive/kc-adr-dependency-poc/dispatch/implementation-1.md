# implementation-1

Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0 (dev2-poc workflow checkout, kc-dev-flow-2 0.27.0 README); POC, first dispatch
Model: sonnet

## Checklist

Answer the four questions in the task Scope with real installs, one arm at a time (native dependency if either host has one, symlink, run-time resolution, wrap-not-move as the control), on Claude Code and on Codex, each claim citing the tool's own docs, `--help` or the observed install result
A report under the task folder in the state checkout (report.md) with one row per arm and host against the bar (installs, update reaches dev2, absent kc-adr refuses loudly, incompatible version caught), the recommended arm, and what a move would change in the four adopters' READMEs and pins
Every probe runs with throwaway plugin roots and an isolated config (for example a temporary HOME or CLAUDE_CONFIG_DIR and a temporary Codex home), never the Captain's real ~/.claude or ~/.codex installs, and each probe directory is removed after; the report states the isolation used

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0

Profile: poc. Task kc-adr-dependency-poc in workflow /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc. The Captain's words and the arms and bar are in the task Scope. Build any stand-in kc-adr or dev2 plugin as a minimal throwaway plugin in /tmp; do not edit any file of this repository, any adopter, or any installed plugin. Read the kc-adr boundary contract at PR #691 (`gh pr view 691 --repo iamcxa/kc-claude-plugins`, branch docs/kc-decision-log-boundary) and kc-dev-flow-2's `scripts/number_guards.py`, `scripts/adr_lint.py` and ADR template read-only from origin/main. Commit the report with `spacedock state commit kc-adr-dependency-poc --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc`.

roborev not run: no repository diff (the POC writes only its report in the state checkout).

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not push, open or comment on any PR or issue, or message any other session. If a command is refused by the permission check, stop and report it.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
