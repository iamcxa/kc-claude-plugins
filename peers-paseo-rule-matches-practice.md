---
title: The peers rule on new Paseo asks matches what FOs do, either by listing paseo where peers run inside Paseo or by relaxing the clause
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: interview round 004 finding (state .notes/fo-feedback/round-004.md, 2026-10-28), proposed by FO; the Captain chose theme B for batch 11 (「那就 B 可以」, chat, 2026-10-30), whose row named 「「沒列 paseo 就不能主動問」的規則跟實際做法矛盾」.
- Bite: all five interviewed FOs initiated Paseo asks with paseo unlisted and none recorded `peers not run`; qnow's Captain-directed ask had no compliant path; web did not know the clause existed; default sends steer into running peers and web received about 15 no-action finish notices on 2026-10-28.
- Upstream first: `extensions/peers/EXTENSION.md` § Paseo binding, `extensions/paseo/EXTENSION.md`, `references/sd/adoption.md`, Paseo `send_agent_prompt` defaults.

## Non-goals

- Changing Paseo; a hook that blocks sends.

## Budget

- One package PR to the peers and paseo extensions and adoption text; adopters' README listing follows through the normal sync.

## Stop condition

- Each round-004 event replays as allowed or as refused by a stated rule, with no FO left without a compliant path for a Captain-named ask.

## FO alignment

Alignment: needed before ideation; list paseo everywhere or relax the clause is the Captain's.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
