# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## What This Is

A Claude Code plugin (`kc-plugin-forge`) that provides a one-command quality pipeline for plugin development. It orchestrates marketplace skills (`superpowers:writing-skills`, `plugin-dev:plugin-validator`, `plugin-dev:agent-development`) to scaffold, TDD-test, validate, and improve Claude Code plugins.

## Architecture

**Skills** (2) run in main conversation context:

```
skills/kc-plugin-forge/      -> main orchestrator (4-phase pipeline + routes)
skills/kc-plugin-forge-help/ -> interactive help guide, topic deep-dive, feedback collection
```

**Hooks** (1):

```
hooks/session-start.md       -> reminds user of forge availability at session start
```

**References** (4) — knowledge base read by the orchestrator skill:

```
reference/quality-pipeline.md    -> phase gotchas, cross-phase lessons (grows over time)
reference/skill-evolution.md     -> D1/D2 self-improvement framework
reference/doc-sync-templates.md  -> templates for scaffolding doc-sync into plugins
reference/learned-patterns.md    -> cross-project patterns from forge runs (grows over time)
```

## Self-Improvement

The orchestrator skill accumulates lessons via Phase 4 Learning:

| Dimension | Target | Gate |
|-----------|--------|------|
| D1 (cross-project) | `reference/learned-patterns.md` | Auto-append, no gate |
| Forge-specific | `reference/quality-pipeline.md` | Hard signal detection |

Both files grow over time. `learned-patterns.md` benefits all users via PR-back flow. `quality-pipeline.md` is forge-internal knowledge.

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
