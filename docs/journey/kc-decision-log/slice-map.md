# kc-decision-log 切片地圖

**D5：CLI 優先、MCP 視需要選配；本PR為規劃設計；CLI未實作／部署，非ready handoff。** P1 已於 2026-10-20 重切為「帶著精確裁示走完一次交接」並選定，profile 為 Pilot，投入四個完整工作日。其他切片仍候選，不一次啟動六片。

六片名稱、成果及故事歸屬以原生 [journey.yaml](journey.yaml) 的 releases／stories[].release 為準；本頁保存範圍、依賴與驗收說明。原生 Story map 顯示六條 release band，六個 journey-board 頁顯示各片故事與問答；各片的 slice-Px 問答連至本頁。P1 已選，其餘仍為候選。工作模型見 [CLI 設計](cli-first-design.md)，完整活動見 [故事地圖](story-map.md)。

## 六片與順序

| 片 | 狀態 | 故事 | 端到端成果 |
| --- | --- | --- | --- |
| P1 帶著精確裁示走完一次交接 | 已選／Pilot | S01, S10, S11, S19, S20, S21, S22 | 使用者指定一個獨立決策repo與完整commit後，Claude以CLI讀出一筆裁示的精確引用與原狀態並交給Codex；Codex在自己的已授權環境以同一CLI重讀核對，經既有dev2／Spacedock完成一個合成任務，使用者取回對應該引用的原始執行與驗收證據。 |
| P2 查明各方版本差異 | 候選 | S13, S14, S27 | 接手者分清各runtime的CLI code／ADR checkout與loaded view，知道已配置checkout相對ref的五態、時間及dirty阻礙；選配遠端host只在實際採用時另列。 |
| P3 安全對齊並重新讀取 | 候選 | S15, S16, S18 | 各runtime持有者依既有Git權限安全更新已配置checkout或保留原狀並說明，再用CLI重讀實際ADR commit與loaded view；不以本片維護遠端host。 |
| P4a 第三端加入並看出差距 | 候選 | S02, S23 | dot經已授權且可執行CLI的路徑讀取同一裁示並參與交接；接手者以原任務證據整理裁示與結果之間的預期、實際、未知與影響。 |
| P4b 處理跨層衝突並重新裁示 | 候選 | S04, S05, S06, S24, S26 | 工程方案引用的上層版本改變或出現衝突時，工程 agent 能呈現影響、交回適用決策者，並把確認後的新版本重新交接。 |
| P5 把確認草案送成受控 PR | 候選 | S07, S08, S09, S25 | 在已配置來源內，使用者確認精確內容、範圍與 base 後，獲准提交者建立一個可審查 PR，回讀 PR 身分與提交內容，證明沒有重複或越權。此片的完成不等待 merge、ADR Accepted 或 host 載入。 |

## 投入與入場

- appetite：4 days。使用者原話「1-3天」，其後澄清為「三個完整工作日」；2026-10-20 回覆「1 照建議」改為四個完整工作日，範圍不動。
- estimate：P1 粗估 16–30 active 工程小時，未經同類交付校準；上限 30 小時以 8 小時一天換算為 3.75 天，在四天投入內；依據與假設見 [P1 估工](p1-estimate.md)。估算未校準，不保證做完。
- 重切前 P1（S01, S02, S04, S10, S11）的 32–48 小時粗估不再適用；它計入了已移出本片的雙使用者隔離測試與三端驗收。
- P1 之後逐片以小批次規劃、驗證與決定；沒有一次啟動全部候選切片。

歷史 MCP 入場文件不是新 CLI 來源的 baseline 或 acceptance。依原有 [release slicing](../../../kc-journey-map/skills/kc-journey-map/references/release-slicing.md) 的 cut／brief／handoff 進行，不以舊 hash 製造通過。

## P1

**帶著精確裁示走完一次交接**

使用者指定一個獨立決策repo與完整commit後，Claude以CLI讀出一筆裁示的精確引用與原狀態並交給Codex；Codex在自己的已授權環境以同一CLI重讀核對，經既有dev2／Spacedock完成一個合成任務，使用者取回對應該引用的原始執行與驗收證據。

**故事：** S01, S10, S11, S19, S20, S21, S22。狀態：已選，Pilot。

**重切來源：** 2026-10-20 使用者回覆「重切」，並以「可以」接受上述七張故事為新 P1。重切前 P1 是 S01, S02, S04, S10, S11；S02 移至 P4a，S04 移至 P4b，S19–S22 自原 P4a 移入。卡片文字與 ID 不變。

**沿用與新工作：** S21、S22 沿用既有 dev2／Spacedock 任務、gate 與 Git／gh 證據入口，沒有第二份任務系統。新工作是最小 CLI（S01、S10、S11）與 Claude→Codex 經任務紀錄交接、接手者重讀（S19、S20）。既有查詢原型在使用者的私人決策 repo：`parse`／`makeSnapshot`／`effective` 與 `createService` 已存在，build 已從固定 Git commit 讀 ADR；沒有 CLI 入口（2026-10-20 讀取該 repo 確認）。

