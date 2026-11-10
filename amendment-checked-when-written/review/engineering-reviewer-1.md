# Engineering review: amendment-checked-when-written

Date: 2026-11-10

結論：建議 **adjust（修正覆蓋說明）**。七筆指定提交中，候選程式確實只回報五筆；另外兩筆符合核准設計的整份檔案跳過條件。但「留給既有格式規則」不能解讀成兩筆都會被既有規則抓到：dev2 那筆是 L3 無法判定、整次退出碼 2；relay 那筆沒有任何違規診斷、整次退出碼 0。從七改五不需改候選程式，卻確實撤回原本的七筆回報承諾，包括設計中重複宣稱的七筆覆蓋。這是既有設計衝突的取捨，不能寫成沒有降低任何已承諾保障。

本報告使用的名稱：L2 是派工紀錄完整性規則；L3 是修訂紀錄不可改寫規則；L4 是移動條件不得重用編號規則；AC-4 是第四項驗收條件；FO 是協調工作的一副。

```yaml
engineering_reviewer_report:
  question: "Amendment 1 將歷史重跑由七筆改五筆，是否撤回 Captain 已核准內容，程式需要改什麼，既有規則是否補足兩筆？"
  revision: "candidate 71eb2ec4298812d831573386324641ca6babff5d; base 6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1; task/dispatch at state f98c8426e8f8451726ca263f7a0a621c1239290e"
  conclusion: "整份檔案跳過符合核准 Mechanism；五筆與候選行為一致。七筆承諾被縮減，既有規則並未提供等同覆蓋。保留候選程式，先更正對 Captain 與下游驗收的說明。"
  material_evidence:
    - "獨立執行兩筆完整 laws_check.py：dev2 為 L2 0、L4 0、L3 cannot judge，exit 2；relay 為 L2 0、L3 1 event / 0 violated、L4 0，exit 0。"
    - "直接以候選 L4 的 walk/Context/judge 重跑表內七筆各自的第一父提交範圍，結果為 dev2 2、qnow 3、relay 0。"
    - "parse_amendments 在兩筆提交及各自父提交都回報結構問題；L4 在任一側有問題時直接 continue。"
    - "記憶體內對照顯示：只修結構時不回報，之後只加無關文字也不回報仍存在的 unmarked 缺陷；這不是實際修復或 L3 合規證明。"
    - "候選工作樹乾淨；未改程式、任務、修訂、採用版本或派工紀錄。"
  risk_tradeoff: "保留跳過可避免以不可靠結構推論移動，但缺陷可能完全沒有當次警訊，也不保證修好格式後補報。最便宜可信做法是精確記錄兩筆結果及覆蓋界線，保留現有候選；若 Captain 要求七筆都在寫入時被報出，需另作明確設計決定，不能把那種改動藏入本次文字修訂。"
  recommendation: adjust
  confidence: high
  disproof_condition: "同一候選與相同兩組 before/after 範圍若能重現 L2/L3 對 relay 的實際違規診斷，或紀錄證明 Captain 已明確接受 relay 整次通過與修格式不補報的界線，會改變本建議。換候選、改歷史、或後來的派工檢查不能反證本次結果。"
  authority_boundary: "本報告僅提供建議。Captain 保留風險取捨；FO 保留說明、記錄及派工；實作工人依核准修訂移動驗收條件。未推進狀態、解除關卡、授權發布或判定可收線。"
```

## 綁定的來源與範圍

- 候選工作樹：`/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-amendment-checked-when-written`，分支 `spacedock-ensign/amendment-checked-when-written`，HEAD 為上述候選。
- 工作流程根目錄：`/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree`，HEAD 為上述 base。其既有 `.gitignore` 修改未動。
- 狀態根目錄：上述工作流程根目錄的 `docs/dev2/.spacedock-state`，分支 `spacedock-state/dev2`。任務及本次派工檔的工作副本都與狀態提交 `f98c8426e8f8451726ca263f7a0a621c1239290e` 相同。
- 任務 `amendment-checked-when-written.md` 的 SHA-256：`83be1f6306ebb106c6c0a0a9f153f813773b1dee9f8cb4cbeb4ff904657a6527`。
- 派工 `amendment-checked-when-written/dispatch/engineering-reviewer-1.md` 的 SHA-256：`320381b094d5ea092889a2b344de710488b10c32958d92ff067ae79f61f366d7`。
- 以下程式路徑均相對候選根目錄；任務路徑均相對狀態根目錄。引用用檔名與可搜尋原文，不依賴行號。只建立本報告；其他工作的未追蹤驗證資料未動。

