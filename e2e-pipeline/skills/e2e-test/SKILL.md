---
name: e2e-test
description: Use when running browser E2E tests — executing flow files, batch-testing across sites, or recording runs with video. Triggers on "run e2e", "e2e test", "browser test", "test with video".
---

# E2E Test Orchestrator

Resolve browser E2E test flows and dispatch the `e2e-test-runner` agent for execution.

## Invocation

```
/e2e-test [flow-name|--tag tag|--all] [--mapping name] [--site alias] [--all-sites] [--suite name] [--pr NUMBER] [--issue ISSUE-ID] [--video] [--no-compile] [--no-teams] [--model MODEL]
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
| `--site alias` | Run only the specified site's steps from a cross-site flow (mutually exclusive with `--all-sites` and `--suite`) |
| `--suite name` | Run a specific suite from `.claude/e2e/suites/<name>.yaml` |
| `--video` | Enable screen recording + GIF generation (auto-enabled when `--pr` is used) |
| `--no-compile` | Skip auto-compile and compiled script run after LLM execution |
| `--no-teams` | Force subagent mode even when Agent Teams is available |
| `--model MODEL` | Override default agent model (e.g., `--model sonnet`). Default: `haiku` for test runners |

## Prerequisites

1. **agent-browser** installed globally  2. **Dev server running**  3. **Mapping file** in `.claude/e2e/mappings/`  4. **Flow files** in `.claude/e2e/flows/`

## Knowledge Bootstrap (before Phase 0)

Read accumulated patterns to inform test execution and result analysis:

```
Read → ${CLAUDE_PLUGIN_ROOT}/references/learned-patterns.md
Read → .claude/e2e-lessons.md (if exists — project-specific E2E lessons)
```

Use loaded patterns to:
- Anticipate known timing/selector issues during result analysis
- Recognize recurring divergence patterns in Phase 1.8
- Avoid re-discovering known flaky patterns

## Phase 0 — Resolve Mapping & Flow

Before dispatching any browser runner, require `python3 --version` to succeed. Python 3 is needed
before tracing because the shared finalizer isolates and terminates the complete trace-stop process
group and validates trace archives. If `trace-finalization.env` is missing or unreadable after a
finalizer invocation, record trace infrastructure failure, skip analysis, and continue report
generation with the application verdict unchanged.

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
| Auth lifecycle | omitted/`persistent` or `flow-managed` | any other `auth_mode` | ERROR |
| Step identifier | `id:` | `name:` | SKIP |
| Expect entries | strings or `{not_automated: "<reason>"}` objects | other objects | SKIP |

The `not_automated` object is valid only when it has exactly one key, `not_automated`, and the value is a non-empty string. Objects carrying `not_automated` plus any other key are v1/legacy input.

If ANY fail: warn with migration guidance (`app:`->`mapping:`, `name:`->`id:`, unsupported structured expects->grammar strings or `not_automated` only when genuinely human-only). All v1 -> stop execution of this flow. **In batch mode**: mark as ERROR in results table with "v1 format" reason, continue with remaining flows (per Multi-Flow Execution rule).

**Auth mode validation (mandatory):** Resolve top-level `auth_mode` before dispatch:

- Omitted or `persistent` → existing persistent-auth behavior.
- `flow-managed` → authentication is executed by flow steps. Do not infer this
  from action text or a login route.
- Any other value → mark the flow ERROR before browser setup.

For a cross-site flow, `auth_mode` applies to every browser site in that flow.
For flow-managed auth, the first browser step must be a non-mutating `Navigate` or
`Verify` step with at least one logged-out expectation (for example login URL plus
login control). Otherwise mark the flow ERROR before dispatch. This creates the
pre-auth checkpoint the runner must pass before any authentication action.

**Flow/Mapping Mismatch Guard (mandatory):** If the flow has a `mapping:` field, compare it to the resolved mapping filename (without `.yaml`). If they differ, stop: `"Flow '<flow>' targets mapping '<flow.mapping>' but resolved mapping is '<resolved>'. Use '--mapping <flow.mapping>' or fix the flow's 'mapping:' field."` This catches app mismatches before dispatching the agent, avoiding wasted execution time.

**Element Reference Validation (warning-only):** Cross-check element names in `action:`/`expect:` against mapping (`pages.<page>.elements.<name>`, any `pages.<name>` with `shared: true`, or `_global.elements.<name>` unless `_global.shared === false`). Report mismatches as warnings — do NOT stop execution. Warning format: `⚠ Element not in mapping: "<element>" (step <id>, page <page>). Test may fail at runtime.` Skip validation for `text '...'`, `url contains`, `dialog visible`, and non-element patterns.

**Cross-site flow guard:** If any resolved flow has `sites:` and none of `--all-sites`, `--suite`, or `--site` is present, stop: "Use `--all-sites`, `--suite`, or `--site <alias>` for cross-site flows."

**`--site` validation (Route A only):** When `--site <alias>` is present:
1. Verify the resolved flow has `sites:`. If not: stop with `"Flow is not a cross-site flow. Remove --site flag."`
2. Verify `--site` is not combined with `--all-sites` or `--suite`. If combined: stop with `"Cannot use --site with --all-sites"` (or `--suite`).
3. Verify `<alias>` exists in `flow.sites` keys. If not: stop with `ERROR: Site "<alias>" not found in flow. Available sites: <comma-separated keys>`
4. **Step filtering**: Keep only steps where `step.site === <alias>`.
5. **Mapping resolution**: Read `flow.sites[<alias>].mapping` → resolve to `.claude/e2e/mappings/<name>.yaml`.
6. Proceed with standard Route A single-site dispatch using the filtered steps and resolved mapping.

### Preconditions Check (all routes)

After flow validation, before agent dispatch. Optional — skip if flow has no `preconditions:` block.

**Schema:**
```yaml
preconditions:
  runner: psql              # "psql" (default) | "supabase"
  env:                      # required when runner: psql
    - DATABASE_URL
  project: my-project-ref   # required when runner: supabase
  checks:
    - query: "SELECT count(*) FROM table"
      expect: "> 0"
      fail_message: "Description of what's missing"
      site: alias           # optional — only checked when site context matches
