# kc-decision-log 設計說明

D5 已接受 **CLI 優先、MCP 選配**；本PR為規劃設計；CLI未實作／部署，非ready handoff。完整 28 故事／8 活動及 D1–D4 保留，P1 五故事與 Pilot 不變。使用者先前投入原話「1-3天」；本輪已澄清「三個完整工作日」，appetite 上限 3 days，正式days scalar estimate仍為 `null`、fit `unknown`。具體工作模型見 [CLI 設計](cli-first-design.md)；故事與 AC 唯一來源見 [README](README.md)。

## 從完整故事看最小交付

使用者指定自己的決策空間、釐清裁決權、討論與確認；Claude、Codex、dot 在各自已授權的執行環境讀取同一精確依據，再沿既有流程執行並帶證據回來。共用核心不意味共用一個遠端 process，也不將不同 repo 的裁示合成同一權威。

候選順序仍是 **P1 讀取 → P2 查核 → P3 安全更新 → P4a 單任務閉環 → P4b 跨層重審 → P5 受控 PR**。P1 的路徑是指定來源 → 真正三端執行 CLI → 核對身份／權限與同一原文 → 分清層級 → 回答有效或仍有疑義。最小共用 core／CLI 封裝、多 repo 原生 loader、JSON／人讀輸出與錯誤都服務這五故事；不是已可用的附屬工具，也不預切工程任務。

S17 遠端 host 維護保留全圖、移出候選 P3 至 deferred，因 CLI loaded view 與 checkout 安全更新不要求遠端 host。沒有新增 slice。P3、P4a、P5 的 P2 都是建議順序，非整片硬依賴；P1 必要讀取能力保留。P3 的當次 Git 安全條件與更新後重讀、P4a 的精確 pin／freshness／適用性及接手者權限、P5 的已准來源／base／diff／前次不確定結果及提交前重查都不可跳過。可由既有 Git 等能力提供，不要求 P2 全部診斷產品先交付；替代路徑仍未端到端實測，查不明就 unknown／停止。P3 也是 P4a 建議順序，P5 可以整片延後。

## 權限與來源的分界

| 對象 | 保存處／責任 | 權威邊界 |
| --- | --- | --- |
| 共用 code／CLI | 通用程式目標 `iamcxa/kc-claude-plugins`；解析、搜尋、effective 與引用 | 不攜帶私人 ADR／credential，不授予裁決權 |
| 使用者總指揮裁示 | 使用者指定且獲授權的獨立 Git repo | 該層獲授權決策者確認方向；不自動許可外部動作 |
| 工程 ADR | 各工程 repo 原生 path | 固定引用上層版本，不以較新時間／supersession 覆蓋上層 |
| runtime／source binding | 已准 OS／filesystem／GitHub 或獨立環境；明確 repo／ref／commit／path／level／scope | CLI 設定防誤讀，不把 label／allowlist 稱為安全隔離 |
| dev2／Spacedock | 既有 workflow、任務、gate 與驗收來源 | 任務及驗收不由 CLI、gh 或讀取結果產生 |
| 選配 host／MCP | 原有運行者與授權邊界 | 另觀測自己的 snapshot／code；非 CLI P1 前提，不因本機更新即宣稱部署 |

ADR、Accepted、合併、身分驗證與行動許可是不同事實。OS/process context、gh 帳號、Git remote credential、Sites owner 與裁決權也須分開。agent 可共用同一合法 owner 帳號協作；無需替每個 agent 建 GitHub 用戶，也不能用共用帳號作雙使用者隔離證據。

已有 clone 的合法本機讀取可依 OS／filesystem 與 binding 執行，不必每次在線 gh 或取得 Sites 身份。gh 與 Git remote credential 可能不同；僅回報真正觀測到的身份。無 terminal／權限的 client 路徑另議，不繼承另一 runtime 的登入。真正負向隔離須由實際權限或分隔環境證明，同 OS 原本可讀的資料不能稱被 CLI 隔離；已觀測macOS兩已知檔的局部read-deny機制；完整query／Git helpers／objectstore／aliases隔離仍未驗，不要求使用者先建真帳號。

獨立決策庫與工程 repo 不搬入工具 repo。來源域要包含 repo／層級／scope，不能只靠 project key 或同號 ADR；先分隔合法來源再建查詢 view，不先混 snapshot 再 filter。無權／不可讀來源保持未知，不擴權補齊。

## 版本觀測與安全更新

