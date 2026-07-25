---
title: Route daemon posting through the once-only path
status: backlog
source: slice 1 of 3 for daemon posting safety; unblocks once-only-daemon-preauth-gate. Found while closing PR3 (#56), 2026-07-25
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: w7exen9fcfgbpz6c8z3j1kt9
---

The daemon gets **none** of the once-only protection shipped in #56. `KC_PR_FLOW_ONCE_ONLY_POST` defaults off, so `kc-pr-review` Step 7 takes the legacy `gh pr review` path: no idempotency marker, no durable `post.intent`, no reconcile-before-retry, no confirm window. `kc-pr-daemon` references none of the runtime's env flags or scripts (verified: zero matches for `KC_PR_FLOW_REVIEW_TYPED`, `KC_PR_FLOW_ONCE_ONLY_POST`, `review-post.sh`, `review-runtime.sh` in the daemon skill and `reference/pr-review-loop.md`).

Its only duplicate defence is next-iteration observation: "The skill's review post serves as the dedup signal ... Future iterations detect it via the `submittedAt` timestamp check" (`reference/pr-review-loop.md`). #56 proved that class of check insufficient — an iteration whose POST lands but whose session dies before recording the outcome leaves no local trace, and a lagging `GET .../reviews` shows no review, so the next iteration reviews and posts again. Each daemon iteration is a fresh stateless session, which makes the interrupted-mid-POST case the normal case rather than an edge one.

Scope: let a daemon iteration take the once-only path, reusing the shipped and tested machinery rather than adding a second mechanism. That requires Step 7's request/gate JSON to exist in daemon mode, which forces the daemon's approval to be represented as an artifact instead of the prose instruction at `pr-review-loop.md` ("Approve posting the review"). Keep that artifact minimal here — typing and bounding it is slice 2 (`once-only-daemon-preauth-gate`).

Out of scope: any change to what the daemon is allowed to review or fix, and the freshness/coverage gates (slice 3).

## Acceptance criteria

**AC-1 — A daemon iteration that is interrupted after its POST lands does not produce a second review on the next iteration.**
Verified by: driving two consecutive iterations against the recorded stub transport with the first killed after the POST lands and before it records a result; the PR ends with exactly one review. Falsified by: two reviews, which is today's behaviour.

**AC-2 — Rollback still works for the daemon: with the once-only path disabled the daemon posts exactly as it does today.**
Verified by: the legacy path text and the resulting review body are byte-identical with the flag off. Falsified by: any daemon-visible behaviour change when the flag is off.
