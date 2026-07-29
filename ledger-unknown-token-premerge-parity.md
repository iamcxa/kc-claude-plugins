---
title: Let truthful all-unknown token rows pass the ledger lifecycle gate
status: implementation
source: blocked n9 at the accepted-validation boundary after PR #81 landed, 2026-07-29
started: 2026-07-29T14:13:05Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-ledger-unknown-token-premerge-parity
issue:
pr:
design: trivial-pass
id: s6943mgrss28mygnm1wjb408
lane: defect
---

PR #81 made accepted validation upsert and verify a complete ledger row before the product PR. The shipped contract contradicts itself for runtimes that expose no per-dispatch token usage: `docs/dev/README.md:1149-1152` says an all-unknown set is recorded as `tokens_if_known=n/a`, while `ledger_verify` at `README.md:1295-1315` accepts only numeric token notation and the later bar text at `README.md:1569-1571` says a done transition may not leave tokens at `n/a`.

For n9, all five Codex dispatches truthfully recorded `tokens: n/a (Codex runtime did not expose per-worker usage)`. Substituting `0+` or an invented number would make the ledger pass by falsifying its evidence. The captain approved the contract direction: an all-unknown `n/a` row is complete and terminalizable, but excluded from baseline and bar comparisons; blank or missing evidence remains incomplete.

**AC-1 — A fully instrumented all-unknown token row passes both ledger lifecycle phases without inventing a number.**
Verified by: extending the disposable ledger fixture with one `tokens_if_known=n/a` row that returns `ledger:exact` in `premerge`, then finalizes its sentinels and returns `ledger:exact` in `terminal`. Falsified by: either phase returning 43.

**AC-2 — Missing token evidence still fails closed.**
Verified by: a distinct fixture row with a blank token cell still returns 43 in `premerge`; the change must not make blank, malformed, or duplicate rows valid. Falsified by: any such row returning 0.

**AC-3 — The prose and executable gate state the same policy.**
Verified by: the lifecycle text says all-unknown `n/a` is complete but excluded from baselines, and no remaining done-transition clause forbids the value the roll-up clause requires. Falsified by: a contradictory `done` prohibition or baseline inclusion claim remaining.

## Defect-lane classification

All four bounded-defect conditions hold:

1. Root cause is cited at `docs/dev/README.md:1149-1152`,
   `docs/dev/README.md:1295-1315`, and `docs/dev/README.md:1569-1571`: the
   roll-up contract requires `n/a`, while the verifier and later prose reject it.
2. Acceptance is mechanical through the shipped disposable lifecycle fixture:
   an all-unknown row must pass premerge and terminal, while a blank row remains red.
3. This is one contract seam in `docs/dev/README.md`: token-cell completeness
   semantics, its embedded verifier, and the verifier's own fixture.
4. No design choice remains open. The captain approved truthful all-unknown
   `n/a` as complete but excluded from baseline and bar comparisons.

Design: `trivial-pass` — reconcile the executable gate with the already-approved
roll-up policy; no new ledger field, schema, or lifecycle stage.

Appetite: one implementation dispatch, estimated 60 minutes. Tolerance: up to
90 minutes or one correction commit; if the fix needs a schema change, a
different unknown-value encoding, or files outside `docs/dev/README.md`, return
to ideation.

Implementation dispatch sizing: one fresh worker in one isolated worktree.
Validation remains a fresh-context gate.

## Approved doc diff

- Before: all-unknown dispatch tokens roll up to `n/a`, but premerge/terminal
  reject that same value and the done-transition prose forbids it.
- After: a populated `n/a` token cell is a complete, terminalizable
  all-unknown row; it remains excluded from token baselines and comparisons.
  Blank, malformed, missing, and duplicate evidence still fails closed.

## Measurement

- D1 launched 2026-07-29T14:13:26Z | tokens: pending

## Stage Report: implementation

- DONE: Before editing the contract, extend the shipped disposable lifecycle fixture so a fully populated tokens_if_known=n/a row proves the current premerge and terminal failures, while a blank token row remains fail-closed; record the expected RED evidence.
  RED `all-unknown-premerge`: the full fixture exited 1 at the new expected-0 assertion after `ledger:incomplete`; changing the verifier to continue rejecting `n/a` restores this failure.
  RED `all-unknown-terminal`: the isolated case reported `ledger:incomplete`, actual verifier rc 43 versus expected rc 0; rejecting `n/a` in terminal restores this failure.
  Guard `blank-tokens`: verifier rc 43 matched expected rc 43 before and after the fix; accepting a blank token cell falsifies AC-2.
- DONE: Make the minimum docs/dev/README.md-only change that treats all-unknown n/a as a complete but baseline-excluded token cell in the verifier and prose, with no schema, sentinel, or lifecycle-stage change.
  Code commit `cac584e` changes only `docs/dev/README.md`: the shared token-completeness predicate admits exact `n/a`, and prose keeps it outside baseline/bar comparisons.
  The former `incomplete.csv` n/a arrangement became the approved all-unknown case; `blank-tokens.csv` preserves its fail-closed intent, while the legacy and coverage-n/a arrangements retain their original purposes.
- DONE: Run the complete disposable ledger lifecycle fixture, status --validate, consistency searches for contradictory n/a/done claims, and git diff --check; commit only docs/dev/README.md and report RED/GREEN plus changed-claim falsifiers.
  GREEN full lifecycle: both all-unknown phases emitted `ledger:exact`; blank, missing, duplicate, finalized-as-premerge, and reversed-timestamp cases retained their expected nonzero results.
  `status --workflow-dir docs/dev --validate ... --json` returned `{"command":"validate","valid":"true"}`; warnings referenced pre-existing verdict casing in other entities.
  Positive policy search found complete all-unknown, `tokens_complete`, baseline exclusion, and blank guard clauses; the old token predicate, two-notation heading, legacy-only n/a clause, and done prohibition were absent.
  `git diff --check` passed and the changed-file assertion was exactly `docs/dev/README.md`; no schema, sentinel, lifecycle-stage, or CI-enlisted test changed.

### Summary

Implemented the approved ledger parity rule in `cac584e`: an exact populated `n/a` token cell now passes both premerge and terminal verification, while remaining excluded from token baselines and bar comparisons. The disposable lifecycle fixture proves both phases and preserves fail-closed blank evidence; fresh validation and consistency checks passed.
