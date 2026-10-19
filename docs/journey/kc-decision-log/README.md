# kc-decision-log 故事與交付規劃

P1「讀對同一份裁示」已選為第一個 release，採用 kc-dev-flow-2 的 **Pilot** profile。主要 journey 保留 8 個活動、28 個故事；P1 為 S01、S02、S04、S10、S11。P2、P3、P4a、P4b、P5 仍為候選，S03、S12、S28 明示延後。

先發布並合併地圖，再沿既有 dev2／Spacedock 流程準備 P1 的正式 brief、估算與驗證；後續依實際結果逐片以小批次推進。此選擇沒有一次啟動全部六片。

## 閱讀與來源責任

| 文件 | 用途與編輯責任 |
| --- | --- |
| [完整故事地圖](story-map.md) | 可讀投影：完整活動、故事細節、規則及 P1 release band |
| [切片地圖](slice-map.md) | 可讀投影：六片成果、範圍、依賴、移除測試與驗收條件 |
| [journey.yaml](journey.yaml) | 故事 ID、活動順序、卡片、細節、規則、責任與已選 release membership 的唯一編輯來源 |
| [slices-proposal.yaml](slices-proposal.yaml) | 候選切片的成果、範圍、依賴、驗收與 D1–D4 設計選擇的編輯來源；其中 `story_ids` 是提案索引，已選 membership 以 journey 為準 |
| [設計說明](design-notes.md) | 權限、版本觀測、更新與 ADR 修訂的設計理由及合成案例；不另定故事或 membership |

兩份 `.yaml` 採 **JSON 語法的 YAML 1.2**，可由 JSON parser 讀取。Markdown 地圖由這兩份來源整理而成；更新時先改對應來源，再同步投影，避免另外形成一套故事或 release 權威。

`detail` 是本規劃自訂的故事補充欄位，**不是 kc-journey-map 原生標準 schema**，不承諾原生 renderer 會顯示。`mode`、`proposal_state` 與整份 `slices-proposal.yaml`（含 `selected_release`、`selection`、`budget`、`admission_questions`、`dev2_alignment`）也是本規劃的補充資料；不代表新增工具 API、驗收機制或 dev2 workflow。原生 release band 使用 `releases` 與故事的 `release`。

## 已確認的方向

- D1：使用者手動轉交，或沿用已有驗證的通路；自動橋接延後。
- D2：已配置來源落後、工作目錄乾淨且可 fast-forward 時，由 checkout 持有者依既定規則自行更新、重讀並回報；其餘保留原狀並說明原因。
- D3：agent 沿用既有 Git／PR 工具，MCP 維持唯讀；寫入 MCP 與 host 代寫延後。
- D4：實質變更新 ADR，小修留原 ADR；沿用 dev2 的格式、狀態、配號、取代方向與既有審查。適用層級的獲授權決策者仍負責裁決，host／MCP owner 身分不自動授予裁決權。

dev2 對照基準為 repo 內的 0.25.0：見 [ADR 模板](../../../kc-dev-flow-2/references/adr-template.md)、[workflow](../../../kc-dev-flow-2/references/sd/workflow.md)、[implementation principles](../../../kc-dev-flow-2/skills/implementation/principles.md)、[ADR lint](../../../kc-dev-flow-2/scripts/adr_lint.py)、[number guards](../../../kc-dev-flow-2/scripts/number_guards.py) 與 [Pilot profile](../../../kc-dev-flow-2/references/profiles/pilot.md)。這些參照說明既有機制，不證明整體讀取服務或跨流程相容性已驗收。

## 驗證界線與下一步

六片的設計內容已完成獨立審查，涵蓋故事必要性、角色路徑、來源／權限邊界與可觀察終點。這是規劃意圖，讀取與切片實作狀態尚未驗證；故事沒有 `status` 或 `evidence`，不以 `exists`／`gap` 表示尚未查證的實作情況。

真實三端登入與隔離、完整 hosted adapter、跨 repo 原生 ADR／Legacy 讀取、Git ancestry／race／安全更新、host refresh／last-good、dev2 整體 roundtrip、實際配號與 PR 重試仍須驗證。公開案例使用合成資料；私人 ADR、執行日誌、憑證與受保護證據留在原授權來源。

P1 與 Pilot 已選；**appetite、可信整合估算、正式 Development Brief 與 journey-handoff 檢查尚待完成**。未宣稱正式開發移交、產品 UAT、合併、部署或 host 載入通過。地圖發布與產品 P5 的「受控 PR」是不同工作範圍。

既有 [journey lint](../../../kc-journey-map/lib/journey-lint.mjs) 會對這種未填實作狀態的意圖來源報 `no-status`；其意義是未進入實作查核，不應以補造狀態消除訊息。正式 handoff 仍依 [release slicing](../../../kc-journey-map/skills/kc-journey-map/references/release-slicing.md) 與既有 dev2 流程辦理，本目錄不另建 standing verifier 或 CI。
