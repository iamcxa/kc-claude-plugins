# Plugin Quality Pipeline Reference

Experience-based checklist for the kc-plugin-forge orchestrator. Updated as new lessons are discovered.

## Prerequisites

Required marketplace plugins (runtime dependencies):
- **superpowers** — `superpowers:writing-skills` for skill TDD
- **plugin-dev** — `plugin-dev:plugin-validator`, `plugin-dev:plugin-structure`, `plugin-dev:agent-development`
- **claude-md-management** (optional) — `claude-md-management:revise-claude-md` for self-improvement loop

## Phase 1: Structure Validation Gotchas

- `tools` field in agent frontmatter: use comma-separated string (e.g., `tools: Read, Grep, Glob`), NOT JSON array — matches e2e-pipeline convention
- `${CLAUDE_PLUGIN_ROOT}` for ALL cross-component path references (skills, agents, reference files)
- `reference/` is a custom directory, NOT auto-discovered — files must be explicitly Read by agents/skills
- Agent frontmatter required fields: `name`, `description`, `model`, `color`, `tools`
- `<example>` blocks in agent description improve dispatch accuracy — include 2-4 with context/user/assistant/commentary
- `color` field is required but often forgotten — add during initial creation
- **`plugin.json` `author` field is an object, not a string** — Zod validation requires `{"name": "Kent"}`, not `"Kent"`. Unlike npm's package.json which accepts both forms, Claude Code's strict schema rejects string values with `expected object, received string`. Plugin silently fails to load.
- **`hooks.json` root must be an object with `hooks` key** — the format is `{ "hooks": { "EventName": [...] } }`, not a bare array `[{ "event": "...", "hooks": [...] }]`. The bare array format triggers `expected object, received array`. This is the same nested structure as `settings.json` hooks, not a flat event list.
- **Plugin discovery requires 3-layer registration** — a plugin directory existing is NOT enough. All three must be in place:
  1. **`marketplace.json`**: plugin must be listed in the parent marketplace's `.claude-plugin/marketplace.json` `plugins[]` array (e.g., `~/.claude/plugins/local/.claude-plugin/marketplace.json` for local plugins)
  2. **`enabledPlugins`**: `"<plugin-name>@<marketplace-name>": true` must exist in `~/.claude/settings.json` (user-scope) or project `.claude/settings.json` (project-scope)
  3. **Session restart**: plugins load at session start only — mid-session changes require exit + relaunch
- **`plugin.json` is metadata only** — hooks and skills are NOT declared in `plugin.json`. Claude Code uses auto-discovery: `hooks/hooks.json` for hooks, `skills/<name>/SKILL.md` for skills. Putting hooks/skills in `plugin.json` is silently ignored.
- **Symlinks work for local plugins** — `ln -s /source/path ~/.claude/plugins/local/<name>` is valid, but still needs marketplace.json + enabledPlugins registration.

## Phase 2: Skill TDD Patterns

- **Pressure test design**: academic question (does agent understand?) + pressure scenario (does it comply?) + combo scenario (multiple signals)
- **Deliberation gate skills**: use table format over tree format — more scannable, agents parse better, saves tokens
- **Rationalization table**: name specific compromise patterns and explain why each is wrong (e.g., "spot-check is a compromise disguised as diligence")
- **Red Flags list**: concrete self-check items for agents to recognize when they're about to violate rules
- **Multi-signal ordering**: when multiple paths trigger, resolve information-gathering first (Research > Brainstorm), then decisions (Debate), then structural (Decompose)
- **Token budget**: aim for <800 words in SKILL.md; extract heavy reference (decompose flows, templates, API docs) to `reference/` files
- **Regression testing after refactoring**: run same scenarios on old and new versions, compare behavior consistency
- **Default route for multi-command skills**: Skills with subcommands (start/stop/status, --debug/--maintain, etc.) MUST define a bare invocation handler. Show: (1) available commands with one-line descriptions, (2) current status from relevant data source, (3) suggested next step based on state. Never leave bare invocation undefined — "infer from context" is not a default route.

## Phase 2: Skill Evolution Check

After TDD passes for each skill, verify self-improvement capability per `skill-evolution.md`:

- **Applies when**: skill analyzes, evaluates, or assesses (code review, triage, quality check, etc.)
- **Does NOT apply**: pure utility skills (sync, version bump, scaffold) — skip with note in report
- **Checklist**: Learning step exists → `learned-patterns.md` exists → setup phase reads it → D2 writes reference write threshold → rules include D1 auto-append + D2 gated write

## Phase 2.5: Clean Profile Smoke Test Gotchas

