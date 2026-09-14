---
title: "close.py records merged_sha from the merged PR and matches each task's debrief by its worker, not the FO's"
status: validation
source: "Captain 2026-09-14 「派」 (ship round 3, harden); findings recorded on spacedock-state/ship questions logs"
product: kc-ship-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r3
sprint-readiness: ready
started: 2026-09-14T14:19:51Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-ship-close-records-merged-sha-and-worker-debrief
issue:
pr:
mod-block:
id: fgvjsq1wsftn2r6ay4yxp2q1
gates:
    version: 1
    records:
        - id: gate:fgvjsq1wsftn2r6ay4yxp2q1:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:fgvjsq1wsftn2r6ay4yxp2q1-backlog-1
              briefing:
                id: briefing:fgvjsq1wsftn2r6ay4yxp2q1:backlog:attempt-1:revision-1
                digest: sha256:b8a5bd66a43bbc4856d5f586e7bd2ac2ddc826390eef26cd52f69dd2d8eda87a
                room-ref: ./ship-close-records-merged-sha-and-worker-debrief/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:fgvjsq1wsftn2r6ay4yxp2q1:backlog:1
                briefing: briefing:fgvjsq1wsftn2r6ay4yxp2q1:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-14T14:02:58.89206Z"
                decision: approve
                reason: backlog admission on the batch conn; brief carries AC-1..4, non-goals, route-back. Enter ideation.
                conn:
                    quote: 准
                    source: Captain chat 2026-09-14, approving the ship-cloud-wrapper-r3 batch of five (pilot profile)
              application:
                target-stage: ideation
                state: consumed
        - id: gate:fgvjsq1wsftn2r6ay4yxp2q1:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:fgvjsq1wsftn2r6ay4yxp2q1-ideation-1
              briefing:
                id: briefing:fgvjsq1wsftn2r6ay4yxp2q1:ideation:attempt-1:revision-1
                digest: sha256:75feb07c85e3a4de413c1aa54901be4eb1012e4c0290aac346d14d60d4d836bf
                room-ref: ./ship-close-records-merged-sha-and-worker-debrief/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:fgvjsq1wsftn2r6ay4yxp2q1:ideation:1
                briefing: briefing:fgvjsq1wsftn2r6ay4yxp2q1:ideation:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-14T14:30:41.505528Z"
                decision: approve
                reason: 'ideation read by the ship FO: pilot receipt, 8-step journey with OBSERVED steps verified against close.py and the real _debriefs tree, where-it-touches limited to close.py/close.test.py/fixtures, AC checks name current failure modes. Enter implementation.'
                conn:
                    quote: 准
                    source: Captain chat 2026-09-14, approving the ship-cloud-wrapper-r3 batch of five (pilot profile)
              application:
                target-stage: implementation
                state: consumed
---

Both close receipts the wrapper has produced carry `merged_sha: null`: `close-receipt-ship-cloud-wrapper-r2.json` (kc-claude-plugins `spacedock-state/ship`, 2026-09-11) and `close-receipt-qnow-clerk-poc.json` (qnow `spacedock-state/ship`, 2026-09-14). Nothing in `close.py` reads the merge commit, although every closed task carries the `pr: pr-merge:N` sentinel that names it. On 2026-09-11 the r2 fence also had to be corrected by hand because debrief matching picked the ship FO's own debrief (it names every slug in its Filed section) instead of each worker's.

## Accepted outcome