**範圍**

- 一個已配置的合成決策 repo binding；CLI 只讀它，必填完整 commit，不默用 HEAD／ref、不 fetch
- 依 binding 的 ADR root 讀原生 dev2 路徑，回傳 repo、path、ADR ID、完整 commit、原文 digest 與原 Status，JSON 與人讀兩種輸出
- 保守 effective 沿用原型規則（D9）：有 Decision key 且同 key 只有一筆的明示 Accepted，或同 binding 明示 `Superseded by` 鏈末端的這種 Accepted 才算生效，其餘 unresolved；合成資料帶 Decision key
- 一個簡短的唯讀 skill（D10）：拿到裁示引用時先以 CLI 重讀、比對指紋，不一致就停；Claude 與 Codex 都能載入
- Claude 協調者把讀出的引用寫進任務二的任務說明，Codex 從任務紀錄讀取，並在自己的已授權環境以同一 CLI 重讀核對；使用者不轉述（D1）
- 兩個 dev2 任務（D7）：任務一由 Claude 協調者做 CLI；任務二由 Paseo 啟動的 Codex 協調者執行合成任務，其 worker 先以 CLI 重讀再動手
- 合成任務是一個由合成裁示決定的 CLI 小功能，做到 PR 合併；使用者取回對應該引用的 task／gate／PR 證據

**不做**

- dot 端讀取或交接（P4a；dot 無終端機，需 MCP／connector）
- hook（D10，見 S30）
- 多個決策 repo、上層／工程層級分隔與跨層引用（P4b）
- 兩個使用者之間的作業系統隔離驗證（移至 P4b）；本片不宣稱租戶隔離
- CLI 寫入 Git、配號、建 task、開 PR 或 merge；自動 Git 更新、package 升級或部署
- 自動跨 agent 橋接、替其他 agent 回答權限提示；把 ADR 文字當成行動授權
- 新增 GitHub 帳號、憑證或存取權

**依賴與現況**

| 依賴 | 性質 | 可用性／限制 |
| --- | --- | --- |
| 使用者私人決策 repo 內的既有查詢原型 | 實作基礎 | 存在且有測試；`SOURCE_PATH` 綁 `projects/KEY/docs/adr`，需改為依 binding 的 ADR root。核心複製並改寫進 `kc-decision-log` plugin，原型不動（D8）。 |
| Claude 本機以 Git 讀固定 commit | 交接起點 | 2026-10-20 Claude 在本機以 `git show <完整commit>:<ADR path>` 讀出一筆既有 ADR，exit 0。這只證明 Git 路徑可用，不是新 CLI 的驗收。 |
| Codex 協調者與 Codex worker 在同一台機器執行 CLI 並讀同一 clone | 交接接手端（D7） | 由 Paseo 啟動 Codex 協調者；Spacedock 的 worker 執行環境跟隨協調者，Claude 協調者不能派 Codex worker。Codex 環境的 Node 24 與 clone 讀取未驗；Codex 不執行合併。 |
| 既有 dev2／Spacedock 流程 | S21、S22 的任務與證據入口 | 本 repo 有 `docs/dev2` workflow；合成任務尚未建立。 |

**驗收條件**

- P1-AC1：合成決策 repo 是唯一已配置 binding；CLI 對未配置 binding、錯 repo／path、缺 commit 或非完整 commit 拒絕並以非零 exit 結束，不同原因可有不同訊息（P1 不宣稱隔離）；不把 caller 自稱或任意路徑當授權，不新增存取。
- P1-AC2：CLI 固定讀 D0 時，即使 ref 後來前進到 D1 仍只宣稱 D0；回傳 repo、path、ADR ID、完整 commit、原文 digest 與原 Status，JSON 與人讀模式對照同一結果。
- P1-AC3：用合成 Accepted（帶 Decision key）、Proposed、同 binding 明示取代、缺 Decision key、同 key 兩筆 Accepted 與壞鏈資料，CLI 照原文報 Status；effective 依 D9，缺 key 與同 key 多筆 Accepted 皆 unresolved；不改原文；unresolved 與工具失敗分開。
- P1-AC4：Claude 協調者把讀出的引用寫進任務二的任務說明，標明傳出者、接手者、原任務與 repo／ADR／commit／digest，使用者不轉述；Codex worker 在自己的已授權環境實際執行同一 CLI 重讀，由 CLI 以預期內容指紋比對，不符即非零 exit；只有 effective 指向被轉交的那一筆才開工，未定或被取代就停下回報，不默默改執行目標。貼文自稱或另一端登入不算本端通過。
- P1-AC5：合成 ADR 寫「部署／發訊」時，任務紀錄中沒有任何部署或發訊動作；peer 權限提示交回原持有者或使用者，FO 不代答。
- P1-AC6：經既有 dev2／Spacedock 完成一個合成任務，PR 由使用者合併或逐 PR 授權 Claude 協調者合併；使用者取回原 task／gate／PR 引用，核對它對應本次任務內容、回合與採用的 ADR commit。無法證明關聯就顯示未知；不複製受保護日誌、不另造台帳。

