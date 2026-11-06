---
title: An ADR number reserved by one workflow's task is seen by every workflow that writes ADRs to the same repository
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:adr-reservation-crosses-workflows:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:adr-reservation-crosses-workflows-backlog-1
              briefing:
                id: briefing:adr-reservation-crosses-workflows:backlog:attempt-1:revision-1
                digest: sha256:a0e8f7cd5d68fc975264a67629540905c78807ec5580084c5fdc875405e2d4d2
                room-ref: ./adr-reservation-crosses-workflows/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-reservation-crosses-workflows:backlog:1
                briefing: briefing:adr-reservation-crosses-workflows:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-06T14:28:56.876723Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-06), answering 「決定：第 16 批這五張（跳過的 CI 不擋、Codex 只貼安全摘要時提醒、交付檢查的相對路徑、ADR 編號跨流程預留、婉拒只在出過事時開任務）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？核准即接受「婉拒只在出過事時開任務」任務裡寫的標準（指出真的錯並說得出誰受害、再次出現、或你要求）。要改哪張直接說。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: pending
---

`number_guards.py` refuses a new ADR number that another workflow's live task has already reserved in the same repository, so two FOs sharing a repository cannot both land the same number.

## Scope

- Source: the Captain 「開」 (chat, 2026-11-06), answering FO's batch 14 retrospective ask 「Should I open these two backlog tasks?」, whose first item was this cross-workflow reservation gap.
- Bite: gate-presentation-asks-one-thing-plainly reserved ADR 0060 in this workflow (dispatch 2026-11-05); kc-journey-map #789 (a7c0bdbe0, merged 2026-11-05 23:31 +0800) landed docs/adr/0060 and 0061 from the journey-map private-host workflow; `number_guards.py check --base a7c0bdbe0` then failed R5 on #788, which cost one renumber round (0060 to 0062) and a second validation (FO read of origin/main docs/adr and the #788 worker report, 2026-11-06).
- Upstream first: kc-dev-flow-2 `number_guards.py` (R4/R5, `reserve`), the README's Number guards, ADR-reservation rules; Spacedock has no cross-workflow lock.
- Non-goals: renumbering any landed ADR.

- Batch 16: the Captain 「可以，就這樣」 (chat, 2026-11-06), answering 「這批做 2、3、4、5、9 這 5 張，可以嗎？」, which named this task.

## Budget
- One package PR; the workflow word budget does not rise unless the design names a raise for the Captain.

## Stop condition
- A replay where a second workflow reserves or lands a number another workflow's live task holds is refused before its dispatch or merge ask, and a free number passes.

## FO alignment

Alignment: needed at ideation; where the shared reservation lives is a package design choice for him to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