```

**Execution logic:**

1. Parse `preconditions:` from flow YAML. No block → skip.
2. Resolve runner (default `psql`):
   - **psql**: Read `.env` from project root. Extract vars listed in `env:`. Any missing → stop: `"Missing env var: <name>. Add it to .env"`
   - **supabase**: Verify `project:` field exists. Execute via `execute_sql` MCP tool.
3. Determine site context:
   - Route A with `--site X` → site context = X
   - Route B (`--all-sites`) → run once per site iteration; site context = current alias
   - Route C (`--suite`) → run once per site iteration; site context = current alias
   - Route A without `--site` → site context = none
4. Filter checks:
   - site context = none → run checks WITHOUT `site:` field only
   - site context = X → run global checks (no `site:` field) + checks where `site` === X
5. Execute filtered checks sequentially:
   - **psql**: `psql "$DATABASE_URL" -t -A -c "<query>"` (via Bash). Trim whitespace. Take first line if multi-row.
   - **supabase**: `execute_sql(project, query)` MCP tool.
   - Parse `expect:` → operator (`>`, `>=`, `=`, `!=`) + number.
   - Compare query result against expect.
6. Error handling:
   - psql non-zero exit → treat as failure, show stderr as message.
   - Empty or non-numeric result → failure: `"Query returned non-numeric result: '<value>'. Use aggregate queries (COUNT, SUM, etc.)"`
7. Any check fails → stop:
   ```
   ❌ Precondition failed: <fail_message>
      Query: <query>
      Expected: <expect>, Got: <actual>
   ```
8. All pass → `✅ Preconditions passed (N/N checks)` → proceed to Phase 1.
9. Zero checks after filtering (all checks have `site:` but site context = none) → `ℹ️ Preconditions: 0 checks applicable (all checks are site-specific). Use --site <alias> to run them.` → proceed (not a failure).

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

### Mode selection

> Detection logic: see `references/agent-teams.md` § 1

- **Teams mode**: TeamCreate available AND `--no-teams` not set
- **Subagent mode**: TeamCreate unavailable OR `--no-teams` set

### Prepare Agent Input (both modes)

| Field | Source |
|-------|--------|
| `flow_path` | Absolute path to resolved flow YAML |
| `mapping_path` | Absolute path to resolved mapping YAML |
| `auth_mode` | Flow `auth_mode`, default `persistent` |
| `canonical_auth_profile` | `~/.agent-browser/<app>/` (from mapping `app` field) |
| `ephemeral_auth_profile` | Runtime-prepared path in flow-managed mode; omitted in persistent mode |
| `auth_profile` | Canonical profile in persistent mode; runtime-prepared ephemeral profile in flow-managed mode |
| `auth_profile_freshness` | `persistent-existing` or `verified-absent` |
| `base_url` | From mapping header |
| `app` | From mapping `app` field |
| `report_dir` | `$(pwd)/.claude/e2e/reports/$(date +%Y%m%d-%H%M%S)` (create with `mkdir -p`) |
| `headed` | Always `true` (agent opens browser in headed mode) |
| `video` | `true` when `--video` or `--pr` is present, otherwise `false` |
| `suite_context` | Set to `true` for every multi-site browser runner (`--all-sites`, `--suite`, Scenario C, and Scenario D browser roles); the owned runtime isolates the app session |
| `browser_runtime` | Absolute path to `${CLAUDE_PLUGIN_ROOT}/bin/e2e-browser-runtime.js` |
| `browser_run_id` | One run identity generated before any browser runner dispatch |

Before any multi-site path/session startup, collect aliases and mapping `app` values into separate
Bash arrays and validate both namespaces:

```bash
TRACE_IDENTIFIER_VALIDATOR="${CLAUDE_PLUGIN_ROOT}/scripts/validate-trace-identifiers.sh"
"$TRACE_IDENTIFIER_VALIDATOR" "${SITE_ALIASES[@]}"
"$TRACE_IDENTIFIER_VALIDATOR" "${SITE_APPS[@]}"
```

Do not interpolate or start a session after validation failure. Iterate only with
`"${SITE_ALIASES[@]}"` / `"${SITE_APPS[@]}"`; never flatten identifiers into a scalar word list.

---

### Browser runtime identity (mandatory)

Resolve the shared runtime and generate the run identity exactly once per `/e2e-test`
invocation:

```bash
BROWSER_RUNTIME="${CLAUDE_PLUGIN_ROOT}/bin/e2e-browser-runtime.js"
test -f "$BROWSER_RUNTIME" || {
  echo "Cannot find e2e-browser-runtime.js in the e2e-pipeline plugin." >&2
  exit 1
}
BROWSER_RUN_ID=$(node "$BROWSER_RUNTIME" new-run-id)
```

All browser teammates spawned for this invocation receive the same `browser_run_id`.
Every browser dispatch and browser command also carries the same `browser_runtime` path.
A teammate `RE-RUN` requested inside this invocation keeps that identity. A fresh
`/e2e-test` replay MUST generate a new `browser_run_id`.

### Flow-managed profile preparation

For every logical run whose flow has `auth_mode: flow-managed`, ask the owned runtime
to reserve a profile immediately before dispatch. The runtime enforces that the
canonical profile is `~/.agent-browser/<app>/`, the ephemeral path is below its
managed profile root, and the requested path did not exist:

```bash
CANONICAL_AUTH_PROFILE="$HOME/.agent-browser/<app>"
PROFILE_STATE=$(node "$BROWSER_RUNTIME" \
  --run-id "$BROWSER_RUN_ID" \
  --app "<app>" \
  --auth-mode flow-managed \
  --canonical-profile "$CANONICAL_AUTH_PROFILE" \
  prepare-flow-managed-profile) || exit 1
