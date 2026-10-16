---
title: An activated extension's worker instruction reaches the dispatch only if FO remembers it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:extension-instruction-reaches-dispatch:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:extension-instruction-reaches-dispatch-backlog-1
              briefing:
                id: briefing:extension-instruction-reaches-dispatch:backlog:attempt-1:revision-1
                digest: sha256:cef06b799a2387bc3f780618d3fab4f0d79a60ff765e7814c0486dcd90b9e1e2
                room-ref: ./extension-instruction-reaches-dispatch/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:extension-instruction-reaches-dispatch:backlog:1
                briefing: briefing:extension-instruction-reaches-dispatch:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-16T03:13:38.852018Z"
                decision: approve
                reason: 'Captain approved batch 1 (「批准」): schedule as Pilot and enter ideation; as the gate question states, this accepts profile pilot and five parallel ideations with dev2-laws-check''s design read by the other four for overlap.'
              application:
                target-stage: ideation
                state: consumed
---

Filed from a package issue reported by the spacedock-dev/subspace-relay First Officer; the Captain confirmed filing on 2026-10-14 (「確認」 to "should FO file relay #1 and #4?"). Relay task `owner-sees-all-feedback-room` (PR spacedock-dev/subspace-relay#362, kc-dev-flow-2 0.22.0) dispatched implementation without the roborev extension's worker instruction, so the worker never ran `roborev_gate.py` and its report has no `evidence=` line; FO ran the gate afterwards (roborev:633).

## Scope

- The gap is enforcement: `extensions/roborev/EXTENSION.md` names an "Instruction FO adds to the scope notes", but `spacedock dispatch build` does not read the README's `extensions:` list and the workflow README text never names roborev (checked 2026-10-14: no `roborev` match in `references/sd/workflow.md` at origin/main 656543f4). Dispatch time has no Spacedock mod hook point, so a script check is the candidate route.
- Candidate fix: `dispatch_records.py` fails a dispatch record of a stage whose activated extension declares a worker instruction when that instruction is absent from its scope notes; or the README's stage text names it. Which extensions declare one (roborev; codex and copilot to be checked) is for ideation.
- Related: task `followup-dispatch-records-checked` changes the same script.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain confirmed filing it.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
