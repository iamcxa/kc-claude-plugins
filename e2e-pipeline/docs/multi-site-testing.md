# Multi-Site Testing

Test flows that span multiple web applications — admin panel creates a user, customer portal verifies login. The pipeline supports cross-site flows, per-site filtering, and automatic session isolation.

## When to Use

| Scenario | Approach |
|----------|----------|
| Test a single app | `/e2e-test <flow>` (default) |
| Same test on multiple apps | `/e2e-test --all-sites` or `--suite` |
| Flow crosses apps (A → B → A) | Cross-site flow with `sites:` |
| Run a curated set of flows | `/e2e-test --suite <name>` ([details](suites.md)) |

## Key Concepts

### Sites & Mappings

Each "site" is a web app with its own mapping file:

```
.claude/e2e/mappings/
├── admin-panel.yaml       # app: admin-panel, base_url: http://localhost:5173
└── customer-portal.yaml   # app: customer-portal, base_url: http://localhost:3000
```

Cross-site flows reference sites by **alias**, each alias pointing to a mapping.

### Session Isolation

When testing multiple sites, each gets its own browser session via `--session <app>`. This prevents cookie/localStorage leakage — a login in admin-panel doesn't affect customer-portal's auth state.

Session isolation is **automatic** when using `--all-sites` or `--suite`.

## Cross-Site Flow Format

Use `sites:` instead of `mapping:` (mutually exclusive). Every step requires `site:`:

> `${test_email}` inside a Fill value is substituted by the `/e2e-test` agent
> runner only. `/e2e-compile` refuses it — compiled scripts never interpolate
> flow variables into step values, so this flow runs under `/e2e-test` and does
> not compile.

```yaml
name: admin-creates-customer-verifies
description: "Admin creates a user, customer portal verifies login works"
tags: [cross-site, user-management]

sites:
  admin:
    mapping: admin-panel
  portal:
    mapping: customer-portal

variables:
  test_email: "newuser@example.com"
  test_password: "SecurePass123!"

steps:
  # Phase 1: Admin creates the user
  - id: admin-navigate-users
    site: admin
    action: Navigate to /users
    expect:
      - "users_table visible on users-page"

  - id: admin-click-create
    site: admin
    action: Click create_user_button on users-page
    expect:
      - "user_form visible on create-user-page"

  - id: admin-fill-email
    site: admin
    action: Fill email_input with '${test_email}' on create-user-page

  - id: admin-fill-password
    site: admin
    action: Fill password_input with '${test_password}' on create-user-page

  - id: admin-submit
    site: admin
    action: Click submit_button on create-user-page
    expect:
      - "text 'User created' on create-user-page"

  # Phase 2: Customer portal verifies login
  - id: portal-navigate-login
    site: portal
    action: Navigate to /login
    expect:
      - "login_form visible on login-page"

  - id: portal-fill-email
    site: portal
    action: Fill email_input with '${test_email}' on login-page

  - id: portal-fill-password
    site: portal
    action: Fill password_input with '${test_password}' on login-page

  - id: portal-submit-login
    site: portal
    action: Click submit_button on login-page
    expect:
      - "url contains /dashboard"
      - "welcome_text visible on dashboard"
```

### Validation Rules

| Rule | Error if violated |
|------|-------------------|
| Every step must have `site:` | `Step '<step-id>': cross-site flow step must have a 'site:' qualifier` |
| `site:` value must exist in `sites:` keys | `Step '<step-id>': unknown site '<alias>' (not in sites: block)` |
| Site aliases must be shell identifiers (`^[A-Za-z_][A-Za-z0-9_]*$`) | `Invalid site name '<alias>' in sites: block: expected shell identifier matching ^[A-Za-z_][A-Za-z0-9_]*$` |
| Site aliases cannot be `__proto__`, `prototype`, or `constructor` | `Invalid site name '<alias>' in sites: block: alias is reserved` |
| Aliases must not normalize to the same `<ALIAS>_BASE_URL` key | `Site aliases '<first>' and '<second>' collide on normalized base URL variable '<NORMALIZED>_BASE_URL'` |
| `sites:` and `mapping:` are mutually exclusive | `Flow has both 'mapping:' and 'sites:' — use one or the other in <flow-path>` |

## Running Cross-Site Tests

### Filter by site: `--site <alias>`

Run only one site's steps from a cross-site flow:

```
/e2e-test admin-creates-customer-verifies --site admin
```

Runs steps 1–5 (where `site: admin`), skipping portal steps. Useful for debugging one side of a cross-site flow.

