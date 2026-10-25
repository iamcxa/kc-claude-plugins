---
title: read-adr lists the ADR folder its caller names, and none means no records
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: FO, 2026-10-25. Codex review 5628338608 on iamcxa/kc-claude-plugins#713 head 037d2cf6 (2026-10-23T12:41:08Z), one P2, was not read before the merge: the merge ask named Codex as not read because `codex_review.py` reported `running` (a stuck security-review eyes reaction; see codex-review-hang-detected). The Captain approved the merge on that statement.
- Finding (P2, `kc-dev-flow-2/skills/read-adr/SKILL.md`, a byte copy of `kc-adr/skills/read-adr/SKILL.md`): when the caller passes an ADR folder other than `docs/adr`, or `ADR folder: none` (the design director does), the no-citation branch still lists `docs/adr/`, so it can miss the supplied rulings or apply rulings the caller declared absent.
- Shipped: the text is in kc-dev-flow-2 0.30.0 and kc-adr 0.2.0.
- Fix lives in kc-adr (the source); `scripts/kc-adr-copy-sync.sh sync` carries it to the dev2 copy in the same PR, per the D4 ruling of kc-adr-tools-with-dev2-copy.
- Non-goals: other read-adr wording.

## FO alignment

Alignment: not needed: a reviewer finding in shipped text, fixed in its source.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