AUTH_PROFILE=$(node -e \
  'process.stdout.write(JSON.parse(process.argv[1]).profile)' \
  "$PROFILE_STATE") || exit 1
```

Pass `auth_mode: flow-managed`, `canonical_auth_profile`,
`ephemeral_auth_profile: <AUTH_PROFILE>`, `auth_profile: <AUTH_PROFILE>`, and
`auth_profile_freshness: verified-absent` to the runner. The two ephemeral-path
fields must be identical. A profile preparation failure stops that run before
agent dispatch.

Prepare a separate profile for every replay. This includes batch entries, suite
entries, a fresh `/e2e-test` invocation, and a same-invocation Teams `RE-RUN`.
A same-invocation `RE-RUN` prepares a new fresh ephemeral profile.
The browser runtime identity may stay the same for the Teams teammate, but the
old ephemeral profile is closed and cleaned before a new profile is prepared.

### Fresh invocation team reset (mandatory)

A fresh `/e2e-test` invocation MUST NOT reuse an existing `e2e-test` team. Even when
`app`, `auth_profile`, `base_url`, or `report_dir` appear unchanged, including
when `auth_mode` also appears unchanged:

1. If `~/.claude/teams/e2e-test/config.json` exists, send `shutdown_request` to every
   member and wait for each `shutdown_response`.
2. Run `TeamDelete()`.
3. Run `TeamCreate(...)` and spawn new members with the full invocation fields from
   **Prepare Agent Input**, including the new `browser_run_id`.

If shutdown or deletion fails, fall back to subagent mode; never dispatch the new
invocation to stale teammates. Only a same-invocation `RE-RUN` may reuse the current teammates
and browser identity.

### Teams mode — Multi-role parallel testing

> Shared protocol: `references/agent-teams.md` § 2-6

Teams mode spawns persistent runner teammates. Benefits:
- **Per-step results** — lead sees each step's result immediately via SendMessage
- **Multi-role parallel** — different sites/auth profiles run simultaneously
- **Cross-role coordination** — lead orchestrates sequential dependencies between roles
- **Mixed environments** — browser + CLI teammates in the same test session
- **Fail-fast** — on failure, lead can immediately transition to `/e2e-debug` (same browser)

For flow-managed Teams dispatch, profile ownership is command-scoped. Immediately before each new
`EXECUTE_FLOW` or `BEGIN_FLOW`, run `prepare-flow-managed-profile` for that logical run and put the
returned fresh absent path in every auth-profile field for that command. Keep only one active flow
command per browser teammate. Do not send that teammate another flow until its `FLOW COMPLETE` or
`TRACE FINALIZED` receipt reports cleanup `removed`; parallelism is across different teammates,
not two profiles in one teammate. Sequential suite entries assigned to the same app therefore wait
for the prior receipt and each receive a new different fresh profile. A duplicate delivery of the
same active/finalized command replays its stored response and never prepares or adopts again.

#### Scenario Routing (decision tree)

Evaluate conditions in this order (first match wins):

| # | Condition | Scenario |
|---|-----------|----------|
| 1 | Flow has CLI steps (`Execute external`) mixed with browser steps | **D** (Mixed browser + CLI) |
| 2 | Flow has `sites:` (cross-site) | **C** (Cross-site step routing) |
| 3 | `--all-sites` or `--suite` with multiple single-site flows | **B** (Multi-site parallel) |
| 4 | Single flow, single site (default) | **A** (Single-site) |

**Priority rule**: Scenario D takes precedence over C because CLI steps require a `general-purpose` teammate that Scenario C doesn't spawn. A cross-site flow with CLI steps uses Scenario D's runner spawn (browser runners per site + CLI runner) with Scenario C's step-level routing logic.

**Suite with mixed flow types** (`--suite` containing both single-site and cross-site flows): Spawn runners for all unique sites across all flows (union of single-site mappings + cross-site `sites:` entries). Dispatch single-site flows as `EXECUTE_FLOW` to their respective runners (Scenario B pattern). Dispatch cross-site flows with step-level routing (Scenario C pattern). Both patterns coexist within the same team.

#### Scenario A: Single-site, single-flow

One persistent runner teammate.

```
TeamCreate(team_name="e2e-test", description="E2E test execution")

