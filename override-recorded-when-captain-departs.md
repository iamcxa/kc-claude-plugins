---
title: A gate resolution records an Override when the Captain's ruling departs from FO's recommendation, including a revise and a revised recommendation
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: a package finding relayed by the brainprint evaluation session (Paseo agent b1a74093, 2026-10-23), with the relayed instruction to hand it to the dev2 FO and open no GitHub issue; relayed, not a ruling in this session.
- Bite (peer's measurement, 2026-10-23): `decision_ledger.py --summary` over one adopter's dev2 state (749dc1e3d) gives 239 rulings, 0 overrides, 40 amended_after; of 74 Captain resolutions after the Override rule landed (fcc5a417, 2026-10-09), at least four went against FO's recommendation with no Override line. In this workflow, observers recorded the same class (Override placed outside the resolution reason, or absent) on several batch-5 tasks. ADR 0011's L3 (FO decides a class by its record) needs this record and has none.
- Two causes named: a revise that rejects a design and states new requirements has no option pair, so the Override format does not fit and FO writes nothing; when FO revises its recommendation after pushback and the Captain approves the new one, the ledger records agreement. Nothing checks the rule when a gate is recorded; the observer checks it after archive.
- Directions named by the peer, not decided: (a) widen the Override rule to revise rulings and revised recommendations; (b) a scorer over ledger rows that extracts recommended and chosen options and reports agreement against chance (idea from grahac/brainprint pipeline/decisions.py and pipeline/score.py; brainprint itself judged unsuitable).
- Upstream first: Spacedock gate record (reason text); kc-dev-flow-2 decision_ledger.py, workflow.md review-finding disposition; ADR 0011.
- Non-goals: mining session history.
- Folded 2026-10-25 into fo-written-lines-checked-before-dispatch (the Captain 「可以」 (chat, 2026-10-25), answering 「需要你決定：這份第 6 批的清單可以嗎？」 about FO's batch-6 list); not run on its own while that task is live.
- Added 2026-10-26: partly covered by iamcxa/kc-claude-plugins#724 (merged 1a6149f5): only an `Override:` line placed outside a gate resolution reason is now noted. Not covered: an Override for a revise or hold that departs from FO's recommendation (README widening) and a scorer over the decision ledger; fo-written-lines-checked-before-dispatch D4 chose its option A and excluded both. Stays open for that remainder; the Captain allowed closing the folded tasks only 「如果都涵蓋了」 (chat, 2026-10-26).

## FO alignment

Alignment: needed at ideation; whether to widen the rule, check it at record time, or score the ledger is his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
