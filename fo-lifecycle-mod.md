---
title: kc-dev-flow-2 ships a Spacedock mod that loads FO's merge, idle and startup steps at those moments
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:fo-lifecycle-mod:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:fo-lifecycle-mod-backlog-1
              briefing:
                id: briefing:fo-lifecycle-mod:backlog:attempt-1:revision-1
                digest: sha256:af2480e55707c7b503a21ad1c18ce6c6de9b283fba6565b8ad5a783f22870546
                room-ref: ./fo-lifecycle-mod/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:fo-lifecycle-mod:backlog:1
                briefing: briefing:fo-lifecycle-mod:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-13T23:51:07.681641Z"
                decision: approve
                reason: 'Captain approved (「ok」): schedule as Pilot and enter ideation, next after followup-dispatch-records-checked.'
              application:
                target-stage: ideation
                state: consumed
started: 2026-10-13T23:51:23Z
---

Filed on the Captain's 「開」 (2026-10-14) after an observer read of the spacedock-dev/subspace-relay FO session that delivered PR #362 (task `owner-sees-all-feedback-room`, kc-dev-flow-2 0.22.0). The FO never ran `pr_watch.py` for the PR and ran `merge guard` with no observer step and no learn. Both rules were in the adopter README, but FO read it in `sed -n` ranges up to line 480; `## Delivery authority` starts at line 492 and `## Extensions` at 538. The Captain asked whether the README is too long and whether to split or index it; the direction he approved is a mod keyed to Spacedock's lifecycle points rather than a longer README or read-sized slices.

## Scope

- Spacedock 0.27 already provides the index: mods in `{workflow_dir}/_mods/` with `## Hook: startup`, `## Hook: idle` and `## Hook: merge`, opened only at that lifecycle point and run alphabetically by filename (first-officer shared core, "Mod Hook Convention"). Adopters carry Spacedock's own `_mods/pr-merge.md`, copied unchanged; its `startup`/`idle` hooks handle a MERGED PR (sentinel, then `merge guard`) and its `merge` hook handles the PR at terminal approval.
- Candidate contents of a kc-dev-flow-2 mod:
  - `merge` (approved, before the merge ask): mark ready, wait for the post-ready Codex run, check the head against the validated candidate, `delivery_gate.py`, `pr_watch.py add`, then the merge ask.
  - `idle`: every open task PR has a `pr_watch.py wait` running in the background, else start it; advance an open learning delivery.
  - `idle`/`startup` on a MERGED PR, before the sentinel: `observer_check.py`, dispatching and saving the observer when absent.
  - after the archive: learn, with its notice and the observer report presented together.
  - `startup`: unread learn notices and open learning deliveries.
- Ordering: the observer step must run before `pr-merge`'s sentinel, so the mod's filename must sort before `pr-merge.md`; learn runs after the archive (a later pass, or a second file that sorts after it).
- The README keeps the rules as the authority and points to the mod; the FO steps moved out are expected to lower `WORKFLOW_WORD_BUDGET` (`## Delivery authority` 546 words, `## Extensions` 222 at origin/main 656543f4). How much moves is ideation's count.
- Dispatch-time rules (scope-notes lines, extension worker instructions) have no hook point and stay with script checks: tasks `followup-dispatch-records-checked` and `extension-instruction-reaches-dispatch`.
- Spacedock is not changed (the Captain's ruling); `pr-merge.md` stays an unchanged copy.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation. The proof owed is a replay of the relay #362 situation showing FO starts `pr_watch` and runs the observer and learn at the right moments with the mod, and does not without it.

## FO alignment

Alignment: needed at ideation: the design changes what FO loads at three lifecycle points across every adopter.
Result: direction aligned with the Captain in chat on 2026-10-14, before filing. He asked whether the README is too long and whether to split it, index it, or chain read-sized slices with a hook index; FO answered that the reading length was not the cause (the relay FO chose `sed -n` ranges) and proposed a kc-dev-flow-2 mod on Spacedock's existing `startup`/`idle`/`merge` hook points, with the step list per point; he approved filing it (「開」) and scheduling it (「ok」). No research request; Spacedock is not changed.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none

## Stage Report: ideation

- FAILED: A design (PRFAQ and Mermaid) for a kc-dev-flow-2 Spacedock mod with `## Hook: merge`, `## Hook: idle` and `## Hook: startup` sections (per-step placement, mod filename and order against `_mods/pr-merge.md`, learn relative to archive, README authority and counted word budget, adopter sync)
  Not started: held. `## FO alignment` records "Alignment: needed at ideation" and the task file has no `Result:` line (`grep -n "Result:"` finds none); `skills/ideation/principles.md` says to stop and report in that case, and README `### ideation` requires the `Result:` line before the worker is dispatched.
- FAILED: Acceptance criteria with reproducible evidence clauses and falsifiers, including a replay of the relay PR #362 situation with and without the mod
  Not started: held for the same reason; no `## Acceptance criteria` section was written.
- FAILED: Unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  Not started: held for the same reason.

### Summary

Held before design: the alignment need is recorded without its result, and ideation principles make that a stop, not something the worker may fill from the dispatch notes. Nothing was designed, no repository file was touched, and no other session or PR was contacted. To release the hold, FO adds a `Result:` line under `## FO alignment` (or records that the backlog approval and dispatch scope notes are the alignment) and re-dispatches ideation.
