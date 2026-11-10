## Stage Report: implementation

- DONE: Phase 2 of the Cycle 2 repair, FO fix authorization for finding F3: apply the change your phase-1 report proposes (the live-declaration filtering inside the L4-only move_defects, so a tilde-fenced example cannot supply the marker) in kc-dev-flow-2/scripts/design_surfaces.py only; the shared unfenced, unmarked, amendment parser and the public check and seed functions stay byte-unchanged
  Candidate `864536d1180334fa8a10c1ec7122f2ddf0feea14` matches the concrete phase-1 proposal (`boundaries.json`); `function-boundaries.json` verifies module bytes outside `move_defects` and all 55 other functions identical to `d7502656`. Only the L4-only live input receives the fence filter.
- DONE: Promote the F3 regression and its controls into kc-dev-flow-2/scripts/test_laws_check.py; show the F3 test failing with the fix reverted (python3 -B, caches cleared)
  Five promoted methods cover the tilde false marker, backtick control, real marker, waiver and record-only shapes; `red-before-fix.log` has one F3 failure/four passes, no errors. `reverted-f3.json`/`reverted-f3-test.log` show that exact F3 assertion failing with only the temporary helper reverted, bytecode absent; all 19 L4 methods and the complete 84-case laws suite pass at the candidate (one optional suite skip).
- DONE: Re-run at the new candidate: all package test files, the existing mutation controls, the check and seed comparison, and the corpus replay with all seven named events unchanged; F2 is not part of this repair
  `tests-summary.json`: all 27 commands exit 0, 1282 unittest cases/11 skips plus model-free CLI assertions. Nine existing mutations reject regressions; three F1 reverted-fix probes fail as expected. `check-comparison-summary.json` has 1032 identical base/candidate check/seed verdicts; `corpus-comparison.json` preserves all seven event headlines/diagnostics, and `current-tail.json` adds no event at the three observed newer local tips.
- DONE: One local commit on the existing branch, no push and no PR write; update the PR text file /tmp/impl-amendment-checked-when-written-pr.md if its claims change; FO pushes and runs RoboRev
  `commit-receipt.log` records one repair commit `864536d1180334fa8a10c1ec7122f2ddf0feea14` after `d7502656`, on `spacedock-ensign/amendment-checked-when-written`, pinned base `6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1`; the tree is clean. `pr-draft.md` matches the updated local text file; no product push or PR write was performed.
- DONE: Append one complete `## Stage Report: implementation` naming the new candidate SHA, every item followed by its own indented evidence line, evidence kept in the task folder in the state checkout
  Evidence is under `amendment-checked-when-written/implementation/cycle-2-phase-2/`; `artifact.json`, `manifest.json` and `README.md` bind candidate/source digests, full logs, declared local inputs and reproduction commands. The report appends without rewriting prior task bytes, frontmatter, findings or reports.
- DONE: AC-1 — the original event retains both diagnostics and each predicate falsifier detects its removal.
  Fresh `candidate-bite.log`/`bite-exit.json` show one L4 event at `a113aa3e9a3d`, reused AC-1/AC-2/AC-4 and unmarked replacement; `mutation-{reuse,marker}-bite.log` each loses its own diagnostic and the named test fails. The unchanged base's no-L4 receipt remains in `implementation/amendment-2/base-bite.log`.
- DONE: AC-2 — examples cannot replace a real marked declaration in L4, while legitimate marker, waiver and record-only shapes remain valid.
  The five new methods exercise actual CLI pushes with clean L3; restoring the old filter fails `test_tilde_example_does_not_supply_live_marker` (`reverted-f3-test.log`). Removing the payload gate fails the record-only control (`mutation-payload-0.log`); the candidate's full laws suite passes.
- DONE: AC-3 — existing per-id event identity and first-parent behavior remain intact within the accepted scope.
  `laws_check.py` is byte-identical to `d7502656` (`boundaries.json`); all three partial/growth/mixed methods pass and fail with their old runner restored (`reverted-f1.json`), and removing parent comparison fails `mutation-parent-0.log`. F2's unreadable-batch diagnostic preservation is unrepaired, as FO directed.
