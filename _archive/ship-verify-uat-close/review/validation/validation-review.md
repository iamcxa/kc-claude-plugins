# Validation review — ship-verify-uat-close (7e)

## Checklist (validation dispatch)
1. DONE — Local verification: AC-1/AC-2/AC-3 reproduced live at head 3053f925 (fixtures under kc-ship-flow/scripts/fixtures/{uat-doc-v2,close-v2}/, uat-doc.test.py and close.test.py both "all checks passed").
2. DONE — Draft PR opened via pr-merge mod: https://github.com/iamcxa/kc-claude-plugins/pull/411 (base main, head spacedock-ensign/ship-verify-uat-close, Candidate 3053f92539c9ee7d92e1b2164c248ce7286574c3), recorded as pr: 411.
3. DONE (named blocker, not attempted) — AC-4 (the real sprint run) remains blocked: kc-ship-flow/scripts/fenced-dispatch.sh has no _ship_fence/debrief/workspace_id/session_id/merged_sha fields yet; the batch-record schema this task invented needs reconciling with the sibling dispatch/watch task's real fence-file shape before AC-4 can run.

Count: 3 done, 0 skipped, 0 failed.

## Acceptance criteria cross-check
- AC-1: MET — uat-doc.py fixture reproduction (ready exits 0, missing-gate exits 1 naming DEV-203).
- AC-2: MET — close.py --dry-run fixture reproduction (one conductor message line, unmerged task omitted; without --dry-run exits 3 "not all tasks merged").
- AC-3: MET — close.py --validate fixture reproduction (valid receipt exits 0; copy missing DEV-301's debrief exits 1 naming DEV-301).
- AC-4: NOT MET, scoped out per this entity's own Work profile receipt ("testing: AC-1 to AC-3 on fixtures; AC-4 on the real sprint") — depends on the sibling ship-cloud-dispatch-and-watch task landing dispatch.sh/watch.sh's real fence-file shape first. That sibling's own validation report independently marks its AC-3 (the real dispatch producing these gates) SKIPPED for the same reason, so this is a genuine cross-entity sequencing dependency, not a dropped requirement.

## Native stack exception
23 files changed (>20 numeric trigger), no independent/dependent layers: 18 fixture files inseparable from the 2 rewritten scripts + 2 tests they prove, plus 1 contract-test.py wiring line. Recorded in the PR body per the Local Profile's delivery-topology rule.

## Residuals carried into the gate
- Design doc `docs/superpowers/specs/2026-09-10-ship-flow-cloud-wrapper-design.md` exists only on `origin/docs/ship-flow-cloud-wrapper-spec`, not `main`.
- `_ship_fence/<sprint>.json` batch-record schema is this task's own invention pending reconciliation with the sibling dispatch/watch task.
- `close.py` reads but does not itself write `debrief.status: "failed"` — no script in this sprint writes that field yet.
- Pre-existing `fenced-dispatch.test.sh` failure (3/4 cases) reproduces identically on unmodified main; unrelated to this change.
