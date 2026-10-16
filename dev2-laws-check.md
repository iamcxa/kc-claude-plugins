---
title: A dev2 laws file whose invariants a script checks over the committed state history
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:dev2-laws-check:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:dev2-laws-check-backlog-1
              briefing:
                id: briefing:dev2-laws-check:backlog:attempt-1:revision-1
                digest: sha256:128e6b9bbe1ce5ef45e08615dbc9f571a061845d1056e74b50353b38f787cecc
                room-ref: ./dev2-laws-check/review/backlog/briefing-1
---

Filed on the Captain's 「同意兩件」 (2026-10-14), after FO compared Bend 2's `LAWS.bend` idea (invariants a checker proves the program keeps) with dev2's failures that day. Those failures were at the layer where FO follows text: a relay FO archived a task without an observer report, FO built dispatches before running `dispatch_records.py --names`, and FO answered a chat cue without running Spacedock's hooks. The scripts themselves were not wrong.

## Scope

- One file listing dev2 invariants, each checked by a script against the committed `spacedock-state` history, for example: no `pr: pr-merge:N` sentinel without a committed `observer.md` where `learn` is listed; every dispatch record carries an absolute `Package root:` line; the head a delivery gate question names equals the latest passing validation report's candidate.
- Existing checks that are already such laws and would join the list: `observer_check.py`, `dispatch_records.py`, `delivery_gate.py`, `design_surfaces.py check`.
- A run point that does not depend on FO remembering it: candidate is CI on each push to the state branch; which run point is for ideation.
- Observer rules read today as `can't tell` are candidates to become laws (task `chat-only-evidence-observer-blind`).
- No Spacedock change; Python, no new language.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
