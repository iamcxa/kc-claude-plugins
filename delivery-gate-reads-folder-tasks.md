---
title: delivery_gate.py reads a folder task's index.md
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:delivery-gate-reads-folder-tasks:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:delivery-gate-reads-folder-tasks-backlog-1
              briefing:
                id: briefing:delivery-gate-reads-folder-tasks:backlog:attempt-1:revision-1
                digest: sha256:04ce3fbc310de40dd326f41fe75d711d523c543fe4e2052007e5d609f2ff37cb
                room-ref: ./delivery-gate-reads-folder-tasks/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:delivery-gate-reads-folder-tasks:backlog:1
                briefing: briefing:delivery-gate-reads-folder-tasks:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-25T14:15:31.710779Z"
                decision: approve
                reason: Captain 「全准」 (chat, 2026-10-25) answering the batch-6 backlog sitting, which listed this task's backlog briefing-1 question
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: FO, 2026-10-23, at the release-acceptance merge ask (PR #709). `delivery_gate.py check <task>/index.md` derives the dispatch folder by stripping `.md`, so it looks in `<task>/index/dispatch` and exits 2 ("no latest validation dispatch record"); passing the folder exits 2 ("Is a directory"). FO ran the check through a temporary `<name>.md` copy beside a symlink to the real folder; the record landed in the real `merge/ask-1.json`.
- Outcome: `delivery_gate.py check` accepts a folder task (its `index.md` or the folder) and reads `<task>/dispatch`, with a test.
- Upstream first: none checked yet; check whether other package scripts share the same path derivation before fixing one.
- Non-goals: other scripts' folder support unless they share the helper.
- Batch 6 (2026-10-25): the Captain 「可以」 (chat, 2026-10-25), answering 「需要你決定：這份第 6 批的清單可以嗎？」 about FO's batch-6 list, which placed this task third, after fo-written-lines-checked-before-dispatch (same script), and folded into it merge-check-reads-two-pr-tasks (whether a task may deliver through two PRs stays the Captain's at ideation).

## FO alignment

Alignment: needed at ideation: whether a task may deliver through two PRs (folded merge-check-reads-two-pr-tasks) is the Captain's.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