- P1-AC7：唯讀 skill 讓 agent 拿到裁示引用時先以 CLI 重讀、比對指紋，不一致就停；任務二的 Codex worker 實際使用並留下紀錄。

P1-AC1–AC6 與其修改由使用者 2026-10-20 回覆「同意」接受；AC7 隨 D10 加入。

**移除測試：** S01 沒有可讀且可拒絕的來源；S10 交接只剩轉述；S11 接手者可能照仍在提議或已被取代的裁示行動；S19 交接段不存在；S20 「讀的是同一份」只能靠對方自稱；S21 沒有執行入口；S22 證據回不到使用者，迴圈不閉合。移除任一張，本片的端到端成果就不成立。

## P1技術契約與投入提案

[P1技術契約](p1-technical-contract.md) 是為重切前 P1（S01, S02, S04, S10, S11）寫的 35 個技術問答，包含已移出本片的三端、隔離與多來源議題。新 P1 只取其中與單一 binding 讀取、原文 digest、原 Status 和保守 effective 有關的部分；dev2 ideation 依新驗收條件選用，契約內容不是已接受的 API。重切後的估工見 [P1 估工](p1-estimate.md)。

## P2

**查明各方版本差異**

接手者分清各runtime的CLI code／ADR checkout與loaded view，知道已配置checkout相對ref的五態、時間及dirty阻礙；選配遠端host只在實際採用時另列。

**故事：** S13, S14, S27。狀態：候選。

**沿用與新工作：** 沿用P1 CLI精確引用與context；Git提供已准來源的remote／ancestry查核。MCP／Sites不是必要前提；package無Git checkout照實不適用。

**範圍**

- code／data checkout分role，按repo/ref比對commit與祖先
- 每runtime loaded view的data revision／digest／時間與所用core分開
- remote unknown／source mismatch／缺commit／無checkout的誠實回應
- 本機dirty／分支阻礙唯讀觀測；ADR影響分析留P3
- 選配host若存在，分開回報其snapshot，無host不阻擋本片

**不做**

- 修改checkout、reset／stash、loaded view替換或host切換
- 把Git五態當成已安裝package／contract／部署已更新
- CLI／MCP根據client自報commit直接修改檔案
- 未配置來源掃描、登入／新增存取或背景監控

**依賴與現況**

| 依賴 | 性質 | 可用性／限制 |
| --- | --- | --- |
| P1 | 硬依賴 | 已選Pilot但CLI與交接驗收尚未完成；以當時實際證據為準。 |
| 各runtime既有Git遠端目標與ancestry觀測權限 | 查核前提 | 須逐runtime定位；offline／無權／history不足回unknown，不從本機一端權限推定其他端。 |
| 選配host的既有唯讀provenance | 僅採用遠端adapter時適用 | 不是CLI候選P2的必要依賴，缺此能力只限制該host觀測。 |

**驗收條件**

- P2-AC1：合成 Git 圖逐一顯示一致、落後、領先、分岔；遠端查詢失敗時，即使舊 cache SHA 相等也顯示遠端未知。
- P2-AC2：一個runtime的loaded view仍D0、data checkout已D1而code checkout一致時，分別回報；另一runtime可不同，不合成全部最新。若採用host另列其revision，不用host有無決定CLI驗收。
- P2-AC3：repo/ref不符、commit缺失、未配置來源不猜；package無code checkout或某runtime無data checkout顯示不適用，不捏造一致；offline／祖先不足回remote unknown並附時間。
- P2-AC4：分別準備 staged、unstaged、未追蹤檔與來源／分支不符案例，呈現可理解的阻礙及下一步；前後 Git commit／檔案保持一致，不進行更新或 ADR 影響分析。

**移除測試：** S13 不在就不知道比較哪個 repo／ref；S14 不在就不知道五態；S27 不在就無法回答本片承諾的本機更新阻礙。三者均直接支撐本片終點。

## P3

**安全對齊並重新讀取**

各runtime持有者依既有Git權限安全更新已配置checkout或保留原狀並說明，再用CLI重讀實際ADR commit與loaded view；不以本片維護遠端host。

**故事：** S15, S16, S18。狀態：候選。

**沿用與新工作：** D2由checkout持有者用既有Git工具執行；CLI僅讀固定commit並回報。遠端host維護S17已明示延後，不是本片依賴。

**範圍**

- 依已准來源的新舊版本列出受影響ADR及上層引用，未知則擴大重讀／停止
- 乾淨、behind、可fast-forward才由持有者依D2自行更新
- 各runtime依實際新data commit重讀CLI loaded view，不沿用舊判定
- 區分更新成功、讀取／驗證失敗與ref race；若有last-good明示舊revision

**不做**

- dirty強制reset、自動stash、覆蓋領先／分岔或靜默切分支
- CLI／MCP代做Git更新、package升級或外部動作
- 遠端host候選切換／部署／MCP維護（S17延後）
- 自動通知、持續輪詢或新增背景授權

