# 使用者與 agents 共用決策：完整故事地圖

**CLI 優先、MCP 選配（D5）方向已接受；本PR為規劃設計；CLI未實作／部署，非ready handoff。** P1 五故事／Pilot／先前投入原話「1-3天」；本輪已澄清「三個完整工作日」（上限 3 days）保留，estimate `null`、fit `unknown`。原 MCP 審查不沿用；前輪CLI actor／removal獨立審查僅支持其當時來源；後續問題／觀測及本次四包提案以增量核對為準，未重跑獨立整圖審查，與人類書面審閱、實測／UAT、fit 及 handoff 分開核對。

主角：使用者：對跨專案方向負責的總指揮；由 Claude、Codex、dot 協助讀取、交接與回報。

使用者確認的裁示有獨立Git原文與明確權限；agents在各自已授權的執行環境用同一CLI核心讀對版本、對齊自己持有的checkout，交由既有流程執行，再帶證據回來重新決策。

故事、規則、責任與已選 membership 的唯一來源是 [journey.yaml](journey.yaml)。本頁是同步的可讀投影；`detail` 為自訂補充欄位。工作模型見 [CLI 設計](cli-first-design.md)，文件責任見 [README](README.md)。

## 現在的路徑

| 觀測 | 困難 | 現有做法 |
| --- | --- | --- |
| n1 在對話與 Git 之間核對裁示 | 對話中的共識、ADR 狀態與行動許可可能混淆。 | 由使用者或 agent 人工確認原文、版本及本次授權。 |
| n2 在不同執行環境核對同一原文 | 工具code、ADR revision與各runtime loaded view可能混淆；尚無已驗可用CLI。 | 使用既有Git能力人工核對明確來源／commit與操作身分，不把另一端的登入或摘要當本端驗收。 |

## 8 活動、28 故事

| A1 設定自己的決策空間 | A2 釐清誰能裁決什麼 | A3 討論並確認裁示 | A4 查出此刻適用的決策 | A5 對齊手上的版本 | A6 交接既有執行流程 | A7 讀回執行證據 | A8 重審並更新方向 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **S01** 我指定獨立決策庫與追蹤分支 **[P1]** | **S04** 我分清總指揮裁示與工程決策 **[P1]** | **S07** 我保留原話與決策出處 | **S10** 我查到原文與可重現的版本引用 **[P1]** | **S13** 我知道目前比的是哪個來源 | **S19** 我把裁示引用交給接手 agent | **S22** 我看到執行與驗收的原始證據 | **S24** 我用新證據重新討論裁示 |
| **S02** 我讓三個客戶端讀取同一空間 **[P1]** | **S05** 我讓工程方案引用上層版本 | **S28** 我比較可選方案再形成草案 | **S11** 我知道哪些已生效或仍有疑義 **[P1]** | **S14** 我看懂一致落後領先分岔或未知 | **S20** 接手者先核對版本與行動範圍 | **S23** 我看出裁示與結果之間的差距 | **S25** 我保留舊裁示與新舊關係 |
| **S03** 我能改設定而不誤讀別人的庫 | **S06** 遇到跨層衝突時我請原裁決者處理 | **S08** 我確認特定版本的裁示 | **S12** 我分清查不到與沒有讀取權限 | **S27** 我知道更新被哪些本機狀態阻擋 | **S21** 我沿用既有任務及驗收入口 |  | **S26** 我讓受影響的協作者重新確認 |
|  |  | **S09** 我把草案送成可審查的變更 |  | **S15** 我知道更新將影響哪些決策 |  |  |  |
|  |  |  |  | **S16** 持有 checkout 的 agent 安全更新 |  |  |  |
|  |  |  |  | **S17** 我讓 host 載入可驗證的新裁示 |  |  |  |
|  |  |  |  | **S18** 更新後我重讀並重檢原交接 |  |  |  |

## 已選 release band：P1

使用者指定獨立決策repo／ref／commit後，Claude、Codex、dot在各自已授權且可執行CLI的環境，以可核對的身份／來源context讀到同一精確裁示與正確層級，或照實保留疑義。

