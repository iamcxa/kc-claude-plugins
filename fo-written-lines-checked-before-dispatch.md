---
title: Three FO-written lines are checked before dispatch and gate, not found by the observer after merge
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: handed over by the kc-adr FO (Paseo session 1bcf070c), 2026-10-25, relaying the Captain's 「開，但是直接轉交給dev2 fo不要開issue」 answering 「要不要開這三個 issue？」 (relayed; no GitHub issues). Filed here as one task; ideation may split it.
- Gap 1, amendment entries carry FO words. README `## Captain amendments`: "FO adds no words of its own"; `Asked:` is verbatim. Seen: `_archive/kc-adr-format-source/observer.md` (FO parenthetical on `Captain:`, half a question with JSON `\"` escapes on `Asked:`, a `Design:` naming a Scope non-goal); `_archive/release-acceptance/observer.md` (FO prose on `Asked:` of Amendments 1 to 3); `_archive/release-walk-picky-reviewers-and-director/observer.md` (Amendment 1 `Design:`). The existing amendment-form check (`design_surfaces.py check`) reads moved criteria and `Supersedes:`, not these lines.
- Gap 2, `Alignment: needed` dispatched with no `Result:` line. README `## Stages` (ideation): "FO records the alignment result as a `Result:` line before dispatching the worker." Seen: `_archive/adr-protected-path-guard/observer.md`, and this batch's `release-review-staleness-held-at-dispatch`, `release-acceptance`, `kc-adr-tools-with-dev2-copy` and `release-walk-picky-reviewers-and-director` observer reports. `dispatch build --stamp` does not refuse; `dispatch_records.py --names` does not read it.
- Gap 3, the delivery gate question lacks "unless he says he merges or holds". README `## Delivery authority`. Seen: `_archive/adr-protected-path-guard/observer.md`. `delivery_gate.py check` requires only the `Sufficiency:` and `Necessity:` clauses, second-reviewer outcomes and bracketed declines (2026-10-25, 0.29.0 `CONFIRMATIONS`); `gate prepare` reads no question text.
- Bite: each was caught only by the observer after merge; about 25 FO record errors this batch (FO count, 2026-10-23 to 2026-10-25); record reliability is the main risk for the autopilot path.
- Upstream first: dev2 scripts `design_surfaces.py` (amendment form, FO alignment), `delivery_gate.py`, `dispatch_records.py`, `role_triggers.py`; Spacedock `dispatch build` and `gate prepare` take no FO-text precondition (0.27.x).
- Non-goals: any other FO-write rule; changing what the README requires.

## FO alignment

Alignment: needed before ideation: which checks run where (dispatch, gate, observer) is a design choice the Captain may want to see.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
