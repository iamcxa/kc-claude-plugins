---
name: e2e-dispatch
description: Use when the user explicitly invokes /e2e-dispatch or asks for the E2E operations menu without specifying a particular operation. This is a unified router — for specific operations, prefer e2e-test, e2e-map, e2e-walkthrough, or e2e-skill-ops directly.
---

# E2E Dispatch — Unified Entry Point

Route E2E operations to the correct executor with auth pre-flight.

## Invocation

```
/e2e-dispatch <intent> [options]
```

| Argument | Example |
|----------|---------|
| `--test <flow>` | `/e2e-dispatch --test login-flow` |
| `--test --tag <tag>` | `/e2e-dispatch --test --tag smoke` |
| `--test --suite <name>` | `/e2e-dispatch --test --suite smoke` |
| `--test --all` | `/e2e-dispatch --test --all` |
| `--map <app>` | `/e2e-dispatch --map my-app` |
| `--map --interactive` | `/e2e-dispatch --map my-app --interactive` |
| `--walk [mapping]` | `/e2e-dispatch --walk admin-panel` |
| `--analyze <path>` | `/e2e-dispatch --analyze e2e-reports/trace.zip` |
| `--ops [mode]` | `/e2e-dispatch --ops --debug` |

No args or ambiguous request: present the routing menu and ask user to choose:

> **Available E2E operations:**
> 1. `--test` — Run E2E test flows (single flow, suite, tag, or all)
> 2. `--map` — Create or update UI element mappings
> 3. `--walk` — Interactive walkthrough / explore UI
> 4. `--analyze` — Analyze a Playwright trace file
> 5. `--ops` — Debug, maintain, or evaluate E2E skills
>
> Which operation? (or describe what you want to do)

**Routing priority** (when user intent matches multiple routes):
1. Explicit `--flag` → use that route directly
2. Natural language with clear action verb → match: "test" → `--test`, "record/map" → `--map`, "walk/explore/browse" → `--walk`, "analyze/trace" → `--analyze`, "debug/fix skill" → `--ops`
3. Ambiguous → present the menu above and ask user to clarify

**Unknown command** (e.g., `--deploy`, `--something`): respond with "Unknown e2e operation. Available operations:" + the menu above.

## Auth Gate

**Applies to**: `--test`, `--map`, `--walk` (NOT `--analyze` or `--ops`)

1. **Determine app name** from the arguments:
   - `--test`: resolve flow file → read `mapping:` field → load mapping → `app` field
   - `--test --suite`: resolve suite → collect all unique site mappings → `app` fields (check all)
   - `--map <app>`: use the `<app>` argument directly
   - `--walk [mapping]`: read mapping file → `app` field

2. **Check auth profile exists**:
   ```bash
   ls ~/.agent-browser/<app>/ 2>/dev/null && echo "EXISTS" || echo "MISSING"
   ```

3. **Check server reachable**:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" <base_url>
   ```
   Any 2xx or 3xx = OK. Fail → report and stop.

4. **Profile missing or expired**:
   - Open headed browser: `agent-browser --profile ~/.agent-browser/<app> --headed open <base_url>`
   - Present mapping's `auth.manual_prompt` (or default: "Please complete login in the browser. Let me know when done.")
   - After user confirms → `agent-browser get url` → verify against `auth.verification`
   - Verified → close browser (`agent-browser close`), proceed to dispatch
   - Not verified → re-prompt (max 3 attempts) → stop on failure

5. **Auth gate pass** → proceed to dispatch

## Dispatch

### --test
Invoke `Skill: "e2e-test"` with the original arguments (flow name, --tag, --suite, --all, --pr, --issue, **--video**).
The e2e-test skill handles flow resolution and dispatches e2e-test-runner agent(s).

### --map (non-interactive)
Invoke `Skill: "e2e-map"` with --scope and --page arguments.
The e2e-map skill runs codebase analysis then dispatches e2e-mapper agent.

### --map --interactive
Invoke `Skill: "e2e-map"` — runs entirely in main context (interactive mode).

### --walk
Invoke `Skill: "e2e-walkthrough"` with mapping name and any --mode, --smoke, --sites, --pr, --issue, **--no-video** arguments.
Runs entirely in main context (interactive).

### --analyze
Dispatch directly — no skill needed:
```
Agent(subagent_type="e2e-trace-analyzer"):
  trace_path: <absolute path to trace.zip>
  report_dir: <dirname of trace_path>
```
Present summary when agent returns.

### --ops
Invoke `Skill: "e2e-skill-ops"` with --debug/--maintain/--add-feature/--evaluate mode.

## Background vs Foreground

| Route | Default | Override |
|-------|---------|---------|
| `--test` | Background | `--fg` for foreground |
| `--map` (no --interactive) | Background | `--fg` for foreground |
| `--map --interactive` | Foreground | — |
| `--walk` | Foreground | — |
| `--analyze` | Background | `--fg` for foreground |
| `--ops` | Foreground | — |

Background = `run_in_background: true` on Agent dispatch. Main context free for other work.
Foreground = wait for completion, interactive.

## Backward Compatibility

Direct invocation of `/e2e-test`, `/e2e-map`, `/e2e-walkthrough`, `/e2e-skill-ops` still works.
`/e2e-dispatch` is a convenience unified entry point — not required.

## Quick Reference

| Need | Command |
|------|---------|
| Run one flow | `/e2e-dispatch --test login-flow` |
| Smoke suite | `/e2e-dispatch --test --suite smoke` |
| All smoke tagged | `/e2e-dispatch --test --tag smoke` |
| Map new app | `/e2e-dispatch --map my-app` |
| Update one page | `/e2e-dispatch --map my-app --page dashboard` |
| Interactive explore | `/e2e-dispatch --walk admin-panel` |
| Analyze trace | `/e2e-dispatch --analyze e2e-reports/20260306/trace.zip` |
| Debug skill issue | `/e2e-dispatch --ops --debug` |
| Record a test run | `/e2e-dispatch --test login-flow --video` |
| Walkthrough no video | `/e2e-dispatch --walk admin-panel --no-video` |
