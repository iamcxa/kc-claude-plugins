---
title: What a worker is told about pushing matches what the state commit command does
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:worker-push-words-match-state-commit:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:worker-push-words-match-state-commit-backlog-1
              briefing:
                id: briefing:worker-push-words-match-state-commit:backlog:attempt-1:revision-1
                digest: sha256:dc702b36756f0c9febd73862fb29bc675e8613609d26eecda819aa1778ccb149
                room-ref: ./worker-push-words-match-state-commit/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:worker-push-words-match-state-commit:backlog:1
                briefing: briefing:worker-push-words-match-state-commit:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-11T01:18:48.041651Z"
                decision: approve
                reason: 'The Captain chose 「五張都核准（建議）」 (host question dialog, 2026-11-11), answering 「決定：第 21 批這五張要不要進設計階段。我建議五張都核准：故事做完回報切片進度、發版後鋪開到採用 repo 與法規檢查、超預算要停與重大發現先對照不做清單、工人收到的推送說明與狀態提交工具一致、拒絕一個指令不等於全停。核准代表接受每張任務檔寫的範圍、預算與停止條件，並各派一個設計工人；不代表接受任何設計或修法。前三張標了方向要先對齊，派工前我會各問你一題。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
started: 2026-11-11T01:19:15Z
---

## Scope

- Source: item 2 of a peer report from the qnow dev2 FO (Paseo 519ab4c8, 2026-11-10), which states its Captain approved handing it over (「要」, relayed, not a ruling here).
- Selected for batch 21: the Captain chose 「放 1 到 5（建議）」 (host question dialog, 2026-11-11), answering 「第 21 批要放哪幾張？我建議放清單的 1 到 5：故事做完回報切片進度、發版後鋪開到採用 repo 與法規檢查、超預算要停與重大發現先對照不做清單、狀態提交自動推送與派工單矛盾、拒絕一個指令不等於全停。選完後我只為被選中的建任務檔，再一次請你過待辦關卡；選進來不代表接受任何設計。」.
- Bite (qnow FO's report; the two commits read by FO 2026-11-10): `spacedock state commit` pushes the state branch, while dispatches tell workers not to push. On iamcxa/qnow `spacedock-state/dev2` a validator committed its report in a0d280f3b and 71 seconds later amended it in ee7a248ab ("state: record validation helper publication") to disclose a publication it had not intended. That amendment then tripped `rewritten-report` in kc-dev-flow-2 0.38.0, fixed for that shape in 0.38.1 (PR #834).
- Same class in this workflow (the retiring FO's handoff note of 2026-11-10, not re-run): Codex workers under auto-review stopped at the state push with "internal reports need explicit publication approval", and one asked the Captain with a UI button.
- FO's own dispatch text (this FO's helper, 2026-11-11) says both "do not push the product branch" and "the state-branch push that `spacedock state commit` makes is expected and allowed", in the validation dispatch only.
- Non-goals: changing Spacedock's state commit; the 0.38.1 rewrite rule.

## Budget
- One package PR to the worker-facing words (stage skills or the workflow reference), with the documented-invocation test if a command line changes.

## Stop condition
- A replayed implementation and validation dispatch at the candidate each state which push is the worker's and which is not, and a worker run on each reports its state commit without calling it an unintended publication; or the design shows why not and says what was learned.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it and the direction is to make two existing statements agree.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
