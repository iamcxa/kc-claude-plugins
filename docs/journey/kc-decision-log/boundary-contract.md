# kc-decision-log 與 dev2 的邊界合約（草稿）

**草稿，使用者尚未接受。** 內容是兩個工具各自負責什麼、分開時各自怎麼用、合在一起時在哪裡接上。kc-decision-log 是否取代 dev2 讀取 ADR 的方式仍未決定；要先由 POC 證明 agent 用它比較容易讀到正確的 ADR（使用者 2026-10-21：「甚至未來工具可以取代 dev2 的 ADR 讀取器，但這個不急著決定，必須證明更容易讓 agent 使用」）。格式參照 dev2 與 kc-journey-map 的邊界（`kc-dev-flow-2/extensions/journey-map/EXTENSION.md`）。

## 各自負責

| 擁有者 | 負責 | 不做 |
| --- | --- | --- |
| kc-decision-log | 在固定 commit 讀取任何決策空間裡 ADR 格式的紀錄：原始 bytes 指紋、照原文回報 Status、保守的 effective 判定；交接用的引用區塊；唯讀 skill；決策空間的設定（binding） | 寫入、配號、建任務、開 PR 或合併（D3）；授予任何行動許可 |
| dev2 | 工程 repo 的 ADR 寫入：格式模板、`number_guards.py` 配號、`adr_lint.py` 檢查、協調者把裁示落成 ADR、`Precedent:` 行（ADR 0011 的 L2）；任務、關卡與驗收 | 讀取使用者層的決策空間 |
| kc-journey-map | 使用者看得到的能力，包括延後的功能 | 裁示與工程決策 |
| 使用者 | 裁決、合併、授權 | — |

## 分開也能用

- **只有 dev2：** 照現行方式。設計階段讀相關領域的 ADR，協調者遇到 ADR 已決定的事以 `Precedent:` 套用。dev2 待辦任務 `agent-reads-governing-adr` 會補上指示檔指向與 ADR 標題 hook。
- **只有 kc-decision-log：** 任何 repo 只要有 ADR 格式的紀錄就能讀，不需要 dev2；使用者層的決策空間（產品方向、人生、財務）靠它讀。

## 合在一起時接上的地方

- **交接：** 傳出的 agent 把 kc-decision-log 的引用區塊寫進 dev2 任務說明（D1）。接手的 worker 開工前用 `effective --expect-digest --require-effective` 重讀，不符或不在生效狀態就停（`read-ruling` skill）。
- **先例：** 協調者的 `Precedent:` 行可以引用使用者層的裁示，把 L2 從單一 repo 擴大到使用者層。待 POC 證明 agent 會實際這樣做。
- **提醒：** dev2 的 ADR 標題 hook 可以接上已設定決策空間的標題（S30）。兩邊共用一個 hook 機制，不各做一套。

## 介面與版本

- **輸入格式：** dev2 的 ADR 模板，格式標準是 `adr_lint.py`，由 dev2 擁有。kc-decision-log 在輸出的 `format_baseline` 宣告它移植的是哪個 dev2 版本。
- **輸出：** 引用區塊的欄位、JSON 欄位與結束碼由 kc-decision-log 擁有並版本化；P1 實作時定第一個 schema 版本。
- **Decision key：** 是 kc-decision-log 的保守擴充，不是 dev2 的格式要求。dev2 的工程 ADR 沒有它，那些紀錄的 effective 規則延後再定（D9）。

## 什麼寫進哪裡（POC 要測的規則草稿）

| 資訊 | 放哪裡 | 誰寫 |
| --- | --- | --- |
| 跨 repo 的方向；人生、職涯、財務這類沒有工程 repo 的裁示 | 使用者的決策空間 | agent 起草，使用者確認後經 PR 合併（D3） |
| 某個工程 repo 內，會約束之後工作的產品規則、限制或方向 | 該 repo 的 dev2 ADR | dev2 協調者落地，worker 寫檔 |
| 只管單一任務的取捨 | 任務檔 | 協調者／worker |
| 延後的使用者功能 | 故事地圖 | 地圖的維護流程 |
| agent 該怎麼工作的指示 | CLAUDE.md／AGENTS.md | 使用者或經使用者同意 |
| agent 自己的筆記 | agent 記憶，不當權威 | agent |
| agent 可以自行決定的範圍 | 一筆專門的授權 ADR（ADR 0011 L3）；錢、合併、對外動作、不可逆變更永不授權 | 使用者裁決 |

判斷原則：會被其他 agent 或之後的工作當成依據的，放有版本、有人確認的地方（決策空間或 ADR）；只影響眼前這件事的，留在任務裡；描述怎麼工作的，放指示檔。

## 取代 dev2 ADR 讀取方式的條件（未決）

- **現況：** dev2 沒有專用的讀取器，靠指示文字和 hook（`agent-reads-governing-adr`）。
- **要先成立的：**
  1. POC 顯示，agent 透過 kc-decision-log 的 skill 或 hook，比 dev2 現行方式更常在做決定前讀到正確的 ADR，而且成本沒有明顯增加。
  2. 工程 ADR 沒有 Decision key 時的 effective 規則已經定好。
  3. dev2 FO 同意，使用者裁決。

## 限制

- dot 是 ChatGPT 上沒有終端機的 agent，要等 MCP 或 connector 才讀得到（D13）。
- agent 會不會在沒人提醒時自己去查、會不會把資訊放對地方，還沒證實；這正是 POC 要量的。
