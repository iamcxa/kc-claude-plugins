---
title: After a release, adopters' workflow READMEs and the state laws check are brought to it by a named step, and a repository left behind is reported
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:release-rollout-reaches-adopters-and-laws-pin:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:release-rollout-reaches-adopters-and-laws-pin-backlog-1
              briefing:
                id: briefing:release-rollout-reaches-adopters-and-laws-pin:backlog:attempt-1:revision-1
                digest: sha256:b8934f759c9b6a5fe38bbb047c32c266b198d455619c43d52f73c1b9ab54bd03
                room-ref: ./release-rollout-reaches-adopters-and-laws-pin/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:release-rollout-reaches-adopters-and-laws-pin:backlog:1
                briefing: briefing:release-rollout-reaches-adopters-and-laws-pin:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-11T01:18:34.32566Z"
                decision: approve
                reason: 'The Captain chose 「五張都核准（建議）」 (host question dialog, 2026-11-11), answering 「決定：第 21 批這五張要不要進設計階段。我建議五張都核准：故事做完回報切片進度、發版後鋪開到採用 repo 與法規檢查、超預算要停與重大發現先對照不做清單、工人收到的推送說明與狀態提交工具一致、拒絕一個指令不等於全停。核准代表接受每張任務檔寫的範圍、預算與停止條件，並各派一個設計工人；不代表接受任何設計或修法。前三張標了方向要先對齊，派工前我會各問你一題。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain 「也派工去其他採用的 repo 升級到最新版，此外說明這個法規升級是怎樣，之前好幾個版本都沒做，是否採用的 repo 也都沒升級？」 and 「說明法規如果安裝到每個repo會改變什麼？為何不是預設安裝？」 (chat with this FO, 2026-11-10).
- Selected for batch 21: the Captain chose 「放 1 到 5（建議）」 (host question dialog, 2026-11-11), answering 「第 21 批要放哪幾張？我建議放清單的 1 到 5：故事做完回報切片進度、發版後鋪開到採用 repo 與法規檢查、超預算要停與重大發現先對照不做清單、狀態提交自動推送與派工單矛盾、拒絕一個指令不等於全停。選完後我只為被選中的建任務檔，再一次請你過待辦關卡；選進來不代表接受任何設計。」.
- Bite (FO read at each source, 2026-11-10): this repository's `.github/workflows/dev2-laws.yml` on `spacedock-state/dev2` pinned the kc-dev-flow-2-v0.26.0 tag commit while the package reached 0.38.0, with six commits to `scripts/laws_check.py` in between that never ran hosted; nothing reported it. On the trunks, qnow's workflow README was at 0.37.0 and me-company, subspace-relay, subspace-web and subspace-v0 at 0.35.0; none of the five state branches held the laws workflow. The sync was done by hand that day (kc-claude-plugins PR #833, qnow #1350, relay #498, web #240, v0 #98, me-company #22) from prompts FO keeps outside the package.
- Package fact (kc-dev-flow-2 0.38.1 references/sd/adoption.md, "State laws check"): "Roll it out once per adopter, on the Captain's word"; it names no step after a later release, and states as not verified "the minutes a private adopter pays per run".
- Trial in progress: the laws workflow was installed on iamcxa/qnow `spacedock-state/dev2` at 77b0d1902 on 2026-11-10, on the Captain's choice 「裝 qnow（建議）」, to measure cost; its first run took 28 seconds wall clock (run 42848648288). The design reads the runs since.
- Non-goals: changing what the laws judge; making a failed laws run block a push, dispatch or merge; syncing an adopter without its Captain's merge.

## Budget
- One package PR (the release and adoption references, and a check or script only if the design shows prose cannot report a repository left behind).

## Stop condition
- For a release, one command or named step lists each known adopter with its README marker and laws pin against the released tag, and the design says who moves each and on whose word; or the design shows why not and says what was learned.

## FO alignment

Alignment: needed at ideation; whether the laws check is installed by default, whether its pin follows each release, and who may open an adopter's sync PR are the Captain's call.
Result: the Captain chose 「先報落後，預設與否等數字（建議）」 (host question dialog, 2026-11-11), answering 「「發版後鋪開到採用 repo 與法規檢查」這張任務的設計方向要怎麼定？我建議：設計先做「每次發版列出每個採用 repo 的說明檔版本和法規釘選、落後的報出來」，法規檢查要不要預設安裝、釘選要不要自動跟著發版走，等 qnow 的費用量出來、在設計關卡用數字讓你選。這是設計的方向，細節與證明仍在設計關卡由你核准。」.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
