# Commands

## Skills (Claude Code)

| Command | What it does |
|---------|-------------|
| `/e2e-map` | Create or update UI element mappings |
| `/e2e-test <flow>` | Run a specific E2E test flow |
| `/e2e-test --tag smoke` | Run all flows tagged with `smoke` |
| `/e2e-test --suite <name>` | Run a named [test suite](suites.md) |
| `/e2e-test --all-sites` | Auto-discover all mappings and run flows on each site ([details](multi-site-testing.md#auto-discover-all-sites)) |
| `/e2e-test --site <alias>` | Run only one site's steps from a [cross-site flow](multi-site-testing.md#filter-by-site-site-alias) |
| `/e2e-test <flow> --video` | Run flow with video recording + GIF |
| `/e2e-test <flow> --pr 940` | Run flow, record, post results to PR |
| `/e2e-walkthrough` | Interactive walkthrough (records by default) |
| `/e2e-walkthrough --no-video` | Walkthrough without video recording |
| `/e2e-flow --from <plan>` | Generate E2E flow YAML from a plan or spec |
| `/e2e-flow --smoke` | Generate visit-all-pages smoke flow from mapping |
| `/e2e-flow --verify-only <flow>` | Verify an existing flow in browser with auto-repair |
| `/e2e-flow --no-verify` | Generate flow only, skip browser verification |
| `/e2e-compile <flow>` | Compile one flow YAML to a standalone bash script |
| `/e2e-compile --all` | Compile all flows in the flows directory |
| `/e2e-compile --all --coverage` | Compile all + produce element coverage report |
| `/e2e-dispatch` | Unified entry point (routes to the right skill) |
| `/e2e-skill-ops` | Debug, maintain, or evaluate E2E skills |
| `/e2e-help` | Interactive help guide — topics, examples, feedback |
| `/e2e-help <topic>` | Deep dive into a topic (e.g., `cross-site`, `suites`, `checkpoints`) |
| `/e2e-doc-sync` | Scan docs for gaps against skills/agents, write updates |

## CLI Tools (Node.js)

These run outside Claude Code — in CI pipelines, local terminals, or scripts.

### e2e-compile

```bash
npx e2e-compile <flow-name>              # compile one flow
npx e2e-compile --all                    # compile all flows
npx e2e-compile --all --coverage         # compile + coverage report
npx e2e-compile --dry-run <flow-name>    # validate without writing output
npx e2e-compile --verbose <flow-name>    # show resolved step details
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--all` | Compile all `.yaml` files in the flows directory |
| `--dry-run` | Validate flow + mapping coherence without writing output |
| `--verbose` | Show resolved operands and expects per step |
| `--coverage` | Produce static element coverage report after compilation |
| `--coverage-output <dir>` | Directory for coverage JSON (default: `.claude/e2e/coverage`) |
| `--flows-dir <dir>` | Flows directory (default: `.claude/e2e/flows`) |
| `--mappings-dir <dir>` | Mappings directory (default: `.claude/e2e/mappings`) |
| `--output-dir <dir>` | Output directory (default: `.claude/e2e/compiled`) |

**Coverage output:**
- `coverage.json` — per-element coverage data (verified, reached, untouched)
- `coverage-history.json` — appended on each run for trend tracking
- Console prints regression warnings when coverage drops

### e2e-quarantine

```bash
node bin/e2e-quarantine.js \
  --metrics-dir <path> \
  --quarantine-path <path> \
  [--rotate] \
  [--manage-issues] \
  [--pr-comment <number>]
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--metrics-dir <path>` | Directory containing per-run metrics JSON files (required for evaluation) |
| `--quarantine-path <path>` | Path to `quarantine.json` (created if missing) |
| `--rotate` | Delete metrics files beyond 2x window per flow |
| `--manage-issues` | Auto-create/close GitHub issues for quarantine transitions |
| `--pr-comment <number>` | Post quarantine status table as PR comment |

**What it does:**
1. Reads per-run metrics files and evaluates flaky rates per flow
2. Quarantines flows exceeding the flaky threshold (default: 20%)
3. Recovers flows that pass consistently (default: 3 consecutive first-attempt passes)
4. Optionally creates GitHub issues with failure history and closes them on recovery
5. Optionally posts a quarantine status table as a PR comment

See [CI Integration](ci-integration.md) for how this fits into a GitHub Actions workflow.

### Multi-Site & Suite Flags

| Flag | Description | Details |
|------|-------------|---------|
| `--all-sites` | Discover all mappings and run applicable flows on each site. Presents execution plan before running. Session isolation automatic. | [Multi-Site Testing](multi-site-testing.md) |
| `--site <alias>` | Run only the specified site's steps from a cross-site flow. Cannot combine with `--all-sites` or `--suite`. | [Cross-site filter](multi-site-testing.md#filter-by-site-site-alias) |
| `--suite <name>` | Run a named suite from `.claude/e2e/suites/<name>.yaml`. Resolves flows and site assignments per suite definition. | [Test Suites](suites.md) |

**Mutual exclusivity**: `--site`, `--all-sites`, and `--suite` are mutually exclusive — use only one.

## Flow Step Types

Flow YAML supports three step types. Browser steps are the default; checkpoint steps handle non-browser actions.

| Step type | `action:` value | Required block | Default `on_fail` |
|-----------|----------------|----------------|-------------------|
| Browser | `Navigate to`, `Click`, `Fill`, `Wait for networkidle` | `expect:` | (test fails) |
| Execute external | `"Execute external"` | `execute:` | `fail` |
| Verify external | `"Verify external"` | `verify:` | `warn` |

**Execute external** — trigger CLI commands, API calls, or scripts:

```yaml
- id: trigger-something
  action: "Execute external"
  description: "Why this step exists"
  execute:
    cli:
      - run: "my-command --flag"
        repeat: 3            # optional
        expect: "exit code 0"
  wait_after: 5              # seconds after execution
  on_fail: fail
```

**Verify external** — check analytics, tracing, or external service state:

```yaml
- id: verify-something
  action: "Verify external"
  description: "Why this checkpoint exists"
  wait: 10                   # propagation delay
  verify:
    posthog:
      - event: my_event
        expect: "Event exists with expected properties"
  on_fail: warn
```

See [Cross-Boundary Testing](cross-boundary-testing.md) for a complete example.

### Compiled Flow Scripts

Each compiled `.sh` script supports these runtime flags:

| Flag | Description |
|------|-------------|
| `--junit <path>` | Write JUnit XML test results |
| `--metrics-output <path>` | Write per-run metrics JSON (for quarantine evaluation) |
| `--continue-on-error` | Don't exit on first step failure (collect all results) |
