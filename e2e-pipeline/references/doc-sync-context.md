---
plugin: e2e-pipeline
version: 2.3.0
last_sync: 2026-03-20 (Phase 5 self-update)
---

# Doc-Sync Domain Context

Reference file for the doc-sync system. Maps source files to documentation targets,
defines sync levels, probe classification, and style defaults.

## Source Map

### Skills → Doc Targets

| Source | Primary Doc Target | Secondary Doc Target |
|--------|-------------------|---------------------|
| `skills/e2e-dispatch/SKILL.md` | `docs/commands.md` (dispatch row) | `docs/architecture.md` (routing table) |
| `skills/e2e-map/SKILL.md` | `docs/commands.md` (e2e-map row) | `docs/getting-started.md` (step 1) |
| `skills/e2e-flow/SKILL.md` | `docs/commands.md` (e2e-flow row) | `docs/writing-tests.md` (generation guide) |
| `skills/e2e-test/SKILL.md` | `docs/commands.md` (e2e-test row) | `docs/writing-tests.md` (execution guide) |
| `skills/e2e-walkthrough/SKILL.md` | `docs/commands.md` (e2e-walkthrough row) | `docs/recording-evidence.md` (video defaults) |
| `skills/e2e-compile/SKILL.md` | `docs/commands.md` (e2e-compile row) | `docs/ci-integration.md` (compiled scripts) |
| `skills/e2e-skill-ops/SKILL.md` | `docs/commands.md` (e2e-skill-ops row) | `docs/debugging.md` (pipeline debugging) |
| `skills/e2e-help/SKILL.md` | `docs/commands.md` (e2e-help row) | — |
| `skills/e2e-doc-sync/SKILL.md` | `docs/commands.md` (e2e-doc-sync row) | `docs/architecture.md` (doc maintenance) |
| `skills/e2e-pipeline-doc-sync/SKILL.md` | `docs/commands.md` (e2e-pipeline-doc-sync row) | `docs/architecture.md` (doc maintenance) |

### Agents → Doc Targets

| Source | Primary Doc Target |
|--------|-------------------|
| `agents/e2e-mapper.md` | `docs/architecture.md` (Agent table) |
| `agents/e2e-flow-writer.md` | `docs/architecture.md` (Agent table) |
| `agents/e2e-flow-verifier.md` | `docs/architecture.md` (Agent table) |
| `agents/e2e-test-runner.md` | `docs/architecture.md` (Agent table) |
| `agents/e2e-trace-analyzer.md` | `docs/architecture.md` (Agent table) |
| `agents/e2e-media-processor.md` | `docs/architecture.md` (Agent table) |
| `agents/e2e-doc-scanner.md` | `docs/architecture.md` (Agent table) |
| `agents/doc-probe.md` | `docs/architecture.md` (Agent table) |

### Hooks → Doc Targets

| Source | Hook Type | Matcher | Doc Target |
|--------|-----------|---------|-----------|
| `hooks/hooks.json` — SessionStart | SessionStart | `*` | `docs/architecture.md` (hooks section) |
| `hooks/hooks.json` — PreToolUse/Bash (pre-commit) | PreToolUse | Bash | `docs/ci-integration.md` (pre-commit gate) |
| `hooks/hooks.json` — PreToolUse/Bash (stale-check) | PreToolUse | Bash | `docs/ci-integration.md` (stale compiled check) |
| `hooks/hooks.json` — PreToolUse/Write (flow-guard) | PreToolUse | Write | `docs/writing-tests.md` (flow authoring note) |
| `hooks/hooks.json` — PostToolUse/Write (plan-check) | PostToolUse | Write | `docs/architecture.md` (planning integration) |

### References → Doc Targets

| Source | Doc Target |
|--------|-----------|
| `references/commands.md` | `docs/commands.md` (agent-browser CLI reference) |
| `references/common-patterns.md` | `docs/writing-tests.md` + `docs/cross-boundary-testing.md` |
| `references/knowledge-capture.md` | `docs/self-improvement.md` |
| `references/learned-patterns.md` | `docs/debugging.md` (common issues) |
| `references/pr-report-template.md` | `docs/pr-workflow.md` |

## Doc Structure

