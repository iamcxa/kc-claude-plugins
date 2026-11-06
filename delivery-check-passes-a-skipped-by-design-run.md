---
title: delivery_gate.py check does not hold on a workflow run skipped by design
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:delivery-check-passes-a-skipped-by-design-run:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:delivery-check-passes-a-skipped-by-design-run-backlog-1
              briefing:
                id: briefing:delivery-check-passes-a-skipped-by-design-run:backlog:attempt-1:revision-1
                digest: sha256:7c0597c313a651f965eef34859be7ed0867804870b15a4e8c24191cf201f2f25
                room-ref: ./delivery-check-passes-a-skipped-by-design-run/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:delivery-check-passes-a-skipped-by-design-run:backlog:1
                briefing: briefing:delivery-check-passes-a-skipped-by-design-run:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-06T14:28:23.458368Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-06), answering 「決定：第 16 批這五張（跳過的 CI 不擋、Codex 只貼安全摘要時提醒、交付檢查的相對路徑、ADR 編號跨流程預留、婉拒只在出過事時開任務）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？核准即接受「婉拒只在出過事時開任務」任務裡寫的標準（指出真的錯並說得出誰受害、再次出現、或你要求）。要改哪張直接說。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
---

`delivery_gate.py check` treats a workflow run that its own conditions skip on purpose as no hold, while still holding a failed, pending or unexpectedly skipped required check.

## Scope

- Source: the Captain 「開」 (chat, 2026-11-06), answering 「要開這 4 張嗎？」 after fo-feedback round 005 (.notes/fo-feedback/round-005.md, closed 2026-11-06).
- Bite: qnow: check held #1338 on a by-design skipped "Release Gate" run, and the Captain waived it (「豁免release gate跳過，合併1338」); the qnow FO reports it holds every feature PR (round 005, operator report, not re-run here).
- Upstream first: kc-dev-flow-2 scripts/delivery_gate.py check ("a workflow run on the head is not completed and successful (a skipped run included)").
- Non-goals: changing which checks are required.

- Batch 16: the Captain 「可以，就這樣」 (chat, 2026-11-06), answering 「這批做 2、3、4、5、9 這 5 張，可以嗎？」, which named this task.

## Budget
- One package PR; the workflow word budget does not rise unless the design names a raise for the Captain.

## Stop condition
- A replay of the #1338 check passes the skipped Release Gate run; a required check that fails or stays pending still holds.

## FO alignment

Alignment: needed at ideation; the design choice is his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
