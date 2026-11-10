## Stage Report: implementation

- DONE: Phase 2 of the Cycle 1 repair, FO fix authorization for finding F1: apply the repair your phase-1 report proposes (compare reused ids one by one within each amendment, keep the unmarked comparison and the grouped output) in kc-dev-flow-2/scripts/laws_check.py only
  Candidate `d7502656c765e36ce3d24be8602862ccc2551254` changes the reused-id delta in L4; `boundaries.json` proves the repair touches the runner and tests only, retaining the unmarked comparison, first-parent walker, parser and grouped diagnostics.
- DONE: Add the three regressions (partial repair adds no event, growth reports only the added ids, mixed removal and addition) to kc-dev-flow-2/scripts/test_laws_check.py; show each failing with the fix reverted (python3 -B, caches cleared)
  `reverted-fix.json` and `reverted-fix-{0,1,2}.log`: each exact new test fails an assertion, without errors, with only the temporary runner reverted to `72216e2e`; all three pass in the candidate's 79-test laws suite. Each fixture requires L3 to remain clean, so an unrelated append-only violation cannot supply the failure.
- DONE: Re-run at the new candidate: all package test files, the existing mutation controls, and the corpus replay with all seven named events unchanged
  `tests.json`/`tests-summary.json`: all 27 test-file commands exit 0, 1277 unittest cases run with 11 skips plus model-free CLI assertions; local Spacedock CLI 0.27.2/plugin root 0.27.3, not hosted CI. `mutations.json` has nine rejected regressions; `corpus-comparison.json` proves all seven event commits, headlines and diagnostics unchanged at the same three pinned ranges.
- DONE: One local commit on the existing branch, no push and no PR write; update the PR text file /tmp/impl-amendment-checked-when-written-pr.md if its claims change; FO pushes and runs RoboRev
  `commit-receipt.log` records the single repair commit `d7502656c765e36ce3d24be8602862ccc2551254` on `spacedock-ensign/amendment-checked-when-written`, base `6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1`; `pr-draft.md` matches the updated local PR text file. No product push or PR write was performed.
- DONE: Append one complete `## Stage Report: implementation` naming the new candidate SHA, every item followed by its own indented evidence line, evidence kept in the task folder in the state checkout
  Evidence is under `amendment-checked-when-written/implementation/cycle-1-phase-2/`; `artifact.json`, `manifest.json`, `README.md` and this report bind the candidate, source digests, declared local inputs and rerunnable commands; prior task bytes are preserved by append.
- DONE: AC-1 — the original introducing event retains both diagnostics and the base has no L4.
  Fresh `candidate-bite.log` reports one L4 event at `a113aa3e9a3d`, reused AC-1/AC-2/AC-4 and one unmarked diagnostic; the unchanged base's absence is retained in `implementation/amendment-2/base-bite.log`. Reuse/marker mutations each remove their own bite line and fail their named fixture.
- DONE: AC-2 — record-only, marked and waived moves remain green; reused ids and unmarked replacements remain violations.
  `test_laws_check.log` runs the temporary-repository controls; `mutation-payload-0.log` fails when the payload gate is removed, while reuse and marker mutations fail their respective controls.
- DONE: AC-3 — each reused id is judged when introduced, and partial repairs add no event.
  The three new named tests reject whole-tuple comparison in `reverted-fix-{0,1,2}.log`: partial repair must exit 0; growth and mixed changes must name AC-3 without surviving AC-1/AC-2. `mutation-parent-0.log` rejects discarding the first-parent comparison; the candidate laws suite passes.
- DONE: AC-5 — registry, documentation word budget and FO reading boundaries remain satisfied.
  `boundaries.json` records four approved files across the task branch, two in this repair, and laws.md 1345 to 1587 words (+242 <=250); `mutation-heading-0.log` rejects a missing registry heading. Workflow, skills, dispatch records, CI template and versions remain outside the diff.
- DONE: AC-6 — the shared replacement-marker predicate and design-check behavior remain unchanged by this repair.
  `boundaries.json` proves design_surfaces.py and its tests byte-identical to `72216e2e`; `test_design_surfaces.log` runs 217 cases (four skipped). Both suites reject the disabled shared marker (`mutation-marker-{0,1}.log`).
- SKIPPED: AC-7 — containing release, Captain-approved dev2 pin and observed hosted state-push run.
  Approved D2 still defers release/adoption/hosted proof and its hosted old-pin falsifier; no pin was changed, and this task is not closable until that evidence exists.
- DONE: AC-8 — seven historical events, valid sibling entries and first-judgeable heading repairs remain covered.
  `corpus-reconciliation.json` proves 3/3/1 events with no extras in the pinned ranges, including dev2 `bf8c73be99c4` and relay `06cadae7681f`; the structural-skip mutations fail their named fixtures. All three full CLI runs exit 2 for existing L3 ambiguity; no overall-history green claim is made.
- DONE: Required repository checks and CI-cost disposition.
  `checks.json`: repository skill lint, package ADR lint since the pinned base, number guards, task-design, role triggers and doc-impact all exit 0; comment ratio is 0/246 (0%, maximum 5%). CI cost per PR/state push was not measured; no job or trigger changed. No ADR was added or changed; `artifact.json` binds the accepted ADR 0017 read at the candidate.
- DONE: Affected document docs/adr/0041-seed-admission-enforces-required-fields.md — unaffected.
  `doc-verdicts.json`: seed admission is unchanged; this repair changes the L4 event delta only.
- DONE: Affected document docs/adr/0057-rewritten-criteria-are-compared-with-the-captains-words.md — unaffected.
  `doc-verdicts.json`: criterion-word and dispatch comparisons are unchanged, and design_surfaces.py is byte-identical to the preceding candidate.
- DONE: Affected document kc-dev-flow-2/references/sd/laws.md — updated in the preceding implementation, retained here.
  `doc-verdicts.json`: the existing L4 Event section describes the repaired behavior; no additional words were added in phase 2, retaining +242 within the bound.
- DONE: Affected document learning.md — unaffected.
  `doc-verdicts.json`: retained historical practices remain applicable and are followed; this repair adds no new practice or ruling.
- DONE: Resolve evidence-driver/environment failures without changing the candidate or repeating green tests.
  `disk-full-attempt/` preserves the interrupted ENOSPC run; the completed 27 test-file receipts all exit 0. `all-tests.log` retains the post-run bytecode assertion; `finalize-tests.log` exits 0 after matching the receipts to the unchanged candidate/test digests and removing seven generated caches. Reverted-fix/mutation probes separately proved absent bytecode.
- SKIPPED: Eleven local fixture cases, real worker/model execution, product publication, RoboRev and hosted CI.
  `tests-summary.json` and individual logs record the 11 skips; the model-free CLI harness names its limits. FO owns product push, PR delivery/review and fresh validation; no delegated check is reported as run or clean.

### Summary

This report supersedes the earlier implementation reports: the authorized F1 repair is committed locally at `d7502656c765e36ce3d24be8602862ccc2551254`, with all 27 test-file commands green, three reverted-fix failures, nine mutation rejections and seven unchanged corpus events. The evidence distinguishes resolved ENOSPC/reporting-cache failures and existing L3 history ambiguity from the repaired behavior; FO publication, RoboRev, independent revalidation and D2 hosted activation remain outstanding.
