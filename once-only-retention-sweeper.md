---
title: Once-only posting retention sweeper (autonomous GC)
status: backlog
source: deferred from safe-resume-once-only-post (PR3) gate decision D4 cut-order second item, 2026-07-25
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: 7jjpw4c26fcv0tw8pg5fnr6h
---

Deferred from PR3 `safe-resume-once-only-post` per captain gate decision D4 (cut order, second-cut item). PR3 shipped the bounded-expiry retention policy and an on-demand `review-post.sh gc` hook (commit 174dfb4); what remains deferred is the AUTONOMOUS invocation — no cron/daemon wiring runs GC on a schedule today. Documented as deferred in `kc-pr-flow/CLAUDE.md`, `README.md`, and `reference/review-runtime.md`.

Scope: wire a scheduled/daemon invocation of `review-post.sh gc` that expires past-retention-window pending payloads while preserving the fail-safe invariant (never GC a within-window unreconciled payload).

## Acceptance criteria

**AC-1 — Past-window pending payloads are expired without manual invocation, and within-window unreconciled payloads are never GC'd.**
Verified by: a test driving the autonomous trigger that expires an aged pending payload and leaves a fresh one intact. Falsified by: a within-window payload removed, or a past-window payload surviving a scheduled run.
