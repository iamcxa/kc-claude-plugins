---
name: e2e-flow
description: Use when generating E2E test flows from plans, specs, or PRs, verifying flows in browser, or running smoke tests across all mapped pages. Triggers on "e2e flow", "generate flow", "create flow", "verify flow", "draft flow", "smoke test", "e2e smoke", "write a flow", "produce flow", "validate flow", "flow from plan".
---

# E2E Flow — Generate & Verify

Generate structured E2E flow YAMLs from codebase analysis, then verify them in a real browser with auto-repair. Combines autonomous flow generation (no browser) with adaptive browser validation.

## Pipeline Context

```
/e2e-map       → mapping.yaml        (map UI elements)
/e2e-flow      → flow.yaml + report  (generate & verify)
/e2e-test      → report.md           (replay automated)
/e2e-walkthrough → flow.yaml         (explore interactively)
```

## Invocation

```
/e2e-flow [--from <source>] [--smoke] [--verify-only] [--mapping <name>] [--pr N] [--issue ID] [--no-verify] [--no-video]
```

| Arg | Effect |
|-----|--------|
| (no args) | Generate from current conversation context |
| `--from <file>` | Read a plan file, spec, or requirements doc |
| `--from pr <N>` | Read PR diff via `gh pr diff` |
| `--smoke` | Generate visit-all-pages flow from mapping |
| `--verify-only` | Skip generation, verify an existing flow in browser |
| `--mapping <name>` | Target a specific mapping (skip selection if only one) |
| `--pr N` | Post PR comment with verification results |
| `--issue ID` | Include issue context in report header |
| `--no-verify` | Generate flow only, skip browser verification |
| `--no-video` | Skip video recording during verification |

## Discover Mapping (BLOCKING — must complete before proceeding)

1. Scan `.claude/e2e/mappings/*.yaml`
2. One file → use it. Read `app`, `base_url`, `auth` from the mapping.
3. Multiple files + no `--mapping` → list them (show filename, `app`, `base_url`), ask user which to use.
4. None → stop: "No mappings. Run `/e2e-map` first."
5. Parse failure → report error with line number and stop.

## Phase 0 — Prepare

### Source Parsing

**From file** (`--from <file>`):
- Read the file
- Extract acceptance criteria, user stories, verification steps, UI-facing requirements

**From PR** (`--from pr N`):
- `gh pr diff <N>` + `gh pr view <N> --json title,body`
- Identify changed UI components, routes, user-facing behavior
- Map changes to affected pages in the mapping

**From conversation** (no args):
- Scan recent context for planning artifacts, feature descriptions
- If no clear criteria found → ask: "What should the E2E flow verify?"

**Smoke mode** (`--smoke`): Skip source parsing. Mapping provides everything needed.

**Verify-only** (`--verify-only`):
- List existing flows in `.claude/e2e/flows/`
- Ask user which to verify (or accept flow name as argument)
- Skip to Phase 2

### Codebase Scan

For non-smoke, non-verify-only invocations, scan the codebase to build a `context_summary` for the flow-writer agent. See [reference.md](./reference.md) § Codebase Scan Strategy for exact patterns.

**Summary:** Identify routes → component files → form fields → API endpoints → external service integrations → assemble into `context_summary` text block. Also scan for external service integrations (PostHog, Langfuse, Sentry, webhooks) — see [reference.md](./reference.md) § External Service Discovery. Include matches in the `context_summary` under "External services detected".

**Cap:** Max 20 file reads during scan. Prioritize files matching affected pages.

### Present Plan

Before dispatching agents, present what will happen:

```
Flow generation plan:
  Source: <PR #940 / plan file / conversation>
  Mapping: <app-name> (<N> pages, <M> elements)
  Criteria: <N> acceptance items extracted
  External: <N> service integrations detected
  Estimated steps: ~<N>

Proceed? (y / adjust)
```

## Phase 1 — Generate (dispatch flow-writer agent)

Dispatch `e2e-pipeline:e2e-flow-writer` with:
- `description`: Extracted criteria or feature description
- `mapping_path`: Absolute path to mapping YAML
- `context_summary`: Assembled codebase scan results
- `output_dir`: `.claude/e2e/flows/` absolute path
- `source_text`: Full plan/spec/PR diff text (if `--from` used)
- `smoke_mode`: true if `--smoke`
- `flow_name`: User-specified or auto-generated

See [reference.md](./reference.md) § Agent Dispatch Patterns for exact dispatch message format.

