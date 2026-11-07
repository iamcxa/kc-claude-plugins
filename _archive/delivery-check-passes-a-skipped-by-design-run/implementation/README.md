# Implementation evidence

Candidate: `1ca2625de0706e5494f73e010a394f8e5194b2a1`.
Base: `ba055b8a7a55a787ac989c4cef52d07dd75661ad` (fetched origin/main before editing).
Profile: Pilot. Product publication and RoboRev belong to FO.

The only product changes are the two files in `artifact.json`. Test exits, mutation
outcomes, reduced replay output and live read-only gh output are preserved here.
`sha256.json` covers the copied evidence; this README and the enclosing task report
are narrative references rather than inputs to the checks.

## Reproduce the bounded acceptance proof

The following paths are the code worktree, workflow and package declared in the
dispatch/loaded skill; no credentials or secret wrapper are needed. Change the
absolute worktree/package paths when running on a different machine.

```bash
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-delivery-check-passes-a-skipped-by-design-run
WORKFLOW=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2
PACKAGE=/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0
ENTITY="$WORKFLOW/.spacedock-state/delivery-check-passes-a-skipped-by-design-run.md"
TASK_ROOT="${ENTITY%.md}"
EVIDENCE="$TASK_ROOT/implementation"
bash --noprofile --norc "$EVIDENCE/acceptance.sh" "$WT" "$TASK_ROOT" /tmp/skipped-run-acceptance "$PACKAGE"
```

The fresh-shell proof checks the six replay exit/word pairs, the required-check
boundary tests, ten assertion-failing mutants, the two-file allowlist and unchanged
workflow bytes. Mutation copies start without caches, run with `python3 -B`, and
must remain cache-free. `fresh-shell.log` records the completed run. It does not
rerun live GitHub reads or the five complete suites.

## Commands actually run

The variables above name the same inputs used for these commands. All five suites
exited 0; `tests.json` has their case/skip counts. Their original output is in the
corresponding `*-tests.log`. The full package suite was not run.

```bash
cd "$WT"
python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p test_delivery_gate.py
python3 -B kc-dev-flow-2/scripts/test_pr_watch.py
python3 -B kc-dev-flow-2/scripts/test_dispatch_records.py
python3 -B kc-dev-flow-2/scripts/test_validation_security.py
python3 -B kc-dev-flow-2/scripts/test_design_surfaces.py
python3 -B kc-dev-flow-2/scripts/lint-skills.py
python3 -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since ba055b8a7a55a787ac989c4cef52d07dd75661ad
python3 -B "$PACKAGE/scripts/number_guards.py" check --repo "$WT" --workflow-dir "$WORKFLOW" --task "$ENTITY" --base ba055b8a7a55a787ac989c4cef52d07dd75661ad
python3 -B "$PACKAGE/scripts/comment_ratio.py" ba055b8a7a55a787ac989c4cef52d07dd75661ad HEAD --workflow-dir "$WORKFLOW"
python3 -B "$PACKAGE/scripts/doc_impact.py" ba055b8a7a55a787ac989c4cef52d07dd75661ad HEAD --json
python3 -B "$PACKAGE/scripts/design_surfaces.py" check "$ENTITY"
```

All guard/lint commands exited 0. Migration checks explicitly skipped because the
workflow declares no migrations-path. Comment ratio is 0.0%, within the 5% maximum.
`doc-verdicts.json` gives each retained-document disposition and its exact base
commit/SHA-256. No retained document needed an update under the approved scope.

## Live read contract and limits

Read on 2026-11-06 16:23 UTC (2026-11-07 Asia/Taipei); `gh-version.log` records
2.103.0. `live-contract.json` records each exit and links its original stdout and
stderr. A failed required check on qnow #1316 still returned JSON with exit 0; stub
tests additionally exercise JSON returned with exit 1 and 8.

```bash
gh --version
gh pr checks 477 --repo spacedock-dev/subspace-relay --required --json name,bucket
gh pr checks 1338 --repo iamcxa/qnow --required --json name,bucket
gh pr checks 1316 --repo iamcxa/qnow --required --json name,bucket
```

Validation must refresh these live observations. GitHub may omit a required check
it never created; this task does not detect that existing blind spot. A changed
no-required stderr message fails closed. No branch push, PR creation, RoboRev,
hosted CI, ready action, merge or release was performed. CI cost per PR was not
measured; the workflow triggers are unchanged.