Agent(
  team_name="e2e-test",
  name="runner",
  subagent_type="e2e-pipeline:e2e-test-runner",
  model="haiku",
  prompt="TEAMS MODE. Execute E2E flow.
          flow_path: <path>  mapping_path: <path>  auth_profile: <path>
          auth_mode: <persistent|flow-managed>
          canonical_auth_profile: <canonical path>
          ephemeral_auth_profile: <ephemeral path or omit>
          auth_profile_freshness: <persistent-existing|verified-absent>
          base_url: <url>  app: <name>  report_dir: <path>
          browser_runtime: <absolute path>  browser_run_id: <run id>
          video: <bool>
          Open browser, execute all steps, send FLOW COMPLETE with results.
          Then go idle — browser stays open for potential re-run or debug."
)
```

Wait for `BROWSER_READY` (30s timeout per `references/agent-teams.md` § 4 — applies to startup). If no `BROWSER_READY` within 30s → treat as hard crash, fall back to subagent dispatch.

Runner executes flow → `FLOW COMPLETE` with results.

On failure, persistent mode may offer
`"Investigate with /e2e-debug? (browser is still open)"`. Flow-managed mode has
already closed and cleaned the ephemeral profile; offer report/trace inspection.
On re-run within this invocation:

- Persistent mode:
  `SendMessage(to="runner", message="RE-RUN\nflow_path: <path>\nbrowser_runtime: <absolute path>\nbrowser_run_id: <same run id>\nauth_mode: persistent\ncanonical_auth_profile: <canonical path>\nauth_profile: <same canonical profile>\nauth_profile_freshness: persistent-existing")`
  — navigation may reuse the browser.
- Flow-managed mode: require the prior report to show cleanup `removed`, run
  `prepare-flow-managed-profile` again, then send
  `SendMessage(to="runner", message="RE-RUN\nflow_path: <path>\nbrowser_runtime: <absolute path>\nbrowser_run_id: <same run id>\nauth_mode: flow-managed\ncanonical_auth_profile: <canonical path>\nephemeral_auth_profile: <new path>\nauth_profile: <same new different fresh ephemeral profile>\nauth_profile_freshness: verified-absent")`.
  The runner closes/reopens the owned browser and rejects reuse of the previous
  ephemeral path.

A new `/e2e-test` invocation follows the mandatory team reset above.

#### Scenario B: Multi-site suite / --all-sites (parallel flows)

One teammate per site. Flows dispatched in parallel.

```
TeamCreate(team_name="e2e-test", description="Multi-site E2E suite")

# Spawn one runner per unique site/mapping
for site in sites:
  Agent(
    team_name="e2e-test",
    name="runner-<site.alias>",
    subagent_type="e2e-pipeline:e2e-test-runner",
    model="haiku",
    prompt="TEAMS MODE. Role: <site.alias>.
            auth_profile: <canonical or prepared ephemeral path>
            mapping_path: <site.mapping>
            auth_mode: <persistent|flow-managed>
            canonical_auth_profile: <site canonical auth>
            ephemeral_auth_profile: <ephemeral path or omit>
            auth_profile_freshness: <persistent-existing|verified-absent>
            base_url: <site.base_url>  app: <site.app>
            report_dir: <report_dir>/<site.alias>/
            browser_runtime: <absolute path>  browser_run_id: <same run id>
            video: <bool>
            Wait for EXECUTE_FLOW commands."
  )
```

Wait for all `BROWSER_READY` messages (30s timeout per runner per `references/agent-teams.md` § 4 — applies to startup). Handle `WAITING_FOR_AUTH` per `references/agent-teams.md` § 3. If a runner fails to send `BROWSER_READY` within 30s → mark as crashed, skip flows assigned to it, continue with remaining runners. If ALL runners fail startup → fall back to subagent dispatch entirely.

Then dispatch flows in parallel across different runner teammates. If multiple suite entries map
to the same runner, dispatch them sequentially under the command-scoped profile rule above:

```
SendMessage(to="runner-admin", message="EXECUTE_FLOW\nflow_path: <admin-flow>\nbrowser_runtime: <absolute path>\nbrowser_run_id: <same run id>\nauth_mode: <persistent|flow-managed>\ncanonical_auth_profile: <canonical path>\nephemeral_auth_profile: <ephemeral path or omit>\nauth_profile: <canonical or ephemeral path>\nauth_profile_freshness: <persistent-existing|verified-absent>", summary="admin: smoke-navigation")
SendMessage(to="runner-customer", message="EXECUTE_FLOW\nflow_path: <customer-flow>\nbrowser_runtime: <absolute path>\nbrowser_run_id: <same run id>\nauth_mode: <persistent|flow-managed>\ncanonical_auth_profile: <canonical path>\nephemeral_auth_profile: <ephemeral path or omit>\nauth_profile: <canonical or ephemeral path>\nauth_profile_freshness: <persistent-existing|verified-absent>", summary="customer: booking-flow")
```

Responses arrive asynchronously. Aggregate into combined results table.

#### Scenario C: Cross-site flow (step-level routing)

One teammate per site defined in flow `sites:`. Lead routes each step by `site:` field.

```
# Same multi-runner spawn as Scenario B (one per sites: entry), with suite_context: true.
```

After all runners ready, lead routes steps:

```
FLOW_RUN_ID="<validated unique id for this flow execution>"

# First, for every participating browser runner:
SendMessage(
  to="runner-<site.alias>",
  message="BEGIN_FLOW\nflow_run_id: <flow_run_id>\nbrowser_runtime: <absolute path>\nbrowser_run_id: <browser run id>\nsession: <site.app>\nauth_mode: <persistent|flow-managed>\ncanonical_auth_profile: <canonical path>\nephemeral_auth_profile: <ephemeral path or omit>\nauth_profile: <canonical or ephemeral path>\nauth_profile_freshness: <persistent-existing|verified-absent>\ntrace_path: <report_dir>/<site.alias>/runs/<flow_run_id>/trace.zip\ntrace_finalization_result_path: <report_dir>/<site.alias>/runs/<flow_run_id>/trace-finalization.env",
  summary="<site.alias>: begin <flow_run_id>"
)
# Wait for FLOW READY from every runner before routing any steps.

