---
name: e2e-test
description: Use when running browser E2E tests against web apps — executing flow files, running smoke suites, testing specific features, recording test runs with video, or batch-testing across sites. Triggers on "run e2e", "browser test", "test the flow", "smoke test", "e2e test", "playwright test", "run the suite", "test this feature in browser", "record test run", "e2e video", "test with video".
---

# E2E Test Orchestrator

Resolve browser E2E test flows and dispatch the `e2e-test-runner` agent for execution.

## Invocation

```
/e2e-test [flow-name|--tag tag|--all] [--mapping name] [--all-sites] [--suite name] [--pr NUMBER] [--issue ISSUE-ID] [--video] [--no-compile]
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
| `--no-compile` | Skip auto-compile and compiled script run after LLM execution |

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

## Phase 1.8 -- Auto-Compile and Compiled Run

> Default ON. Skip entirely when `--no-compile` was passed.

After trace analysis, auto-compile and run the same flow as a compiled script to detect divergence between LLM and deterministic execution.

### Step 1: Locate compiler

```bash
COMPILER=$(find ~/.claude/plugins -name "e2e-compile.js" -path "*/e2e-pipeline/bin/*" -print -quit 2>/dev/null)
```

If not found: skip Phase 1.8 with note "Compiler not found -- skipping auto-compile."

### Step 2: Compile the flow

```bash
node "$COMPILER" "$FLOW_NAME" \
  --flows-dir .claude/e2e/flows \
  --mappings-dir .claude/e2e/mappings \
  --output-dir .claude/e2e/compiled
```

If compilation fails: present the error, skip compiled run, note divergence is unavailable.

### Step 3: Run the compiled script

```bash
COMPILED_JUNIT="$REPORT_DIR/compiled-junit.xml"
bash ".claude/e2e/compiled/${FLOW_NAME}.sh" \
  --junit "$COMPILED_JUNIT" \
  --continue-on-error
COMPILED_EXIT=$?
```

Capture exit code. Both pass (0) and fail (non-zero) proceed to divergence analysis.

### Step 4: Divergence analysis (INT-03)

Compare LLM agent results vs compiled script results step-by-step.

**Source data:**
- LLM results: `key_findings` from agent return (natural language per step)
- Compiled results: Parse `$COMPILED_JUNIT` XML for step outcomes (`<testcase>` pass vs `<failure>`)

**Build divergence table:**

| Step | LLM Result | Compiled Result | Status | Likely Cause |
|------|-----------|-----------------|--------|--------------|
| step-id | PASS | PASS | Same | -- |
| step-id | PASS | FAIL | Diverged | Selector may be timing-sensitive |
| step-id | FAIL | PASS | Diverged | LLM may have hallucinated failure |

**Likely cause heuristics:**
- LLM PASS / Compiled FAIL -> "Selector may be timing-sensitive; LLM used snapshot @ref, compiled uses static selector"
- LLM FAIL / Compiled PASS -> "LLM may have hallucinated failure; compiled script is authoritative"
- Both FAIL -> "Genuine bug in app or test"
- Both PASS -> No action needed

**Summary line:** "Divergence: N diverged steps out of M total"

If 0 diverged: "LLM and compiled runs agree on all steps."

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

**Quick Re-Run (always shown after single-flow results):**

```
## Quick Re-Run

To reproduce this test without AI execution:
```bash
bash .claude/e2e/compiled/<flow-name>.sh
```

With full options (continue on error, JUnit output):
```bash
bash .claude/e2e/compiled/<flow-name>.sh --continue-on-error --junit /tmp/junit.xml
```

