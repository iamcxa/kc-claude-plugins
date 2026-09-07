# batch-ab2fb2635f0c — QNow PoC acceptance, second batch (code_repo iamcxa/qnow)

Plan receipt ab2fb2635f0ce205 (session plan-flow-session-2026-09-07b-qnow); approval: go · 13 workspaces · concurrency 1 · repair 2 · Pilot.
Pre-batch blocker: DEV-114 (kc-claude-plugins merge station script) — every merge in this batch goes through it.
Order: DEV-136 (support files PR) → DEV-137 (hosted/ PR) → DEV-36 (#1174 rebased onto main) → DEV-37 (Conductor cloud, one deploy, Captain watching).
Runtime: local Sonnet workers in worktrees; FO stations local via ~/.claude/plugins/local/kc-ship-flow (main 1d4e95e0).

## Decisions made under `defaults`

- 2026-09-07T07:02:36Z — **DEV-114 accepted** (station 1d4e95e0, ACCEPT with AC-3 WARN partial variant); Draft PR #391 (merge-station.sh + test + fake-gh-merge fixture + station page + docs/ship merged line). Review: code-reviewer + silent-failure-hunter dispatched. Every later merge in this batch must go through this script once it lands.
