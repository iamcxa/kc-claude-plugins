---
title: kc-dev-flow v1 is deprecated on a set date, its consumers moved to kc-dev-flow-2, so no host resolves a v1 skill in place of a v2 one
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「這是個新議題，找一個時間應該棄用 dev1，避免衝突」 (chat, 2026-10-23), after FO's report of a read-only investigation he approved through the Comms Officer.
- Bite (investigation 2026-10-23): under OMP (Oh My Pi) with Claude plugins enabled, skill names lose their plugin prefix and the first installed copy wins, so `chief-engineer` resolves to kc-dev-flow 4.6.0 instead of kc-dev-flow-2 (installed_plugins.json order: kc-dev-flow index 73, kc-dev-flow-2 index 79). It is the only v1/v2 name collision; `learn` collides with ~/.claude/skills/learn, not with v1.
- Consumers of v1 found (read-only scan of ~/.claude, /Users/kent/conductor and /Users/kent/Project, 2026-10-23): the Captain's global CLAUDE.md (`kc-dev-flow:science-officer`, no v2 name equal); docs/dev v1 workflows in this repository and in several adopters (qnow, subspace-relay, moneyflow, carlove-v1, subspace-web adopt-dev-flow branch, crewdock, kc-hermes-spacedock), most of which also carry docs/dev2; kc-journey-map map-from-conversation.md (`kc-dev-flow:adopt-dev-flow`); kc-pr-review's optional v1 handoff helper; kc-ship-flow (a thin wrapper over v1); CI (marketplace-parity.yml runs kc-dev-flow-contract-test.py as a required check; kc-dev-flow-release-gate.yml), release-please config and manifest, marketplace.json. Not checked: live tasks in any docs/dev workflow; cloud images and Codex local installs.
- Interim containment named by the investigation, unverified: an OMP-only disable through ~/.omp/plugins/installed_plugins.json (`enabled: false` for kc-dev-flow@kc-claude-plugins), read from OMP source; with the OMP trial FO.
- Shape to design: the deprecation date and order (consumers first: global instructions, kc-journey-map and kc-pr-review references, each adopter's docs/dev archived or migrated, kc-ship-flow; then CI, release-please and marketplace), and what stays readable for archived v1 tasks.
- Upstream first: kc-claude-plugins README (v1 "No longer maintained"), kc-dev-flow-2 README ("A kc-dev-flow project is not migrated automatically") and its adoption reference, release-please deprecation practice for a component.
- Non-goals: renaming kc-dev-flow-2 skills.

## FO alignment

Alignment: needed at ideation; the date, and whether each adopter's docs/dev is archived or migrated, are his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