**依賴與現況**

| 依賴 | 性質 | 可用性／限制 |
| --- | --- | --- |
| P2 | 建議順序，非硬依賴 | 可由當次既有Git查核提供必要證據，不要求P2全部code／data／loaded-view診斷產品先交付；替代途徑尚未端到端驗證，無法核實即unknown／停止。 |
| P1固定版本讀取，以及各checkout持有者既有Git權限／當次安全查核 | 不可跳過的能力／證據前提 | 動作前在本runtime重查repo/ref、HEAD／target、ancestry、dirty與ref race，確認D2條件；更新後以CLI核對實際commit並重讀。可沿既有Git完成，不新增權限、不依賴host；不能核實則保留／停止，不宣稱已有端到端替代實證。 |

**驗收條件**

- P3-AC1：agent 查到已配置 repo／ref 的合成 checkout 乾淨、落後且可 fast-forward，重新查核後不逐次等待使用者確認即完成更新；回報來源、操作身分及實際 commit，重讀受影響 ADR 原文與有效判定。
- P3-AC2：dirty、領先、分岔、遠端未知、來源不符及更新期間 ref 變動時，不覆蓋修改、不自動改支線；以可驗證原因停止依賴該更新的動作。
- P3-AC3：持有者更新合成data checkout後，CLI重讀並回報實際D1；讀取／驗證失敗不能把D0標D1，若有last-good則明示舊commit／未知。此條驗runtime loaded view，不要求維護遠端host。
- P3-AC4：一runtime code checkout已更新但installed package或loaded view仍舊，或不同runtime data commit不同，分開呈現；ref在兩次呼叫間移動時重新取得精確引用，不自動安裝／部署。
- P3-AC5：合成更名、刪除、替代鏈及上層引用變動能進入重讀範圍；既有引用不可讀或不能證明完整時保守擴大為該作用域全部裁示，或停止並回報，不能漏讀後繼續。
- P3-AC6：每runtime的Git更新與CLI重讀回執標明操作者／context、來源、前後data commit與成功／停止原因；D2不新增host維護、package安裝、部署或背景執行權限。

**移除測試：** S15界定需重讀的影響；S16由持有者完成安全checkout更新；S18證明CLI loaded view與判定已重讀。移除任一就無法安全重新採用新裁示。S17只服務選配遠端host，非CLI成果必要，留在全圖延後。

## P4a

**第三端加入並看出差距**

dot經已授權且可執行CLI的路徑讀取同一裁示並參與交接；接手者以原任務證據整理裁示與結果之間的預期、實際、未知與影響。

**故事：** S02, S23。狀態：候選。

**重切說明：** 2026-10-20 P1 重切後，原 P4a 的 S19–S22 移入 P1；S02 自原 P1 移入本片，S23 留在本片。本片改名、改目標，以及 S04 與舊 P1-AC1／AC3 移至 P4b，由使用者 2026-10-20 回覆「照建議」接受。

**沿用與新工作：** 沿用 P1 的 CLI、經任務紀錄的交接與 dev2／Spacedock 證據入口；新工作是 dot 端的已授權執行路徑，以及以原任務證據整理差距。

**範圍**

- dot 經已授權 delegated local task 或 cloud runtime 實際執行同一 CLI，讀取同一精確裁示
- dot 參與 P1 的交接路徑，不另要求 dot 前端直接 shell，不推定 cloud 繼承本機登入或 localhost
- 接手者在可核對的執行 context 內，用原任務證據整理預期、實際觀測、未知與影響

**不做**

- 自動跨 agent 橋接或替其他 agent 回答權限提示
- 把差距摘要當成原驗收，或把敏感執行日誌複製進共用 code repo
- 把每次工程回報自動變成 Accepted 裁示

**依賴與現況**

| 依賴 | 性質 | 可用性／限制 |
| --- | --- | --- |
| P1 | 硬依賴 | CLI 與 Claude→Codex 交接須先成立。 |
| dot 讀取同一裁示的路徑 | 驗收條件 | dot 是 ChatGPT 上的 agent，沒有終端機，Paseo 只在本機，dot 連不到（使用者決策 repo 的 DOT#0008 記為延後）；需 MCP／connector（D5、D13）。 |

**驗收條件**

- P4a-AC1：dot 經已授權可執行命令的本機連線 task 或 cloud runtime，實際執行同 core／contract CLI 查詢同一合成 ADR；回傳 repo、path、ID、完整 commit、digest 與原狀態／effective，可與 Claude、Codex 的結果對照一致。help、轉述或另一端 gh 登入不算本端通過；無可用路徑時明列失敗或未驗。
- P4a-AC2：接手者以原任務證據整理裁示與結果之間的預期、實際、未知與影響；CLI 讀取裁示不等於能讀敏感執行日誌，證據保留在原保護來源。
- P4a-AC3：接手版本已落後或裁示前提改變時，回原任務流程重審；不默默改執行目標。

