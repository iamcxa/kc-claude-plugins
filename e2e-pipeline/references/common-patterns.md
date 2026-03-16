# Common Browser Testing Patterns

Patterns and gotchas for E2E testing agents. For project-specific patterns, check `<project>/.claude/skills/agent-browser/references/`.

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

## React Native Web (Expo)

- Text elements render TWICE in DOM (nth=0 hidden, nth=1 visible) — use `>> nth=1` for `text=` selectors
- `text=` does substring match — use `text="exact"` with quotes for exact match
- Tab bars get proper `role=tab[name="..."]` attributes — prefer over `text=`
- Multi-row table elements need `>> nth=0` for "at least one exists" assertion

## Repeated Elements (Tables, Lists)

- Multiple matches -> strict mode violation
- Use `>> nth=0` for "at least one exists" check
- Use `>> nth=N` for specific row/item
- Per-row buttons (edit, delete) all share same selector — must use nth or @ref

## Selector Priority (for mapping files)

1. `data-testid` — best stability, explicit test anchor
2. `role=button[name="..."]` — good, accessible, reliable
3. `role=button[name=/pattern/]` — regex partial match
4. `css=[aria-label="..."]` — semantic
5. NEVER use `css=...has-text('...')` — broken in agent-browser, times out

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

E2E runs produce large binary artifacts (webm, mp4, trace.zip) that should NOT be committed. Before writing any of these files, ensure the project's `.gitignore` includes rules for them.

**Patterns to add** (if missing):

```
# E2E pipeline artifacts (large binary files)
e2e-reports/**/*.webm
e2e-reports/**/*.mp4
e2e-reports/**/trace.zip
```

**Check & append** (idempotent — safe to run multiple times):

```bash
PROJ_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
if [ -f "$PROJ_ROOT/.gitignore" ]; then
  if ! grep -q 'e2e-reports/\*\*/\*.webm' "$PROJ_ROOT/.gitignore" 2>/dev/null; then
    printf '\n# E2E pipeline artifacts (large binary files)\ne2e-reports/**/*.webm\ne2e-reports/**/*.mp4\ne2e-reports/**/trace.zip\n' >> "$PROJ_ROOT/.gitignore"
  fi
else
  printf '# E2E pipeline artifacts (large binary files)\ne2e-reports/**/*.webm\ne2e-reports/**/*.mp4\ne2e-reports/**/trace.zip\n' > "$PROJ_ROOT/.gitignore"
fi
```

Run this **once per session**, during the setup phase (after `mkdir -p` for `report_dir`). If `.gitignore` already has the patterns, the check is a no-op.

## Trace Analysis

- `trace.zip` contains: `trace.network` (JSONL HAR), `trace.trace` (JSONL events), `resources/` (response bodies)
- View interactively: `npx playwright show-trace trace.zip`
- Response bodies in `resources/` are SHA1-referenced files (`.dat` extension)
- Screencast frames in `resources/` use full filename as SHA1 (e.g., `page@xxx-timestamp.jpeg`). Use `frameSwapWallTime` (wall clock ms) for duration, NOT `timestamp` (monotonic).
- Filter trace.network for `status >= 400` to find API failures
- Filter trace.trace for console errors (after noise removal)

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
