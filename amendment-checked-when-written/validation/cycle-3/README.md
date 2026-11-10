# Independent validation, cycle 3

**PASSED within the accepted local validation boundary.** All 27 package test commands exit 0 (1,282 unittest cases, 11 explicitly skipped, plus model-free CLI assertions). The six-step acceptance, nine mutation rejections, repaired F1/F3 boundaries, 1,032 unchanged check/seed verdicts and all seven historical events pass. AC-7 remains open after release/adoption; F2 retains FO's Deferred risk disposition.

Candidate: `864536d1180334fa8a10c1ec7122f2ddf0feea14`; pinned base: `6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1`; PR: https://github.com/iamcxa/kc-claude-plugins/pull/828. Candidate source and all product checks run from a fresh `git archive` export, not from a new or mutated Git worktree. Read-only metadata comes from the explicitly declared product repository in `identity.json`.

## Scope and prior findings

The accepted Pilot outcome is flagging each introducing state commit with reused criterion ids or a missing real replacement marker. This can be tested now by the full CLI and reverted-fix controls. Deleting the new law loses reporting at the push; deleting the marker predicate loses the original bite's diagnostic and ADR 0016's protection. These are the three step-back answers, also recorded in `step-back-answers.json`.

F3 (a tilde-fenced example supplied a false live marker) is repaired: `review-example-tilde.log` and the backtick control both reject the real unmarked move. `reverted-f3.json` proves the promoted assertion fails when only the previous helper is restored. F1 (a partial repair repeated an old reused id) stays closed: partial/growth/mixed tests pass, while all three fail with their previous runner restored (`reverted-f1.json`). Legitimate marked, waived and record-only controls pass.

F2 (a constructed unreadable task discards another diagnostic) stays **Deferred risk**, as FO decided in Feedback Cycles 2 following the chief engineer's report. The exception path is byte-unchanged, and this validation establishes no new observed trigger that would make it Material. It is neither repaired nor re-reported. The original artificial unreadable-batch probe was excluded from this cycle's acceptance script on that disposition; it remains in the previous evidence unchanged.

## Captain acceptance: six steps, no screen surface

Prerequisites: macOS/POSIX shell, Bash, Git, tar, Python 3; the product repository and dev2 history paths named in `acceptance.sh`; both pinned product commits and bite commits; and installed package `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.37.0`. These are declared local dependencies, not a portable hosted proof. Equivalent installations require explicit path substitution.

Run unchanged:

```sh
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/amendment-checked-when-written/validation/cycle-3/acceptance.sh
```

The six steps export the exact candidate/base, replay the bite (both diagnostics, absent at base), run 20 L4/registry tests, run ADR lint (65 records, exit 0), exercise partial repair (exit 0, no new event), and reject both types of fenced false markers (`Tilde-fenced example ignored: True`, exit 0). `acceptance-durable.log` and `acceptance-exit.json` retain the observed run from this exact durable path. The script takes less than five minutes locally; it has no UI because this change has no screen surface.

The script does not cover all package tests, full corpus history, hosted activation, real model execution, release, review completion, merge or adoption. The independent evidence below covers the relevant local obligations separately.

## Reproduction and evidence map

Copy this directory to a new scratch directory before rerunning drivers, to preserve original receipts. Export the candidate/base into that directory's `candidate/` and `base/` from `identity.json` using `git -C <product repository> archive <revision> | tar -x -C <new export directory>`. Python drivers explicitly use the original product repository only for read-only revision/source lookup (`driver-adaptations.json`). Do not export Git environment variables globally: fixture repositories must keep their own metadata. `checks.py` supplies metadata only to the checks that need it.

```sh
python3 -B run-tests.py <candidate export>
python3 -B reverted-f3.py <candidate export>
python3 -B reverted-f1.py <candidate export>
python3 -B mutations.py <candidate export>
python3 -B compare-checks.py <candidate export>
python3 -B run-corpus.py <candidate export> corpus-inputs.json dev2
python3 -B run-corpus.py <candidate export> corpus-inputs.json qnow
python3 -B run-corpus.py <candidate export> corpus-inputs.json relay
python3 -B verify-corpus.py
python3 -B compare-corpus.py /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/amendment-checked-when-written/validation/cycle-2
python3 -B run-tail.py <candidate export>
python3 -B checks.py <candidate export>
```

