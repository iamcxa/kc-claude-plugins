# validation-1

Dispatched: from workflow checkout at 6d344bcb6ced154fb1aeb3b4e362676c80aec443 (kc-claude-plugins, detached; the workflow README there was the 2026-10-08 copy, not the 0.21.0 sync)
Model: sonnet
Recorded: 2026-10-13, after the fact by FO; the original dispatch files were under /tmp/spacedock-dispatch/

## Checklist

Independent verdict on #627 (head 89769eb6) and #628 (head d8281e1c) against AC-1, AC-2, AC-4, AC-5, AC-6 and AC-11, re-running each Verified-by command and at least one falsifier per criterion yourself rather than citing the implementation report
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh shell from a named checkout, with its observed output
adr_lint.py docs/adr --since <base> run with its exit code, and unverified obligations named (billed CI minutes, Release PR smoke, live adopter run)

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.20.0

Profile: pilot. The PRs are stacked: #628's base is #627's branch, so check out each head in a throwaway worktree. Read and run only; do not push, comment on the PRs, or edit a candidate. A repair goes back through feedback.

The minimal acceptance script follows kc-dev-flow-2 0.21.0's validation rule, which the next FO will apply: it must run unchanged in a fresh shell and must name any checkout or install it needs.
