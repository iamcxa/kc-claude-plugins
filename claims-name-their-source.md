---
title: A number or factual claim in a gate summary, PR body or Captain message names the command and date that produced it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「都開」 (chat, 2026-10-23), answering FO's 「要不要把這三項各開成一張待辦任務？我建議開。」, after his 「另外看一下我的 user scrope claude.md 有沒有特別適合 dev2 的部分可以移植的？」; FO read his global ~/.claude/CLAUDE.md and grepped the kc-dev-flow-2 0.28.0 package for each theme (2026-10-23).
- Port: from his global instructions, "Give a number only if you measured it", "Re-verify any factual claim against the current implementation before it goes into a PR, issue, review, or third-party message", and the artifact rule "Point at the source".
- Bite: 2026-10-22, FO relayed a worker's claim that design_surfaces.py prints Preview paths to the Captain; the checker prints only the review report path (FO corrected it when he asked). The kc-adr FO reported a gate summary and PR body that said two cells were unmeasured where it was three (its read-adr-reporting-rule-followup task). The package has no such rule (grep of 0.28.0 markdown for "measured it", "enforcement point": 0 files).
- Upstream first: kc-dev-flow-2 delivery_gate.py (checks clause presence, not claim sources); the repository CLAUDE.md rule that an absolute names its enforcement point.
- Non-goals: checking claims in code comments.

## FO alignment

Alignment: needed at ideation; whether this is a written rule or a checked one is his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
