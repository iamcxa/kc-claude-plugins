# kc-adr 與 dev2 的邊界合約（草稿 v2）

**方向已接受，細節待接受。** 使用者 2026-10-21 接受：kc-adr 是讓 agent 讀寫 ADR 的套件，dev2 是第一個使用者、moneyflow 是第二個；每個 repo 的 ADR 就是它自己的決策紀錄；前綴是選用的（「可以，但是前綽應該是選用，不是必要」）。本文其餘內容是提案。v1 的「決策空間」概念由此取消。

## 定位

kc-adr 負責讓 agent 把 ADR 讀對、寫對、寫到對的地方，任何 repo 都能用。它不管任務、關卡與交付，那是 dev2 的事。

| 擁有者 | 負責 | 不做 |
| --- | --- | --- |
| kc-adr | 讀：在固定版本讀到正確的一筆並核對指紋；寫：什麼該寫成 ADR、寫到哪個 repo、怎麼寫；選用的前綴規格 | 任務、關卡、驗收；授予任何行動許可 |
| dev2 | 任務、關卡、驗收；協調者把裁示落成 ADR 的時機；`Precedent:` 行（ADR 0011 的 L2） | — |
| kc-journey-map | 使用者看得到的能力，包括延後的功能 | 裁示 |
| 使用者 | 裁決、合併、授權 | — |

ADR 寫入的工具今天都在 dev2：格式模板、`number_guards.py` 的配號、`adr_lint.py` 檢查。這些要搬到 kc-adr，還是由 kc-adr 包住 dev2 的工具，**待 dev2 FO 與使用者決定**。在決定前，kc-adr 不另做一套。

## 每個 repo 的 ADR 就是它的決策紀錄

| 種類 | 例子 | 放什麼 |
| --- | --- | --- |
| 單一產品 repo | qnow、moneyflow | 這個產品內的裁決 |
| monorepo | kc-claude-plugins（多個 plugin） | 各 plugin 的裁決，以及跨 plugin 的方向 |
| 人生目標 repo | me-company（「me as a company」） | 人生方向、職涯，以及要被多個 repo 依據的個人原則 |

一筆 ADR 需要依據另一個 repo 的裁決時，以引用區塊固定引用那一筆的版本（repo、路徑、版本、指紋），不複製內容。

## 前綴（選用）

前綴有兩種用途，由各 repo 自己決定要不要開：

1. **跨 repo 引用的短名。** 例如用 `ME#0003` 代表 me-company 的第 3 筆。這不改任何檔案，只是引用時的簡寫；引用區塊本來就帶 repo 名稱。
2. **monorepo 內分命名空間。** 例如在 kc-claude-plugins 裡，dev2 和 kc-journey-map 各自從 0001 編號。這會改路徑與編號，配號和檢查工具都要支援。dot 的原型用過這種做法：`projects/KEY/docs/adr`，編號寫成 `KEY#NNNN`。

kc-claude-plugins 適合開第 2 種：它有多個 plugin，現有的 28 筆 ADR 分屬不同 plugin，卻共用一條編號。提案是等 kc-adr 接手配號、能支援命名空間之後再開，新的 ADR 用命名空間，舊的 28 筆保留原編號、不重編。

## 讀

POC（dev2-poc `adr-read-and-route-poc`，已結案）顯示，agent 本來就會讀對 ADR；給它一個讀取工具，沒有勝過只教它用 git 讀。所以 kc-adr 不做讀取工具，`read-adr` skill 教的是：

- 用 `git show <版本>:<路徑>` 讀固定版本，用 `shasum -a 256` 核對指紋；
- 看 Status 與 `Superseded by` 行，判斷一筆是否還在生效；
- 依引用區塊跨 repo 讀，讀不到就停下回報，不靠轉述。

## 寫到哪裡

依序問下面五個問題，第一個答「是」的就是去處。一件事只寫在一個地方；其他地方需要時只放指向，不重述內容。

