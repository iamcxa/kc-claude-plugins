# CI Integration

Run E2E tests in GitHub Actions using compiled flow scripts -- no Claude Code required at runtime.

## Overview

The pipeline provides a GHA workflow template (`templates/browser-e2e.yml`) with three jobs:

```
auth-setup  ->  browser-e2e (matrix)  ->  report
```

1. **auth-setup** -- runs a login flow once, uploads the browser session as an artifact
2. **browser-e2e** -- runs each flow in parallel (matrix strategy), reusing the auth session
3. **report** -- aggregates JUnit results, publishes check annotations, evaluates quarantine state

## Setup

### Step 1: Compile your flows

Compiled scripts are standalone bash files that run `agent-browser` commands. They don't need Claude Code.

```
/e2e-compile --all
```

This produces `.claude/e2e/compiled/<flow>.sh` for each flow YAML. Commit these to your repo.

### Step 2: Copy the workflow template

```bash
mkdir -p .github/workflows
cp <plugin-path>/templates/browser-e2e.yml .github/workflows/browser-e2e.yml
```

> **Finding the plugin path:** The plugin is installed at `~/.claude/plugins/cache/local/kc-claude-plugins/e2e-pipeline/` (or wherever Claude Code caches plugins). The template path is `templates/browser-e2e.yml`.

### Step 3: Copy the quarantine CLI

The quarantine evaluator runs in CI as a standalone Node.js script. Copy it to your repo:

```bash
mkdir -p scripts/e2e
cp <plugin-path>/bin/e2e-quarantine.js scripts/e2e/
cp <plugin-path>/compiler/quarantine.js scripts/e2e/
cp <plugin-path>/compiler/metrics.js scripts/e2e/
```

Then update the workflow's quarantine step to use your local path:

```yaml
# In .github/workflows/browser-e2e.yml, change:
run: |
  node scripts/e2e/e2e-quarantine.js \
    --metrics-dir junit-results \
    --quarantine-path .claude/e2e/quarantine.json \
    --manage-issues \
    --rotate
```

> **Why copy instead of install?** The plugin is a Claude Code plugin (`private: true`), not an npm package. CI environments don't have Claude Code -- they need the quarantine logic as plain Node.js files with no external dependencies.

### Step 4: Customize the workflow

Edit `.github/workflows/browser-e2e.yml`:

**Required changes:**

```yaml
# 1. List your compiled flows
matrix:
  flow:
    - login-flow
    - catalog-browse
    - smoke-all-pages

# 2. Set your deployment URL
env:
  E2E_BASE_URL: http://localhost:3000
  # Or for preview deploys:
  # E2E_BASE_URL: ${{ needs.deploy.outputs.preview_url }}
```

**Optional changes:**

```yaml
# Adjust parallelism (default: 3)
max-parallel: 5

# Adjust timeout per flow (default: 20 min)
timeout-minutes: 30

# Skip auth-setup if your app doesn't require login
# Remove the auth-setup job and `needs: [auth-setup]` from browser-e2e
```

### Step 5: Configure secrets (if using auth)

If your login flow uses credentials:

1. Go to **Settings -> Secrets and variables -> Actions** in your GitHub repo
2. Add `E2E_TEST_EMAIL` and `E2E_TEST_PASSWORD`
3. Uncomment the secrets in the workflow:

```yaml
env:
  E2E_TEST_EMAIL: ${{ secrets.E2E_TEST_EMAIL }}
  E2E_TEST_PASSWORD: ${{ secrets.E2E_TEST_PASSWORD }}
```

Compiled flows can reference these via environment variables instead of hardcoded values.

---

## Quarantine System

The quarantine system automatically manages flaky tests so they don't block merges while still tracking them for resolution.

### How it works

1. Each compiled flow emits a metrics JSON file (`--metrics-output`) with pass/fail data per step
2. The `report` job runs `e2e-quarantine.js` to evaluate flaky rates over a sliding window (default: 20 runs)
3. Flows exceeding the flaky threshold (default: 20%) are **quarantined**
4. Quarantined flows are excluded from the CI gate -- their failures don't block merges
5. Flows that pass consistently (default: 3 consecutive first-attempt passes) are **recovered**

