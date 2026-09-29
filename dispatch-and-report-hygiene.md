---
title: Dispatches name the reachable FO, the package's script paths and the secret wrapper, and a report never ends in a false FAILED line
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:dispatch-and-report-hygiene:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:dispatch-and-report-hygiene-backlog-1
              briefing:
                id: briefing:dispatch-and-report-hygiene:backlog:attempt-1:revision-1
                digest: sha256:3d7eb68063e7caa0a0a5ba0193029cb4e98dcee67ba791fbd0c188aa4d0b24d8
                room-ref: ./dispatch-and-report-hygiene/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:dispatch-and-report-hygiene:backlog:1
                briefing: briefing:dispatch-and-report-hygiene:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-29T23:28:24.783586Z"
                decision: approve
                reason: 'Captain 2026-09-30: 「可以」 to the FO''s dev2 fix batching, batch A first'
              application:
                target-stage: ideation
                state: consumed
---

Four dispatch and report defects from qnow dogfooding (2026-09-28..30) that cost retries or leaked secrets.

## Scope

Captain 2026-09-30, approving the FO's batching of the dev2 fixes: 「可以」 — batch A (guardrails) first. This task covers issues #526, #527, #528 and #530.
Evidence (qnow): every worker reported "team-lead was unreachable, sent to main"; a report line "- FAILED: none." blocked `spacedock status --set`; one worker searched the whole filesystem for comment_ratio.py for about three hours; two workers printed the Clerk development secret key despite dispatch-note bans, and a user-level PreToolUse(Bash) guard (block Netlify environment and database API reads, 1Password value reads and reveals, Keychain password reads) has held since.
Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Needed at ideation: the name the runtime actually exposes for the dispatching FO; how every dispatch carries the absolute scripts directory of the installed package version; the report-template rule that FAILED marks only an unmet item; and whether kc-dev-flow-2 ships the secret guard for adopters or documents it, plus how dispatches name one run-time secret wrapper.
Result: the FO delegates these questions to ideation, which decides each with its source and returns any ruling that needs the Captain.
Surfaces: none
Visible change: none
