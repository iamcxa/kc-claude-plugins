# kc-decision-log 設計說明

這份規劃保留完整 28 個故事與六片端到端成果。使用者已選 P1「讀對同一份裁示」為第一個 release，採 kc-dev-flow-2 的 Pilot profile；其餘切片仍為候選。先發布並合併地圖，再由既有流程準備正式 brief 與驗證，之後逐片以小批次推進。這份地圖不建立產品 workflow、host、憑證或存取權限。

## 從完整故事看最小交付

主角是使用者：指定自己的決策空間，釐清裁決權，討論與確認，再讓 agents 查詢正確版本、處理手上 checkout、交接既有流程，最後用證據重新決策。Claude、Codex、dot 是接手者；host 與本機 agent 在更新步驟各自負責自己的狀態。

設計包含：拒絕跨層 supersession、引用固定上層版本、把 freshness 拆成獨立觀測、先查再更新、更新後重讀、寫入只形成待審查變更。這些是為了落實已確認方向的候選行為；checkout 條件式自行更新已由使用者確認；具體資料欄位、host 維護機制、確認出處的保存格式與 MCP 工具名仍是後續技術細節。

建議的交付順序是 **P1 讀取 → P2 版本查核 → P3 安全更新 → P4a 單任務閉環 → P4b 跨層重審 → P5 受控 PR**。P1 已帶最小的協作引用，因此協作不必等待寫入 MCP。P4a 硬依賴 P1／P2，P3 只是建議先完成：可用既有人工核對與安全更新補足前置，不能略過 freshness 未知。P5 可整片延後，直到既有 Git／PR 方式顯現具體缺口。

P1 的最小路徑是：使用者明確指定獨立 repo → 三端驗證身分 → 讀到同一精確來源 → 分清裁決層級 → 回答有效或仍有疑義。隔離、範圍與衝突拒絕是必要條件，不能為了變小移到後片。若跨客戶端登入不成立，先做範圍受限的相容性驗證並交付可行／不可行證據，再決定產品切片；本輪未執行跨客戶端登入實測。

P1 與 Pilot 已選定；投入期限、可信整合工期與正式 Development Brief 尚待既有 dev2／Spacedock 流程完成。未執行 journey-handoff 檢查，不把 release 選擇或設計審查當作正式開發移交通過，也不由本圖產生另一份任務系統。

## 權限與來源的分界

| 對象 | 原文／狀態保存處 | 可決定什麼 | 可引用什麼 | 不由它決定的事 |
| --- | --- | --- | --- | --- |
| 共用工具引擎 | 本公開 repo 的規劃範圍 | 解析、查詢與一致的工具行為 | 合成 fixtures、公開規格 | 不持有使用者私人裁示，不授予裁決權 |
| 使用者總指揮裁示 | 使用者指定並獲授權的獨立 Git repo | 由該層獲授權決策者確認的方向與適用範圍 | 工程證據的受保護引用 | 不自動批准任意外部動作，不取代工程 gate |
| 工程 ADR | 各工程 repo | 該 repo 的工程方案與取捨 | 明確上層 ADR 版本及本地工程決策 | 不能以更新時間、key 或 supersession 覆蓋上層 |
| dev2／Spacedock | 原有 workflow、任務及驗收來源 | 任務、執行、gate、驗收的原有權威 | 精確 ADR 引用 | 不因任務完成就自動改上層裁示 |
| hosted transport／host | 現有運行實體 | 驗證 caller、依授權提供查詢、管理其 snapshot | 已配置且獲准的決策來源 | site owner 身分不等於通用的總指揮裁決權；本機 checkout 更新不代表已部署 |

「工程 ADR 留原 repo」與「每人有獨立決策庫」同時成立：獨立庫保存上層裁示，工程 repo 保存其局部工程決策；不把所有工程 ADR 搬成一份共享權威。工程來源要另行註冊並按權限讀取，讀不到時保持未知，不為了補齊視圖擴大存取。

project key 是命名空間，不足以單獨表示總指揮／工程層級。不同來源即使 ADR ID、Decision key 或數字相同，也不能碰撞。候選引用內容為：**來源 repo、層級、適用範圍、完整 ADR ID、path、commit、內容摘要**；這是語義需求，尚非已定 schema。

## 版本查核究竟查什麼

每筆比較都先綁定配置的 repo 與追蹤 ref，再記錄遠端 commit 及觀測時間。範圍至少分成：