| 故事 | 使用者卡片 |
| --- | --- |
| S01 | 我指定獨立決策庫與追蹤分支 |
| S02 | 我讓三個客戶端讀取同一空間 |
| S04 | 我分清總指揮裁示與工程決策 |
| S10 | 我查到原文與可重現的版本引用 |
| S11 | 我知道哪些已生效或仍有疑義 |

其他五片仍為候選；S03、S12、S17、S28 延後。S17 遠端 host 維護保留全圖，CLI P1／P3 不以它為前提。來源解析、身份邊界、實際三端路徑與權限負向隔離尚待驗收；故事未填 `status`／`evidence`，不能讀成實作進度。

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

## 完整細節

### A1 設定自己的決策空間

適用規則：R1、R6。

| ID | 使用者卡片 | 補充細節 |
| --- | --- | --- |
| S01 | 我指定獨立決策庫與追蹤分支 | 使用者明確指定獨立決策repo、可用本機位置、追蹤ref／immutable commit、原文path及層級／scope，形成受控source binding；上層與工程repo各自配置，不把原文搬進工具repo。CLI唯讀loader只讀已配置且該OS/filesystem/GitHub context有權取得的來源，拒絕錯來源／未配置binding，不以任意CLI路徑擴權。native dev2 docs/adr或既有實際路徑保留，不為配parser改寫原文。 |
| S02 | 我讓三個客戶端讀取同一空間 | Claude、Codex、dot須各自透過能實際執行CLI且已有存取權的本機連線task或cloud runtime讀取同一依據，回報可核對的OS/process/runtime context。已有clone可依OS/filesystem與source binding合法離線讀固定commit，不必每次在線呼叫gh或取得Sites身份；需要GitHub操作時分別核對該runtime既有gh身分與Git remote credential，不假設兩者相同。可沿用同一合法owner credential協作，不要求每個agent新建帳號；這不是跨使用者隔離證明。沒有terminal的client需另議選配MCP／既有connector，不能用help、轉述或合成principal當三端pass。 |
| S03 | 我能改設定而不誤讀別人的庫 | 設定變更須顯示新舊來源差異；來源隔離、可撤銷存取與錯誤設定的拒絕行為可驗證。 |

### A2 釐清誰能裁決什麼

適用規則：R2、R3、R4。

| ID | 使用者卡片 | 補充細節 |
| --- | --- | --- |
| S04 | 我分清總指揮裁示與工程決策 | 每筆結果識別來源repo、層級、scope與裁決權；來源binding／實際存取權分開核對，各repo各有commit，canonical引用不能只靠project#number。不同owner／權威域在查詢前分隔，不先混成snapshot再filter；讀不到來源保留未知，工程決策不能反向取代上層。local OS／gh帳號或相同引擎不授予裁決權，不承諾跨repo原子view。 |
| S05 | 我讓工程方案引用上層版本 | 工程 ADR 只在其 repo 適用範圍內決策；固定引用上層 commit／內容摘要，上層變更後可重新評估。 |
| S06 | 遇到跨層衝突時我請原裁決者處理 | 不能把兩層替代鏈合成一條；工程端提出衝突及影響，回到上層決策者，不自動反向覆蓋。 |

### A3 討論並確認裁示

適用規則：R2、R4、R5、R9。

