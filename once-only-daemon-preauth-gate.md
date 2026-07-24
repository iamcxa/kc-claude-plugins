---
title: Once-only posting active daemon preauthorization gate
status: backlog
source: deferred from safe-resume-once-only-post (PR3) gate decision D4 cut-order first item, 2026-07-25
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: vf88cvthkhh9je2ng71xbbs9
---

Deferred from PR3 `safe-resume-once-only-post` per captain gate decision D4 (cut order, first-cut item). Today the entire daemon-safety mechanism is default-deny-by-absence: `KC_PR_FLOW_ONCE_ONLY_POST` off denies every caller (commit 174dfb4). Documented as deferred in `kc-pr-flow/CLAUDE.md`, `README.md`, and `reference/review-runtime.md`.

Scope: an ACTIVE daemon preauthorization gate for autonomous posting — typed decision state + coverage + a fresh head/idempotency recheck immediately before an autonomous post, so a daemon may post only under an explicit, current, typed authorization rather than merely the rollback flag being on.

## Acceptance criteria

**AC-1 — An autonomous (daemon) post is refused unless a typed preauthorization with current head, coverage, and idempotency gates is present and fresh.**
Verified by: a test where a daemon post is denied on stale/absent preauth and allowed only with a fresh typed gate. Falsified by: a daemon post proceeding on a stale head or without the typed gate.