`tests.json`/`tests-summary.json` contain every package test-file command, source digest, result and fixture skips. The runner checks its command list against the candidate CI workflow. `mutations.json` requires nine injected regressions to fail by assertion, without import errors or stale bytecode. The changed test file exercises real temporary Git repositories and the CLI; expected failures are control evidence, not failed product tests.

`artifact.json` verifies the four-file branch footprint and that only `move_defects` changes in runtime code since the previous candidate; 55 other functions and all module bytes outside it remain identical. `check-comparison.json` has 1,032 identical check/seed verdicts at the three fixed tips. The shared marker predicate is still used by both check paths, and disabling it fails a test in each suite.

`corpus-inputs.json` and `corpus-readme-inputs.json` bind the historical ranges and mutable README input bytes. `corpus-reconciliation.json` requires precisely seven L4 events (3 dev2, 3 qnow, 1 relay). `corpus-comparison.json` compares every L4 headline/diagnostic to validation-2. `current-tail.json` additionally binds the newer local tips: no new L4 event there. No fetch of those histories or remote-freshness claim is made. Full historical CLI commands exit 2 for existing L3 ambiguity, so this is not an overall-history green claim. The two previously omitted events are separately exercised in `recovered-dev2.log` (exit 2) and `recovered-relay.log` (exit 1).

`checks.json` includes lint, ADR lint, explicit ADR 0016/0017/0041/0057 requirements, number guards, comment ratio, task design, role triggers, dispatch records and document impact. `doc-verdicts.json` independently dispositions every affected document. The named package scripts in the dispatch and skill installs are byte-identical (`installed-package.json`). Number guards' attempted state fetch is sandbox-blocked, so reservations are local-ref-only; this candidate changes or reserves no number.

One initial metadata-only assertion located an inline quoted heading instead of the actual Acceptance criteria section. Requiring newline-delimited top-level headings fixed that validation script; candidate bytes were unchanged. An optional process inventory was sandbox-denied; background handles, completion exits and logs are used instead. Neither is a product failure or omitted test.

## Goal sufficiency, necessity and limits

Local goal sufficiency is supported by the original bite, all seven promised events, first-parent event identity and the repaired false-marker boundary. Each retained file serves that outcome: shared predicate/input filtering; existing event runner/registry; meaningful regressions; and rule documentation. `laws.md` grows 242 words (1345 to 1587), within 250. Workflow text, dispatch implementation, skills, CI template, jobs/triggers, versions and adoption pins remain unchanged.

Reporting is after push and cannot stop commit/dispatch/gate/merge. Record-only entries and in-place rewrites without a moved payload are outside L4; it does not authenticate missing rulings or quote fidelity. A forgotten waiver retains the existing L3 metadata-edit constraint. A missed failed-run notice remains unreported in later pushes by ADR 0017. The model-free CLI harness is not a real worker run; local CLI 0.27.2/plugin 0.27.3 differ from CI's matched 0.27.2 pins, and optional fixture skips remain explicit.

AC-7 and its hosted old-pin falsifier remain deferred by approved D2: containing release, Captain-approved adoption pin, then an observed hosted state push printing L4. `activation-limit.json` confirms the local old 0.26.0 pin lacks L4; that local negative control is not hosted proof. CI cost per PR/state push was not measured; no job, trigger or pin is changed.

GitHub snapshots in `pr-*.json` confirm the exact candidate, open Draft status, two historical unresolved threads (F3 outdated), and a latest exact-head review receipt reporting no major issues. The summary still carries unresolved findings; no review-resolution claim is made. The PR body and its RoboRev line still name `72216e2e`; FO owns updating these, the settled F2 disposition at the gate, delivery approval and later AC-7 adoption. This validation does not grant those authorities.