**移除測試：** S02 不在就沒有第三端；S23 不在，使用者只拿到原始證據而看不出裁示與結果的差距。

## P4b

**處理跨層衝突並重新裁示**

工程方案引用的上層版本改變或出現衝突時，工程 agent 能呈現影響、交回適用決策者，並把確認後的新版本重新交接。

**故事：** S04, S05, S06, S24, S26。狀態：候選。S04 於 2026-10-20 自原 P1 移入：第二個決策來源在本片出現，權威域分隔隨之進來。

**沿用與新工作：** 沿用P1人工交接通路及原流程；新版本以既有Git修訂／審查與人類確認取得，再用CLI精確重讀，不依賴寫入CLI或MCP。

**範圍**

- 工程 ADR 固定引用上層版本
- 跨層矛盾及上層變動的回報
- 原適用決策者重審
- 重新交接並由既有任務流程處理範圍變動
- 沿用 dev2 一決策一檔、原配號與取代狀態；實質變更新 ADR，小修保存原檔

**不做**

- 由工程 ADR 自動覆蓋總指揮裁示
- 自然語言矛盾的完備自動判定
- 工具自動確認新裁示
- 自動推送或批量重排進行中任務
- 自動跨 agent 橋接或替其他 agent 回答權限提示

**依賴與現況**

| 依賴 | 性質 | 可用性／限制 |
| --- | --- | --- |
| P1 | 硬依賴 | 已選，尚未驗收 |
| 上層引用及跨層衝突的表達方式 | 設計前提 | 欄位機制仍為草案；先以引用與人工指明衝突，不宣稱模型能完備辨識矛盾 |
| 適用決策者的精確確認及確認後 Git 版本的可讀路徑 | 人工重審與再交接前提 | 沿用可信確認來源與既有Git提交；各runtime按本端既有權限以CLI讀精確commit。若僅能用選配遠端adapter，按其實際loaded view另驗，讀不到就待交接；不因CLI方向新增host維護或登入授權。D4仍沿用原機制。 |

**驗收條件**

- P4b-AC1：合成工程 ADR 引用總指揮 D0，當 D1 改變適用前提時，呈現原引用與影響；工程 repo 的較新 commit 不自動勝出。
- P4b-AC2：明示跨層衝突時停止依賴衝突裁示的動作，將問題交回適用決策者；同層替代與跨層引用不混成一條鏈。
- P4b-AC3：由適用決策者確認維持／改變後，接手者重讀明確版本，原 dev2／Spacedock 流程處理範圍變更；原決策及證據可追溯。
- P4b-AC4：由使用者將問題與重新確認後的精確版本逐段交回；每位接手者自行核對身分、空間及讀取權限。尚未驗證的自動通路不可作為本片成功前提。
- P4b-AC5：人類確認綁定 repo、層級／scope、可讀原文／diff、精確內容及 base，可信出處可核對；內容／base 改變重新檢視確認。git author、agent 整理或無權出處不視為裁決；裁示確認不補授權 Git 動作。
- P4b-AC6：D1已確認後，接手者以本端已准CLI/Git路徑核對原文、明示狀態／有效關係及精確commit；不能證明就待交接。若某端只用選配adapter且loaded view仍D0，明列該端受阻，不視為全體已重讀；使用者確認受影響者，每人版本／原因可核對，不新增自動橋接或host權限。
- P4b-AC7：合成實質改變經原權威確認後，沿用目標來源 dev2 配號與四章模板形成新 ADR，取代時舊 Status 指向新號且原話／歷史可追。新稿 Proposed 或未確認時不提前切換；只在同層同來源維護取代鏈，工程對上層只固定版本引用。

- P4b-AC8：分開的合成上層／工程 Git repos 各保留實際原文 path 並配置明確 binding，各自回報 commit；同號不碰撞，supersession 限同來源／層級／scope，工程不能反向覆蓋上層。查詢前依已准 context 分隔來源；無權或不可讀來源保持未知。（自重切前 P1-AC3 移入）
- P4b-AC9：以實際 OS／filesystem／GitHub 權限或獨立執行環境分隔的兩個合成使用者，驗證無權 context 不能取得另一人的索引、原文或 source metadata；兩個 label 或 binding allowlist 不能當隔離證據。（自重切前 P1-AC1 移入）

**移除測試：** S04 不在就無法分清兩個來源的裁決權。只有單任務交接，無法處理上層方向變更；引用版本、拒絕反向覆蓋、回到原裁決者與重新交接缺一，就不能完成一次跨層重新決策。

## P5

**把確認草案送成受控 PR**

在已配置來源內，使用者確認精確內容、範圍與 base 後，獲准提交者建立一個可審查 PR，回讀 PR 身分與提交內容，證明沒有重複或越權。此片的完成不等待 merge、ADR Accepted 或 host 載入。

**故事：** S07, S08, S09, S25。狀態：候選。

**沿用與新工作：** agent沿用既有且本次獲准的git／gh或原Git／PR工具；CLI與選配MCP維持唯讀，不配號或建task。無Git能力由使用者轉交，PR審查／merge仍由原流程；CLI讀取不依賴本片。

