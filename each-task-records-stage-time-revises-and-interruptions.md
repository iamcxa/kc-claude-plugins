---
title: Every task records its time per stage, its revise count and its interruption count, and a helper reads them out
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:each-task-records-stage-time-revises-and-interruptions:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:each-task-records-stage-time-revises-and-interruptions-backlog-1
              briefing:
                id: briefing:each-task-records-stage-time-revises-and-interruptions:backlog:attempt-1:revision-1
                digest: sha256:34a62b970da873e147a12ba0bb7b6c7b26551529acdc7259ff6e670129ab6f69
                room-ref: ./each-task-records-stage-time-revises-and-interruptions/review/backlog/briefing-1
---

## Scope

- Source: the Captain 「prod 應該要縝密沒有問題的，但是不管哪個 profile 都必須明確加入計時機制，要可以追溯每個 stage 的時間，revise 次數，打斷次數，以便改進整個 agentic DX」 (chat with FO session 3, 2026-11-12); earlier 「如果可行，應該要搭配一套 lint + helper 工具記錄時間，判準，取出時間」 and 「而且你沒記錄時間現在看來是一個非常大的問題」 (same chat, 2026-11-11).
- Bite (FO, 2026-11-11 and 2026-11-12): FO could not say how long PR #849 took per stage without reading commit times by hand; a two-week measurement could match agent sessions to tasks for 3 of 10 sampled tasks and could not count interruptions at all, because none is recorded.
- What exists (study of 2026-11-12, FO's local notes, not verified line by line): Spacedock stamps started, completed and archived once per task and each gate decision, not when a gate was opened; kc-dev-flow version 1's POC close guard recorded decision-ready seconds, Captain interventions and Captain wait; a Codex First Officer keeps a per-task time file by hand; state commit times give stage times after the fact.
- Outcome: for any task, one command prints each stage's start and end, agent time against waiting where the source allows, the number of repeat dispatches per stage, and the number of questions put to the Captain outside the task's scheduled gates, from records written at the time.
- Open for the design: the definition of a revise and of an interruption that can be counted; what must be newly recorded and by whom; the time source on Claude and on Codex; whether a check refuses a task with missing records or only reports.
- Non-goals: a time or minutes budget that holds work (ADR 0077 says minutes are not counted); cost in money or tokens; dashboards.

## Budget
1 cycle per stage, in one package PR.

## Stop condition
- The command, run on three tasks finished after the change, prints the same stage times FO kept by hand for them within five minutes each, and the counts match FO's hand tally. Return to the Captain if a reliable time source does not exist on one host.

## FO alignment

Alignment: not needed: the Captain's words under Source name the three quantities and that every profile carries them; definitions are compared in the design and ruled at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
