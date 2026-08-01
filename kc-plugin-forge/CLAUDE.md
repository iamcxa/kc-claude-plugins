# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## What This Is

A Claude Code plugin (`kc-plugin-forge`) that provides a one-command quality pipeline for plugin development. It orchestrates marketplace skills (`superpowers:writing-skills`, `plugin-dev:plugin-validator`, `plugin-dev:agent-development`) to scaffold, TDD-test, validate, and improve Claude Code plugins.

## Architecture

**Skills** (5) run in main conversation context:

```
skills/kc-plugin-forge/                -> main orchestrator (7-phase pipeline + routes: 1→1.5→2→2.7→2.5→3→4 + dreaming)
skills/kc-plugin-forge-help/           -> interactive help guide, topic deep-dive, feedback collection
skills/kc-plugin-forge-doc-sync/       -> documentation gap scanner & writer (Light — static scan + history)
skills/kc-plugin-forge-sanitize-check/ -> prepublish safety-net grep (REJECT/BLOCK/WARN classes) — backstop to Early-stage Dreaming
skills/kc-plugin-release/              -> exact-head PR checks + post-release local Claude/Codex install sync
```

**Release helper scripts** are packaged under `scripts/` and guarded by
`plugin-release-contract.test.sh`. `watch-pr-checks.sh` uses the GitHub CLI
without a host-global monitor dependency; `post-release-sync.sh` can only copy
an already-released plugin into local Claude Code and Codex install roots.

**Hooks** (1):

```
hooks/hooks.json                 -> SessionStart reminder of forge availability
```

**References** (8) — knowledge base read by the orchestrator skill:

```
reference/quality-pipeline.md      -> phase gotchas, cross-phase lessons (grows over time)
reference/skill-evolution.md       -> D1/D2 self-improvement framework
reference/doc-sync-templates.md    -> templates for scaffolding doc-sync into plugins
reference/learned-patterns.md      -> cross-project patterns from forge runs (grows over time)
reference/clean-profile-test.sh    -> execution isolator for Phase 2.5 clean profile smoke test
reference/doc-sync-context.md      -> doc-sync domain knowledge (self-maintained by doc-sync skill)
reference/agent-teams-quality.md   -> Agent Teams verification patterns, templates, TDD scenarios
reference/parallel-forge.md        -> Teammate dispatch templates, coordination, error recovery for --parallel mode
```

## Self-Improvement

The orchestrator skill accumulates lessons via Phase 4 Learning:

| Dimension | Target | Gate |
|-----------|--------|------|
| D1 (cross-project) | `reference/learned-patterns.md` | Auto-append, no gate |
| Forge-specific | `reference/quality-pipeline.md` | Hard signal detection |

Both files grow over time. `learned-patterns.md` benefits all users via PR-back flow. `quality-pipeline.md` is forge-internal knowledge.

Phase 2.7 (Dreaming) is **two-stage**:

- **Early-stage** (sanitize gate): LOCAL store `~/.claude/kc-plugins-config/learned-patterns-local/<plugin>.md` → public `<plugin>/reference/learned-patterns.md`. Required for plugins with PII concerns (kc-pr-flow, kc-team-ops). Each LOCAL entry rewritten to remove org identifiers + generalized.
- **Late-stage** (taxonomy gate): public `learned-patterns.md` → structured refs (`quality-pipeline.md`, etc.). Existing behavior, mature-pattern promotion.

Knowledge flywheel: capture (LOCAL, raw) → Early Dreaming (sanitize) → public learned-patterns.md (flat, curated) → Late Dreaming (taxonomize) → structured refs.

Forge itself does not adopt the LOCAL layer (no PII concerns for its own learned-patterns.md). Plugins opt in by updating their D1 capture step to target LOCAL.

Adjacent skill: `kc-plugin-forge-sanitize-check` is a prepublish safety net — greps for known leak patterns in case Dreaming missed something. Not a replacement for Dreaming.

## Editing Skills

- The main skill (`kc-plugin-forge/SKILL.md`) is the single source of truth for the pipeline
- Reference files provide depth — SKILL.md references them via `${CLAUDE_PLUGIN_ROOT}/reference/`
- After editing SKILL.md, run `self-forge` to verify quality hasn't regressed
- Token budget: aim for <800 words in SKILL.md; heavy content belongs in `reference/`

## Editing References

- `quality-pipeline.md` is append-friendly — add new gotchas under the appropriate Phase section
- `learned-patterns.md` is append-friendly — add new patterns with date and context
- `skill-evolution.md` is the framework spec — changes here affect all plugins that use self-improvement
- `doc-sync-templates.md` contains templates — `{{PLUGIN_NAME}}` placeholders are replaced during scaffolding

## Key Conventions

- **`plugin.json` is metadata only** — no skills/hooks registration. Auto-discovery from directory structure.
- **`${CLAUDE_PLUGIN_ROOT}`** for all cross-component path references
- **Phase 1 is mandatory** for `<path>` inputs — no exceptions
- **Disambiguate on bare invocation** — never infer a default plugin

## Git Conventions

Semantic commit prefixes: `feat`, `fix`, `docs`, `chore`. Do not bump plugin or
marketplace versions in a feature PR. Root release-please configuration owns
version propagation, changelogs, tags, and GitHub Releases. After its Release
PR merges, use `kc-plugin-release` only for local Claude Code and Codex install
synchronization.