| 觀測對象 | 比較的本地／持有版本 | 目標 | 誰更新 |
| --- | --- | --- | --- |
| host 決策 snapshot | snapshot 的來源 commit S | 決策庫追蹤 ref 的目標 D | host 維護者／host agent，依既有權限 |
| client checkout | agent 實際持有的 commit C | 該 checkout 所配置 repo／ref 的目標 T | 該 checkout 持有者在本機操作 |
| host 部署 code | 部署自身可證明的 code revision | 部署來源及版本 | 既有部署流程與適用授權 |

client checkout 可以是工具 code repo、決策 repo 或工程 repo，須按用途與來源分開。讀 MCP 不要求 client clone 私人決策庫。沒有 checkout 是「該觀測不適用」，不是 Git 關係的第六種狀態。

工具 code checkout 進到 T，不能證明安裝中的 plugin、MCP schema 或 Sites 部署 code 也進到 T。host 的 S 追上 D，也不能證明 agent 的 C 已追上自己的 T。不要提供一個把這些混在一起的「全部最新」旗標。

在已驗證相同 repo／ref、遠端目標可讀且祖先關係可判斷的前提下：

| Git 關係 | 顯示 | 自動更新候選行為 |
| --- | --- | --- |
| C = T | 一致 | 不動；仍顯示觀測時間 |
| C 是 T 的嚴格祖先 | 落後 | 僅在工作目錄乾淨、目標明確且現有授權允許時嘗試 fast-forward |
| T 是 C 的嚴格祖先 | 領先 | 保留；回報本地未在目標 ref 的 commit，不自動退回 |
| 雙方互非祖先 | 分岔 | 保留；由持有者按既有 Git 流程處理，不自動 merge／rebase／reset |
| 遠端、commit 或祖先證據不足 | 遠端未知 | 說明原因與最後可用觀測，不以舊 cache 宣稱一致 |

這個關係表同樣適用 host 的 S 對 D。repo／ref 不符時先回來源不符，不能跨 repo 算 ancestry。shallow history 或無法讀到 commit 若不足以判斷，也不能猜成分岔或落後。

MCP 對 agent 自報 commit 所作的查核是建議資訊；真正更新前，本機持有者還要重新確認 remote identity、HEAD、工作目錄與目標。不要把私人本機路徑、帶憑證 remote URL 或任意輸入直接變成遠端執行參數。

## 更新與重讀的完整路徑

1. 先觀測 repo／ref、目標 commit、持有 commit、可用 ancestry、dirty 狀態與時間；來源不符或未知就停止依賴更新的動作。
2. 呈現差異與受影響 ADR。影響不只看文字變更：還含刪除、更名、狀態／key／替代鏈改變，以及工程 ADR 所引用上層版本的變動。
3. checkout 持有者按既有授權重新查核，再做允許的安全更新。dirty 含 staged、unstaged 與未追蹤檔；不自動 stash、不強制 reset、不靜默切錯分支。其他獨立 worktree 策略仍是候選，須按實際來源與任務另行評估。
4. host 獨立讀自己的配置來源，驗證候選 snapshot 後才切換；失敗保留 last-good、明示舊 revision 與落後／未知，不把失敗當成功。
5. 更新後各自回報實際 commit，再重讀受影響原文與有效判定。舊 `revision` 失效時重新取得索引及版本；不能沿用舊結論。
6. 若檢查與更新之間 ref 移動，重新觀測或停止，不承諾「永遠最新」。裁示前提影響任務時回 dev2／Spacedock 重審，不能自行換掉任務目標。

使用者已確認：agent 查到已配置來源落後、工作目錄乾淨且可 fast-forward，即自行更新、重讀並回報；其餘狀態保留原狀並說明原因。此規則適用 checkout 持有者，不新增 host 維護或背景執行權限。自動通知／輪詢、host 更新由何者觸發仍待機制設計；本圖不提供背景執行或 automation 授權。工具名也保持未定，不把範例名稱當介面承諾。

## 合成討論案例

案例全部虛構；`D0`、`D1`、`C0` 是示意符號，不是可呼叫 API 的真實 commit。

虛構使用者 Mira 把上層裁示放在 `example/mira-decisions`。其中 `GUIDE#0012@D0` 裁定「展示站先限團隊登入」。之後若實質改變規則，另立 `GUIDE#0013@D1`；D1 是 repo 新 commit，包含新 ADR 及舊 ADR 的明示取代狀態，不是把 0012 原話改寫成另一個意思。`example/harbor-app` 的工程 ADR `ENG#0012@C0` 固定引用 D0，選擇沿用既有登入服務。兩筆同號、同用一個引擎，也不共用裁決權。