> Compiled script regenerated automatically. To force recompile: `/e2e-compile <flow-name>`
```

Include the Quick Re-Run section in both single-flow results and in the per-flow section of batch results.

**Divergence Report (when Phase 1.8 ran):**

Present the divergence table from Step 4. If 0 diverged steps, show: "Compiled run matches LLM run -- all steps agree."

If diverged steps exist, add recommendation: "Re-run `/e2e-compile --dry-run <flow>` to validate selectors, or update the mapping with a more stable selector."

**On failures:** Offer "Investigate?", "Keep browser open", "Re-run failed?".

**Mapping staleness:** 0 stale -> nothing; 1-2 -> `/e2e-walkthrough --page`; 3+ -> `/e2e-map --page`.

**PR comment (if --pr):** Write `$REPORT_DIR/pr-summary.md` with:
- Pass/fail summary table
- Steps GIF reference (local path)
- Key findings from trace analysis
- Link to full report
- Replay line: `` > **Replay:** `/e2e-test <flow>` | **Trace:** `npx playwright show-trace <path>` ``

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
`Click <el> on <page>` | `Click <el>(<p>=<v>) on <page>` | `Fill <el> with '<text>' on <page>` | `Wait for <el> on <page>` | `Navigate to <path>` | `Press <key>` | `Scroll <dir>` | `Verify <el> on <page>` | `Eval '<js>'` | `Verify external` (checkpoint)

### External Verification Checkpoint Steps

Steps with `action: "Verify external"` pause browser automation and verify external service side-effects. The LLM uses available tools (MCP, curl, API calls, DB queries) to fulfill each check.

```yaml
  - id: verify-intent-events
    action: "Verify external"
    description: >
      After agent responds, verify PostHog received the intent event
      and Langfuse recorded the classifier trace.
    wait: 10                             # seconds to wait before starting checks
    verify:
      posthog:
        - event: web_agent_support_intent_detected
          expect: "count > 0 in last 5 minutes"
          properties: [email, organizationId, projectId]
          note: "Triggered by support escalation intent"
        - event: web_agent_support_skill_loaded
          expect: "count >= 0"
          note: "May be 0 if fast-path routing bypasses load_skill"
      langfuse:
        - check: "Recent trace with generation containing 'support_escalation'"
          expect: "At least one trace within last 5 minutes"
        - check: "Classifier generation with intent=support_escalation"
          expect: "Generation exists in trace"
      custom:
        - check: "Query orders API for new record"
          expect: "JSON array length > 0"
        - check: "確認 Slack #support channel 收到通知"
          expect: "最新訊息包含 request title"
    on_fail: warn                        # warn (default) | fail | block
```

**Checkpoint fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `action` | Yes | Must be `"Verify external"` |
| `description` | Yes | Why this checkpoint exists (context for LLM) |
| `wait` | No | Seconds to pause before starting checks (default: 5). Allows propagation delay. |
| `verify` | Yes | Service-grouped checks. Keys are service names (`posthog`, `langfuse`, `custom`, or any identifier). |
| `on_fail` | No | `warn` (log + continue, default), `fail` (mark FAIL + continue), `block` (mark FAIL + stop flow) |

**Within each service group**, entries use:

| Field | Description |
|-------|-------------|
| `event:` | Event/trace name to look for (structured hint for PostHog-style services) |
| `check:` | Natural language description of what to verify (for Langfuse-style or custom) |
| `expect:` | Natural language success criteria |
| `properties:` | List of expected property names (hint, not strict validation) |
| `note:` | Context hint for the LLM (edge cases, known exceptions) |

**Execution model:**
- **Walkthrough** (main context): Full tool access — LLM uses MCP, curl, database, Slack, anything needed.
- **Test runner** (subagent): Best-effort via Bash/curl. Complex checks that need MCP → marked SKIP with note.

**Flow schema validation**: `verify-external` steps have no page/element references, so they skip mapping cross-check entirely. They MUST have a `verify:` block — missing `verify:` on a `verify-external` step is a validation error.

**Execution model**: In the test-runner subagent, checkpoints execute best-effort via Bash/curl. Complex checks requiring MCP tools (Slack, database) are marked SKIP. For comprehensive checkpoint verification, use `/e2e-walkthrough --verify` which runs in main context with full tool access. See test-runner agent § 2m for execution details.

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
| `verify-external` without `verify:` block | `verify:` is required on checkpoint steps |
| `verify-external` with `expect:` at step level | Browser `expect:` doesn't apply — use `expect:` inside `verify:` entries |
| Checkpoint `on_fail: block` on flaky external service | Use `warn` for services with propagation delay or intermittent availability |
