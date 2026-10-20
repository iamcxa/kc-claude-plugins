# P1 四包技術契約提案

> **2026-10-20 重切：** 本契約為重切前 P1（S01、S02、S04、S10、S11）撰寫。新 P1 見[切片說明](slice-map.md#p1)，只取單一 binding 讀取、原文 digest、原 Status 與保守 effective 相關部分，由 dev2 ideation 依新驗收條件選用；三端、隔離與多來源議題屬 P4a／P4b。

**這是P1工程契約草案，尚未實作、驗證，亦不是已接受API或ready handoff。** 僅收斂既有S01／S02／S04／S10／S11、三端／Pilot／D1–D5，不新增故事、規則或切片。候選介面與常數供書面審閱；原卡片／AC仍以[journey.yaml](journey.yaml)與[切片說明](slice-map.md)為準。工程量見[P1估工](p1-estimate.md)。投入已澄清為三個完整工作日；先前1-3天與3 days上限保留，32–48h／風險40–64h仍為未校準提案，未證fit。

## 共同入口與結果

候選Node24 checkout入口：

```text
node <fixed-code-checkout>/kc-decision-log/cli.mjs <context|list|read|search|effective>
  --config <trusted-binding-json> --binding <id> --commit <full-commit>
  --format <json|human>
```

該檔目前不存在；這是預定交付入口，不是可用命令。使用固定可核對code checkout／source-closure manifest，不要求global install、npm publish或新依賴。`--help`／`--version`不讀source，也不算產品驗收。

每次source命令只載入一個binding、一個full immutable commit。`--commit`必填，依repo object-format接受40／64hex且必須是commit object；拒HEAD、ref、shortsha、tag解參照與省略。tracking_ref僅保留配置及後片freshness用途；配置repo／roots內合法可讀、本地已有的歷史pin可讀，不宣稱仍在現ref或最新，不fetch。

JSON stdout一份結果；失敗也給小型`ok:false/reason` envelope與非零exit，stderr只受控診斷、不輸出原文／credential。人讀模式呈現同一事實，失敗在stderr給相同reason。兩模式都明示ADR是來源資料，`authorization=none`；不執行其文字指令。原文只在memory及本次requested stdout，不dist／cache／原文logs。

## A. 來源、權威與context（9題）

可信JSON binding最少包括`repo_id`、`clone_path`、`tracking_ref`、`level`、`scope`、`adr_roots`、既有authority evidence reference。不自動掃repo／搜尋設定，不接受任意`--repo`／檔外path。配置不新增OS權限或裁決權；實際可讀範圍由已准OS／filesystem／執行context決定。

`repo_id`由可信binding宣告並沿既有來源證據核對，clone位置／URL alias不是全域identity。fork即使相同commit仍不同repo_id。離線只稱configuration-derived身分，不偽裝server attestation、不強制gh在線。Words只作attribution；authority另呈現既有可信人類確認／原流程引用及已知／未知狀態，不新建簽章、帳號或權威系統。

`binding_fingerprint`為正規化`repo_id/tracking_ref/level/scope/adr_roots`之SHA256，排除clone_path／別名／display／runtime。scope與roots以明確字串規則排序，保留大小寫與原義，不用本機locale排序。本提案不以namespace/project_key形成ID；若後續採用，必納入語義fingerprint，只有display label可排除。跨runtime相同語義設定可比；本機clone path可以不同。

canonical reference完整包含`repo_id/level/scope/record_id/path/commit/rawsha256`。本提案`--id`用native四位ADR號NNNN、僅作binding內selector；先前GUIDE#0012只是例示，沒有承諾沿用舊MCP grammar。ID不唯一就回歧義，不find首筆；可用list已顯示的精確`--path`重讀，僅限本view已枚舉、allow-root內的path。

碰撞只在本已准config內，依static repo／roots語義重疊判斷；同repo／commit／path被配置成衝突level／scope時，拒`configuration_ambiguous`，不挑第一個、不升權。不得為尋找衝突去讀其他owner／private config、打開未准binding或原文；未知不升權。單view不混owner後filter；上層引用另pin，沒有跨repo原子snapshot承諾。

context分`observed`、`declared`與`unknown`：實際platform/process與可核對code來源另列；named client的可信發起鏈來自既有tool回執，不由CLI自印label證明。不仿造Sites ID，gh／Git credential／OS context與裁決權分開。

## B. 固定blob、唯讀loader、native parser（8題）

loader取代舊build的code/data-root綁定、UTF8字串先解碼與寫dist流程；core保持純查詢，不接Git、transport auth或任意owner自報。

1. 只用已准trusted repo／gitdir／common-dir；正常worktree可用已核對common-dir，不接受外來object store／alternates重導或任意repo。
2. Git用固定可信executable與`execFile` argv，不拼shell。清除GIT_*注入／trace／object重導，global/system config指向OS null device；固定no-lazy-fetch／no-replace-objects／no-optional-locks／no-pager／literal-pathspecs，關fsmonitor與hooks。
3. 不改safe.directory、不增例外；不做status／worktree掃描、不執行filter／textconv／follow-symlinks／batch-all-objects。以固定OID驗type，按configured roots枚舉tree、讀blob size後才讀raw內容；核對實收size。
4. `rawsha256`先算raw Buffer，再嚴格UTF8 decode。回覆原text保留CRLF／BOM，與UTF8重編碼的bytes相符；parser只用暫存分析副本，不改原文或NFC正規化。
5. regular mode100644／100755可讀；120000／160000不follow，invalidUTF8／不支援mode／超limit明示fatal exit5，原Git blob留原處。不新增base64／二進位產品。

原path由binding adr_roots與固定Git tree取得，不為SOURCE_PATH搬檔，無DOT必要條件。raw Buffer／digest／BOM／CRLF保留與adapter分析副本、原生lint結果是不同事實；保留bytes不能當成native lint已通過。

<a id="native-dev2-alignment"></a>

### 對齊dev2 0.25.0原生ADR機制

**撤回前稿把整個binding所有ADR一律effective unresolved作為既定規則。** 舊core的全snapshot issues拒絕、Decision key、同key多Accepted與effective演算法是額外服務策略，均不是dev2原生機制。原生ADR格式／Status、FO配號、原驗收及feedback路線不變；不新增全庫生效gate、lint分支或per-record恢復引擎。

| 層次 | 沿用與輸出邊界 |
| --- | --- |
| 原生格式檢查 | [adr_lint.py](../../../kc-dev-flow-2/scripts/adr_lint.py)只檢查單次傳入adr_dir直層*.md集合的NNNN檔名／重號、first-nonblank title的整數號、Date字串regex、四章與順序、第一非空Status行、Words／Options標記存在與明示取代target存在；不額外要求title補零、Date真日曆、structured Words或Status整section完全匹配。 |
| Recommended／Legacy | Recommended只針對`--require`或`--since`判定新增／變更的非Legacy檔；一般歷史缺漏不作格式錯。Legacy依前30行`Status: Legacy`辨識；explicit require Legacy沿原拒絕規則，不能寫新裁決進舊Legacy。 |
| 整體結果與逐檔診斷 | 原生any errors為exit1；`--since`配置／Git diff錯誤為exit2，沿原feedback／FO回報。重號／target存在性限該adr_dir集合，不是跨repo／roots權威；整體check fail不改任何ADR Status，不能推成其他Accepted已失效。未實跑原工具及正確`--since <base>`／`--require <numbers>`、candidate／base commit證據，reader不能報`native_validation_passed`。 |
| read／list | 安全可讀原文、raw Status／path／digest與逐檔診斷可回；reader診斷不是原生lint pass證明。以合成0001 valid＋0007 bad為例，整體lint fail但0001原Accepted仍保留，0007診斷不會改寫0001。 |
| 非權威衍生effective | dev2沒有Decision key／effective／resolved／unresolved，也不檢查循環或按key多Accepted。資料不足／鏈疑義只表示查詢未知；不把自訂key、循環或同key衝突列native格式錯或新裁決。需要完整合法view的操作可明示`validation_failed`／能力不足或非零error；這是查詢結果／能力狀態，不散發每筆ADR已失效或改Status。 |

沿[ADR模板](../../../kc-dev-flow-2/references/adr-template.md)、[implementation ADR責任](../../../kc-dev-flow-2/skills/implementation/principles.md)、[validation](../../../kc-dev-flow-2/skills/validation/principles.md)及[workflow Decision records／Number guards](../../../kc-dev-flow-2/references/sd/workflow.md)。adapter不能把舊core較嚴的Date／Words／Recommended／Status／fenced-section解析偷渡成native規範；本設計不改原工具或替FO配號。CLI同binding多roots遇同NNNN可拒絕selector歧義，但應稱查詢歧義，不能冒稱native有跨roots全域重號規則。D4實質新ADR／小修原檔是使用者已確認的產品政策；原生lint不判斷意思、裁決是否Accepted或替代人類確認。

有限合成觀測已核對：valid缺Decision key=exit0；0001 valid＋0007壞格式及dangling target=exit1；循環與同optional key兩Accepted=exit0；歷史Recommended缺漏一般讀取exit0、required時exit1；explicit required Legacy=exit1。另unpadded heading、Status附註、非structured Words與僅符合Date regex也沿原工具接受。這些只是原工具的實際行為，不是新的產品測試或新增norm；`--since`路徑本輪未probe，正式驗收仍須原正確base／candidate／required證據。

已在公開模板上完成固定env的rev-parse／ls-tree／cat-file-size／raw-blob四步exit0，708bytes及raw SHA與snapshot相符。**stderr並非乾淨**：各步有DARWIN_USER_TEMP_DIR confstr code5／tmp fallback，首步另有Apple xcodebuild FSEvents／cache-dir warning。minimal env／Apple launcher需保留必要可信runtime環境並後驗；不可宣稱零bootstrap副作用、完整無寫或完整無網路。這只是公開模板的機制觀測，沒有讀取私人ADR。

官方依據（已核對官方文件）：[Git 2.50](https://git-scm.com/docs/git/2.50.0)說明禁止lazy-fetch／replacement／optional-lock及config／object環境變數；[cat-file 2.50](https://git-scm.com/docs/git-cat-file/2.50.0)可取raw blob，filter／textconv會轉換；[safe.directory](https://git-scm.com/docs/git-config)不應以萬用例外繞過不同owner保護。旗標解析與公開blob成功不代替partial／network／外owner／alternates的負向驗證。

## C. CLI／輸出／資源與交付（12題）

| 命令 | 結果／語義 |
| --- | --- |
| context | 顯示已合法載入source的binding／commit／版本／觀測限制，不列他人的binding |
| list | 固定view的metadata與record diagnostics，path/rawsha/原status可追；合法空集合為0、items=[] |
| read --id／--path | 回單份原文與完整canonical reference；duplicate ID不任選，精確path僅從已枚舉集合選 |
| search --query | 只在合法單view做literal case-sensitive match，不lowercase／NFC，避免舊offset錯位 |
| effective --id | 明示resolved／unresolved／chain，保留原status；不自創跨域替代，unknown_id明示record_present=false |

list/search每頁預設50、最多100。輸出`complete/has_more/next`；complete只表此查詢結果頁覆蓋完，不能當format clean。view枚舉完成與integrity diagnostics另外標。cursor綁fingerprint／domain／fullcommit／contract／operation／query／offset／limit並驗bounds；不是credential，跨view或壞cursor拒2。不給無限`--all`。

search snippet保留原文Unicode scalar offset，最多240 scalars並標`excerpt=true`，不冒稱完整原文。人讀保留合法LF作排版（可保留TAB），CR／ESC與其餘C0／C1明示escape；JSON依法escape。包含BOM／CRLF的bytes round-trip須驗，不能默丟BOM。digest始終算未轉義blob，不把顯示sanitize當原bytes。

| exit | 本提案意義 |
| --- | --- |
| 0 | 完成；包含合法query unresolved、合法空集合 |
| 2 | 輸入／selector／cursor拒絕；已合法完整view的unknown_record或ambiguous_id |
| 3 | source_unavailable統一permission／未知未准binding／missing repo/commit/object，不探無權存在 |
| 5 | 無可信可查view、不支援text/mode、資源上限／deadline |
| 1 | 非預期內部失敗 |

source_unavailable的envelope明確`source=null, record=null, loaded_view=null`；不echo未准binding的實際path／remote／存在性或原生Git stderr。只有已合法載入view的missing-record才可附該view metadata。Git stderr先受控處理，不把raw內容當公開錯誤或原文log。

取消前版候選exit4；舊文件僅為候選，不是既有API。合法view read缺ID為2；effective unknown_id仍0且record_present=false，不能混同現有Accepted但效力未知。合法空集合定義：full commit存在，configured ADR root在該Git tree確為directory，可只含README.md／index.md／template.md／.gitkeep等明示skip檔而無ADR candidate，才回0 empty。Git不保存純空directory；root不存在／型別錯不能假空，repo無commit也是source_unavailable。來源失敗不能回假empty，致命讀取不能回假complete或silent truncate。

候選pilot資源值如下，**未benchmark、非SLA，需boundary案例驗證**：

| 項目 | 候選上限 |
| --- | --- |
| config | 64KiB |
| 單ADR blob | 1MiB |
| 每view raw blobs | 16MiB／2000 records |
| stdout | 8MiB；超過改小型resource_limit error，不截原文／半份JSON |
| query／cursor | 256 Unicode scalars／4096 bytes |
| Git單命令／整體query | 10秒／30秒；deadline後終止同一子程序樹，不能仍回成功 |

這些是保守工程建議，不是人類接受、平台保證或量測速度。超限回5／resource_limit；若必要有效資料超過，呈現具體差異再調整，不以無限輸出補救。

code與data provenance分開。P1驗收使用固定code checkout／manifest，核對共用entry/core/loader source closure fingerprint；只印HEAD不證明實際執行同code。closure與參考不符／code dirty／無法證明loaded來源時，comparable=false／unknown，仍可回原文但不能宣稱三端core語義一致。這不需要Git status掃描所有worktree；可核對固定已宣告closure bytes／manifest。ADR data checkout即使dirty，固定Git D0仍可合法讀，不能混同code變動。

view／record摘要按UTF8 path byte順序與固定canonical序列化取hash，排indexed_at／PID／local clonepath等可異欄位；不同runtime比較相同fingerprint／data commit／contract／rawsha／原status／effective。remote／gh未觀測就是unknown，不稱最新。

## D. oracle、named-client回執與OS隔離（2題）

oracle獨立由committed合成Git blobs取得fullcommit／path／rawsha，加原dev2規範與人工明示status／鏈expected；不能呼叫被測parser/service生成expected。三端結果相同必要但不充分。fixtures包括不同repo同號、原native／Legacy／缺key／歷史Recommended、壞鏈／duplicate、D0在ref前進D1後仍可讀及上列error/limits界線；這是待建CLI驗收拓樸；本輪僅執行有限原生lint合成probe，未建CLI tests或執行產品。

每named client沿既有可核對事件鏈留：initiation→本端executor/cwd→命令/exit→code closure／source binding/fullcommit→result。dot可用已准delegated local task路徑，不要求前端直接shell、不推cloud繼承本機gh；不能同一端跑三次貼名。回執沿既有tool/task記錄，不造中央任務／帳號系統。

Claude normal-session唯讀命令回執仍pending-not denied。最小後續是在**正常既有Claude Code工作階段、非OutsideVoice reviewer**，取得公開code checkout的安全rev-parse命令原tool_use/result/exit/cwd/runtime及commit；協調端host同命令成功不能頂替Claude發起。本輪只描述、不新起Claude/Bash、不新增權限；若既有工具拒絕或需新權限就停。

OS合成negative harness提案：A/B各在真OS受限context執行**整個query及Git/helpers子程序**，含code/runtime/own repo/准許gitdir-common-dir，foreign repo metadata／objects／aliases亦受保護。不得先在未受限process載入foreign原文／cache後再filter，也不得留下未受限helper／替代objectstore旁路。驗index/read/search/context/error metadata及raw logs皆不洩漏。實際權限邊界只聲稱該受限process subtree，不能宣稱保護任意同OS unrestricted agent。

現有macOS兩已知檔4次read-deny probe只證機制可用，不是這個完整harness、跨平台依賴或AC1通過。後續須在既有允許機制內收斂profile/runtime需求並驗整個repo/objectstore/alias／子程序；必要新安裝／身份／權限／host改動不藏在工程常數內，自動停返具體scope。

## 31技術主題與35題全文

以下保留35題的完整規劃提問／答覆；其中31技術主題仍分四包9／8／12／2，其餘4題為Fact核對，不新增story或slice。原題對照的唯一編輯來源為[故事問題來源對照](story-map.md#question-origins)；native questions僅放短ask／answer／doc，不使用保留的source。

以上是工程提案與待驗假設，不等於新增的人類產品接受。P1／Pilot／appetite／D1-D5的既有明確接受在scope／premises仍相符時沿用；真正value／scope／acceptance改變才需新決定。正式estimate／fit及歷史guard分開保存；本草案沒有產生accepted digest或新的handoff結果。

### cli-p1-u01

**所屬故事：S11**

原題：C01, C23, X03；契約包：固定Git原文、唯讀loader與native parser。

提案：read/list回安全可讀原文、raw Status與逐檔診斷；native整體lint fail不改其他Accepted。撤回舊整binding一律unresolved策略；需要完整合法view的衍生操作可報validation_failed／能力不足或非零error，不能改寫或散發每筆ADR失效。

待驗：原生整體check與逐檔診斷、raw Status／bytes保持；衍生查詢能力錯誤與ADR狀態嚴格分開，不新建per-record恢復引擎。

**完整規劃提問：** 同一合法binding內壞檔的故障範圍、可讀原文／partial結果與exit語義如何處理？

**完整規劃答覆：** Gap：原生adr_lint對單次傳入adr_dir中*.md集合的檔名／重號／格式與明示target等診斷有錯時整體exit1，不改任何ADR Status；舊source.effective因snapshot.issues令全部source_validation_failed是額外服務策略，撤回作為新CLI既定規則。read/list可回安全可讀原文、raw Status與逐檔診斷。需要完整合法view的衍生查詢可操作級validation_failed／能力不足或非零error，不散發每筆ADR已失效；不新造per-record恢復或全庫生效gate。Gap／實作驗證仍在，未接受API。

### cli-p1-u03

**所屬故事：S01**

原題：C03, C07；契約包：固定Git原文、唯讀loader與native parser。

提案：每binding配置adr_roots；唯讀枚舉固定commit各root直接子檔，沿native NNNN-short-title.md規則；移除SOURCE_PATH projects限定與硬DOT依賴，不搬檔。

待驗：native docs/adr與舊projects根各保持Git原path，DOT非必要。

**完整規劃提問：** native path與不依賴DOT namespace的loader適配如何處理？

**完整規劃答覆：** Gap：技術草案已提出：每binding配置adr_roots；唯讀枚舉固定commit各root直接子檔，沿native NNNN-short-title.md規則；移除SOURCE_PATH projects限定與硬DOT依賴，不搬檔。 後續須驗：native docs/adr與舊projects根各保持Git原path，DOT非必要。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u04

**所屬故事：S04**

原題：C04；契約包：來源、權威與context契約。

提案：canonical reference固定repo_id/level/scope/record_id/path/commit/rawsha256；--id提案用原生四位ADR號NNNN、只在binding內解析；舊GUIDE#0012是先前例示，不承諾新CLI沿用MCP grammar。

待驗：同號跨repo可分；ID重複須歧義，--path只從該view已枚舉集合精確選。

**完整規劃提問：** binding內selector與完整canonical引用的對應如何處理？

**完整規劃答覆：** Gap：技術草案已提出：canonical reference固定repo_id/level/scope/record_id/path/commit/rawsha256；--id提案用原生四位ADR號NNNN、只在binding內解析；舊GUIDE#0012是先前例示，不承諾新CLI沿用MCP grammar。 後續須驗：同號跨repo可分；ID重複須歧義，--path只從該view已枚舉集合精確選。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u05

**所屬故事：S04**

原題：C05, C18；契約包：來源、權威與context契約。

提案：一次命令只建一個已准binding/fullcommit view；先在實際權限context分隔來源，無跨repo原子view承諾。上層引用保留另一repo的精確pin，不自動載入。

待驗：foreign source錯誤不影響本binding；不同repo各有revision。

**完整規劃提問：** 每binding／owner view與各repo commit邊界，不能混owner後filter或承諾跨repo原子snapshot如何處理？

**完整規劃答覆：** Gap：技術草案已提出：一次命令只建一個已准binding/fullcommit view；先在實際權限context分隔來源，無跨repo原子view承諾。上層引用保留另一repo的精確pin，不自動載入。 後續須驗：foreign source錯誤不影響本binding；不同repo各有revision。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u06

**所屬故事：S10**

原題：C06；契約包：CLI輸出、資源界線與可重現交付。

提案：統一exit3/source_unavailable處理未知／未准binding、permission、missing repo/commit/object；不探無權存在性或回外來path。合法完整view內unknown record另可exit2；effective有效unknown_id為0。 此錯誤source/record/loaded_view=null，不echo未准path/remote/存在性或native Git stderr；只有合法view missing-record可附該view metadata。

待驗：未准/不存在/不可讀source同形；合法view unknown_record不混Accepted效力未知。

**完整規劃提問：** 跨權限錯誤不得形成存在性oracle，合法可揭露context的錯誤mapping如何處理？

**完整規劃答覆：** Gap：技術草案已提出：統一exit3/source_unavailable處理未知／未准binding、permission、missing repo/commit/object；不探無權存在性或回外來path。合法完整view內unknown record另可exit2；effective有效unknown_id為0。 此錯誤source/record/loaded_view=null，不echo未准path/remote/存在性或native Git stderr；只有合法view missing-record可附該view metadata。 後續須驗：未准/不存在/不可讀source同形；合法view unknown_record不混Accepted效力未知。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u07

**所屬故事：S02**

原題：C08；契約包：固定Git原文、唯讀loader與native parser。

提案：僅trusted repo/gitdir/common-dir；固定Git executable＋execFile argv，清GIT_*注入/trace，指定global/system config=/dev/null及no-lazy-fetch/no-replace/no-optional-locks/no-pager/literal-pathspecs、關fsmonitor/hooks；拒外來alternates/objectstore重導，不改safe.directory。

待驗：現有raw object四步成功但Apple bootstrap警告保留；後續測env/runtime整理、外owner/config/alternates/partial/network與子程序邊界。

觀測限制：現toolchain minimal env之警告／bootstrap副作用尚未完成驗證，不是新授權要求。

**完整規劃提問：** 本機Git object讀取的config／ownership／hooks／限制安全策略如何處理？

**完整規劃答覆：** Gap：技術草案已提出：僅trusted repo/gitdir/common-dir；固定Git executable＋execFile argv，清GIT_*注入/trace，指定global/system config=/dev/null及no-lazy-fetch/no-replace/no-optional-locks/no-pager/literal-pathspecs、關fsmonitor/hooks；拒外來alternates/objectstore重導，不改safe.directory。 後續須驗：現有raw object四步成功但Apple bootstrap警告保留；後續測env/runtime整理、外owner/config/alternates/partial/network與子程序邊界。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u08

**所屬故事：S01**

原題：C09；契約包：固定Git原文、唯讀loader與native parser。

提案：必填符合repo object-format的40/64hex完整commit，type必須commit且解析結果與輸入一致；禁止ref/shortsha/HEAD與隱式fetch。缺object統一exit3；不以promisor下載補齊。

待驗：missing-object/partial-clone/networktrap需後續合成驗證，旗標解析成功不等於全無網路。

**完整規劃提問：** immutable commit解析、shallow／partial缺object與禁止隱式fetch如何處理？

**完整規劃答覆：** Fact：合法固定pin與不隱式fetch／login的邊界保留。Gap：技術草案已提出：必填符合repo object-format的40/64hex完整commit，type必須commit且解析結果與輸入一致；禁止ref/shortsha/HEAD與隱式fetch。缺object統一exit3；不以promisor下載補齊。 後續須驗：missing-object/partial-clone/networktrap需後續合成驗證，旗標解析成功不等於全無網路。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u09

**所屬故事：S10**

原題：C10, X14；契約包：固定Git原文、唯讀loader與native parser。

提案：先以raw Buffer算SHA256，再嚴格UTF8 decode並保留原換行/BOM bytes可往返；invalid UTF8、超limit、120000 symlink/160000 submodule明示exit5，不follow、不替換、不加base64二進位產品。100644/100755 regular blob可讀。

待驗：CRLF/BOM／控制碼／invalidUTF8／mode邊界案例；原Git blob不改。

**完整規劃提問：** 原blob bytes digest／非UTF8與symlink或submodule的明示處理如何處理？

**完整規劃答覆：** Gap：技術草案已提出：先以raw Buffer算SHA256，再嚴格UTF8 decode並保留原換行/BOM bytes可往返；invalid UTF8、超limit、120000 symlink/160000 submodule明示exit5，不follow、不替換、不加base64二進位產品。100644/100755 regular blob可讀。 後續須驗：CRLF/BOM／控制碼／invalidUTF8／mode邊界案例；原Git blob不改。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u10

**所屬故事：S01**

原題：C11；契約包：來源、權威與context契約。

提案：顯式--config選既有可信JSON binding配置，無自動搜尋/掃repo；binding_fingerprint對正規化repo_id/tracking_ref/level/scope/adr_roots做SHA256，排除clonepath/別名/display/runtime。

待驗：不同clone同語義fingerprint相同；改scope/roots不同；config不授權OS存取。

**完整規劃提問：** controlled binding設定位置／編輯者與可比較config身分如何處理？

**完整規劃答覆：** Gap：技術草案已提出：顯式--config選既有可信JSON binding配置，無自動搜尋/掃repo；binding_fingerprint對正規化repo_id/tracking_ref/level/scope/adr_roots做SHA256，排除clonepath/別名/display/runtime。 後續須驗：不同clone同語義fingerprint相同；改scope/roots不同；config不授權OS存取。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u11

**所屬故事：S02**

原題：C12；契約包：來源、權威與context契約。

提案：context分observed(實際平台/process/程式來源)、declared(既有named-client回執引用)、unknown；不自造Sites ID或attestation，不把CLI --client字串當真發起者。

待驗：不能觀測的gh/remote/權威不驗證；metadata留來源與時間。

**完整規劃提問：** context欄位可觀測與自報的來源，不偽造attestation如何處理？

**完整規劃答覆：** Gap：技術草案已提出：context分observed(實際平台/process/程式來源)、declared(既有named-client回執引用)、unknown；不自造Sites ID或attestation，不把CLI --client字串當真發起者。 後續須驗：不能觀測的gh/remote/權威不驗證；metadata留來源與時間。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u12

**所屬故事：S10**

原題：C13；契約包：來源、權威與context契約。

提案：所有JSON/人讀回應明示source_content_is_data與authorization=none；ADR文字不形成外部動作/任務/裁決權。只memory與本次requested stdout，無dist/cache/raw logs。

待驗：包含惡意指令的合成ADR仍作字串回覆，不觸發tool。

**完整規劃提問：** ADR原文作來源資料與不授權外部動作的既有邊界保留如何處理？

**完整規劃答覆：** Gap：技術草案已提出：所有JSON/人讀回應明示source_content_is_data與authorization=none；ADR文字不形成外部動作/任務/裁決權。只memory與本次requested stdout，無dist/cache/raw logs。 後續須驗：包含惡意指令的合成ADR仍作字串回覆，不觸發tool。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u13

**所屬故事：S04**

原題：C14；契約包：CLI輸出、資源界線與可重現交付。

提案：只搜尋已准單view；採literal case-sensitive字串匹配，不做lowercase/NFC轉換；snippet以原文Unicode scalar offset定位、至多240 scalars且標excerpt=true，不冒稱完整原文。

待驗：大小寫差異、CJK/Unicode與轉義控制碼對照原文位置。

**完整規劃提問：** 合法domain前置隔離搜尋與Unicode excerpt精確性如何處理？

**完整規劃答覆：** Gap：技術草案已提出：只搜尋已准單view；採literal case-sensitive字串匹配，不做lowercase/NFC轉換；snippet以原文Unicode scalar offset定位、至多240 scalars且標excerpt=true，不冒稱完整原文。 後續須驗：大小寫差異、CJK/Unicode與轉義控制碼對照原文位置。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u14

**所屬故事：S11**

原題：C15；契約包：固定Git原文、唯讀loader與native parser。

提案：native無key／Legacy沿原格式與Status；effective只作非權威同域明示鏈查詢。資料不足／鏈疑義則未知／能力不足；循環、同key多Accepted與key mismatch不列native格式錯，不改Accepted或建立全庫生效gate。

待驗：原生lint實際結果與額外查詢未知分列；循環／同key兩Accepted不冒稱原生會拒，原Accepted不改。

**完整規劃提問：** 壞替代鏈／多Accepted／缺key的保守effective與native適配如何處理？

**完整規劃答覆：** Fact：舊source.effective的missing key／same-key多Accepted／全snapshot issues規則是服務自訂，不是dev2原生機制。Gap：native格式／Status／target存在性以adr_lint為準；原生不定義Decision key、effective或循環／同key多Accepted拒絕。衍生查詢只沿同域明示鏈，資料不足／鏈疑義明示未知或能力不足，不改Accepted、不把自訂key／循環／同key衝突列native格式錯，也不一律令整庫ADR失效；實作驗證仍在。

### cli-p1-u16

**所屬故事：S11**

原題：C17；契約包：固定Git原文、唯讀loader與native parser。

提案：以[原生對齊表](#native-dev2-alignment)的檔名／first-nonblank整數號title／Date regex／四章／first Status／Words與Options presence／required-only Recommended／Legacy為準。舊core更嚴的條件不偷渡；raw bytes保留與原生lint通過分開，adapter分析副本沿原生文字行行為。

待驗：用原模板及正確since／require／commit證據跑原工具；reader不代稱native_validation_passed，不改原文／Status。

**完整規劃提問：** Legacy／歷史Recommended寬容與native四章parser差異如何處理？

**完整規劃答覆：** Gap：adapter依dev2 0.25.0原生檔名／重號、first-nonblank整數號title、Date regex、四章、first-nonblank Status及Words／Options presence；Recommended僅required或since changed要求，Legacy沿前30行與原require規則。舊core的真日曆Date／整section Status／structured Words／全部Recommended等較嚴規則不能偷渡成native拒絕。raw bytes保留與native lint通過分開；只有實跑原工具及正確since／require／commit證據才能報native_validation_passed，Gap／實作驗證仍在。

### cli-p1-u17

**所屬故事：S10**

原題：C19, X08, X11；契約包：CLI輸出、資源界線與可重現交付。

提案：list/search預設50、max100，每頁明示complete/has_more/next；cursor綁fingerprint/domain/fullcommit/contract/op/query/offset/limit且驗bounds，跨view拒exit2；不提供無限--all。

待驗：page交集/缺漏、改query/commit/domain/limit、偽造offset與cursor size都測；cursor非授權。

**完整規劃提問：** 一次CLI查詢是否paging、完整性標示與保留cursor時的binding/domain/fullcommit/query綁定如何處理？

**完整規劃答覆：** Gap：技術草案已提出：list/search預設50、max100，每頁明示complete/has_more/next；cursor綁fingerprint/domain/fullcommit/contract/op/query/offset/limit且驗bounds，跨view拒exit2；不提供無限--all。 後續須驗：page交集/缺漏、改query/commit/domain/limit、偽造offset與cursor size都測；cursor非授權。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u18

**所屬故事：S10**

原題：C20；契約包：CLI輸出、資源界線與可重現交付。

提案：分dev2 read-basis、package/core/contract與可證code checkout/source-closure fingerprint；code HEAD不是loaded code證明。closure mismatch/dirty或來源不明=>comparable=false/unknown仍可回原文。

待驗：data dirty不阻固定Git D0；view digest排時間/PID/localpath並採UTF8 byte順序非locale。

**完整規劃提問：** dev2基準、程式package與core/contract/build provenance分離如何處理？

**完整規劃答覆：** Gap：技術草案已提出：分dev2 read-basis、package/core/contract與可證code checkout/source-closure fingerprint；code HEAD不是loaded code證明。closure mismatch/dirty或來源不明=>comparable=false/unknown仍可回原文。 後續須驗：data dirty不阻固定Git D0；view digest排時間/PID/localpath並採UTF8 byte順序非locale。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u19

**所屬故事：S02**

原題：C21, X12；契約包：CLI輸出、資源界線與可重現交付。

提案：候選入口node <code-checkout>/kc-decision-log/cli.mjs，Node24、固定可核對code/manifest與共用core，不需globalinstall/npm publish/new deps；metadata --help/version不算查詢驗收。

待驗：三端相同入口/closure/contract，正常CLI從checkout執行；目前只是提案沒有檔案/API已存在。

**完整規劃提問：** 三端交付／Node與CLI封裝，Pilot是否需脫離source checkout的安裝證據如何處理？

**完整規劃答覆：** Gap：技術草案已提出：候選入口node <code-checkout>/kc-decision-log/cli.mjs，Node24、固定可核對code/manifest與共用core，不需globalinstall/npm publish/new deps；metadata --help/version不算查詢驗收。 後續須驗：三端相同入口/closure/contract，正常CLI從checkout執行；目前只是提案沒有檔案/API已存在。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u22

**所屬故事：S10**

原題：C25；契約包：CLI輸出、資源界線與可重現交付。

提案：穩定view摘要含fingerprint/contract/fullcommit與按path byte排序的mode/blob OID/rawsha；排indexed_at/PID/localclonepath/context。observed_at僅標觀測時間，remote/gh未查=>unknown，非latest。

待驗：不同runtime可比stable subset，時間/路徑差異不得誤報原文不一致。

**完整規劃提問：** 比較穩定欄位、observed_at／offline與可異時間context標記如何處理？

**完整規劃答覆：** Gap：技術草案已提出：穩定view摘要含fingerprint/contract/fullcommit與按path byte排序的mode/blob OID/rawsha；排indexed_at/PID/localclonepath/context。observed_at僅標觀測時間，remote/gh未查=>unknown，非latest。 後續須驗：不同runtime可比stable subset，時間/路徑差異不得誤報原文不一致。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u23

**所屬故事：S04**

原題：X01；契約包：來源、權威與context契約。

提案：authority只回既有可信人類確認/原流程引用之declared evidence與核對狀態，Words為attribution；config/gh不製造decider、不新增簽章PKI。

待驗：錯層/未知確認如實標，無適用權威不說已批准外部動作。

**完整規劃提問：** binding裁決者的可信確認來源，不以ADR author歸屬代替如何處理？

**完整規劃答覆：** Gap：技術草案已提出：authority只回既有可信人類確認/原流程引用之declared evidence與核對狀態，Words為attribution；config/gh不製造decider、不新增簽章PKI。 後續須驗：錯層/未知確認如實標，無適用權威不說已批准外部動作。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u24

**所屬故事：S01**

原題：X02；契約包：來源、權威與context契約。

提案：tracking_ref只是配置／後片freshness；P1可讀該配置repo/roots中本地既存、合法可讀完整歷史pin，即使不在目前ref，也只稱該commit。無新增全history掃描/遠端取object或額外ancestry限制。

待驗：D0在ref前進D1後仍可重現；未宣稱D0最新/仍為現ref。

**完整規劃提問：** 配置追蹤分支歷史以外但本機存在的commit能否合法被讀取如何處理？

**完整規劃答覆：** Gap：技術草案已提出：tracking_ref只是配置／後片freshness；P1可讀該配置repo/roots中本地既存、合法可讀完整歷史pin，即使不在目前ref，也只稱該commit。無新增全history掃描/遠端取object或額外ancestry限制。 後續須驗：D0在ref前進D1後仍可重現；未宣稱D0最新/仍為現ref。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u25

**所屬故事：S04**

原題：X04；契約包：來源、權威與context契約。

提案：只在本已准config依static repo/roots語義重疊判斷level/scope衝突，拒configuration_ambiguous/exit2，不任選/升權。不為找衝突讀其他owner/private config或打開未准binding；未知不升權。

待驗：衝突配置在query前被拒，不改原文/人類權威。

**完整規劃提問：** 同repo/commit/path被不同binding指派衝突層級或scope如何處理？

**完整規劃答覆：** Gap：技術草案已提出：只在本已准config依static repo/roots語義重疊判斷level/scope衝突，拒configuration_ambiguous/exit2，不任選/升權。不為找衝突讀其他owner/private config或打開未准binding；未知不升權。 後續須驗：衝突配置在query前被拒，不改原文/人類權威。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u26

**所屬故事：S01**

原題：X05；契約包：來源、權威與context契約。

提案：repo_id由可信binding宣告並沿既有repo證據核對；clonepath/URL aliases非全域identity，fork相同commit仍不同configured repo_id；offline標configuration-derived，不假server attestation。

待驗：同repo兩clone可比，不同repo_id不合併，無強制gh在線。

**完整規劃提問：** 不同clone URL／本機路徑的repo identity與同commit fork區分如何處理？

**完整規劃答覆：** Gap：技術草案已提出：repo_id由可信binding宣告並沿既有repo證據核對；clonepath/URL aliases非全域identity，fork相同commit仍不同configured repo_id；offline標configuration-derived，不假server attestation。 後續須驗：同repo兩clone可比，不同repo_id不合併，無強制gh在線。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u27

**所屬故事：S01**

原題：X06；契約包：CLI輸出、資源界線與可重現交付。

提案：所有source命令必填--commit完整OID，省略exit2/missing_commit；不默HEAD，也不在查詢內解析會移動ref。若操作者要pin ref由既有Git工具先解析再明示傳入。

待驗：HEAD/branch/shortsha/tagOID/缺參數都不當可接受commit。

**完整規劃提問：** 省略commit時拒絕或一次解析ref後pin如何處理？

**完整規劃答覆：** Gap：技術草案已提出：所有source命令必填--commit完整OID，省略exit2/missing_commit；不默HEAD，也不在查詢內解析會移動ref。若操作者要pin ref由既有Git工具先解析再明示傳入。 後續須驗：HEAD/branch/shortsha/tagOID/缺參數都不當可接受commit。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u28

**所屬故事：S10**

原題：X07；契約包：固定Git原文、唯讀loader與native parser。

提案：同ID多path=>read --id exit2/ambiguous_id並只列合法view matches；可read --path精確已枚舉path取得各自原文，不能任意path；effective對重複ID保守unresolved。

待驗：不find首筆，不改資料以抹掉duplicate。

**完整規劃提問：** 同ADR ID重複檔案的read歧義處理如何處理？

**完整規劃答覆：** Gap：技術草案已提出：同ID多path=>read --id exit2/ambiguous_id並只列合法view matches；可read --path精確已枚舉path取得各自原文，不能任意path；effective對重複ID保守unresolved。 後續須驗：不find首筆，不改資料以抹掉duplicate。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u29

**所屬故事：S11**

原題：X09；契約包：CLI輸出、資源界線與可重現交付。

提案：合法完整view內read unknown_record=>exit2；effective unknown_id=>exit0、record_present=false與明示reason，與現有Accepted但缺key不同；source不可讀統一exit3。

待驗：JSON與人讀同一reason；未知source不洩漏ID存在性。

**完整規劃提問：** 不存在ADR的read失敗與effective unresolved之區分如何處理？

**完整規劃答覆：** Fact：service.read找不到ID會拒絕；source.effective unknown_id為有效unresolved。Gap：技術草案已提出：合法完整view內read unknown_record=>exit2；effective unknown_id=>exit0、record_present=false與明示reason，與現有Accepted但缺key不同；source不可讀統一exit3。 後續須驗：JSON與人讀同一reason；未知source不洩漏ID存在性。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u30

**所屬故事：S01**

原題：X10；契約包：CLI輸出、資源界線與可重現交付。

提案：P1只memory及本次requestedstdout，不dist/raw/index cache或原文logs；診斷僅受控reason/counters，原文不進stderr。後續持久化跨保護邊界需另scope。

待驗：檔案寫入觀察與OS限制後驗；Apple Git bootstrap warnings不等於已證零副作用。

**完整規劃提問：** 唯讀CLI是否持久化原文／索引與保護來源外衍生資料如何處理？

**完整規劃答覆：** Gap：技術草案已提出：P1只memory及本次requestedstdout，不dist/raw/index cache或原文logs；診斷僅受控reason/counters，原文不進stderr。後續持久化跨保護邊界需另scope。 後續須驗：檔案寫入觀察與OS限制後驗；Apple Git bootstrap warnings不等於已證零副作用。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u31

**所屬故事：S01**

原題：X13；契約包：CLI輸出、資源界線與可重現交付。

提案：full commit存在且configured ADR root在Git tree確為directory（可只含README.md/index.md/template.md/.gitkeep明示skip檔）而無ADR candidate，才exit0 items=[]/complete=true。root不存在/型別錯、repo無commit或missing object均source_unavailable/exit3，不能假空；Git不保存純空dir。

待驗：合法含skip檔空root、缺root、root為blob、無commit、missing object與denied source分別驗；無錯誤偽裝empty。

**完整規劃提問：** 合法空ADR repo回空list或source error如何處理？

**完整規劃答覆：** Gap：技術草案已提出：full commit存在且configured ADR root在Git tree確為directory（可只含README.md/index.md/template.md/.gitkeep明示skip檔）而無ADR candidate，才exit0 items=[]/complete=true。root不存在/型別錯、repo無commit或missing object均source_unavailable/exit3，不能假空；Git不保存純空dir。 後續須驗：合法含skip檔空root、缺root、root為blob、無commit、missing object與denied source分別驗；無錯誤偽裝empty。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u32

**所屬故事：S10**

原題：X15；契約包：CLI輸出、資源界線與可重現交付。

提案：人讀保留合法LF（可留TAB）排版，CR/ESC/其餘C0+C1明示escape；JSON依法escape。rawsha取原blob，BOM/CRLF bytes round-trip須驗，不默丟BOM，不以sanitize結果冒稱原文。

待驗：terminal escape、換行/CR/tab及Unicode offset驗證，不改原文。

**完整規劃提問：** 人讀stdout如何安全呈現terminal control characters如何處理？

**完整規劃答覆：** Gap：技術草案已提出：人讀保留合法LF（可留TAB）排版，CR/ESC/其餘C0+C1明示escape；JSON依法escape。rawsha取原blob，BOM/CRLF bytes round-trip須驗，不默丟BOM，不以sanitize結果冒稱原文。 後續須驗：terminal escape、換行/CR/tab及Unicode offset驗證，不改原文。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u33

**所屬故事：S10**

原題：X16；契約包：CLI輸出、資源界線與可重現交付。

提案：候選pilot limits明列blob1MiB/view16MiB/2000records/stdout8MiB/config64KiB/query256scalars/cursor4096bytes/Git10s/query30s；超過exit5 resource_limit，無silenttruncate，無SLA或benchmark宣稱。

待驗：limit前/等/後、輸出JSON膨脹、timeout與child終止boundary後驗；數值是工程建議。

**完整規劃提問：** 最大回覆size與明示limit，避免靜默截斷／token成本如何處理？

**完整規劃答覆：** Gap：技術草案已提出：候選pilot limits明列blob1MiB/view16MiB/2000records/stdout8MiB/config64KiB/query256scalars/cursor4096bytes/Git10s/query30s；超過exit5 resource_limit，無silenttruncate，無SLA或benchmark宣稱。 後續須驗：limit前/等/後、輸出JSON膨脹、timeout與child終止boundary後驗；數值是工程建議。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u34

**所屬故事：S10**

原題：X17；契約包：獨立oracle與三端驗證回執。

提案：獨立由committed合成Git blobs與原dev2人工expected確認path/commit/rawsha/status/明示鏈；oracle不得呼叫被測parser/service建立expected；三端agree只是必要不充分。

待驗：獨立錯parser/錯digest mutant亦須被oracle發現，這是驗收方法非新standing verifier。

**完整規劃提問：** 獨立於共用parser的Git原文／expected oracle驗證如何處理？

**完整規劃答覆：** Gap：技術草案已提出：獨立由committed合成Git blobs與原dev2人工expected確認path/commit/rawsha/status/明示鏈；oracle不得呼叫被測parser/service建立expected；三端agree只是必要不充分。 後續須驗：獨立錯parser/錯digest mutant亦須被oracle發現，這是驗收方法非新standing verifier。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u35

**所屬故事：S02**

原題：X18；契約包：獨立oracle與三端驗證回執。

提案：使用既有事件鏈留named-client initiation、runtime/cwd、命令/exit、source/contract/code closure與result；dot可走已准delegated local route，不能一端跑三次貼名。Claude需正常既有session的真命令回執，不用OutsideVoice reviewer Bash。

待驗：後續用同一公開checkout唯讀rev-parse最小命令取得原tool_use/result；新CLI三端查詢仍屬產品UAT。

觀測限制：Claude自身發起既有唯讀命令的可回讀真回執pending-not denied；現有證據只有協調端host命令成功及Claude Read/Grep。

**完整規劃提問：** 命名client真正發起CLI invocation的可信端到端證據如何處理？

**完整規劃答覆：** Gap：技術草案已提出：使用既有事件鏈留named-client initiation、runtime/cwd、命令/exit、source/contract/code closure與result；dot可走已准delegated local route，不能一端跑三次貼名。Claude需正常既有session的真命令回執，不用OutsideVoice reviewer Bash。 後續須驗：後續用同一公開checkout唯讀rev-parse最小命令取得原tool_use/result；新CLI三端查詢仍屬產品UAT。 Gap／實作與驗證仍在，候選介面未成為已接受API。

### cli-p1-u21

**所屬故事：S01**（Fact核對）

原題：C24；非新增技術主題。

**完整規劃提問：** 實際雙使用者驗收context未定位就未驗，不得以未驗簽整片pass如何處理？

**完整規劃答覆：** Fact：AC1實際權限分隔test context未定位即未驗，不可因此簽整片pass；合成principals／label／allowlist不代替權限隔離。不新建帳號、不默縮五故事／三端目標；本輪原則已明示。

### cli-p1-u20

**所屬故事：S10**（Fact核對）

原題：C22；非新增技術主題。

**完整規劃提問：** 白名單snapshot省略lint不等於原repo缺檔，舊server script不等於CLI如何處理？

**完整規劃答覆：** Fact：interrogation prompt明示snapshot只收白名單，未帶scripts/lint.mjs不證明原repo缺檔。package.start／demo是既有HTTP server路徑，不能當CLI；不據此增刪產品範圍。

### cli-p1-u02

**所屬故事：S11**（Fact核對）

原題：C02；非新增技術主題。

**完整規劃提問：** Accepted缺Decision key時原狀態與effective的回覆如何處理？

**完整規劃答覆：** Fact：dev2原生沒有Decision key／effective／resolved／unresolved；Accepted缺Decision key不是原生格式錯。原Status與原文保留；若衍生查詢缺資料只能表示非權威的未知／能力限制，不新增key、不改需求或Accepted。

### cli-p1-u15

**所屬故事：S11**（Fact核對）

原題：C16；非新增技術主題。

**完整規劃提問：** dev2 0.25 Status格式／跨repo引用不可作同域supersession如何處理？

**完整規劃答覆：** Fact：snapshot的dev2 0.25模板／adr_lint STATUS regex與core此處相同；沒有證據支持較豐富Status新格式，版本pin不同不等於不相容。跨repo引用不能當同域supersession；原狀態仍照實保留。
