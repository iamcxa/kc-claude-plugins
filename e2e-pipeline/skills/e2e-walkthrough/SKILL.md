---
name: e2e-walkthrough
description: Use when walking through UI flows interactively, exploring features with human guidance, or visually validating changes in a browser. Records video by default for evidence and communication. Triggers on "walkthrough", "explore this feature", "walk the UI", "step through", "browse the app", "guided e2e", "interactive walkthrough", "record walkthrough", "video walkthrough".
---

# E2E Walkthrough — Interactive UI Exploration

Human-agent collaborative browser walkthrough with trace recording, health monitoring, and reusable flow output.


## Pipeline Context

```
/e2e-map       -> mapping.yaml    (map)
/e2e-walkthrough -> flow.yaml     (explore with human)
/e2e-test      -> report.md       (replay with monitoring)
```

## Invocation

```
/e2e-walkthrough [context] [--mode guided|step|auto] [--sites name1,name2] [--pr N] [--issue ID] [--no-video]
```

| Entry point | Behavior |
|-------------|----------|
| `--pr 940` | Read PR diff, propose path covering changed UI |
| `--issue DRC-2811` | Read issue, propose path for the feature |
| Free text | Use mapping + codebase to propose path |
| `--page org-settings` | Explore all mapped elements on that page |
| `--smoke` | Walk critical paths from mapping |
| `--sites admin,portal` | Cross-site walkthrough using named mappings |
| `--no-video` | Skip screen recording (default: recording ON) |

## Discover Mapping (BLOCKING — must complete before proceeding)

1. Look for `.claude/e2e/mappings/*.yaml`
2. One file: use it. Read `app`, `base_url`, `auth` from the mapping.
3. Multiple files: list them (show filename, `app`, `base_url` for each), ask user which to use (or accept `--mapping <name>`). **After selection, use ONLY the chosen mapping — do not reference pages/elements from other mapping files.**
4. None: "No mapping files found in `.claude/e2e/mappings/`. Mappings define page structure, selectors, and auth config that walkthroughs depend on. Run `/e2e-map` to create one first." **Stop — do NOT continue to Pre-Flight.**
5. If mapping YAML fails to parse: report the parse error with line number and stop. "Mapping file `<path>` has invalid YAML at line N. Fix the syntax error or re-run `/e2e-map` to regenerate."

### Multi-Site Discovery (when `--sites` provided)

1. Parse `--sites` argument: comma-separated mapping names (filename without `.yaml`)
2. Load each mapping from `.claude/e2e/mappings/<name>.yaml`. If any not found -> report and stop.
3. Assign aliases: use the mapping's `app` field as the alias
4. Present merged page list:

```
Available pages:
  [admin-panel] users_page, dashboard, settings
  [customer-portal] projects_page, user_profile, billing

Which page to start? >
```

## Prerequisites & Pre-Flight

**After Discover Mapping completes, proceed to Pre-Flight.** These checks use `base_url` and `app` from the **selected** mapping.

1. **agent-browser** installed globally
2. **Dev server running** (read `base_url` from mapping)
3. **Auth profile** (derived from mapping `app`: `~/.agent-browser/<app>`)
4. **`--headed` mode** — human must see the browser (NOT headless)

```bash
agent-browser --version
curl -s -o /dev/null -w "%{http_code}" <base_url>
ls ~/.agent-browser/<app>/ 2>/dev/null && echo "OK" || echo "MISSING"
```

If agent-browser is not installed, stop and report: "agent-browser is required for browser automation. Install from https://github.com/nicobrinkkemper/agent-browser." If the dev server is unreachable, stop and report: "Cannot reach `<base_url>`. The walkthrough navigates real pages so the dev server must be running. Start it and retry." Any 2xx or 3xx HTTP response means the server is running (3xx is normal for auth-protected apps that redirect to login).

**After Pre-Flight passes, proceed to Phase 1.**

**First-Run Auth (if profile missing):**

- If `auth.type: none` in mapping: skip auth entirely. Profile auto-creates on first `open`.
- **Automated OTP path**: If mapping has `auth.test_accounts` with phone numbers AND the project has Supabase `config.toml` with `[auth.sms.test_otp]` entries, automate login: navigate to signin path → fill phone number (strip country code if UI has country selector) → submit → fill OTP from config → submit → verify URL. This avoids blocking on human input for local dev environments.
- **Manual path**: If no test accounts or OTP config available, open browser `agent-browser --profile ~/.agent-browser/<app> --headed open <base_url>`, read `auth.manual_prompt` from mapping and relay it to the user (e.g., "Please complete login in the browser"). After user confirms → `agent-browser get url` and verify using `auth.verification.url_not_contains` from mapping (`url_not_contains` performs a **substring check** on the full URL). If verification fails, re-prompt user. Repeat until verified or user aborts. Profile persists — login is one-time only.

## Phase 1 — Plan

