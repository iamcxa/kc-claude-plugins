---
title: FO's Captain-facing gate presentation asks one thing, leads with the conclusion, defines its terms and quotes the bound acceptance sentence
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「都開」 (chat, 2026-10-23), answering FO's 「要不要把這三項各開成一張待辦任務？我建議開。」, after his 「另外看一下我的 user scrope claude.md 有沒有特別適合 dev2 的部分可以移植的？」; FO read his global ~/.claude/CLAUDE.md and grepped the kc-dev-flow-2 0.28.0 package for each theme (2026-10-23).
- Port: from his global instructions, "One decision", "No undefined nouns", "Conclusion first" and "Open in plain language", plus a dev2 rule his file does not hold: the chat presentation carries the bound gate question's "approving accepts …" sentence verbatim.
- Bite: observers on four dev2 tasks (codex-reader-reads-receipt-marker, agent-reads-governing-adr, merge-ask-holds-missing-clauses, codex-reader-counts-code-review-only) recorded that the chat question the Captain answered did not carry the bound acceptance sentence; the Captain asked what an FO term meant several times in the 2026-10-21 to 10-23 sittings. The package holds none of these rules (grep of the 0.28.0 markdown for "conclusion first", "one decision", "eight words", "plain language": 0 files).
- Upstream first: Spacedock present-gate skill (render the gate once, name entity, stage, briefing, one recommendation and the decision); kc-dev-flow-2 README Gate content and FO steps.
- Non-goals: his personal language and status-block preferences.

## FO alignment

Alignment: needed at ideation; where the rules live (README, a skill, or the Spacedock presenter) is his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