### GitHub issue lifecycle

With `--manage-issues`, the quarantine CLI:
- **Creates** a GitHub issue when a flow is quarantined (labeled `e2e-flaky` + flow name)
- **Closes** the issue with a recovery summary when the flow stabilizes
- **Adds** an `e2e-stale` label if a flow stays quarantined beyond the stale threshold (default: 14 days)
- **Deduplicates** -- won't create a new issue if one already exists for that flow

### PR comments

With `--pr-comment <number>`, a status table is posted to the PR showing all quarantined flows, their flaky rates, and last failure dates. The comment is updated (not duplicated) on subsequent runs.

### Metrics JSON format

Each compiled flow run with `--metrics-output` produces a JSON file like:

```json
{
  "flow": "login-flow",
  "timestamp": "2026-03-18T14:30:00Z",
  "duration_ms": 12340,
  "result": "pass",
  "steps": [
    { "id": "navigate-to-login", "result": "pass", "duration_ms": 1200 },
    { "id": "fill-credentials", "result": "pass", "duration_ms": 800 },
    { "id": "submit-form", "result": "pass", "duration_ms": 2100 },
    { "id": "verify-dashboard", "result": "pass", "duration_ms": 1500 }
  ],
  "retries": 0
}
```

The quarantine CLI reads these files to calculate flaky rates over the sliding window.

### Quarantined flow entry

When a flow is quarantined, its entry in `quarantine.json` looks like:

```json
{
  "flows": {
    "checkout-flow": {
      "status": "quarantined",
      "quarantined_at": "2026-03-15T10:00:00Z",
      "flaky_rate": 0.25,
      "last_failure": "2026-03-18T09:00:00Z",
      "consecutive_passes": 0,
      "issue_number": 42
    }
  }
}
```

### Configuration

Quarantine thresholds are stored in `quarantine.json`:

```json
{
  "config": {
    "thresholds": {
      "flaky_rate": 0.2,
      "window": 20,
      "recovery_passes": 3,
      "stale_days": 14
    }
  },
  "flows": {}
}
```

| Threshold | Default | Meaning |
|-----------|---------|---------|
| `flaky_rate` | 0.2 (20%) | Quarantine when flaky rate exceeds this |
| `window` | 20 | Number of recent runs to evaluate |
| `recovery_passes` | 3 | Consecutive first-attempt passes to recover |
| `stale_days` | 14 | Days before adding `e2e-stale` label |

---

## Mapping Linter (`scripts/lint-mapping.sh`)

`scripts/lint-mapping.sh` is a 4-token-class linter that rejects banned Playwright vocabulary from mapping YAML files. It exists to keep mappings on the canonical Cand 2 grammar (`[role="X"][aria-label="Y"]`, CSS `:nth-of-type(N)`, `find role` subcommand, etc.) and prevent regression after the 2.7.0 selector-grammar realignment.

| Banned token | Why | Use instead |
|---|---|---|
| `role=X[name="Y"]` | Playwright role-selector attribute syntax | `[role="X"][aria-label="Y"]` |
| ` >> nth=N` | Playwright chord nth selector | `:nth-of-type(N)` (CSS) |
| bare `text=...` at selector start | Playwright text shorthand | `find text "..."` (subcommand) |
| `has-text(...)` | Playwright pseudo (broken in agent-browser) | role + name match |

Usage:

```bash
# Lint a single mapping
bash scripts/lint-mapping.sh .claude/e2e/mappings/my-app.yaml

# Lint every mapping in a project (CI-friendly: exit 1 on any violation)
find .claude/e2e/mappings -name '*.yaml' -print0 \
  | xargs -0 -n1 bash scripts/lint-mapping.sh
```

Exit codes: `0` clean · `1` one or more banned tokens detected (path + line printed to stderr).

Wire into CI as a fast pre-flight gate before the browser job spins up.

## Fallback Counter Baseline (`scripts/measure-fallback-baseline.sh`)

