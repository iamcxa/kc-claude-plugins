---
title: observer_check prints the learn steps only where the workflow README lists learn
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: intake from the subspace-web/v0 dev2 FO (Paseo agent 295b873d, 2026-10-21), relaying the Captain's 「開給 dev2 ，可以先送給這個 fo  2e87a82e-a8a9-4e41-973a-7483aa46e39d」 (relayed, not a ruling in this session).
- Bite: subspace-v0's dev2 README has no `extensions:` and never mentions learn; `learning.py notices --all` there is empty. After archiving task first-publish-reads-right, `observer_check.py` still told FO to run learn and to send learn's notice.
- Verified 2026-10-21 in kc-dev-flow-2 0.27.0 `scripts/observer_check.py`: the `learn` step list ("next: run kc-dev-flow-2:learn for {slug}.", "next: send learn's notice, then the observer report unedited…") is appended whenever the task is archived, with no read of the README's `extensions:`; `extensions/learn/EXTENSION.md` says a repository uses learn "by listing `learn` under `extensions:`".
- Shape proposed by the relaying FO (its wording, not the Captain's): when the README does not list `learn`, print no learn steps, or say learn is not enabled here.
- Related: adoption-asks-which-extensions (adoption never asks which extensions to enable).
- Upstream first: `observer_check.py` and its tests; how other scripts already read `extensions:` (dispatch_records.py).

## FO alignment

Alignment: not needed before ideation.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