for step in flow.steps:
  target = f"runner-{step.site}"
  SendMessage(to=target, message="EXECUTE_STEP\nflow_run_id: <flow_run_id>\nbrowser_runtime: <absolute path>\nbrowser_run_id: <same run id>\nauth_mode: <persistent|flow-managed>\ncanonical_auth_profile: <canonical path>\nephemeral_auth_profile: <ephemeral path or omit>\nauth_profile: <canonical or ephemeral path>\nauth_profile_freshness: <persistent-existing|verified-absent>\n{step as YAML}", summary=f"{step.site}: {step.id}")
  # Wait for STEP COMPLETE before next step to SAME site
  # Steps to DIFFERENT site with no data dependency → can dispatch in parallel
```

**Parallel eligibility** (`references/agent-teams.md` § 6):
- Consecutive steps to DIFFERENT sites → dispatch simultaneously
- Steps to SAME site → must be sequential (one browser)
- Steps referencing `{{variable}}` from a prior step → must wait for that step

**Failure handling** (`references/agent-teams.md` § 6 — Failure handling in multi-step routing):
- A step returns `result: FAIL` → **continue dispatching** (collect maximum evidence)
- **Dependency cascade**: scan remaining steps' `context:` for references to the failed step's `data:` keys → mark matched steps as `SKIP` with reason `"dependency failed: <step-id>"`. Do NOT dispatch with empty context.
- **Partial data**: FAIL always triggers cascade regardless of partial data in the response
- Independent steps (no data dependency on the failed step) proceed normally
- Log cascade in the final report: `"Steps skipped due to dependency: <list>"`

**Runner crash** (no response within 30s — see `references/agent-teams.md` § 4):
- If a runner crashes mid-flow, mark ALL remaining steps assigned to that runner as `SKIP` with reason `"runner crashed: <runner-name>"`
- Steps assigned to OTHER runners continue normally (their browsers are unaffected)
- Do NOT attempt to respawn a replacement runner — fall back to subagent dispatch for skipped steps if the user requests a re-run
- Log in final report: `"Runner <name> crashed after step <id>. N steps skipped."`

**Data passing between roles**:
When a step produces data needed by a subsequent cross-site step, the runner includes it in the response:

```
STEP COMPLETE
id: create-order
result: PASS
data:
  order_id: "12345"
  order_url: "/orders/12345"
```

Lead extracts `data:` and includes as `context:` in the next step's command:

```
SendMessage(to="runner-customer",
  message="EXECUTE_STEP\nflow_run_id: <flow_run_id>\nbrowser_runtime: <absolute path>\nbrowser_run_id: <same run id>\nauth_mode: <persistent|flow-managed>\ncanonical_auth_profile: <canonical path>\nephemeral_auth_profile: <ephemeral path or omit>\nauth_profile: <canonical or ephemeral path>\nauth_profile_freshness: <persistent-existing|verified-absent>\nid: verify-order\ncontext:\n  order_id: 12345\naction: Navigate to /orders\nexpect:\n  - text '12345' on orders-list",
  summary="customer: verify-order")
