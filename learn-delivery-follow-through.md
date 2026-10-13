---
title: The learn loop carries its learning.md PR to a recorded merge or close
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:learn-delivery-follow-through:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:learn-delivery-follow-through-backlog-1
              briefing:
                id: briefing:learn-delivery-follow-through:backlog:attempt-1:revision-1
                digest: sha256:ae5d4d75c6df6e5983014325ab604b45c42a07f785eafd52ec5ca129c87c5057
                room-ref: ./learn-delivery-follow-through/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:learn-delivery-follow-through:backlog:1
                briefing: briefing:learn-delivery-follow-through:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-13T10:57:32.271196Z"
                decision: approve
                reason: 'Captain 2026-10-13: 「開」 to the backlog gate question "Schedule now as Pilot and enter ideation, learn-delivery-follow-through first, then fo-record-checks?", after 「向 kc-dev-flow-2 回報的問題可以回報，這個是否可以排進清單處理修復跟補強？」; profile pilot selected.'
              application:
                target-stage: ideation
                state: pending
---

`kc-dev-flow-2:learn` (0.21.0 and 0.22.0, `skills/learn/SKILL.md`) creates the learning.md PR with `gh pr create --draft` and records the observation at creation, then stops. It names no step to mark the PR ready once CI is green, no `pr_watch.py add`, and no step to record the later merge or close. On 2026-10-13 FO asked the Captain to merge learning PR iamcxa/kc-claude-plugins#637 while it was still a Draft, and recorded its merge only after the Captain said it had merged. Until a delivery is recorded merged, closed or released, `learning.py claim` refuses every new learning job in the store, so the next task's learn step stalls. The workflow README's Delivery authority (ready after CI green, `pr_watch.py add`) covers task PRs, not learn's PR.

## Captain's words

Captain 2026-10-13, in chat: 「如果建議我合併的 PR應該要設成 ready，這是 dev2 缺陷嗎？你應該也要主動追蹤他的合併狀態，還是是 learn 的流程沒補強到？」, then 「向 kc-dev-flow-2 回報的問題可以回報，這個是否可以排進清單處理修復跟補強？」

## Scope

- learn's delivery: mark the PR ready once CI is green before asking for merge, add it to `pr_watch.py`, and record the merged or closed observation when the watch reports it.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain asked for the fix.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
