---
title: dispatch_records.py says what it did not check, and refuses a relative package script path
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:names-check-says-what-it-skipped:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:names-check-says-what-it-skipped-backlog-1
              briefing:
                id: briefing:names-check-says-what-it-skipped:backlog:attempt-1:revision-1
                digest: sha256:673bdc90c43332620087320fb379e5e83b5682f54cc8b4fd1228991d4159f7a6
                room-ref: ./names-check-says-what-it-skipped/review/backlog/briefing-1
---

## Scope

- Source: batch-10 learn list presented to the Captain (chat, 2026-10-30) as package candidates, proposed by FO; no ruling yet.
- Bite: batch 9: FO's scripts ran `--names` on a record copy under /tmp, where task-fact checks skip and it exits 0, so three ideation dispatches went out with no Result: line (reproduced 2026-10-29: exit 0 on the copy, exit 1 in the task folder). Batch 10: FO's checklists named package scripts as kc-dev-flow-2/scripts/NAME.py, which `--names` passes though the README requires the absolute package path (captain-amendment-form-checked observer report).
- Upstream first: `scripts/dispatch_records.py` (`--names`, `check_task_facts`), README Stages (the script-path sentence). Open for ideation: how a checklist names a repository file the worker edits, as opposed to a script it runs.

## Non-goals

- Changing what the task-fact checks refuse.

## Budget

- One package PR inside `scripts/dispatch_records.py`; no new script.

## Stop condition

- A record outside a task folder no longer exits 0 silently, the relative form is refused or ruled allowed, and every current in-folder record keeps its verdict.

## FO alignment

Alignment: not needed before ideation: closes a silent pass in an existing check.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