```

**End-of-flow trace/profile finalization (mandatory, exactly once per step-routed browser runner):**

After all `STEP COMPLETE` responses have arrived (and dependency/crash skips are recorded),
calculate the already-known overall application verdict: `PASS` only when no browser/CLI step
failed, otherwise `FAIL`. Then send one finalization command to every successfully started browser
runner participating in this step-routed flow, including a runner whose assigned steps were all
skipped before dispatch:

```
SendMessage(
  to="runner-<site.alias>",
  message="FINALIZE_FLOW\nflow_run_id: <flow_run_id>\nflow_verdict: PASS|FAIL\nbrowser_runtime: <absolute path>\nbrowser_run_id: <browser run id>\nsession: <site.app>\nauth_mode: <persistent|flow-managed>\ncanonical_auth_profile: <canonical path>\nephemeral_auth_profile: <ephemeral path or omit>\nauth_profile: <canonical or ephemeral path>\nauth_profile_freshness: <persistent-existing|verified-absent>\ntrace_path: <report_dir>/<site.alias>/runs/<flow_run_id>/trace.zip\ntrace_finalization_result_path: <report_dir>/<site.alias>/runs/<flow_run_id>/trace-finalization.env",
  summary="<site.alias>: finalize trace and profile"
)
```

The configured runner `report_dir` is `<report_dir>/<site.alias>/`, so each validated
`flow_run_id` has a distinct `runs/<flow_run_id>/` trace and result path. `BEGIN_FLOW` starts a new
named trace. Duplicate begin/finalize delivery for the same ID replays state/result; after one ID
is finalized, a new ID starts a fresh trace. Track `finalization_sent` per runner and run ID. Do not
send `BEGIN_FLOW` or `FINALIZE_FLOW` to runners that use `EXECUTE_FLOW`: that command owns one fresh
start/finalize lifecycle internally. In particular, Scenario B remains `EXECUTE_FLOW`-only and
must not receive either lifecycle command.

Every browser teammate is spawned with `browser_runtime` and `browser_run_id`; repeat both fields
and the complete mode-appropriate auth binding in every `BEGIN_FLOW`, `EXECUTE_STEP`, and
`FINALIZE_FLOW`. They are required ownership data, not a shell command string. The runner passes
runtime identity to the lifecycle helper as separate argv together with `--app <site.app>`.

Wait for `TRACE FINALIZED` from every commanded browser runner before Phase 1.75 trace analysis
aggregation or teardown. The response preserves application, trace infrastructure, and profile
infrastructure verdicts independently. Flow-managed runners invoke owned profile cleanup only
after the shared trace finalizer returns; record canonical integrity, cleanup, and
`profile_retained`. Persistent runners report profile fields `not-applicable`.

Use a 120-second response budget for `FINALIZE_FLOW`, covering the finalizer's default
60-second stop timeout, 15-second recovery timeout, 30-second validation timeout, and handoff
overhead. If no response arrives, do not blindly resend the command; mark trace infrastructure
failed for that runner and do not analyze by path presence. Preserve the application flow verdict.

#### Scenario D: Mixed browser + CLI

Spawn browser runners + a CLI runner (general-purpose agent, not test-runner):

```
Agent(
  team_name="e2e-test",
  name="runner-cli",
  subagent_type="general-purpose",
  prompt="TEAMS MODE. You are a CLI test runner.
          report_dir: <report_dir>/cli/

          STARTUP: Create report_dir with mkdir -p. Then send:
            SendMessage(to='lead', message='CLI_READY\nrole: runner-cli', summary='CLI runner ready')
          Then STOP and wait for commands.

          On EXECUTE_STEP: run the command via Bash, capture stdout/stderr/exit code.
          PASS/FAIL rule: exit code 0 = PASS, non-zero = FAIL. stderr alone does NOT mean FAIL (many CLI tools write progress to stderr).
          Persist output: write stdout to <report_dir>/cli/<step-id>.stdout.txt, stderr to <step-id>.stderr.txt.
          Send STEP COMPLETE with result (include exit_code in data:).

          On shutdown_request: respond with shutdown_response approve=true."
)
```

**CLI runner ready signal**: Wait for `CLI_READY` (analogous to `BROWSER_READY` for browser runners) before dispatching steps. The CLI runner uses `CLI_READY` (not `BROWSER_READY`) since it doesn't open a browser. Same 30s startup timeout applies — if no `CLI_READY` within 30s, treat as hard crash and skip CLI steps.

Lead coordinates: "CLI runner executes `recce run ...`" → "browser runner verifies result appears in UI."

When Scenario D uses step-level routing, apply Scenario C's end-of-flow `FINALIZE_FLOW` handoff
exactly once to each step-routed **browser** runner after all mixed steps finish. Never send
`FINALIZE_FLOW` to `runner-cli`, and never send it to a browser runner that already returned
`FLOW COMPLETE`.

**CLI result contract:**

| Field | Meaning |
|-------|---------|
| `result: PASS` | exit code 0 |
| `result: FAIL` | exit code non-zero |
| `data.exit_code` | raw exit code for the lead's report |
| `data.stdout_path` | path to saved stdout file |
| `data.stderr_path` | path to saved stderr file (if non-empty) |

#### Teams mode: Teardown

> See `references/agent-teams.md` § 2 (Teardown)

After all results collected and presented: shutdown all runners → `TeamDelete()`.
For a persistent single-flow run, keep runners alive if the user might re-run or
debug; teardown on explicit close. A flow-managed runner may stay idle only after
cleanup and can accept a new prepared profile for re-run, but it has no browser to
hand off for debugging.

#### Teams mode: Result aggregation

Collect `FLOW COMPLETE` or `STEP COMPLETE` messages from all runners. For step-routed browser
runners, also collect every `TRACE FINALIZED` response before proceeding. Build the same result
structure as subagent mode (total_steps, passed, failed, etc.) plus one trace-finalization contract
per browser runner.

**Mixed flow handling**: CLI step results are aggregated alongside browser step results in the same report. CLI steps show `exit_code` and `stdout_path` instead of screenshots. The final results table includes a `Runner` column to distinguish browser vs CLI steps:

```
| Step | Runner | Result | Details |
|------|--------|--------|---------|
| create-order | runner-admin | PASS | screenshot: step-01.png |
| run-pipeline | runner-cli | PASS | exit: 0, stdout: cli/run-pipeline.stdout.txt |
| verify-result | runner-web | PASS | screenshot: step-03.png |
```

Proceed to Phase 1.5 as normal.

---

### Subagent mode (original behavior)

#### Dispatch

```
Agent(subagent_type="e2e-test-runner", model="haiku"):  # override with --model if provided
  "Execute E2E flow:
   flow_path: <path>  mapping_path: <path>  auth_profile: <path>
   auth_mode: <persistent|flow-managed>
   canonical_auth_profile: <canonical path>
   ephemeral_auth_profile: <ephemeral path or omit>
   auth_profile_freshness: <persistent-existing|verified-absent>
   base_url: <url>  app: <name>  report_dir: <path>  headed: true
   browser_runtime: <absolute path>  browser_run_id: <run id>
   video: true               # only when --video or --pr
   suite_context: true"      # only for --all-sites / --suite
```

Batch mode: dispatch sequentially (session reuse). Multi-site: dispatch per-site groups, always include `suite_context: true`.

#### Receive Results

Agent returns: `total_steps, passed, failed, skipped, not_automated, console_errors, api_failures, report_path, key_findings`.

### Phase 1.5 — Media Post-Processing

After agent returns, dispatch media processing.

**Detect flow type**: Classify based on step actions:
- **CLI-only**: ALL steps are `Execute external` or `Verify external` (zero browser steps)
- **Browser-only**: ALL steps are browser actions (zero CLI steps)
- **Mixed** (Teams Scenario D): both browser and CLI steps exist

**Browser-only flow** (default):
```
Agent(subagent_type="e2e-pipeline:e2e-media-processor"):
  "Process media:
   report_dir: <report_dir>
   output_name: test-run"
