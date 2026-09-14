---
title: "close.py closes only the tasks the batch dispatched, and its validator exempts Captain-stopped tasks from the merged_sha rule"
status: ideation
source: "measured on the first close after #448 merged, ship-cloud-wrapper-r3, 2026-09-15 (questions log on spacedock-state/ship)"
product: kc-ship-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r4
sprint-readiness: ready
started: 2026-09-14T22:32:03Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: 8ekqymrkgz5f9y0h8qaf6vp2
gates:
    version: 1
    records:
        - id: gate:8ekqymrkgz5f9y0h8qaf6vp2:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:8ekqymrkgz5f9y0h8qaf6vp2-backlog-1
              briefing:
                id: briefing:8ekqymrkgz5f9y0h8qaf6vp2:backlog:attempt-1:revision-1
                digest: sha256:a4abe55b7f086322b4f438e04bcced96ed7fed0cd2fabbb3fdfb4994c786de58
                room-ref: ./close-roster-is-the-fence-and-captain-stopped-validates/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:8ekqymrkgz5f9y0h8qaf6vp2:backlog:1
                briefing: briefing:8ekqymrkgz5f9y0h8qaf6vp2:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-14T22:30:03.889959Z"
                decision: approve
                reason: 'backlog admission on the batch conn: brief carries bite, consumer, AC-1..4, non-goals, route-back. Enter ideation.'
                conn:
                    quote: r4 現在開
                    source: Captain chat 2026-09-15, opening the ship-cloud-wrapper-r4 batch of three (pilot profile)
              application:
                target-stage: ideation
                state: consumed
        - id: gate:8ekqymrkgz5f9y0h8qaf6vp2:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:8ekqymrkgz5f9y0h8qaf6vp2-ideation-1
              briefing:
                id: briefing:8ekqymrkgz5f9y0h8qaf6vp2:ideation:attempt-1:revision-1
                digest: sha256:cdc4e9d23e04cedd9861dddf81d737ec7c0f69f2af544cfd74dd1d58992abce1
                room-ref: ./close-roster-is-the-fence-and-captain-stopped-validates/review/ideation/briefing-1
---