| Doc File | Purpose | Auto-Sync Level | Notes |
|----------|---------|-----------------|-------|
| `README.md` | Entry point, quick start, plugin overview | **yes** | Regenerable from skill inventory |
| `docs/commands.md` | Command reference with all flags | **yes** | Generated from skill frontmatter + invocation |
| `docs/architecture.md` | Pipeline design, skill→agent model, hooks | **yes** | Generated from directory inventory |
| `docs/getting-started.md` | Install, prerequisites, first test tutorial | **partial** | Has tutorial narrative; command table is syncable |
| `docs/writing-tests.md` | Flow YAML format, element names, expectations | **partial** | Narrative guide; schema section is syncable |
| `docs/multi-site-testing.md` | Cross-site flows, `--site`, `--all-sites` | **partial** | Conceptual guide; flag list is syncable |
| `docs/suites.md` | Grouping flows into test suites | **partial** | Conceptual guide; syntax section is syncable |
| `docs/cross-boundary-testing.md` | Execute/Verify external checkpoints | **partial** | Pattern-heavy; action type schema is syncable |
| `docs/recording-evidence.md` | Video, screenshots, traces, PR evidence | **partial** | Narrative; recording defaults table is syncable |
| `docs/ci-integration.md` | GitHub Actions, quarantine, compiled scripts | **partial** | Workflow examples are project-specific |
| `docs/debugging.md` | Troubleshooting test failures | **partial** | Mix of generated patterns + user-contributed tips |
| `docs/self-improvement.md` | D1/D2 knowledge capture framework | **partial** | Conceptual; dimension table is syncable |
| `docs/pr-workflow.md` | PR comment template, evidence workflow | **partial** | Template is syncable; workflow is narrative |

## Style Guide

Defaults extracted from `agents/e2e-doc-scanner.md` style rules:

1. **Practical over abstract** — lead with a working code/YAML example, explain after
2. **Troubleshooting tables** — Issue | Cause | Fix format for complex topics
3. **Cross-reference** — every doc ends with a Related section linking to sibling docs
4. **Code examples** — use actual plugin commands (`/e2e-test`, `/e2e-flow`) not pseudocode
5. **CTA at the end** — every doc ends with PR link + `/e2e-help --feedback` prompt
6. **Match siblings** — read an existing doc first for tone calibration before writing
7. **No fabrication** — only document what is defined in skill/agent files; uncertain content gets `<!-- TODO: verify -->`

## Probe Config

Classifies each skill for automated doc-sync probing (can the scanner invoke it safely?).

| Skill | Method | Reason |
|-------|--------|--------|
| `e2e-help` | cli | Pure text output, no side effects |
| `e2e-help --list-topics` | cli | Pure text, enumerates available topics |
| `e2e-compile --all` | cli | Compiles flow YAML to scripts, no browser |
| `e2e-doc-sync --check` | cli | Scan-only mode, no file modifications |
| `e2e-dispatch` | skip | Requires user intent routing input |
| `e2e-map` | skip | Requires browser + live application |
| `e2e-flow` | skip | Requires browser + live application |
| `e2e-test` | skip | Requires browser + live application + test data |
| `e2e-walkthrough` | skip | Requires browser + live application |
| `e2e-skill-ops` | skip | Requires failure context or specific debug target |
| `e2e-pipeline-doc-sync --check` | cli | Report-only mode, no writes, MCP graceful degradation |
| `e2e-pipeline-doc-sync` | skip | Full sync modifies files + dispatches agents |

## Post-Sync Hooks

Actions to run after doc-sync writes documentation updates:

1. **Update e2e-help topic mapping** — if new docs were created, add entries to
   `skills/e2e-help/SKILL.md` Phase 3 topic-to-doc mapping table
2. **Check feedback log** — read `.claude/e2e/reports/feedback-log.md` (if exists)
   for user-reported gaps related to the updated docs
3. **Verify dispatch routing** — confirm `skills/e2e-dispatch/SKILL.md` routing table
   includes any newly added skills
4. **Update CLAUDE.md counts** — if skills or agents were added/removed, update the
   Architecture section skill/agent counts in `CLAUDE.md`
5. **Sync README docs table** — if new docs were created, add row to `README.md`
   documentation table
