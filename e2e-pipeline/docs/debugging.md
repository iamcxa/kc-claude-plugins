# Debugging

## Approach by failure type

### Static issues (always reproducible)

The problem is visible every time -- a broken button, wrong text, missing element.

```
/e2e-walkthrough
```

Describe the reported issue. The skill plans a walkthrough targeting the affected area. As you step through:

- **Snapshots** show the accessibility tree -- missing elements or wrong roles are immediately visible
- **Screenshots** capture the visual state
- **Console/error buffers** catch JS exceptions
- **Trace analysis** flags failed API calls

The walkthrough generates a flow that captures the broken state. After fixing, re-run the flow to confirm the fix:

```
/e2e-test <flow-name>
```

### Dynamic issues (specific conditions required)

The bug only appears under certain conditions -- specific data, user role, or navigation sequence.

1. **Set up the condition** by writing a flow with the specific preconditions:

   ```yaml
   steps:
     - id: setup-condition
       action: Navigate to /settings
     - id: change-role
       action: Click role_selector on settings
     - id: select-admin
       action: Click admin_option on settings
     - id: navigate-to-bug
       action: Navigate to /dashboard
     - id: verify-bug
       action: Verify broken_element on dashboard
       expect: broken_element visible on dashboard
   ```

2. Or use a guided walkthrough to reproduce the exact sequence:

   ```
   /e2e-walkthrough
   ```

   Describe the conditions: "Navigate to settings, switch role to admin, then go to dashboard -- the chart should show but it's blank." The skill plans the sequence and you walk through it.

3. The trace captures the full network + console history leading up to the failure, making root cause visible.

### Intermittent issues (requires multiple attempts)

The bug appears randomly -- race conditions, timing issues, flaky state.

1. **Create the flow** for the problematic sequence (write manually or via walkthrough)

2. **Run it multiple times** to catch the failure:

   ```
   /e2e-test flaky-flow
   ```

   Repeat across runs. Each run produces a separate report in `.claude/e2e/reports/<timestamp>/` with its own trace.

3. **Compare traces** across passing and failing runs. The trace analyzer extracts API failures and console errors -- diff these to isolate what's different in failing runs.

4. **Use `/e2e-skill-ops --evaluate`** after collecting several runs to classify failures by pattern:

   ```
   /e2e-skill-ops --evaluate
   ```

   This aggregates results, distinguishes recurring vs one-off failures, and identifies skill/mapping gaps.

5. Once the root cause is found and fixed, keep the flow as a **regression test** tagged for smoke:

   ```yaml
   tags: [smoke, regression, flaky-fix]
   ```

### Runtime data shape issues (wrong data, not wrong UI)

The UI renders correctly but shows wrong data, empty lists, or stale values. The DOM and selectors are fine -- the bug is in the data flow between API responses and component state.

```
/e2e-debug "workspace list shows 0 items but API returns 42"
```

