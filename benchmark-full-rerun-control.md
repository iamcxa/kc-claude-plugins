---
title: Give the token benchmark a real full-rerun control
status: backlog
source: token-efficiency claims are currently unmeasurable against a real baseline, 2026-07-25
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: qef01h5aj8qwgggmpme7hy8y
---

The typed review runtime exists to spend fewer tokens, and it already has promotion gates (G1-G5, correctness before efficiency, and only the documented 20% reported-token or 60% bound local-rehydration branch). What it does not have is a trustworthy denominator: `reference/review-runtime.md` states plainly that "replay output is not a full-rerun control".

So the saving is unproven in either direction. Nobody can currently say whether typed mode saves 20% or 2%, and no promotion decision resting on that number is defensible. That makes this a measurement task, not an optimisation task — and it should land before any work that claims a token win.

Scope: a control arm that actually re-runs the designed full review, so treatment and control are comparable under `canonical-artifact-bytes/v1`, plus the recorded numbers for at least one real review.

## Acceptance criteria

**AC-1 — A paired run reports treatment and control token counts where the control is a genuine full rerun, not a replay.**
Verified by: the recorded pair plus the command that produced the control, showing it re-executed the review rather than rehydrating a receipt. Falsified by: a control derived from replay, or a pair whose two arms are not byte-comparable.

**AC-2 — The measured delta is written down with its inputs, so a later promotion decision can be re-checked rather than re-argued.**
Verified by: a recorded number tied to a specific review identity and runtime version. Falsified by: a percentage with no reproducible provenance.
