---
title: The observer lists each merge in its window that no task's saved merge ask carries
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:observer-lists-unasked-merges:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:observer-lists-unasked-merges-backlog-1
              briefing:
                id: briefing:observer-lists-unasked-merges:backlog:attempt-1:revision-1
                digest: sha256:b2ad9cdc9bcf9da7256f7fca7df2c3bc48c1fea883b4a455111ee7047d5de06a
                room-ref: ./observer-lists-unasked-merges/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:observer-lists-unasked-merges:backlog:1
                briefing: briefing:observer-lists-unasked-merges:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-07T08:09:36.024308Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-07), answering 「決定：第 17 批這五張（Paseo 瀏覽器當工人驗收的預設、決策紀錄檢查分清驗證取代與指向依據、派工時自動寫派工紀錄、沒給範圍時設計檢查說沒跑、觀察者列出沒有合併提問紀錄的合併）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？建議核准。要改哪張直接說。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
---

At archive, the observer reports every PR merged in its window whose number and merged head match no saved `merge/ask-N.json` in any state checkout it can read, so an unasked merge is found after the fact without a pre-tool hook.

## Scope

- Source: the Captain 「可以」 (chat, 2026-11-06), answering FO's 「要照這樣做嗎？」, which proposed keeping merge-guard-stops-unasked-merges held and doing first the cheaper after-the-fact check and a look at whether #785 and #727 were asked.
- Bite: fo-feedback round 005 (2026-11-06): journey-map PR #785 merged 2026-11-05 while its task still reads `status: backlog` with no gate decision (FO read of that state file); ops-inbox PR #727 merged 2026-10-27 with the Captain's 「准」 recorded (FO read of its archived gate, 2026-11-06) but with Codex's code review only on an earlier commit. The held merge-guard replay counts (54/30, then 74/10) stay in its task file.
- Added 2026-11-06 (journey-map FO reply, Paseo 7b9a9beb, operator statement): #785 was asked; the Captain answered 「Ａ可以，我覺得配對流程不是很順，應該參考 relay 的做法，但可以先合併再重構」 to a question ending 「要合 #785 就說合併」 in the journey-map FO's session on 2026-11-05, and the FO then ran `gh stack merge 785 --squash`. The wording is in that session's transcript only, not in task state. So neither #785 nor #727 was an unasked merge; both are record gaps (no gate record; no code review on the merged head). An audit that flags "no ask record" would list #785 although the Captain approved it, so the design must say how a chat-only approval is told apart from an unasked merge, or the task's value is in surfacing record gaps.
- Upstream first: the merge-guard task's record discovery (state worktrees on `spacedock-state/*`, `*/merge/ask-*.json`); the observer skill; delivery_gate.py's saved ask records.
- Non-goals: blocking any merge; Release, workflow-sync and learning PRs, which carry no task ask (the observer names them as such instead of as violations).

## Budget
- One package PR; the workflow word budget does not rise unless the design names a raise for the Captain.

## Stop condition
- A replay over the window that holds #785 lists #785 as merged with no ask record, lists a task PR with a matching record as carried, and names Release and sync PRs separately.

## FO alignment

Alignment: needed at ideation; which state checkouts the observer reads and how a Release PR is named are his to accept.
Result: aligned at backlog: Batch 17 backlog sitting, the Captain 「核准（建議）」 (host question dialog, 2026-11-07), answering 「決定：第 17 批這五張（Paseo 瀏覽器當工人驗收的預設、決策紀錄檢查分清驗證取代與指向依據、派工時自動寫派工紀錄、沒給範圍時設計檢查說沒跑、觀察者列出沒有合併提問紀錄的合併）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？建議核准。要改哪張直接說。」, approved the outcome and bounds in this file; the design choice the Alignment line names stays his at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
