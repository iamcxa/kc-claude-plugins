# kc-plugin-forge

One-command plugin development and quality pipeline for Claude Code. Orchestrates marketplace skills to scaffold, TDD-test, validate, and improve Claude Code plugins.

## Install

```bash
# From marketplace (recommended)
claude plugin add iamcxa/kc-claude-plugins/kc-plugin-forge

# Or load directly
claude --plugin-dir path/to/kc-plugin-forge
```

## Prerequisites

Required marketplace plugins (runtime dependencies):

- **superpowers** — provides `superpowers:writing-skills` for skill TDD
- **plugin-dev** — provides `plugin-dev:plugin-validator`, `plugin-dev:plugin-structure`, `plugin-dev:agent-development`
- **claude-md-management** (optional) — provides `claude-md-management:revise-claude-md` for self-improvement loop

## Quick Start

```bash
# Validate an existing plugin (full 4-phase pipeline)
/kc-plugin-forge path/to/my-plugin

# Validate structure only
/kc-plugin-forge validate-only

# Create a new plugin from scratch
/kc-plugin-forge new my-plugin-name

# Forge audits itself
/kc-plugin-forge self-forge

# Get help
/kc-plugin-forge-help
```

## Pipeline Phases

| Phase | What it does | Marketplace skill used |
|-------|-------------|----------------------|
| 1. Structure | Validate plugin.json, file layout, agent frontmatter | `plugin-dev:plugin-validator` |
| 1.5 Autonomy | A: Self-Learning level (D1/D2) + B: Doc Self-Iteration level | — |
| 2. Skill TDD | RED/GREEN/REFACTOR cycle per skill | `superpowers:writing-skills` |
| 3. Agent Verify | Check examples, tools, prompts per agent | `plugin-dev:agent-development` |
| 4. Report | Final structure check, summary, learning capture | `plugin-dev:plugin-validator` |

## Routes

| Input | Phases run |
|-------|-----------|
| `<path>` | 1 → 1.5 → 2 → 3 → 4 (full pipeline) |
| `new <name>` | scaffold → 1.5 → 2 → 3 → 4 |
| `validate-only` | 1 only |
| `skill-tdd-only` | 2 only |
| `agent-verify-only` | 3 only |
| `self-forge` | 2 + 4 (self-audit) |
| *(bare)* | Disambiguate: list plugins, confirm target + scope |

## Self-Improvement

Forge accumulates lessons during runs via a two-dimension framework:

- **D1 (cross-project)**: General patterns auto-append to `reference/learned-patterns.md`
- **D2 (project-specific)**: Gated write to project CLAUDE.md with severity gate + three-question test

Phase 1.5 lets you choose the level (Full D1+D2 / D1 only / Skip) for each plugin you forge.

## Doc Self-Iteration

Phase 1.5 B offers template-based documentation sync:

- **Full**: `<plugin>-doc-sync` skill + `doc-probe` agent + `doc-sync-context.md` reference
- **Light**: Skill + reference only (no live probing)
- **Skip**: No doc-sync capability

Run with `/<plugin>-doc-sync` after scaffolding.

## Skills

| Skill | Purpose |
|-------|---------|
| `kc-plugin-forge` | Main orchestrator — full pipeline or single-phase routes |
| `kc-plugin-forge-help` | Interactive guide, topic deep-dive, feedback → GitHub issue |

## Reference Files

| File | Content |
|------|---------|
| `reference/quality-pipeline.md` | Experience-based checklist, phase gotchas, cross-phase lessons |
| `reference/skill-evolution.md` | D1/D2 self-improvement framework |
| `reference/doc-sync-templates.md` | Templates for scaffolding doc-sync into plugins |
| `reference/learned-patterns.md` | Cross-project patterns accumulated from forge runs |

## Contributing

Found a gap or have a better pattern?

```bash
# Quick feedback → GitHub issue
/kc-plugin-forge-help --feedback "description of the gap"

# Or open an issue directly
# https://github.com/iamcxa/kc-claude-plugins/issues/new
```

PRs welcome — especially new entries for `learned-patterns.md`.

## License

[MIT](LICENSE)
