# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## What This Is

A Claude Code plugin (`kc-plugin-forge`) that provides a one-command quality pipeline for plugin development. It orchestrates marketplace skills (`superpowers:writing-skills`, `plugin-dev:plugin-validator`, `plugin-dev:agent-development`) to scaffold, TDD-test, validate, and improve Claude Code plugins.

## Architecture

**Skills** (3) run in main conversation context:

```
skills/kc-plugin-forge/          -> main orchestrator (7-phase pipeline + routes: 1→1.5→2→2.7→2.5→3→4 + dreaming)
skills/kc-plugin-forge-help/     -> interactive help guide, topic deep-dive, feedback collection
skills/kc-plugin-forge-doc-sync/ -> documentation gap scanner & writer (Light — static scan + history)
```

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

Phase 2.7 (Dreaming) promotes mature D1 patterns from `learned-patterns.md` into structured reference files, completing the knowledge flywheel: learn → accumulate → promote → lean file.

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

Semantic commit prefixes: `feat`, `fix`, `docs`, `chore`. Version follows semver in `.claude-plugin/plugin.json`. After bumping, sync marketplace via `/kc-marketplace-sync`.
