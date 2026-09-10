---
title: "ship-flow POC: verify at the integrated head, one UAT document, worker-written debriefs, and a slim close receipt"
status: backlog
source:
product: kc-ship-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
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
                state: pending
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