The 2.7.0 release added an `eval_fallback_hits` counter to `/e2e-test` traces and reports — every silent eval-fallback the runner used to mask is now tallied loudly. To bound regressions, capture a baseline:

```bash
bash scripts/measure-fallback-baseline.sh \
  --flows .claude/e2e/flows \
  --output .claude/e2e/baselines/fallback-hits.json
```

The script invokes `/e2e-test` per flow, parses each report's `eval_fallback_hits` field, and emits an aggregate JSON (per-flow + total). Compare future runs against this baseline; a non-trivial increase indicates either a selector regression in the mapping or a fall-out in agent-browser locator handling.

## Mapping Staleness Detection

The `auth-setup` job includes a staleness check that compares mapping file dates against UI source changes:

```yaml
- name: Check mapping staleness
  run: |
    UI_PATHS="src/ app/ pages/ components/"   # CUSTOMIZE
    # ... warns if mapping hasn't been updated since UI changes
```

Customize `UI_PATHS` to match your project's frontend source directories. The check emits `::warning::` annotations -- it doesn't fail the build.

---

## CI Gate -- Quick Start (Minimal)

The simplest setup: 3 jobs, ~60 lines. No dynamic discovery, no quarantine, no JUnit report.

```yaml
name: Browser E2E Gate

on:
  pull_request:

jobs:
  auth-setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          sparse-checkout: .claude/e2e/compiled
          sparse-checkout-cone-mode: false

      - name: Install agent-browser
        run: |
          npm install -g agent-browser
          agent-browser install

      - name: Run login flow
        env:
          E2E_BASE_URL: https://your-preview-url.example.com
          WAIT_TIMEOUT: '30'
          AGENT_BROWSER_PROFILE: /tmp/e2e-auth-profile
        run: |
          mkdir -p /tmp/e2e-auth-profile
          chmod +x .claude/e2e/compiled/gate-login-flow.sh
          .claude/e2e/compiled/gate-login-flow.sh

      - name: Upload auth session
        uses: actions/upload-artifact@v7
        with:
          name: e2e-auth-session
          path: /tmp/e2e-auth-profile
          if-no-files-found: error

  browser-e2e:
    needs: [auth-setup]
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        flow: [gate-catalog-browse, gate-smoke-all-pages]
    steps:
      - uses: actions/checkout@v6
        with:
          sparse-checkout: .claude/e2e/compiled
          sparse-checkout-cone-mode: false

      - name: Install agent-browser
        run: |
          npm install -g agent-browser
          agent-browser install

      - name: Download auth session
        uses: actions/download-artifact@v8
        with:
          name: e2e-auth-session
          path: /tmp/e2e-auth-profile

      - name: Run flow
        env:
          E2E_BASE_URL: https://your-preview-url.example.com
          WAIT_TIMEOUT: '30'
          AGENT_BROWSER_PROFILE: /tmp/e2e-auth-profile
        run: |
          chmod +x .claude/e2e/compiled/${{ matrix.flow }}.sh
          .claude/e2e/compiled/${{ matrix.flow }}.sh --continue-on-error

  gate:
    needs: [auth-setup, browser-e2e]
    if: always()
    runs-on: ubuntu-latest
    outputs:
      passed: ${{ steps.check.outputs.passed }}
    steps:
      - name: Evaluate results
        id: check
        env:
          AUTH: ${{ needs.auth-setup.result }}
          E2E: ${{ needs.browser-e2e.result }}
        run: |
          PASSED=true
          if [ "$AUTH" != "success" ]; then
            echo "Auth setup failed: $AUTH"; PASSED=false
          fi
          if [ "$E2E" != "success" ] && [ "$E2E" != "skipped" ]; then
            echo "E2E failed: $E2E"; PASSED=false
          fi
          echo "passed=$PASSED" >> "$GITHUB_OUTPUT"
          [ "$PASSED" = "true" ] || exit 1
```

**Key environment variables:**

