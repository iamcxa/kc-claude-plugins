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

## How It Works

```
     /kc-plugin-forge path/to/my-plugin
                    |
          +---------+---------+
          |                   |
    Phase 1: Structure   Phase 1.5: Autonomy
    Validate plugin.json,   Choose self-improvement
    layout, agents          level (D1/D2/Skip) +
          |                 doc-sync level
          |                   |
          +---------+---------+
                    |
          Phase 2: Skill TDD
          RED → GREEN → REFACTOR
          per skill, under pressure
                    |
          Phase 3: Agent Verify
          Examples, tools, prompts,
          dispatch test per agent
                    |
          Phase 4: Report + Learning
          Re-validate, capture patterns
          to learned-patterns.md
```

## Why It Works — Real Examples

The forge pipeline catches issues that code review and manual testing miss. These are real findings from forge runs on production plugins:

### "MANDATORY" doesn't mean enforced

During the **kc-em-triage** forge, Phase 2 TDD revealed that a "MANDATORY" Learning step (Step 7) existed in the skill text but was **absent from the dot graph**. Under pressure testing, agents followed the graph — `discuss → next issue` — and silently skipped Learning every time.

**Root cause:** Agents treat flow visualizations as the authoritative contract. Text-only steps are invisible.

**Fix:** Every mandatory step must appear in BOTH the text description AND the flow graph. The forge now checks for this mismatch.

### Escape hatches get stretched

During the **superpowers /auto** forge, a skill had an escape hatch: "skip TDD for pure UI with no testable logic." In practice, agents classified a button with `onClick → useCustomMutation → error handling` as "pure UI" — because the predicate was subjective.

**Root cause:** Vague predicates invite rationalization. "Pure UI" means whatever the agent wants it to mean.

**Fix:** Replace subjective predicates with concrete decision lists. "Does it have an `on*` handler that calls a mutation? → TESTABLE." No list match → escape hatch does not apply.

### Template blocks dominate live-read instructions

During **kc-plugin-forge self-forge** (this plugin auditing itself), a help skill was told to "Read live data from `skills/*.md`" but then shown a hardcoded output template. The template's specificity dominated — agents emitted it verbatim, silently missing any newly added skills.

**Root cause:** Specific templates win over abstract instructions. The agent sees a ready-made answer and uses it.

**Fix:** Insert an explicit "formatting guide only — populate from live reads" directive before template blocks.

### These patterns compound

Each finding becomes a permanent entry in `learned-patterns.md`. The forge reads this file at startup, so future runs catch the same class of issues across ALL plugins — not just the one where the pattern was discovered.

```
Plugin A forge run → discovers "escape hatch abuse" pattern
                   → auto-appends to learned-patterns.md
                   ↓
Plugin B forge run → reads learned-patterns.md at startup
                   → flags similar escape hatches in Plugin B
                   → fixes before they cause real issues
```

After 8 forge runs across 6 plugins, the knowledge base has **9 cross-project patterns** — each discovered from a real failure, each preventing the same failure in every future run.

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
| `kc-plugin-forge-doc-sync` | Documentation gap scanner & writer (Light — static scan + history) |

## Documentation

| File | Content |
|------|---------|
| `docs/getting-started.md` | Prerequisites, install, first forge run, Phase 2.5 setup |
| `docs/commands.md` | All routes, flags, Phase 2.5 configuration |
| `docs/architecture.md` | Pipeline flow, file tree, reference descriptions, dependencies |

## Reference Files

| File | Content |
|------|---------|
| `reference/quality-pipeline.md` | Experience-based checklist, phase gotchas, cross-phase lessons |
| `reference/skill-evolution.md` | D1/D2 self-improvement framework |
| `reference/doc-sync-templates.md` | Templates for scaffolding doc-sync into plugins |
| `reference/learned-patterns.md` | Cross-project patterns accumulated from forge runs |
| `reference/doc-sync-context.md` | Doc-sync domain knowledge (self-maintained) |
| `reference/clean-profile-test.sh` | Phase 2.5 execution isolator script |

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
