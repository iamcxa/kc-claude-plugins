# Independent validation of PR 828

Candidate: `72216e2e947e962737a17c6e61ef3800f9d639c4`. Base: `6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1`.

Verdict: **REJECTED**. The accepted first-parent/new-event boundary fails when a worker repairs only one of several already reported reused criterion ids. `findings.json` records F1 as Material with the four required fields. The product checkout and candidate bytes were not changed.

## Captain acceptance

This is a command-line workflow change with no changed screen. Prerequisites are Python 3, Bash, Git, tar, the existing product and dev2 state clones, and the explicitly declared kc-dev-flow-2 0.37.0 package. The script names all local paths; it writes temporary exports/repositories only. It does not change the product, state history, Git configuration, PR or adoption pin.

Run this exact command in a fresh shell after the state evidence commit is available:

```sh
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/amendment-checked-when-written/validation/cycle-1/acceptance.sh
```

The five steps and their commands are in `acceptance.sh`:

1. Export the pinned candidate and baseline. Expect `STEP 1 PASS`.
2. Replay the historical defect. Expect one L4 event, reuse and unmarked diagnostics, and no L4 in the baseline. Both full CLI invocations exit 1 because the historical record also has L2 debt.
3. Run L4 behavior and registry tests. Expect 12 tests and `OK`, followed by `STEP 3 PASS`.
4. Run the declared package's ADR linter with the exact base. Expect `65 ADR file(s) checked, 0 legacy` and `STEP 4 PASS`; exit 0.
5. Repair one of two already reported reused ids without introducing a new id violation. AC-3 requires no L4 event and exit 0. At this candidate the observed result is one new L4 event for unchanged AC-2 and exit 1, followed by `FAIL AC-3`.

I ran this script, byte-for-byte, using `bash --noprofile --norc`; `acceptance.log` and `acceptance-exit.json` contain the observed output and exit 1. This checks a small local acceptance path, not hosted activation, release, review completion or merge readiness. The final failure is a product finding, not a harness error.

## Evidence guide

- `identity.json`, `artifact.json`: worktree identity, exact product hashes, four-file scope, unchanged design tests and documentation word count.
- `laws-tests.log`, `design-tests.log`, `test-summary.json`: original candidate suites, including explicit optional skips.
- `mutations.py`, `mutations.json`, `mutation-*.log`: all nine implementation mutation controls independently rerun in cache-free temporary copies; each exits 1 with a test assertion failure rather than an import/error failure.
- `prior-regression.log`: the three new regression methods run with the prior product sources; all fail as expected, with one method containing two failing subcases.
- `candidate-bite.log`, `base-bite.log`, `bite-exits.json`: original historical event and without-change control.
- `recovered-*.log`, `recovered-exits.json`: the two events missed by the prior candidate now have L4 diagnoses. dev2 still exits 2 because of pre-existing L3 ambiguity; relay now exits 1 for L4 while L2/L3 do not diagnose a violation.
- `corpus-inputs.json`, `corpus-*.log`, `corpus-*-exit.json`, `corpus-reconciliation.json`: full three-adopter history runs against freshly pinned local tips. All histories are read-only. Pins are local snapshots, not claims of current remote state.
- `check-comparison.json`: base/candidate check and seed comparison over every task at those tips; the count differs from implementation because the tips advanced.
- `partial-repair.log`, `partial-repair.json`, `probe-partial-repair.py`: independent F1 reproduction, including a full-repair control that exits 0.
- `checks.json` and matching logs: skill lint, ADR lint, comment ratio, number guards, task design, dispatch records and role triggers. The initial standalone role-trigger check passed. A redundant invocation inherited the product export's GIT_DIR and failed to identify the state checkout; the corrected clean-environment invocation passes in `role-triggers-state.log`. This was a validation invocation error, not a product issue. Number guards pass but report that their state fetch was unavailable; no migration or ADR number is reserved or changed here.
- `doc-impact.log`, `doc-verdicts.json`: every listed document disposition checked; `laws.md`'s no-repeat promise is subject to F1.
- `criterion-move.json`, `amendment-added-words.json`: exact old AC-4 moved to Amendment 1, fresh AC-8 naming both amendments, and no inserted-word findings.
- `activation-limit.json`, `old-pin-bite.log`, `dev2-laws.yml`: local old-pin negative control; no hosted activation or hosted old-pin run was observed. AC-7 remains open under D2.
- `pr-info.json`, `pr-comments.json`: read-only remote snapshot, exact candidate and Draft/Open status. The comment list was empty at read time. The PR body's RoboRev statement is an FO report, not independent local-daemon verification by this validator.

## Limits and necessity

The approved output is a post-push signal, not a pre-commit refusal or a blocking merge hook. Record-only amendments, in-place rewrites without moved text, missing amendments and quote fidelity remain outside L4. Broken entries can be skipped while valid siblings are judged; heading repair reports first-judgeable defects but does not certify L3 compliance. Full-history nonzero results include existing L1/L2 debt and L3 cannot-judge conditions; only the separately reconciled L4 event results support the seven-event claim.

The four changed files have direct accepted purposes: shared move detection, integration with the existing push-event runner, falsifiable behavior tests, and the law registry documentation. No new job, trigger, adopter pin, version, skill or workflow instruction was added. Documentation grows by 242 words, below the 250-word bound. CI cost per PR and per state push was not measured. Goal sufficiency fails AC-3 until F1 is resolved; the remaining code footprint is within the approved Pilot scope. Release, adoption and delivery remain with FO/Captain.