- DONE: AC-5 — registry, documentation budget and FO reading boundaries remain satisfied.
  `boundaries.json`: only two files in this repair and four approved files in the task branch; laws.md stays 1345 to 1587 words (+242 <=250). The registry test and lint pass; removing its L4 heading fails `mutation-heading-0.log`. Workflow, skills, dispatch records, CI template and versions are outside the diff.
- DONE: AC-6 — the shared replacement-marker predicate and existing design-check compatibility remain preserved.
  `function-boundaries.json` proves shared/public functions byte-unchanged; `check-comparison.json` preserves 1032 check/seed verdicts, including inherited gate behavior. Unchanged design tests run 217 cases/four skips; both suites reject the disabled shared marker (`mutation-marker-{0,1}.log`).
- DONE: AC-8 — seven historical events, per-entry structural skips and heading-repair semantics remain covered.
  `corpus-reconciliation.json` proves 3/3/1 events without extras in fixed ranges, including dev2 `bf8c73be99c4` and relay `06cadae7681f`; every line equals `d7502656`. Restoring either whole-file skip fails its structural fixture. All three full CLI runs still exit 2 for existing L3 ambiguity; no overall-history green is claimed.
- SKIPPED: AC-7 — containing release, Captain-approved dev2 pin and observed hosted state-push run, including the hosted old-pin falsifier.
  Approved D2 still defers these obligations; no pin or release changed, and no hosted evidence is claimed. The task cannot close before the required hosted L4 headline.
- DONE: Required repository checks, explicit ADR checks and CI-cost disposition.
  `checks.json` and `adr-explicit.json`: skill lint, package ADR lint since the pinned base with explicit 0016/0017/0041/0057 records, number guards, task design, role triggers and doc-impact exit 0; comment ratio is 0/295 (0%, maximum 5%). CI cost per PR/state push was not measured; no job or trigger changed.
- DONE: Re-establish the Pilot profile, role trigger and step-back answers for the authorized repair.
  `step-back-answers.json` retains the same missing-marker outcome, direct testability and the protection lost if the rule were deleted; role triggers exit 0. `adr-bindings.json` binds accepted ADR 0016/0017 at this candidate; no decision record is added or changed.
- DONE: Affected document docs/adr/0041-seed-admission-enforces-required-fields.md — unaffected.
  `doc-verdicts.json`: seed fields and public seed paths are byte-unchanged, and check/seed corpus verdicts match the pinned base.
- DONE: Affected document docs/adr/0057-rewritten-criteria-are-compared-with-the-captains-words.md — unaffected.
  `doc-verdicts.json`: word/dispatch comparisons remain byte-unchanged; the new input filter is local to the L4-only helper.
- DONE: Affected document kc-dev-flow-2/references/sd/laws.md — updated in the preceding implementation, retained here.
  `doc-verdicts.json`: filtering examples from live L4 declarations fulfills the existing rule without adding words; the +242-word total remains within its bound.
- DONE: Affected document learning.md — unaffected.
  `doc-verdicts.json`: retained historical practices still apply; this repair adds no new ruling or operating practice.
- SKIPPED: Repair F2, publish the product, write the PR, run RoboRev/hosted CI, make gate decisions or merge.
  F2 is outside this dispatched repair and the exception path remains byte-unchanged; its disposition stays with FO. Product push, PR publication/review and independent validation remain FO-owned; no delegated check is called run or clean.
- SKIPPED: Eleven environment-dependent fixture cases and real worker/model execution.
  `tests-summary.json`/individual logs record 11 skips; local CLI is Spacedock 0.27.2 with plugin root 0.27.3, while CI pins both to 0.27.2. The model-free CLI harness states its execution limits; no hosted or real-model claim is made.

### Summary

This report supersedes earlier implementation readiness claims: the authorized F3 repair is committed locally at `864536d1180334fa8a10c1ec7122f2ddf0feea14`, with all 27 test-file commands successful, the required reverted-fix/mutation failures, unchanged public check/seed verdicts and seven unchanged historical events. F2 remains unrepaired per FO scope, and existing L3 history ambiguity, FO publication/RoboRev/independent validation and D2 hosted activation remain explicit limits; this report is not a gate approval or task closure.
