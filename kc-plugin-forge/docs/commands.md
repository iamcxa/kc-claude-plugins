# Commands

## `/kc-plugin-forge`

Main orchestrator — runs the quality pipeline on a target plugin.

### Routes

| Input | Phases | Description |
|-------|--------|-------------|
| `<path>` | 1 → 1.5 → 2 → 2.5 → 3 → 4 | Full pipeline on existing plugin |
| `new <name>` | scaffold → 1.5 → 2 → 2.5 → 3 → 4 | Create new plugin + full pipeline |
| `validate-only` | 1 | Structure check only |
| `skill-tdd-only` | 2 → 2.5 | Skill TDD + smoke test only |
| `agent-verify-only` | 3 | Agent verification only |
| `self-forge` | 2 → 4 | Forge audits itself |
| *(bare)* | — | Disambiguate: list plugins, confirm target + scope |

### Phase Reference

| Phase | What it does | Marketplace skill |
|-------|-------------|-------------------|
| 1 | Validate plugin.json, file layout, agent frontmatter | `plugin-dev:plugin-validator` |
| 1.5 | A: Self-Learning level (D1/D2/Skip) + B: Doc Self-Iteration level | — |
| 2 | RED/GREEN/REFACTOR TDD cycle per skill | `superpowers:writing-skills` |
| 2.5 | Clean profile smoke test per skill | `clean-profile-test.sh` |
| 3 | Verify agent examples, tools, prompts, dispatch test | `plugin-dev:agent-development` |
| 4 | Re-validate, summary report, learning capture | `plugin-dev:plugin-validator` |

### Phase 1.5 Options

**A — Self-Learning:**

| Level | What's scaffolded |
|-------|-------------------|
| Full (D1+D2) | `learned-patterns.md` + Learning step in each skill + D1 auto-append + D2 gated write |
| D1 only | `learned-patterns.md` + D1-only Learning step |
| Skip | No self-improvement scaffolding |

**B — Doc Self-Iteration:**

| Level | What's scaffolded |
|-------|-------------------|
| Full | `<plugin>-doc-sync` skill + `doc-probe` agent + `doc-sync-context.md` |
| Light | `<plugin>-doc-sync` skill + `doc-sync-context.md` (no live probing) |
| Skip | No doc-sync capability |

### Phase 2.5 Configuration

API key is resolved automatically:

1. `ANTHROPIC_API_KEY` env var (if already set)
2. `~/.claude/kc-plugins-config/forge.yaml` → `api_key_file` path
3. Neither → `(clean profile unavailable)`

```yaml
# ~/.claude/kc-plugins-config/forge.yaml
api_key_file: /path/to/.env
```

Report shows `key_source=<env|path>` for traceability.

### Smoke Test Files

| Type | Location | When used |
|------|----------|-----------|
| Hand-written | `<plugin>/smoke-tests/<skill-name>.smoke.yaml` | Preferred — explicit trigger + assertions |
| Auto-generated | *(ephemeral)* | Fallback — derived from SKILL.md description |

## `/kc-plugin-forge-help`

Interactive help guide for the forge.

| Arg | Effect |
|-----|--------|
| *(none)* | Overview of all commands and topics |
| `<topic>` | Deep dive into a topic |
| `--feedback "<message>"` | Report a doc gap → GitHub issue |
| `--list-topics` | Show available help topics |

## `/kc-plugin-forge-doc-sync`

Documentation gap scanner and writer for this plugin.

| Arg | Effect |
|-----|--------|
| *(bare)* | Full sync: scan → enrich → write → report |
| `--check` | Report only (no writes) |
| `--auto` | Full sync without confirmation prompts |
| `--section <doc-file>` | Targeted sync on one doc file |
