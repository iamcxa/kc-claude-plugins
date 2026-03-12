---
name: e2e-test
description: Use when running browser E2E tests against web apps — executing flow files, running smoke suites, testing specific features, recording test runs with video, or batch-testing across sites. Triggers on "run e2e", "browser test", "test the flow", "smoke test", "e2e test", "playwright test", "run the suite", "test this feature in browser", "record test run", "e2e video", "test with video".
---

# E2E Test Orchestrator

Resolve browser E2E test flows and dispatch the `e2e-test-runner` agent for execution.

## Invocation

```
/e2e-test [flow-name|--tag tag|--all] [--mapping name] [--all-sites] [--suite name] [--pr NUMBER] [--issue ISSUE-ID] [--video]
```

| Arg | Effect |
|-----|--------|
| `flow-name` | Run a specific flow by filename (without `.yaml`) |
| `--tag smoke` | Run all flows tagged with `smoke` |
| `--all` | Run every flow in `.claude/e2e/flows/` |
| `--mapping name` | Select a specific mapping file (without `.yaml`) |
| `--pr 940` | Post summary as PR comment after execution |
| `--issue DRC-2779` | Include issue context in report header |
| `--all-sites` | Discover all mappings and run applicable flows on each site |
| `--suite name` | Run a specific suite from `.claude/e2e/suites/<name>.yaml` |
| `--video` | Enable screen recording + GIF generation (auto-enabled when `--pr` is used) |

## Prerequisites

1. **agent-browser** installed globally  2. **Dev server running**  3. **Mapping file** in `.claude/e2e/mappings/`  4. **Flow files** in `.claude/e2e/flows/`

## Phase 0 — Resolve Mapping & Flow

### Mapping Resolution Reference

**By filename** (flow `mapping:` field): `mapping: <name>` -> `.claude/e2e/mappings/<name>.yaml`.

**By `app` field** (suite `site:`/`sites:`): scan all `.claude/e2e/mappings/*.yaml`, find `app: <name>`. No match -> error. Multiple -> error (ambiguous).

### Route A: Single-Site (default — no --all-sites, no --suite)

**Discover Mapping:**
1. `--mapping <name>` -> `.claude/e2e/mappings/<name>.yaml`. Not found -> stop.
2. Otherwise scan `*.yaml`: one -> use it; multiple -> ask user; none -> stop with: "No mapping files found in `.claude/e2e/mappings/`. Mappings define selectors and page structure that flows depend on. Run `/e2e-map` first to create one."

**Resolve Flow:**
1. List `.claude/e2e/flows/*.yaml`, filter by args (`--tag`, `--all`, flow-name)
2. **Batch** (`--tag`/`--all`): run ALL matching. Zero matches -> report available tags. Stop.
3. **Single** (explicit name): not found -> stop.
4. **Interactive** (no args): one -> use; multiple -> menu.
5. No flows at all -> suggest `/e2e-walkthrough`. Stop.

**Flow Schema Validation (mandatory):**

| Check | v2 (valid) | v1 (legacy) | Action |
|-------|-----------|-------------|--------|
| Top-level key | `mapping:`/`sites:` | `app:` | SKIP |
| Step identifier | `id:` | `name:` | SKIP |
| Expect entries | strings | objects | SKIP |

If ANY fail: warn with migration guidance (`app:`->`mapping:`, `name:`->`id:`, structured->`grammar strings`). All v1 -> stop.

**Flow/Mapping Mismatch Guard (mandatory):** If the flow has a `mapping:` field, compare it to the resolved mapping filename (without `.yaml`). If they differ, stop: `"Flow '<flow>' targets mapping '<flow.mapping>' but resolved mapping is '<resolved>'. Use '--mapping <flow.mapping>' or fix the flow's 'mapping:' field."` This catches app mismatches before dispatching the agent, avoiding wasted execution time.

