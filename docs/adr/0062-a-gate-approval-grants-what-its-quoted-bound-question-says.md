# 0062. A gate approval grants what its quoted bound question says

Date: 2026-11-05

## Status

Accepted

## Context

The gate-presentation-asks-one-thing-plainly design replay found that the four
validation answers for codex-reader-reads-receipt-marker,
agent-reads-governing-adr, merge-ask-holds-missing-clauses and
codex-reader-counts-code-review-only quoted a shorter chat ask than the bound
Briefing question. The acceptance and merge sentence was omitted. This is the
ideation report's historical finding; implementation replays the recorded
questions and reasons rather than claiming what the Captain saw in chat.

ADR 0023 permits a delivery question to carry the merge grant. ADR 0027 D4
rejects a word-matching check for prose quality, and ADR 0055 prints a writing
rule at the gate scripts FO already runs. This decision compares recorded
strings and prints the writing rules without judging their meaning.

## Decision

**Words:** 「准」 — Captain, chat, 2026-11-05, ideation gate attempt 1 of
gate-presentation-asks-one-thing-plainly.

**Asked:** 「決定：閘門一次問一件事這份設計進入實作嗎？核准即接受 D1（合併問句照綁定原文呈現，英文那句「核准也涵蓋…」放進中文問句裡）與 D2（待辦和構想閘門的回答對不上綁定問句時不擋，由觀察員在封存後回報）兩個建議。」

**Options considered:**
- Print one reminder at gate preparation: one decision, decision and
  recommendation first, plain words, unfamiliar terms expanded in eight words
  or fewer, and what approving accepts. Present the bound question verbatim
  and record `answering 「<that question>」` (chosen).
- D1: retain the bound merge question verbatim, including its English
  acceptance sentence inside the Chinese ask (chosen); maintain translated
  clause patterns in the gate checker (not chosen).
- D2: report backlog and ideation mismatches through the observer after archive
  without holding dispatch (chosen); add a dispatch hold without a supported
  repair route for consumed approvals (not chosen).

**Recommended:** the reminder and D1 and D2 as the approved design recommends;
the gate record says the Captain followed this recommendation.

**Protects:**
- `kc-dev-flow-2/scripts/decision_ledger.py` — `quotes_bound_question`
- `kc-dev-flow-2/scripts/delivery_gate.py` — `ASK_FORM`, `ASK_UNQUOTED` and `check`

FO shows the bound question verbatim and records the whole question after
`answering 「`. `quotes_bound_question` removes whitespace from both strings
and checks for that complete substring, including its closing bracket;
nested brackets are part of the question. Ledger JSON remains unchanged.

When the latest validation attempt has a resolution, `delivery_gate.py check`
uses the newest Captain validation approval for this comparison. A mismatch
prints and saves `ASK_UNQUOTED`: that approval grants no merge, so FO asks
separately. An unanswered attempt keeps the pre-ask `ASK`, and a later repair
resolution by FO does not replace the Captain's approval being checked. The
existing PR holds and exit codes stay in place.

## Consequences

Each passing backlog, ideation or validation preparation prints a 62-word
reminder. Startup and the adopted workflow README do not grow. The observer
checks all Captain gate answers; backlog and ideation mismatches remain
report-only. The merge ask loses one word when `ASK_UNQUOTED` replaces `ASK`.

The English acceptance sentence makes the Chinese ask longer. Recorded string
equality does not prove the Captain read that question, and FO can still
misquote him. No semantic writing check, runtime merge guard, new gate, hook,
adopter migration or expanded merge authority is introduced. Reopen if an
approval with an omitted acceptance sentence is treated as a merge grant, or
if a matching record is shown to misrepresent the question he answered.
