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
/e2e-walkthrough [context] [--mode guided|step|auto] [--sites name1,name2] [--pr N] [--issue ID] [--verify] [--no-video]
```

| Entry point | Behavior |
|-------------|----------|
| `--pr 940` | Read PR diff, propose path covering changed UI |
| `--issue DRC-2811` | Read issue, propose path for the feature |
| Free text | Use mapping + codebase to propose path |
| `--page org-settings` | Explore all mapped elements on that page |
| `--smoke` | Walk critical paths from mapping |
| `--verify` | Verification mode: focus on assertions + external checkpoints, tag flow as `verification` |
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

### `--verify` Mode (PR Verification)

When invoked with `--verify`, the walkthrough focuses on producing a stable, repeatable verification flow with external checkpoints:

1. **Every step MUST have `expect:`** — bare navigation without assertions is insufficient for verification
2. **Core integration path only** — 5-12 steps covering the feature's critical user journey
3. **Deterministic assertions** — prefer `url contains`, `element visible`, `text '...'` over timing-dependent checks
4. **External checkpoints** — at key integration points, insert `verify-external` steps to check external services:
   - After a tracked user action → PostHog event checkpoint
   - After an AI interaction → Langfuse trace checkpoint
   - After a form submission → API/database checkpoint
   - After a notification trigger → Slack/email checkpoint
5. **Full tool access** — unlike the test-runner subagent, walkthrough runs in main context. Claude uses MCP, curl, database queries, Slack MCP, or any available tool to execute checkpoint `verify:` blocks.
6. **Tagged output** — generated flow gets `tags: [verification, auto-generated]`
7. **Replay suggestion** — after flow generation: "Run `/e2e-test <flow>` to confirm this flow passes consistently"

**Checkpoint execution in walkthrough (Phase 3):**

When the current step has `action: "Verify external"`:
1. Wait `wait` seconds (allow propagation)
2. Read the `verify:` block, iterate service groups
3. For each check: use the best available tool — MCP server, curl, database query, file read, etc.
4. Report result inline to user: `✓ PostHog: event found (count=3)` or `✗ Langfuse: no trace found`
5. Apply `on_fail:` logic (default `warn` — log and continue)
6. No browser interaction for checkpoint steps

**Verify mode plan example:**

```
Verification walkthrough (8 steps + 2 checkpoints):
1. Navigate to /projects
2. Click "Create Project" → dialog opens
3. Fill form with test data
4. Click Submit → expect success toast
5. ✓ CHECKPOINT: Verify PostHog 'project_created' event
6. Navigate to /projects → verify new project in list
7. Click new project → verify detail page
8. ✓ CHECKPOINT: Verify Langfuse trace for project creation flow
```

Combine `--verify` with `--pr N` to read PR diff for context + produce verification flow.

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

## Phase 3 — Execute & Monitor (Observe-and-Continue)

For detailed execution mechanics (startup, multi-site, per-step loop, anomaly observation, step log), see [reference.md](./reference.md).

**Summary**: Open browser (without `--profile` when recording) → verify auth (auto-login if needed) → **start recording** → start trace → execute steps → observe anomalies → write step log.

**Start recording** (unless `--no-video`):

```bash
agent-browser record start "$REPORT_DIR/full.webm"
```

> **Note**: `record start` is incompatible with `--profile` sessions (v0.16.x). When recording is ON, open the browser WITHOUT `--profile` and handle auth via auto-login or manual prompt. See [reference.md](./reference.md) § Startup for details.

**Per-step loop (observe-and-continue)**:
1. `snapshot -i` → find `@ref` (interactive-only, less noise)
2. Action via `@ref`
3. `wait networkidle` → `screenshot`
4. `errors --json` → non-empty? record anomaly + notify (don't stop)
5. Visual observation → unexpected UI? record anomaly + notify (don't stop)
6. One-line report: `Step N ✓` / `Step N ✓  ⚠ <anomaly summary>` / `Step N ✗  <failure reason>`

**Key principle**: Anomalies are recorded and reported inline, but the walkthrough **never pauses** for them. Full analysis happens in Phase 4 via trace cross-reference. The only exception is auth expiration (which makes all subsequent steps meaningless).

**Interaction modes**: Guided (default, show plan + one-line report), Step (wait "go" between steps), Auto (silent, record anomalies).

**Step log**: At the end of Phase 3, write `$REPORT_DIR/step-log.json` with step timestamps + anomalies. This feeds the enhanced trace analyzer in Phase 4.

**After all steps complete (or human says "stop here"), proceed to Phase 4.**

## Phase 4 — Output & Learn (STRICT ORDER)

**Execute ALL subsections below in order. Do NOT skip to Browser Handoff.**

**Print this checklist at the start of Phase 4. Update each line as you complete it. Do NOT proceed to Browser Handoff until lines 1-11 are checked.**

```
Phase 4 checklist:
[ ] 1. record stop (or N/A if --no-video)
[ ] 2. trace stop → trace.zip saved
[ ] 3. trace-analyzer dispatched (with step-log.json)
[ ] 4. anomaly review presented (or N/A if zero anomalies AND trace clean)
[ ] 5. report.md written (full artifact with flowchart + step table + health log)
[ ] 6. pr-summary.md written (PR reviewer version with inline screenshots)
[ ] 7. GIF generated (or N/A if no screenshots)
[ ] 8. MP4 generated (from trace screencast or recording)
[ ] 9. flow YAML written to .claude/e2e/flows/
[ ] 10. PR comment posted with pr-summary.md (or N/A if no --pr)
[ ] 11. mapping discrepancy check done
[ ] 12. browser handoff + action menu presented
[ ] 13. pipeline next steps shown
```

For detailed procedures (trace analysis, anomaly review, report templates, flow YAML rules, mapping self-repair), see [reference.md](./reference.md).

Checklist items map to procedure steps below. Items 5-6 are both from procedure step 5 (dual output). Item 13 maps to Pipeline Next Steps section below.

1. **Stop recording** (if recording): `agent-browser record stop`
2. **Stop trace**: `agent-browser trace stop "$REPORT_DIR/trace.zip"`
3. **Trace analysis (enhanced)**: Dispatch `e2e-trace-analyzer` subagent with `trace_path` + `report_dir` + `step_log_path`. Prerequisite: `step-log.json` must exist in `$REPORT_DIR` (written at end of Phase 3). If missing, write it now from in-memory step data and verify the file exists. If write fails again, dispatch WITHOUT `step_log_path` — analyzer degrades gracefully to non-enhanced mode (no cross-reference, but analysis still completes). See [reference.md](./reference.md) § Trace Analysis.
4. **Anomaly review** (checklist item 4): If anomalies were observed during Phase 3 (check step-log.json `anomalies` arrays) OR trace found issues (`clean: false`), present the cross-reference summary and offer: review details / fix / re-walk / continue. Skip to step 5 ONLY when BOTH conditions are true: zero anomalies in step-log AND trace returns `clean: true`. Note: `clean: true` from trace-analyzer means zero API/console/silent-failure — it does NOT account for unmatched visual anomalies. See [reference.md](./reference.md) § Anomaly Review.
5. **Report (dual output, MANDATORY)** (checklist items 5+6): Write both `$REPORT_DIR/report.md` and `$REPORT_DIR/pr-summary.md`. Health Log now includes step-correlated data from trace analysis. See [reference.md](./reference.md) § Report for templates.
6. **GIF generation** (checklist item 7, if recording): see `references/commands.md` § GIF Generation for the canonical ffmpeg command. Warn but continue if ffmpeg fails.
7. **MP4 video conversion** (checklist item 8, if recording): see `references/commands.md` § MP4 Video Conversion. Default 1.5x speed. Warn but continue if ffmpeg fails.
8. **Flow YAML auto-generation (MANDATORY)** (checklist item 9): Always auto-generate — never ask. Auto-name: `walkthrough-<timestamp>-<first-page>.yaml`. Write to `.claude/e2e/flows/`. Cross-site: use `sites:` instead of `mapping:` when `--sites` was used.
9. **PR/Issue posting** (checklist item 10): If `--pr` provided, ask user to confirm → commit + push screenshots → `gh pr comment` with `pr-summary.md`. See [reference.md](./reference.md) § PR/Issue Posting.
10. **Mapping self-repair** (checklist item 11): Present discrepancy list, human approves, patch mapping. 3+ stale on same page → recommend `/e2e-map --page`
11. **Browser handoff** (checklist item 12, BLOCKING: report + flow YAML must be written first): Present summary table, then numbered action menu. Do NOT close browser — user may need to inspect final state.

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

**Top 5 (highest frequency):**

| Mistake | Fix |
|---------|-----|
| Stopping walkthrough for anomalies | **Observe-and-continue**: record anomaly + notify + keep going. Only auth expiration pauses. Full analysis in Phase 4 via trace cross-reference. |
| Running `console --json` at any point during walkthrough | Never used in Phase 3 — not once, not "just for this error." Trace.zip captures complete console with better coverage. `errors --json` is the only per-step check. If user asks to "pay attention to console," use `errors --json` — that IS the console error check. |
| Using full `snapshot` instead of `snapshot -i` | Per-step loops always use `snapshot -i`. Full snapshot only for `--smoke` post-walkthrough selector sweep or when user explicitly requests element discovery. |
| Skipping step-log.json write | MANDATORY at end of Phase 3. Trace analyzer needs it for step correlation. Without it, cross-reference sections are absent. |
| Skipping Phase 4 checklist items | Phase 4 has 13 items. Print checklist, complete ALL. "Context pressure" is NOT a valid reason to skip. |

**agent-browser gotchas (see also `references/commands.md`):**

| Mistake | Fix |
|---------|-----|
| Acting without snapshot | `snapshot -i` before every action — a11y tree is source of truth |
| CSS selectors for clicks | Use `@ref` from snapshot. `role=` only for visibility checks |
| `has-text()` selectors | BROKEN in agent-browser — times out. Use `role=button[name="..."]` |
| Screenshot relative paths | agent-browser needs absolute paths (sandbox CWD differs) |
| Forgetting `trace stop` | Trace data lost if browser closes without stopping |
| `scroll` to element | `scroll` only accepts direction (up/down). Use `hover "@ref"` to auto-scroll |
| `is visible` exit code always 0 | Check stdout text "true"/"false", NOT exit code. Don't chain with `&&` |
| Large table snapshots consume context | Use targeted `is visible` checks instead of full snapshot for 10+ row tables |
| Assuming snapshot shows `data-testid` | a11y snapshot does NOT expose `data-testid`/`aria-label`. Use `is visible` |
| `--profile` silently ignored | Daemon already running without profile. `agent-browser close` → wait 3s → re-open |
| Checkpoint steps interact with browser | `verify-external` steps do NOT touch browser — skip snapshot, skip element resolution |
