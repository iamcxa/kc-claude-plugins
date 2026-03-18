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
steps:
  # Browser: confirm initial state
  - id: verify-empty-state
    action: Navigate to /dashboard
    expect:
      - "items_table visible on dashboard"
      - "empty_state_cta visible on dashboard"
    screenshot: true

  # CLI: trigger actions outside browser
  - id: trigger-data-load
    action: "Execute external"
    description: "Load data via CLI to populate the dashboard"
    execute:
      cli:
        - run: "my-tool load-batch --name batch-${i}"
          repeat: 3
          expect: "exit code 0"
    wait_after: 5
    on_fail: fail

  # Browser: confirm the change appeared
  - id: verify-data-appeared
    action: Navigate to /dashboard
    expect:
      - "items_table visible on dashboard"
      - "empty_state_cta not visible on dashboard"
    screenshot: true

  # Analytics: verify side effect
  - id: verify-analytics
    action: "Verify external"
    description: "Confirm analytics event was emitted"
    wait: 10
    verify:
      posthog:
        - event: data_batch_loaded
          expect: "Event exists with batch_count=3"
    on_fail: warn
```

This flow mixes three step types: browser actions (steps 1, 3), CLI execution (step 2), and external verification (step 4). The test runner handles all three — browser steps use the mapping, `Execute external` steps run commands, and `Verify external` steps check external services.

For a complete real-world example with environment setup and multi-phase verification, see [Cross-Boundary Testing](cross-boundary-testing.md).

### Cross-site flows

When a test spans multiple apps, use `sites:` instead of `mapping:`:

```yaml
# .claude/e2e/flows/admin-portal-sync.yaml
name: Admin Portal Sync
tags: [cross-site]
sites:
  admin:
    mapping: admin-panel
  portal:
    mapping: customer-portal

steps:
  - id: admin-create-item
    site: admin
    action: Click create_button on items-page
    expect: ["text 'Created' on items-page"]

  - id: portal-verify-item
    site: portal
    action: Navigate to /items
    expect: ["items_table visible on items-page"]
```

Every step requires `site:`. Run with `--all-sites`, `--suite`, or `--site <alias>`.

For the complete guide, see [Multi-Site Testing](multi-site-testing.md). For organizing flows into suites, see [Test Suites](suites.md).

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

---

> **Need help?** `/e2e-help writing-tests` for an interactive guide.
> **Found a better pattern?** [Open a PR](https://github.com/iamcxa/kc-claude-plugins/pulls) to update this doc.
