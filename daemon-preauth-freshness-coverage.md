---
title: Gate autonomous posts on fresh head and complete coverage
status: backlog
source: slice 3 of 3 for daemon posting safety; depends on once-only-daemon-preauth-gate (slice 2), 2026-07-25
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: x0fxzgrqcmtsbvp4c2cnp7z0
product: kc-pr-flow
sprint: S6
---

**Unblocked 2026-07-26.** `attended-pr-review-wait` (4p) briefly threatened this slice's
premise by proposing to remove the unattended caller entirely; the captain parked it the
same day because unattended operation is a standing daily need. This slice still depends on
slice 2 (`once-only-daemon-preauth-gate`), and on nothing else.

Once a daemon iteration carries a typed preauthorization (slice 2), two checks remain before it may post autonomously, both of which a human at the §6c gate supplies implicitly today:

- **Freshness.** The head may have moved between classification and posting. The interactive path already invalidates on `head_moved`; an autonomous post needs the same recheck immediately before the mutation, against the preauthorization's bound head and idempotency key.
- **Coverage.** `InteractiveCollationDecision/v1` already computes required gaps and caps the event at COMMENT when coverage is incomplete. A human can knowingly post a partial review; a daemon should not. An autonomous post whose typed decision reports required gaps must be refused rather than silently downgraded.

Scope: the two gates plus their refusal receipts. No new posting mechanism — this constrains the one from slices 1-2.

## Acceptance criteria

**AC-1 — An autonomous post is refused when the head moved after preauthorization, and the refusal is recorded.**
Verified by: a test moving the head between preauthorization and post; the attempt is denied and leaves a typed refusal, not a stale post. Falsified by: posting against the old head, or denying with no record.

**AC-2 — An autonomous post is refused when the typed decision reports required coverage gaps.**
Verified by: a decision carrying required gaps drives a denial; the same decision with gaps satisfied is allowed. Falsified by: an autonomous post proceeding on incomplete coverage, or a complete decision being refused.
