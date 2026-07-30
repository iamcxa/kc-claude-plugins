# Common Browser Testing Patterns

Patterns and gotchas for E2E testing agents. For project-specific patterns, check `<project>/.claude/skills/agent-browser/references/`.

## Run-Scoped Runtime State and Cleanup

- Declare runtime inputs as `{from_env, sensitive}` under `runtime_values`; do not put secret values in flow YAML or argv.
- Use `value: {runtime_ref: key}` for a sensitive mapped fill. The compiler sends encoded bytes through `agent-browser eval --stdin`.
- Use `type: capture-url-query` with an ASCII `query`, identifier `save_as`, and `validate: uuid`. Capture requires exactly one non-empty value via browser `URLSearchParams.getAll`.
- Reuse only declared/captured names through `runtime_ref`. Ordered `finally` HTTP steps must cancel then read back state when cleanup is authoritative.
- `finally` always runs, records into the same metrics/JUnit arrays, and overrides success when cleanup or readback fails.

## Environment Setup

- **PATH**: `agent-browser` is installed globally via npm at `~/.npm-global/bin/`. After context reset or in subagent contexts, this path may not be in `$PATH`. Always verify availability before first use:
  ```bash
  command -v agent-browser >/dev/null 2>&1 || export PATH="$HOME/.npm-global/bin:$PATH"
  ```
- Run this check at the start of any agent or skill that calls `agent-browser` CLI commands.

## SPA Navigation

- After `open <url>`, always `wait --load networkidle` before snapshot
- Client-side routing may not trigger network activity — verify URL after wait
- Some SPAs use infinite polling (websocket/SSE) — networkidle may hang. Use element wait as fallback
- Auth-protected apps redirect to login on first load — 3xx is normal, check URL after wait

## Authentication

- Auth profiles persist in `~/.agent-browser/<app>/`
- Persistent auth remains the default when a flow omits `auth_mode`.
- `auth_mode: flow-managed` means flow steps own authentication. The e2e-test
  runtime prepares a previously absent profile under its managed root for every
  replay, verifies Chrome bound to it, skips setup auth/auto-login, and cleans it
  after evidence capture.
- The canonical `~/.agent-browser/<app>/` profile is not opened in flow-managed
  mode, so it must remain unchanged. Runtime preparation records its recursive byte digest and cleanup compares
  the digest; a change is reported as a fail-closed lifecycle error.
- Never delete an arbitrary temporary-looking profile. Only
  `cleanup-flow-managed-profile` may remove a profile with matching run/app/path
  lifecycle state.
- Profile MISSING on first run — open `--headed`, human logs in manually
- Verify auth: `get url` + check against known signin path (substring check)
- Auth expired: DON'T close browser — user re-logs in existing `--headed` window
- Clear auth state: `eval "localStorage.clear(); sessionStorage.clear();"` then `open <base_url>`
- If mapping has `auth.type: none` — skip all auth checks, profile auto-creates on first open
- **`--profile` daemon gotcha**: `--profile` only takes effect when starting a NEW daemon. If a daemon is already running (from a prior command without `--profile`), the flag is silently ignored. Fix: `agent-browser close` → wait 3-5s for full exit → then `--profile` open.
- **SingletonLock after force-kill**: Force-killing chrome leaves `SingletonLock`/`SingletonCookie`/`SingletonSocket` in the profile dir. Remove with `rm -f ~/.agent-browser/<app>/Singleton*` before re-opening.

## Ant Design Components

- **Select**: click `.ant-select` -> wait `.ant-select-dropdown` -> snapshot scoped to dropdown -> click option @ref
- **Modal**: wait `.ant-modal` -> snapshot scoped to `.ant-modal` -> interact within modal
- **Table**: snapshot scoped to `.ant-table` to reduce noise (10+ rows = 100+ @refs)
- **Segmented control**: CSS-hidden radio inputs. `is visible` returns false. Verify via snapshot a11y tree instead
- **Popover/Tooltip**: wait for `.ant-popover` after hover trigger
- **`Input.Password` drops `name` attribute**: `Input.Password` doesn't pass `name` to inner `<input>`. Use `input[type="password"]` instead of `input[name="password"]`

## React Controlled Input Gotchas

