# kc-decision-log 故事與交付規劃

**CLI 優先、MCP 視需要選配的方向已接受（D5）。本PR為規劃設計；CLI未實作／部署，非ready handoff，技術安排與切片增量待人類書面審閱。** 先前地圖發布不代表這次 CLI 變更已發布。

P1「讀對同一份裁示」仍是第一個 release，採 kc-dev-flow-2 **Pilot**；五故事為 **S01、S02、S04、S10、S11**。先前投入原話「1-3天」；本輪已澄清「三個完整工作日」，appetite 上限 **3 days**；`estimate: null`、fit `unknown`。全圖保留 8 活動、28 故事；P2、P3、P4a、P4b、P5 仍候選，S03、S12、S17、S28 延後。S17 遠端 host 維護不再是 CLI P3 的必要成果，故事仍保留。

## 閱讀與來源責任

| 文件 | 用途與編輯責任 |
| --- | --- |
| [互動HTML地圖](index.html) | 由canonical兩份YAML生成的本機靜態投影；可展開卡片／問題與強調切片 |
| [P1技術契約](p1-technical-contract.md) | 四包31主題的具體候選介面／驗證；未實作、未驗證、未接受API |
| [P1估工](p1-estimate.md) | 完整P1 32–48 active工程小時、風險40–64h與時間基準限制 |
| [完整故事地圖](story-map.md) | 可讀投影：完整活動、故事細節、規則及 P1 release band |
| [切片地圖](slice-map.md) | 可讀投影：六片成果、範圍、依賴、移除測試與驗收條件 |
| [journey.yaml](journey.yaml) | 故事 ID、活動順序、卡片、細節、規則、責任與已選 release membership 的唯一編輯來源 |
| [slices-proposal.yaml](slices-proposal.yaml) | 切片成果、範圍、依賴、驗收、D1–D5 與投入的編輯來源；`story_ids` 是提案索引，已選 membership 以 journey 為準 |
| [CLI 優先設計](cli-first-design.md) | 本次可審閱的工作模型、來源／身份／輸出邊界與待驗收項；不另定故事或 membership |
| [設計說明](design-notes.md) | 裁決權、版本、安全更新、ADR 修訂與候選批次的理由 |

兩份 `.yaml` 使用 **JSON 語法的 YAML 1.2**；Markdown 地圖依它們同步。`detail` 是自訂補充欄位，**不是 kc-journey-map 原生標準 schema**，不承諾原生 renderer 顯示。`technical_proposal`、`effort_proposal`、`mode`、`proposal_state` 及整份 `slices-proposal.yaml` 也屬本規劃補充資料，不代表新工具 API 或 workflow。原生 release band 仍是 `releases` 與故事的 `release`。

## 已確認的方向

- D1：使用者手動轉交或已有驗證的通路；自動 bridge 延後。
- D2：已配置來源落後、乾淨且可 fast-forward 時，由 checkout 持有者用既有 Git 更新、重讀並回報；其他狀態保留原狀。
- D3：agent 沿用既有 Git／PR 工具；MCP 唯讀，不由 host 代寫。
- D4：實質變更新 ADR、小修原檔；沿用原生 dev2 的配號、狀態、取代方向與審查。適用層級決策者保有裁決權。
- D5：CLI 共用唯讀查詢核心，git 管版本與安全更新，gh 沿用該 runtime 既有身份／PR；MCP 選配。最小 core 整理與 CLI 封裝是新工作，未宣稱已可用。

共用 owner 身分可以協作；gh 登入、Git remote credential、OS／process context、Sites owner 都不等於裁決權。已有合法 clone 可離線讀固定 commit，不強制每次在線 gh；遠端 freshness 未觀測時保持未知。真正雙使用者隔離依實際權限邊界驗證，label／allowlist 不能替代。

## 驗證與下一步

