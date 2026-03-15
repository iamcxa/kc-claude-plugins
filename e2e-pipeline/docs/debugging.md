# Debugging

## Approach by failure type

### Static issues (always reproducible)

The problem is visible every time — a broken button, wrong text, missing element.

```
/e2e-walkthrough
```

Describe the reported issue. The skill plans a walkthrough targeting the affected area. As you step through:

- **Snapshots** show the accessibility tree — missing elements or wrong roles are immediately visible
- **Screenshots** capture the visual state
- **Console/error buffers** catch JS exceptions
- **Trace analysis** flags failed API calls

The walkthrough generates a flow that captures the broken state. After fixing, re-run the flow to confirm the fix:

```
/e2e-test <flow-name>
```

### Dynamic issues (specific conditions required)

The bug only appears under certain conditions — specific data, user role, or navigation sequence.

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

   Describe the conditions: "Navigate to settings, switch role to admin, then go to dashboard — the chart should show but it's blank." The skill plans the sequence and you walk through it.

3. The trace captures the full network + console history leading up to the failure, making root cause visible.

### Intermittent issues (requires multiple attempts)

The bug appears randomly — race conditions, timing issues, flaky state.

1. **Create the flow** for the problematic sequence (write manually or via walkthrough)

2. **Run it multiple times** to catch the failure:

   ```
   /e2e-test flaky-flow
   ```

   Repeat across runs. Each run produces a separate report in `e2e-reports/<timestamp>/` with its own trace.

3. **Compare traces** across passing and failing runs. The trace analyzer extracts API failures and console errors — diff these to isolate what's different in failing runs.

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
| Flow uses v1 format | Migrate: `app:` → `mapping:`, step `name:` → `id:`, structured expects → grammar strings |
| Test keeps failing on one step | Run `/e2e-skill-ops --debug` to diagnose |
| `node_modules/` missing for compiler | Run `npm install` in the plugin directory |
| Compiled script fails with `command not found` | Ensure `agent-browser` is on PATH; check `chmod +x` on the script |
| Coverage report shows 0% | Verify mapping file matches the flow's `mapping:` field |

For deeper diagnostics: `/e2e-skill-ops --debug`
