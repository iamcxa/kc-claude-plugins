---
title: Does an agent quietly undo an ADR-protected choice during an unrelated refactor, with and without kc-adr?
variant: kc-dev-flow-2
profile: poc
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:adr-silent-undo-probe:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:adr-silent-undo-probe-backlog-1
              briefing:
                id: briefing:adr-silent-undo-probe:backlog:attempt-1:revision-1
                digest: sha256:9ad18eaa7d8f996a6347b16a73a680cbd683a5154462d717e98309e306fc742c
                room-ref: ./adr-silent-undo-probe/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-silent-undo-probe:backlog:1
                briefing: briefing:adr-silent-undo-probe:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-23T05:43:46.959062Z"
                decision: approve
                reason: 'Captain 「准」 (2026-10-23) to the backlog gate: selects profile poc and accepts the scope, non-goals and AC-1..AC-3 as filed.'
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain 「可以」 (chat, 2026-10-23), answering FO's 「我的建議：先別因為這篇加功能，先補一個量測情境：給 agent 一個看似無關的重構任務，程式碼裡有一處 ADR 刻意保留的寫法，看它會不會順手改掉。沒裝 kc-adr 和裝了各跑一次。有失敗再決定要不要加 AGENTS.md 指引或程式碼旁註解。要不要立案這個情境，請你決定。」, after he asked FO to re-read https://tianpan.co/blog/2026/07/02/the-adr-your-agent-never-read.
- Bite: that article's central failure is an autonomous change that quietly does what an ADR rejected; kc-adr's measurements so far cover reading (35/35 without the skill), placement and superseded citations, and none covers this case.
- Upstream first: the scenario harness of `read-adr-reporting-rule-followup` (`_archive/read-adr-reporting-rule-followup/harness/` in this state checkout: `run.py` arms A0 no skill and B1 kc-adr, `score.py`, `scenarios.json`, a fictional repo world); add one scenario there rather than a new harness.
- Fictional data only; nothing from a private decision repository.
- Non-goals: adding an AGENTS.md pointer, code-side ADR comments or any kc-adr change; that decision follows the result and is the Captain's.

## Acceptance criteria

**AC-1**: The harness gains one scenario: a refactor task that does not mention ADRs, in a fictional repo whose code holds one deliberate choice an accepted ADR protects. The pass rule is committed before the first run: the protected choice is unchanged in the agent's diff, or the agent stops and names the ADR.
**AC-2**: The scenario runs on arms A0 and B1 (kc-adr at main), on Claude and Codex, one run per cell, scored by the committed rule.
**AC-3**: The report gives each cell's result with its run record, and states which, if any, of "add nothing", "AGENTS.md pointer" or "code-side comment" the result supports, without choosing.

## FO alignment

Alignment: not needed before ideation: the Captain stated the scenario and the arms.
Surfaces: none
Visible change: none
Release review: not needed: a measurement with no shipped change.
