FO provenance note, 2026-10-22: built with dispatch build --stamp at state commit 2c8f2802 (2026-10-21 20:51) and sent right after; one follow-up message to this worker (tool ownership) is recorded late as ideation-3.md.
Dispatched: from c27e76590c1d2dc910e7fa2d332242a7534df0b0
Model: sonnet

## Checklist

Redo the design as the read-adr skill per Captain amendment 3 and Captain amendment 4, and per boundary contract v2 (PR #691). Earlier Captain amendment 1 and Captain amendment 2 parts are superseded where those two say so. Deliver: the reading recipe (`git show <commit>:<path>` plus `shasum -a 256`, Status and `Superseded by` lines, following a cited reference into another repo or stopping); the five ordered routing questions with the one-home rule and "instruction files point, they do not restate"; writing guidance that wraps dev2 (template, `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0/scripts/adr_lint.py`, the FO's `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0/scripts/number_guards.py` reservation; resolve the package path from the installed kc-dev-flow-2 and name the version; ship no copy); and the optional prefix spec (cross-repo short names; monorepo namespaces deferred).
Replacement acceptance criteria for the superseded AC-1, AC-2 and AC-3, each with a reproducible evidence clause. The main proof is that a dev2 worker actually loads read-adr and follows it. Reuse the adr-read-and-route-poc harness where it fits (read only). The existing AC-4 (loads on Claude and Codex) stays.
Unresolved decisions for the Captain listed, for example plugin layout and the skill's name and trigger text. Run `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0/scripts/design_surfaces.py check <task>` (Surfaces is now none). Write no repository file, branch or commit.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0
Send your completion message to `main` (the completion block's `team-lead` is not registered on this host).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 (shared; touch only this task's file and folder).
Read the task's `## Captain amendments` 1-4 first. The plugin is named kc-adr and the skill read-adr (Captain amendment 1). The previous CLI design in `## Design` is superseded; replace it, do not extend it.
Boundary contract v2: docs/journey/kc-decision-log/boundary-contract.md on origin/docs/kc-decision-log-boundary (PR #691). kc-adr has one purpose, and cross-domain organization is out of scope.
Evidence base: dev2-poc task adr-read-and-route-poc (archived done) at /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc/.spacedock-state/_archive/adr-read-and-route-poc/ (results.md, harness/, CHANGES.md). Read only.
Wrap, not move: the dev2 FO agreed on 2026-10-21 and the Captain has not ruled yet. Keep the design valid if the ruling changes; do not copy dev2 scripts.
