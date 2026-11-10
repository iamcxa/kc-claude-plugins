# Independent validation, cycle 2

Candidate: `d7502656c765e36ce3d24be8602862ccc2551254`; base: `6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1`; PR: https://github.com/iamcxa/kc-claude-plugins/pull/828. Product source was read and run from `git archive` exports, with read-only Git metadata supplied only to checks that need commit identity. No product byte, branch, version, workflow pin, PR body, review thread or delivery state was changed.

The Cycle 1 F1 repair is effective: partial repair adds no event, and growth/mixed changes report only new ids. `reverted-fix.json` proves the three tests fail with only the runner reverted to the previous candidate. The original five-step acceptance remains in `acceptance-f1-only.*` as a passing historical receipt. Current validation nevertheless recommends **REJECTED**: independent full-CLI probes reproduce the two new exact-head GitHub review findings, F2 and F3 in `findings.json`. They are not inferred from the review alone. `review-probes.json` and its six logs distinguish each failing path from a positive control.

## Captain acceptance: six steps, no screen/UI surface

Prerequisites: macOS/POSIX shell, Git, Python 3, tar, the assigned local product repository containing both pinned commits, the dev2 state history containing `b91e7434adde` and `a113aa3e9`, and declared package `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.37.0`. Those machine-specific inputs are named explicitly in `acceptance.sh`; equivalent clones/installations require deliberate path substitution. The script uses a fresh `/tmp` export and never edits the product checkout.

Run the following unchanged, after this evidence folder is committed:

```sh
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/amendment-checked-when-written/validation/cycle-2/acceptance.sh
```

The script is the exact commands, with six labelled steps and expected observations. Step 1 resolves/exports the exact candidate and base. Step 2 expects one original L4 event with both diagnostics, absent at base. Step 3 expects 15 L4/registry tests to pass. Step 4 expects the declared ADR command to check 65 records and exit 0. Step 5 expects partial repair exit 0 with no L4 event. Step 6 expects both `Known move diagnostic retained: True` and `Tilde-fenced example ignored: True`; at this candidate both are **False**, so the script exits **1**. `acceptance.log`/`acceptance-exit.json` retain the exact fresh-Bash run. This is the final script; its failure is a product finding, not an environment failure.

This bounded script does not cover the full history, every package test, hosted activation, real worker/model execution, release, merge or review completion. It does not claim those from green steps. The exported directory is retained as scratch for inspection; it is not a worktree.

## Reproduce the other evidence without overwriting receipts

Copy this evidence folder to a new scratch directory. Export candidate and base into that directory's `candidate/` and `base/` with `git -C <product_repo> archive <sha> | tar -x -C <destination>`. The product repository path and read-only git directory are declared in `identity.json`; the three history checkout paths and ranges are in `corpus-inputs.json`. The test driver declares the local Spacedock CLI and plugin root. These inputs are local dependencies, not portable hosted proof.

From that scratch directory run:

```sh
python3 -B run-tests.py "$PWD/candidate"
python3 -B reverted-fix.py "$PWD/candidate"
python3 -B mutations.py "$PWD/candidate"
python3 -B run-corpus.py
python3 -B verify-corpus.py
python3 -B compare-corpus.py /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/amendment-checked-when-written/implementation/amendment-2
python3 -B run-current-tail.py
python3 -B compare-checks.py "$PWD/candidate"
python3 -B run-checks.py
python3 -B review-probes.py
```

`tests.json`/`tests-summary.json` give every test-file command, source hash, exit and skips. `mutations.json` gives nine expected assertion rejections, not nine product failures. `corpus-reconciliation.json` gives seven events (3 dev2, 3 qnow, 1 relay); full CLI exits 2 on existing L3 history ambiguity, so no whole-history clean claim is made. `corpus-comparison.json` compares exact L4 headlines/diagnostics against the preceding candidate over identical ranges. `current-tail.json` separately checks newer local commits; local tips were not fetched and do not establish remote freshness. `check-comparison.json` retains all 1,032 check/seed results at the three pinned tips; candidate and base verdicts are identical.

`run-checks.py` should use read-only `GIT_DIR`/`GIT_WORK_TREE` for number guards as well as ADR/comment/doc checks. The initial number-guards attempt omitted that metadata and exited 2 (`number-guards-initial.log`); the corrected unchanged command exits 0 (`number-guards.log`). Its sandbox-blocked internal state fetch limits reservation freshness to local refs. This task reserves/changes no ADR or migration number, so that limitation does not weaken a changed-number claim. An initial `spacedock status --read` lacked `--workflow-dir`; the explicit workflow invocation succeeded. These are validation setup failures, not product defects.

## Scope and sufficiency

The four-file footprint is minimal for the accepted goal: a shared predicate removes marker duplication; L4 uses the existing walker and correspondence; tests reject omission of each rule; the registry documentation adds 242 words within the 250-word allowance. The F1 repair touches only event comparison and its three tests. The goal is not yet sufficient because F2 loses a known introducing diagnostic and F3 accepts an example as the required live replacement.

The implementation report's limits remain valid: post-push reporting cannot prevent commit/dispatch/gate/merge, record-only entries and in-place changes without a move are outside L4, missing rulings and quote fidelity are not authenticated, and the once-per-push design requires inspecting each failed run. A forgotten waiver still has the pre-existing L3 metadata-edit constraint. The local test environment uses Spacedock CLI 0.27.2 and plugin 0.27.3, while hosted CI pins 0.27.2; optional fixture skips and model-free CLI assertions are not real-worker proof. Prior ENOSPC/cache-cleanup receipts describe implementation's environment, not this validation's outcome.

`activation-limit.json`, `dev2-laws.yml` and `old-pin-bite.log` confirm the current local dev2 pin lacks L4 and the local negative control prints no L4. AC-7 and its hosted old-pin falsifier remain deferred by approved D2: containing release, Captain approval of the pin, then an observed hosted state push. CI cost per PR/state push was not measured; no job, trigger or pin changed.

GitHub snapshots are saved in `pr-*.json`. Exact-head review completed with two unresolved findings, independently reproduced here; the PR body still cites the previous candidate's validation/RoboRev. FO owns review disposition, body refresh, product publication and the delivery gate. This report grants none of them.