1. At close, for every task with `pr: pr-merge:N`, `merged_sha` is resolved from `gh pr view N --repo <owner/repo> --json mergeCommit` (repo from the state checkout's remote) and written to the receipt; a task whose PR is not `MERGED` is refused with its state named, not closed with null.
2. Debrief matching prefers the debrief written by the task's own worker: a `_debriefs/*.md` whose body names the slug under `## Shipped` and whose frontmatter or body carries the worker's session id or dispatch token when present; the ship FO's debrief is never matched to a task. The r2 fence correction (paths -04/-05, shas 916010b3/b4c34965) is the fixture.
3. `close.py --validate` refuses a v2 receipt whose task `merged_sha` is null or not a 40-hex SHA.
4. Fixtures pin no real SHA from this repository; measured evidence is quoted in the PR body.


## Acceptance criteria

* **AC-1** For a task with `pr: pr-merge:N`, `close.py` writes `merged_sha` as the 40-hex `mergeCommit.oid` from `gh pr view N --repo <owner/repo> --json state,mergeCommit`; when `state` is not `MERGED` it exits non-zero naming the slug and state, and writes no receipt.
* **AC-2** Debrief matching picks a `_debriefs/*.md` whose `## Shipped` names the slug and which is not the ship FO's own debrief; with the r2 fixture (two worker debriefs plus one FO debrief naming every slug) each task maps to its worker's file.
* **AC-3** `close.py --validate` refuses a v2 receipt whose task `merged_sha` is null or not 40 hex.
* **AC-4** `close.test.py` covers AC-1..AC-3 with fake `gh` output; no fixture pins a real SHA from this repository.

## Non-goals

- No schema version bump beyond what AC-3 needs; no change to `uat-doc.py` output.
- No network call other than `gh pr view`.

## Route-back conditions

- Back to backlog if the pr-merge mod's sentinel format changes from `pr-merge:N`, or if worker debriefs stop carrying a `## Shipped` section.

Profile recommendation: pilot (harden round; retained code with fixtures).

## Work profile receipt

```yaml
schema: kc-dev-flow-work-profile/v3
selected: pilot-product-slice
recommended: pilot-product-slice
route: [shape, build, verify-deliver]
basis: Reconciled to the Captain's batch conn (Captain chat 2026-09-14, approving the ship-cloud-wrapper-r3 batch of five, pilot profile). close.py's receipt and debrief-matching are retained code every ship close run depends on (kc-ship-flow is the package every adopter's cloud wrapper runs); the r2 fence's hand-corrected debrief (origin/spacedock-state/ship commit 54798ee7, _ship_fence/close-receipt-ship-cloud-wrapper-r2.json) is measured evidence the current heuristic already broke once in real use.
obligations:
  architecture: [close.py gains a `gh pr view` merged_sha resolver and a Shipped-heading-aware, FO-excluding debrief matcher; schema/validate tightened so a null or non-40-hex merged_sha is refused]
  implementation: [kc-ship-flow/scripts/close.py; kc-ship-flow/scripts/close.test.py; kc-ship-flow/scripts/fixtures/close-v2/*; kc-ship-flow/schemas/kc-ship-close-receipt.v2.schema.json]
  testing: [AC-1..AC-4, with a fake gh stub and no real SHA pinned]
scope_boundary: No schema version bump beyond AC-3's merged_sha tightening; no change to uat-doc.py output; no network call other than gh pr view; no live conductor message create call (print-only, unchanged).
semantics_unchanged: false
semantics_unchanged_basis: Three observable behaviors change from today's close.py — (1) merged_sha is resolved from `gh pr view` instead of copied verbatim from the fence record (close.py:248 today), (2) debrief matching stops picking the first sorted-glob regex hit and instead requires a `## Shipped` heading match while excluding the ship FO's own debrief, (3) `--validate` gains a new refusal condition (null/non-40-hex merged_sha) that today's validate_receipt does not check at all (close.py:339-342 checks only `debrief`).
decision:
    authority: Captain (batch conn, ship-cloud-wrapper-r3 batch of five, pilot profile; recorded by agent:first-officer, gate:fgvjsq1wsftn2r6ay4yxp2q1:backlog)
    at: "2026-09-14T14:02:58.89206Z"
```

## Accepted journey

Each step is labeled by how it was established: OBSERVED (verified directly against this
checkout's code/fixtures/history) or DESIGNED (the accepted outcome's requirement, not yet built).

1. **OBSERVED** — `build_receipt` (`close.py:237-261`) writes `merged_sha` straight from
   `fence.get("merged_sha")` (`close.py:248`); nothing in `close.py` calls `gh`. The real r2 fence
   (`origin/spacedock-state/ship` commit `54798ee7`, `_ship_fence/ship-cloud-wrapper-r2.json`)
   carries hand-entered 8-char shas `b4c34965` / `916010b3` — not a 40-hex `mergeCommit.oid`, and
   not derived from any merge-state check.
2. **DESIGNED** (AC-1) — At close, for each `pr-merge:N` task, run
   `gh pr view N --repo <owner/repo> --json state,mergeCommit`; write the 40-hex `mergeCommit.oid`
   as `merged_sha`; when `state` is not `MERGED`, refuse (non-zero exit, slug + state named, no
   receipt written).
3. **OBSERVED** — `find_debrief_path` (`close.py:128-147`) returns the first `_debriefs/*.md` match
   in **sorted filename order** whose body contains the slug as a whole token, anywhere in the file
   — no `## Shipped`-heading requirement, no exclusion of a batch/FO debrief. On the real
   `docs/dev/.spacedock-state/_debriefs/` tree, `2026-09-11-03-claude-claude-fable-5-1.md`
   (frontmatter `scope: ... batch First Officer for sprint ship-cloud-wrapper`) names both
   `ship-dispatch-watch-round-2` and `ship-verify-uat-close-round-2` in its "Filed (backlog)"
   section (lines 27-28) and sorts *before* each task's own worker debrief
   (`2026-09-11-04-claude-claude-sonnet-5.md`, `2026-09-11-05-claude-claude-sonnet-5.md`) — so
   today's scan would return the FO's file for both slugs, reproducing the exact defect the r2
   fence needed hand correction for.
4. **DESIGNED** (AC-2) — Debrief matching prefers a `_debriefs/*.md` whose `## Shipped` section
   names the slug and which is not the ship FO's own debrief (identifiable the way step 3's fixture
   is: a batch-scoped `scope:` naming "First Officer" plus a "Filed (backlog)"-only mention, versus
   a worker debrief whose own `## Shipped` names the slug); validated against a fixture patterned on
   the real -03/-04/-05 trio.
5. **OBSERVED** — `validate_receipt` (`close.py:318-355`) checks only that `debrief` is non-empty
   per task (`close.py:339`); it never inspects `merged_sha`. The schema
   (`kc-ship-flow/schemas/kc-ship-close-receipt.v2.schema.json`) types `merged_sha` as
   `["string","null"]` with no pattern — a null or short/non-hex value passes both gates today.
6. **DESIGNED** (AC-3) — `--validate` refuses (exit 1, slug named) any task whose `merged_sha` is
   null or not exactly 40 hex characters, per the file's own documented two-gate design
   (hand-rolled check first, schema second, `close.py:318-322`).
7. **OBSERVED** — `close.test.py` has no `gh` fixture, stub, or mock anywhere in its 195 lines;
   no existing test exercises a `gh` call because `close.py` never makes one today.
8. **DESIGNED** (AC-4) — `close.test.py` adds coverage for AC-1..AC-3 using a fake `gh` (a stub
   script placed first on `PATH`, matching how other kc-ship-flow scripts fake external commands
   rather than monkeypatching `subprocess`); no fixture pins a real SHA from this repository —
   synthetic values follow the existing fixture convention (`abc1230000...`, `deadbeef`).

### Non-goals

- No schema version bump beyond what AC-3 needs (a `merged_sha` format tightening within
  `kc-ship-close-receipt/v2`, not a v3).
- No change to `uat-doc.py` output.
- No network call other than `gh pr view` (no other GitHub API calls; no `conductor message create`
  invocation — `run_close` still only prints the argv, per its existing docstring contract).
- No change to `commit_and_push_fence`'s git commit/push behavior.

### Where it touches

| File | Touches | Journey stop(s) |
|---|---|---|
| `kc-ship-flow/scripts/close.py` | `build_receipt`'s `merged_sha` source → `gh pr view` resolver; `find_debrief_path` → `## Shipped`-aware, FO-excluding matcher; `validate_receipt` → `merged_sha` format check | 1, 2, 3, 4, 5, 6 |
| `kc-ship-flow/scripts/close.test.py` | New fake-`gh` cases for AC-1; new debrief-trio fixture case for AC-2; new `merged_sha` format cases for AC-3 | 7, 8 |
| `kc-ship-flow/scripts/fixtures/close-v2/**` (`dry-run/`, `closeable/`, `debrief-scan/`, `receipts/`) | New/adjusted fixtures: a `pr-merge` task + fake `gh` stub; a three-file debrief set patterned on -03(FO)/-04/-05(worker) with a `## Shipped` heading; `receipts/invalid-merged-sha.json` | 2, 4, 6, 8 |
| `kc-ship-flow/schemas/kc-ship-close-receipt.v2.schema.json` | `merged_sha` pattern/format tightening (if the schema gate is used for AC-3, alongside the hand-rolled check) | 6 |

### Stop numbers

Delivery base: `26cb22f7` (current tip of
`conductor/ship-cloud-wrapper-r3-ship-close-records-merged-sha-and-worker-debrief`, matching
`origin/main`'s `fix(kc-dev-flow): restore the POC close path after a prove stage (#443)` — the
commit this branch was cut from; all counts below are the diff against this ref).

- **Changed-files stop: 12.** The where-it-touches table names 4 paths, one of which
  (`fixtures/close-v2/**`) is itself ~6-8 files (a new `gh` stub, a `pr-merge` fixture task, a
  three-file debrief trio, one new invalid-`merged_sha` receipt) — predicting ~10-11 touched files
  total. Stop and report to the FO rather than continuing past 12 changed files; a slice that needs
  more has drifted past this fixture set.
- **Changed-lines stop: 350.** `close.py`'s four touched functions (`build_receipt`,
  `find_debrief_path`, `scan_and_record_debriefs`, `validate_receipt`) total ~90 lines today;
  `close.test.py` is 195 lines today and the new AC-1..AC-4 cases are sized similarly to its
  existing per-AC blocks (~20-40 lines each); fixtures are small JSON/markdown. Stop and report
  past 350 added/changed lines (diff against `26cb22f7`) rather than continuing.
- **Named runaway area: the debrief-matching heuristic (`find_debrief_path` → `## Shipped`-aware,
  FO-excluding matcher, journey stop 4).** There is no existing field that flags a debrief as
  "the ship FO's own" — the r2 fixture only shows it indirectly (a batch-scoped `scope:` plus a
  "Filed (backlog)"-only mention). Without a bound, implementation could balloon into speculative
  heuristics (session-id cross-referencing, multiple heading-format variants, worker-identity
  lookups) well past what the -03/-04/-05 fixture needs. Bound: match on the `## Shipped` heading
  plus first-match-in-sorted-order among files whose `## Shipped` (not the whole body) names the
  slug; do not add any FO-identity signal beyond "the match came from a non-`## Shipped` section."

## Task-specific acceptance checks

**AC-1** — `gh pr view` resolution, refusal on non-merged state.
- Given a `pr-merge:N` task and a fake `gh` stub returning
  `{"state":"MERGED","mergeCommit":{"oid":"<40-hex>"}}`, the written receipt's `merged_sha` for
  that task equals the stub's `oid` exactly — a build that still copies the fence's `merged_sha`
  unchanged (today's `close.py:248` behavior) fails this.
- Given the same stub returning `{"state":"OPEN",...}`, `close.py` exits non-zero, prints the slug
  and `OPEN`, and writes no `close-receipt-*.json` — today's `run_close` only consults the
  `pr-merge:` sentinel via `is_merged` and never checks `gh` state, so it would fail this by writing
  a receipt anyway.

**AC-2** — worker-vs-FO debrief matching.
- Given a fixture trio patterned on the real -03/-04/-05 files (an FO debrief naming multiple slugs
  outside a `## Shipped` heading, sorting alphabetically first; two worker debriefs each with a
  `## Shipped` heading naming exactly one slug), matching returns each worker's own file for its
  slug, never the FO's file — today's `find_debrief_path` (first sorted regex hit, no heading or
  identity check) fails this exact fixture, reproducing the r2 defect.
- Given a slug with only an FO-authored debrief present (no worker debrief yet), matching returns
  no path (task stays pending), not a false match on the FO's debrief.

**AC-3** — `--validate` refusal on a bad `merged_sha`.
- `close.py --validate` on a receipt with one task's `merged_sha: null` exits 1 naming that slug —
  today's `validate_receipt` checks only `debrief` and would exit 0 on this receipt, so this is a
  real regression check, not a tautology.
- `close.py --validate` on a receipt with `merged_sha: "abc123"` (short, non-40-hex) exits 1 naming
  the slug; the same receipt with a genuine 40-hex value exits 0.

**AC-4** — fake-`gh`, no real SHA.
- The new AC-1 test cases fail (non-zero) when the fake `gh` stub is removed from `PATH` or its
  output is swapped to an unmerged state — proving the test exercises the `gh` call path rather
  than asserting against a hardcoded receipt.
- `grep -RE '[0-9a-f]{40}' kc-ship-flow/scripts/fixtures/close-v2/` after the change matches no
  value that is also a real commit SHA in this repository's `git log --all` — a fixture-hygiene
  check, not a unit test, but a runnable command an FO/gate can execute to confirm AC-4's
  no-real-SHA condition.

### Summary

Verified against this checkout that `close.py` never calls `gh` and copies `merged_sha` verbatim
from the fence (`close.py:248`), and reproduced the exact r2 debrief-matching defect: the real
`_debriefs/` tree's batch-FO file (`2026-09-11-03-claude-claude-fable-5-1.md`) sorts before each
task's own worker debrief and would be picked first by today's `find_debrief_path` for both
`ship-cloud-wrapper-r2` slugs. The accepted outcome's four ACs are journeyed against this evidence
(OBSERVED steps 1/3/5/7, DESIGNED steps 2/4/6/8) and reconciled into a where-it-touches table and
falsifiable acceptance checks so `build` has a concrete fixture (the -03/-04/-05 pattern) rather
than a restated requirement.

## Stage Report: ideation

- DONE: Work profile receipt recorded (kc-dev-flow-work-profile/v3, selected: pilot-product-slice, semantics_unchanged declared with basis) citing the Captain's ship-cloud-wrapper-r3 batch conn.
  See "## Work profile receipt" above; basis cites gate:fgvjsq1wsftn2r6ay4yxp2q1:backlog and the r2 fence hand-correction as measured evidence.
- DONE: Accepted journey (each step OBSERVED or DESIGNED) plus explicit non-goals, and a `where it touches` table (close.py, close.test.py, fixtures) reconciled against the journey with named stop numbers.
  See "## Accepted journey" — 8 numbered steps, OBSERVED steps 1/3/5/7 verified directly against close.py line ranges and the real `_debriefs/` tree; the table maps each touched file to its stop numbers.
- DONE: Task-specific acceptance checks able to falsify the slice, mapped to AC-1..AC-4 (gh pr view resolution, worker-vs-FO debrief matching, --validate refusal, no real SHA in fixtures).
  See "## Task-specific acceptance checks" — each AC has a check naming the current code's actual failure mode, not a restated requirement.

### Summary

Read `close.py`/`close.test.py` in full and confirmed two things directly: `merged_sha` is copied verbatim from the fence with no `gh` call anywhere in the script, and the real `docs/dev/.spacedock-state/_debriefs/` tree reproduces the r2 debrief-matching bug exactly (the batch FO's debrief, `2026-09-11-03-...md`, sorts before each worker's own debrief and would be the first regex match for both slugs). That evidence anchors the OBSERVED/DESIGNED journey, the where-it-touches table, and falsifiable AC-1..AC-4 checks the build stage can implement against.

## Stage Report: implementation

- DONE: close.py resolves merged_sha via `gh pr view N --json state,mergeCommit` and refuses (non-zero, slug+state named, no receipt) a non-MERGED task; find_debrief_path prefers a worker's own `## Shipped`-naming debrief and never matches the ship FO's, per the ideation journey/AC-1/AC-2.
  `resolve_merged_shas`/`_gh_pr_view` (close.py:248-281) and `_shipped_section`/`find_debrief_path` (close.py:138-172); close.test.py's not-merged and debrief-fo-exclude cases exercise both against the r2-pattern fixture (commit feeb97ce).
- DONE: close.py --validate refuses a v2 receipt whose merged_sha is null or not 40-hex (AC-3); close.test.py covers AC-1..AC-3 with a fake gh stub on PATH and no real SHA from this repository pinned anywhere (AC-4).
  `validate_receipt`'s new `MERGED_SHA_RE` check (close.py:425-432) plus schema pattern tightening; `bad-merged-sha.json` fixture flips both cases (null + short) from pass to refusal; `fake-gh/` stub is on PATH by default in every `run()` call, and the AC-4 case proves removing it from PATH flips a would-succeed close to a failure (`git log --all` has none of the fixtures' synthetic 40-hex values).
- DONE: Stayed within the ideation stop numbers (delivery base 26cb22f7; <=12 changed files, <=350 changed lines) and ran kc-dev-flow/scripts/surface-map-check.py against the candidate diff at exit.
  `git diff --numstat 26cb22f7` (post-commit feeb97ce): 12 files changed, 303 insertions(+), 46 deletions(-) = 349 changed lines, at the stop-number boundary; `surface-map-check.py` exits 0 ("OK (2 files checked)") for the two non-excluded surfaces (close.py -> AC-1, the schema -> AC-3), run against a wrapper-corrected copy of the entity's own Work profile receipt (see note below).

### Summary

Added a `gh pr view`-backed merged_sha resolver (refusing non-MERGED tasks) and restricted debrief matching to each file's `## Shipped` section, which excludes the ship FO's own debrief without any separate FO-identity signal, reproducing and fixing the exact r2 defect. `--validate` and the schema now both refuse a null/non-40-hex merged_sha. All new behavior is covered by close.test.py against a fake `gh` stub on PATH, with no real repository SHA pinned in any fixture; `close.test.py` and `uat-doc.test.py` both pass. Note for the FO: the entity's own "## Work profile receipt" YAML lacks the `work_profile:` wrapper key `surface-map-check.py`'s loader requires (an ideation-stage format gap); the check above ran against a wrapper-corrected copy of the same receipt content rather than editing the entity's body outside this stage's scope.
