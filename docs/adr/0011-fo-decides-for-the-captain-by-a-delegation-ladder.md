# 0011. FO decides for the Captain only by a four-level delegation ladder

Date: 2026-10-12

## Status

Accepted

## Context

The Captain wants dev2 to learn his decision trajectory and, at high confidence, decide
on his behalf: 「讓 FO 可以依據 ADR 以及自我學習與改進的結果，可以代替我決策」 (chat,
2026-10-12). ADR 0009 covers the same direction for package self-improvement only, and
left open how work is triggered when a task closes.

Two facts measured on 2026-10-12 over one adopter's state branch (65 archived task files)
bear on it. `python3 kc-dev-flow-2/scripts/decision_ledger.py` read 168 gate resolutions and
15 withdrawals, matching `grep -c` of `decision:`, `resolution:` and `withdrawal:` lines;
9 resolutions were recorded by `agent:first-officer` under a quoted grant. No gate record
carries an `Override:` line, so no area yet shows when the Captain chose against FO.

## Decision

**Words:** 「可以，就照此方向。」 — Captain, chat, 2026-10-12

**Asked:** 「**要你決定：** 照這個方向做下一批嗎？內容是 learn 擴充（歸檔時觸發）加上決策帳本，再加 L2「依先例代決」。L3 等資料夠了再說。我建議做，並把整條授權階梯另外寫成一份 ADR，和 ADR 0009 互相引用。」

**Options considered:**
- a four-level ladder, built up from L2, with L3 waiting for ledger data (chosen)
- not in this batch, the other answer to the yes-or-no question asked

**Recommended:** the four-level ladder

FO decides for the Captain only at one of four levels:

- **L0:** FO recommends; the Captain decides. The default.
- **L1:** a gate question that says approval accepts FO's recommendation (workflow
  README, `## FO steps: review findings`).
- **L2, decide by precedent:** a decision an accepted ADR already settles is applied by
  FO and stated in the gate summary as `Precedent: ADR <number> — 「<Words line>」`; the
  Captain may reopen it.
- **L3, decide by record:** not built. A class of decisions moves to L3 only by a Captain
  grant recorded as its own ADR, on ledger evidence that his rulings in that area agreed
  with FO and were not later amended. Any reversal returns the area to L0.

Authority, gate approval, merge, outward-facing actions, irreversible changes and money
are never delegated at any level. A delegated decision is recorded as FO's decision with
its basis, never as the Captain's words.

The decision ledger is derived, not stored: `decision_ledger.py` reads the gate records
SD already writes (who, when, decision, reason, grant, briefing question) plus
`Override:` lines and `## Captain amendments`. The learn extension runs `learn` and the
observer when FO archives a task.

## Consequences

This answers ADR 0009's open trigger at task close for adopters that list the learn
extension. L3 needs `Override:` lines to accumulate before any area shows a record; the
ledger's `amended_after` counts amendments dated on or after a ruling, which approximates
a later reversal and can over-count. Reopen if an L2 precedent is reopened by the Captain
twice in one area, or if the ledger cannot separate areas well enough to support an L3
grant.