**Element Reference Validation (warning-only):** Cross-check element names in `action:`/`expect:` against mapping (`pages.<page>.elements.<name>` or `_global.elements.<name>`). Report mismatches as warnings — do NOT stop execution. Warning format: `⚠ Element not in mapping: "<element>" (step <id>, page <page>). Test may fail at runtime.` Skip validation for `text '...'`, `url contains`, `dialog visible`, and non-element patterns.

**Cross-site flow guard:** If any resolved flow has `sites:`, stop: "Use `--all-sites` or `--suite` for cross-site flows."

**Multi-Flow Execution** (batch mode): alphabetical order, navigate to `base_url` between flows, each gets `$REPORT_DIR/<flow-name>/`, failed flow does NOT abort remaining. If a flow has invalid YAML or fails schema validation, mark it as ERROR in results table with the parse reason, skip it, and continue with remaining flows.

### Route B: `--all-sites`

1. Discover ALL mappings. None -> stop.
2. Discover flows matching filter. None -> stop.
3. Classify: `mapping: X` -> assigned to that mapping; `sites: {...}` -> cross-site; neither -> generic, run once per mapping.
4. Present execution plan for confirmation:
```
Execution plan:
  admin-panel (http://localhost:3001): smoke-navigation (7 steps)
  customer-portal (http://localhost:3000): smoke-navigation (7), project-creation (9)
  cross-site: user-registration (8 steps, admin <-> portal)
Total: 4 runs, 31 steps. Proceed?
```
5. Confirm -> proceed. Order: single-site first (by mapping), then cross-site.

### Route C: `--suite <name>`

1. Read `.claude/e2e/suites/<name>.yaml`. Not found -> list available, stop.
2. Resolve each `runs` entry's flow file.
3. `sites: [...]` -> expand to one run per site, resolved **by `app` field**.
4. `site:` -> resolve **by `app` field**, assign mapping.
5. No site info: flow has `mapping:` -> use it; has `sites:` -> use own def; neither -> error, stop.
6. Pre-scan sessions: collect unique mappings, deduplicate.
7. Present plan (same as Route B). Confirm -> proceed.

## Phase 1 — Dispatch

For each mapping+flow group:

### Prepare Agent Input

| Field | Source |
|-------|--------|
| `flow_path` | Absolute path to resolved flow YAML |
| `mapping_path` | Absolute path to resolved mapping YAML |
| `auth_profile` | `~/.agent-browser/<app>/` (from mapping `app` field) |
| `base_url` | From mapping header |
| `app` | From mapping `app` field |
| `report_dir` | `$(pwd)/e2e-reports/$(date +%Y%m%d-%H%M%S)` (create with `mkdir -p`) |
| `headed` | Always `true` (agent opens browser in headed mode) |
| `record` | `true` when `--video` or `--pr` is present, otherwise `false` |
| `suite_context` | Set to `true` when dispatching via `--all-sites` or `--suite` (enables multi-session with `--session <app>`) |

### Dispatch

```
Agent(subagent_type="e2e-test-runner"):
  "Execute E2E flow:
   flow_path: <path>  mapping_path: <path>  auth_profile: <path>
   base_url: <url>  app: <name>  report_dir: <path>  headed: true
   record: true              # only when --video or --pr
   suite_context: true"      # only for --all-sites / --suite
```

Batch mode: dispatch sequentially (session reuse). Multi-site: dispatch per-site groups, always include `suite_context: true`.

### Receive Results

Agent returns: `total_steps, passed, failed, skipped, console_errors, api_failures, report_path, key_findings`.

### Phase 1.5 — Media Post-Processing

After agent returns, if `record` was `true`:

**Generate steps GIF** from per-step screenshots (see `references/commands.md` § GIF Generation for the canonical ffmpeg command). Warn but continue if ffmpeg fails — GIF is optional.

### Phase 1.75 — Trace Analysis

After agent returns (regardless of `record`), dispatch trace analysis:

```
Agent(subagent_type="e2e-trace-analyzer"):
  trace_path: $REPORT_DIR/trace.zip
  report_dir: $REPORT_DIR
```

