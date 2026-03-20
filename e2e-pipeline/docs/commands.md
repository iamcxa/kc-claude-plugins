# Commands

## Skills (Claude Code)

| Command | What it does |
|---------|-------------|
| `/e2e-map` | Create or update UI element mappings |
| `/e2e-map --interactive` | Run browser exploration inline (skip agent dispatch, for debugging) |
| `/e2e-test <flow>` | Run a specific E2E test flow |
| `/e2e-test --tag smoke` | Run all flows tagged with `smoke` |
| `/e2e-test --suite <name>` | Run a named [test suite](suites.md) |
| `/e2e-test --all-sites` | Auto-discover all mappings and run flows on each site ([details](multi-site-testing.md#auto-discover-all-sites)) |
| `/e2e-test --site <alias>` | Run only one site's steps from a [cross-site flow](multi-site-testing.md#filter-by-site-site-alias) |
| `/e2e-test --mapping <name>` | Select a specific mapping file (skip auto-detection) |
| `/e2e-test <flow> --video` | Run flow with video recording + GIF |
| `/e2e-test <flow> --pr 940` | Run flow, record, post results to PR |
| `/e2e-test <flow> --issue DRC-2779` | Include issue context in test report header |
| `/e2e-test <flow> --no-compile` | Skip auto-compile and compiled script run after LLM execution |
| `/e2e-walkthrough` | Interactive walkthrough (records by default) |
| `/e2e-walkthrough --mode guided` | Default mode: show plan + one-line per-step reports |
| `/e2e-walkthrough --mode step` | Pause between steps, wait for "go" before each |
| `/e2e-walkthrough --mode auto` | Silent execution, record anomalies without prompting |
| `/e2e-walkthrough --no-video` | Walkthrough without video recording |
| `/e2e-walkthrough --issue DRC-2811` | Read issue description, propose walkthrough covering the feature |
| `/e2e-flow --from <plan>` | Generate E2E flow YAML from a plan or spec |
| `/e2e-flow --from pr 940` | Generate flow from PR diff |
| `/e2e-flow --smoke` | Generate visit-all-pages smoke flow from mapping |
| `/e2e-flow --verify-only <flow>` | Verify an existing flow in browser with auto-repair |
| `/e2e-flow --no-verify` | Generate flow only, skip browser verification |
| `/e2e-flow --no-pr` | Skip PR auto-detection, commit, and PR comment posting |
| `/e2e-flow --issue DRC-2779` | Include issue context in report header |
| `/e2e-compile <flow>` | Compile one flow YAML to a standalone bash script |
| `/e2e-compile --all` | Compile all flows in the flows directory |
| `/e2e-compile --all --coverage` | Compile all + produce element coverage report |
| `/e2e-dispatch` | Unified entry point (routes to the right skill) |
| `/e2e-dispatch --test <flow> --fg` | Force foreground execution (override background default) |
| `/e2e-skill-ops` | Debug, maintain, or evaluate E2E skills |
| `/e2e-help` | Interactive help guide -- topics, examples, feedback |
| `/e2e-help <topic>` | Deep dive into a topic (e.g., `cross-site`, `suites`, `checkpoints`) |
| `/e2e-help --feedback "<text>"` | Report a documentation gap or confusing area |
| `/e2e-doc-sync` | Scan docs for gaps against skills/agents, write updates |
| `/e2e-doc-sync --check` | Report-only mode (no writes) |
| `/e2e-doc-sync --fix` | Scan + auto-write approved gaps |
| `/e2e-pipeline-doc-sync` | Full doc sync: static scan + history enrichment + write + live probe verification |
| `/e2e-pipeline-doc-sync --check` | Report gaps + history enrichment, no writes |
| `/e2e-pipeline-doc-sync --probe-only` | Verify existing docs against actual skill behavior |
| `/e2e-pipeline-doc-sync --auto` | Full sync, skip user confirmation |
| `/e2e-pipeline-doc-sync --section <doc>` | Targeted sync for one doc file |

## Background vs Foreground Execution

Some dispatch routes run in the **background** by default (main context stays free for other work). Use `--fg` to force foreground execution:

| Route | Default | Override |
|-------|---------|---------|
| `/e2e-test` | Background | `--fg` |
| `/e2e-map` (no --interactive) | Background | `--fg` |
| `/e2e-map --interactive` | Foreground | -- |
| `/e2e-flow` | Foreground | -- |
| `/e2e-walkthrough` | Foreground | -- |
| `/e2e-skill-ops` | Foreground | -- |

Interactive skills (walkthrough, flow, skill-ops) always run in foreground. Non-interactive skills (test, map) default to background so you can continue working.

## Auto-Compile & Divergence

By default, `/e2e-test` auto-compiles the flow after the LLM run and executes the compiled script to detect divergence between AI and deterministic execution. This is Phase 1.8 of the test orchestrator.

**What happens:**

1. After the LLM test-runner agent completes, the skill locates the compiler
2. Compiles the flow YAML to a standalone bash script (`.claude/e2e/compiled/<flow>.sh`)
3. Runs the compiled script with `--continue-on-error`
4. Compares LLM results vs compiled results step-by-step

**Divergence report:**

| Step | LLM Result | Compiled Result | Status | Likely Cause |
|------|-----------|-----------------|--------|--------------|
| step-3 | PASS | FAIL | Diverged | Selector may be timing-sensitive |
| step-7 | FAIL | PASS | Diverged | LLM may have hallucinated failure |
| step-9 | PASS | PASS | Same | -- |

Zero diverged steps means both execution modes agree -- high confidence the test is reliable.

**Skip it:** Pass `--no-compile` to skip auto-compile entirely. Useful when you only care about the LLM run, or the compiler is not installed.

**Quick Re-Run:** After every single-flow test, the compiled script path is shown so you can re-run without AI:

```bash
bash .claude/e2e/compiled/<flow-name>.sh
bash .claude/e2e/compiled/<flow-name>.sh --continue-on-error --junit /tmp/junit.xml
```

## CLI-Only Flow Recording

When a flow contains **zero browser steps** (only `Execute external` and `Verify external` actions), the skill automatically switches from browser-based recording to terminal recording via asciinema.

**Detection logic:** The skill scans all steps in the flow. If every step has `action: "Execute external"` or `action: "Verify external"`, the flow is classified as CLI-only.

**Prerequisites:** `asciinema` and `agg` must be installed. If either is missing, the skill warns and proceeds without recording.

```bash
brew install asciinema agg
```

**Dispatch behavior:** The skill wraps CLI execution with `asciinema rec`, producing a `.cast` file. It then dispatches the `e2e-media-processor` agent with `cast_path` instead of `recording_path`:

```yaml
# Browser flow (default):
#   recording_path: $REPORT_DIR/full.webm

# CLI-only flow (automatic):
#   cast_path: $REPORT_DIR/recording.cast
```

The media processor converts the cast file to GIF (via `agg`), MP4 (via `ffmpeg`), and thumbnail -- the same output artifacts as browser recording, just sourced from terminal output instead of screenshots.

**Override:** Pass `--no-video` to skip terminal recording entirely.

For the full terminal recording pipeline and parameters, see [Cross-Boundary Testing -- Recording CLI-Only Flows](cross-boundary-testing.md#recording-cli-only-flows).

## CLI Tools (Node.js)

These run outside Claude Code -- in CI pipelines, local terminals, or scripts.

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
- `coverage.json` -- per-element coverage data (verified, reached, untouched)
- `coverage-history.json` -- appended on each run for trend tracking
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

**Mutual exclusivity**: `--site`, `--all-sites`, and `--suite` are mutually exclusive -- use only one.

## Flow Step Types

Flow YAML supports three step types. Browser steps are the default; checkpoint steps handle non-browser actions.

| Step type | `action:` value | Required block | Default `on_fail` |
|-----------|----------------|----------------|-------------------|
| Browser | `Navigate to`, `Click`, `Fill`, `Wait for networkidle` | `expect:` | (test fails) |
| Eval | `Eval '<js>'` | -- | (test fails) |
| Execute external | `"Execute external"` | `execute:` | `fail` |
| Verify external | `"Verify external"` | `verify:` | `warn` |

**Execute external** -- trigger CLI commands, API calls, or scripts:

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

**Verify external** -- check analytics, tracing, or external service state:

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
| `--retries <N>` | Retry failed steps up to N times before marking as failed |

**Environment variables** (read by compiled scripts at runtime):

| Variable | Default | Description |
|----------|---------|-------------|
| `E2E_BASE_URL` | `http://localhost:5173` | Target URL (overridden by `$1` positional arg) |
| `WAIT_TIMEOUT` | `10` | Seconds for visibility/URL poll timeouts (use `30` for deploy previews) |
| `E2E_SCREENSHOT_DIR` | `/tmp/e2e-screenshots` | Where `_handle_failure` saves diagnostic screenshots |
| `AGENT_BROWSER_PROFILE` | (none) | Persistent browser profile directory for auth session sharing |

## Related

- [Getting Started](getting-started.md) -- install, prerequisites, first run
- [Writing Tests](writing-tests.md) -- flow YAML format, preconditions, cross-site flows
- [CI Integration](ci-integration.md) -- GitHub Actions setup with compiled scripts
- [Multi-Site Testing](multi-site-testing.md) -- cross-site flows, `--site`, `--all-sites`
- [Test Suites](suites.md) -- suite file format and site assignment
- [Cross-Boundary Testing](cross-boundary-testing.md) -- `Execute external` / `Verify external` steps
- [Self-Improvement](self-improvement.md) -- how skills learn from execution

---

> **Found a better pattern?** [Open a PR](https://github.com/iamcxa/kc-claude-plugins/pulls) to share it.
> **Docs unclear?** Use `/e2e-help --feedback "<description>"` to let us know.
