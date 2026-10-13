---
title: The journey-map footprint and fold commands refuse inputs that can only produce a record no check reads or a clean count that read nothing
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined under the round-3 rule from the third external review round (Codex) of iamcxa/kc-claude-plugins PR #627 (head 32db1273, review:5499643839) and PR #628 (head 7d89898e, review:5499645217), 2026-10-13, task `journey-map-dev2-contract`, plus one Deferred risk its validation cycle 3 recorded. None is P1 or Material, so none started a repair cycle there; each is filed here with its decline reason, per `## FO steps: review findings` step 5.

## Scope

- Finding 1 (Codex P2, #627 `map_footprint.py` `add`, `--story`): on a task with `journey` but no `journey-story`, `add --story` appends a footprint that `check` and `audit` later skip, because a journey task needs both fields. Decline reason: FO sets `journey-story` at Release review before any gate footprint, and the extension's instruction never passes `--story` for a task without one; no observed trigger.
- Finding 2 (Codex P2, #627 `map_footprint.py` `add`, `--question ''`): an empty question id is written and `add` exits 0; the next `check` rejects the line. Decline reason: the error is caught by the next `check` before merge guard, so it fails closed; the cost is a hand edit of one JSONL line.
- Finding 3 (Codex P2, #627 `map_footprint.py` `audit --since`): an impossible date such as `2026-13-01` passes the shape check and sorts after every real date, so audit can skip every task and print clean zeros. Decline reason: the cutover date is set once per adopter at extension adoption and read back at each release review; a typo there is an operator error with no observed instance. Same class as Deferred risk 5 below.
- Finding 4 (Codex P2, #628 `journey-fold.mjs` `already`): editing a folded question's `source.words`, `source.date` or `source.kind` while keeping `source.ref` still reads `already`, so reconcile does not see the corrupted provenance. Decline reason: needs a hand edit of the source block of an answered question; no observed instance, and the round-2 repair already catches an edited answer or status.
- Deferred risk 5 (validation cycle 3): `journey-reconcile.mjs --workflow-dir` and `audit` accept a wrong directory that holds a README (the repository root, a plain-text README), and `spacedock status` lists no tasks there, so the counts read clean. Would become Material if a release-review command passes a wrong directory that holds a README and the clean count is read as proof. Candidate fix named there: require the README to declare a Spacedock workflow, or print a "tasks read: N" line.
- Polish 6 (validation cycle 3): `ambiguous` in `FAILING` in `journey-fold.mjs` is reached by no path (the command throws first); `audit`'s usage text still names only "exit 2 without --since"; `audit` labels the not-needed contradiction `unrecorded`.
- Non-goals: to be set at ideation. `journey-progress.mjs` accepting a nonexistent `--workflow-dir` (outside #628's diff) is a candidate to fold in under Deferred risk 5.

## Acceptance criteria

To be written at ideation.

## FO alignment

Needed at ideation: whether findings 1-4 and risk 5 land as one patch, once the Captain schedules this task.
Surfaces: none
Visible change: none