| 觀測對象 | 保留的版本 | 更新責任 |
| --- | --- | --- |
| code／安裝包 | package、core／contract 版本、可證明的 code commit；無 checkout 就不適用 | 既有安裝／code checkout 持有者，非 CLI 自升級 |
| 各 ADR repo | 明確 repo／ref、immutable data commit、原文 digest | 該 checkout 持有者依 D2 用既有 Git |
| 各 runtime loaded view | 實際 data commit／digest、config、所用 core／contract、indexed_at | 讀取重建，不能假定另一 runtime 同步 |
| 選配遠端 host | 自己載入的 data revision 與獨立 code 版本 | 原維護流程另行授權；S17 延後 |

adapter 版本可與 core／contract 分開；看相容語義，不以號碼不同直接判不一致。同 core／contract、相同來源與 data commit 應有相同原文 digest、狀態與 effective；context／時間可不同。code checkout、安裝包、ADR revision、loaded view 不合成一個「全部最新」。

離線讀固定 D0 可以成立，但遠端身份／ref／freshness 未觀測就是未知。P1 誠實標示 D0；P2 提供版本與阻礙查核；P3 才做 ADR 影響分析，再由持有者安全更新及重讀。各片當次必要查核可沿既有 Git 進行，不能為等待 P2 而省略，也不要求 P2 整片產品先完成。先核對相同 repo／ref 與 ancestry，再分同／落後／領先／分岔／remote unknown，另報 dirty 與觀測時間。shallow history 或無法取得 commit 不猜成落後。

D2 已確認：配置來源落後、工作目錄乾淨且可 fast-forward，持有者按既有授權自行更新、重讀並回報；dirty、領先、分岔或未知保留。不自動 stash／reset／merge／rebase，不把任意 path／帶憑證 remote URL 變成執行參數。ref race 時重新觀測或停下。CLI 本身唯讀，不 fetch、不做 Git 更新。

P3 更新後分別回報實際 checkout commit 與 loaded view；重讀受影響原文／effective，舊 revision 不沿用。失敗保留原可用狀態並說明舊版／未知。選配 host 候選驗證後才切換 last-good 的工作留 S17；不要求建立 host 才完成 CLI P3。

## 合成案例與後續批次

全部符號虛構。使用者在 `example/mira-decisions` 的 `GUIDE#0012@D0` 確認「展示站先限團隊登入」；`example/harbor-app` 的 `ENG#0012@C0` 固定引用它並選擇工程方案。實質改方向另立 `GUIDE#0013@D1`，原話及歷史保留。兩筆同號也不共用裁決權。

- **P1**：三端各自合法執行 CLI，對照同一 D0／path／層級／digest／原狀態與 effective；真實權限分隔的另一使用者不能讀取。這是待驗收案例，不是本輪實測。
- **P2**：一個 runtime 的 view 還在 D0、決策 checkout 已見 D1，工具安裝包又是另一版本；分別回報，不稱全部最新。
- **P3**：乾淨落後 checkout 依 D2 前進；dirty 保留，各 runtime 重讀自己的 view。無遠端 host 仍可完成本路徑。
- **P4a**：使用者轉交或走已有驗證通路；接手者在自己的已准環境讀精確引用，由原 dev2／Spacedock 完成一個任務並留下 gate 證據。自動 bridge 延後。
- **P4b**：工程證據改變裁示前提，回適用層級原決策者重審；新的裁示不被工程較新 commit 反向覆蓋。
- **P5**：確認具體 diff／base 後由既有 Git／gh 送待審查 PR；前次結果未知或 base 移動先查清。PR、merge、Accepted 與選配 view 載入分開核對。

## ADR 寫入沿用原有權威

D3 保留：agent 可整理草案，並依該次已准動作用既有 Git／PR 工具；CLI 及選配 MCP 唯讀，不代配號、不造 task、不自動提交。內容為「部署」不代表已授權部署。確認須綁定原文／diff、repo、層級／scope、內容版本、base 與可信出處；變動須重新檢視。

D4 保留：實質變更新 ADR，小修原檔；沿用 dev2 **0.25.0** [ADR 模板](../../../kc-dev-flow-2/references/adr-template.md)、[workflow](../../../kc-dev-flow-2/references/sd/workflow.md) 的原 FO／number guards 與 [implementation principles](../../../kc-dev-flow-2/skills/implementation/principles.md)。取代為舊 ADR Status 的 Superseded by NNNN，草案不預配號；Recommended 缺欄按原規範記 not recorded。

D4是使用者已確認的產品政策，lint本身不判斷語意變更、誰已確認或是否應Accepted；配號與feedback仍走原FO機制。

原格式沒有定義本產品的 effective 演算法。Accepted 與 query unresolved 分開，不改人類裁示，不強迫增欄或改路徑。小修／實質變更含糊時回原適用決策者，不能由 lint 證明語義。

## 本批審閱與 admission 邊界

