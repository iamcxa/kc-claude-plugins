# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code plugin (`e2e-pipeline`) that automates browser E2E testing via context-isolating subagents. The pipeline: **Map UI** → **Generate Flows** → **Verify & Test** → **Analyze**.

## Architecture

**Skills** (7) run in main conversation context as thin orchestrators. They handle pre-flight checks, codebase analysis, user interaction, and media post-processing.

**Agents** (5) run as subagents for heavy work, keeping verbose data out of main context:
- `e2e-mapper` — explores pages, generates YAML mappings
- `e2e-flow-writer` — analyzes codebase + mapping to generate flow YAML (no browser)
- `e2e-flow-verifier` — runs flows in browser, auto-repairs selectors/steps, produces reports
- `e2e-test-runner` — executes flow files, validates expectations
- `e2e-trace-analyzer` — parses Playwright trace.zip for API failures and console errors

```
skills/e2e-dispatch/     → router (auth gate + skill selection)
skills/e2e-map/          → mapping orchestrator → dispatches e2e-mapper agent
skills/e2e-test/         → test orchestrator → dispatches e2e-test-runner + trace-analyzer
skills/e2e-walkthrough/  → interactive exploration (main context)
skills/e2e-flow/         → generate & verify flows → dispatches flow-writer + flow-verifier + trace-analyzer
skills/e2e-compile/      → compile flow YAML to standalone bash test scripts (requires npm deps)
skills/e2e-skill-ops/    → meta-skill for debugging/maintaining the pipeline itself
agents/                  → subagent definitions (e2e-mapper, e2e-flow-writer, e2e-flow-verifier, e2e-test-runner, e2e-trace-analyzer)
hooks/                   → E2E pipeline hooks (SessionStart context + pre-commit check)
references/              → agent-browser CLI commands, common browser testing patterns
```

## Data Flow

```
/e2e-map           → .claude/e2e/mappings/<app>.yaml
/e2e-walkthrough   → .claude/e2e/flows/walkthrough-*.yaml + e2e-reports/<ts>/flow-report.md
/e2e-flow          → .claude/e2e/flows/<feature>.yaml + e2e-reports/<ts>/report.md
/e2e-test <flow>   → e2e-reports/<ts>/report.md, trace.zip, screenshots, video
/e2e-compile       → .claude/e2e/compiled/<flow>.sh (standalone bash test scripts)
```

## YAML Format Conventions (v2 only)

**Mapping files** — page names in `kebab-case`, element names in `snake_case`:
```yaml
version: 2
app: <name>
base_url: <url>
pages:
  <kebab-case-page>:
    url_pattern: "/path"
    elements:
      <snake_case_element>:
        selector: 'data-testid="value"'
        description: "..."
```

**Flow files** — use `mapping:` (not `app:`), steps use `id:` (not `name:`):
```yaml
name: <flow-name>
mapping: <app-name>
steps:
  - id: <step-id>
    action: "Click <element> on <page>"
    expect: ["<element> visible on <page>"]
```

Using `app:` or `name:` in steps means v1 format — rejected by the test runner.

## Selector Priority

1. `data-testid="value"` — best stability
2. `role=button[name="..."]` — good semantic match
3. `aria-label="..."` — acceptable
4. Never use `has-text()` — broken in agent-browser, causes timeout

## Key Gotchas

- **`e2e-flow-writer` has no Bash tool**: intentional — it does pure codebase analysis, never opens a browser. Adding Bash would break isolation.
- **`@ref` is ephemeral**: snapshot `@ref` values change on every DOM mutation. Mappings store stable selectors, not `@ref`.
- **`is visible` exit code is always 0**: check stdout text `"true"`/`"false"`, not exit code.
- **React Native Web**: text elements render twice. Use `>> nth=1` for `text=` selectors.
- **Ant Design CSS-hidden inputs**: `is visible` returns false for functional elements. Verify via snapshot a11y tree presence instead.
- **Snapshot doesn't expose `data-testid`/`aria-label`**: use `agent-browser is visible "<selector>"` for attribute-based verification.
- **Don't pass-through what you can execute**: If an agent has the tools to attempt a step (e.g., verifier has Bash → can run CLI commands), it should attempt it best-effort rather than blindly skipping. Silent skip = the user discovers broken commands only at execution time, not verification time. External checkpoint failures in the verifier use `on_fail: warn` override so they never block browser verification.

## Editing Skills and Agents

