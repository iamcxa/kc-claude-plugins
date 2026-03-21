# Test Suites

Suites define a curated set of flows to run together, with per-flow site assignment. Think of them as playlists for your E2E tests.

## Suite vs Tags vs --all-sites

| Method | Best for | How it works |
|--------|----------|--------------|
| `--tag smoke` | Dynamic filtering | Run all flows that have a matching `tags:` entry |
| `--all-sites` | Auto-discovery | Detect all mappings, run applicable flows on each |
| `--suite regression` | Curated orchestration | Run a defined set of flows with explicit site assignments |

**Key difference**: Tags are properties of flows (dynamic). Suites are standalone definitions (static). Only suites let you specify which site(s) each flow runs on.

## Suite File Format

Store suites in `.claude/e2e/suites/<name>.yaml`:

```yaml
name: regression

runs:
  # Run the same flow on multiple sites
  - flow: smoke-navigation
    sites: [admin-panel, customer-portal]

  # Run a flow on one specific site
  - flow: user-management
    site: admin-panel

  # Cross-site flow — uses the flow's own sites: definition
  - flow: admin-creates-customer-verifies
```

### Site Assignment Methods

| Config | Behavior | Resolution |
|--------|----------|------------|
| `sites: [a, b]` | Run flow once per site | Each site resolved by mapping's `app` field |
| `site: a` | Run flow on one site | Resolved by mapping's `app` field |
| *(neither)* | Cross-site flow | Flow must have its own `sites:` block |

**How resolution works**: `site: admin-panel` scans all `.claude/e2e/mappings/*.yaml` for a file with `app: admin-panel`, then uses that mapping's `base_url` and selectors.

### Validation

| Rule | Error |
|------|-------|
| Flow must exist in `.claude/e2e/flows/` | `"Flow not found: <name>"` |
| `site`/`sites` values must match a mapping `app` field | `"No mapping with app: <name>"` |
| Cannot use both `site:` and `sites:` on the same entry | `"Use one or the other"` |
| Cannot override a cross-site flow's sites | `"Flow has own sites: definition"` |
| Generic flow without site info | `"Add site: or sites: to the run entry"` |
| Duplicate flow + site combination | Warning (not error) |

## Running Suites

```
/e2e-test --suite regression
```

The skill resolves each entry, presents an execution plan, and waits for confirmation:

```
Suite: regression (5 runs)
  admin-panel:
    smoke-navigation (7 steps)
    user-management (12 steps)
  customer-portal:
    smoke-navigation (7 steps)
  cross-site:
    admin-creates-customer-verifies (10 steps, admin <-> portal)
Total: 4 dispatches, 36 steps. Proceed?
```

Each site gets session isolation automatically (`--session <app>`). Single-site flows run first, then cross-site flows.

### With PR reporting

```
/e2e-test --suite smoke --pr 123
```

Each flow in the suite gets its own report directory. The PR comment includes a combined summary table.

### With video

```
/e2e-test --suite smoke --video
```

Records each dispatch separately. Media files generated per-site.

## Examples

### Smoke Suite

Quick post-deploy sanity check -- one flow, all sites:

```yaml
name: smoke

runs:
  - flow: smoke-navigation
    sites: [admin-panel, customer-portal, mobile-app]
```

### Regression Suite

Comprehensive coverage with mixed flow types:

```yaml
name: regression

runs:
  # Smoke on all sites
  - flow: smoke-navigation
    sites: [admin-panel, customer-portal]

  # Auth on all sites
  - flow: login-flow
    sites: [admin-panel, customer-portal]

  # Feature-specific (single site)
  - flow: order-creation
    site: admin-panel

  - flow: order-tracking
    site: customer-portal

  # Cross-site integration
  - flow: admin-creates-customer-verifies
```

### Feature Suite

Focused on one feature area -- good for feature branch validation:

```yaml
name: user-management-v2

runs:
  - flow: create-user
    site: admin-panel

  - flow: user-login
    site: customer-portal

  - flow: admin-creates-customer-verifies

  - flow: user-permissions
    site: admin-panel

  - flow: user-deactivation
    site: admin-panel
```

## CI Integration

Suites are the recommended way to organize CI test runs:

```bash
# Fast gate — runs after every deploy
/e2e-test --suite smoke

# Thorough — nightly or pre-release
/e2e-test --suite regression

# Feature validation — on feature branches
/e2e-test --suite user-management-v2
```

### Without Claude Code (compiled scripts)

`/e2e-compile` compiles individual flows, not suites. To compile all flows referenced by suites:

```
/e2e-compile --all
```

Then run in CI without Claude Code:

```bash
# Run all compiled scripts
for script in .claude/e2e/compiled/*.sh; do
  bash "$script" \
    --continue-on-error \
    --junit "/tmp/junit-$(basename "$script" .sh).xml"
done
```

**Note**: Compiled scripts run single-site flows only. Cross-site flows and session isolation require the LLM test runner (Claude Code). Compiled scripts are the deterministic subset of your suite.

## Relationship to Other Features

| Feature | Relationship |
|---------|-------------|
| **Tags** (`--tag`) | Suites can reference tagged flows, but tags don't provide site assignment |
| **Cross-site flows** (`sites:`) | Suites orchestrate cross-site flows alongside single-site ones |
| **--all-sites** | Auto-discovery mode; suites provide explicit control over what runs where |
| **Preconditions** | Per-flow preconditions still run; site-scoped checks filter by the suite's site context |
| **Compiled scripts** | Compile individual flows from a suite; the suite definition itself isn't compiled |

## Related

- [Multi-Site Testing](multi-site-testing.md) -- cross-site flows, `--site`, `--all-sites`, session isolation
- [Commands](commands.md) -- all skills and flags including `--suite`
- [Writing Tests](writing-tests.md) -- flow YAML format and preconditions
- [CI Integration](ci-integration.md) -- running suites in GitHub Actions
- [PR Workflow](pr-workflow.md) -- posting suite results to pull requests

---

> **Have a suite pattern that works well?** [Open a PR](https://github.com/iamcxa/kc-claude-plugins/pulls) to share it here.
> **Missing a feature?** Use `/e2e-help --feedback "<what you need>"` and we'll track it.