**範圍**

- 本次明確範圍及內容確認
- 受控草案／PR 與 base commit 衝突檢查
- 重試可辨識既有結果而非重複 PR
- 回讀 PR URL／提交版本與 diff，保留確認出處及原文歷史；merge／Accepted／host 載入分開追蹤
- 每次一個新裁示沿用 dev2 原 FO 配號、模板與 lint；必要時同一變更包含舊裁示狀態更新，小修不取新號

**不做**

- 建立 PR 就自動 Accepted 或 merge
- 默示廣泛 repo 寫入、配發憑證或授予外部動作許可
- 直接改工程 repo 來更新總指揮裁示
- 覆蓋新的遠端變更或刪除原文歷史
- 來源設定的變更管理與方案比較介面
- 把PR建立當成各runtime已重讀或選配host已載入；CLI重讀依實際commit，遠端host維護S17延後或沿既有獲准途徑。
- 寫入 MCP、host 代寫與新憑證／權限配發；本片只沿用既有 Git／PR 工具

**依賴與現況**

| 依賴 | 性質 | 可用性／限制 |
| --- | --- | --- |
| P1來源與精確內容讀取 | 硬依賴 | 須能辨識已准來源與待提交原文，仍以P1實際驗收證據為準。 |
| P2 | 建議順序，非硬依賴 | 不要求完整code／data／loaded-view診斷產品；可由當次既有Git／PR查核提供base與前次結果證據，尚未端到端驗證此替代路徑。 |
| P1、P4b | 建議先完成 | 先驗證跨 agent 如何讀及交接，避免先擴寫入權限 |
| 目標 repo 既有 dev2 配號、Git 動作許可與 PR 審查途徑 | 執行及驗收前提 | D3/D4不變，D5僅改CLI優先入口；以各runtime現有git/gh及原FO／number guard／審查權限核對本次動作。CLI不另造寫入、配號或任務系統；缺途徑回原權威。 |
| 已准來源／base／diff、前次不確定結果與提交前重查 | 不可跳過的能力／證據前提 | 提交前由持有者用既有Git／PR工具核對本次權限、來源、base、精確diff及可能既有PR／提交；base移動或前次結果不能查明就停止／待確認，不以P2未交付略過。 |

**驗收條件**

- P5-AC1：只對明確確認過的合成 diff、repo、層級、範圍與 base 產生一次可審查 PR；未確認及越權內容拒絕。
- P5-AC2：送出前 base 已改變則不覆蓋；檢查不確定的前次結果後才重試，不製造重複變更。
- P5-AC3：建立 PR、merge、ADR Accepted 與有效判定分別呈現；內容變更重新確認；未批准的替代目標仍 unresolved。
- P5-AC4：實質變更新 ADR、小修留原檔；保留原話、確認出處及 Git 歷史，PR 後回讀精確提交／diff。取代使用 dev2 舊 Status 的 Superseded by NNNN；新稿 Proposed 不提前替代。未 merge、未 Accepted 或未被 host 載入各自呈現，不影響「可審查 PR 已建立」的完成終點。
- P5-AC5：持有該runtime既有適用權限的agent用git／gh或原Git／PR工具完成本次獲准提交；無能力者由使用者依D1轉交。CLI與選配MCP不接受寫入／配號／建task指令，沒有host代寫、新憑證或背景動作；gh帳號不代替裁決／本次動作許可。
- P5-AC6：合成確認出處不可讀、錯決策層級／scope、內容或 base 改變時，保留待確認並回到適用決策者；分清內容確認與本次 Git 動作許可。agent 自述或 author 欄位不能代替原可信出處。
- P5-AC7：新裁示草案無預配編號；由目標 repo 原 FO 在原實作 dispatch 使用 number_guards reserve，按原 task 保留 ADR 號且不撞號／補洞；需第二個新裁示回 FO。驗收沿用 adr_lint --since &lt;base&gt; 加原預約／報告的 --require，保存實際結果；本工具不另配號或自動判斷語義小修。
- P5-AC8：合成不改意思的小修留原 ADR，Git 可重現前後版本且原話不被改造；觸及缺 Recommended 的舊檔只按 dev2 記 not recorded。實質語義變更不得包裝小修，分類含糊回原裁決者；不新增 ADR 第五章、YAML 狀態或跨層 supersedes。

**移除測試：** S07 保存確認依據；S08 綁定本次內容及範圍；S09 建立及回讀唯一 PR；S25 保留原文與新舊關係。移除任一項就無法證明本片提交的是正確、獲准且可追溯的變更。S03 設定管理與 S28 方案比較不影響固定來源內建立 PR，保留在全圖而延後。

## 延後但保留在完整故事

