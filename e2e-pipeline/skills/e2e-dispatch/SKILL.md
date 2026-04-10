---
name: e2e-dispatch
description: Use when the user invokes /e2e-dispatch or asks for the E2E operations menu. Router — prefer e2e-test, e2e-map, e2e-walkthrough, e2e-skill-ops directly for specific operations.
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
| `--flow [--from source]` | `/e2e-dispatch --flow --from plan.md` |
| `--flow --smoke` | `/e2e-dispatch --flow --smoke` |
| `--flow --verify-only` | `/e2e-dispatch --flow --verify-only login-flow` |
| `--analyze <path>` | `/e2e-dispatch --analyze .claude/e2e/reports/trace.zip` |
| `--compile [flow]` | `/e2e-dispatch --compile login-flow` |
| `--compile --all` | `/e2e-dispatch --compile --all` |
| `--ops [mode]` | `/e2e-dispatch --ops --debug` |

No args or ambiguous request: present the routing menu and ask user to choose:

> **Available E2E operations:**
> 1. `--test` — Run E2E test flows (single flow, suite, tag, or all)
> 2. `--map` — Create or update UI element mappings
> 3. `--flow` — Generate & verify E2E flows from plans/specs/PRs, or smoke test
> 4. `--walk` — Interactive walkthrough / explore UI
> 5. `--analyze` — Analyze a Playwright trace file
> 6. `--compile` — Compile flow YAML to standalone bash test scripts
> 7. `--ops` — Debug, maintain, or evaluate E2E skills
> 8. `--help` — Interactive help guide & topic deep-dive
> 9. `--doc-sync` — Scan docs for gaps, write updates
> 10. `/e2e-debug` — Debug frontend runtime bugs (inject logs → browser observe → cleanup) *(direct skill — not dispatched, suggest user invoke directly)*
>
> Which operation? (or describe what you want to do)

**Routing priority** (when user intent matches multiple routes):
1. Explicit `--flag` → use that route directly
2. Natural language with clear action verb → match: "test/run flow" → `--test`, "record/map" → `--map`, "generate flow/verify flow/smoke test" → `--flow`, "walk/explore/browse" → `--walk`, "analyze/trace" → `--analyze`, "compile/generate script/bash script" → `--compile`, "fix skill/maintain skill/evaluate skill" → `--ops`, "help/how/what commands" → `--help`, "doc/sync docs/update docs" → `--doc-sync`, "debug runtime/inject logs/browser debug/data shape/why is X empty" → suggest `/e2e-debug` (direct invocation)

**"debug" disambiguation**: The word "debug" alone is ambiguous — ask the user to clarify:
   - Debug a **skill/pipeline issue** (e.g., "e2e-test is broken", "mapper fails") → `--ops --debug`
   - Debug a **frontend runtime bug** (e.g., "login button does nothing", "data not showing") → `/e2e-debug`
   - If user says "debug" + mentions a skill name → `--ops --debug`
   - If user says "debug" + describes UI/runtime symptoms → `/e2e-debug`
   - If unclear → ask: "Are you debugging an e2e pipeline skill, or a frontend runtime bug?"
3. Ambiguous → present the menu above and ask user to clarify

**Unknown command** (e.g., `--deploy`, `--something`): respond with "Unknown e2e operation. Available operations:" + the menu above.

## Auth Gate

**Applies to**: `--test`, `--map`, `--flow`, `--walk` only (browser operations).
**Skipped for**: `--analyze`, `--compile`, `--ops`, `--help`, `--doc-sync`, `/e2e-debug` (no browser needed).

1. **Determine app name** from the arguments:
   - `--test`: resolve flow file → read `mapping:` field → load mapping → `app` field
   - `--test --suite`: resolve suite → collect all unique site mappings → `app` fields (check all)
   - `--map <app>`: use the `<app>` argument directly
   - `--flow`: resolve mapping from `--mapping` arg or auto-discover → `app` field
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

