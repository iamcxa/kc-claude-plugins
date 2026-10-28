---
title: A follow-up dispatch to a reused worker leaves a dispatch record before it is sent
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:reused-worker-dispatch-leaves-a-record:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:reused-worker-dispatch-leaves-a-record-backlog-1
              briefing:
                id: briefing:reused-worker-dispatch-leaves-a-record:backlog:attempt-1:revision-1
                digest: sha256:9682249dd49b43628e358a80e2df2fc1ef8b35a3a5f9dd97772029e8cf766227
                room-ref: ./reused-worker-dispatch-leaves-a-record/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:reused-worker-dispatch-leaves-a-record:backlog:1
                briefing: briefing:reused-worker-dispatch-leaves-a-record:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-28T05:38:45.589286Z"
                decision: approve
                reason: The Captain 「准」 (chat, 2026-10-28), answering FO's joint batch-9 backlog presentation of five gates whose ask was 「決定：五張全准進入設計階段；要拿掉或換掉哪張，直接說。」; accepts FO's recommendation to enter ideation on the pilot profile.
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain 「照建議」 (chat, 2026-10-27), answering FO's batch-7 retrospective list (items a to d).
- Bite: kc-ops-inbox task ops-metric-event-protocol (PR #727, two rejected validation cycles; its observer report at state commit f25c224f6, relayed by its FO 2026-10-27): no dispatch records for the implementation or validation dispatches sent to reused workers, and the misses that followed (no delivery_gate question before validation briefings 1 and 2, no Override line, polish items left out of FO declines) all sat on that path, where no `dispatch build --stamp` runs and nothing prompts the record. The README already says a follow-up message to a worker FO resumes is a dispatch.
- Upstream first: the README's Stages (follow-up dispatch rule), `scripts/dispatch_records.py`, `scripts/pr_watch.py tasks`, Spacedock `dispatch build`.

## Non-goals

- A change to Spacedock `dispatch build`; recording messages that are not dispatches (a question answered, a status read).

## Budget

- One package PR; extend `scripts/dispatch_records.py`, no new script.

## Stop condition

- The ops-metric-event-protocol path replays as caught (a reused-worker follow-up with no record is named before the next gate) and every current task with records still passes. Return to the Captain if the record can only be enforced inside Spacedock.

## FO alignment

Alignment: needed before ideation; where the check or rule lives is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.


## Stage Report: ideation

- FAILED: A design for where a follow-up dispatch to a reused worker gets its record checked (scripts/dispatch_records.py, scripts/pr_watch.py tasks, or the gate path), replaying kc-ops-inbox ops-metric-event-protocol (PR #727) as caught; read kc-ops-inbox state only through read-only commands
  Hold before design: `## FO alignment` says `Alignment: needed before ideation` but contains no `Result:`; the selected ideation principles explicitly require stopping at this missing input. No replay or adopter-state inspection performed.
- SKIPPED: A `### Batch overlap` section naming each file the design would change and each other batch task (reused-worker-dispatch-leaves-a-record, paseo-codex-dispatch-practice, captain-ruling-sources-checked, batch-reaches-each-gate-together, fo-interviews-extension) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Deferred with design until FO records its required alignment result; no sibling files edited.
- SKIPPED: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  No design authored, so no lifecycle-word comparison claimed.
- FAILED: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  No acceptance criteria authored under the hold; `python3 /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1/scripts/design_surfaces.py check <this-task>` exited 1: `missing '## Acceptance criteria' section`; gate is not presentable.

### Summary

Ideation is held, not completed: the required FO alignment result is absent. Authority: the loaded `skills/ideation/SKILL.md` routes pilot to `skills/ideation/principles.md`, whose opening paragraph says that alignment needed with no `Result:` means “stop and report instead of starting the design”; FO must record its actual alignment result and redispatch. The generated stage definition was read successfully, `git fetch origin` succeeded, and `origin/main:kc-dev-flow-2/.claude-plugin/plugin.json` reports 0.32.1; no GitHub API request, product edit, branch creation, or design/replay claim was made.