| 故事 | 使用者卡片 | 原因 |
| --- | --- | --- |
| S12 | 我分清查不到與沒有讀取權限 | P1 必須保有不洩漏的錯誤及安全下一步；更細的使用者診斷體驗暫不承諾獨立交付片。 |
| S03 | 我能改設定而不誤讀別人的庫 | 第一版使用明確且固定的來源配置；變更來源的管理體驗不是固定來源內建立 PR 的必要條件，隔離驗證在 P4b。 |
| S28 | 我比較可選方案再形成草案 | 方案比較可先沿用既有討論方式；在已確認內容後建立 PR 的片段不另建比較介面。 |
| S17 | 我讓 host 載入可驗證的新裁示 | CLI-first當前P1/P3成果不需遠端host維護；保留故事與last-good要求，日後確定選配遠端adapter需求及既有授權後再排，不新增slice或把host當CLI前提。 |

## 已確認選擇

D1–D4 原由先前規劃標為已確認，但已索引紀錄找不到使用者原話；2026-10-20 使用者逐條裁決如下各條。D7–D13 部分內容來自 2026-10-20 一次提出的 11 題，使用者回覆「同意」全部接受。

### D1 P4 協作交接通路

交接由 agent 經既有任務紀錄完成，使用者不轉述：傳出的 agent 把精確引用寫進接手任務的任務說明，接手的 agent 從任務紀錄讀取並自行重讀。原先「使用者先轉交」被否決；agent 之間的自動推送延後。這項選擇本身不新增外部動作授權。

使用者 2026-10-20：「D1手動轉交不是很好，不就等於我再講一次？」P4b-AC4 等後片仍寫手動轉交的條文，待該片規劃時改寫。

影響：S19, S20, S22, S26, P1, P4b。

### D2 checkout 安全更新觸發

agent 查到已配置 repo／ref 落後、工作目錄乾淨且可 fast-forward 時，依既定規則自行更新、重讀受影響 ADR 並回報；其他狀態保留原狀並說明原因。

已確認：符合既定條件即可自行更新、重讀並回報；仍由各 checkout 持有者在既有權限內操作。使用者 2026-10-20：「D2 我同意」。

影響：S16, S18, P3。

### D3 ADR 提交入口

Agent 用既有 Git／PR 工具；kc-decision-log MCP 先維持唯讀，寫入 MCP 及 host 代寫延後。

P1 照此確認：CLI 唯讀，寫入走既有 Git／PR，實際提交仍核對本次適用授權。後續方向（P5）：同一個 CLI 包住 gh 與 Git 提供寫入命令，agent 只需 repo 權限與這一個工具；合併仍由使用者決定（D12）。使用者 2026-10-20：「D3 現在可以，但是應該要有更聰明的辦法，例如只要給 repo 權限，把 gh 抽象化，只保留一個 cli 工具？」

影響：S09, P5。

### D4 ADR 修訂與 dev2 對齊

實質變更新建 ADR，小修留原 ADR；格式、狀態、取代關係、配號及原審查沿用 dev2 既有機制，不另創一套。

已確認的 ADR 修訂政策，與 repo 內 dev2 模板、配號及審查機制對齊；不擴大其他權限。使用者 2026-10-20：「D4 同意」。

影響：S11, S24, S25, S26, P4b, P5。

### D5 CLI優先、MCP選配的讀取入口

採CLI-first：各agent有可執行命令且有repo存取權時，用同core的CLI讀取／搜尋／effective／精確引用；git負責版本與安全更新，gh或既有工具負責GitHub身分／PR，MCP僅在需要時選配。

使用者提出CLI加本機gh的方向，確認三端仍需有各自已准執行環境／身份／來源路徑後，明確答覆「可以，就這個方向」。此決定授權記錄方向與書面設計，不授權實作、安裝、auth、提交／push／PR或部署。

原以hosted MCP／Sites為P1必要讀取入口的方向由CLI優先取代；D1-D4及各repo決策權威保留。歷史OAuth失敗仍是當時路徑證據，不要求先修好，也不標成已解決。

影響：P1, P2, P3, P4a, P4b, P5, S01, S02, S04, S08, S09, S10, S11, S13, S14, S15, S16, S17, S18, S19, S20, S22, S23, S26。

### D6 決策空間與層級

通用工具、多個決策空間，各自是獨立 repo；小範圍決策以明確版本引用大範圍決策，推導出的決定仍由使用者確認。

使用者 2026-10-20 回覆「同意」。影響：S05、S29、P4b。

### D7 P1 兩個任務

任務一由 Claude 協調者與 Claude worker 做 CLI（S01、S10、S11）。任務二由 Paseo 啟動的 Codex 協調者執行合成任務，其 Codex worker 先以 CLI 重讀再動手；Codex 跑不起 CLI 即 P1 未過，不以 `git show` 代替。合成任務是一個由合成裁示決定的 CLI 小功能，做到 PR 合併才算完成：由使用者合併或逐 PR 授權 Claude 協調者合併，Codex 不合併。

使用者 2026-10-20 回覆「可以」（兩個任務）與「同意」（完成終點）。影響：P1、S19–S22。

### D8 程式位置與 plugin