## 1. 兩筆是否符合跳過條件，既有規則是否回報？

**符合跳過條件；既有規則的結果不同，不能合稱為兩筆均有保障。**

任務 `amendment-checked-when-written.md`，Design / Mechanism 明寫：

> A file whose `parse_amendments` reports structural issues is left to L2/L3 and not judged by L4.

候選 `kc-dev-flow-2/scripts/laws_check.py`，`l4_amendment_moves_use_fresh_ids` 的條件是：

```python
if parse_amendments(before)[1] or parse_amendments(after)[1]:
    continue
```

候選 `kc-dev-flow-2/scripts/design_surfaces.py`，`move_defects` 也在 `if issues:` 時 `return []`。因此一個無關修訂標題的結構問題，可以使同檔其他修訂也不受 L4 判斷；不是只跳過出錯的那一個修訂。

### dev2 的 release-acceptance 提交

提交：`bf8c73be99c4f0a569a15ce1ee7426578ae7ce85`；父提交：`aa4f5b7c8b52fe27031851c399fda7346da87b1d`；檔案：`release-acceptance/index.md`。

直接對兩個提交的原始內容執行候選 `parse_amendments`，都得到 `amendment outside '## Captain amendments'`、`malformed amendment heading` 與 `duplicate amendment number 1`，對應可搜尋標題 `### Amendment 1`。同檔的目標是正常位於 `## Captain amendments` 的 `### Amendment 2 — 2026-10-23, chat`；該次提交加入其 `Superseded text:` 移動內容。

實際完整 CLI 輸出包含：

```text
L2 dispatch-record-complete: 0 events judged in aa4f5b7c8b52..bf8c73be99c4, 0 violated
L4 amendment-moves-use-fresh-ids: 0 events judged in aa4f5b7c8b52..bf8c73be99c4, 0 violated
```

另有 `L3 amendment-append-only: cannot judge:`，其原因為 `ambiguous protected spans`，並列出標題格式及重複編號問題；整次退出碼 **2**。這是無法判定的非零訊號，**不是 L3 抓到未標記替代條件或重用編號的違規**。

### relay 的 owner-sees-all-feedback-room 提交

提交：`06cadae7681fe3425bb47f66efa3d17e8de837ea`；父提交：`8a5b7f0280c87cad390a80712a4051ba18b53730`；檔案：`owner-sees-all-feedback-room.md`。

兩個提交的候選解析器都回報 `amendment outside '## Captain amendments'`，對應 `### Amendment 2 — 2026-10-13, chat at the ideation gate`。同檔目標是 `### Amendment 3 — 2026-10-13, chat at the validation gate`，其 `Supersedes: AC-1, AC-2` 沒有 waiver（免替代條件的明文註記）。

實際完整 CLI 輸出：

```text
L1 observer-before-sentinel: 0 events judged in 8a5b7f0280c8..06cadae7681f, 0 violated
L2 dispatch-record-complete: 0 events judged in 8a5b7f0280c8..06cadae7681f, 0 violated
L3 amendment-append-only: 1 events judged in 8a5b7f0280c8..06cadae7681f, 0 violated
L4 amendment-moves-use-fresh-ids: 0 events judged in 8a5b7f0280c8..06cadae7681f, 0 violated
```

整次退出碼 **0**。這筆沒有既有法律違規或無法判定的診斷。不能把 L3 的「有判斷一個事件」說成「有報出問題」。

原因可直接由候選程式核對：