| ID | 使用者卡片 | 補充細節 |
| --- | --- | --- |
| S07 | 我保留原話與決策出處 | 保留人類原話、作者／裁決者與可信出處，並區分引用、agent 整理與人類確認；PR 提交前可核對草案未冒稱新的確認。 |
| S28 | 我比較可選方案再形成草案 | 討論階段整理可選方案、取捨與建議，供適用決策者選擇；在內容已確認後提交 PR 的切片中，不為此另建方案比較介面。 |
| S08 | 我確認特定版本的裁示 | 適用層級原已獲授權的人類決策者確認可閱讀的精確原文／diff、repo、層級／scope、內容版本及base，保留可信出處。內容或base變更重新檢視；CLI查詢、gh帳號、本次Git許可、PR／merge／Accepted與各runtime已重讀分別核對，選配host載入另列。 |
| S09 | 我把草案送成可審查的變更 | agent透過既有git／gh或原Git／PR工具，只對本次獲准repo與範圍建立可審變更，保留base、diff、確認出處及歷史。唯讀CLI與選配MCP不提交／開PR／配號或建立task，無既有Git能力由使用者依D1轉交。新ADR草案不預配號，需要時沿用目標repo原dev2 FO／number guards及審查；缺途徑回原權威，不另造服務。 |

### A4 查出此刻適用的決策

適用規則：R2、R3、R4、R5、R9。

| ID | 使用者卡片 | 補充細節 |
| --- | --- | --- |
| S10 | 我查到原文與可重現的版本引用 | CLI以JSON與人讀模式回傳已授權的執行context／選定binding，以及repo、層級／scope、完整ADR ID、實際path、immutable commit與原文digest；同core／contract及同來源commit可比較語義，不要求transport envelope或indexed_at逐字相同。code版本、ADR revision與loaded view分開；錯誤不洩漏無權來源是否存在，未知不補猜。 |
| S11 | 我知道哪些已生效或仍有疑義 | 照實讀取dev2原始Proposed／Accepted／Deprecated／Superseded by NNNN；只沿同repo／層級／scope的明示取代關係，不以時間或編號推論。CLI共用core的Decision key／effective resolved或unresolved是保守查詢語義，不是新ADR格式；缺key、壞鏈、衝突、Legacy或來源疑義保留原文／原狀態及未知，不強制新增欄位、改路徑或改Accepted。 |
| S12 | 我分清查不到與沒有讀取權限 | 使用者得到可行的下一步，但對外錯誤不洩漏不該讀的 ADR 或 repo 是否存在。 |

### A5 對齊手上的版本

適用規則：R5、R6、R7。

| ID | 使用者卡片 | 補充細節 |
| --- | --- | --- |
| S13 | 我知道目前比的是哪個來源 | 分別列出每runtime的CLI package／core／contract、已配置的code／ADR checkout與實際loaded view；每個data repo各報commit、digest、觀測時間。已安裝package無code Git checkout時報package version及不適用，不假造Git最新；選配host另列，不是CLI前提。 |
| S14 | 我看懂一致落後領先分岔或未知 | 相同repo/ref、可讀遠端目標與完整祖先證據才判checkout一致／落後／領先／分岔；不足為remote unknown並附observed_at。每runtime loaded view依實際data commit回報，不把code已更新或舊tracking ref當資料最新；沒有checkout是不適用，source mismatch另報。 |
| S27 | 我知道更新被哪些本機狀態阻擋 | 先由 checkout 持有者在本機查核 staged、unstaged、未追蹤檔及來源／分支狀態，回報可否安全更新及原因；P2 只觀測，不修改檔案、不送出私人本機路徑或內容。 |
| S15 | 我知道更新將影響哪些決策 | 由既有Git查核新舊版本，更新前列受影響ADR，含更名／刪除／狀態／取代鏈及既有上層pin；CLI以明確commit讀取，不自行fetch或更新。影響集合無法完整證明時擴大有權scope重讀或停止依賴該判斷的動作。 |
| S16 | 持有 checkout 的 agent 安全更新 | checkout持有者在該runtime既有權限內重新核對已配置repo/ref、乾淨、落後且可fast-forward，依D2用既有Git工具自行更新並回報；CLI不執行更新。更新後用CLI按實際新commit重讀；dirty／領先／分岔／遠端未知／來源不符或ref race保留原狀，不reset／stash／靜默切分支，不順便安裝package或部署。 |
| S17 | 我讓 host 載入可驗證的新裁示 | 若日後選配遠端host，由既有獲准維護途徑驗證候選snapshot並切換，失敗留last-good且顯示舊revision／未知。這是延後故事；CLI P1與目前P3不依賴它，D2也不新增host維護或部署權限。 |
| S18 | 更新後我重讀並重檢原交接 | 每個已納入的runtime在持有者安全更新後回報實際data commit，重新載入／查詢原文與有效判定，code／data checkout與loaded view分開。讀取失敗不把舊view標成新版本；若有last-good明示舊來源，前提變動回原dev2／Spacedock重審。選配host只有在其既有維護完成後另驗，不作本片前提。 |

