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
      submit_button: { selector: "[role='button'][aria-label='Sign In']" }
  dashboard:
    url_pattern: "/dashboard"
    elements:
      welcome_text: { selector: "[data-testid='welcome']" }
```

## Step 2: Generate or write a flow

**Automated** -- generate from a plan, spec, or PR:
```
/e2e-flow --from <plan.md>
```
The flow-writer agent reads your codebase and mapping to produce a validated flow YAML, then the flow-verifier agent tests it in a real browser and auto-repairs broken selectors.

**Manual** -- write a flow in natural language. Flow files use plain English for actions and expectations:

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

**Flow write guard**: A PreToolUse hook blocks direct writes to `.claude/e2e/flows/*.yaml`. This prevents accidental hand-editing of flow files -- flows should be generated via `/e2e-flow` (which authorizes its agents via a sentinel file) or `/e2e-walkthrough`. If you need to make a manual edit, the hook warns you and suggests using the appropriate skill instead.

### CLI-only flows (no mapping required)

Flows can also be entirely CLI-based -- all `Execute external` and `Verify external` steps, with no browser interaction. These flows do not need a mapping file. `/e2e-flow` auto-detects CLI-only intent when no mapping exists and your source material describes shell commands or API calls. See [Cross-Boundary Testing -- CLI-Only Flows](cross-boundary-testing.md#cli-only-flows-no-mapping-required) for the full guide.

### Preconditions

Flows can include a `preconditions:` block that validates data readiness before the browser agent launches. If any check fails, the test stops immediately with a clear error message -- no wasted browser time.

```yaml
name: Audit Options
mapping: secha-admin
preconditions:
  runner: psql
  env:
    - DATABASE_URL
  checks:
    - query: "SELECT count(*) FROM work_order_tasks WHERE status = 'reviewing'"
      expect: "> 0"
      fail_message: "No tasks in reviewing state -- run seed lifecycle first"
    - query: "SELECT count(*) FROM profiles WHERE role = 'admin'"
      expect: ">= 1"
      fail_message: "No admin users -- check seed script"
steps:
  # ...
```

**Schema overview:**

| Field | Required | Description |
|-------|----------|-------------|
| `runner` | No | `psql` (default) or `supabase` |
| `env` | When `psql` | Environment variables to read from `.env` (e.g., `DATABASE_URL`) |
| `project` | When `supabase` | Supabase project ref for MCP-based execution |
| `checks` | Yes | List of query/expect pairs |
| `checks[].query` | Yes | SQL query (use aggregates like `COUNT`, `SUM`) |
| `checks[].expect` | Yes | Comparison: `"> 0"`, `">= 5"`, `"= 1"`, `"!= 0"` |
| `checks[].fail_message` | Yes | Human-readable message when check fails |
| `checks[].site` | No | Only check when running this site (for cross-site flows) |

**Runner types:**

| Runner | How it executes | When to use |
|--------|----------------|-------------|
| `psql` | `psql "$DATABASE_URL" -t -A -c "<query>"` via Bash | Local dev with direct DB access |
| `supabase` | `execute_sql` MCP tool | Remote projects, no direct DB connection |

**Supabase runner example:**

```yaml
preconditions:
  runner: supabase
  project: abcdefghijklmnop    # Supabase project ref
  checks:
    - query: "SELECT count(*) FROM auth.users WHERE role = 'admin'"
      expect: ">= 1"
      fail_message: "No admin user in Supabase -- run seed via dashboard"
```

The Supabase runner uses the `execute_sql` MCP tool instead of a local `psql` connection. No `env` field is needed -- the MCP tool handles authentication via the Supabase project ref.

**Expect operators:**

| Operator | Example | Meaning |
|----------|---------|---------|
| `>` | `"> 0"` | Greater than |
| `>=` | `">= 5"` | Greater than or equal |
| `=` | `"= 1"` | Exact match |
| `!=` | `"!= 0"` | Not equal |

**Site-scoped checks** for cross-site flows:

```yaml
preconditions:
  runner: psql
  env: [DATABASE_URL]
  checks:
    - query: "SELECT count(*) FROM users"
      expect: "> 0"
      fail_message: "No users"
      # No site: field -- always checked
    - query: "SELECT count(*) FROM mobile_sessions"
      expect: "> 0"
      fail_message: "No mobile sessions"
      site: mobile    # Only checked when --site mobile or iterating mobile
```

Checks without `site:` run for every site. Checks with `site: X` run only when the current site context matches X.

**Error messages:**

When a precondition fails, the test stops with:

```
Precondition failed: No tasks in reviewing state -- run seed lifecycle first
   Query: SELECT count(*) FROM work_order_tasks WHERE status = 'reviewing'
   Expected: > 0, Got: 0
```

Non-numeric query results and psql connection errors are also caught and reported.

### Flows with external checkpoints

Some tests need to go beyond the browser -- run CLI commands, call APIs, or verify external services. Use `Execute external` (do things) and `Verify external` (check things):

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

This flow mixes three step types: browser actions (steps 1, 3), CLI execution (step 2), and external verification (step 4). The test runner handles all three -- browser steps use the mapping, `Execute external` steps run commands, and `Verify external` steps check external services.

Flows with **zero browser steps** (only `Execute external` and `Verify external`) automatically get terminal recording instead of browser recording. See [Cross-Boundary Testing -- Recording CLI-Only Flows](cross-boundary-testing.md#recording-cli-only-flows).

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

Walk through the app interactively. When done, the skill **automatically generates** a flow YAML capturing every step you performed -- ready to replay with `/e2e-test`.

## Step 4: Run it

```
/e2e-test login-flow
```

The test runner resolves element names to selectors via the mapping, executes each step, validates expectations, and returns a pass/fail report.

## Step 5: Compile for CI

```
/e2e-compile login-flow
```

Produces `.claude/e2e/compiled/login-flow.sh` -- a standalone bash script that runs the same test headlessly without Claude Code. See [CI Integration](ci-integration.md).

---

## When the UI Changes

### Scenario A: UI updated, flow unchanged

The visual design changed (new layout, restyled buttons) but the user journey is the same. Only selectors need updating.

```
/e2e-map --page login
```

This re-explores just the `login` page, updates selectors in the mapping, and preserves all other pages. Your existing flow files remain untouched -- they reference element *names*, not selectors.

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

The user journey itself changed -- new pages, different steps, removed features. The old flow YAML no longer matches reality.

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

## Deterministic mapped visibility

Mapped element visibility is strict by default: the effective DOM selector must
match exactly one raw DOM candidate and that candidate must be
nonzero-layout-visible. A non-CSS `selector` such as `role=` or `text=` needs a
literal `css_selector` so the DOM identity is explicit. When the exact retained
ghost signature is a real application invariant—one rendered candidate plus
only style-visible zero-area extras—an author may opt in to
`retained-zero-rect` after reviewing probe evidence:

```yaml
# file: mappings/visibility-example.yaml
version: 2
app: visibility-example
base_url: https://example.test
pages:
  home:
    url_pattern: /
    elements:
      page_heading:
        selector: 'role=heading[name="Heading"]'
        css_selector: '[data-testid="page-heading"]'
        visibility_policy: retained-zero-rect
```

```yaml
# file: flows/visibility-example.yaml
name: visibility-example
mapping: visibility-example
steps:
  - id: verify-heading
    type: snapshot
    action: Take snapshot
    expect:
      - page_heading visible on home
```

The mapper and verifier may propose that policy but never auto-apply it.
Prefer a unique stable selector when there are hidden-style extras, two
rendered candidates, or distinct responsive/application states.

Reports include the result class, effective selector and policy, match count
and aggregates, attempts/elapsed, and bounded candidate evidence. Positive
assertions retry only `no_match` and `all_non_rendered`. Negative assertions
pass those two states and retry valid visible states. Invalid CSS, browser/probe
errors, and cardinality failures are terminal even for negative assertions; OR
cannot mask a terminal operand. Literal `text '...'` expectations remain
snapshot assertions and are intentionally separate.

## Expect Grammar Reference

Every `expect:` string is matched against an ordered list of regex patterns in
`compiler/resolver.js`. The first pattern that matches wins; a string matching none
of them is a compile error, because it would not produce a runtime assertion.
This table is the canonical reference; no other doc enumerates the full grammar.

For assertions that are intentionally not automatable, use a per-assertion object:

```yaml
expect:
  - not_automated: "Verify the legal disclaimer copy with product counsel."
```

`not_automated` items compile, appear in the compile summary, and never count as
active or verified assertions.

| Form | Resolves to |
|---|---|
| `<element> is visible` | `active` |
| `<element> is visible on <page>` | `element-visible` |
| `<element> visible on <page>` | `element-visible` |
| `<element> visible` | `element-visible` |
| `<element> is not visible on <page>` | `element-not-visible` |
| `<element> not visible on <page>` | `element-not-visible` |
| `<element> is not visible` | `element-not-visible` |
| `<element> not visible` | `element-not-visible` |
| `url does not contain <value>` | `url-not-contains` |
| `url contains <value>` | `url-contains` |
| `text '<value>' not on page` | `text-not-visible` |
| `text "<value>" not visible` | `text-not-visible` |
| `text '<value>' is not visible` (new) | `text-not-visible` |
| `text '<value>' on page` | `text-visible` |
| `text '<value>' is visible` (new) | `text-visible` |
| `text "<value>" visible` | `text-visible` |
| `<elemA> visible or <elemB> visible` | `or-visible` |

For element action and expectation forms, `on <page>` binds resolution to that page.
If the element is not on the stated page, resolution falls back only to shared pages:
pages with `shared: true`, plus the literal `_global` page unless `_global.shared === false`.
Steps that omit the page keep mapping-wide resolution for compatibility.

**Caution:** the cross-site example earlier in this doc ([Step 2](#step-2-generate-or-write-a-flow))
uses `expect: ["text 'Created' on items-page"]`, which reads as if `items-page` were
a page qualifier for the text assertion. It is not, and the effect is stronger than
"the page name is ignored": the `text '<value>' on page` pattern's `on page` is a
fixed literal, not `on <page-name>`, so this exact string matches none of the forms
above and fails compilation. There is no page-scoped text assertion in this grammar;
only the element forms accept a qualifier. Rewrite it to a supported text assertion
such as `text 'Created' on page`, or use an element assertion with an `on <page>`
qualifier when the page binding matters.

## Element Coverage

After compiling flows, you can check how well your tests cover the mapped UI:

```
/e2e-compile --all --coverage
```

This produces `.claude/e2e/coverage/coverage.json` with per-element data:

```json
{
  "login": {
    "email_input": { "verified": 1, "reached": 2, "status": "verified" },
    "password_input": { "verified": 1, "reached": 1, "status": "verified" },
    "forgot_link": { "verified": 0, "reached": 0, "status": "untouched" }
  }
}
```

| Status | Meaning |
|--------|---------|
| `verified` | Element appears in `expect:` assertions -- actively checked |
| `reached` | Element is used in actions (click, fill) but never in expects |
| `untouched` | Element exists in mapping but no flow references it |

**Coverage regression**: When coverage drops between runs, the compiler prints a warning. Use this to catch flows that were removed or narrowed.

**Improving coverage**: Look for `untouched` elements -- these represent UI that no test exercises. Consider adding steps or new flows targeting them.

## Related

- [Commands](commands.md) -- all skill invocations and flags
- [Cross-Boundary Testing](cross-boundary-testing.md) -- `Execute external` / `Verify external` steps, CLI-only flows
- [Multi-Site Testing](multi-site-testing.md) -- cross-site flows with `sites:`
- [PR Workflow](pr-workflow.md) -- posting E2E evidence to pull requests
- [Debugging](debugging.md) -- troubleshooting test failures
- [CI Integration](ci-integration.md) -- running compiled flows in GitHub Actions

---

> **Need help?** `/e2e-help writing-tests` for an interactive guide.
> **Found a better pattern?** [Open a PR](https://github.com/iamcxa/kc-claude-plugins/pulls) to share it.
> **Docs unclear?** Use `/e2e-help --feedback "<description>"` to let us know.
