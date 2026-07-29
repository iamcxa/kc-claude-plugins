---
title: Let truthful all-unknown token rows pass the ledger lifecycle gate
status: validation
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

- D1 launched 2026-07-29T14:13:26Z | tokens: n/a (Codex runtime did not expose per-worker usage)
- D2 launched 2026-07-29T14:21:49Z | tokens: n/a (Codex runtime did not expose per-worker usage)

## Stage Report: implementation

- DONE: Before editing the contract, extend the shipped disposable lifecycle fixture so a fully populated tokens_if_known=n/a row proves the current premerge and terminal failures, while a blank token row remains fail-closed; record the expected RED evidence.
  RED `all-unknown-premerge`: the full fixture exited 1 at the new expected-0 assertion after `ledger:incomplete`; changing the verifier to continue rejecting `n/a` restores this failure.
  RED `all-unknown-terminal`: the isolated case reported `ledger:incomplete`, actual verifier rc 43 versus expected rc 0; rejecting `n/a` in terminal restores this failure.
  Guard `blank-tokens`: verifier rc 43 matched expected rc 43 before and after the fix; accepting a blank token cell falsifies AC-2.
- DONE: Make the minimum docs/dev/README.md-only change that treats all-unknown n/a as a complete but baseline-excluded token cell in the verifier and prose, with no schema, sentinel, or lifecycle-stage change.
  Code commit `da74fd2` changes only `docs/dev/README.md`: the shared token-completeness predicate admits exact `n/a`, and prose keeps it outside baseline/bar comparisons.
  The former `incomplete.csv` n/a arrangement became the approved all-unknown case; `blank-tokens.csv` preserves its fail-closed intent, while the legacy and coverage-n/a arrangements retain their original purposes.
- DONE: Run the complete disposable ledger lifecycle fixture, status --validate, consistency searches for contradictory n/a/done claims, and git diff --check; commit only docs/dev/README.md and report RED/GREEN plus changed-claim falsifiers.
  GREEN full lifecycle: both all-unknown phases emitted `ledger:exact`; blank, missing, duplicate, finalized-as-premerge, and reversed-timestamp cases retained their expected nonzero results.
  `status --workflow-dir docs/dev --validate ... --json` returned `{"command":"validate","valid":"true"}`; warnings referenced pre-existing verdict casing in other entities.
  Positive policy search found complete all-unknown, `tokens_complete`, baseline exclusion, and blank guard clauses; the old token predicate, two-notation heading, legacy-only n/a clause, and done prohibition were absent.
  `git diff --check` passed and the changed-file assertion was exactly `docs/dev/README.md`; no schema, sentinel, lifecycle-stage, or CI-enlisted test changed.

### Summary

Implemented the approved ledger parity rule in `da74fd2`: an exact populated `n/a` token cell now passes both premerge and terminal verification, while remaining excluded from token baselines and bar comparisons. The disposable lifecycle fixture proves both phases and preserves fail-closed blank evidence; fresh validation and consistency checks passed.

## Stage Report: validation — 2026-07-29

### Summary

Fresh-context validation **PASS** on exact code head
`da74fd21ebe0b993832366d353854b2e806c49d5`. The complete embedded lifecycle
fixture exited 0. Direct named cases returned `ledger:exact`/rc 0 for populated
all-unknown `n/a` in both premerge and terminal, while blank and malformed token
cells returned rc 43, a missing row returned rc 41, a duplicate row returned rc
42, and a terminal row presented to premerge returned rc 43.

No implementation file or README was edited. The code worktree remained clean on
`spacedock-ensign/ledger-unknown-token-premerge-parity` at the dispatched head.

### Acceptance evidence

- **AC-1 PASS:** Loaded the exact-head embedded `ledger_upsert` and
  `ledger_verify`, plus `ledger_phase` from the documented `pr-merge` hook, and
  executed the complete disposable fixture. `all-unknown-premerge.csv` and
  `all-unknown-terminal.csv` each emitted `ledger:exact` with rc 0.