1. Read context: PR diff (`gh pr diff`), issue description (Linear MCP), or human's text
2. Read discovered mapping file
3. Cross-reference: which pages/elements/dialogs are relevant to the context
4. Propose numbered walkthrough steps with concrete actions

### `--smoke` Mode

When invoked with `--smoke`, auto-generate a walkthrough plan from the mapping:

1. **Select pages** using these rules (in order):
   a. Include pages with non-empty `elements:` AND a navigable `url_pattern` (no unresolvable parameters like `${traceId}`, `${sessionId}`)
   b. Skip pages whose `url_pattern` contains parameters that require external state (e.g., `${traceId}`, `${sessionId}`)
   c. Skip pages that match the mapping's `auth.signin_path` (navigating there would log out the session)
   d. Skip pages with `note:` containing "Requires admin" or "admin access" — unless explicitly included by user
   e. **RBAC-aware filtering**: Elements with `note:` containing role requirements (e.g., "Requires auditor/manager role") should be marked `expected: conditional` in the plan when the current test account's role doesn't match. These are NOT failures — report as "expected not visible for [role]" rather than MISMATCH.
   f. For onboarding pages: include only if the user is in onboarding state (or mark with `optional: true` in generated steps)
2. **Ordering**: shared sidebar verification first, then main pages, then settings, then onboarding
3. **Per page**: Navigate → verify 2-3 key elements exist (prefer headings and primary buttons) → take screenshot.
4. **Interactions**: For pages with dialogs in the `dialogs:` section, include one open-close cycle for the primary dialog (first dialog whose `trigger_page` matches the current page).
5. **Auth state**: Smoke plans assume an authenticated session. Login flows should run separately before smoke. Flows that assume authenticated state should document `precondition: Authenticated`.
6. **Total steps**: Aim for 2-3 steps per page. Present proposed plan before execution.
7. **Post-walkthrough selector sweep**: After all navigation steps, run a dedicated `is visible` verification pass for all `data-testid` and `aria-label` selectors in the mapping. The a11y snapshot does NOT expose these attributes — only `is visible` can confirm they exist in the DOM. Group tests by page to minimize navigation.

Present the plan conversationally. If context is vague, ask clarifying questions.

**After plan is presented, proceed to Phase 2 for human approval.**

```
Based on PR #940:

Proposed walkthrough (8 steps):
1. Navigate to org-settings
2. Click "Add Connection" -> dialog opens
3. Fill form with test data
...

Mode: guided (default). Adjust? Or "go" to start.
```

### Cross-Site Plan

When `--sites` is provided, the walkthrough plan includes site transitions:

```
Proposed walkthrough (6 steps):
1. [admin] Navigate to users_page
2. [admin] Click create_user_button
3. [admin] Fill user form
4. [portal] Navigate to /users -> verify user appears
5. [portal] Open user detail -> grant permission
6. [admin] Navigate to /users -> verify permission

Mode: guided. Adjust? Or "go" to start.
```

## Phase 2 — Approve & Configure

Human adjusts the plan via natural conversation:

- **"go"** -> start execution
- **Add/remove/reorder steps** -> agent updates plan
- **"auto mode"** -> switch interaction mode
- **"actually walk onboarding instead"** -> back to Phase 1
- **"pay attention to console errors on submit"** -> agent adds focus area

**After human says "go" (or equivalent), proceed to Phase 3.**

## Phase 3 — Execute & Monitor

For detailed execution mechanics (startup, multi-site, per-step loop, health checks, anomaly handling), see [reference.md](./reference.md).

**Summary**: Open browser (without `--profile` when recording) → verify auth (auto-login if needed) → **start recording** → start trace → execute steps in chosen interaction mode → track mapping discrepancies.

**Start recording** (unless `--no-video`):

```bash
agent-browser record start "$REPORT_DIR/full.webm"
```

> **Note**: `record start` is incompatible with `--profile` sessions (v0.16.x). When recording is ON, open the browser WITHOUT `--profile` and handle auth via auto-login or manual prompt. See [reference.md](./reference.md) § Startup for details.

**Per-step loop**: snapshot → action via `@ref` → wait networkidle → screenshot → health check → report to human.

**Interaction modes**: Guided (default, show plan + summary), Step (wait "go" between steps), Auto (silent, log anomalies).

**On anomaly**: Track mapping discrepancies (stale selectors, missing elements, trigger mismatches, new elements) for Phase 4 self-repair. On step failure, offer: continue / debug / stop.

**After all steps complete (or human says "stop here"), proceed to Phase 4.**

## Phase 4 — Output & Learn (STRICT ORDER)

**Execute ALL subsections below in order. Do NOT skip to Browser Handoff.**

For detailed procedures (trace analysis, report templates, flow YAML rules, mapping self-repair), see [reference.md](./reference.md).