Codex本機命令／gh metadata可用；dot→已授權delegated local task已有實際shell／Git／gh metadata鏈，不另要求dot前端直接shell，也不推cloud繼承登入。Claude CLI／native reader既有auth及Read/Grep已觀測；正常Claude本人發起唯讀Git命令原回執仍pending（非denied），由我方後續查核。新CLI尚待實作，三端named-client產品回執與合法來源驗收仍未完成。 macOS兩已知非私密檔的4個read-deny cases已證process限制機制局部可用；不是完整A/B使用者隔離、跨平台保證或AC1通過。完整合成repo harness須限制整個query及Git/helpers，保護foreign metadata／objects／aliases並排除未受限旁路；屬P1驗證工作，不要求使用者先建真帳號或備妥成品。 歷史unit與單端metadata不是新CLI UAT；舊OAuth失敗保留歷史，CLI P1不以修復它為前提。

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

先前 MCP 方向的六片設計審查不沿用；前輪CLI actor／removal獨立審查僅支持其當時來源；後續問題／觀測及本次四包提案以增量核對為準，未重跑獨立整圖審查，與人類書面審閱、實測／UAT、fit 及 handoff 分開核對。待這次 map／設計審閱接受，先重整 **新 full-map requirements baseline**，再依 [release slicing](../../../kc-journey-map/skills/kc-journey-map/references/release-slicing.md) 與既有 dev2／Spacedock 做正式 brief、cut／handoff；不得沿用歷史 MCP brief／assessment／handoff 的舊 hash 或 acceptance。原 P1／Pilot／投入選擇有效，後續小批次逐片推進，不一次啟動六片。

故事不填未查證的 `status`／`evidence`；原有 [journey lint](../../../kc-journey-map/lib/journey-lint.mjs) 的 `no-status` 是意圖地圖限制，不以補造 `exists`／`gap` 消除。本輪另有文件PR授權；無正式ready handoff或產品UAT，不包含產品實作、安裝、登入、新憑證、merge或部署。

dev2 基準維持 **0.25.0**：見 [ADR 模板](../../../kc-dev-flow-2/references/adr-template.md)、[workflow](../../../kc-dev-flow-2/references/sd/workflow.md)、[implementation principles](../../../kc-dev-flow-2/skills/implementation/principles.md)、[ADR lint](../../../kc-dev-flow-2/scripts/adr_lint.py)、[number guards](../../../kc-dev-flow-2/scripts/number_guards.py) 與 [Pilot profile](../../../kc-dev-flow-2/references/profiles/pilot.md)。這些是沿用規範，不是整合已驗收證據。

本批已完整執行兩native陌生讀者interrogation：43原題去重35主題，7 Fact／28 Gap；31主題含技術shaping／適配，沒有新增人類value決策。P1 `questions` 保留穩定ID與短問答／doc，原題mapping列於slices-proposal.yaml的interrogation.mapping_by_question，原始回答及scope audit留本批task驗證紀錄。回答Gap不等於完成Gap；原生lint／contract／handoff的實際結果另見本批報告，不以敘述替代通過。

HTML投影以本資料夾[render.py](render.py)重建，只生成index.html，不改手整Markdown。既有明確接受在scope／premises仍相符時沿用；格式／問題記錄更新不自動要求重選，真正投入／value／scope／acceptance改變才需新決定。歷史handoff結果不綁定本次新hash。

原生ADR格式／Status／配號／驗收與feedback沿dev2；原生lint整體check fail不改其他Accepted。已撤回整binding一律unresolved策略，衍生effective只作非權威查詢；見[dev2原生對齊](p1-technical-contract.md#native-dev2-alignment)。

本輪已明確授權文件PR（見slices-proposal.yaml的publication_scope）；D5原先只確認方向的歷史邊界仍保留。35題短ask／answer均遵原生80欄建議，完整問答留各doc章節；原題對照是自訂interrogation.mapping_by_question。`questions.source`保留給journey-fold寫入gate／amendment footprint，本批不填、不偽造fold metadata；參見[原生欄位表](../../../kc-journey-map/lib/schemas.mjs)與[Rulings契約](../../../kc-journey-map/README.md)。
