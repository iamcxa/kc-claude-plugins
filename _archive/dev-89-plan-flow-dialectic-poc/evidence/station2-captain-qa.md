## Station 2 — Q1 Demand reality (Captain, verbatim, 2026-09-03)

我很喜歡這四題，我認為方向是對的，這跟 CL 一直問我的問題完全一樣。第一題，目前主要容易遇到的問題是，PR 乍看可以，驗證很多面向，但是每個檔案進去看很容易遇到註解過多，或是容易找出其實不必要的檔案改動或新增，security 部分我沒有直接強烈的印象，但這也是個問題，因為沒有非常明確的驗證機制。目前 pr-review-flow 有 general security 這一塊，但問題是跑 dev-flow 不會用它，太重型了，手動 steering 等太久太零碎，所以要用 ship-flow 包起 dev flow 的用意就是，dev 走標準流程，輸出驗證結果，讓 pr-review 接手繼續驗證，必要時加入 e2e 更直接的驗證（我要直接，快速的驗證到重點，用 e2e-map 繪製地圖，e2e-flow 按 code logic 導航，幾次就可以錄製可重複的流程），最後補上 UAT 這樣就可以讓 flow 本身自我包含，且對齊預期

### FO reading
- Real pain, already felt: PRs that pass surface verification but carry excess comments and unnecessary file changes or additions. This is the minimal-necessity gap; DEV-78's surface-map check is the first enforcement point for it.
- Security: no strong incident, but named as a gap because there is no explicit verification mechanism. kc-pr-review has a general security pass; dev-flow never invokes it because it is too heavy and manual steering is slow and fragmented.
- The wedge the Captain is describing is not the three sentences themselves but the pipeline they sit in: dev-flow emits verification output -> kc-pr-review continues -> e2e (map, flow, record) when direct proof is wanted -> UAT. Sentence (c) "security findings block" is the hook that lets kc-pr-review's security pass become a ship-flow gate instead of a manual step.
## Station 2 — Q2 Status quo (Captain, verbatim, 2026-09-03)

我希望你可以參考 office-hour 用 harness 的 ask ui 從過去發現給我選項同時讓我可以自述，等於 plan flow應該要先觀察痛點，然後讓我選，再讓我自述補充。目前每次我幾乎都會問是否是最小堆疊，是否測過 without-it，驗證過哪些，此外我也會 UAT 親自測試，這些都等重。我也會看 PR diff，這是用來快速確認是否混入不必要檔案，是否過多註解，是否關鍵字不符合，我不會很仔細看 code logic，但就是從 diff 內容與 LOC 觀察是否有可能不是最小最必要堆疊

### FO reading
- The workaround today is the Captain himself, per PR: ask "smallest stack? without-it run? what was verified?", then UAT by hand, then eyeball the diff for stray files, excess comments, keyword mismatch, and LOC shape. He does not read logic; he reads shape. All of these carry equal weight to him.
- Method feedback (plan-flow design input, not a Q2 answer): station 2 should be run through the harness Ask UI, offering options mined from past evidence first, then a free-text field; observe pain -> let the Captain pick -> let him elaborate. Recorded as a plan-flow requirement.
## Station 2 — Q3 Desperate specificity (Captain, Ask UI, 2026-09-03)

Options mined from evidence; the Captain selected ALL FOUR:
- 你在 UAT 時 — PR passes surface checks; the Captain's own questions or diff read catch stray files, excess comments, missing without-it (DEV-66 round 0 parser).
- FO 在驗收時 — Codex catches a P1 per Issue and the FO re-messages (DEV-66/65/64, 1-2 rounds each), each round ~10 min plus quota plus Captain wait.
- 下一層 worker — a lower-layer fix invalidates an already-dispatched upper layer's base (DEV-64 on DEV-65 round-0).
- 沒人，但沒證據 — security: no incident, no mechanism proving none.
No free-text elaboration given.

### FO reading
Selecting all four says the pain is not one role's; the same missing gate is re-paid at every station (Captain, FO, next worker, and an unmeasured security surface). That is the strongest possible demand signal for "put it in the flow, not in a person".
## Station 2 — Q4 Narrowest wedge (Captain, Ask UI, 2026-09-03)

Selected: 三條一起，Pilot 深度 — all three sentences enter the README with contract-test pins now; script enforcement is deferred to a Production round.

### FO reading -> station 2 outputs
Profile: pilot-product-slice.
User value (one line, FO draft for Captain confirmation, 27 words):
  "A ship-flow candidate cannot reach the Captain's UAT with an unverified lower layer, an unsandboxed without-it run, or an unblocked security finding."
Why Pilot: the Captain wants the rule in the flow, not in a person (Q3: all four roles pay today), and accepts README-plus-pin as sufficient for this round; script enforcement is a named promotion trigger.
