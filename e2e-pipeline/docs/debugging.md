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
