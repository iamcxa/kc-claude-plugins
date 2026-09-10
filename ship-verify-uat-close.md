---
title: "ship-flow POC: verify at the integrated head, one UAT document, worker-written debriefs, and a slim close receipt"
status: implementation
source:
product: kc-ship-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper
sprint-readiness: ready
started: 2026-09-10T08:56:36Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-ship-verify-uat-close
issue:
pr: 411
mod-block:
id: 7efj5b0dh4dh7616yma4nykm
gates:
    version: 1
    records:
        - id: gate:7efj5b0dh4dh7616yma4nykm:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:7efj5b0dh4dh7616yma4nykm-backlog-1
              briefing:
                id: briefing:7efj5b0dh4dh7616yma4nykm:backlog:attempt-1:revision-1
                digest: sha256:5e72e261ae2278e8489b44c8db3040afa3f475a72ae1729da40db721405e4d3f
                room-ref: ./ship-verify-uat-close/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:7efj5b0dh4dh7616yma4nykm:backlog:1
                briefing: briefing:7efj5b0dh4dh7616yma4nykm:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T08:49:47.915875Z"
                decision: approve
                reason: 'Captain approved in chat: approve 2026-09-10'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:7efj5b0dh4dh7616yma4nykm:validation
          stage: validation
          attempts:
            - id: gate-attempt:7efj5b0dh4dh7616yma4nykm-validation-1
              briefing:
                id: briefing:7efj5b0dh4dh7616yma4nykm:validation:attempt-1:revision-1
                digest: sha256:4047200f33c792d975771a7a4dd83b490edddcdefd2a33aa6706568f56349581
                room-ref: ./ship-verify-uat-close/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:7efj5b0dh4dh7616yma4nykm:validation:1
                briefing: briefing:7efj5b0dh4dh7616yma4nykm:validation:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-10T16:04:56.707615Z"
                decision: revise
                reason: 'Batch FO verification at the PR head: built from main without #406; integration defects (see feedback message)'
                conn:
                    quote: '批 (2026-09-10, answering the First Officer: "#410/#411 各一輪 feedback ... 合了我就對兩個雲端 workspace 各送一則 feedback")'
                    source: Captain chat reply 2026-09-10 to the three-gate table
---

After dispatch and watch exist and the duplicated stations are gone, the back half of a batch
still reads files the new design no longer produces: `uat-doc.py` reads
`receipt/plan-receipt.json` and `receipt/plan-approval.json`, the close receipt v1 requires
embedded `dev_debrief` / `ship_debrief` blocks written by ship, and nothing sends a cloud worker
the post-merge instruction to write its own `spacedock debrief`. Design:
`docs/superpowers/specs/2026-09-10-ship-flow-cloud-wrapper-design.md`, sections "verified",
"uat", "closed".

## Accepted outcome

`uat-doc.py <sprint>` reads only the `docs/dev` entities of the sprint and the batch record and
writes one UAT document: tasks, PR links, gate status, e2e result at the integrated head,
questions asked and answered. `e2e-gate.py` is called with `--root` set to the head the
`Integrated head` Local Profile row selects (`preview` | `trunk` | `staging`). `close.py <sprint>`
sends each worker whose task shows `pr: pr-merge:N` one message asking it to run
`spacedock debrief`, commit path-scoped under `_debriefs/`, and push; records `debrief-failed`
after a second rejected push; and writes `kc-ship-close-receipt/v2` (schema id, sprint, per task
{slug, workspace id, session id, PR, merged sha, debrief path or failure}, e2e result, questions
and answers, residuals) only when every task shows a merged PR and a pushed debrief or a
`captain_stopped` record.

## Non-goals

* Writing a debrief on a worker's behalf.
* Any reader of the close receipt outside kc-ship-flow (open item for the Captain).
* Any Linear read or write.

## Acceptance criteria

