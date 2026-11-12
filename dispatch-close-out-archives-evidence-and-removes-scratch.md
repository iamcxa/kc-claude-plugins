---
title: When a dispatch closes, its necessary evidence is archived compressed and its removable scratch is deleted
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:dispatch-close-out-archives-evidence-and-removes-scratch:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:dispatch-close-out-archives-evidence-and-removes-scratch-backlog-1
              briefing:
                id: briefing:dispatch-close-out-archives-evidence-and-removes-scratch:backlog:attempt-1:revision-1
                digest: sha256:385f8a76e9972e37f5d2d3227b89582f45e161d19cf571788289a44b509b42ec
                room-ref: ./dispatch-close-out-archives-evidence-and-removes-scratch/review/backlog/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-11-12T05:11:39.090063Z"
                reason: The Captain answered the joint question with a change to the experiment instead of a decision (host question dialog, 2026-11-12); FO asks again with the experiment written into the question.
            - id: gate-attempt:dispatch-close-out-archives-evidence-and-removes-scratch-backlog-2
              briefing:
                id: briefing:dispatch-close-out-archives-evidence-and-removes-scratch:backlog:attempt-2:revision-1
                digest: sha256:26fa43c8e6d66c114da66525c5c343ed33b1d75f1de9f9a85e1e1b876e0f26b5
                room-ref: ./dispatch-close-out-archives-evidence-and-removes-scratch/review/backlog/briefing-2
---

## Scope

- Source: the Captain 「把派工結束收尾清理要刪除過程產生的可移除檔案，以及把必要證據壓縮封存到派工分支中紀錄成故事，下一批要做，目前這樣都沒人刪檔很困擾」 (chat with FO session 3, 2026-11-11); earlier that day 「都刪除，且要找出為何完工了卻沒清理的原因？等於完工一定要清理」.
- Bite (FO measured 2026-11-11): free disk fell to 5.6 Gi; single finished tasks left 3.6 G and 4.3 G under /tmp, and a shared scratch folder held 17 G of which about 12 G belonged to archived tasks. Cause FO found: no step and no owner removes scratch; validation dispatches tell workers to export candidates under /tmp; workers kept /tmp copies "as supporting evidence"; FO's close-out removed only the git worktree.
- Interim practice since 2026-11-11, by hand: each dispatch asks the worker to remove its own scratch by exact path and list it; FO removes the rest at archive.
- Outcome: at close-out, evidence a later reader needs is in the task's records in compressed form and can be restored, and every scratch path the dispatch created is gone, with a record of what was removed.
- Open for the design: what "派工分支" means per stage, given that the state branch is public; what counts as necessary evidence and its size limit; who removes what and when (worker at report, FO at archive); how a removed path is told from missing evidence by the delivery check.
- Non-goals: cleaning other sessions' or other repositories' scratch; a retention policy for git branches.

## Budget
1 cycle per stage, in one package PR.

## Stop condition
- One real task run after the change ends with no path it created left under /tmp, its evidence restorable from the archive by the documented command, and the delivery check passing. Return to the Captain if evidence that must stay private cannot be kept off the public state branch.

## FO alignment

Alignment: not needed: the Captain's words under Source name the outcome; where the archive lives is compared in the design and ruled at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