- **`timeout` on macOS requires coreutils**: The `timeout` command is from GNU coreutils (`brew install coreutils`). macOS ships `gtimeout` instead. If the script fails with "timeout: command not found", install coreutils or alias `timeout=gtimeout`.
- **`ANTHROPIC_API_KEY` is required**: The script uses `claude --bare` which only accepts API key auth (no OAuth/keychain). Store the key in a `.env` file and `export` it before running forge. Without the key, Phase 2.5 silently degrades.
- **Smoke assertions should target skill-level output, not tool-level**: In `--bare` mode, no other plugins are loaded. Assertions like `contains: "plugin-validator"` test that the skill mentions the concept, not that the tool actually ran. Skills with inter-plugin dependencies should use hand-written smoke files scoped to skill-own output.
- **`not_contains` is case-insensitive**: `not_contains: "MEMORY.md"` catches both `MEMORY.md` and `memory.md`. Be specific with patterns.
- **AskUserQuestion skills skip auto-generate**: Skills with interactive prompts and no non-interactive path are skipped entirely by auto-generate. Hand-written smoke files can override this by providing a prompt that takes the non-interactive path.
- **Large plugins add ~15s per skill with `--effort low`**: Each smoke test invokes `claude --bare --effort low -p` (~15s, ~$0.025 per test). A 9-skill plugin adds ~2.5 minutes / ~$0.23 to Phase 2.5. Without `--effort low`, cost is ~4x higher (~$0.10/test).
- **Do NOT use haiku for smoke tests**: Haiku fabricates prior conversation context in `--bare` mode (e.g., `"Based on the recent conversation..."` when there is none). This defeats the core purpose of clean profile testing — distinguishing real context pollution from clean operation. Sonnet + `--effort low` is the cost-effective floor.
- **Skill-name fallback trigger produces topic summaries, not skill invocations**: In `--bare` mode, using the skill name (e.g., `"kc-sentry-insight"`) as the smoke trigger causes the LLM to treat it as an informational query about the plugin, not a skill invocation. Skill routing never fires, and assertions expecting skill-level output (like `contains: "Usage"`) fail. Prefer first-clause extraction from description (e.g., `"scanning Sentry for production errors"`) over skill-name fallback. If the first clause also fails, the smoke trigger should prepend a slash: `"/kc-sentry-insight"` to signal invocation intent.

## Phase 3: Agent Verification Checklist

- **model selection**: research/utility tasks → `sonnet`; reasoning/review/complex tasks → `inherit` or `opus`
- **`<example>` blocks**: 2-4 examples, each with Context/user/assistant/commentary
- **Input/Output contract**: explicitly define what agent receives and what it returns
- **Rules section**: include anti-patterns (what NOT to do) alongside positive rules
- **Reference file paths**: always use `${CLAUDE_PLUGIN_ROOT}/reference/filename.md`
- **Tool restriction**: principle of least privilege — only grant tools the agent needs

## Phase 4: Re-validation

- Run `plugin-dev:plugin-validator` agent after all fixes
- Expect PASS on all previously-FAIL items
- WARN items are acceptable if documented (README, SKILL.md Prerequisites)

## Phase 1→2 Transition Gotchas

- **fix → reaudit loop has no max-retry**: Add "after 3 fix attempts, escalate to user" if the same FAIL item keeps recurring. Prevents infinite loops when a FAIL item has a deeper structural cause.
- **`--add-dir` ≠ plugin loading**: `--add-dir` only adds working directory (CLAUDE.md + file access). Use `--plugin-dir` to load skills/agents/hooks. This caused "skill not appearing" bugs when plugins were added via wrong flag.

## Cross-Phase Lessons