- **React 18 `_valueTracker` suppresses `nativeInputValueSetter` onChange**: Setting value via `nativeInputValueSetter.call(el, value)` works at DOM level, but React's internal `_valueTracker` can suppress the `change` event if tracked value matches. Fix: clear tracker before dispatching — `const t=el._valueTracker; if(t) t.setValue('');`. Also `el.focus()` before setting value. Silent failure: no error, form submits with empty values.
- **Wrap consecutive `eval` calls in IIFEs**: `agent-browser eval` calls share global JS scope. Redeclaring `const`/`let` across calls causes SyntaxError. Always use `(()=>{...})()`.

## React Native Web (Expo)

- Text elements render TWICE in DOM (nth=0 hidden, nth=1 visible) — use `:nth-of-type(2)` CSS pseudo or `find text "<v>"` subcommand; `>> nth=1` is BANNED (BANNED — see e2e-pipeline/scripts/lint-mapping.sh)
- `text=` does substring match — use `find text "<v>"` subcommand form for reliable matching
- Tab bars get proper role attributes — use `[role="tab"][aria-label="..."]` CSS attribute selector (Cand 2, canonical since PR #8); do NOT emit `find role tab --name "..."` as a `selector:` value — that is a subcommand chain, not a selector string
- Multi-row table elements need `:nth-of-type(1)` for "at least one exists" assertion; `>> nth=0` is BANNED (BANNED — see e2e-pipeline/scripts/lint-mapping.sh)

## Repeated Elements (Tables, Lists)

- Multiple matches -> strict mode violation
- Use `:nth-of-type(1)` CSS pseudo for "at least one exists" check; `>> nth=0` is BANNED (BANNED — see e2e-pipeline/scripts/lint-mapping.sh)
- Use `:nth-of-type(N)` for specific row/item; `>> nth=N` is BANNED
- Per-row buttons (edit, delete) all share same selector — must use `:nth-of-type(N)` or @ref

## Selector Priority (for mapping files)

1. `[data-testid="value"]` — best stability, explicit test anchor
2. `[role="<r>"][aria-label="<v>"]` — CSS attribute selector (Cand 2, canonical since PR #8); e.g., `[role="button"][aria-label="Submit"]`
3. `[role="<r>"]` — role only; combine with `:nth-of-type(N)` if repeated
4. `[aria-label="<v>"]` — when role isn't stable
5. NEVER use `css=...has-text('...')` — broken in agent-browser, times out
6. BANNED: `role=<r>[name="<v>"]` Playwright attr syntax → use `[role="<r>"][aria-label="<v>"]` (BANNED — see e2e-pipeline/scripts/lint-mapping.sh)
7. BANNED: ` >> nth=N` Playwright nth chord → use `:nth-of-type(N)` CSS pseudo
8. BANNED: bare `text=<v>` at selector start → use `find text "<v>"` subcommand
9. DEPRECATED as `selector:` value: `find role <r> --name "<v>"` — subcommand chain, not selector grammar (PR #8 Copilot review; see design.md addendum)

**Regex selector note**: Former form `find role <r> --name "/<pattern>/"` with regex partial match is also DEPRECATED as a `selector:` value (same reason — subcommand chain). For pattern-based matching, use `[aria-label*="prefix"]` (CSS substring attribute selector) or add `data-testid`. Former form `role=X[name=/pattern/]` is BANNED (BANNED — see e2e-pipeline/scripts/lint-mapping.sh).

## Snapshot vs is visible

- Snapshot a11y tree does NOT expose `data-testid` or `aria-label` attributes
- Use `is visible "<selector>"` for DOM-level verification of attribute-based selectors
- Use snapshot for @ref extraction and text/role verification
- `is visible` returns text "true"/"false" but exit code is always 0

## Known Noise (filter before reporting)

- HMR websocket messages (hot module replacement)
- favicon 404 errors
- React DevTools warnings
- Browser extension background requests
- App-specific: check project's `health.known_noise` in mapping files

## Browser Crash / Hang Recovery

- **Detection**: If an `agent-browser` command hangs beyond the step timeout (or 60 seconds default), the browser process may be unresponsive.
- **Recovery sequence**: `agent-browser close` (force-close the context) → re-open with `agent-browser --profile <path> --headed open <url>` → re-authenticate if needed → resume from the failed step.
- **Save partial results**: Before retrying, write whatever report data was collected so far. A partial report is better than no report.
- **Max retries**: Attempt recovery once. If the browser crashes again on the same step, STOP and report: "Browser unresponsive on step `<id>`. Partial results saved to `<report_dir>`."
- **Common causes**: Memory-heavy pages, infinite redirect loops, unresponsive dev server, stale browser profiles.

## Gitignore Housekeeping

E2E runs produce large binary artifacts (webm, mp4, trace.zip, quarantined
trace.invalid-*.zip) that should NOT be committed. Before writing any of these files, ensure the
project's `.gitignore` includes rules for them.

**Patterns to add** (if missing):

```
# E2E pipeline artifacts (large binary files)
.claude/e2e/reports/**/*.webm
.claude/e2e/reports/**/*.mp4
.claude/e2e/reports/**/trace.zip
.claude/e2e/reports/**/trace.invalid-*.zip
```

**Check & append** (idempotent — safe to run multiple times):

```bash
PROJ_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
if [ -f "$PROJ_ROOT/.gitignore" ]; then
  if ! grep -q '.claude/e2e/reports/\*\*/trace.invalid-\*\.zip' "$PROJ_ROOT/.gitignore" 2>/dev/null; then
    printf '\n# E2E pipeline artifacts (large binary files)\n.claude/e2e/reports/**/*.webm\n.claude/e2e/reports/**/*.mp4\n.claude/e2e/reports/**/trace.zip\n.claude/e2e/reports/**/trace.invalid-*.zip\n' >> "$PROJ_ROOT/.gitignore"
  fi
else
  printf '# E2E pipeline artifacts (large binary files)\n.claude/e2e/reports/**/*.webm\n.claude/e2e/reports/**/*.mp4\n.claude/e2e/reports/**/trace.zip\n.claude/e2e/reports/**/trace.invalid-*.zip\n' > "$PROJ_ROOT/.gitignore"
fi
```

Run this **once per session**, during the setup phase (after `mkdir -p` for `report_dir`). If `.gitignore` already has the patterns, the check is a no-op.

## CLI Terminal Recording (for CLI-only flows)

CLI-only cross-boundary flows (no browser steps) use `asciinema` + `agg` for terminal recording instead of browser screenshots + WebM.

### Prerequisites

```bash
# Check and install (one-time)
command -v asciinema >/dev/null 2>&1 || brew install asciinema
command -v agg >/dev/null 2>&1 || brew install agg
```

### Record a CLI execution

```bash
asciinema rec --cols 120 --rows 35 \
  -c "<command to record>" "$REPORT_DIR/recording.cast"
```

- `--cols 120 --rows 35`: fixed terminal dimensions for consistent rendering
- Headless mode (non-interactive shells): produces cast file without TTY — this is normal
- Cast format: JSONL with header + `[timestamp, "o", "data"]` events

### Convert cast → GIF → MP4

```bash
# Cast → GIF (via agg)
agg --cols 120 --rows 35 --speed 2 --theme monokai recording.cast recording.gif

# GIF → MP4 (via ffmpeg)
ffmpeg -y -i recording.gif -movflags faststart -pix_fmt yuv420p \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" recording.mp4
```

- `--speed 2`: 2x playback (terminal output often has long pauses)
- `--theme monokai`: dark background, readable in PR comments
- `scale=trunc(...)`: ensures even dimensions for libx264 compatibility

### Gitignore additions

Add alongside existing browser artifact patterns:

```
.claude/e2e/reports/**/*.cast
.claude/e2e/reports/**/*.gif
```

## Trace Analysis

- `trace.zip` contains: `trace.network` (JSONL HAR), `trace.trace` (JSONL events), `resources/` (response bodies)
- View interactively: `npx playwright show-trace trace.zip`
- Response bodies in `resources/` are SHA1-referenced files (`.dat` extension)
- Screencast frames in `resources/` use full filename as SHA1 (e.g., `page@xxx-timestamp.jpeg`). Use `frameSwapWallTime` (wall clock ms) for duration, NOT `timestamp` (monotonic).
- Filter trace.network for `status >= 400` to find API failures
- Filter trace.trace for console errors (after noise removal)

### Trace finalization failure/recovery contract

All pipeline producers use one executable:

```bash
TRACE_FINALIZER="${CLAUDE_PLUGIN_ROOT}/scripts/finalize-trace.sh"
TRACE_FINALIZER_RC=0
"$TRACE_FINALIZER" \
  --trace-path "$REPORT_DIR/trace.zip" \
  --flow-verdict "$FLOW_VERDICT" \
  --result-file "$REPORT_DIR/trace-finalization.env" ||
  TRACE_FINALIZER_RC=$?
```

For an orchestrator-owned browser runtime, append
`--browser-runtime "$BROWSER_RUNTIME" --browser-run-id "$BROWSER_RUN_ID" --app "$APP"`.
Provide all three fields together. The finalizer passes them as fixed argv to the executable; it
does not accept a compound command string. `team-trace-lifecycle.sh` accepts the same ownership
fields and routes both `trace start` and finalization through that runtime.

- Set `FLOW_VERDICT` from completed application steps first. Never replace it with trace
  infrastructure status.
- The stop attempt is bounded (default 60 seconds; override with
  `E2E_TRACE_STOP_TIMEOUT` or `--timeout`).
- ZIP validation runs under the same process-group watchdog (default 30 seconds; override with
  `E2E_TRACE_VALIDATION_TIMEOUT` or `--validation-timeout`). A timeout kills validator descendants,
  quarantines the artifact, and still writes the result contract.
- A usable artifact must exist, be non-empty, pass the shared Python validator's full ZIP
  read/CRC check, and contain a root-level `trace.trace` or `trace.network` entry that the analyzer
  can consume. Nested-only entries, presence, or exit code 0 alone do not qualify.
- Before any full ZIP read or extraction, central-directory metadata must remain within these
  defaults: 50,000 entries, 2 GiB total uncompressed bytes, 512 MiB per entry, and 1,000:1 maximum
  per-entry compression ratio. Trusted projects may override them with
  `E2E_TRACE_MAX_ENTRIES`, `E2E_TRACE_MAX_TOTAL_UNCOMPRESSED_BYTES`,
  `E2E_TRACE_MAX_ENTRY_UNCOMPRESSED_BYTES`, and `E2E_TRACE_MAX_COMPRESSION_RATIO`; invalid or
  exceeded limits fail closed as `resource_limit_exceeded`.
- Stop timeout/failure triggers one bounded `agent-browser close` recovery attempt (default 15
  seconds). Use `--session <name>` for named sessions.
- Invalid/uncertain artifacts are quarantined under
  `trace.invalid-<reason>-<timestamp>-<pid>.zip` when the destination is writable. Otherwise the
  result contract reports `retained_invalid`; neither disposition is accepted for analysis.
- Dispatch trace analysis only when `analysis_eligible=true`. All other outcomes continue to
  report generation.

`trace-finalization.env` is the report contract:

Treat this as data, not shell code: parse the fixed keys by splitting each line at its first `=`.
Never `source`, `.`, `eval`, or otherwise execute `trace-finalization.env`. The finalizer rejects
CR/LF-bearing paths, sessions, and verdicts and accepts only `PASS`, `PARTIAL`, or `FAIL` verdicts.

| Field | Meaning |
|-------|---------|
| `flow_verdict` | Already-known application flow result |
| `infrastructure_result` | `PASS` only for completed + valid finalization |
| `finalization_status` | `valid`, `timeout`, `stop_failed`, `invalid_artifact`, or pre-trace `dependency_missing` |
| `stop_status`, `stop_exit_code` | `completed`, `timeout`, or `failed` |
| `validation_status` | `valid`, `missing`, `not_regular`, `empty`, `timeout`, `invalid_zip`, `unsafe_archive`, `resource_limit_exceeded`, `missing_playwright_content`, `validator_unavailable` |
| `recovery_status`, `recovery_exit_code` | `not_needed`, `closed`, `timeout`, or `failed` |
| `artifact_disposition`, `artifact_path` | Accepted, quarantined, retained invalid, or missing |
| `analysis_eligible` | The sole dispatch gate for trace analysis |
| `dependency_status` | Present as `missing_python3` when Python preflight fails before tracing |

In `report.md`, record all rows above under **Trace Finalization**. Trace failure is an explicit
infrastructure failure, not evidence that an otherwise observed application flow failed.

## Preconditions (Data Readiness Checks)

Preconditions validate seed data before dispatching browser agents. Executed by the skill in Phase 0 — if any check fails, the agent is never launched.

### psql runner (default)

```yaml
preconditions:
  runner: psql
  env:
    - DATABASE_URL
  checks:
    - query: "SELECT count(*) FROM work_order_tasks WHERE status = 'reviewing'"
      expect: "> 0"
      fail_message: "No tasks in reviewing state — run seed lifecycle first"
    - query: "SELECT count(*) FROM work_order_tasks WHERE jsonb_array_length(audit_template_snapshots) > 0"
      expect: "> 0"
      fail_message: "No tasks with audit snapshots — run `pnpm seed` first"
```

### Supabase MCP runner

```yaml
preconditions:
  runner: supabase
  project: my-project-ref
  checks:
    - query: "SELECT count(*) FROM profiles WHERE role = 'admin'"
      expect: ">= 1"
      fail_message: "No admin users — check seed script"
```

### Site-scoped checks

```yaml
preconditions:
  runner: psql
  env: [DATABASE_URL]
  checks:
    - query: "SELECT count(*) FROM users"
      expect: "> 0"
      fail_message: "No users"
      # No site: field — always checked (global)
    - query: "SELECT count(*) FROM mobile_sessions"
      expect: "> 0"
      fail_message: "No mobile sessions"
      site: mobile    # Only checked when --site mobile or --all-sites iterating mobile
```

### Comparison operators

| Operator | Example | Meaning |
|----------|---------|---------|
| `>` | `"> 0"` | Greater than |
| `>=` | `">= 5"` | Greater than or equal |
| `=` | `"= 1"` | Exact match |
| `!=` | `"!= 0"` | Not equal |

## External Verification Checkpoints

Checkpoint steps (`action: "Verify external"`) let the LLM pause browser automation to verify external service side-effects. The `verify:` block uses semi-structured YAML — service grouping for organization, natural language for the actual checks.

### PostHog Patterns

```yaml
- id: verify-tracking-event
  action: "Verify external"
  description: "After CTA click, verify PostHog received the conversion event"
  wait: 10
  verify:
    posthog:
      - event: button_clicked
        expect: "count > 0 in last 5 minutes"
        properties: [button_name, page, user_id]
      - event: "$pageview"
        expect: "path matches /thank-you"
  on_fail: warn
```

**Walkthrough**: Claude uses PostHog API via curl or MCP.
**Test runner**: Attempts curl to `$POSTHOG_HOST/api/projects/$POSTHOG_PROJECT_ID/events/`. Needs `POSTHOG_API_KEY` env var.

### Langfuse Patterns

```yaml
- id: verify-ai-trace
  action: "Verify external"
  description: "After AI chat response, verify Langfuse recorded the trace"
  wait: 15
  verify:
    langfuse:
      - check: "Recent trace named 'ai-chat' with output"
        expect: "At least one trace within last 5 minutes"
      - check: "Generation with model containing 'claude'"
        expect: "Generation exists in trace, input/output non-empty"
        note: "Check generations endpoint, filter by trace name"
  on_fail: warn
```

**Walkthrough**: Claude uses Langfuse API via curl (Basic auth with `$LANGFUSE_PUBLIC_KEY:$LANGFUSE_SECRET_KEY`).
**Test runner**: Same curl approach. Needs env vars set.

### Custom / Generic Patterns

For any external service — database, Slack, webhooks, email, etc.:

```yaml
- id: verify-db-record
  action: "Verify external"
  description: "After form submission, verify database has the new record"
  wait: 5
  verify:
    custom:
      - check: "Query the orders table for a record created in the last minute"
        expect: "At least one row with status='confirmed'"
      - check: "確認 Slack #alerts channel 收到下單通知"
        expect: "最新訊息包含 order ID"
  on_fail: fail
```

The `check:` field is natural language — the LLM decides how to verify:
- Database → SQL query via MCP or curl to admin API
- Slack → Slack MCP `slack_read_channel`
- Email → check inbox via API
- Webhook → check webhook receiver logs
- Any HTTP endpoint → curl

### Checkpoint Design Guidelines

| Guideline | Reason |
|-----------|--------|
| Always include `description:` | LLM needs context to choose the right tool |
| Set `wait:` based on service latency | PostHog: 5-10s, Langfuse: 10-15s, DB: 3-5s |
| Use `on_fail: warn` for flaky services | External services have propagation delay and intermittent availability |
| Use `on_fail: fail` for critical checks | DB record existence, payment confirmation |
| Use `on_fail: block` sparingly | Only when subsequent steps depend on the checkpoint |
| Group related checks in one step | One checkpoint per integration point, not one per assertion |
| `note:` for edge cases | "May be 0 if fast-path routing bypasses load_skill" |

## External Execution Checkpoints

Execution steps (`action: "Execute external"`) let the LLM pause browser automation to trigger non-browser side-effects. The `execute:` block uses semi-structured YAML — context grouping for organization, commands or natural language for the actual execution.

### CLI Patterns

```yaml
- id: trigger-recce-sessions
  action: "Execute external"
  description: "Run touch-recce-session 3 times to trigger artifact upload threshold"
  execute:
    cli:
      - run: "touch-recce-session"
        repeat: 3
        expect: "exit code 0"
  wait_after: 10
  on_fail: fail
```

**Test runner**: Executes via Bash. Inherits session env vars. `repeat: 3` runs command 3 times sequentially.

### API Trigger Patterns

```yaml
- id: trigger-webhook
  action: "Execute external"
  description: "POST to webhook endpoint to simulate external event"
  execute:
    api:
      - run: "curl -X POST $WEBHOOK_URL -H 'Content-Type: application/json' -d '{\"event\": \"test\"}'"
        expect: "HTTP 200"
  wait_after: 5
  on_fail: fail
```

### Data Seeding Patterns

```yaml
- id: seed-test-data
  action: "Execute external"
  description: "Insert test records before browser verification"
  execute:
    db:
      - run: "Insert 3 test orders with status='pending' into the orders table"
        expect: "3 rows inserted"
  wait_after: 2
  on_fail: fail
```

The `run:` field can be a literal command or natural language — the LLM decides how to execute:
- Literal command → run directly via Bash
- Natural language → interpret and construct the appropriate command
- Unknown/ambiguous → SKIP with note

### Execution Design Guidelines

| Guideline | Reason |
|-----------|--------|
| Always include `description:` | LLM needs context to construct the right command |
| Set `wait_after:` based on backend latency | Give the backend time to process before the next browser step |
| Use `on_fail: fail` (default) for execution | Execution failure usually means the test can't proceed |
| Use `on_fail: warn` for optional setup | Non-critical data seeding that doesn't block the flow |
| Use `repeat:` instead of multiple `run:` entries | For identical commands, `repeat` is cleaner |
| Literal commands over natural language | When you know the exact command, write it — less LLM interpretation needed |

### Combined Flow Example: Browser → CLI → Browser → PostHog

A real-world pattern mixing all three modes — browser actions, CLI execution, and external verification:

```yaml
name: Recce Artifacts Auto Upload
description: "Verify artifacts_auto_uploaded flips after 3 CLI sessions and PostHog event fires"
mapping: recce-cloud
variables:
  project_id: "test-project-001"

steps:
  - id: verify-initial-false
    action: Navigate to /projects/${project_id}/settings
    expect:
      - "text 'artifacts_auto_uploaded: false' on page"

  - id: trigger-recce-sessions
    action: "Execute external"
    description: "Run touch-recce-session 3 times to hit artifact upload threshold"
    execute:
      cli:
        - run: "touch-recce-session"
          repeat: 3
          expect: "exit code 0"
    wait_after: 10
    on_fail: fail

  - id: verify-state-flipped
    action: Navigate to /projects/${project_id}/settings
    timeout: 30
    expect:
      - "text 'artifacts_auto_uploaded: true' on page"

  - id: verify-posthog-funnel
    action: "Verify external"
    description: "Confirm PostHog received the artifacts_auto_uploaded funnel event"
    wait: 15
    verify:
      posthog:
        - event: artifacts_auto_uploaded
          expect: "count > 0 in last 5 minutes"
    on_fail: warn
```

**Pattern**: Browser (verify precondition) → Execute external (trigger) → Browser (verify postcondition) → Verify external (confirm side-effect). The `wait_after: 10` on the execution step gives the backend time to process before the next browser check.
