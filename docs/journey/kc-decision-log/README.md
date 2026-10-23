# kc-decision-log 原生故事與切片地圖

本目錄使用 `kc-journey-map` 原生 YAML、Markdown 說明及 tldraw `.tldr` 快照。可繪製來源是 [journey.yaml](journey.yaml)；故事總覽與六個切片頁由同一次原生 render 產生，快照為 [journey.tldr](journey.tldr)。

P1「帶著精確裁示走完一次交接」已選，採 dev2 Pilot，故事為 S01、S10、S11、S19、S20、S21、S22；2026-10-20 自原「讀對同一份裁示」重切。P2、P3、P4a、P4b、P5 的既有提案歸屬以「候選」標明，供完整地圖討論；S03、S12、S17、S28、S29、S30 延後且不指派 release。畫入候選切片不等於啟動開發。

## 來源與畫布

| 內容 | 原生來源 | 畫布位置 |
| --- | --- | --- |
| 8 個活動、30 張故事、原卡片文字 | `steps[].activity`、`steps[].stories[].card` | Story map |
| 六片名稱、成果與故事歸屬 | `releases[]`、`stories[].release` | Story map 的六條 release band；六個 journey-board 頁 |
| 35 個既有技術問答 | `stories[].questions[]` 的 id／ask／answer／doc | 掛在所屬故事的切片頁；全文連到技術契約章節（為重切前 P1 撰寫） |
| 28 個故事範圍連結、6 個切片說明連結 | 同一原生 questions／answer／doc 欄位 | 已指派故事的切片頁；四個延後故事的說明保留在來源及 Markdown |
| 9 項規則、責任範圍與驗證限制 | `rules[]`、`ownership[]`、`status` | 責任帶、各切片規則卡與狀態卡 |

原生 1.7.0 的 Story map renderer 呈現故事與 release band；問答由 journey-board renderer 呈現在切片頁。本目錄沒有自行補繪另一套 HTML 或自訂圖形。未建立 `system`／`evidence` 的實作宣稱；原生切片頁的 flow placeholder 表示尚無實作流程證據。

## 說明文件

- [故事說明](story-map.md)：活動、六片歸屬、30 張故事的完整範圍、規則全文與原題對照。
- [切片說明](slice-map.md)：六片成果、範圍、排除項、依賴、驗收條件及移除測試。
- [設計理由與 D1–D5](design-notes.md)：決策權限、版本、受控提交與已確認選擇。
- [CLI 優先設計](cli-first-design.md)：跨端工作模型及權限邊界。
- [P1 技術契約](p1-technical-contract.md)：35 個技術問答的完整提案與待驗項目。
- [P1 估工](p1-estimate.md)：重切後 P1 的粗估、依據與假設。
- [P1 開發說明（草稿）](p1-development-brief.md)：交給 dev2 的五段式 Development Brief，待使用者接受交接。
- [邊界合約（草稿 v2）](boundary-contract.md)：kc-adr 是讓 agent 讀寫 ADR 的套件；它與 dev2、故事地圖各自負責什麼，什麼資訊寫進哪裡，以及 P1 重排提案。

卡片、順序、規則短句及 membership 編輯 YAML；長篇故事說明、切片驗收與技術章節編輯對應 Markdown。原生 `doc` 使用 GitHub blob 章節網址；同 repo branch 的文件與地圖一起送審。畫布手改須先用原生 readback 檢查，再處理來源；不以另一份自訂 YAML 重複管理 membership。

69 個文件連結的章節標題已按原生 popup 的 heading slug 核對。本次沿用的本機 host 尚未配置此 repo 的 `JOURNEY_DOC_REPOS`，實際 `/repo-doc` 回傳 `unavailable`；目前可用視窗內的 **Open on GitHub** 開啟文件。畫布內閱讀仍待 host 維護者依原生 canvas 合約設定，不能把章節檢查通過當成該功能已驗收。

## 原生重現

下列命令從 repository root 執行，使用已備妥依賴的 `kc-journey-map`；亦可使用已安裝 plugin 的同名 CLI 並傳入本目錄的絕對來源路徑。server 的啟動、房間保存與文件連結設定依 [原生 canvas 合約](../../../kc-journey-map/skills/kc-journey-map/references/canvas.md)。

```sh
node kc-journey-map/lib/journey-render.mjs docs/journey/kc-decision-log/journey.yaml kc-decision-log-design --pages story-map,journey-board
node kc-journey-map/lib/journey-read.mjs docs/journey/kc-decision-log/journey.yaml kc-decision-log-design
node kc-journey-map/lib/journey-tldr.mjs export kc-decision-log-design docs/journey/kc-decision-log/journey.tldr
```

本機房間：[kc-decision-log-design](http://127.0.0.1:3737/?room=kc-decision-log-design)。頁面選單包含 Story map 及 P1、P2、P3、P4a、P4b、P5。`.tldr` 是該房間原生匯出的快照，YAML 仍是版本化來源；快照若要匯入，使用新房間以保留其他手動畫布。

## 驗證界線

2026-10-20 起 30 張故事都標 `status: gap`：kc-decision-log 尚無實作。開發進度由 `kc-journey-progress` 依 Spacedock 任務的 `journey`／`journey-release`／`journey-story` 回填；`exists` 必須附可搜尋的證據符號。render、原生 schema 接收、readback、快照內容及實際畫面分開核對。P1 的故事數 7（`slice_because` 記錄理由），其餘切片 3、3、2、5、4。

新 CLI 尚未實作／部署，Claude→Codex 交接驗收、正式 fit 與 ready handoff 均未成立。投入為四個完整工作日；P1 粗估 16–30 active 工程小時，未經校準。ADR 格式、Status、配號及審查沿用 dev2 原機制；任務與驗收沿用 dev2／Spacedock。
