---
title: A batch reaches each gate together and the Captain answers it in one sitting, after an optional reviewer pass over the whole batch
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain (chat, 2026-10-27): 「全准。目前這是批次決定的 dogfood，我想繼續改善批次決策，批次實作，批次審核，注意重點是應該一次只做同一個release slice 或是找同主題，然後直到這一批全部都到達另外一個 gate，才批次審，中間有某個完成了不必急著在對話中問決策，甚至讓 CR or ER 在一批完成後立即跑一輪 review 再給我建議或是問我最終問題。我可以接受等待時間略長，但是每次應該集中精神好好討論回答，不要讓對話切割得太零碎。這裡也有一個關於 SD Review 的問題，理想上應該要讓 review 可以乘載每次的 design preview，一次可以多個 html，等於你看 web FO 這次給 A1,A2 兩組設計應該要可以放到同一份簡報中，我在簡報內回覆就好，這樣 FO 跟我的對話就可以更節制，因為重點擺在 gate 簡報中了，你可以訪談一下 relay + web FO，然後把重點對 relay FO or web FO 提需求，但是把這個精神納入批次決策改進中」.
- Bite: batch 7 (2026-10-26/27) put four separate merge asks to the Captain (#728, #729, #732, #730) as each PR finished, plus mid-batch questions; batch sittings so far exist only as FO practice (archived task fo-batch-sittings, interim rules from 2026-10-17).
- Outcome he named: a batch is one release slice or one theme; FO holds every task until the whole batch reaches the next gate, then presents the batch in one sitting; it does not ask when one task finishes early; chief-engineer or engineering-reviewer may review the whole batch first and give the recommendation or the final question; the gate briefing, not chat, carries the substance, including several design previews in one Spacedock Review briefing that he answers in place.
- Added 2026-10-27: Review-deck interview (fo-interviews-extension/review-deck-2026-10-27.md): a briefing renders Markdown parts only (no images or HTML, sandboxed frame) and holds one decision per briefing; the requirement (static image parts, a decision per part, several tasks in one briefing) went to the web and relay FOs at the Captain's direction, for their own backlogs. This task's dev2 side reads the per-part answers once those exist.
- Upstream first: archived fo-batch-sittings (and its `decision_ledger.py --sittings`), Spacedock Review and `gate prepare` (one briefing per task today), the relay and web FOs' answers on carrying several HTML previews (interview 2026-10-27, to be recorded under fo-interviews-extension).

## FO alignment

Alignment: needed before ideation; how a batch is held at a gate and what the batch review owes are the Captain's.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
