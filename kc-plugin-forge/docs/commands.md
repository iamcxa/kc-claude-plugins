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
| 4 | Re-validate, summary report, learning capture, doc-sync offer | `plugin-dev:plugin-validator` |

### Phase 4 Learning

After the summary report, forge scans for **hard signals** — concrete events during the run that indicate a new pattern:

| Signal | Source |
|--------|--------|
| Phase 1 FAIL item fixed | Structural problem → potential new gotcha |
| Phase 2 TDD RED failure mode | Skill weakness → potential pattern |
| Phase 2 REFACTOR rationalization | New anti-pattern discovered |
| Phase 3 agent verification failure | Agent design issue |
| Fix attempt > 1 | Non-obvious problem |
| Workaround used | Tool/process limitation |

Signals found → compared against `learned-patterns.md` + `quality-pipeline.md`. Novel patterns are captured. No signals → Light Reflection ("What was most unexpected?").

### Phase 4 Doc-Sync Offer

After learning, forge checks if the target plugin has a doc-sync skill (`*-doc-sync/SKILL.md`):

- **Found** → "Forge made changes — run `/<plugin>-doc-sync`?" (y/n)
- **Not found but `docs/` exists** → advisory suggesting Phase 1.5 B scaffolding
- **Neither** → skip silently

### Phase 1.5 Options

**A — Self-Learning:**

Forge analyzes the plugin description to recommend a level:

| Description keywords | → Classification | → Recommended |
|---------------------|-----------------|---------------|
| review, analyze, audit, triage, check, evaluate | analysis | Full (D1+D2) |
| sync, bump, scaffold, generate, compile, convert | utility | Skip |
| create, build, new, init | scaffold | Skip |
| mixed or ambiguous | mixed | Full (D1+D2) |

The recommendation is advisory — you always pick the final level:

| Level | What's scaffolded |
|-------|-------------------|
| Full (D1+D2) | `learned-patterns.md` + Learning step in each skill + D1 auto-append + D2 gated write |
| D1 only | `learned-patterns.md` + D1-only Learning step |
| Skip | No self-improvement scaffolding |

**B — Doc Self-Iteration:**

Forge counts docs and skills to recommend a level:

| Signal | → Full | → Light | → Skip |
|--------|--------|---------|--------|
| `docs/` with 3+ files | Yes | | |
| `docs/` with <3 files | | Yes | |
| README.md only | | Yes | |
| No documentation at all | | | Yes |
| 3+ skills | Yes | | |

| Level | What's scaffolded |
|-------|-------------------|
| Full | `<plugin>-doc-sync` skill + `doc-probe` agent + `doc-sync-context.md` |
| Light | `<plugin>-doc-sync` skill + `doc-sync-context.md` (no live probing) |
| Skip | No doc-sync capability |

**Existing plugin retrofit**: When forging an existing plugin, forge checks for pre-existing `learned-patterns.md` (A) and `*-doc-sync/` skill (B). If found → verifies setup matches level. If not found → presents the same choices above.

### Phase 2.5 Configuration

Smoke tests use `claude --bare --effort low` — `--effort low` reduces cost ~77% ($0.107→$0.025/test) and time ~50% with zero quality loss for assertion checking. Do NOT substitute haiku — it fabricates prior conversation context in `--bare` mode, defeating the test's purpose.

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
| `--feedback "<message>"` | Report a doc gap → GitHub issue (falls back to local `feedback-log.md` if `gh` unavailable) |
| `--list-topics` | Show available help topics |

The help skill also has two proactive behaviors:
- **Gap Detection**: When answering from SKILL.md instead of docs, it offers to draft a doc section or create a tracking issue.
- **Knowledge Loop**: After any interaction, checks if the user shared a pattern worth capturing.

## `/kc-plugin-forge-doc-sync`

Documentation gap scanner and writer for this plugin (Light variant — no live probes).

| Arg | Effect |
|-----|--------|
| *(bare)* | Full sync: scan → enrich → write → report |
| `--check` | Report only (no writes) |
| `--auto` | Full sync without confirmation prompts |
| `--section <doc-file>` | Targeted sync on one doc file |

### Phases

| Phase | What it does |
|-------|-------------|
| 1. Static Scan | Inventory skills/hooks, cross-reference against docs, classify gaps (Critical/Warning/Info) |
| 2. History Enrichment | Search episodic memory + journal for usage context. **Graceful degradation**: if MCP tools unavailable → runs static-only mode (no error) |
| 3. Write / Update | Present gaps for approval: **a** (all), **s** (select), **e** (edit outlines), **q** (quit). Respects `auto-sync` flag per doc: `yes` = safe to rewrite, `partial` = edit subsection only |
| 4. Live Probe | *Disabled (Light variant)* — forge skills depend on marketplace plugins, probes would fail |
| 5. Self-Update | Sync `doc-sync-context.md` Source Map with current skill/hook inventory. New files → auto-added. Removed files → marked deprecated. |
| 6. Report | Summary table + D1 learning check + offer to create GitHub issue for remaining gaps |

## SessionStart Hook

The plugin includes a SessionStart hook (`hooks/hooks.json`) that fires at the start of every session where the forge plugin is loaded. It detects uncommitted plugin changes and suggests running `validate-only`.
