---
title: A batch reaches each gate together and the Captain answers it in one sitting, after an optional reviewer pass over the whole batch
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:batch-reaches-each-gate-together:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:batch-reaches-each-gate-together-backlog-1
              briefing:
                id: briefing:batch-reaches-each-gate-together:backlog:attempt-1:revision-1
                digest: sha256:75fa236d431a3f1bf2f93ffe8e25cd1cc12081a41231caba7741f35ae4df7e53
                room-ref: ./batch-reaches-each-gate-together/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:batch-reaches-each-gate-together:backlog:1
                briefing: briefing:batch-reaches-each-gate-together:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-28T05:39:03.680242Z"
                decision: approve
                reason: The Captain 「准」 (chat, 2026-10-28), answering FO's joint batch-9 backlog presentation of five gates whose ask was 「決定：五張全准進入設計階段；要拿掉或換掉哪張，直接說。」; accepts FO's recommendation to enter ideation on the pilot profile.
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain (chat, 2026-10-27): 「全准。目前這是批次決定的 dogfood，我想繼續改善批次決策，批次實作，批次審核，注意重點是應該一次只做同一個release slice 或是找同主題，然後直到這一批全部都到達另外一個 gate，才批次審，中間有某個完成了不必急著在對話中問決策，甚至讓 CR or ER 在一批完成後立即跑一輪 review 再給我建議或是問我最終問題。我可以接受等待時間略長，但是每次應該集中精神好好討論回答，不要讓對話切割得太零碎。這裡也有一個關於 SD Review 的問題，理想上應該要讓 review 可以乘載每次的 design preview，一次可以多個 html，等於你看 web FO 這次給 A1,A2 兩組設計應該要可以放到同一份簡報中，我在簡報內回覆就好，這樣 FO 跟我的對話就可以更節制，因為重點擺在 gate 簡報中了，你可以訪談一下 relay + web FO，然後把重點對 relay FO or web FO 提需求，但是把這個精神納入批次決策改進中」.
- Bite: batch 7 (2026-10-26/27) put four separate merge asks to the Captain (#728, #729, #732, #730) as each PR finished, plus mid-batch questions; batch sittings so far exist only as FO practice (archived task fo-batch-sittings, interim rules from 2026-10-17).
- Outcome he named: a batch is one release slice or one theme; FO holds every task until the whole batch reaches the next gate, then presents the batch in one sitting; it does not ask when one task finishes early; chief-engineer or engineering-reviewer may review the whole batch first and give the recommendation or the final question; the gate briefing, not chat, carries the substance, including several design previews in one Spacedock Review briefing that he answers in place.
- Added 2026-10-27: Review-deck interview (fo-interviews-extension/review-deck-2026-10-27.md): a briefing renders Markdown parts only (no images or HTML, sandboxed frame) and holds one decision per briefing; the requirement (static image parts, a decision per part, several tasks in one briefing) went to the web and relay FOs at the Captain's direction, for their own backlogs. This task's dev2 side reads the per-part answers once those exist.
- Added 2026-10-27: the Captain 「等等，我在想是否不用 CE/ER 而是叫產品總監（設計總監）看整批？」, then 「可，按你建議」 to FO's recommendation: the batch reviewer follows the batch's kind (chief-engineer for a theme batch of package or process changes with no screen; design director for a release slice with screens), engineering-reviewer only for a contested hard-to-reverse claim; whether to add a product-director role, and what it reviews, is decided in this task's ideation. Batch 8 uses chief-engineer.
- Added 2026-10-27: from batch 8's chief-engineer review: FO put its own four suspicions into the reviewer's brief and the reviewer confirmed all four, so the review may have been anchored; a batch reviewer gets the task files, not FO's conclusions. The batch reviewer runs on a model of a different family from the batch's workers (batch 8: workers Codex gpt-6-astra, reviewer Claude opus).
- Upstream first: archived fo-batch-sittings (and its `decision_ledger.py --sittings`), Spacedock Review and `gate prepare` (one briefing per task today), the relay and web FOs' answers on carrying several HTML previews (interview 2026-10-27, to be recorded under fo-interviews-extension).

## Non-goals

- The Spacedock Review deck with several previews (in the web and relay FOs' backlogs); a product-director role unless ideation shows the need.

## Budget

- One package PR to the workflow rules and, if needed, `scripts/decision_ledger.py`; no change to Spacedock gate commands.

## Stop condition

- Batch 7's four separate merge asks replay as one sitting under the new rule. Return to the Captain if holding a batch at a gate needs a Spacedock change.

## FO alignment

Alignment: needed before ideation; how a batch is held at a gate and what the batch review owes are the Captain's.
Result: aligned at backlog: the Captain 「准」 (chat, 2026-10-28) to FO's batch-9 backlog sitting, which asked 「決定：五張全准進入設計階段；要拿掉或換掉哪張，直接說。」, approved the outcome and bounds in this file. His rules for a batch are his words of 2026-10-27 quoted in Scope. How a batch is held at a gate and what the batch review owes stay his: ideation returns them as decisions at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Stage Report: ideation

- FAILED: A design for holding a batch at each gate and presenting it in one sitting (rules in the workflow README and, if needed, scripts/decision_ledger.py), with the batch reviewer chosen by the batch's kind and given the task files rather than FO's conclusions; batch 7's four separate merge asks replayed as one sitting; whether a product-director role is needed decided from evidence
  Hold before design: FO alignment says "Alignment: needed before ideation" but has no Result line; selected pilot ideation principles and the dispatched stage definition require FO to record that result before design/dispatch.
- SKIPPED: A `### Batch overlap` section naming each file the design would change and each other batch task (reused-worker-dispatch-leaves-a-record, paseo-codex-dispatch-practice, captain-ruling-sources-checked, batch-reaches-each-gate-together, fo-interviews-extension) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  No design or file-change proposal authored while the required alignment result is missing; overlap research remains owed on redispatch.
- SKIPPED: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  The current root learning rule was read; no candidate exists to measure, so no before/after count or reduction is claimed.
- SKIPPED: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  No criteria authored before alignment; FO must first record the alignment result or route the unresolved alignment to the Captain.

### Summary

Held pilot ideation before design because the task's FO alignment requires alignment but lacks the mandatory Result line; the recorded backlog approval was not treated as a substitute. Read the operating contract, selected ideation route and current task; git fetch origin succeeded, pinning origin/main to e57feb6eec956b74a1d4b29f26f1d0a7d1693785 with package version 0.32.1, and inspected Spacedock 0.27.3 gate lifecycle/presentation docs, but the full upstream/package/adopter chain, batch replay and design checks remain unperformed. FO next records the actual alignment result and redispatches; this report changes only this entity's body and grants no gate or implementation authority.