* **AC-1** `python3 kc-ship-flow/scripts/uat-doc.py ship-cloud-wrapper --state-dir <fixture>` exits 0 writing the document with every task of the fixture sprint, and exits 1 printing the slug when a task lacks a prepared `validation` gate.
* **AC-2** `python3 kc-ship-flow/scripts/close.py ship-cloud-wrapper --dry-run --state-dir <fixture>` prints one `conductor message create --session <id>` argv per merged task and none for an unmerged one, and exits 3 printing `not all tasks merged` when asked to write the receipt with an unmerged task present.
* **AC-3** `python3 kc-ship-flow/scripts/close.py --validate <receipt.json>` exits 0 on the fixture receipt and exits 1 on a copy missing any task's `debrief` field.
* **AC-4** The real run: this sprint's own batch is closed by `close.py`; the state branch carries one `_debriefs/` file per cloud worker, each with an Agent Testimonial section, pushed by that worker.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [shape, build, verify-deliver]
  basis: Back half of the fifth ship-flow POC; the falsifier is that the sprint closes with worker-written debriefs and a receipt no ship script had to hand-edit. Evidence first; the code is rewritten after the POC.
  obligations:
    architecture: [Read docs/dev entities and the batch record only; the integrated head comes from one Local Profile row; debriefs are written by workers]
    implementation: [uat-doc.py rewrite; close.py; close receipt v2 schema; delete v1 fixtures]
    testing: [AC-1 to AC-3 on fixtures; AC-4 on the real sprint]
  scope_boundary: No debrief written by ship; no external receipt reader; no Linear.
  semantics_unchanged: false