1. **Stop recording** (if recording): `agent-browser record stop`
2. **Stop trace**: `agent-browser trace stop "$REPORT_DIR/trace.zip"`
3. **Trace analysis**: Dispatch `e2e-trace-analyzer` subagent with `trace_path` + `report_dir`
4. **Report (dual output, MANDATORY)**: Write both `$REPORT_DIR/report.md` (full artifact: flowchart + step results + health log + observations + artifacts) and `$REPORT_DIR/pr-summary.md` (PR reviewer version: inline screenshots + flowchart + step table + video). See [reference.md](./reference.md) § Report for templates.
5. **GIF generation** (if recording): see `references/commands.md` § GIF Generation for the canonical ffmpeg command. Warn but continue if ffmpeg fails.
6. **MP4 video conversion** (if recording): see `references/commands.md` § MP4 Video Conversion. Default 1.5x speed. Warn but continue if ffmpeg fails.
7. **Flow YAML auto-generation (MANDATORY)**: Always auto-generate — never ask. Auto-name: `walkthrough-<timestamp>-<first-page>.yaml`. Write to `.claude/e2e/flows/`
8. **Cross-site flow**: Use `sites:` instead of `mapping:` when `--sites` was used
9. **PR/Issue posting**: If `--pr` provided, ask user to confirm → commit + push screenshots → `gh pr comment` with `pr-summary.md`. See [reference.md](./reference.md) § PR/Issue Posting.
10. **Mapping self-repair**: Present discrepancy list, human approves, patch mapping. 3+ stale on same page → recommend `/e2e-map --page`
11. **Browser handoff (BLOCKING: report + flow YAML must be written first)**: Present summary table, then numbered action menu. Do NOT close browser — user may need to inspect final state.

**Post-completion menu** (always present, numbered):

```
What's next?

1. Post report to PR (pr-summary.md → gh pr comment)
2. Edit flow YAML (already auto-generated — rename or adjust steps)
3. Generate GIF (step screenshot animation)
4. Generate video recording (full viewport)
5. Generate GIF + video (both)
6. Done (browser stays open)
```

- Options 3-5 only shown when recording was active
- Option 1 only shown when `--pr` was provided or user mentioned a PR
- Option 2 is always shown (flow YAML already auto-generated — this option lets user rename/edit)
- **Never close browser without explicit user confirmation**
- Multiple selections allowed (e.g., "1, 2")

### Pipeline Next Steps (MANDATORY — always shown after menu interaction)

After the user completes their menu selection(s) — including selecting "Done" — present context-aware pipeline guidance:

```
Next steps:
- `/e2e-test <flow-name>` — replay this walkthrough automatically (flow saved)
{if anomalies found}
- `/e2e-map --page <page>` — re-scan pages with stale selectors
{endif}
- `/e2e-walkthrough` — explore other features or pages
```

**Rules:**
- Always show `/e2e-test` replay line (flow YAML is always generated)
- Show `/e2e-map` line ONLY when mapping discrepancies were found during this walkthrough
- Always show `/e2e-walkthrough` continue line
- Use the actual generated flow filename in the `/e2e-test` suggestion
- This block appears BEFORE browser close confirmation — the user needs this info while deciding whether to continue

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping Pipeline Next Steps | MANDATORY block — present after every menu interaction, even under context pressure. "User already knows" is not a valid reason to skip. |
| Headless mode for walkthrough | Always `--headed` — human must see browser |
| Acting without snapshot | `snapshot` before every action — a11y tree is source of truth |
| CSS selectors for clicks | Use `@ref` from snapshot. `role=` only for visibility checks |
| `has-text()` selectors | BROKEN in agent-browser — times out. Use `role=button[name="..."]` |
| Screenshot relative paths | agent-browser needs absolute paths (sandbox CWD differs) |
| Forgetting `trace stop` | Trace data lost if browser closes without stopping |
| `scroll` to element | `scroll` only accepts direction (up/down). Use `hover "@ref"` to auto-scroll element into view |
| Reporting noise as errors | Filter known noise per mapping or defaults (HMR, favicon, React DevTools) |
| `is visible` false on CSS-hidden inputs | Ant Design Segmented radio, custom checkboxes — element works but CSS-hidden. Verify via `snapshot` a11y tree presence instead |
| `is visible` exit code always 0 | `agent-browser is visible` returns text "true"/"false" but exit code is always 0. Do NOT chain with `&&` for conditional logic — check stdout text |
| Large table snapshots consume context | Ant Design tables with 10+ rows produce 100+ @ref entries. Use targeted `is visible` checks instead of full snapshot when only verifying element presence |
| Strict mode violation on `aria-label` | React Native Web may render duplicate `aria-label` elements (e.g., two notification buttons). Use `role=button[name="..."] >> nth=0` or add `data-testid` to disambiguate |
| Assuming snapshot shows `data-testid` | a11y snapshot does NOT expose `data-testid` or `aria-label` attributes. Use `is visible` for DOM-level verification of attribute-based selectors |