- `kc-dev-flow-2/scripts/laws_check.py` 的 `l2_dispatch_record_complete` 只在 `status in "AR" and DISPATCH.match(new)` 且符合新增派工條件時建立事件。兩筆 `git show --stat` 都只改任務檔，沒有新增派工紀錄，所以 L2 沒有事件。
- 同檔 `parsed_amendments` 只把包含 `"duplicate"` 或 `"malformed"` 的結構診斷轉成 `Cannot`。relay 的「位於修訂區塊之外」不在這兩種之內。
- `l3_amendment_append_only` 判斷舊修訂是否被改寫；`payload_append_allowed` 接受符合格式的新增移動內容。它不查替代標記，不能代替 L4。
- `kc-dev-flow-2/references/sd/laws.md` 的 L2 Event 明寫 `adds a dispatch/<name>.md record`；L3 Rule 明寫 `it checks shape, not origin or truth`。候選測試 `test_structural_issues_are_left_to_existing_laws` 只證明 malformed 標題會產生 L3 `cannot judge`，沒有證明 relay 這種區塊歸屬問題也會產生非零訊號。

重現命令（在候選工作樹執行，皆只讀提交內容）：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B kc-dev-flow-2/scripts/laws_check.py /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state --before 'bf8c73be99c4^' --after bf8c73be99c4 --readme /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/README.md
PYTHONDONTWRITEBYTECODE=1 python3 -B kc-dev-flow-2/scripts/laws_check.py /Users/kent/conductor/workspaces/subspace-relay/beirut-dev2/docs/dev2/.spacedock-state --before '06cadae7681f^' --after 06cadae7681f --readme /Users/kent/conductor/workspaces/subspace-relay/beirut-dev2/docs/dev2/README.md
```

## 2. 七改五撤回了什麼，程式改什麼？

**撤回七筆都由 L4 報出的驗收承諾；沒有證據顯示還需要撤回別的功能、改動候選程式，或縮減其他驗收條件。** 但七筆承諾不只出現在 AC-4，也出現在同一份已核准 Design 的能力說明與推薦理由，必須在後續報告中明確註記已被 Amendment 1 取代，不能繼續引用為現行能力。

可搜尋原文均在 `amendment-checked-when-written.md`：

- AC-4：`prints L4 events exactly at the seven commits named there`。
- Design / Existing-code capability check：`it fires at 7 commits`，其前文限定來源為 `A prototype of move_defects`。原型的歷史量測可以保留為歷史事實，但不能當成候選程式的結果。
- Design / Decisions for the Captain / D1：`it judges every state commit, and it fires on all 7 events above`。這項推薦理由在候選程式不成立。
- Amendment 1：`Captain: 「改成 5 次（建議）」`，`Supersedes: AC-4`；其 Asked 明說 `你核准的設計同時寫了「歷史重跑抓到 7 次」和「任務檔格式有問題時新規則不判，留給既有的格式規則」，兩者衝突`。

這表示 Captain 已選擇保留結構跳過、將期望改五筆；不是工人單方面刪掉一項可實現但不願實作的承諾。另一方面，Asked 的 `並寫明另外 2 次留給既有格式規則` 只足以表示責任範圍，不能證明等同偵測。現在已有 relay 整次通過的直接反例，FO 應把這個事實帶回風險說明；若原批准依賴「兩筆仍會被報出」，風險是否接受仍由 Captain 判斷。

獨立以候選 `walk`、`Context`、`judge(..., "L4", LAWS["L4"])` 重跑能力表七筆的各自第一父提交範圍，得到：

- dev2：`a113aa3e9a3dad8f16e4a6d8ba638acfe3b3dd96`、`7326e2a1162b68bf968e3319cd527c965255ce12` 各一個 L4 事件；`bf8c73be99c4f0a569a15ce1ee7426578ae7ce85` 為零。
- qnow：`3a384063e44fd1e8ce128c4a4eea968026cd542a`、`4ad69292227ae4a2dff0540f0936e18a278cb2cf`、`4993b5b603aead90bb2738873ba5b6c6c67d10e3` 各一個 L4 事件。
- relay：`06cadae7681fe3425bb47f66efa3d17e8de837ea` 為零。

因此 **指定七筆中五筆** 有獨立證據；數字是提交事件數，不是診斷行數，bite（原始故障提交）同一個事件有 reuse 與 unmarked 兩行。

套用此修訂只需要狀態文件作業：依 `docs/adr/0005-a-captain-amendment-is-recorded-by-fo-and-moved-by-the-next-worker.md` 的 `writes any replacement under a fresh id`，由實作工人移動原 AC-4 全文至修訂的 `Superseded text:`，以新編號寫替代條件，保留其他證據及反證要求，補上兩筆的真實結果。不要倒改原核准設計或原始 Captain 引文；以追加說明保存取捨。`docs/adr/0057-rewritten-criteria-are-compared-with-the-captains-words.md` 亦說檢查 `does not judge semantic fidelity`，所以格式檢查通過不能替代本次語義判斷。

相對 base，候選只改 `kc-dev-flow-2/scripts/design_surfaces.py`、`kc-dev-flow-2/scripts/laws_check.py`、`kc-dev-flow-2/scripts/test_laws_check.py`、`kc-dev-flow-2/references/sd/laws.md`。本次七改五不需要新增產品差異。原本按推送回報、不阻擋提交的界線不變；AC-7 的發布後採用版本更新及實際託管執行仍未完成，沒有被修訂免除。沒有新增 CI（自動檢查）工作或觸發條件；每個 PR（合併請求）及每次狀態推送的成本未量測。

## 3. 證據沒有解決什麼？

**不能保證修好格式就補報原先漏掉的缺陷。** Amendment 1 的 Asked 說 `要等格式修好才會被新規則看到`。候選不只是檢查當前檔案：前一版本有結構問題也會跳過；之後 `previous = set(move_defects(before))` 與 `if defect not in previous` 又排除持續存在的缺陷。這符合 `docs/adr/0017-history-laws-judge-only-the-events-a-push-adds.md` 的 `each run judges only the events the commits of the push add`，卻不能保證對漏掉的舊缺陷補報。

本次做了只在記憶體內的對照：取 relay 原始事件檔，把唯一出錯的 `### Amendment 2 — 2026-10-13, chat at the ideation gate` 改為四個井字，保留 amendment 3 與其未標記狀態。候選解析器的結構問題清空，`move_defects` 回傳 `[("unmarked", 3)]`；以原檔為前一版本執行候選 L4，仍得到零事件。再以前述文字為前一版本、只加無關開頭文字，仍為零事件。沒有寫檔、改歷史或改候選程式；這只證明 L4 的跳過與差分行為，**不是建議的實際修法，也不證明該修法符合 L3**。

其他界線：

- 沒有重新跑三個儲存庫的完整歷史，所以本報告證明的是表內七筆的結果；不替代「整個歷史只有這五筆、更新歷史沒有額外事件」的替代驗收條件證據。實作報告的完整重跑數量仍屬其作者的證據。
- 沒有改候選或執行完整測試、mutation（故意破壞程式的反證）、發布、採用版本更新或託管工作；不主張整個任務驗收通過。
- 沒有證明實際故障當時的託管版本曾報出兩筆。此處是固定候選對歷史提交的重跑，不能回推當年的保護。
- 沒有核實 Captain 當時對「留給既有格式規則」的理解。紀錄支持改五筆；沒有支持「兩筆都有同等即時警訊」。
- 既有後續派工有可能觸發 L2 結構檢查，但沒有新增派工就不會觸發；不能把未來可能的檢查算成這兩次寫入已被檢查。

最小可信下一步是 FO 採用本報告的精確覆蓋說明，再決定是否需把新增的風險事實交 Captain 判斷；工人僅在既有核准範圍內套用五筆替代條件。若要求兩筆都當次回報或修格式後補報，這會改變程式機制及證據義務，應先明確決定再派工。本報告沒有替 FO 作該決定。
