---
title: FO writes one DOING line before each outward write, in the same form as the Captain's global instructions so the line is never doubled
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「DOING 開頭的說明我想加進去，但要注意我應該不會看到兩次吧？」 (chat, 2026-10-23), on FO's list of global-instruction items not ported to dev2.
- Port: his global instruction "Remote state change: `DOING: [action] ON: [target] FOR: [purpose]` before a push, PR creation or update, deployment, or other external write", in the identical form, so an FO that also loads his global instructions emits one line, not two near-duplicates.
- Shape to design: which FO actions it covers (push, PR create, ready, comment, branch update, merge, release), whether worker lines count (workers report to FO, not the Captain), and whether Spacedock state commits are excluded (FO makes many per turn).
- Bite: none recorded in dev2; adopters' FOs that do not load his global instructions write no such line today.
- Upstream first: his global ~/.claude/CLAUDE.md "Pre-action narration"; kc-dev-flow-2 Delivery authority.
- Non-goals: the commit-line form for every local commit.

## FO alignment

Alignment: needed at ideation; the covered actions are his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