### --flow
Invoke `Skill: "e2e-flow"` with --from, --smoke, --verify-only, --mapping, --pr, --issue, --no-verify, --no-video arguments.
The e2e-flow skill runs codebase scan then dispatches flow-writer + flow-verifier agents.

### --walk
Invoke `Skill: "e2e-walkthrough"` with mapping name and any --mode, --sites, --pr, --issue, **--no-video** arguments.
Runs entirely in main context (interactive).

**Rerouting:** If `--walk` is combined with `--smoke` or `--verify`, redirect to `--flow`:
- `--walk --smoke` → `--flow --smoke` (smoke test is now automated via flow-writer)
- `--walk --verify` → `--flow --verify-only` (verification is now automated via flow-verifier)

Forward all additional flags to the target route (e.g., `--walk --smoke --site carlove` → `--flow --smoke --site carlove`). The mapping argument from `--walk` becomes the `--mapping` argument for `--flow`.

### --analyze
Dispatch directly — no skill needed:
```
Agent(subagent_type="e2e-trace-analyzer"):
  trace_path: <absolute path to trace.zip>
  report_dir: <dirname of trace_path>
```
Present summary when agent returns.

### --compile
Invoke `Skill: "e2e-compile"` with flow name or --all arguments.
The e2e-compile skill compiles flow YAML to standalone bash test scripts.

### --ops
Invoke `Skill: "e2e-skill-ops"` with --debug/--maintain/--add-feature/--evaluate mode.

### --help
Invoke `Skill: "e2e-help"` with topic name or --feedback arguments.

### --doc-sync
Invoke `Skill: "e2e-doc-sync"` with --fix or --check arguments.

## Background vs Foreground

| Route | Default | Override |
|-------|---------|---------|
| `--test` | Background | `--fg` for foreground |
| `--map` (no --interactive) | Background | `--fg` for foreground |
| `--map --interactive` | Foreground | — |
| `--flow` | Foreground | — |
| `--walk` | Foreground | — |
| `--analyze` | Background | `--fg` for foreground |
| `--compile` | Foreground | — |
| `--ops` | Foreground | — |
| `--help` | Foreground | — |
| `--doc-sync` | Foreground | — |

Background = `run_in_background: true` on Agent dispatch. Main context free for other work.
Foreground = wait for completion, interactive.

## Backward Compatibility

Direct invocation of any target skill (`/e2e-test`, `/e2e-map`, `/e2e-flow`, `/e2e-walkthrough`, `/e2e-compile`, `/e2e-skill-ops`, `/e2e-help`, `/e2e-doc-sync`, `/e2e-debug`) still works.
`/e2e-dispatch` is a convenience unified entry point — not required.

## Quick Reference

| Need | Command |
|------|---------|
| Run one flow | `/e2e-dispatch --test login-flow` |
| Smoke suite | `/e2e-dispatch --test --suite smoke` |
| All smoke tagged | `/e2e-dispatch --test --tag smoke` |
| Map new app | `/e2e-dispatch --map my-app` |
| Update one page | `/e2e-dispatch --map my-app --page dashboard` |
| Generate flow from plan | `/e2e-dispatch --flow --from plan.md` |
| Smoke test all pages | `/e2e-dispatch --flow --smoke` |
| Verify existing flow | `/e2e-dispatch --flow --verify-only login-flow` |
| Interactive explore | `/e2e-dispatch --walk admin-panel` |
| Analyze trace | `/e2e-dispatch --analyze .claude/e2e/reports/20260306/trace.zip` |
| Compile one flow | `/e2e-dispatch --compile login-flow` |
| Compile all flows | `/e2e-dispatch --compile --all` |
| Debug skill issue | `/e2e-dispatch --ops --debug` |
| Record a test run | `/e2e-dispatch --test login-flow --video` |
| Walkthrough no video | `/e2e-dispatch --walk admin-panel --no-video` |
| Get help on suites | `/e2e-dispatch --help suites` |
| Report doc gap | `/e2e-dispatch --help --feedback "suite subset"` |
| Sync docs after changes | `/e2e-dispatch --doc-sync --fix` |
