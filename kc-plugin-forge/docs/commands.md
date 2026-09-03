# Commands

## `/kc-plugin-forge`

Main orchestrator — runs the quality pipeline on a target plugin.

### Routes

| Input | Phases | Description |
|-------|--------|-------------|
| `<path>` | 1 → 1.5 → 2 → 2.7 → 2.5 → 3 → 4 | Full pipeline on existing plugin |
| `new <name>` | scaffold → 1.5 → 2 → 2.7 → 2.5 → 3 → 4 | Create new plugin + full pipeline |
| `validate-only` | 1 | Structure check only |
| `skill-tdd-only` | 2 → 2.7 → 2.5 | Skill TDD + dreaming + smoke test |
| `agent-verify-only` | 3 | Agent verification only |
| `self-forge` | 2 → 2.7 → 4 | Forge audits itself (incl. pattern promotion) |
| `dreaming <path>` | 2.7 | Pattern promotion only — pure knowledge curation |
| `dreaming --all` | 2.7 × N | Multi-plugin discovery + promotion per plugin |
| `dreaming --dry-run` | 2.7 (analysis) | Show promotion plan without executing (combinable) |
| `--parallel` | (modifier) | Enable teammate dispatch for Phase 2/3 scenario design and GREEN authoring — RED/GREEN execution itself always goes through the clean runner (`skill-runner.sh`), sequential or parallel. Combinable with `<path>`, `skill-tdd-only`, `new`. Falls back to sequential if TeamCreate unavailable or ≤1 skill+agent. |
| *(bare)* | — | Disambiguate: list plugins, confirm target + scope |

### Phase Reference

| Phase | What it does | Marketplace skill |
|-------|-------------|-------------------|
| 1 | Validate plugin.json, file layout, agent frontmatter | `plugin-dev:plugin-validator` |
| 1.5 | A: Self-Learning level (D1/D2/Skip) + B: Doc Self-Iteration level + C: Agent Teams capability (Full/Skip) | — |
| 2 | RED/GREEN/REFACTOR TDD cycle per skill — scenario design + GREEN authoring in-session, every run scored on the clean runner | `superpowers:writing-skills` + `skill-runner.sh` |
| 2.5 | Clean profile smoke test per skill | `clean-profile-test.sh` |
| 2.7 | Dreaming — promote mature patterns from `learned-patterns.md` into reference files | — (LLM analysis) |
| 3 | Verify agent examples, tools, prompts, dispatch test | `plugin-dev:agent-development` |
| 4 | Re-validate, summary report, learning capture, doc-sync offer | `plugin-dev:plugin-validator` |

### Phase 2.7 Dreaming

After Phase 2 TDD, forge analyzes mature patterns in `learned-patterns.md` and promotes them into structured reference files. This graduates knowledge from a flat list into the files where it's most useful.

**Entry gate**: ≥5 dated patterns in `learned-patterns.md`. **Age filter**: only patterns ≥7 days old become candidates. Both must pass for dreaming to run.

**Steps:**

| Step | What it does |
|------|-------------|
| 2.7.1 Inventory | Parse dated headings, apply age filter, build candidate list |
| 2.7.2 Duplicate Detection | Check candidates against existing reference files (batch LLM calls) — auto-cleanup already-covered patterns |
| 2.7.3 Placement Analysis | LLM determines target file, section, promotion type (`new_entry` / `enhance_existing` / `new_section` / `skill_rule`) |
| 2.7.4 Confirm & Execute | Present plan, user approves. `skill_rule` requires per-item confirmation. |

**Safety limits**: max 5 promotions/run, max 2 `skill_rule`/run, oldest patterns first if exceeded. Cleanup (auto-delete of already-covered patterns) is unlimited.

**Standalone route** (`dreaming <path>` / `--all`): commits changes + offers PR if repo has remote. In-pipeline: changes are working-tree only (no mid-pipeline commit).

**Discovery for `--all`**: `$KC_WORKSPACE` → `~/.claude/plugins/local/` → ask user.

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

The Phase 4 report includes a Dreaming section when Phase 2.7 ran:

```
Dreaming:   N candidates → M promoted, K cleanup
            Promoted: <file> §<section>, ...
```

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

**C — Agent Teams Capability:**

Forge detects whether the plugin's agents would benefit from Agent Teams (persistent teammates):

| Signal | → Full Teams | → Skip |
|--------|-------------|--------|
| Browser-operating agents (tools include Bash) | Full | |
| Multi-agent dispatch (2+ agents from one skill) | Full | |
| Analysis-only agents (Read/Grep/Glob — no Bash) | | Skip |
| No agents | | Skip |

| Level | What's scaffolded |
|-------|-------------------|
| Full | `references/agent-teams.md` + Team Mode Protocol per agent + `--no-teams` fallback in skills |
| Skip | No Teams components |

**Existing plugin retrofit**: When forging an existing plugin, forge checks for pre-existing `learned-patterns.md` (A), `*-doc-sync/` skill (B), and `references/agent-teams.md` (C). If found → verifies setup matches level. If not found → presents the choices above.

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

## `/kc-plugin-release`

Maintainer-only release handoff for this marketplace repository. It does not
change versions, tags, changelogs, or marketplace metadata; release-please owns
those operations.

| Route | Effect |
|-------|--------|
| Feature or release PR | Run the packaged `watch-pr-checks.sh` helper and reject failed checks or a moved PR head |
| After a release exists | From a clean, current `main`, run `post-release-sync.sh` to copy one plugin to both local Claude Code and Codex install roots |

Both helpers resolve from the installed `kc-plugin-forge` root. They do not
depend on user-global skill directories or repository-name conventions.

## SessionStart Hook

The plugin includes a SessionStart hook (`hooks/hooks.json`) that fires at the start of every session where the forge plugin is loaded. It detects uncommitted plugin changes and suggests running `validate-only`.
