# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code plugin (`e2e-pipeline`) that automates browser E2E testing via context-isolating subagents. The pipeline: **Map UI** → **Walk Through** → **Test** → **Analyze**.

## Architecture

**Skills** (5) run in main conversation context as thin orchestrators. They handle pre-flight checks, codebase analysis, user interaction, and media post-processing.

**Agents** (3) run as subagents for heavy browser work, keeping verbose data out of main context:
- `e2e-mapper` — explores pages, generates YAML mappings
- `e2e-test-runner` — executes flow files, validates expectations
- `e2e-trace-analyzer` — parses Playwright trace.zip for API failures and console errors

```
skills/e2e-dispatch/     → router (auth gate + skill selection)
skills/e2e-map/          → mapping orchestrator → dispatches e2e-mapper agent
skills/e2e-test/         → test orchestrator → dispatches e2e-test-runner + trace-analyzer
skills/e2e-walkthrough/  → interactive exploration (main context, no dedicated agent)
skills/e2e-skill-ops/    → meta-skill for debugging/maintaining the pipeline itself
agents/                  → subagent definitions (e2e-mapper, e2e-test-runner, e2e-trace-analyzer)
references/              → agent-browser CLI commands, common browser testing patterns
```

## Data Flow

```
/e2e-map           → .claude/e2e/mappings/<app>.yaml
/e2e-walkthrough   → .claude/e2e/flows/walkthrough-*.yaml + e2e-reports/<ts>/flow-report.md
/e2e-test <flow>   → e2e-reports/<ts>/report.md, trace.zip, screenshots, video
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

- **`@ref` is ephemeral**: snapshot `@ref` values change on every DOM mutation. Mappings store stable selectors, not `@ref`.
- **`is visible` exit code is always 0**: check stdout text `"true"`/`"false"`, not exit code.
- **React Native Web**: text elements render twice. Use `>> nth=1` for `text=` selectors.
- **Ant Design CSS-hidden inputs**: `is visible` returns false for functional elements. Verify via snapshot a11y tree presence instead.
- **Snapshot doesn't expose `data-testid`/`aria-label`**: use `agent-browser is visible "<selector>"` for attribute-based verification.

## Editing Skills and Agents

When modifying skill or agent definitions:
- Skills have a main `SKILL.md` and optional `reference.md` for detailed mechanics
- Cross-reference step numbers between `SKILL.md` (summary) and `reference.md` (details)
- Run the **e2e-skill-ops 5 rules**: search before diagnose, 3-skill impact scan, verify after fix, write back findings, propose (don't ship) SKILL.md changes without review
- Quality findings persist in `e2e-reports/skill-quality-findings.md`

## Recording Defaults

| Skill | Video Default | Override |
|-------|--------------|----------|
| `/e2e-walkthrough` | ON | `--no-video` |
| `/e2e-test` | OFF | `--video` or `--pr` |
| `/e2e-map` | No recording | — |

## Git Conventions

Semantic commit prefixes: `feat`, `fix`, `docs`, `chore`. Version follows semver in `.claude-plugin/plugin.json`. After bumping, sync marketplace via `/kc-marketplace-sync`.
