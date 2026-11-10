## Stage Report: validation

- DONE: Independent verdict on PR #828 head 72216e2e against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  REJECTED at `72216e2e947e962737a17c6e61ef3800f9d639c4`, base `6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1`: F1 violates AC-3. Evidence below is under `amendment-checked-when-written/validation/cycle-1/`; AC-7's hosted proof/falsifier remain explicitly deferred by D2, with a local old-pin negative control only.
- DONE: Captain amendments Amendment 1 and Amendment 2 are applied: judge the replacement criterion (seven events, per-entry skip) and the engineering review's points in amendment-checked-when-written/review/engineering-reviewer-1.md, including what a later heading-only repair push reports
  `criterion-move.json` verifies the exact old AC-4 move and fresh AC-8 naming both amendments; `recovered-exits.json` records dev2 L4 event plus L3 cannot-judge (exit 2), relay L4 event with L2/L3 clean (exit 1). `prior-regression.log`, `laws-tests.log` and structural-skip mutations prove heading-only repair reports previously unjudged defects without repeating an already reported sibling.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.37.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  `README.md` gives the exact fresh-shell invocation; `acceptance.sh` has five steps. `acceptance.log` and `acceptance-exit.json`: steps 1–4 pass, step 5 exposes F1, overall exit 1; step 4 runs the exact declared package ADR command against the pinned base and exits 0 (65 records).
- DONE: AC-1 — the original event reports both defects, absent at base, and both predicate falsifiers are caught.
  `candidate-bite.log` has one L4 event and two diagnostics; `base-bite.log` has no L4. Disabling reuse or the shared marker removes its corresponding diagnostic and fails its test: `mutation-reuse-bite.log`, `mutation-marker-bite.log`, `mutations.json`.
- DONE: AC-2 — record-only, marked and waived moves stay green; actual reuse/unmarked moves fail.
  `laws-tests.log` passes the declared temporary-repository fixtures; removing the payload gate fails `test_record_only_marked_move_and_waived_move_are_green` in `mutation-payload-0.log`.
- FAILED: AC-3 — a defect is reported once at the commit that adds it, and repair adds no new event.
  The original fixture and first-parent mutation pass, but `partial-repair.log` shows an already reported AC-2 repeated when only AC-1 is fixed; L3 reports no violation, the partial-repair push exits 1, and full repair exits 0. `acceptance.log` step 5 independently reproduces F1.
- DONE: AC-5 — registry, documentation word bound and FO reading boundaries.
  `artifact.json`: only four approved files, laws.md 1345→1587 words (+242 ≤250), original design tests unchanged; workflow, skills, dispatch records, CI template and versions unchanged. `lint.log` exits 0; removing L4's heading fails `mutation-heading-0.log`.
- DONE: AC-6 — one marker predicate serves both checks, preserving design check/seed behavior.
  `design-tests.log`: 217 run, 213 passed, four optional fixtures skipped. `check-comparison.json`: 1036 task/mode verdicts at fresh local tips identical to base; disabling the shared marker fails each suite (`mutation-marker-0.log`, `mutation-marker-1.log`).
- SKIPPED: AC-7 — containing release, Captain-approved dev2 pin and observed hosted state-push run, including its hosted old-pin falsifier.
  D2 defers this obligation; `activation-limit.json` and `dev2-laws.yml` verify the unchanged old pin and a local replay with no L4. No release, adoption edit or hosted proof is claimed; the task cannot close before AC-7.
- DONE: AC-8 — the seven-event corpus, per-entry skips and first-judgeable heading repair.
  `corpus-reconciliation.json` verifies dev2/qnow/relay 3/3/1 events at the seven specified commits, with no extra event at the fresh local tips in `corpus-inputs.json`; all three full CLI runs exit 2 on existing L3 ambiguity, not a clean overall-history claim. `mutations.json` records all nine rejected regressions, including both restored whole-file structural skips; `prior-regression.log` shows all three new regression methods fail on prior sources.
- DONE: Required repository checks, implementation dispatch records and added-comment review.
  `checks.json`: repository skill lint, package ADR lint, comment ratio (0/205; 0%, maximum 5%), number guards, task-design and six dispatch records pass. Initial/clean-env role checks pass; one redundant export-GIT_DIR invocation error is disclosed in `README.md`. Number guard's unavailable state fetch is scoped to local reservations; this candidate reserves/changes no number.
- DONE: doc-impact — docs/adr/0041-seed-admission-enforces-required-fields.md is unaffected.
  `doc-verdicts.json` and `check-comparison.json`: seed admission is unchanged and all compared verdicts match.
- DONE: doc-impact — docs/adr/0057-rewritten-criteria-are-compared-with-the-captains-words.md is unaffected.
  `added_words` is unchanged; `amendment-added-words.json` is empty and the marked replacement passes the task check.
- DONE: doc-impact — kc-dev-flow-2/references/sd/laws.md is updated.
  `doc-verdicts.json`: per-entry skip/heading-repair statements match observed behavior; the no-repeat claim is not satisfied for partial repair (F1).
- DONE: doc-impact — learning.md is unaffected.
  `doc-verdicts.json`: historical practices remain intact; fresh exports, later-history checks and check/seed comparisons were exercised without rewriting past evidence.
- DONE: Assess goal sufficiency, minimal necessity and implementation limits at the same candidate.
  `README.md`: the four-file footprint directly serves detection, event wiring, falsifiers and registry docs; goal sufficiency fails F1. `test-summary.json` preserves 76 laws tests (75 passed, one optional skip); historical whole-CLI exit 2 is not green. Post-push-only, record-only/in-place/quote limits remain; CI cost per PR/state push is unmeasured and no job/trigger/pin changed.
- F1 Material: Partial repair re-reports old reused ids; `kc-dev-flow-2/scripts/laws_check.py:383` compares the entire reused-id tuple, so a smaller set is treated as a new defect.
  User/workflow: an adopter worker fixes a previously reported multi-id move across commits; harm: a no-new-defect push fails and attributes old AC-2 to the repair commit; boundary: `value-ac[AC-3]` once at introduction, `contract[docs/adr/0017-history-laws-judge-only-the-events-a-push-adds.md#decision]` new events only; trigger: `partial-repair.log`, `acceptance.log` step 5. Full fields and proposed repair boundary: `findings.json`.

### Summary

Independent validation recommends REJECTED for PR #828 at `72216e2e947e962737a17c6e61ef3800f9d639c4`: both Captain amendments are applied, but the supported partial-repair path violates AC-3. Product bytes remain unchanged; return F1 through FO disposition/implementation feedback, while AC-7 remains open for the approved release/adoption sequence. This is an evidence verdict, not gate, merge, review-completion or delivery authority.