- **P1**：三端讀到相同上層原文與 D0，辨識工程紀錄只是局部方案；未登入或另一位合成使用者無法讀取。
- **P2**：決策 repo 已到 D1、host 還在 D0；工具 code checkout 卻已對齊它自己的追蹤 ref。回報兩個獨立狀態。
- **P3**：乾淨且落後的 checkout 可安全前進；有未提交說明文件時停下保留。host 驗證 D1 成功才切換，接手者重讀受影響裁示。
- **P4a**：Claude 交接 `GUIDE#0013@D1` 引用給 Codex；Codex 透過既有流程完成一個合成任務，dot 讀回原 gate 證據。裁示中的「部署」字樣本身不提供部署許可。
- **P4b**：D1 的新 ADR 改變工程方案的前提，工程 agent 帶回影響，由原適用決策者重審；若再實質改方向，另立後續 ADR，不能因 ENG 的 commit 較新就覆蓋 GUIDE。
- **P5**：若日後需要寫入，Mira 確認特定 diff 與 base 後才送待審查 PR。base 已改變或前次結果不明，先查清，不覆蓋、不重複送出；PR、merge、Accepted、host 已載入分開核對。

## 已確認與待決的討論

- 協作交接：使用者先轉交，或沿用已有驗證的通路；自動橋接延後。每位接手者仍用自己的已驗證身分重讀原文及證據。
- checkout 更新：已配置來源落後、乾淨且可 fast-forward 時自行更新並回報；其他狀態保留原狀。更新後重讀受影響 ADR。

目前的待決問題與確認紀錄統一維護於 [切片來源](slices-proposal.yaml)，可讀投影見 [切片地圖](slice-map.md)。避免在多份說明保留互相矛盾的問卷副本。

第一片已選 P1、profile 為 Pilot；開發投入期限、估算與正式 brief 留在既有 admission 流程處理。工程與上層的身分／範圍分離已確認，不重開此題。P4b 的人工重新裁示仍須精確確認版本及保存歷史，不因寫入 MCP 延後而略過。

## MCP 唯讀與 ADR 寫入的分工

MCP 唯讀不代表使用者必須手動寫 ADR。Agent 仍可整理草案，持有該 repo 既有且適用權限的 agent，可透過 Git／PR 工具執行本次獲准的提交；若某個客戶端沒有該能力，由使用者轉交。另一個候選是由 agent 呼叫寫入 MCP、host 代寫，此時 host 需要承擔受控寫入、衝突及重試核對。

使用者已選 agent 沿用既有 Git／PR 工具，MCP 先維持唯讀；寫入 MCP 與 host 代寫延後。裁決者、Git 提交者及本次動作授權均須分清。共同的最小確認契約已寫入 S08／S24 及 P4b／P5 驗收條件：確認綁定原文／diff、repo、層級／scope、內容版本與 base，保留可核對的可信出處；內容或 base 改變需重新檢視。P1 已選 Pilot，後續候選尚未選入 release。

## ADR 機制沿用 dev2

ADR 修訂政策已確認：實質變更新建 ADR、小修留原 ADR。沿用 dev2 0.25.0 原模板、狀態、原 FO／number guards 配號及 Git／PR 審查；取代是舊 ADR Status 的 Superseded by NNNN，不另設 supersedes 狀態／欄位。草案不預配號，原話及 Git 歷史保留，Recommended 舊缺欄按原規範記 not recorded。格式見 [dev2 ADR 模板](../../../kc-dev-flow-2/references/adr-template.md)，配號及審查見 [dev2 workflow](../../../kc-dev-flow-2/references/sd/workflow.md) 的 Decision records 與 Number guards；實作責任見 [implementation principles](../../../kc-dev-flow-2/skills/implementation/principles.md)。

dev2 並沒有在這些檔案定義 get_effective／Decision key 演算法；那是既有服務的保守查詢擴充。原 Accepted 與 query unresolved 分開，不以查詢不確定改寫人類裁示，也不強制新增欄位才承認原格式。小修／實質變更的語義分類無法由 lint 自動證明，含糊時回原適用決策者。

## 公開規劃與驗證界線

六片的故事必要性、角色路徑、來源／權限邊界與可觀察終點已完成獨立設計審查；P1 的選擇不代表其他五片已被接受。真實三端登入、完整 hosted adapter、跨 repo 讀取、Git race／安全更新、host last-good 與整體 dev2 roundtrip 尚未驗證。本次文件未賦予任何故事 `exists` 或 `gap`。

[README](README.md) 說明來源責任與自訂欄位；[完整故事地圖](story-map.md) 與 [切片地圖](slice-map.md) 是兩份可讀投影。