```

Always dispatch for browser flows when `--video` or `--pr` — GIF, MP4, and thumbnail all come from step screenshots.

**CLI-only flow**:

1. Check prerequisites: `command -v asciinema && command -v agg`. If missing → warn, skip recording.
2. The test-runner agent should have already recorded the primary `Execute external` command with asciinema during execution. If `$REPORT_DIR/recording.cast` exists:
   ```
   Agent(subagent_type="e2e-pipeline:e2e-media-processor"):
     "Process media:
      report_dir: <report_dir>
      cast_path: <report_dir>/recording.cast
      output_name: test-run"
   ```
3. If no cast file exists (prerequisites missing or recording skipped) → skip media processing for CLI flow.

**Mixed flow** (Teams Scenario D):

Process browser and CLI media separately:
1. **Browser media**: dispatch media-processor for browser runner's `report_dir` (screenshots from browser steps)
2. **CLI media**: if `<report_dir>/cli/recording.cast` exists → dispatch media-processor in CLI mode for the CLI runner's output
3. Both media sets are included in the final report. Browser steps get screenshots/video; CLI steps get stdout/stderr text files.

Agent returns: `gif_path`, `gif_frames`, `mp4_path`, `thumbnail_path`, `blank_frames`. Store for Phase 2 results.

### Phase 1.75 — Trace Analysis

After the runner returns, read `trace_finalization_result_path` and confirm its parsed result agrees
with the runner summary. For Scenario C and step-routed Scenario D browser roles, do this
independently for every `TRACE FINALIZED` response; CLI runners have no browser trace. Dispatch
trace analysis only under this gate:

```text
trace_analysis_eligible: true
analysis_eligible: true in trace-finalization.env
trace_infrastructure_result: PASS
```

When all three conditions hold, dispatch trace analysis:

```
Agent(subagent_type="e2e-trace-analyzer"):
  trace_path: <trace_path returned by runner>
  report_dir: $REPORT_DIR
```

Agent returns: `api_failures`, `console_errors`, `clean`, `analysis_path`. Merge these counts into the results (they may differ from the test-runner's per-step health counts, as trace analysis covers the full session including background requests).

For multiple step-routed browser runners, dispatch the analyzer once per eligible trace using that
runner's distinct `trace_path` and `report_dir`, then aggregate counts. One ineligible or missing
runner finalization does not suppress analysis for another eligible runner. Never reuse a
`STEP COMPLETE` message as trace eligibility.

For every other result, **Do NOT dispatch the trace-analyzer**. Presence of `trace.zip` is not a
validity signal. Keep the runner's application `flow_verdict` unchanged, surface the independent
trace infrastructure result, and continue to compile/present results. The report must include stop
status/timeout, validation status, recovery status, artifact disposition/path, and analysis
eligibility from `trace-finalization.env`.

## Phase 1.8 -- Auto-Compile and Compiled Run

> Default ON. Skip entirely when `--no-compile` was passed, flow is **CLI-only**
> (all steps are `Execute external` / `Verify external`), or flow declares
> `auth_mode: flow-managed`. The standalone compiler does not yet own the runtime
> profile-freshness/binding/cleanup boundary. Note:
> `"Phase 1.8 skipped — flow-managed auth is not supported by standalone compiled replay."`

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

**Single persistent mode:** `Test complete: N/M PASS, Z not automated (X console errors, Y API failures) Report: <path> Browser still open.`

**Single flow-managed mode:** `Test complete: N/M PASS, Z not automated (X console errors, Y API failures) Report: <path> Ephemeral auth profile cleanup: <removed|failed>.`

If trace finalization failed, append:
`Application flow: <flow_verdict>. Trace infrastructure: FAIL (<finalization_status>;
validation=<validation_status>; recovery=<recovery_status>; artifact=<artifact_disposition> at
<artifact_path>).` Do not convert the application flow result to FAIL solely because trace
infrastructure failed.

If `--video` or `--pr` was used, append:
- `Video: <path>/test-run.mp4` (step-paced, via media agent)
- `Steps GIF: <path>/steps.gif`

**Batch:**
| Flow | Result | Steps |
|------|--------|-------|
| login-flow | PASS | 7/7 |
| catalog-browse | FAIL | 5/7 |
| bad-format | ERROR | — (invalid YAML) |

**Multi-site:** Per-site summary + total.

When present, include `not_automated: N` in single, batch, and multi-site summaries without counting it as passed, failed, or skipped.

**Quick Re-Run:**

Persistent mode, when Phase 1.8 produced a compiled script:

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

Flow-managed mode cannot use the standalone compiled script because it lacks the
owned profile lifecycle. Show:

```text
## Quick Re-Run

`/e2e-test <flow-name> --no-compile`

Each invocation prepares a new absent profile and records binding/cleanup.
```

Include the mode-appropriate Quick Re-Run section in both single-flow results and
the per-flow section of batch results.

**Divergence Report (when Phase 1.8 ran):**

Present the divergence table from Step 4. If 0 diverged steps, show: "Compiled run matches LLM run -- all steps agree."

If diverged steps exist, add recommendation: "Re-run `/e2e-compile --dry-run <flow>` to validate selectors, or update the mapping with a more stable selector."

**On failures:** Persistent mode may offer "Keep browser open". Flow-managed mode
has already cleaned the profile after evidence capture; offer "Inspect report/trace"
and "Re-run with a new fresh profile" instead.

**Mapping staleness:** 0 stale -> nothing; 1-2 -> `/e2e-walkthrough --page`; 3+ -> `/e2e-map --page`.

**PR comment (if --pr):** Write `$REPORT_DIR/pr-summary.md` following the [unified PR report template](../../references/pr-report-template.md).

**e2e-test-specific extensions** (insert between `### Steps` and `### Health`):