```

## Stage Report: implementation

- DONE: uat-doc.py rewritten to read only docs/dev entities + batch record and write one UAT document (tasks, PR links, gate status, e2e result), calling e2e-gate.py with --root from the Integrated head Local Profile row
  `kc-ship-flow/scripts/uat-doc.py` (commit 3053f925): reads `<state-dir>/*.md` frontmatter directly (no plan-receipt.json/plan-approval.json/close-receipt.json) plus `<state-dir>/_ship_fence/<sprint>.json`; `run_e2e_gate()` calls `e2e-gate.py --root <resolved> --flows <resolved>` with the root/flows resolved from `docs/ship/README.md`'s `Integrated head`/`E2E flows` Local Profile rows.
- DONE: close.py written to message each merged task's worker to run spacedock debrief, record debrief-failed on repeated push rejection, and write kc-ship-close-receipt/v2 only when every task has a merged PR + pushed debrief or captain_stopped
  `kc-ship-flow/scripts/close.py` (new, commit 3053f925): a task is "merged" iff its `pr:` frontmatter is exactly `pr-merge:<N>`; `print_debrief_messages()` prints one `conductor message create --session <id>` argv per merged task still pending a debrief; `build_receipt()`/`run_close()` write `kc-ship-close-receipt/v2` only once every non-`captain_stopped` task is merged with a `pushed` or `failed` (repeated-push-rejection) debrief, reading that status from the fence file's `tasks.<slug>.debrief`.
- DONE: AC-1, AC-2, AC-3 pass against fixtures per the entity's Acceptance criteria
  `kc-ship-flow/scripts/uat-doc.test.py` (AC-1: `fixtures/uat-doc-v2/ready` exits 0 with both tasks and the recorded Q&A; `fixtures/uat-doc-v2/missing-gate` exits 1 printing exactly `DEV-203`, whose validation gate is already resolved, not prepared). `kc-ship-flow/scripts/close.test.py` (AC-2: `fixtures/close-v2/dry-run` `--dry-run` prints exactly one `conductor message create --session sess-301 ...` line and nothing for the unmerged `DEV-302`; the same fixture without `--dry-run` exits 3 printing `not all tasks merged`; AC-3: `--validate` on `fixtures/close-v2/receipts/valid.json` exits 0, on a copy with `DEV-301`'s `debrief` field deleted exits 1 naming `DEV-301`). Both test files run standalone (`python3 kc-ship-flow/scripts/uat-doc.test.py`, `python3 kc-ship-flow/scripts/close.test.py`) and are wired into `kc-ship-flow/scripts/contract-test.py`'s `STATIONS`/`STATION_TESTS`/`py_compile` lists.

### Residuals (not fixed, flagged for the next stage/task)

- `docs/superpowers/specs/2026-09-10-ship-flow-cloud-wrapper-design.md` (this entity's own header cites it) does not exist on `main` or this worktree's branch; it was found only on `origin/docs/ship-flow-cloud-wrapper-spec` (fetched during this stage) and used as the authoritative design source for `uat-doc.py`/`close.py`'s "uat"/"closed" sections. Whoever merges this sprint's design doc into `main` should confirm nothing in it contradicts the schemas invented here.
- The `_ship_fence/<sprint>.json` batch-record schema (`tasks.<slug>.{workspace_id,session_id,merged_sha,debrief}`, `questions[]`, `captain_stopped[]`) is this task's own invention (the sibling dispatch/watch task's real fence-file shape was not mergeable/readable from this worktree at time of writing -- its own report only says "the claim fence is dispatch.sh's own JSON file under `_ship_fence/`", no field list). If dispatch.sh/watch.sh land a different shape, `uat_doc.load_batch_record()`/`close.py`'s readers need reconciling before the AC-4/real-sprint run.
- "record debrief-failed on repeated push rejection" is read, not written, by `close.py`: this script expects the fence file to already carry `debrief.status: "failed"` after a worker's second rejected push (the design assigns that write to the worker/watch side, not to `close.py`). No script in this sprint writes that field yet; AC-4's real run needs it before `close.py` can close a debrief-failed task.
- Per the design's "What leaves kc-ship-flow" table and this entity's own `implementation` obligation ("delete v1 fixtures"), `fixtures/uat-doc/` (the old plan-flow-batch-dir fixtures) and `dev-debrief.py`/`ship-debrief.py` are removal candidates -- left untouched here because removing stations is explicitly the sprint's second task ("Slimming uat-doc.py, the close receipt, or writing close.py (third task)" is this entity's own non-goal boundary in the sibling task). `uat-doc.py` keeps `find_worker_evidence_files()`/`load_defaults_decisions()` as explicitly-labeled legacy compatibility so `dev-debrief.py`/`ship-debrief.py`'s existing tests keep passing until that removal lands.
- AC-4 (the real sprint's own batch closed by `close.py`, worker-written debriefs pushed to the state branch) is out of this stage's checklist (which names only AC-1 to AC-3) and was not attempted -- it depends on the sibling dispatch/watch task's real cloud run landing first.
- `kc-ship-flow/scripts/contract-test.py`'s pre-existing `fenced-dispatch.test.sh` failure (3 of 4 cases) reproduces identically on this branch's unmodified HEAD (verified via `git stash`) -- unrelated to this stage's changes, not fixed here.

### Summary

`uat-doc.py` and `close.py` are rewritten/written per the cloud-wrapper design's "uat" and "closed"
stages: both read a sprint's `docs/dev` entity frontmatter and a new `_ship_fence/<sprint>.json`
batch record directly, with no plan-flow receipt in the loop. `close.py` messages each merged
task's worker to debrief and writes `kc-ship-close-receipt/v2` only once every task is closeable.
AC-1 through AC-3 pass against purpose-built fixtures (`fixtures/uat-doc-v2/`,
`fixtures/close-v2/`); the design doc itself and the sibling dispatch/watch task's fence-file
schema were not available in this worktree, so the batch-record shape and the debrief-failed
write path are this stage's own invention, flagged above for reconciliation before AC-4's real run.

## Stage Report: validation

- DONE: Local POC verification: AC-1 and AC-2 and AC-3 reproduce against fixtures at this exact head (not just cited from the implementation report)
  At worktree HEAD 3053f925: `uat-doc.py ship-cloud-wrapper --state-dir fixtures/uat-doc-v2/ready` exits 0 with both tasks + Q&A rendered; `--state-dir fixtures/uat-doc-v2/missing-gate` exits 1 printing `DEV-203`. `close.py ship-cloud-wrapper --dry-run --state-dir fixtures/close-v2/dry-run` prints exactly one `conductor message create --session sess-301 ...` line, none for unmerged `DEV-302`; the same fixture without `--dry-run` exits 3 printing `not all tasks merged`. `close.py --validate fixtures/close-v2/receipts/valid.json` exits 0; the same file with `DEV-301`'s `debrief` field removed exits 1 naming `DEV-301`. `uat-doc.test.py` and `close.test.py` both print "all checks passed", exit 0.
- SKIPPED: Draft PR opened for this entity's diff via the pr-merge mod per the Local Profile's delivery authority
  Per the FO's explicit correction this run, PR push/creation is the FO's action, not this ensign's — I did not push the branch or run `gh pr create`. Preflight is done and reusable: `git merge-tree --write-tree origin/main HEAD` (origin/main at c2c62bf9) is clean; diff is 23 files / +1016/-379 against origin/main, tripping the numeric topology trigger (files > 20) with no dependent/independent layers, so the delivery unit is one Draft PR carrying a `## Native stack exception` heading (the 14 fixture files only make sense paired 1:1 with the two rewritten scripts/tests). Split-root audit-link tuple resolved: entity path `ship-verify-uat-close.md`, state SHA `4bbf5638b747e5dcdb8da8dd5d1bd356ee9b3eb0`, state repo `iamcxa/kc-claude-plugins` -> `[7e](/iamcxa/kc-claude-plugins/blob/4bbf5638b747e5dcdb8da8dd5d1bd356ee9b3eb0/ship-verify-uat-close.md)`.
- SKIPPED: AC-4 real run attempted or its exact blocking dependency (sibling dispatch/watch task's fence-file shape) named as a residual, not silently dropped
  Not attempted; still blocked on the same dependency the implementation stage report named. Reverified this stage: `kc-ship-flow/scripts/fenced-dispatch.sh` (the only dispatch station present on this branch; no `watch.sh` exists yet) has zero references to `_ship_fence`, `debrief`, `workspace_id`, `session_id`, or `merged_sha` — the batch-record schema `close.py`/`uat-doc.py` read is still this task's own invention, not yet produced by any dispatch/watch station. AC-4 needs that station to land and its fence-file shape reconciled with `uat_doc.load_batch_record()`/`close.py`'s readers before a real run can be attempted.

### Summary

AC-1 through AC-3 reproduced live at worktree HEAD 3053f925 (not re-cited from the implementation
report); both fixture-driven test files still report all-clear. Draft PR creation was deliberately
left to the FO per this run's explicit correction — the PR body, topology decision, and split-root
audit-link tuple are pre-resolved above so the FO's pr-merge pass needs no rework. AC-4 remains
blocked on the sibling dispatch/watch task's fence-file schema, reverified absent on this branch,
and is named here rather than silently dropped.

## Stage Report: implementation (cycle 2)

- DONE: Branch merges origin/main (merge commit, not rebase) picking up #406's dispatch.sh/watch.sh
  Merge commit 750db571 (`git merge origin/main --no-edit`), clean, no conflicts; `origin/main` was at c9c5752f (post-#406/#407/#412).
- DONE: close.py and uat-doc.py read/write the fence shape dispatch.sh actually writes (top-level slug -> {workspace, session, message_sha256}, debrief recorded as slug.debrief -> {status, path}), fixtures/tests updated, new test loads a dispatch.sh --dry-run-format fence file
  `uat_doc.load_batch_record()` now returns the raw top-level dict (no `sprint`/`tasks` synth wrapper); `close.py`'s `debrief_status`/`debrief_message`/`build_receipt` read `record.get(slug, {})` directly, and write `merged_sha`/`debrief` as further keys of that same slug object. All four v2 fixtures (`uat-doc-v2/{ready,missing-gate}`, `close-v2/{dry-run,closeable}`) rewritten to the flat shape; commit 8dc28e4f. New tests in both `uat-doc.test.py` and `close.test.py` load `fixtures/watch/state/_ship_fence/ship-cloud-wrapper.json` — the sibling dispatch/watch task's own fixture, pinned to dispatch.sh's real committed shape per `dispatch.test.sh` cases (b)/(e) — through `load_batch_record`/`debrief_status`/`build_receipt`, proving the reader matches dispatch.sh's actual output rather than a hand-authored stand-in.
- DONE: v2 receipt schema shipped as kc-ship-flow/schemas/kc-ship-close-receipt.v2.schema.json and used by close.py --validate
  New file (commit 8dc28e4f); `close.py`'s `validate_receipt()` runs its existing name-the-field checks first, then `jsonschema.validate()` against this schema (hard `import jsonschema` dependency, matching `docs/plan-flow/schema/validate-receipt.py`'s established pattern in this tree). `close.test.py`'s AC-3 cases (valid/missing-debrief) still pass against the schema-backed validator.
- SKIPPED: Delete the v1 schema and its fixtures
  Finding 3's own condition ("only if nothing left in the tree reads them") is not met: `docs/plan-flow/schema/validate-receipt.py`, `dev-debrief.py`, `ship-debrief.py`, `e2e-gate.py`, and `contract-test.py` all still read `kc-ship-close-receipt.v1.schema.json` or `kc-ship-close-receipt/v1`, plus a dozen v1-shaped fixtures. Removal is explicitly the sprint's second task (`ship-remove-duplicated-stations`) per this entity's own non-goals; deleting here would break those still-live readers.
- DONE: PR #411 body rewritten exactly per docs/dev/_mods/pr-merge.md template
  Rewritten via `gh pr edit 411 --body-file` to: one <=25-word motivation sentence, `## What changed` (4 bullets, each <=15 words, no rationale), `## Evidence` (2 bullets, N/N-passed form), `## Native stack exception` (retained per the topology gate: merge-base diff is 23 files / +1117/-375 against `origin/main`, tripping the numeric trigger with no independently reviewable layer), `## Residuals` (3 bullets, known limits only), `---`, then the split-root audit link resolved fresh at this cycle's own state SHA (below) — no Linear id anywhere.

### Split-root audit-link tuple (this cycle)

`ENTITY_PATH=/home/vercel-sandbox/kc-claude-plugins/docs/dev/.spacedock-state/ship-verify-uat-close.md`,
`STATE_ROOT` = same dir's toplevel, `STATE_RELATIVE_PATH=ship-verify-uat-close.md`,
`STATE_ORIGIN=https://github.com/iamcxa/kc-claude-plugins` -> `STATE_REPO=iamcxa/kc-claude-plugins`,
`SHORT_ID=7e`. `STATE_SHA` is this stage report's own commit SHA on `spacedock-state/dev` (resolved
fresh, per the mod, immediately before constructing the PR body -- not reconstructed after).
Recorded literally in the PR body's audit link below.

### Summary

Merged `origin/main` (merge commit, not rebase) to pick up #406's `dispatch.sh`/`watch.sh`; fixed
the fence-shape mismatch findings 1-2 flagged (top-level slug map, no `tasks` wrapper, debrief
nested per-slug) with fixtures and tests reconciled against the sibling task's own real fence
fixture, not a hand-authored guess; shipped the v2 receipt schema as a file and wired
`close.py --validate` to it via `jsonschema` (v1 deletion skipped — still read by five other
scripts, out of this task's scope per the entity's own non-goals); and rewrote PR #411's body to
the FO's exact template. All of `uat-doc.test.py` (14/14 checks) and `close.test.py` (9/9 checks)
pass at this cycle's head; the pre-existing, unrelated `fenced-dispatch.test.sh` failure (3 of 4
cases) was reverified identical on the clean merge commit before any of this cycle's edits.
