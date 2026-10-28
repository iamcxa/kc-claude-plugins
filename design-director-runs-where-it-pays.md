---
title: The design director runs where it pays, its decline round costs less, and it sees every screen the change touches
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain (chat, 2026-10-28): 「現在有沒有需要手動訪談其他fo？特別是哪時候派設計總監，哪時候 FO 自己看可以兼顧嚴謹跟效率？或是怎樣可以加快設計總監腳步，例如減少 reasoning 程度，或是限制時間？」. Filed by FO from interview round 3; no ruling on the outcome yet.
- Evidence: fo-interviews-extension/round-3-design-director.md (160 recorded runs; web, project-env and relay FO answers). Runs take 1 to 3 minutes on the declared sonnet tier; the cost sits in the decline round's bookkeeping and in cycles started by false or late findings; all three FOs name skip cases and always-run cases; misses came from missing inputs (CLI screens not captured) and pixel faults found only by measuring.
- Today every task with `Surfaces: ui` runs passes 1a and 2a, plus 1b and 2b on any decline, with no skip path (`skills/ideation/design-review.md`, `skills/validation/principles.md`, 0.32.1).
- Upstream first: `skills/design-director/SKILL.md`, `skills/design-director/review-brief.md`, `scripts/design_surfaces.py` (single `preview:` path, decline listing), the design-director agent file (model sonnet, reasoning high).

## Non-goals

- Lowering the director's model or reasoning below its declared tier, or a time limit on a run (no FO reported the run as the cost).
- Changing who holds a gate; the director still advises only.

## Budget

- One package PR across the design-review and validation rules and `scripts/design_surfaces.py`; no new script.

## Stop condition

- Recorded cases replay as intended: web sidebar-head-stays-level-after-send validation and project-env-vault-change-repoints-refs built review would skip; web-serves-formats-list validation, project-env-docs-site ideation cycle 2 and rr-pairs-once validation-1 would still run. Return to the Captain on the disputed skip reason (built screen matches the approved preview).

## FO alignment

Alignment: needed before ideation; which tasks may skip the director is the Captain's.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
