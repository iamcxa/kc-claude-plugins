---
title: AGENTS.md holds this repository's agent instructions and CLAUDE.md imports it, so every host reads one copy
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain, batch-5 sitting 2026-10-21: 「可以，建立agent.md，這個應該統一成此檔案而不是Claude.md，合理嗎？」 then 「可以」 to FO's two-step proposal: agent-reads-governing-adr creates `AGENTS.md` with the ADR pointer and adds `@AGENTS.md` to `CLAUDE.md`; this task moves the rest of `CLAUDE.md` into `AGENTS.md` and leaves `CLAUDE.md` as the import line.
- First step: verify from each host's own documentation whether Claude Code reads `AGENTS.md` by itself, how `@` imports resolve in a project `CLAUDE.md`, and what Codex reads; inventory the plugin-level `CLAUDE.md` files (`e2e-pipeline`, `kc-hyperfocus`, `kc-nightwatch`, `kc-plugin-forge`, `kc-pr-flow`) and say which move.
- Constraint: every session working in this repository reads `CLAUDE.md` (release-please rules, pre-merge gates, commit conventions), so a session started during the move must still see every rule; prove it on both hosts after the change.
- Upstream first: the hosts' documentation; how sibling adopters (subspace-relay, subspace-web, qnow) split `AGENTS.md` and `CLAUDE.md` today, read-only, as facts and not as the contract.
- Non-goals: rewording any rule; adopters' instruction files.

## FO alignment

Alignment: not needed before ideation; the Captain chose the direction.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