When modifying skill or agent definitions:
- Skills have a main `SKILL.md` and optional `reference.md` for detailed mechanics
- Cross-reference step numbers between `SKILL.md` (summary) and `reference.md` (details)
- Run the **e2e-skill-ops 5 rules**: search before diagnose, 3-skill impact scan, verify after fix, write back findings, propose (don't ship) SKILL.md changes without review
- Quality findings persist in `e2e-reports/skill-quality-findings.md`

**Removing a skill or agent:**
1. Delete the directory/file
2. Run: `grep -rn "<name>" e2e-pipeline/ --include="*.md" --include="*.json" --include="*.sh" | grep -v skill-quality-findings | grep -v node_modules | grep -v docs/superpowers/`
3. Update every hit — replace with successor or remove
4. Update `skills/e2e-dispatch/SKILL.md` routing table + reroute removed flags to successor
5. Re-run grep to verify zero active references (historical in findings/specs is OK)

## Documentation Maintenance

When adding, removing, or renaming skills or agents, update these files:

1. `README.md` — quick start commands, pipeline summary
2. `docs/commands.md` — command table with all flags
3. `docs/architecture.md` — skill→agent table and plugin file tree
4. `docs/getting-started.md` — step-by-step guide
5. `docs/writing-tests.md` and `docs/recording-evidence.md` — check for stale references
6. `.claude-plugin/plugin.json` — bump version
7. `CLAUDE.md` (this file) — Architecture section counts, directory listing, Recording Defaults table

## Recording Defaults

| Skill | Video Default | Override |
|-------|--------------|----------|
| `/e2e-walkthrough` | ON | `--no-video` |
| `/e2e-flow --verify-only` | ON | `--no-video` |
| `/e2e-test` | OFF | `--video` or `--pr` |
| `/e2e-map` | No recording | — |

## Planning Integration (E2E-First Acceptance)

Enforced by three layers — any planning framework (superpowers, GSD, plan mode, or bare conversation) is covered:

| Layer | Mechanism | When | Strength |
|-------|-----------|------|----------|
| **Upstream** | SessionStart hook | Every session in a project with mappings | Injects reminder into context |
| **Bridge** | `/e2e-flow` skill | During or after planning | Generates structured flow YAML from plan/spec/PR |
| **Downstream** | PreToolUse hook on `git commit` | Every commit in a project with mappings | Warns if no recent E2E report |

**Closed loop:**
```
SessionStart ──→ "E2E infrastructure detected, use /e2e-flow"
     │
     ▼
Planning (any framework)
     │
     ▼
/e2e-flow --from <plan>  ──→  .claude/e2e/flows/<feature>.yaml
     │                         (generates + verifies in browser)
     ▼
/e2e-test <feature>  ──→  e2e-reports/*/report.md
     │                                    ▲
     ▼                                    │ (no flow? create one first)
git commit  ──→  hook checks      /e2e-flow --from <plan>
                                         └→ generates flow → verifies → future /e2e-test
```

**Verification decision**: Draft flow exists → `/e2e-test` (automated, subagent). No flow → `/e2e-flow --from <plan>` (generates + verifies automatically). For interactive exploration → `/e2e-walkthrough`.

**Draft flow template** (for plans that embed acceptance criteria inline):

```yaml
# draft — validate against mapping before use
name: <feature-name>
description: "<what this verifies>"
tags: [acceptance, <feature-tag>]
mapping: <app-name>                    # must match an existing mapping

steps:
  - id: navigate-to-feature
    action: "Navigate to <path>"
    expect:
      - "<key_element> visible on <page>"

  - id: perform-action
    action: "Click <element> on <page>"
    expect:
      - "url contains <expected-path>"
      - "text '<success message>' on <page>"

  # Optional: external execution checkpoint (trigger non-browser actions)
  - id: trigger-side-effect
    action: "Execute external"
    description: "Run <command> to <purpose>"
    execute:
      cli:
        - run: "<command>"
          expect: "exit code 0"
    wait_after: 5
    on_fail: fail

  # Optional: external verification checkpoint (check side-effects)
  - id: verify-side-effect
    action: "Verify external"
    description: "Confirm <service> received the expected event"
    wait: 5
    verify:
      <service>:
        - event: <event_name>
          expect: "count > 0 in last 5 minutes"
    on_fail: warn
```

**Rules for draft flows:**
- Element/page names MUST match the mapping exactly (`snake_case` elements, `kebab-case` pages)
- 5-12 steps — focused acceptance path, not exhaustive coverage
- Every step needs `expect:` — bare navigation is insufficient for acceptance
- `Execute external` for triggering non-browser actions (CLI, API, scripts)
- `Verify external` for checking external service side-effects
- External checkpoints only at real integration boundaries
- Use `/e2e-flow --from <plan>` to generate from plan; manual embedding is fallback

## Compiler Dependencies

The `/e2e-compile` skill uses a Node.js CLI (`bin/e2e-compile.js`) that requires npm packages. Run `npm install` in the plugin directory if `node_modules/` is missing. Dependencies are declared in `package.json`.

## Plugin Runtime Variable

`${CLAUDE_PLUGIN_ROOT}` is set by Claude Code at session start to the plugin's installation directory. Skills and hooks use this to resolve paths to `references/`, `hooks/scripts/`, and `bin/`. It is only available within the plugin context (skills, agents, hooks) — not in user code.

## Git Conventions

Semantic commit prefixes: `feat`, `fix`, `docs`, `chore`. Version follows semver in `.claude-plugin/plugin.json`. After bumping, sync marketplace via `/kc-marketplace-sync`.