### A6 交接既有執行流程

適用規則：R2、R3、R4、R5。

| ID | 使用者卡片 | 補充細節 |
| --- | --- | --- |
| S19 | 我把裁示引用交給接手 agent | 使用者手動轉交或沿用已驗通路，附傳出者／接手者、原task內容／回合／gate與repo／ADR／commit／digest／core contract版本、freshness及疑義。各接手者須用自己的已授權執行路徑重讀；共用合法owner身分不等於新的裁決權，cloud dot不自動橋接localhost，自動bridge延後。 |
| S20 | 接手者先核對版本與行動範圍 | 接手者核對自己的runtime／OS/process context及必要gh身分、來源binding與本次行動範圍，再以CLI重讀精確版本；不能繼承另一台機器的gh登入。無路徑／無權／引用不符就回報；ADR、其他agent聲稱或owner帳號不能批准外部動作，也不能代答peer權限提示。 |
| S21 | 我沿用既有任務及驗收入口 | 以既有 dev2／Spacedock brief、任務與 gate 接手，呈現原 repo／task／執行角色與可核對入口；決策庫僅提供引用，不另造任務狀態或驗收權威。 |

### A7 讀回執行證據

適用規則：R3、R4、R5。

| ID | 使用者卡片 | 補充細節 |
| --- | --- | --- |
| S22 | 我看到執行與驗收的原始證據 | 使用者轉交原流程的受保護commit／PR／gate／回執，或用已驗通路讀取；接收者用該runtime既有Git／gh或原入口核對執行者／驗收者／來源版本，證明對應本次任務內容、回合與ADR pin。相同task舊成功／錯回合／舊裁示／無權不能當成本次驗收；CLI不另造台帳。 |
| S23 | 我看出裁示與結果之間的差距 | agent在可核對的執行context及已准source binding內，用原任務證據整理預期、實際觀測、未知與影響。CLI讀取裁示不等於能讀敏感執行日誌；證據保留原保護來源，不複製到共用code或把摘要當原驗收。 |

### A8 重審並更新方向

適用規則：R2、R3、R4、R5、R9。

| ID | 使用者卡片 | 補充細節 |
| --- | --- | --- |
| S24 | 我用新證據重新討論裁示 | 適用層級原已獲授權的人類決策者，在原可信對話或既有審查來源確認維持或改變；確認綁定可讀原文／diff、來源 repo、層級／scope、精確內容版本及 base，保留可核對的確認出處。agent 整理、Git author 或工程成果不能自行證明上層裁決；內容／base 變更需重新檢視確認。實質改變另立新 ADR，小修留原檔；沿用 dev2 模板、既有配號與確認流程，不把 task amendment 的 Supersedes 當 ADR 欄位。 |
| S25 | 我保留舊裁示與新舊關係 | 依使用者已確認政策與 dev2 既有機制：實質改變裁示另立 NNNN-short-title.md，沿用原 FO 配號；取代時在舊 ADR Status 使用 Superseded by NNNN，未確認或仍 Proposed 的新稿不提前讓舊裁示失效。不改意思的說明拼字／排版／連結小修留原檔與 Git 歷史，不追改人類原話；舊 Recommended 缺失按 dev2 填 not recorded，不重建當年建議；Legacy 原文保留但不能充當新 required 裁示。分類不明交回原適用決策者，不增設新狀態、欄位或配號權威。 |
| S26 | 我讓受影響的協作者重新確認 | 使用者確認受影響接手者，逐人手動／已驗通路轉交精確新版本及影響；各runtime以自己的既有權限用CLI讀Git固定commit，核對原文／dev2狀態／保守有效關係，回報版本或受阻原因。無終端／無權來源就待交接，不能以他人轉述冒充重讀；若另採選配MCP／connector則依其實際loaded view核對，不因此新增自動橋接或host權限。 |