| Variable | Purpose | Default |
|----------|---------|---------|
| `E2E_BASE_URL` | Target URL for compiled scripts | `http://localhost:5173` |
| `WAIT_TIMEOUT` | Seconds for visibility/URL polls | `10` (use `30` for deploy previews) |
| `AGENT_BROWSER_PROFILE` | Persistent browser profile directory (cookies, localStorage) | none |
| `E2E_SCREENSHOT_DIR` | Where `_handle_failure` saves diagnostic screenshots | `/tmp/e2e-screenshots` |

### Why `gate` job uses explicit output

`needs.X.result` for reusable workflows is unreliable when internal jobs use `if: always()`. A succeeding `always()` job can mask upstream failures. The `gate` job provides an explicit `passed` output that callers check:

```yaml
# In caller workflow (e.g., release-gate.yaml):
if: needs.browser-e2e.outputs.passed == 'true'
# NOT: needs.browser-e2e.result == 'success'
```

### Why `!= success` instead of `== failure`

Gate conditions must exclude known-safe states rather than match known-bad states. `== "failure"` misses `cancelled` (e.g., job timeout). Use `!= "success" && != "skipped"` to catch all failure modes.

---

## CI Gate -- Full Example (Reusable Workflow)

For production use with dynamic flow discovery, JUnit reports, and release gate integration, see this structure:

```
reuse-browser-e2e.yaml (reusable, workflow_call)
|- discover        -- scan .claude/e2e/compiled/gate-*.sh, build matrix JSON
|- auth-setup      -- login flow + upload AGENT_BROWSER_PROFILE artifact
|- browser-e2e     -- matrix of gate flows (excludes login)
|- report          -- aggregate JUnit XML via mikepenz/action-junit-report
+-- gate            -- explicit passed output for callers

release-gate.yaml (caller)
+-- browser-e2e     -- uses: reuse-browser-e2e.yaml
    +-- auto-approve -- if: needs.browser-e2e.outputs.passed == 'true'
```

**Dynamic flow discovery** avoids hardcoding flow names in the matrix:

```yaml
# In discover job:
FLOWS=$(ls .claude/e2e/compiled/gate-*.sh | xargs -I{} basename {} .sh \
  | grep -v "^gate-login-flow$" \
  | jq -R -s -c 'split("\n") | map(select(length > 0))' || echo '[]')
```

**Empty matrix workaround**: GitHub Actions crashes on `fromJSON('[]')`. Use `["__skip__"]` sentinel + early exit in run step.

**Auth session sharing**: `AGENT_BROWSER_PROFILE=/tmp/e2e-auth-profile` persists cookies/localStorage. Upload as artifact in auth-setup, download in matrix jobs. Do NOT use `agent-browser session dir` -- it returns the session name (`"default"`), not a directory path.

---

## Headless CI Limitations

`agent-browser` uses Playwright under the hood. On **GitHub Actions Linux runners** (headless Chrome), Playwright's actionability checks behave differently:

| Command | Local (macOS) | CI (Linux headless) |
|---------|---------------|---------------------|
| `agent-browser snapshot` | Works | Works |
| `agent-browser is visible` | Works | Always returns `false` |
| `agent-browser fill` | Works | Returns exit 0 but doesn't fill |
| `agent-browser click` | Works | Returns non-zero |
| `agent-browser eval` | Works | Works |
| `agent-browser screenshot` | Works | Works |

### Workarounds (applied by the compiler)

