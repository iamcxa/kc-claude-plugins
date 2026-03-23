# Getting Started

## Prerequisites

Required marketplace plugins (runtime dependencies):

- **superpowers** — provides `superpowers:writing-skills` for skill TDD (Phase 2)
- **plugin-dev** — provides `plugin-dev:plugin-validator`, `plugin-dev:plugin-structure`, `plugin-dev:agent-development` (Phase 1, 3)
- **claude-md-management** (optional) — provides `claude-md-management:revise-claude-md` for self-improvement loop (Phase 4)

## Install

```bash
# From marketplace (recommended)
claude plugin add iamcxa/kc-claude-plugins/kc-plugin-forge

# Or load directly for development
claude --plugin-dir path/to/kc-plugin-forge
```

## First Forge Run

### Validate an existing plugin

```bash
/kc-plugin-forge path/to/my-plugin
```

This runs the full 4-phase pipeline: Structure → Skill TDD → Agent Verify → Report.

### Create a new plugin

```bash
/kc-plugin-forge new my-plugin-name
```

Scaffolds a new plugin directory, then runs the full pipeline on it.

### Quick structure check

```bash
/kc-plugin-forge validate-only
```

Runs Phase 1 only — checks plugin.json, file layout, agent frontmatter. No TDD or agent verification.

## Phase 1.5: Autonomy Decision

After structure validation, forge asks two questions about the plugin's self-improvement capabilities:

**A — Self-Learning**: Should the plugin accumulate patterns from its own runs?
- Forge analyzes the plugin description (review/analyze → recommends Full, sync/scaffold → recommends Skip)
- You pick: Full (D1+D2), D1 only, or Skip

**B — Doc Self-Iteration**: Should the plugin have a doc-sync skill?
- Forge counts docs and skills to recommend a level
- You pick: Full (with live probes), Light (static scan only), or Skip

Both choices are presented with recommendations. See [commands.md](commands.md#phase-15-options) for the full signal tables.

**Existing plugins**: If the plugin already has `learned-patterns.md` or a doc-sync skill, forge verifies the existing setup instead of re-scaffolding.

## Phase 2.5: Clean Profile Smoke Test

Phase 2.5 runs automatically after Phase 2 TDD. It verifies each skill works without user-specific context (no MEMORY.md, no CLAUDE.md, no other plugin hooks).

### API Key Setup (one-time)

The smoke test requires `ANTHROPIC_API_KEY`. Configure once in `~/.claude/kc-plugins-config/forge.yaml`:

```yaml
api_key_file: /path/to/your/.env
```

The `.env` file should contain:

```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

The script auto-resolves the key: env var → config file → error with hint. The report shows `key_source=` so you know where the key was loaded from.

### Cost

Each smoke test costs ~$0.025 with `--effort low`. A 10-skill plugin adds ~$0.25 total.

## What to Expect

After a full forge run, you'll see a summary report:

```
Plugin Forge Report: my-plugin
─────────────────────────────────
Structure:  PASS (0 items fixed)
Skills:     3 skills tested (9 scenarios, 9 passed)
Clean Profile: 3 skills verified (3 clean-pass)
Agents:     1 agent verified
Evolution:  2 skills with self-improvement (D1 only)
Overall:    PASS
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "superpowers:writing-skills not found" | Install the superpowers marketplace plugin |
| "plugin-dev:plugin-validator not found" | Install the plugin-dev marketplace plugin |
| Phase 2.5 shows `(clean profile unavailable)` | Set up API key in `forge.yaml` (see above) |
| Phase 2.5 timeout on large skills | Increase timeout or write hand-written smoke files in `smoke-tests/` |
| Self-forge route doesn't run Phase 1 | By design — forge's own structure is stable |