## P1 陌生讀者提問與答案

35個短問答依原生80欄建議整理；全文在各doc章節。原題對照屬[slices-proposal.yaml](slices-proposal.yaml)的interrogation.mapping_by_question，不是native questions.source或fold裁決來源。7 Fact／28 Gap保留；規劃答覆不代表實作驗證。

### S01 提問

| 問題ID／原題 | 短問題 | 短答覆（全文見連結） |
| --- | --- | --- |
| [cli-p1-u03](p1-technical-contract.md#cli-p1-u03) / C03, C07 | 如何沿用原生路徑而不依賴DOT？ | Gap：依配置root讀原生路徑，不搬檔；loader仍待驗。 |
| [cli-p1-u08](p1-technical-contract.md#cli-p1-u08) / C09 | 離線固定commit如何讀取？ | Fact：只讀既有固定commit、不fetch；安全仍待驗。 |
| [cli-p1-u10](p1-technical-contract.md#cli-p1-u10) / C11 | binding配置與fingerprint如何定義？ | Gap：顯式可信配置，摘要排除本機位置；仍待驗。 |
| [cli-p1-u21](p1-technical-contract.md#cli-p1-u21) / C24 | 如何驗證真正權限隔離？ | Fact：隔離須真實權限；局部OS觀測未完成AC1。 |
| [cli-p1-u24](p1-technical-contract.md#cli-p1-u24) / X02 | 可讀不在目前ref的歷史pin嗎？ | Gap：可讀已准本機歷史pin，不稱最新；仍待驗。 |
| [cli-p1-u26](p1-technical-contract.md#cli-p1-u26) / X05 | 如何辨別repo身分與clone別名？ | Gap：可信binding指定repo身分，別名不合併；仍待驗。 |
| [cli-p1-u27](p1-technical-contract.md#cli-p1-u27) / X06 | 省略commit或只給ref怎麼辦？ | Gap：必填完整commit，不默HEAD或解析移動ref；仍待驗。 |
| [cli-p1-u30](p1-technical-contract.md#cli-p1-u30) / X10 | 是否持久保存原文或索引？ | Gap：僅記憶體與本次輸出，不做持久cache；仍待驗。 |
| [cli-p1-u31](p1-technical-contract.md#cli-p1-u31) / X13 | 如何辨認合法空ADR集合？ | Gap：root存在且無ADR才是空；來源錯誤不假空，仍待驗。 |

### S02 提問

| 問題ID／原題 | 短問題 | 短答覆（全文見連結） |
| --- | --- | --- |
| [cli-p1-u07](p1-technical-contract.md#cli-p1-u07) / C08 | 唯讀loader如何避開Git副作用？ | Gap：固定Git物件讀取與環境控制；安全邊界仍待驗。 |
| [cli-p1-u11](p1-technical-contract.md#cli-p1-u11) / C12 | context可觀測與自報如何區分？ | Gap：分觀測、自報與未知，不冒充權威；仍待驗。 |
| [cli-p1-u19](p1-technical-contract.md#cli-p1-u19) / C21, X12 | P1如何提供可重現CLI入口？ | Gap：提案用Node24固定checkout入口；尚未實作驗證。 |
| [cli-p1-u35](p1-technical-contract.md#cli-p1-u35) / X18 | 如何證明三端各自發起查詢？ | Gap：各端留發起與結果回執；Claude真命令回執仍待補。 |

### S04 提問

| 問題ID／原題 | 短問題 | 短答覆（全文見連結） |
| --- | --- | --- |
| [cli-p1-u04](p1-technical-contract.md#cli-p1-u04) / C04 | 精確引用與ADR選取如何區分？ | Gap：完整引用含來源域；NNNN僅作選取，仍待驗。 |
| [cli-p1-u05](p1-technical-contract.md#cli-p1-u05) / C05, C18 | 各repo的view與權限如何分隔？ | Gap：單binding／commit建view，不混權限；仍待驗。 |
| [cli-p1-u13](p1-technical-contract.md#cli-p1-u13) / C14 | 搜尋如何維持原文位置？ | Gap：單view做literal搜尋，保留原文位置；仍待驗。 |
| [cli-p1-u23](p1-technical-contract.md#cli-p1-u23) / X01 | Words是否足以證明裁決權？ | Gap：Words僅歸屬；權威沿可信確認，呈現仍待驗。 |
| [cli-p1-u25](p1-technical-contract.md#cli-p1-u25) / X04 | 來源層級配置衝突怎麼辦？ | Gap：只查已准配置的靜態衝突，不任選；仍待驗。 |

### S10 提問

| 問題ID／原題 | 短問題 | 短答覆（全文見連結） |
| --- | --- | --- |
| [cli-p1-u06](p1-technical-contract.md#cli-p1-u06) / C06 | 如何避免錯誤洩漏來源存在性？ | Gap：未准來源統一拒絕，不探存在；錯誤對照仍待驗。 |
| [cli-p1-u09](p1-technical-contract.md#cli-p1-u09) / C10, X14 | 如何保留原文bytes與digest？ | Gap：先算原bytes摘要，再嚴格解碼；邊界仍待驗。 |
| [cli-p1-u12](p1-technical-contract.md#cli-p1-u12) / C13 | ADR文字是否授權工具動作？ | Gap：原文只作資料，不授權外部動作；輸出仍待驗。 |
| [cli-p1-u17](p1-technical-contract.md#cli-p1-u17) / C19, X08, X11 | 分頁與cursor如何固定查詢？ | Gap：明示分頁完整度，cursor綁固定view；仍待驗。 |
| [cli-p1-u18](p1-technical-contract.md#cli-p1-u18) / C20 | 程式與載入來源版本如何證明？ | Gap：分開code／data／view，以實載來源核對；仍待驗。 |
| [cli-p1-u20](p1-technical-contract.md#cli-p1-u20) / C22 | 快照缺檔能推論原repo缺檔嗎？ | Fact：白名單未帶檔案，不證明原repo缺檔。 |
| [cli-p1-u22](p1-technical-contract.md#cli-p1-u22) / C25 | 三端哪些語義必須一致？ | Gap：固定來源與核心比較語義，時間可異；仍待驗。 |
| [cli-p1-u28](p1-technical-contract.md#cli-p1-u28) / X07 | 同號ADR如何避免任取一份？ | Gap：同號回查詢歧義，可選已列path；仍待驗。 |
| [cli-p1-u32](p1-technical-contract.md#cli-p1-u32) / X15 | 人讀輸出如何處理控制碼？ | Gap：保留原bytes，人讀安全轉義；round-trip仍待驗。 |
| [cli-p1-u33](p1-technical-contract.md#cli-p1-u33) / X16 | 資源超限如何回報？ | Gap：候選limit超限明示錯誤，不截斷；數值未benchmark。 |
| [cli-p1-u34](p1-technical-contract.md#cli-p1-u34) / X17 | 合成驗收的expected從哪裡來？ | Gap：獨立Git blob與人工預期，不用被測parser；仍待驗。 |

### S11 提問

| 問題ID／原題 | 短問題 | 短答覆（全文見連結） |
| --- | --- | --- |
| [cli-p1-u01](p1-technical-contract.md#cli-p1-u01) / C01, C23, X03 | 同一來源壞檔會影響哪些查詢？ | Gap：檢查失敗不改Status；原文可讀，衍生查詢仍待驗。 |
| [cli-p1-u02](p1-technical-contract.md#cli-p1-u02) / C02 | 缺Decision key會改變Accepted嗎？ | Fact：缺key不違反原生格式，Accepted不變。 |
| [cli-p1-u14](p1-technical-contract.md#cli-p1-u14) / C15 | effective與原生規範如何分開？ | Fact：原生無effective；衍生未知不改Status，仍待驗。 |
| [cli-p1-u15](p1-technical-contract.md#cli-p1-u15) / C16 | 版本不同就代表Status不相容嗎？ | Fact：Status規則相同；版本號差異不證不相容。 |
| [cli-p1-u16](p1-technical-contract.md#cli-p1-u16) / C17 | Legacy與歷史Recommended如何讀？ | Gap：沿原生格式與required規則，不加嚴；仍待驗。 |
| [cli-p1-u29](p1-technical-contract.md#cli-p1-u29) / X09 | 查不到與效力未知如何區分？ | Fact：原文查無與衍生未知分開；CLI錯誤仍待驗。 |

## 跨活動規則

| ID | 規則 |
| --- | --- |
| R1 | 每位使用者指定獨立決策Git repo；共用code不攜帶私人ADR／憑證。使用者隔離依實際OS／filesystem／GitHub權限或獨立環境驗證，不以label或CLI allowlist冒充tenant security。 |
| R2 | 總指揮裁示與工程 ADR 的權限、適用範圍、來源及裁決者分開；同一引擎不授予同一裁決權。 |
| R3 | 工程 ADR 留在各自 repo，可引用上層決策版本，不能以 supersession 或較新時間覆蓋上層。 |
| R4 | ADR、Accepted、合併、身分驗證與行動許可是不同事實；OS／process context、gh帳號、Git remote credential、Sites owner與裁決權也分開。agent可沿用同一合法owner身分協作，任務及驗收仍由dev2／Spacedock負責。 |
| R5 | 有效判定保留原文與精確來源；含糊、衝突、無權限或版本不明不能補猜為已生效。 |
| R6 | 版本分code package／core／contract、各ADR repo immutable commit及每runtime loaded view；checkout按已配置repo/ref觀測，選配遠端host另報，不合成全部最新旗標。 |
| R7 | 唯讀CLI不做Git更新或寫入；由checkout持有者依D2用既有Git工具更新。dirty、領先、分岔、遠端未知不覆寫，更新後重讀受影響ADR。 |
| R8 | 來源隔離與機敏資料留在原保護來源；公開案例使用合成資料。裁示、讀取權限與本次外部動作授權分開核對，提交、merge、部署、host 維護及新增存取須有各自適用授權。 |
| R9 | ADR 沿用 dev2 格式與配號；實質變更新檔，小修留原檔，原話及歷史不改寫。 |

## 責任與交接

| ID | 負責者 | 活動範圍 | 說明 |
| --- | --- | --- | --- |
| O1 | 使用者／該層級獲授權決策者 | A1 → A4 | 裁決權依適用層級人類授權；OS／process context、gh帳號或Sites owner不自動賦予它。 |
| O2 | 各runtime／checkout持有者；選配host另由原維護者負責 | A5 → A5 | agent透過既有Git操作code／data checkout，CLI只重讀與回報loaded view；S17遠端host維護延後。 |
| O3 | 接手 agent 與既有 dev2／Spacedock 流程 | A6 → A7 | 每位接手者須有已授權CLI執行／來源存取路徑；CLI提供依據，既有dev2／Spacedock保有任務與驗收權威。 |
| O4 | 使用者／原適用層級決策者 | A8 → A3 | 新證據回到討論與確認，不能由工具自動批准。 |

P1 六條 AC、各片範圍／依賴及 D1–D5 見 [切片地圖](slice-map.md)；它們的編輯來源是 [slices-proposal.yaml](slices-proposal.yaml)。新需求接受後須先重整 full-map baseline，再依既有 admission 做 cut／brief／handoff；原 profile／投入／P1 選擇不用重選。

原生ADR格式／Status／配號／驗收與feedback沿dev2；原生lint整體check fail不改其他Accepted。已撤回整binding一律unresolved策略，衍生effective只作非權威查詢；見[dev2原生對齊](p1-technical-contract.md#native-dev2-alignment)。
