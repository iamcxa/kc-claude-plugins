---
id: pmh2t9zpz4ayz9qqm2550x8s
title: Re-test whether scheduled Spacedock projection automation is still necessary
status: backlog
source: Speculative automation escape required by kc-dev-flow reverse-recovery policy at origin/main@5f14040b; review on 2026-09-14
product: kc-dev-flow
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design: required
lane:
---

On or after 2026-09-14, re-test whether the installed scheduled reconcile remains necessary after real kc-claude-plugins dogfood. Removal is the default recommendation unless evidence shows that manual or explicit post-state-push dispatch alone misses the configured freshness window or fails recovery after a dropped run.

## Acceptance criteria

### AC-1 — The automation must re-earn its durable cost

Compare dogfood reconcile receipts for scheduled runs, manual/explicit dispatches, missed freshness windows, and recovery from one deliberately skipped or failed fast-path run. Keep the schedule only when the observed history plus a live removal mutant demonstrates a named projection-liveness failure without it. Otherwise remove the schedule while preserving manual dispatch and deterministic reconciliation.

Verified by: receipt inventory, one schedule-disabled observation window, and before/after run evidence. Falsified by: retaining the schedule only because it already exists or removing it without proving the remaining path converges.

## Authority

This seed grants no change, removal, sprint admission, or execution authority. It exists only as the dated review target required by the originating automation's speculative escape record.