The `/e2e-debug` skill injects `console.log` probes at key data flow points (API response handlers, hook returns, state updates), opens a browser to reproduce the issue, and reads the logged values to pinpoint where data is lost or transformed incorrectly. See [Runtime Debugging with /e2e-debug](#runtime-debugging-with-e2e-debug) below for the full workflow.

**When to use `/e2e-debug` vs `/e2e-walkthrough`:**

| Symptom | Tool | Why |
|---------|------|-----|
| Element missing, button broken, wrong page | `/e2e-walkthrough` | UI structure issue -- snapshots + screenshots reveal it |
| Data wrong, list empty, stale cache, wrong count | `/e2e-debug` | Data flow issue -- `console.log` probes reveal it |
| Not sure | `/e2e-debug` with `--headed` | Headed mode lets you see the UI while probes capture data |

---

## Runtime Debugging with /e2e-debug

The `/e2e-debug` skill runs an **inject-observe-cleanup** pipeline for diagnosing frontend runtime bugs -- particularly data shape issues that are invisible to screenshot/snapshot-based testing.

### The workflow

```
Phase 0: Analyze     -- identify suspect code, form hypothesis, pick injection points
Phase 1: Inject      -- insert [E2E-DBG] console.log probes into source files
Phase 2: Observe     -- open browser, reproduce the bug, collect console output (via e2e-debug-observe agent)
Phase 3: Diagnose    -- cross-reference observed values with expected values, identify root cause
Phase 4: Cleanup     -- remove ALL injected code (mandatory, runs even if prior phases fail)
```

### Basic usage

Describe the bug in natural language:

```
/e2e-debug "the workspace list shows 0 items even though the API returns data"
```

The skill analyzes your codebase, identifies 2-5 key data flow points (API response, state hook, component render), injects `console.log('[E2E-DBG:module:variable]', JSON.stringify(value))` at each point, opens a browser to reproduce, and reads the output to find where the data gets lost.

### Headed mode for manual auth

When the target page requires authentication that cannot be handled by an agent-browser profile:

```
/e2e-debug "dashboard shows stale data" --headed --url http://localhost:3000/dashboard
```

The browser opens visibly. You log in manually, then tell the skill to continue. The agent resumes from where you left off.

### Multi-round debugging with --continue

If the first round narrows the problem but does not pinpoint it:

```
/e2e-debug --continue
```

The skill reads the previous round's history (`.claude/e2e/debug/history/`), loads its observations and conclusions, and generates new injection points based on what was learned. Each round cleans up before the next.

### Experiment mode for systematic-debugging integration

When another skill (e.g., `systematic-debugging`) has already analyzed the problem and knows exactly what to probe:

```
/e2e-debug --experiment \
  --inject '[{"file":"src/hooks/useWorkspaces.ts","line":42,"tag":"hook-return","code":"console.log(\"[E2E-DBG:useWorkspaces:data]\", JSON.stringify(data));"}]' \
  --steps "Navigate to /dashboard; Wait for network idle; Observe workspace list" \
  --url http://localhost:3000/dashboard
```

Experiment mode skips the analysis phase entirely. All three flags (`--inject`, `--steps`, `--url`) are required. The skill injects, observes, and returns a structured `experiment_result` YAML without user interaction.

### Force cleanup

If a previous session crashed and left `[E2E-DBG]` markers in your source code:

```
/e2e-debug --cleanup
```

This skips all phases and runs only the cleanup pipeline (manifest-driven removal, then grep fallback, then verification).

### What the agent collects

The `e2e-debug-observe` agent (dispatched during Phase 2) captures:

| Data | Method |
|------|--------|
| `[E2E-DBG]` console logs | `agent-browser console --json` filtered by tag |
| JS errors | `agent-browser errors --json` |
| Network requests | `agent-browser network requests` (with optional URL filters) |
| Storage/cookie changes | `agent-browser storage local/session` + `agent-browser cookies` diff against baseline |
| HAR recording | `agent-browser network har start/stop` for full request/response bodies |
| Screenshots per step | `agent-browser screenshot --annotate` |

Storage and cookie diffing is particularly useful for diagnosing auth token mutations, cache invalidation issues, and session state corruption -- the agent captures baselines before reproduction and reports only changed entries.

### Output files

```
.claude/e2e/debug/
|- manifest.yaml          # injection registry (deleted after cleanup)
|- report.md              # observation report from agent (deleted after cleanup)
|- history/               # round history (persisted for --continue)
|   |- <session>-r1.yaml
|   +-- <session>-r2.yaml
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `agent-browser not found` | Install globally: see [agent-browser](https://github.com/anthropics/agent-browser) |
| Auth expired during test | Delete `~/.agent-browser/<app>/` and re-login |
| Selectors stale | Re-run `/e2e-map --page <page>` to refresh |
| Flow uses v1 format | Migrate: `app:` -> `mapping:`, step `name:` -> `id:`, structured expects -> grammar strings |
| Test keeps failing on one step | Run `/e2e-skill-ops --debug` to diagnose |
| `node_modules/` missing for compiler | Run `npm install` in the plugin directory |
| Compiled script fails with `command not found` | Ensure `agent-browser` is on PATH; check `chmod +x` on the script |
| Coverage report shows 0% | Verify mapping file matches the flow's `mapping:` field |
| CLI recording skipped (agg/asciinema missing) | Install: `brew install asciinema agg`. Required only for CLI-only flows (zero browser steps). |
| Residual `[E2E-DBG]` markers in source | Run `/e2e-debug --cleanup` to remove them. Nuclear option: `git checkout -- <file>` |
| `/e2e-debug` cleanup missed some files | Check non-standard directories. Cleanup scans `apps/ src/ lib/ components/` by default. |
| `eval_fallback_hits > 0` in test report | A step's selector failed native resolution and the runner fell through to JS eval. Re-run `/e2e-map` for the affected page or fix the selector to a native form (`role=<r>[name="<v>"]`, `text=<v>`, or `[data-testid="…"]` — see `CLAUDE.md` § Selector Priority). Bound the metric with `scripts/measure-fallback-baseline.sh` -- see [CI Integration](ci-integration.md#fallback-counter-baseline-scriptsmeasure-fallback-baselinesh). |
| Mapping fails `lint-mapping.sh` | Banned token in mapping (`>> nth=N`, `has-text(`, or `find role\|text\|label\|testid ...` stored as a `selector:` value). Replace per the [linter table](ci-integration.md#selector-policy-compilerlibselector-policyjs) and re-run `/e2e-map` to regenerate. |

For deeper diagnostics: `/e2e-skill-ops --debug`

## Interpreting Divergence Analysis

When `/e2e-test` runs, it auto-compiles the flow and runs both the LLM agent and the compiled script. The divergence table shows where they disagree:

| Pattern | Meaning | Action |
|---------|---------|--------|
| Both PASS | High confidence — step works reliably | None |
| LLM PASS, Compiled FAIL | Selector may be timing-sensitive. LLM used snapshot `@ref` (adaptive), compiled uses static selector. | Add `wait_after` or increase `timeout` in the flow step |
| LLM FAIL, Compiled PASS | LLM may have hallucinated a failure. The compiled script is authoritative. | Verify the step manually; trust compiled result |
| Both FAIL | Genuine bug in the app or incorrect test | Fix the app or update the flow |

**Zero diverged steps** = both modes agree on every step. This is the highest confidence level — the test is deterministic and reliable.

**When to use `--no-compile`:** Skip divergence when you only care about the LLM run (debugging a specific interaction) or the compiler is not installed (`node_modules/` missing).

## Observe-and-Continue Model

During `/e2e-walkthrough`, the browser agent follows an **observe-and-continue** execution model:

1. Execute step action
2. Check `errors --json` for console errors
3. Visual observation — unexpected UI?
4. **Record anomaly + notify** — but **never pause**
5. Continue to next step

Anomalies (console errors, visual issues, unexpected state) are logged inline with a `⚠` marker but do not interrupt the walkthrough. Full analysis happens in **Phase 4** where trace data is cross-referenced with the step log to identify root causes.

**The only exception**: auth expiration pauses the walkthrough, because all subsequent steps would fail without authentication.

**Why this model?** Stopping for every anomaly breaks flow and makes walkthroughs painfully slow. Many anomalies are transient (analytics errors, non-blocking console warnings). By continuing, the walkthrough captures the complete picture — Phase 4 trace analysis is far better at distinguishing real issues from noise than per-step interruption.

## Related

- [Commands](commands.md) -- all skills and flags
- [Writing Tests](writing-tests.md) -- flow YAML format and preconditions
- [Recording & Evidence](recording-evidence.md) -- trace replay and PR evidence
- [Self-Improvement](self-improvement.md) -- how debugging findings feed back into pipeline learning
- [Architecture](architecture.md) -- pipeline design and skill-to-agent model

---

> **Found a better pattern?** [Open a PR](https://github.com/iamcxa/kc-claude-plugins/pulls) to share it.
> **Docs unclear?** Use `/e2e-help --feedback "<description>"` to let us know.
