---
title: Diagnosis rounds on one symptom count toward the step back
status: ideation
variant: kc-dev-flow-2
gates:
    version: 1
    records:
        - id: gate:diagnosis-rounds-count-toward-step-back:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:diagnosis-rounds-count-toward-step-back-backlog-1
              briefing:
                id: briefing:diagnosis-rounds-count-toward-step-back:backlog:attempt-1:revision-1
                digest: sha256:2f1bf4de795fa1ef5f6c5c6a210df8e2a138270466f031373fa925a32549279f
                room-ref: ./diagnosis-rounds-count-toward-step-back/review/backlog/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-11-03T07:39:00.446123Z"
                reason: The Captain widened the batch 13 sitting to seven tasks (chat, 2026-11-03); the bound question named four.
            - id: gate-attempt:diagnosis-rounds-count-toward-step-back-backlog-2
              briefing:
                id: briefing:diagnosis-rounds-count-toward-step-back:backlog:attempt-2:revision-1
                digest: sha256:0dc4d82e27a0cb325611c5e1b7795119a251282a6259cc481217ce51ff653c43
                room-ref: ./diagnosis-rounds-count-toward-step-back/review/backlog/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:diagnosis-rounds-count-toward-step-back:backlog:2
                briefing: briefing:diagnosis-rounds-count-toward-step-back:backlog:attempt-2:revision-1
                by: person:captain
                at: "2026-11-03T07:44:30.807123Z"
                decision: approve
                reason: The Captain 「進」 (chat, 2026-11-03), answering the batch 13 sitting 「決定：這批七張（A 權限、B 同症狀計數、C 改寫條件比對原話、D release 驗收不在正式站、來源標註、FO 先自己試、release 驗收到期提醒）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構思嗎？要改哪張直接說。」; approves Pilot, these outcomes and bounds.
              application:
                target-stage: ideation
                state: consumed
---

## Scope
- Source: Batch 13 sitting, the Captain, chat 2026-11-03: 「ABC 都開，不屬於套件的本身也要討論一下」, answering 「決定：A、B、C 三個都開成 dev2 任務，跟 #768 一起發版嗎？要刪哪個直接說。」; and 「先不合併，我想要把這些也評估修復後，再一起發版」 about Release PR #768. FO had proposed it as 「診斷回合要按『同一個症狀』累計」.
- Outcome: repeated diagnosis rounds on the same symptom inside one stage reach the step-back questions, the way a second failed validation or a second replacing amendment already does.
- Gap: the step-back reminder from PR #766 counts failed validations and replacing amendments only; rounds inside one validation do not count. The global circuit breaker counts per approach, not per symptom.
- Bite: the agent-observatory report on the qnow FO, 2026-11-03 (sampled, not yet checked against the source). One mobile-width freeze was chased through more than six browser runs from 2026-10-30 17:58 to 21:05, and stopped only when the Captain tried it by hand and it did not reproduce.
- Consumer: every adopter FO and its validation workers, through the reminder that `role_triggers.py` already prints.
- Upstream first: `scripts/role_triggers.py` and its step-back counts, `scripts/pr_watch.py`, ADR 0026.

## Non-goals
- Grading the answers; counting rounds across different symptoms; a new stage or tool.

## Budget
- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## FO alignment
Alignment: needed before ideation; the scope is the Captain's ruling and the evidence is an observatory sample, which ideation must check against its source first.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Stop condition
- A replay shaped like the qnow freeze prints the step-back reminder at the second diagnosis round on the same symptom; rounds on different symptoms print none.
