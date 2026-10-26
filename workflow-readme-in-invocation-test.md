---
title: The documented-invocation test covers the workflow README template
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「可以，開 A-D」 (chat, 2026-10-26), answering 「需要你決定：下面 5 個套件缺口候選，要開哪幾張待辦？我建議開 A 到 D，E 先不開。」 after the learn backfill of 11 archived tasks (Captain 「補跑」, 2026-10-26).
- Bite: Codex round 2 P2 on iamcxa/kc-claude-plugins#724: `references/sd/workflow.md` told FO to run `<package>/scripts/delivery_gate.py` directly; the script is mode 100644, so the command exited 126 (validation, 2026-10-26). learn job c0eba667 found `test_observer_check.py` `DocumentedInvocationTest` enforces `python3 <package>/scripts/...` for other files but not workflow.md. One case.
- Upstream first: `scripts/test_observer_check.py` `DocumentedInvocationTest`, `references/sd/workflow.md`.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