bite: 2026-09-15, `python3 kc-ship-flow/scripts/close.py ship-cloud-wrapper-r3 --dev-state … --ship-state …` at main 625c6b50. (1) It exited 3 `not all tasks merged` because three entities carrying `sprint: ship-cloud-wrapper-r3` with `sprint-readiness: defer` — never dispatched, absent from the fence — were counted as batch tasks; the ship FO had to move them to another sprint to close. (2) After that, `close.py --validate` refused the receipt it had just written: the two `captain_stopped` tasks (PRs #446 and #450, closed unmerged by the Captain) carry `merged_sha: null`, and #448's 40-hex rule has no exemption for them, so the first receipt the new validator ever saw failed on its own rule. The receipt was committed with the refusal disclosed.

consumer: the ship first officer's close step (`kc-ship-flow:run-batch`, stage closed), every batch that has a deferred sibling in the sprint or a Captain-closed PR — both happened in the first three batches.

## Accepted outcome

`close.py` treats the fence as the batch roster, and a Captain-stopped task closes with a receipt entry that says so instead of failing validation.

## Acceptance criteria

* **AC-1** `close.py` builds its task set from the fence's slugs (what `dispatch.sh` claimed), not from every entity whose `sprint` matches; an entity in the sprint but absent from the fence is listed once on stderr as `not dispatched` and ignored. Verified by: the r3 state replayed with the three deferred entities present closes without moving them. Falsified by: exit 3 on that replay.
* **AC-2** A task in `captain_stopped` is written with `merged_sha: null` and `closed: captain_stopped`, and `--validate` accepts it; a merged task with a null or non-40-hex `merged_sha` is still refused. Verified by: the r3 receipt validates as committed; the existing bad-merged-sha fixture still fails. Falsified by: either outcome flipping.
* **AC-3** No new fixture copies real repository SHAs or duplicates an existing file.

## Non-goals

- No change to the receipt schema version; add the `closed` field as optional.
- No change to debrief matching (#448).

## Route-back conditions

- Back to backlog if the fence shape written by `dispatch.sh --resume` (#445 `history`) changes the slug roster semantics.

Profile recommendation: pilot.

## Shape

Read `docs/architecture.md`: not present in this repo tree (no per-repo architecture
map exists yet); `kc-ship-flow/CLAUDE.md` and the module docstring in `close.py` are
the working map for this slice and are sufficient — no bootstrap needed for a
same-file fix this small.

### Journey

1. OBSERVED — `dispatch.sh` writes `<ship-state>/_ship_fence/<sprint>.json` as a
   top-level map keyed by each *dispatched* slug (`workspace`, `session`,
   `message_sha256`), with batch-level siblings `questions`, `residuals`, and
   `captain_stopped` (a list of slugs the Captain closed unmerged). `close.py`
   already reads this file via `uat_doc.load_batch_record` (`close.py` lines
   192-203 in `uat-doc.py`).
2. DESIGNED — `run_close` currently takes its task set straight from
   `uat_doc.load_task_entities(dev_state, sprint)`, which matches *every* entity
   whose `sprint:` frontmatter equals the sprint — dispatched or not. The fix scopes
   that set to fence membership: any entity slug that is not a key of the loaded
   `record` (excluding the reserved batch-level keys `questions`, `residuals`,
   `e2e`, `captain_stopped`) is dropped before any merged/debrief check runs, and
   its slug is printed once to stderr as `close: <slug> not dispatched, skipping`.
3. OBSERVED (bug) — 2026-09-15, r3 replay at main 625c6b50: three entities carried
   `sprint: ship-cloud-wrapper-r3` with `sprint-readiness: defer`, were never
   claimed in the fence, and were still counted by `load_task_entities`, forcing
   exit 3 `not all tasks merged` until the ship FO moved their `sprint:` field by
   hand. Step 2 removes that workaround.
4. DESIGNED — for the fence-scoped task set, the existing merged/debrief/gh-confirm
   logic (`resolve_merged_shas`, `NotMergedError`) is unchanged: a task whose `pr:`
   is `pr-merge:<N>` but `gh pr view` doesn't confirm `MERGED` still exits 3.
5. DESIGNED — `build_receipt` gains a `closed` key per task: when `slug` is in
   `captain_stopped`, the entry carries `"closed": "captain_stopped"` alongside the
   `"merged_sha": null` it already writes today (unchanged — `resolve_merged_shas`
   already skips non-merged tasks, so the field was already null; only the `closed`
   marker is new). A merged task's entry omits `closed` entirely (optional field,
   per non-goals).
6. OBSERVED (bug) — same 2026-09-15 run: `close.py --validate` refused the receipt
   it had just written, because PRs #446/#450 (`captain_stopped`) carry
   `merged_sha: null` and #448's 40-hex-or-refuse rule had no exemption for them —
   the first receipt the new validator ever saw failed on its own rule. The ship FO
   committed the receipt with the refusal disclosed rather than block the batch.
7. DESIGNED — `validate_receipt`'s `bad_sha` check accepts a task when either (a)
   `merged_sha` matches `MERGED_SHA_RE`, or (b) `merged_sha is None` and
   `task.get("closed") == "captain_stopped"`. Every other shape (null/short/
   non-hex `merged_sha` without that marker, including on a merged task) still
   fails exactly as before — unchanged fixture `bad-merged-sha.json` must keep
   failing. `kc-ship-close-receipt.v2.schema.json` is relaxed to match: `merged_sha`
   becomes `type: ["string", "null"]` (pattern applies only when non-null via an
   `if`/`then`, or a `oneOf` split — implementation detail for `build`), and an
   optional `closed` property is added (`enum: ["captain_stopped"]`), so schema
   validation doesn't re-reject what the hand-rolled check now accepts.

Observable semantics changed (not `semantics_unchanged`): (a) `close.py`'s batch
membership test changes from "entity's `sprint:` field matches" to "slug is a
fence key" — a real behavior change for any sprint carrying a deferred/undispatched
sibling; (b) the `kc-ship-close-receipt/v2` schema's `merged_sha` becomes nullable
and gains an optional `closed` enum field — additive, no schema version bump (the
non-goal), but a receipt-shape change a downstream reader (e.g. a debrief-matching
consumer) must tolerate a null `merged_sha` when `closed` is set.

### Where it touches

| path | lines now | lines after |
|---|---|---|
| `kc-ship-flow/scripts/close.py` | 478 | ~505 (fence-scoped filter in `run_close`, `not dispatched` stderr line, `closed` key in `build_receipt`, exemption clause in `validate_receipt`'s `bad_sha`) |
| `kc-ship-flow/schemas/kc-ship-close-receipt.v2.schema.json` | 51 | ~62 (`merged_sha` type widened to allow null, new optional `closed` enum property) |
| `kc-ship-flow/scripts/close.test.py` | 256 | ~300 (AC-1: not-dispatched-sibling skip test; AC-2: captain_stopped receipt validates, existing `bad-merged-sha` fixture still fails) |
| `kc-ship-flow/scripts/fixtures/close-v2/not-dispatched/` (new) | 0 | small fixture: two entities sharing a sprint, only one present as a fence key, `_ship_fence/<sprint>.json` naming only the dispatched slug |
| `kc-ship-flow/scripts/fixtures/close-v2/receipts/captain-stopped.json` (new) | 0 | receipt fixture with one `captain_stopped`/null-`merged_sha` task and one normally-merged task — new file, no real repo SHAs (AC-3) |

Reconciled against the journey: every touched file appears in a journey step
(steps 2/4/5 -> `close.py`; step 7 -> schema; fixtures back steps 2 and 7's test
claims); no journey step depends on a file the table omits.

### Stop numbers

Diff base: `main` at 625c6b50 (`fix(kc-ship-flow): make sql a degradable probe,
watch.sh falls back to session message (#451)`), the tip named in the entity's
`source:`. Stop and report rather than continuing past:

- **8 changed files** (the 5 in the table above plus at most 3 more if the fence
  filter needs a small helper split out, or an existing fixture needs a
  companion `.md` beyond the ones listed).
- **150 changed lines** (diff insertions+deletions against the base above).
- **`validate_receipt`'s `bad_sha` branch is the area most likely to run away** —
  it is the one place tempted to grow a general "reason codes for a null
  merged_sha" system instead of the single `captain_stopped` exemption AC-2 asks
  for; if it needs more than the one `or` clause described in journey step 7,
  stop and report rather than generalizing.

## Stage Report: ideation

- DONE: Record the Work Profile receipt (schema kc-dev-flow-work-profile/v3, selected pilot-product-slice) with basis, route, and task-specific obligations.
  `{"schema": "kc-dev-flow-work-profile/v3", "profile": "pilot-product-slice", "basis": "entity frontmatter Profile recommendation: pilot, ship-cloud-wrapper-r4 batch (pilot profile per gate resolution conn)", "route": "shape -> build (no multi-slice, no brownfield-capability-change, no user-visible surface)", "obligations": ["one accepted journey with OBSERVED/DESIGNED marks and semantics_unchanged declaration", "file-level where-it-touches table reconciled against the journey", "task-specific AC-1/AC-2 falsification checks", "stop numbers against main@625c6b50"]}`
- DONE: Shape AC-1: derive close.py's task set from the dispatch fence's slugs, not from every sprint-matching entity, with a stderr-visible not-dispatched skip.
  Journey step 2/3; traced current bug through `close.py` lines 333-345 (`run_close` calling `uat_doc.load_task_entities`) against `uat-doc.py` lines 173-189 and the r3 bite in this entity's `bite:` line.
- DONE: Shape AC-2: define the captain_stopped receipt shape (merged_sha: null, closed: captain_stopped) that --validate accepts, while the existing bad-merged-sha refusal for merged tasks is unchanged.
  Journey steps 5-7; traced against `close.py` lines 306-330 (`build_receipt`) and 394-442 (`validate_receipt`), and the schema's current `required: [... "merged_sha" ...]` non-nullable pattern at `kc-ship-close-receipt.v2.schema.json` line ~20.

### Summary

Traced the r3 bite through `close.py`/`uat-doc.py`/the fence schema to ground both ACs in the exact functions and line ranges `build` will touch: `run_close`'s task-set derivation (AC-1) and `build_receipt`/`validate_receipt`/the JSON Schema's `merged_sha` nullability (AC-2). No code changed this stage — shape only. Where-it-touches table names two new fixture files (a not-dispatched-sibling fixture, a captain-stopped receipt) alongside `close.py`, the schema, and `close.test.py`; stop numbers are 8 files / 150 lines against `main@625c6b50`.