| 順序 | 問題 | 是 → 放哪裡 |
| --- | --- | --- |
| 1 | 這是 agent 的推測、筆記或還沒確認的想法嗎？ | agent 記憶或任務的待確認事項；不寫成任何裁示 |
| 2 | 這只影響眼前這個任務嗎？ | 任務檔 |
| 3 | 這是延後要做、使用者看得到的功能嗎？ | 故事地圖（一個任務裡的實作取捨不算，留在任務檔） |
| 4 | 這是給 agent 的操作指示（怎麼工作），而不是使用者對方向的裁決嗎？ | CLAUDE.md／AGENTS.md |
| 5 | 這是使用者的裁決，而且只關係到某一個 repo 嗎？ | 那個 repo 的 ADR |
| — | 以上皆否：使用者的裁決，跨好幾個 repo | 它們共同的上層：同一個 monorepo，或 me-company |

**指示檔只指位置，不重述裁示。** CLAUDE.md／AGENTS.md 可以寫「ADR 在哪裡、何時去查」，不抄某一筆的內容。抄過去的摘要會過時，例如 qnow 的 AGENTS.md 指向一個已刪除的分支去讀 ADR 0001（2026-10-20 以 `git ls-remote` 確認）。

授權 agent 自行決定的範圍，是一筆專門的授權 ADR（ADR 0011 L3），放在被授權者所屬的 repo。錢、合併、對外動作與不可逆變更永不授權。

**POC 看到的錯誤與對應的規則：**

| POC 中的錯誤 | 對應規則 |
| --- | --- |
| 同一件事既寫成 ADR，又寫進 AGENTS.md | 一件事只寫一處；指示檔只指位置 |
| 任務內的取捨被寫進故事地圖 | 第 3 問 |
| 工作習慣被寫成 ADR | 第 4 問 |
| 未確認的直覺被寫進任務檔當結論 | 第 1 問 |

## 用真實例子檢查

| 例子 | 依規則的去處 | 現在在哪裡 |
| --- | --- | --- |
| 「長期打造 FO's FO」 | kc-claude-plugins（跨這個 monorepo 內多個 plugin 的方向） | 只以背景出現在原型 repo 一筆 2026-10-19 的跨 FO 試跑裁示裡 |
| qnow 用 Clerk 做身分驗證 | qnow | qnow 的 ADR 0001 |
| dev2 的授權階梯 | kc-claude-plugins | kc-claude-plugins 的 ADR 0011 |
| 「先開 Draft PR，CI 綠了再轉 ready」 | 指示檔（第 4 問） | 使用者的全域 CLAUDE.md |
| 家庭財務的裁示 | moneyflow；人生層次的財務原則放 me-company | 原型 repo 的財務命名空間 |
| 「錢永不授權」這類跨產品原則 | me-company | 只在 kc-claude-plugins 的 ADR 0011 裡 |

**原型 repo 的去留待決：** 原型 repo 裡的裁示要按上表搬到各自的 repo，還是原地保留、只改讀法，待使用者決定。

## 與 dev2 的接點

- **提醒：** dev2 任務 `agent-reads-governing-adr` 的 hook 會在工作階段開始時列出 ADR 標題，指示檔加一段指向 `docs/adr`。kc-adr 不另做 hook；之後若要列出其他 repo 的標題，換掉 hook 背後的腳本即可（S30）。
- **先例：** 協調者的 `Precedent:` 行照舊引用 ADR；跨 repo 時改用引用區塊。
- **worker：** dev2 的 worker 讀寫 ADR 時載入 kc-adr 的 skill。這是 dev2 作為第一個使用者的接法，要 dev2 FO 同意。

## P1 重排提案（待接受）

- **任務一：** 交付 `read-adr` skill（讀的做法，加上「寫到哪裡」五問）與選用前綴的規格，不做讀取工具。驗收以 dev2 的 worker 實際載入並照做為準。
- **任務二：** 原本的 Codex 交接演練延後到後面的切片，因為它成本高，也不再是證明價值的第一步。
- **moneyflow 接入：** 列為第二個使用者，排在任務一之後。
- **地圖：** 「決策空間」相關的故事用字要改成以 repo 為單位，例如 S01；改動在你接受本提案後提出。

## 限制

- dot 是 ChatGPT 上沒有終端機的 agent，要等 MCP 或 connector 才讀得到。
- agent 會不會把資訊放對地方，POC 顯示 Claude 有一份規則時會明顯進步（6/10 → 9/10），Codex 沒有（5–6/10）；規則還要再測。