先前 MCP 方向的六片獨立設計審查是歷史，不沿用為 CLI P1 AC／六片依賴增量的通過。前輪CLI actor／removal獨立審查僅支持其當時來源；後續問題／觀測及本次四包提案以增量核對為準，未重跑獨立整圖審查，與人類書面審閱、實測／UAT、fit 及 handoff 分開核對。已觀測 Codex 本機命令及 Claude CLI 啟動可用；新 CLI 尚不存在，Claude本人正常唯讀Git回執pending非denied；dot→已准delegated local task已有命令鏈基礎，三端新CLI、完整隔離harness與native loader仍待實作／驗證；歷史 unit tests 不等於新 UAT。舊 OAuth 失敗不改寫，CLI 方向不依賴修復也不宣稱已解決。

投入上限 3 days 不等於估算。[P1估工](p1-estimate.md)已有32–48 active工程小時粗估／風險40–64h，含整合、驗證與一次修正；未經同類交付校準，8h/day僅規劃換算，正式estimate null／fit unknown。歷史 MCP admission 的 brief／assessment／handoff hash 與 acceptance 不套用新來源。待 map／spec 審閱接受，先依 [release slicing](../../../kc-journey-map/skills/kc-journey-map/references/release-slicing.md) 以新 full-map requirements 重整 baseline，再走既有 cut／brief／handoff；P1／Pilot／投入不需重選。

本輪不改 SD state／gate、不實作或新增授權；全圖不造 `status`／`evidence`，不宣稱 ready handoff 或六片全接受。可讀投影見 [故事地圖](story-map.md) 與 [切片地圖](slice-map.md)。

## 本批陌生讀者核對

兩native讀者在history-free白名單快照提43題；root逐題按已讀symbol／既有設計分成Fact或Gap後，35個穩定questions已回填P1。7 Fact、28 Gap中共有31主題仍含工程shaping／適配；沒有新產品value決策，也沒有新ADR或task。未實作能力不列成先要成品的外部前提；待補技術證據是正常Claude本人唯讀Git原回執；dot委派local task基礎已具，完整OS合成repo harness及三端CLI是P1待實作驗證，不是使用者先供成品。已知本task／delegated local命令與native reader啟動能力保留，不能推為三端UAT。

## P1技術契約與投入提案

四包是既有五故事的工程收斂，**尚未實作／驗證、未接受API**，不是新增release或任務。31個技術問題已有逐項提案，Gap仍在；見[P1技術契約](p1-technical-contract.md)與[估工及假設](p1-estimate.md)。

| 契約包 | 對應P1故事 | 草案內容 | active工程小時 |
| --- | --- | --- | --- |
| [A 來源、權威與context](p1-technical-contract.md) | S01, S02, S04, S10 | 可信binding／authority／canonical引用與context來源；不賦予存取或裁決權。 | 4–6 |
| [B 固定blob、唯讀loader與native parser](p1-technical-contract.md) | S01, S02, S10, S11 | 固定Git原blob／嚴格UTF8；native格式與Status沿dev2，原生lint結果與非權威衍生查詢分開，不將一筆診斷改成全庫失效。 | 8–12 |
| [C CLI輸出、資源界線與可重現交付](p1-technical-contract.md) | S01, S02, S04, S10, S11 | Node24固定checkout入口、JSON／人讀、exit／paging／limits與code closure。 | 6–9 |
| [D 獨立oracle與三端驗證回執](p1-technical-contract.md) | S02, S10 | committed合成blob獨立expected、三端發起鏈及整個query／Git helpers的OS負向harness。 | 8–12 |
| 跨包整合／Pilot驗收重跑及一次修正 | 五故事整體 | 不重複計入各包局部驗證／D首次驗證 | 6–9 |

投入已明確為**三個完整工作日**；先前原話「1-3天」保留，上限仍3 days，不再是工作日／日曆日待選。完整P1粗估**32–48 active工程小時**，條件風險範圍**40–64h**，未經同類交付校準。8h/day僅我方規劃換算（4–6／風險5–8工程工作天）；若據此換算三工作日為24h，估量不支持該假設下完整P1可交，但24h不是人類原話／承諾。正式estimate `null`、fit `unknown`，沒有三日可交證明或增加上限。

Claude本人正常工作階段的唯讀Git原回執仍pending（非denied）；dot→已授權delegated local task已有命令鏈基礎，後續需各named client的真CLI回執，不要求dot前端直接shell。macOS兩已知檔4個read-deny cases只證局部機制，不是完整query／Git helpers／objectstore／aliases隔離或AC1通過。上述產品驗證由P1完成，不要求使用者先備妥成品。

原生ADR格式／Status／配號／驗收與feedback沿dev2；原生lint整體check fail不改其他Accepted。已撤回整binding一律unresolved策略，衍生effective只作非權威查詢；見[dev2原生對齊](p1-technical-contract.md#native-dev2-alignment)。
