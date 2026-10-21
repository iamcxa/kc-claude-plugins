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

## 決策空間與專案 ADR 的定義

**決策空間**是一個 Git repo，存放使用者本人的裁示：使用者的原話、ADR 格式、帶 Decision key、有版本，由 agent 起草、使用者確認後經 PR 合併（D3）。每個空間一個 repo，因為讀者不同，權限要分開（D6）。

| 空間 | 放什麼 | 主要讀者 | 狀態 |
| --- | --- | --- | --- |
| 產品空間 | 跨產品、跨 repo 的方向，例如「長期打造 FO's FO」 | Claude、Codex、dot | 尚未建立 |
| 人生空間 | 人生方向、職涯、投資與財務 | dot 與使用者的私人環境 | 現有原型 repo 的財務部分；依 D6 之後拆出 |

**專案 ADR** 是某個產品 repo 自己的 `docs/adr`，由 dev2 管理（格式、配號、檢查、協調者落地）。它只裁決那個產品內的事，需要依據上層方向時，以引用區塊固定引用決策空間裡某一筆的版本，不複製內容。

本文不再用「ADR repo」這個詞，因為它分不出決策空間和專案 ADR。

## 什麼寫進哪裡（POC 測過的規則，依 POC 結果修訂）

依序問下面五個問題，第一個答「是」的就是去處。一件事只寫在一個地方；其他地方需要時只放指向，不重述內容。

| 順序 | 問題 | 是 → 放哪裡 |
| --- | --- | --- |
| 1 | 這是 agent 的推測、筆記或還沒確認的想法嗎？ | agent 記憶或任務的待確認事項；不寫成任何裁示 |
| 2 | 這只影響眼前這個任務嗎？ | 任務檔 |
| 3 | 這是延後要做、使用者看得到的功能嗎？ | 故事地圖（一個任務裡的實作取捨不算，留在任務檔） |
| 4 | 這是給 agent 的操作指示（怎麼工作），而不是使用者對方向的裁決嗎？ | CLAUDE.md／AGENTS.md |
| 5 | 這是使用者的裁決，而且範圍只在某一個產品 repo 內嗎？ | 該 repo 的專案 ADR |
| — | 以上皆否：使用者的裁決，跨產品或沒有對應的產品 repo | 對應的決策空間 |

授權 agent 自行決定的範圍，是一筆專門的授權 ADR（ADR 0011 L3），放在被授權者所屬的地方：授權某個產品的協調者，放那個產品的專案 ADR；跨產品的授權放產品空間。錢、合併、對外動作與不可逆變更永不授權。

**指示檔只指位置，不重述裁示。** CLAUDE.md／AGENTS.md 可以寫「裁示在哪裡、何時去查」，不抄某一筆的內容。抄過去的摘要會過時，例如 qnow 的 AGENTS.md 指向一個已刪除的分支去讀 ADR 0001（2026-10-20 以 `git ls-remote` 確認）。

**POC 看到的錯誤與對應的規則：**

| POC 中的錯誤（adr-read-and-route-poc） | 對應規則 |
| --- | --- |
| 同一件事既寫成 ADR，又寫進 AGENTS.md | 一件事只寫一處；指示檔只指位置 |
| 任務內的取捨被寫進故事地圖 | 第 3 問：故事地圖只收延後、使用者看得到的功能 |
| 工作習慣被寫成決策空間的 ADR | 第 4 問：操作指示放指示檔 |
| 未確認的直覺被寫進任務檔當結論 | 第 1 問：推測不寫成裁示 |

## 用真實例子檢查

| 例子 | 依規則的去處 | 現在在哪裡 | 一致嗎 |
| --- | --- | --- | --- |
| 「長期打造 FO's FO」（使用者 2026-10-19 起的說法） | 產品空間（第 5 問否：跨產品） | 只在對話與 agent 記憶裡 | 否：沒有任何紀錄 |
| qnow 用 Clerk 做身分驗證 | qnow 的專案 ADR（只在 qnow 內） | qnow 的 ADR 0001 | 是 |
| dev2 的授權階梯（ADR 0011） | kc-claude-plugins 的專案 ADR：它規定 dev2 這個產品怎麼運作 | kc-claude-plugins 的 ADR 0011 | 是；但「錢永不授權」這類跨產品的原則，依規則應在產品空間另有一筆 |
| 「先開 Draft PR，CI 綠了再轉 ready」 | 指示檔（第 4 問：操作指示） | 使用者的全域 CLAUDE.md | 是 |
| 家庭財務的裁示 | 人生空間 | 原型 repo 的財務命名空間，與另一個命名空間放在一起 | 部分：依 D6 應拆成獨立 repo |
| plan、dev、ship 三個流程只靠輸入輸出約定串接 | 產品空間（跨 kc-claude-plugins 內多個 plugin 的方向）或 kc-claude-plugins 專案 ADR | agent 記憶 | 待定（見下） |

**待使用者決定：**

1. 原型 repo 裡另一個命名空間（關於 dot 本身與溝通流程的裁示）屬於產品空間還是人生空間？
2. 「跨 kc-claude-plugins 內多個 plugin」算一個產品（放專案 ADR），還是跨產品（放產品空間）？上面最後一個例子取決於此。
3. 操作指示若日後需要被其他裁示引用（例如工程 ADR 要依據「先開 Draft PR」），是否升級成決策空間裡的一筆，指示檔改為指向？

## 取代 dev2 ADR 讀取方式的條件（未決）

- **現況：** dev2 沒有專用的讀取器，靠指示文字和 hook（`agent-reads-governing-adr`）。
- **要先成立的：**
  1. POC 顯示，agent 透過 kc-decision-log 的 skill 或 hook，比 dev2 現行方式更常在做決定前讀到正確的 ADR，而且成本沒有明顯增加。
  2. 工程 ADR 沒有 Decision key 時的 effective 規則已經定好。
  3. dev2 FO 同意，使用者裁決。

## 限制

- dot 是 ChatGPT 上沒有終端機的 agent，要等 MCP 或 connector 才讀得到（D13）。
- agent 會不會在沒人提醒時自己去查、會不會把資訊放對地方，還沒證實；這正是 POC 要量的。
