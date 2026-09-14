---
title: "dispatch.sh carries worker credentials through workspace create --env, resumes a task in a fresh workspace, and states that gate decisions are the ship FO's"
status: backlog
source: "Captain 2026-09-14 「派」 (ship round 3, harden); findings recorded on spacedock-state/ship questions logs"
product: kc-ship-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r3
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: 0dg522wbqd0jpd2jeg8tjq4m
gates:
    version: 1
    records:
        - id: gate:0dg522wbqd0jpd2jeg8tjq4m:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:0dg522wbqd0jpd2jeg8tjq4m-backlog-1
              briefing:
                id: briefing:0dg522wbqd0jpd2jeg8tjq4m:backlog:attempt-1:revision-1
                digest: sha256:123bc52ade833c094732c26402df63137aa3a2d58d2bfcfa9c6bfa68a4cbc9a7
                room-ref: ./ship-dispatch-env-file-resume-and-gate-authority/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:0dg522wbqd0jpd2jeg8tjq4m:backlog:1
                briefing: briefing:0dg522wbqd0jpd2jeg8tjq4m:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-14T10:49:39.747782925Z"
                decision: approve
                reason: 'Backlog admission criteria met: title/product/source/sprint/sprint-readiness=ready present, 5-item Accepted outcome is the required brief, profile=pilot recommended and consistent with kernel admission (harden round on an already-shipped tool).'
                conn:
                    quote: 准
                    source: Captain 2026-09-14 batch approval, r3 batch of five tasks under the pilot profile
              application:
                target-stage: ideation
                state: pending
---

On 2026-09-14 (qnow `qnow-clerk-poc`, DEV-146) the Captain provisioned Clerk keys mid-task. Conductor CLI 0.85.0 accepts environment variables only at `conductor workspace create --env KEY=VALUE` (repeatable); `session create` has none and an existing workspace cannot take new ones. The ship FO had to create a second workspace by hand from the task's branch with a hand-written resume boot, because `dispatch.sh` 0.2.0 has no credential surface and no resume mode. On 2026-09-11 (`ship-dispatch-watch-round-2`, task 7z) the Captain's chat approval and the worker's conn-delegated record collided on one gate attempt; today's batch proved the rule that holds: the ship FO records with the Captain's words, workers sync state by merge (never rebase) and never record.

## Accepted outcome

1. `dispatch.sh` accepts `--env-file <path>` (KEY=VALUE lines; values are read into the `conductor workspace create` argv as repeatable `--env` and never printed, logged, or written to the fence; the fence records only the key names) and refuses a file that is world-readable.
2. `dispatch.sh --resume <slug>` creates a fresh workspace from the task's existing branch (read from the entity or the fence), sends a resume boot that names the entity status, gate attempt, PR and candidate SHA, and records the new workspace/session in the fence under the slug with the previous ids kept (`r1`, `r2`, …); the previous workspace is archived only after the new one reports ready.
3. The boot header carries, verbatim: "Gate decisions are recorded by the ship first officer with the Captain's words. Sync state by merge, never rebase. Never record a gate decision." (replacing the r2 wording).
4. `pins/conductor-cli.contract` covers the `--env` and `--branch` shapes; the read-only probes stay as they are.
5. Rehearsal: a `--dry-run` of both modes prints the create command with `--env KEY=***`.

Profile recommendation: pilot.
