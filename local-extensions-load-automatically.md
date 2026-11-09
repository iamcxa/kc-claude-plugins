---
title: A workflow loads a repository-local extension the way it loads a package extension
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「要支援自動載入 local extension，也應該要支援載入 local agent role/profile」 (chat with the Chief Engineer session colombo-9e, 2026-11-09), relayed by Paseo c3511be0 (relayed, not a ruling here; the backlog gate confirms it).
- Bite (relayed from the Chief Engineer session, which read the kc-paseo-plugins FO's state checkout `local-ext/doc-site.md` and the archived project-env tasks' `### Local extension doc-site` records, not re-run here): the doc-site local extension ran 5 rounds; rounds 2, 4 and 5 caught a docs sentence that no longer matched the screen; in every round FO copied its instruction lines into the dispatch checklists by hand, because the package loads extensions only from `<package>/extensions/<name>/`.
- Upstream first (relayed): Spacedock 0.27.3 repo-local `_mods/` give FO hooks at startup, idle and merge but add no instruction to a stage worker's dispatch; the gap is the `## Extensions` rule in `kc-dev-flow-2/references/sd/workflow.md` and the dispatch builder.
- Related: iamcxa/kc-claude-plugins issue #808, where FO answered on 2026-11-09 that project-defined roles and project-local extensions are not supported in kc-dev-flow-2; this task may change that answer.
- Non-goals: the layer above several FOs (Spacedock Bridge); changing Spacedock's _mods.

## Budget
- One package PR, or a split the ideation names; workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- A repository-local extension in the EXTENSION.md shape, listed under `extensions:`, has its instruction added to the matching stage dispatch by the package's dispatch script with no FO copy, with a falsifier.

## FO alignment

Alignment: needed at ideation; where a local definition lives and how it is found are his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