Agent returns: `api_failures`, `console_errors`, `clean`, `analysis_path`. Merge these counts into the results (they may differ from the test-runner's per-step health counts, as trace analysis covers the full session including background requests).

If `trace.zip` doesn't exist (e.g., trace was never started), skip this phase.

## Phase 2 — Present Results

**Single:** `Test complete: N/M PASS (X console errors, Y API failures) Report: <path> Browser still open.`

If recording was enabled, append:
- `Recording: <path>/full.webm`
- `Video: <path>/test-run.mp4` (1.5x speed, converted by agent)
- `Steps GIF: <path>/steps.gif`

**Batch:**
| Flow | Result | Steps |
|------|--------|-------|
| login-flow | PASS | 7/7 |
| catalog-browse | FAIL | 5/7 |
| bad-format | ERROR | — (invalid YAML) |

**Multi-site:** Per-site summary + total.

**On failures:** Offer "Investigate?", "Keep browser open", "Re-run failed?".

**Mapping staleness:** 0 stale -> nothing; 1-2 -> `/e2e-walkthrough --page`; 3+ -> `/e2e-map --page`.

**PR comment (if --pr):** Write `$REPORT_DIR/pr-summary.md` with:
- Pass/fail summary table
- Steps GIF reference (local path)
- Key findings from trace analysis
- Link to full report

Then: `gh pr comment <PR> --body-file $REPORT_DIR/pr-summary.md`

**Browser handoff:** Only close after human confirms. Multi-site: `agent-browser --session <app> close` for each.

## Flow File Format

```yaml
name: <flow-name>
description: "<what this tests>"
tags: [smoke, feature-x]                     # optional
mapping: <mapping-filename-no-ext>           # -> .claude/e2e/mappings/<name>.yaml

steps:
  - id: <unique-step-id>
    action: "<action string>"                # see syntax table below
    expect:                                  # optional assertions
      - "<element> visible on <page>"
      - "url contains <path>"
      - "text '<text>' on <page>"
      - "network POST /api/items status 201"
      - "no network errors"
      - "no console errors since <step-id>"
    screenshot: true                         # optional (always on failure)
    optional: true                           # skip if element missing
    timeout: 30                              # seconds
    note: "..."                              # context for agent
```

**Action syntax:**
`Click <el> on <page>` | `Click <el>(<p>=<v>) on <page>` | `Fill <el> with '<text>' on <page>` | `Wait for <el> on <page>` | `Navigate to <path>` | `Press <key>` | `Scroll <dir>` | `Verify <el> on <page>` | `Eval '<js>'`

### Cross-Site Flow Format

Uses `sites:` instead of `mapping:` (mutually exclusive). Every step requires `site:`.

```yaml
name: <flow-name>
tags: [cross-site]
sites:
  <alias>:
    mapping: <mapping-filename-no-ext>
variables:
  key: "value"
steps:
  - id: <id>
    site: <alias>
    action: "<action>"
    expect: [...]
```

Validation: `site:` must exist in `sites:`. Same mapping cannot appear under two aliases.

## Suite File Format

```yaml
name: <suite-name>
runs:
  - flow: <name>                    # required
    sites: [a, b]                   # run once per site (resolved by app field)
  - flow: <name>
    site: a                         # run on one site
  - flow: <cross-site-flow>         # uses flow's own sites: definition
```

**Validation:** Flow must exist. `site:`/`sites:` must match mapping `app` fields. Cannot use both `site:` and `sites:`. Cannot override cross-site flow's sites. Generic flow without site info -> error. Duplicate flow+site -> warning.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| v1 flow in batch | Migrate: `app:`->`mapping:`, `name:`->`id:`, structured expects->grammar strings |
| Cross-site in Route A | Use `--all-sites` or `--suite` |
| Missing `site:` in cross-site step | Required on every step |
| Mixing `mapping:` and `sites:` | Mutually exclusive |
| Flows with 20+ steps | Split into 5-10 per flow |
