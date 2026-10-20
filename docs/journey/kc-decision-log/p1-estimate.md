# P1工程工作量粗估（重切後，提案）

**重切後 P1 粗估 12–24 active 工程小時，未經同類交付校準；fit 在原生 handoff 檢查前仍未證明。** 投入是使用者澄清的「三個完整工作日」，原話「1-3天」。

重切前 P1（S01, S02, S04, S10, S11）的 32–48 小時粗估不再適用：它計入的雙使用者 OS 隔離測試、三端回執與多來源分隔已移至 P4a／P4b。該版本保留在本 PR 2026-10-20 重切前的提交歷史。

| 工作 | active 工程小時 | 依據 |
| --- | --- | --- |
| CLI：binding 配置、拒絕未配置來源、依 ADR root 讀固定 commit、JSON／人讀輸出與 exit code | 4–8 | 既有查詢原型已有 `parse`／`makeSnapshot`／`effective` 與 `createService`，build 已以 `git rev-parse`／`ls-tree`／`show` 讀固定 commit；需去掉 `SOURCE_PATH` 的 `projects/KEY` 限定、改讀外部 repo、加 CLI 入口。 |
| 合成決策 repo 與驗收 fixtures | 1–2 | Accepted、Proposed、同 repo 取代、缺 Decision key、壞鏈；D0 → D1 ref 前進。既有測試含合成 fixtures 可參考。 |
| Codex 在自己的環境執行同一 CLI | 1–2 | Codex 本機命令可用；需確認它能讀到同一 repo 與 commit。 |
| 一個合成 dev2 任務走完 Pilot 並取回證據 | 4–8 | 沿用本 repo `docs/dev2` workflow；無同類任務的實測週期。 |
| 整合與一次修正 | 2–4 | 跨段介面（引用格式、交接內容、證據核對）。 |

**假設：** 既有查詢原型大小為 2026-10-20 實測：`source.mjs` 136 行、`service.mjs` 67 行，連同測試共 810 行。工時是依此推的判斷，不是測得的生產率。估算假設 CLI 放在既有原型旁；若改放到公開 repo，搬移與公開內容檢查另計，未估。

**未知：** dev2 合成任務的實際週期、Codex 端讀取路徑、CLI 程式放置位置。超過投入時，回到使用者決定縮範圍或加投入，不自行擴大預算。
