# P1工程工作量粗估（提案）

**P1 粗估 16–30 active 工程小時，未經同類交付校準；上限以 8 小時一天換算為 3.75 天，在四個完整工作日的投入內。** 投入原話「1-3天」，澄清為「三個完整工作日」，2026-10-20 改為四個完整工作日。8 小時一天是換算假設，不是使用者的話。

本版反映 2026-10-20 已接受的 D7（兩個 dev2 任務，任務二由 Codex 協調者執行）、D8（程式放進 `kc-decision-log` plugin）、D9（生效判定沿用原型規則）與 D10（唯讀 skill）。重切前 P1 的 32–48 小時與重切當下的 12–24 小時都不再適用，保留在本 PR 的提交歷史。

| 工作 | active 工程小時 | 依據 |
| --- | --- | --- |
| 查詢核心移入 plugin 並改寫：binding、依 ADR root 讀固定 commit、原始 bytes 指紋、略過非 ADR 檔、位元組排序、逐筆判定、JSON／人讀輸出與 exit code、預期指紋比對；測試以 `adr_lint.py` 對照 | 6–10 | 原型 `source.mjs` 136 行、`service.mjs` 67 行，連同測試共 810 行（2026-10-20 實測）；問答列出的六項落差都在這段程式裡。 |
| plugin 骨架：Claude 與 Codex manifest、marketplace 登記、release-please 設定、版本一致性檢查、本機安裝測試、公開內容檢查 | 2–4 | 本 repo 既有 plugin 的做法與 `version-parity-check.sh`；沒有本 repo 新增 plugin 的實測工時。 |
| 唯讀 skill 與其驗收 | 1–2 | 一份短 skill，加上任務二的實際使用紀錄。 |
| 合成決策 repo 與驗收資料 | 1–2 | 帶 Decision key 的 Accepted、Proposed、取代、缺 key、同 key 兩筆、壞鏈；D0 → D1 ref 前進。 |
| 任務二：Paseo 啟動 Codex 協調者，Codex worker 重讀並實作裁示決定的小功能，開 PR 並等合併 | 4–8 | 另一個 repo 已有 Codex 協調者跑 dev2 的紀錄；本 repo 沒有實測週期，Codex 環境的 Node 24 與 clone 讀取未驗。 |
| 整合與一次修正 | 2–4 | 引用格式、交接內容、證據核對之間的介面。 |

**合計 16–30 小時。** 工時是依上列依據推的判斷，不是測得的生產率；不含等待使用者批准與合併的時間。

**未知：** 任務二的實際週期、Codex 環境能否執行 CLI、dev2 兩個任務的關卡往返次數。超過投入時，回到使用者決定縮範圍或加投入，不自行擴大預算。
