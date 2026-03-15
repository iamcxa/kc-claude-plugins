# CI Integration

Run E2E tests in GitHub Actions using compiled flow scripts — no Claude Code required at runtime.

## Overview

The pipeline provides a GHA workflow template (`templates/browser-e2e.yml`) with three jobs:

```
auth-setup  →  browser-e2e (matrix)  →  report
```

1. **auth-setup** — runs a login flow once, uploads the browser session as an artifact
2. **browser-e2e** — runs each flow in parallel (matrix strategy), reusing the auth session
3. **report** — aggregates JUnit results, publishes check annotations, evaluates quarantine state

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

> **Why copy instead of install?** The plugin is a Claude Code plugin (`private: true`), not an npm package. CI environments don't have Claude Code — they need the quarantine logic as plain Node.js files with no external dependencies.

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

1. Go to **Settings → Secrets and variables → Actions** in your GitHub repo
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
4. Quarantined flows are excluded from the CI gate — their failures don't block merges
5. Flows that pass consistently (default: 3 consecutive first-attempt passes) are **recovered**

### GitHub issue lifecycle

With `--manage-issues`, the quarantine CLI:
- **Creates** a GitHub issue when a flow is quarantined (labeled `e2e-flaky` + flow name)
- **Closes** the issue with a recovery summary when the flow stabilizes
- **Adds** an `e2e-stale` label if a flow stays quarantined beyond the stale threshold (default: 14 days)
- **Deduplicates** — won't create a new issue if one already exists for that flow

### PR comments

With `--pr-comment <number>`, a status table is posted to the PR showing all quarantined flows, their flaky rates, and last failure dates. The comment is updated (not duplicated) on subsequent runs.

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

## Mapping Staleness Detection

The `auth-setup` job includes a staleness check that compares mapping file dates against UI source changes:

```yaml
- name: Check mapping staleness
  run: |
    UI_PATHS="src/ app/ pages/ components/"   # CUSTOMIZE
    # ... warns if mapping hasn't been updated since UI changes
```

Customize `UI_PATHS` to match your project's frontend source directories. The check emits `::warning::` annotations — it doesn't fail the build.

---

## Tips

- **Start small.** Add one or two flows to the matrix, verify the workflow runs, then add more.
- **Preview URLs.** For Netlify/Vercel, pipe the preview URL from a deploy job into `E2E_BASE_URL`.
- **No auth?** Remove the `auth-setup` job entirely and drop `needs: [auth-setup]` from `browser-e2e`.
- **Quarantine off?** Remove the quarantine steps from `report` if you want a simpler pass/fail gate.
- **Re-compile after flow changes.** Editing a flow YAML requires re-running `/e2e-compile` and committing the updated `.sh` file.
- **Metrics rotation.** Use `--rotate` to prevent unbounded metrics file growth — keeps 2x window per flow.