**Visibility checks**: The compiler generates `_poll_snapshot_contains` (grepping the a11y tree) instead of `_poll_visible` (Playwright's `isVisible()`). The `selectorToA11yPattern()` function (canonical: `compiler/lib/selector-translate.js`) converts both the post-2.7.0 native CSS attribute selectors and the legacy Playwright role-selector forms (kept for backward compat):

| Input selector | Form | Grep pattern |
|---|---|---|
| `[role="textbox"][aria-label="電子郵件"]` | Cand 2 canonical (post-2.7.0) | `textbox "電子郵件"` |
| `[role="button"][aria-label="登 入"]` | Cand 2 canonical | `button "登 入"` |
| `[role="combobox"]` | role-only | `combobox` (broad) |
| `[data-testid="…"]` | data-testid | `null` (runner uses CSS attr selector directly) |
| `role=textbox[name="電子郵件"]` | Playwright legacy (BANNED in new mappings; translator still accepts) | `textbox "電子郵件"` |
| `role=heading[name=/每日看板/]` | Playwright regex (BANNED) | `每日看板` (literal prefix) |
| `role=combobox >> nth=0` | Playwright nth chord (BANNED) | `combobox` (role only) |

> The mapping linter (`scripts/lint-mapping.sh`) rejects all four banned Playwright token classes (`role=X[name=Y]`, `>> nth=N`, bare `text=`, `has-text(`) at the mapping layer. New mappings produced by `/e2e-map` (2.7.0+) emit only canonical Cand 2 forms.

**Fill and click** (login flows only): Replace `agent-browser fill`/`click` with `agent-browser eval` using JavaScript:

```bash
# Fill (React-compatible via nativeInputValueSetter):
agent-browser eval "(()=>{const el=document.querySelector('input[name=\"email\"]');
const s=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
s.call(el,'user@example.com');
el.dispatchEvent(new Event('input',{bubbles:true}));
el.dispatchEvent(new Event('change',{bubbles:true}));})()"

# Click:
agent-browser eval "(()=>{document.querySelector('button[type=\"submit\"]').click();})()"
```

**IIFE required**: Consecutive `agent-browser eval` calls share the same JS global scope. `const` redeclaration across evals causes `SyntaxError`. Always wrap in `(()=>{...})()`.

**Ant Design `Input.Password`**: Does not pass `name` attribute to inner `<input>`. Use `input[type="password"]` instead of `input[name="password"]`.

### What the compiler handles vs manual patches

| Aspect | Compiler handles | Manual patch needed |
|--------|-----------------|-------------------|
| Visibility checks (`_poll_snapshot_contains`) | All flows | -- |
| Failure diagnostics (`_handle_failure`) | All flows | -- |
| `WAIT_TIMEOUT`, `E2E_SCREENSHOT_DIR` | All flows | -- |
| Fill via eval (login) | No | gate-login-flow.sh |
| Click via eval (login) | No | gate-login-flow.sh |

> **Warning**: Running `/e2e-compile gate-login-flow` will overwrite the manual eval patches. Re-apply them after recompilation. See [e2e-compile Common Mistakes](../skills/e2e-compile/SKILL.md).

---

## Tips

- **Start small.** Add one or two flows to the matrix, verify the workflow runs, then add more.
- **Preview URLs.** For Netlify/Vercel, pipe the preview URL from a deploy job into `E2E_BASE_URL`.
- **No auth?** Remove the `auth-setup` job entirely and drop `needs: [auth-setup]` from `browser-e2e`.
- **Quarantine off?** Remove the quarantine steps from `report` if you want a simpler pass/fail gate.
- **Re-compile after flow changes.** Editing a flow YAML requires re-running `/e2e-compile` and committing the updated `.sh` file.
- **Metrics rotation.** Use `--rotate` to prevent unbounded metrics file growth -- keeps 2x window per flow.
- **Set `WAIT_TIMEOUT=30` for deploy previews.** Default 10s is too short for cold starts on Netlify/Vercel preview deploys.
- **Always use `AGENT_BROWSER_PROFILE`** for auth session sharing across CI jobs. Don't use `agent-browser session dir`.
- **CLI-only flow recording in CI.** If your matrix includes CLI-only flows (zero browser steps), install `asciinema` and `agg` in the runner: `sudo apt-get install -y asciinema && pip install agg` (or `brew install asciinema agg` on macOS runners). Without them, terminal recording is skipped but tests still run.

## Related

- [Commands](commands.md) -- compiled script flags and environment variables
- [Architecture](architecture.md) -- pipeline design and file structure
- [Recording & Evidence](recording-evidence.md) -- metrics and JUnit output

---

> **Found a better pattern?** [Open a PR](https://github.com/iamcxa/kc-claude-plugins/pulls) to share it.
> **Docs unclear?** Use `/e2e-help --feedback "<description>"` to let us know.