**Validation**: `--site` cannot be combined with `--all-sites` or `--suite`.

### Auto-discover: `--all-sites`

```
/e2e-test --all-sites
```

Discovers all mappings, classifies each flow, and presents an execution plan:

```
Execution plan:
  admin-panel (http://localhost:5173): smoke-navigation (7 steps)
  customer-portal (http://localhost:3000): smoke-navigation (7), login-flow (5)
  cross-site: admin-creates-customer-verifies (10 steps, admin ↔ portal)
Total: 4 runs, 29 steps. Proceed?
```

Single-site flows run first (grouped by mapping), then cross-site flows.

### Via suite

```
/e2e-test --suite regression
```

Suites define exactly which flows run on which sites. See [Test Suites](suites.md) for full details.

## Preconditions with Site Scoping

Precondition checks can target specific sites using the `site:` field:

```yaml
preconditions:
  runner: psql
  env: [DATABASE_URL]
  checks:
    - query: "SELECT count(*) FROM users"
      expect: "> 0"
      fail_message: "No users — run seed first"
      # No site: field → global check, always runs

    - query: "SELECT count(*) FROM admin_audit_log"
      expect: "> 0"
      fail_message: "No audit log entries"
      site: admin
      # Only checked when running admin site
```

**Filtering logic**:
- `--site admin` → global checks + `site: admin` checks
- `--all-sites` iterating portal → global checks + `site: portal` checks
- No site context → global checks only

## Combining with External Checkpoints

Cross-site flows work with `Execute external` and `Verify external` steps. External steps don't need `site:` — they run outside the browser:

```yaml
steps:
  - id: admin-create-order
    site: admin
    action: Click create_order_button on orders-page
    expect: ["text 'Order #1234 created' on orders-page"]

  - id: wait-for-replication
    action: "Execute external"
    description: "Wait for order to replicate to customer DB"
    execute:
      cli:
        - run: "sleep 5"
          expect: "exit code 0"

  - id: portal-verify-order
    site: portal
    action: Navigate to /orders
    expect:
      - "orders_table visible on orders-page"
      - "text '#1234' on orders-page"

  - id: verify-order-event
    action: "Verify external"
    description: "Confirm PostHog received order_created event"
    wait: 10
    verify:
      posthog:
        - event: order_created
          expect: "count > 0 in last 5 minutes"
    on_fail: warn
```

**Pattern**: Browser A (action) → External (sync/seed) → Browser B (verify) → External (check side-effect)

## Session Isolation Details

The test runner uses `agent-browser --session <app>` to create isolated browser contexts:

```bash
# Each site gets its own session — separate cookies, localStorage, auth state
agent-browser --session admin-panel open http://localhost:5173
agent-browser --session customer-portal open http://localhost:3000
```

**When isolation is active**:

| Mode | Isolation | Reason |
|------|-----------|--------|
| `--all-sites` | Yes (automatic) | Multiple sites in one run |
| `--suite` | Yes (automatic) | Multiple sites in one run |
| `--site <alias>` | No (single session) | Only one site's steps execute |
| Single flow with `mapping:` | No (single session) | Only one site |

**Why it matters**: Without isolation, logging into admin-panel would set cookies that persist when navigating to customer-portal — potentially bypassing auth or corrupting session state.

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `"Flow is not a cross-site flow"` | Used `--site` on a flow with `mapping:` | Remove `--site` or convert flow to `sites:` format |
| `"Site not found in flow"` | `--site <alias>` doesn't match any `sites:` key | Check flow's `sites:` definition |
| `"Cannot use --site with --all-sites"` | Incompatible flags | Use one or the other |
| Auth expired on one site | Sessions are isolated per site | Re-auth in that site's browser window |
| Wrong selectors resolved | Mapping mismatch | Verify `sites.<alias>.mapping` points to the correct mapping file |
| Cross-site flow without `--all-sites`/`--suite`/`--site` | Guard prevents accidental single-site run | Add one of the required flags |

## Related

- [Test Suites](suites.md) — organize multi-site test runs
- [Cross-Boundary Testing](cross-boundary-testing.md) — `Execute external` and `Verify external` steps
- [Commands](commands.md) — all flags and options
- [Writing Tests](writing-tests.md) — flow YAML format basics

---

> **Found a better cross-site pattern?** [Open a PR](https://github.com/iamcxa/kc-claude-plugins/pulls) to share it.
> **Docs unclear or incomplete?** Use `/e2e-help --feedback "<description>"` to let us know.
