# 0043. A named batch waits for its next gate before one sitting

Date: 2026-10-28

## Status

Accepted

## Context

Batch 7 produced four separate delivery asks as tasks became ready. ADR 0028
groups gates already awaiting the Captain; its accepted task design did not wait
for stragglers. The Captain later asked to keep an agreed slice or theme together.
This changes presentation policy for named batches, while retaining ADR 0028's
separate task records, no second membership store and no sitting counter.

## Decision

**Words:** 「全准。目前這是批次決定的 dogfood，我想繼續改善批次決策，批次實作，批次審核，注意重點是應該一次只做同一個release slice 或是找同主題，然後直到這一批全部都到達另外一個 gate，才批次審，中間有某個完成了不必急著在對話中問決策，甚至讓 CR or ER 在一批完成後立即跑一輪 review 再給我建議或是問我最終問題。我可以接受等待時間略長，但是每次應該集中精神好好討論回答，不要讓對話切割得太零碎。這裡也有一個關於 SD Review 的問題，理想上應該要讓 review 可以乘載每次的 design preview，一次可以多個 html，等於你看 web FO 這次給 A1,A2 兩組設計應該要可以放到同一份簡報中，我在簡報內回覆就好，這樣 FO 跟我的對話就可以更節制，因為重點擺在 gate 簡報中了，你可以訪談一下 relay + web FO，然後把重點對 relay FO or web FO 提需求，但是把這個精神納入批次決策改進中」 — Captain, chat, 2026-10-27; 「照建議」 — Captain, ideation gate, 2026-10-28.

**Asked:** 「決定：五張全照建議（四張准並照上面刪減，一張暫緩）；如果哪張要改，直接說。」 The task's row was 「| 一批只開一次會 | 准，刪兩處 | 刪掉「設計總監看整批」，畫面批次還沒出過問題；刪掉重述 Spacedock 步驟的那一段。「整批等齊才審」寫成一份 ADR（架構決策紀錄），因為它改了之前 ADR 0028「不等落後者」的規則；這次開會本身就當作實測 |」. Amendment 1 in batch-reaches-each-gate-together records this ask and the joint workflow word raise with reused-worker-dispatch-leaves-a-record.

**Options considered:**
- Wait for all accepted members at each next gate, then present one sitting; optional existing-role process review before binding (chosen).
- Present each ready task or group currently ready gates without recovering accepted membership (replaced for named batches).
- Add a director batch pass and repeat per-task Spacedock preparation steps (cut by amendment 1).

**Recommended:** the first option, with the director pass and restating paragraph cut; use batch 9's actual sitting as the live replay.

**Protects:** none

The workflow's Batch gates section is an FO instruction, not a Spacedock
transaction. Recover membership from accepted scopes and questions. Wait for
sufficient committed evidence, continue authorized repairs and validation, and
ask a bounded exception when a blocker needs Captain authority. Membership
changes or splits require his decision. Optional advice uses committed task
files and artifacts without FO's suspicions; reviewer family differs from all
workers or the Captain decides the exception. Existing role input contracts
still apply; no director batch pass is added.

This replaces ADR 0028's as-ready grouping policy for named batches; it does not
withdraw that record's other decisions or grant batch approval/merge authority.
Each task keeps its own binding, question, resolution and existing delivery
checks. Unbatched tasks follow ordinary gates. Multi-preview Review support is
upstream work, not delivered by this rule.

## Consequences

The Captain receives fewer interruptions and a whole-batch discussion. Ready
tasks wait longer, FO reads more instructions, and optional review costs time.
The budget step records one joint raise across the stacked workflow changes.
There is no persistent membership field, timeout removal, new ledger command,
product-director role or runtime barrier. Reopen if waiting makes a batch
infeasible or live use shows a missing screen-batch review responsibility.