CLI 做成 kc-claude-plugins 的 `kc-decision-log` plugin，自原型複製並改寫查詢核心，原型不動。0.1.0 起登記 marketplace 並標實驗中，因為 `version-parity-check.sh` 要求每個 plugin 目錄都有登記；先本機測試安裝，再接 release-please。

使用者 2026-10-20 回覆「放在plugin沒問題」與「同意」。影響：P1。

### D9 P1 生效判定沿用原型規則

沒有 Decision key 的 Accepted，或同 binding 同 key 有多筆 Accepted，皆為 unresolved；合成資料比照真實紀錄帶 Decision key（2026-10-20 檢查：使用者決策 repo 的 15 筆紀錄都有）。工程 repo 的 dev2 ADR 沒有 Decision key，其判定規則延到工具開始讀工程 repo 時再定。

使用者 2026-10-20 回覆「同意」。影響：S11、P1-AC3。

### D10 唯讀 skill 與 hook

P1 交付一個簡短的唯讀 skill：拿到裁示引用時先以 CLI 重讀、比對指紋，不一致就停。hook 不進 P1；它與 dev2 的 ADR 標題 hook 共用機制，即 dev2 待辦任務 `agent-reads-governing-adr`（2026-10-20 建立），見 S30。

使用者 2026-10-20 回覆「同意」。影響：P1-AC7、S30。

### D11 格式標準

CLI 的測試以 dev2 `adr_lint.py` 作 ADR 格式的對照標準，避免另一份解析器與 dev2 格式走樣。

使用者 2026-10-20 回覆「同意」。影響：S11。

### D12 agent 自主範圍

沿用 [ADR 0011](../../adr/0011-fo-decides-for-the-captain-by-a-delegation-ladder.md) 的授權階梯：agent 能自行決定的範圍以專門的授權 ADR 給出；權限、關卡批准、合併、對外動作、不可逆變更與金錢永不授權。不另增欄位或寫法。

使用者 2026-10-20 回覆「同意」。影響：P5、各決策空間。

### D13 定位

kc-decision-log 是一個人指揮多個 AI agent 時的裁示庫：大方向用使用者的原話寫一次、有版本、分空間存放，agents 讀同一份，小決定引用大決定，省掉重複的對話。核心依據是使用者 2026-10-19 的話：「我需要指揮不同 FO，跨產品，跨 LLM，跨工具去達成我的目標」。dot 等沒有終端機的 agent 需待 MCP／connector 才能讀；在此之前「讀同一份」只對可執行 CLI 的 agent 成立。成功指標是每次要使用者決定的題數，以及引用使用者層裁示的 `Precedent:` 行數；兩者目前都沒有基準值。

使用者 2026-10-20 回覆「同意」。

## 驗證層級與待驗收項

| 層級 | 現況 |
| --- | --- |
| design | 2026-10-20 使用者接受重切後七張故事、P1-AC1–AC6 與其修改，以及 D6–D13；兩位陌生讀者的 43 題已逐題答覆或延後。 |
| technical | CLI 尚未實作；Claude 本機以 Git 讀固定 commit 已觀測，Codex 接手重讀與合成 dev2 任務未驗。 |
| admission | 投入四個完整工作日；P1 粗估 16–30 active 工程小時，未校準，上限換算 3.75 天。2026-10-20 使用者回覆「照建議」接受交接，原生 `journey-handoff.mjs` 檢查通過。 |

dev2 基準：0.25.0。原始格式、狀態、配號及審查沿用 dev2。get_effective 與 Decision key 是保守查詢的設計補充，不是 dev2 原生要求。

- [adr-template.md](../../../kc-dev-flow-2/references/adr-template.md)
- [workflow.md](../../../kc-dev-flow-2/references/sd/workflow.md)
- [principles.md](../../../kc-dev-flow-2/skills/implementation/principles.md)
- [adr_lint.py](../../../kc-dev-flow-2/scripts/adr_lint.py)
- [number_guards.py](../../../kc-dev-flow-2/scripts/number_guards.py)
- [pilot.md](../../../kc-dev-flow-2/references/profiles/pilot.md)

30 張故事都標 `status: gap`（2026-10-20，使用者回覆「照建議」），進度之後由 `kc-journey-progress` 依 dev2 任務回填。

## 本批 interrogation 結果

兩native讀者43原題 → 35個story question主題：7 Fact、28 Gap；31主題含技術shaping／適配，無未答的人類value決策。短問答見[故事地圖](story-map.md)及[journey來源](journey.yaml)的questions，全文見[P1契約](p1-technical-contract.md)（為重切前 P1 撰寫），原題對照見[故事問題來源對照](story-map.md#question-origins)；Gap並未實作，三端／隔離／fit仍未驗。沒有新增story、slice或task，也沒有沿舊MCP接受。

原生ADR格式／Status／配號／驗收與feedback沿dev2；原生lint整體check fail不改其他Accepted。已撤回整binding一律unresolved策略，衍生effective只作非權威查詢；見[dev2原生對齊](p1-technical-contract.md#native-dev2-alignment)。