**On return:** Read the generated flow YAML. Present summary to user:

```
Flow generated: .claude/e2e/flows/<name>.yaml
  Steps: N
  Warnings: <count or "none">
  Coverage: <notes>

Proceeding to browser verification...
```

If `--no-verify` → skip to Phase 3.

## Phase 2 — Verify (dispatch flow-verifier + trace-analyzer)

### 2a. Pre-flight

```bash
agent-browser --version
curl -s -o /dev/null -w "%{http_code}" <base_url>
ls ~/.agent-browser/<app>/ 2>/dev/null
```

Dev server must be running. Auth profile should exist (run `/e2e-map` or `/e2e-walkthrough` first to create one).

### 2b. Dispatch flow-verifier

Dispatch `e2e-pipeline:e2e-flow-verifier` with:
- `flow_path`: Path to generated (or existing) flow YAML
- `mapping_path`: Path to mapping YAML
- `auth_profile`: `~/.agent-browser/<app>/`
- `base_url`: From mapping
- `app`: From mapping
- `report_dir`: `e2e-reports/<timestamp>/`
- `record`: `true` (unless `--no-video`)

See [reference.md](./reference.md) § Agent Dispatch Patterns for exact format.

### 2c. Dispatch trace-analyzer

After verifier returns, if `trace_path` is present:

Dispatch `e2e-pipeline:e2e-trace-analyzer` with:
- `trace_path`: From verifier output
- `report_dir`: Same as verifier
- `step_log_path`: From verifier output (if present)

### 2d. Process results

Merge verifier output + trace analysis:
- Corrections applied (repair/adapt/enrich counts)
- Unfixable issues
- Checkpoint results (external execution/verification pass/fail/skip)
- API failures and console errors from trace
- Video path

## Phase 3 — Present Results

### Summary

```
E2E Flow: <flow-name>
Status: <PASS ✅ | PARTIAL ⚠️ | FAIL ❌>
─────────────────────────────
Steps:       N (M original + K inserted)
Corrections: N (R repair, A adapt, E enrich)
Unfixable:   N
Checkpoints: N pass, M fail, K skip
Trace:       N API failures, M console errors
─────────────────────────────
Flow:    .claude/e2e/flows/<name>.yaml
Report:  e2e-reports/<ts>/report.md
Video:   e2e-reports/<ts>/video.mp4

{if corrections}
Corrections applied:
  - step-3: selector repair (add_btn → add_connection_button)
  - step-3.1: [auto-inserted] confirmation dialog
{endif}

{if unfixable}
Unfixable issues:
  - step-7: Element not found (export feature not implemented?)
{endif}

{if checkpoint_results}
Checkpoint results:
  - trigger-sessions: PASS (cli: recce-cloud run ×3, exit 0)
  - verify-posthog: SKIP (POSTHOG_API_KEY not set)
{endif}
```

### PR Posting (if `--pr`)

Ask user to confirm, then:
1. Commit screenshots + video to branch
2. Post `pr-summary.md` as PR comment via `gh pr comment`

### Next Steps (always shown)

```
Next steps:
- `/e2e-test <flow-name>` — replay this flow automatically
{if corrections}
- `/e2e-flow --verify-only <flow-name>` — re-verify after fixing issues
{endif}
{if unfixable}
- `/e2e-map --page <page>` — re-scan pages with missing elements
{endif}
- `/e2e-walkthrough` — explore interactively
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Running verify without dev server | Pre-flight checks catch this — but verify base_url is accessible |
| Element names not matching mapping | Flow-writer validates against mapping. Manual edits can drift — re-run `/e2e-flow` |
| Smoke test on app with dynamic URLs | Smoke auto-skips pages with `${id}` parameters. This is correct behavior, not a bug. |
| Skipping trace analysis | Always dispatch trace-analyzer after verifier — even on PASS. Silent API failures are invisible otherwise. |
| Re-dispatching verifier for minor fixes | Verifier does its own repair loop (2 rounds max). If it returns PARTIAL, the remaining issues are genuinely unfixable by automation. |
| Generating flow without mapping | Mapping must exist first. `/e2e-map` before `/e2e-flow`. |
| Bypassing flow-writer for cross-boundary flows | Always dispatch flow-writer — it supports `Execute external` and `Verify external` steps for non-browser actions (CLI, API, analytics). Runner limits ≠ writer limits. Never hand-write flows to avoid the agent. |
