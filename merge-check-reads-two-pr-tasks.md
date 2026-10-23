---
title: delivery_gate.py check reads a task that delivers through two PRs, so a reserved ADR on one PR does not hold the other
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Bite (FO, 2026-10-23): new-work-starts-from-a-story-map delivers through iamcxa/kc-claude-plugins#704 (kc-journey-map) and #705 (kc-dev-flow-2), with ADR 0029 on #705. `delivery_gate.py check <task> --pr iamcxa/kc-claude-plugins#704` printed "reserved ADR 0029 has no docs/adr/0029-*.md at PR head f0d3f442d5e6" and held the ask, so #704 cannot get a FO merge ask although its ADR lands on the sibling PR that must merge after it.
- Also seen: the task frontmatter `pr:` holds one PR, and validate.py-style records carry one `Candidate:` per PR by hand.
- Shape to design: how a task declares more than one delivery PR, and how the number guard and the merge-ask check read a reserved number satisfied by a sibling PR of the same task.
- Upstream first: Spacedock `pr:` field and merge guard; kc-dev-flow-2 `delivery_gate.py`, `number_guards.py`; kc-ship-flow.
- Non-goals: changing how a single-PR task is checked.

## FO alignment

Alignment: needed at ideation; whether a task may deliver through two PRs at all is the Captain's to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
