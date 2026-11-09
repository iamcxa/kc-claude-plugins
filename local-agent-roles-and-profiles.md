---
title: A workflow can declare a repository-local advisory role or agent profile that FO calls and the records recognize
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「要支援自動載入 local extension，也應該要支援載入 local agent role/profile」 (chat with the Chief Engineer session colombo-9e, 2026-11-09), relayed by Paseo c3511be0 (relayed, not a ruling here; the backlog gate confirms it).
- Captain's earlier direction (chat with this FO, 2026-11-09): 「我們這裡可以考慮的是，針對專案加入 local or project based 的角色擴充，例如，sd repos 加入 cl 角色模擬，例如蒸餾 slack, firefiles 對話紀錄後蒸餾出 cl user 讓它提供建議」.
- Upstream first (relayed): Spacedock's standing teammates (a long-lived specialist declared in `_mods/`) may already cover a local advisory role; check them before building. Today's profile routes in the stage skills hold on any profile outside poc, pilot and prod.
- Privacy: a role distilled from Slack or Fireflies conversations uses real people's words; the design names what is stored, where, and who sees it.
- Related: iamcxa/kc-claude-plugins issue #808, where FO answered on 2026-11-09 that project-defined roles and project-local extensions are not supported in kc-dev-flow-2; this task may change that answer.
- Non-goals: the layer above several FOs (Spacedock Bridge); changing Spacedock's _mods.

## Budget
- One package PR, or a split the ideation names; workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- A repository-local role or profile is declared once, is callable by FO, and is recognized by role_triggers.py and the observer, or the design shows a standing teammate already does this and says what is missing, with a falsifier.

## FO alignment

Alignment: needed at ideation; where a local definition lives and how it is found are his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