- **AC-2 PASS:** The complete fixture preserved the expected nonzero outcomes.
  A separate named replay made the outcomes explicit: blank token rc 43,
  missing row rc 41, malformed token `unknown` rc 43, duplicate row rc 42, and
  terminal-as-premerge rc 43.
- **AC-3 PASS:** The revised policy agrees at the roll-up, verifier, fixture,
  baseline, and bar clauses. Searches found no residual `tokens_recorded`,
  two-notation heading, done/terminal prohibition on token `n/a`, or claim that
  `n/a` participates in the baseline. The parent citations resolve exactly at
  `96fe7f3`: roll-up `README.md:1149-1152`, numeric-only predicate
  `README.md:1295-1315`, and done prohibition `README.md:1569-1571`.
- **Workflow validation PASS:** `spacedock status --workflow-dir
  /Users/kent/conductor/workspaces/kc-claude-plugins/antananarivo/docs/dev
  --validate --json` returned `{"command":"validate","valid":"true"}`. Its
  warnings were pre-existing lowercase verdict values in other entities.
- **Scope/static PASS:** `96fe7f3..da74fd2` changes exactly
  `docs/dev/README.md` (47 insertions, 28 deletions); `git diff --check` returned
  no diagnostics.

### Lens and citation verification

- **Correctness PASS, 0 findings:** The exact `n/a` branch feeds the shared
  `tokens_complete` predicate used by premerge and terminal; the fixture and
  direct named replay exercised both phases and all required failure classes.
- **Silent-failure PASS, 0 findings:** Whitespace-only cells normalize to empty
  and remain invalid; `unknown` remains malformed; missing, duplicate, wrong
  phase, and reversed timestamps retain their distinct fail-closed results.
- No security/auth/permission, type-design, concurrency, resource-lifecycle, or
  manifest/back-compat surface changed.
- `agy` 1.1.8 ran a Google cross-vendor review with
  `gemini-3.1-pro-high` requested and returned **CLEAN**, 0 P0-P3. Its cited
  ranges `README.md:920-960`, `1100-1245`, `1246-1355`, `1356-1506`, and
  `1507-1600` were independently checked at exact head; all matched. Its only
  residual noted possible out-of-diff verifier copies; repository search found
  no second `ledger_verify` definition, and `_mods/pr-merge.md` explicitly
  invokes the README verifier.

### Claim-breaking mutations

- **Reject `n/a` again:** In an isolated scratch copy, disabled the exact `n/a`
  branch of `tokens_complete`. The committed `all-unknown-premerge` expectation
  changed from green to red: verifier output `ledger:incomplete`, fixture
  assertion command rc 1.
- **Accept blank tokens:** In a separate scratch copy, admitted `""` alongside
  `n/a`. The committed `blank-tokens` expectation changed from green to red:
  verifier output `ledger:exact` instead of expected rc 43, fixture assertion
  command rc 1.

### Evidence block

Lenses: Markdown contract with embedded Bash/Python input-validation behavior;
correctness PASS (0 findings) and silent-failure PASS (0 findings); no other
mechanical lens matched the changed surfaces.
Diff coverage: N/A — the committed diff is `docs/dev/README.md` only, with no
changed script, hook, MCP, or server file; the embedded verifier and complete
lifecycle fixture were executed directly instead.
Adversarial: PASS — rejecting `n/a` made `all-unknown-premerge` red, and
accepting blank tokens made `blank-tokens` red; both scratch assertion commands
returned rc 1 at the named expected-result check.
Cross-model: `agy` 1.1.8 / Google `gemini-3.1-pro-high` requested, CLEAN with 0
P0-P3; 5/5 cited README ranges verified, and its one residual was resolved by
repository search.
E2E: PASS — the exact-head embedded Bash/Python lifecycle ran end to end and
exited 0; populated `n/a` produced `ledger:exact` in premerge and terminal while
blank, missing, malformed, duplicate, and wrong-phase cases retained their
expected failures.

### Verdict

**PASS.** AC-1 through AC-3 are independently reproduced at exact head, both
policy guards are claim-breaking, the cross-vendor review is clean with verified
citations, and the change remains within the approved one-file contract seam.
