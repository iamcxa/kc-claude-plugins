# Architecture

## Overview

kc-plugin-forge is a skill-only plugin (no agents) that orchestrates marketplace skills to validate and improve other plugins.

```
kc-plugin-forge/
├── .claude-plugin/plugin.json     # metadata only
├── .codex-plugin/plugin.json      # Codex metadata, skills -> ./skills/
├── skills/
│   ├── kc-plugin-forge/           # main orchestrator (7-phase pipeline + dreaming)
│   │   └── SKILL.md
│   ├── kc-plugin-forge-help/      # interactive help guide
│   │   └── SKILL.md
│   ├── kc-plugin-forge-doc-sync/  # documentation sync (Light — no live probes)
│   │   └── SKILL.md
│   └── kc-plugin-release/         # exact-head checks + local release sync
│       └── SKILL.md
├── scripts/
│   ├── watch-pr-checks.sh         # gh-based exact-head CI watcher
│   ├── post-release-sync.sh       # Claude/Codex local install copy
│   └── plugin-release-contract.*  # packaged-resource and authority tests
├── hooks/
│   └── hooks.json                 # SessionStart reminder
├── reference/
│   ├── quality-pipeline.md        # phase gotchas, cross-phase lessons (grows)
│   ├── learned-patterns.md        # cross-project patterns from forge runs (grows)
│   ├── skill-evolution.md         # D1/D2 self-improvement framework
│   ├── doc-sync-templates.md      # templates for scaffolding doc-sync into plugins
│   ├── doc-sync-context.md        # doc-sync domain knowledge (self-maintained)
│   ├── agent-teams-quality.md    # Agent Teams verification patterns, TDD scenarios
│   ├── parallel-forge.md         # teammate dispatch templates, coordination, error recovery
│   ├── clean-profile-test.sh      # Phase 2.5 execution isolator script; extended for skill-runner.py
│   ├── skill-runner.py            # Phase 2 clean runner entrypoint (cloud | bare): refusals, dispatch, scoring
│   └── skill-scenarios.md         # scenario file format (forge-skill-scenarios/v1)
├── docs/
│   ├── getting-started.md         # prerequisites, install, first run
│   ├── commands.md                # all routes, flags, configuration
│   └── architecture.md            # this file
├── CLAUDE.md                      # plugin-specific conventions
├── README.md                      # marketplace README
└── LICENSE                        # MIT
```

## Pipeline Flow

```
/kc-plugin-forge <path>
        │
Phase 1 ─── plugin-dev:plugin-validator
        │   (validate structure, fix FAILs)
        │
Phase 1.5 ── A: Self-Learning choice (D1+D2 / D1 / Skip)
        │    B: Doc Self-Iteration choice (Full / Light / Skip)
        │    C: Agent Teams capability (Full / Skip)
        │
Phase 2 ─── superpowers:writing-skills (scenario design + GREEN authoring)
        │   + skill-runner.py (RED/GREEN scoring on a clean runner)
        │   + step 9: Teams Setup verification (if Full Teams chosen)
        │
Phase 2.7 ── Dreaming (pattern promotion)
        │    (promote mature learned-patterns.md entries → reference files)
        │
Phase 2.5 ── clean-profile-test.sh
        │    (claude --bare --effort low per skill)
        │
Phase 3 ─── plugin-dev:agent-development
        │   (verify each agent)
        │   + step 6: Agent Teams Readiness (if Full Teams chosen)
        │
Phase 4 ─── plugin-dev:plugin-validator (re-validate)
            + Summary Report
            + Learning (Detection → Capture)
```

## Reference Files (Growing Knowledge Base)

Two reference files grow over time through the Learning mechanism:

### `quality-pipeline.md`

Forge-specific gotchas organized by phase. Entries are added when a forge run discovers a new structural issue or anti-pattern. This is internal knowledge — it helps the forge itself make better decisions.

### `learned-patterns.md`

Cross-project patterns discovered during forge runs on any plugin. These are general — they apply to all plugin development, not just forge. The PR-back flow means patterns discovered by one user benefit everyone:

```
Plugin A forge → discovers pattern → appends to learned-patterns.md
                                            ↓
Plugin B forge → reads at startup → catches same issue class
```

## Self-Improvement Framework

The forge scaffolds self-improvement into other plugins via Phase 1.5. Two dimensions:

**D1 (cross-project)**: General patterns auto-append to `learned-patterns.md`. Low friction, no user gate.

**D2 (project-specific)**: Patterns gated by severity threshold + three-question test (Recurs? Non-obvious? Ruleable?). Written to project CLAUDE.md or project-specific lesson files.

Phase 2.7 (Dreaming) completes the flywheel by graduating mature D1 patterns into structured reference files:

```
Skill session → D1 auto-append → learned-patterns.md accumulates
    → Dreaming (≥7 days, ≥5 patterns):
        cleanup already-covered → promote to reference files → PR-back
            → reference files get richer → fewer novel patterns to capture
                → learned-patterns.md stays lean
```

See `reference/skill-evolution.md` for the full framework.

## Doc-Sync Architecture

The forge also scaffolds doc-sync capability into plugins (Phase 1.5 B). Three levels:

| Level | Components | Probe? |
|-------|-----------|--------|
| Full | Skill + doc-probe agent + context reference | Yes (live behavioral verification) |
| Light | Skill + context reference | No (static scan + history enrichment only) |
| Skip | None | — |

kc-plugin-forge itself uses **Light** — its skills depend on marketplace plugins, making live probes impractical.

## Dependencies

kc-plugin-forge has no agents of its own. It relies entirely on marketplace skills:

| Dependency | Used in | Required? |
|-----------|---------|-----------|
| `superpowers:writing-skills` | Phase 2 (scenario design + GREEN authoring) | Yes |
| `plugin-dev:plugin-validator` | Phase 1, 4 | Yes |
| `plugin-dev:agent-development` | Phase 3 | Yes (if plugin has agents) |
| `plugin-dev:create-plugin` | `new` route | Yes (for new plugins) |
| `claude-md-management:revise-claude-md` | Phase 4 | Optional |

Phase 2's clean runner needs machine-local credentials neither script provisions:
the `conductor` CLI + `CONDUCTOR_API_KEY` for `cloud`, `ANTHROPIC_API_KEY` (env or
`~/.claude/kc-plugins-config/forge.yaml`) for `bare`. Missing either exits with a
named reason; Phase 4 records which runner actually ran.
