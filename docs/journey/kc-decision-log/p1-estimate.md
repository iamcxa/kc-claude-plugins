# P1工程工作量粗估（提案）

**完整P1保守粗估32–48 active工程小時。** 這是依source差異／驗證拓樸的我方工程判斷，未經同類交付校準；不是歷史測得生產率、統計信賴區間或AI wall-clock完成預測。五故事／三端／Pilot／D1-D5不變，沒有為估算偷縮目標。

先前投入原話「1-3天」保留；本輪已明確澄清為**三個完整工作日**，上限仍3 days。工作日／日曆日不再是待選問題。以下8h/工程工作天只是我方規劃換算假設，24h不是使用者原話或承諾；不能據此保證完整P1三日可交。

| 包 | active工程小時 | 已觀測差異 → 工程推論 |
| --- | --- | --- |
| A 來源／權威／context | 4–6 | 既有source用project#number，app單owner；binding／完整canonical／context來源／語義fingerprint不存在，D1-D5與authority界線已定。 → 新binding/context模型、canonical引用與配置衝突拒絕，局部對照驗證。 |
| B 固定blob／loader／native parser | 8–12 | build耦合code/data root、UTF8字串與dist輸出；SOURCE_PATH/DOT與native不同；effective有全view issues保守邏輯。公開raw-blob四步成功但有Apple bootstrap警告，partial/alternate/owner/network未驗。 → 新的唯讀object loader/size/bytes/環境控制；native讀取適配、原生診斷與非權威查詢能力分離；局部boundary驗證。 |
| C CLI／output／checkout入口 | 6–9 | service有查詢/arg/paging雛形但contract仍是舊MCP；package無bin，CLI dispatcher/JSON-human/error/code closure尚未有。Node24與既有local命令已觀測。 → Node24 checkout命令、共享core連接、統一exit/分页/limit與版本輸出、可比性標記及局部驗證。 |
| D Oracle／三端receipt／OS harness初次驗證 | 8–12 | tests/helpers經同parser建snapshot，不能當獨立oracle；dot delegation基礎已具，Claude正常命令回執未具；OS probe只限兩已知檔，Git/helpers/objectstore/aliases等整體未驗。 → committed合成來源+獨立expected，named-client啟動回執與整個query子程序OS隔離harness，首次驗證。 |
| 跨包整合／Pilot審查驗收重跑與一次修正 | 6–9 | canonical/source/bytes/error/receipt與6AC彼此相接，既有Pilot/原生planning guard與產品驗收需分開完成；沒有同類交付生產率基準。 → 跨包介面整合、根據D首次驗證結果的一輪修正與重跑、既有Pilot審閱/驗收收尾及provenance核對。 |

**合計32–48h；按8h/工程工作天換算為4–6工作天，非calendar ETA。** 前4包只含各自建置／局部驗證或D首次harness驗證；末項是跨包整合、首次結果後一輪修正／重跑及Pilot收尾，不重複計數。

## 主要假設與不確定性

- 使用既有Node24、trusted Git與固定checkout入口，不做global install／新dependency／remote host或MCP搬遷。
- 單binding/fullcommit，原生lint結果與非權威effective分開；撤回整binding一律unresolved策略，UTF8／資源範圍外明示error，不新增binary或perrecord復原引擎。
- raw Git公開模板四步已成功但有Apple bootstrap warnings；missing-object／partial／network／foreign owner/config／alternates及整個helpers/context仍未驗。這是工程風險，不是已證新權限需求。
- dot委派本local task的route基礎已具；Claude auth／Read-Grep已具，但自己發起正常readonly命令的原回執仍pending-not denied。不能用協調端host執行替代。
- D需要獨立oracle／三端initiation／完整Git objectstore與alias負向拓樸；現有helpers與兩檔OS deny不足以宣稱通過。
- 沒有同類交付吞吐校準。舊64/58 unit只作可重用基礎，不按其毫秒耗時、題數、LOC或3天倒推。
- 不算外部等候；不預扣並行／AI加速，亦不含無限修正回合。

若Claude既有命令route或OS對Git/helpers隔離需要較大修正，另加8–16h：risk envelope為**40–64h／5–8個8h工程工作天**。這是敏感度範圍，不是機率上界。需要新身份／安裝／權限／平台host改動時不塞入range，停止回具體scope。

## Fit與真正可決的資訊

| 已確認投入與工程換算 | 結論 |
| --- | --- |
| 人類已明確「三個完整工作日」 | 維持3 days上限；不重問工作日／日曆日、不自增預算。 |
| 若我方以8h/工作天換算三日為24h | 32–48h不支持該假設下完整P1可交；24h不是人類原話或承諾。 |
| 正式fit | 估量未校準，完整CLI／三端整合驗收未完成，沒有fit通過證明，保持unknown。 |

優先補正常既有Claude工作階段一條公開checkout唯讀命令回執，工程估量維持32–48 active小時／條件風險40–64h。原P1／Pilot／D1–D5及已澄清的三完整工作日不重問；不因修正文案倒推三日fit或擅縮目標。

既有明確接受在scope／premises仍相符時沿用；格式或Fact/Gap記錄不自動要求重選。真正改投入／value／scope／acceptance才呈現新決定。本估算保留在此 Markdown，供原生問答及切片說明引用；**原appetite不變，正式days scalar estimate仍null／fit unknown，不構成API接受、實作授權或accepted digest。** 歷史assessment／guard不改寫。

具體介面與31題指向見[P1技術契約草案](p1-technical-contract.md)；範圍、假設與分包見[切片說明](slice-map.md#p1)及本頁；不另創原生 estimate schema。

目前沒有已證不可行的技術阻塞。Claude本人正常唯讀Git命令原回執仍pending（非denied）；完整OS harness與三端CLI屬P1待實作驗證，不要求使用者先提供成品。投入時間基準已明確三完整工作日；若後續確認估量超過既定投入，再呈現是否加額或讓完整P1維持draft的具體選擇，不默縮目標或自增預算。
