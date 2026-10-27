---
title: An engineering-reviewer claim that something holds or does not crash shows its probe reached the code under test
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「同意開 1 到 5，第 6 項併進「GPT 夥伴」提案」 (chat, 2026-10-27), answering FO's list of package-issue candidates (items 2 to 5 relayed by the relay FO, Paseo 1671c3a9, from its pair-once and room-specs-follow-web-part-select observer reports; item 1 relayed by the kc-ops-inbox FO, Paseo 46c2ebdf).
- Bite: kc-ops-inbox task ops-metric-event-protocol (PR #727 at 36973c77, 2026-10-27, relayed by its FO): engineering-reviewer (opus) reported no crash and no P1; Codex gpt-6-astra found 2 P1 and Gemini 4 Argon 3 P1 on the same brief and head. The FO reproduced why: the reviewer's top-level 8000-deep array returned not-json-object before serialization ran, and its object probe (3000 deep) was below the stack limit; the same depth inside {"x": …} throws RangeError. `skills/engineering-reviewer/SKILL.md` (0.31.0) asks for no evidence that a probe reached its target. The FO's proposal: a reach check for every negative claim, and a hostile-input class list (nesting past the stack limit inside a valid envelope, wrong JS types, missing arguments that fail open through NaN or undefined). Their files: kc-ops-inbox .spacedock-state/ops-metric-event-protocol/code-review-*-2026-10-27.md.
- Upstream first: `skills/engineering-reviewer/SKILL.md`, `agents/engineering-reviewer.md`, kernel and validation principles on negative evidence.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