1. **Divergence (LLM vs Compiled)** — when Phase 1.8 auto-compile ran:

| Step | LLM | Compiled | Likely Cause |
|------|-----|----------|-------------|
| step-3 | PASS | FAIL | Timing-sensitive selector |
| step-7 | FAIL | PASS | LLM hallucinated failure |

> N diverged steps out of M total

2. **Quick Re-Run**:

Persistent mode with compiled output:
```bash
bash .claude/e2e/compiled/<flow>.sh
```

> Compiled script auto-regenerated. Force recompile: `/e2e-compile <flow>`

Flow-managed mode:

```text
/e2e-test <flow> --no-compile
```

**Footer override:** Persistent compiled output shows the compiled script path.
Flow-managed output shows the `/e2e-test` command because no compiled run exists.

Then: `gh pr comment <PR> --body-file $REPORT_DIR/pr-summary.md`

**Browser handoff:** In persistent mode, only close after human confirms. Multi-site: run
`node "<absolute browser_runtime>" --run-id "<browser_run_id>" --app "<app>" close`
for each app.

Flow-managed mode has no browser handoff after final evidence capture: the runner
closes the owned session and executes `cleanup-flow-managed-profile`. If cleanup
fails, surface the profile path and failure in the result instead of deleting it
with an unowned command.

## Flow File Format

```yaml
name: <flow-name>
description: "<what this tests>"
tags: [smoke, feature-x]                     # optional
mapping: <mapping-filename-no-ext>           # -> .claude/e2e/mappings/<name>.yaml
auth_mode: persistent                        # optional: persistent (default) | flow-managed
preconditions:                               # optional — data readiness checks
  runner: psql
  env: [DATABASE_URL]
  checks:
    - query: "SELECT count(*) FROM users"
      expect: "> 0"
      fail_message: "No users — run seed first"

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
`Click <el> on <page>` | `Click <el>(<p>=<v>) on <page>` | `Fill <el> with '<text>' on <page>` | `Wait for <el> on <page>` | `Navigate to <path>` | `Press <key>` | `Scroll <dir>` | `Verify <el> on <page>` | `Eval '<js>'` | `Verify external` (verify checkpoint) | `Execute external` (execute checkpoint)

### External Checkpoint Steps

**Verify external** — pause browser automation and verify external service side-effects. The LLM uses available tools (MCP, curl, API calls, DB queries) to fulfill each check. See test-runner § 2m.

**Execute external** — pause browser automation and trigger non-browser actions (CLI commands, API calls, scripts, data seeding). The LLM uses Bash to execute commands. See test-runner § 2n.

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

## Phase 3 — Learning

After presenting results, evaluate findings for knowledge capture.

Read → `${CLAUDE_PLUGIN_ROOT}/references/knowledge-capture.md`

### D1 candidates (auto-append)

Scan test results for general patterns:
- Selector strategies that consistently pass/fail (e.g., `[data-testid="value"]` vs `[role="button"][aria-label="..."]` CSS attribute form)
- Divergence patterns between LLM and compiled execution
- Agent-browser behavior discoveries
- Flow design patterns that improve reliability

Before appending, search `${CLAUDE_PLUGIN_ROOT}/references/learned-patterns.md` for existing coverage — if the pattern is already documented (same root cause, even if different wording), skip it.

Auto-append new patterns to `${CLAUDE_PLUGIN_ROOT}/references/learned-patterns.md`. Notify: "Appended pattern: [title]"

### D2 candidates (gated — e2e-test only)

Scan for project-specific patterns that pass the write threshold:
- Recurring timing issues on specific endpoints/pages
- Auth/session patterns unique to this project
- Data dependency requirements for test flows

Apply severity gate + three-question test from `knowledge-capture.md`. Present candidates for user confirmation. Target: `.claude/e2e-lessons.md` or project `CLAUDE.md`.

### Skip conditions

- Zero failures AND zero divergence AND no novel observations → skip Learning
- All findings already in learned-patterns.md → skip (no duplicates)

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| v1 flow in batch | Migrate: `app:`->`mapping:`, `name:`->`id:`, unsupported structured expects->grammar strings or exact `not_automated` objects |
| Cross-site in Route A | Use `--all-sites`, `--suite`, or `--site <alias>` |
| Missing `site:` in cross-site step | Required on every step |
| Mixing `mapping:` and `sites:` | Mutually exclusive |
| Flows with 20+ steps | Split into 5-10 per flow |
| `verify-external` without `verify:` block | `verify:` is required on checkpoint steps |
| `verify-external` with `expect:` at step level | Browser `expect:` doesn't apply — use `expect:` inside `verify:` entries |
| Checkpoint `on_fail: block` on flaky external service | Use `warn` for services with propagation delay or intermittent availability |
| Capturing one-off flake as D2 | Flakes don't pass three-question test — D2 needs recurring patterns |
| Duplicate D1 entry | Search learned-patterns.md before appending |
| Skipping Learning on all-pass | Skip is correct — nothing to learn from clean runs with no novel observations |
