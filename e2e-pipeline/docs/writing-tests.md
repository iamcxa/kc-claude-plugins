# Writing Tests

Tests in this pipeline are written in natural language, not code. You describe *what* to do, not *how* to locate elements.

## Step 1: Map the UI

```
/e2e-map
```

The mapper agent opens your app, explores every page, and produces a mapping YAML with semantic element names:

```yaml
# .claude/e2e/mappings/my-app.yaml
pages:
  login:
    url_pattern: "/login"
    elements:
      email_input: { selector: "[data-testid='email']" }
      password_input: { selector: "[data-testid='password']" }
      submit_button: { selector: "button[role='button'][name='Sign In']" }
  dashboard:
    url_pattern: "/dashboard"
    elements:
      welcome_text: { selector: "[data-testid='welcome']" }
```

## Step 2: Generate or write a flow

**Automated** — generate from a plan, spec, or PR:
```
/e2e-flow --from <plan.md>
```
The flow-writer agent reads your codebase and mapping to produce a validated flow YAML, then the flow-verifier agent tests it in a real browser and auto-repairs broken selectors.

**Manual** — write a flow in natural language. Flow files use plain English for actions and expectations:

```yaml
# .claude/e2e/flows/login-flow.yaml
name: Login Flow
mapping: my-app
tags: [smoke]
steps:
  - id: navigate-to-login
    action: Navigate to /login
    expect: email_input visible on login

  - id: fill-credentials
    action: Fill email_input with 'test@example.com' on login
    expect: email_input visible on login

  - id: enter-password
    action: Fill password_input with 'password123' on login

  - id: submit-form
    action: Click submit_button on login
    expect: url contains /dashboard

  - id: verify-dashboard
    action: Verify welcome_text on dashboard
    expect: welcome_text visible on dashboard
```

No CSS selectors, no XPath, no Page Object boilerplate. Just element names from your mapping + human-readable actions.

### Flows with external checkpoints

Some tests need to go beyond the browser — run CLI commands, call APIs, or verify external services. Use `Execute external` (do things) and `Verify external` (check things):

```yaml
# .claude/e2e/flows/recce-artifacts-auto-upload.yaml
name: Recce Artifacts Auto Upload
description: "Verify artifacts_auto_uploaded flips after 3 CLI sessions and PostHog event fires"
mapping: recce-cloud
variables:
  project_id: "test-project-001"

steps:
  # 1. Browser: confirm initial state
  - id: verify-initial-false
    action: Navigate to /projects/${project_id}/settings
    expect:
      - "text 'artifacts_auto_uploaded: false' on page"
    screenshot: true

  # 2. CLI: trigger 3 sessions (outside browser)
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

  # 3. Browser: confirm state flipped
  - id: verify-state-flipped
    action: Navigate to /projects/${project_id}/settings
    timeout: 30
    expect:
      - "text 'artifacts_auto_uploaded: true' on page"
    screenshot: true

  # 4. External: verify PostHog funnel event
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

This flow mixes three modes: browser actions (steps 1, 3), CLI execution (step 2), and external verification (step 4). The test runner handles all three — browser steps use the mapping, `Execute external` steps use Bash, and `Verify external` steps use curl/API calls.

## Step 3: Or, let the walkthrough generate flows for you

If you don't want to write YAML by hand:

```
/e2e-walkthrough
```

Walk through the app interactively. When done, the skill **automatically generates** a flow YAML capturing every step you performed — ready to replay with `/e2e-test`.

## Step 4: Run it

```
/e2e-test login-flow
```

The test runner resolves element names to selectors via the mapping, executes each step, validates expectations, and returns a pass/fail report.

## Step 5: Compile for CI

```
/e2e-compile login-flow
```

Produces `.claude/e2e/compiled/login-flow.sh` — a standalone bash script that runs the same test headlessly without Claude Code. See [CI Integration](ci-integration.md).

---

## When the UI Changes

### Scenario A: UI updated, flow unchanged

The visual design changed (new layout, restyled buttons) but the user journey is the same. Only selectors need updating.

```
/e2e-map --page login
```

This re-explores just the `login` page, updates selectors in the mapping, and preserves all other pages. Your existing flow files remain untouched — they reference element *names*, not selectors.

Then re-run:

```
/e2e-test login-flow
```

If a few elements moved but the overall mapping is intact, a scoped walkthrough also works:

```
/e2e-walkthrough --page login
```

This walks the specific page, detects stale selectors, and offers to patch the mapping automatically.

### Scenario B: UI flow entirely redesigned

The user journey itself changed — new pages, different steps, removed features. The old flow YAML no longer matches reality.

1. **Re-map the affected pages** (or the whole app):

   ```
   /e2e-map
   ```

2. **Walk through the new flow** to auto-generate a replacement:

   ```
   /e2e-walkthrough
   ```

   Describe what changed. The skill proposes a walkthrough plan based on the updated mapping. After walking, it generates a new flow YAML.

3. **Delete or archive the old flow**, rename the new one:

   ```bash
   mv .claude/e2e/flows/walkthrough-20260309-login.yaml .claude/e2e/flows/login-flow.yaml
   ```

4. **Re-compile** (if using CI):

   ```
   /e2e-compile login-flow
   ```

5. **Verify**:

   ```
   /e2e-test login-flow
   ```