- Plugins have NO formal dependency mechanism — runtime resolution + graceful degradation
- External dependencies must be documented in README and SKILL.md Prerequisites section
- After any structural change, re-run validator (don't assume fixes are correct)
- Writing-skills TDD applies to EDITS too, not just new skills — the Iron Law has no exceptions
- CSO rule: description = "Use when [triggers]" only, NEVER summarize workflow (Claude takes shortcuts)
- **Contract bypass via parallel paths**: When a skill has a specific output contract (e.g., resume ID), audit ALL paths that can trigger the same behavior. Hooks, CLAUDE.md instructions, and enforcer messages can each create a bypass that produces the behavior WITHOUT the skill's output contract. Fix: make all paths point to the skill, not duplicate its logic.
- **Routing priority: explicit intent > implicit system state**: When multiple resume/restore mechanisms coexist (GSD checkpoint, journal handoff), user's explicit input (handoff ID) must take precedence over file-exists checks. Unconditional gates on system state break when the user has stronger intent signals.
- **Forge applies to standalone skills too**: The TDD cycle (RED/GREEN/REFACTOR) works identically for `~/.claude/skills/` standalone skills — skip Phase 1 plugin-validator and Phase 3 agent-verify, focus on Phase 2 skill TDD. The system integration audit (hooks, CLAUDE.md, enforcers) is unique to standalone skills that are referenced by external infrastructure.
- **ToolSearch finds tools, not skills**: `ToolSearch` returns deferred MCP/system tools, not project skills. For skill discovery, rely on documentation layer (CLAUDE.md skill tables, README) — these are the project-specific skill source of truth. ToolSearch is complementary for tool discovery only.
- **Deliberation gate overlap resolution**: When signals trigger multiple paths (e.g., Decompose + Design Spec), add explicit priority rules in the gate description. Agents default to the first matching row — implicit priority by table order is fragile. Add "X supersedes Y when Z" clauses.
- **Partial-route completeness**: When a skill has `X-only` shortcut routes (e.g., `skill-tdd-only`), ensure ALL common use cases have corresponding routes. A missing `validate-only` alongside existing `skill-tdd-only` and `agent-verify-only` was a structural gap — the most common invocation ("just check structure") fell through to the full pipeline or got misrouted. Audit route table for symmetry.
- **Disambiguation over inference**: Bare invocations in multi-plugin workspaces must disambiguate (list plugins, confirm scope) — never infer a default. Two-rule reinforcement (route selection + explicit Rules entry) with "never" language provides the strongest defense against scope-guessing.
- **Audience context vs. project context for language**: When a skill produces repo artifacts (PR body, commit messages), use project-level language config (`language.yaml` pwd match). When a skill produces communication (Slack announcements, messages), use audience-level config (`channels.yaml` channel defaults). Without explicit priority, agents will reason their way to inconsistent answers. Always define the resolution order in the skill.
- **Cross-plugin config over hardcoded prefs**: User preferences that span multiple plugins (language, channels, identity) belong in a shared config directory (`~/.claude/kc-plugins-config/`), not hardcoded in skill source or stored in auto-memory. Hardcoded values require plugin updates to change; auto-memory is designed for AI-remembered facts, not deliberate user config. Shared YAML files are editable, versionless, and readable by any plugin.
- **MCP tool parameter types cause silent rejection**: Some MCP tools require specific JSON types (e.g., `slack_schedule_message` requires `post_at` as integer, not string). A string-typed value is rejected with `invalid_post_at_format` — no auto-coercion. When a skill invokes MCP tools with computed values (bash output, API responses), explicitly document the expected JSON type and add a conversion note. Bash `$(...)` output is always a string — agents must know to pass it as a bare number.
- **State files for cross-project plugins must declare scope**: Plugins loaded via `--plugin-dir` run in the user's CWD, not the plugin directory. State files (`.claude/foo-state.yaml`) resolve to CWD by default, which is correct for project-scoped state. But skills must explicitly document "user's CWD, not `${CLAUDE_PLUGIN_ROOT}`" — otherwise agents may write state into the plugin directory (especially when CWD happens to equal plugin root during development). Add scope annotations in SKILL.md and each sub-skill that reads/writes state.

## Phase 1→1.5 Evolution Decision Gotchas

- **Intent detection is a suggestion, not a decision** — the user always picks the final level. Never auto-select based on detection alone.
- **mixed intent → recommend Full (D1+D2)** — downgrade is easier than upgrade. A plugin that starts with Skip and later needs learning must retrofit the entire structure.
- **Don't backfill history** — when retrofitting `learned-patterns.md` to an existing plugin, start accumulating from now. Do not attempt to reconstruct patterns from past forge runs or git history.
- **Scaffold timing matters** — Evolution Decision runs AFTER Phase 1 scaffold/validate completes, BEFORE Phase 2 TDD begins. The decision determines what Phase 2 step 6 verifies.

### Phase 1.5 B (Doc Self-Iteration) gotchas

- **Probe Config generation is optimistic**: Default `cli` for unknown skills. Don't manually override to `skip` at scaffold time unless you're certain — let the self-correcting loop handle edge cases.
- **Don't scaffold doc-sync for plugins with no docs AND no skills**: Both signals → Skip. A plugin with only hooks or only agents gets Light at most.
- **Reference auto-sync default is `partial`**: When generating Doc Structure, default to `partial` (preserve hand-written content). Only set `yes` for files that are clearly auto-generated (e.g., commands reference tables).
- **Template `{{PLUGIN_NAME}}` replacement is global**: Use exact string replace, not regex. Plugin names with hyphens are fine. Don't replace inside code examples that show the template syntax itself.
- **Post-Sync Hooks section starts empty**: Forge scaffolds an empty Post-Sync Hooks section. Plugin authors add entries manually based on their plugin's needs (e.g., e2e-pipeline adds help topic map update).
