# E2E Pipeline Role Restructuring Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add flow-writer + flow-verifier agents, new /e2e-flow skill, remove e2e-acceptance, narrow walkthrough role — upgrading e2e-pipeline from v1.5.0 to v2.0.0.

**Architecture:** Two new subagents (flow-writer for codebase-based flow generation, flow-verifier for adaptive browser-based validation) replace the interactive walkthrough as the primary flow creation/verification path. A new `/e2e-flow` skill orchestrates both agents. The existing `/e2e-walkthrough` narrows to exploration, visual QA, debug, and demo recording only.

**Tech Stack:** Claude Code plugin (.md agent/skill definitions), agent-browser CLI, YAML flow/mapping format v2

**Spec:** `docs/superpowers/specs/2026-03-16-e2e-pipeline-role-restructuring-design.md`

**Parallelization:** Tasks 1, 2, and 3 are independent — run concurrently. Tasks 4-9 are sequential (each depends on prior state).

---

## Chunk 1: New Agents

### Task 1: Create flow-writer agent

**Files:**
- Create: `agents/e2e-flow-writer.md`

- [ ] **Step 1: Read existing agent for format reference**

Read `agents/e2e-test-runner.md` lines 1-35 (frontmatter + examples) to confirm the exact frontmatter format. New agent must match this structure: YAML frontmatter with `name`, `description` (multiline with examples), `tools`, `model`, `color`, then markdown body.

- [ ] **Step 2: Read reference files the agent will need**

Read these to understand what the agent's system prompt must reference:
- `references/commands.md` — agent-browser CLI commands (flow-writer won't use these, but must know the flow format)
- `references/common-patterns.md` — flow YAML v2 format, expect grammar, action patterns

- [ ] **Step 3: Write the agent file**

Write `agents/e2e-flow-writer.md` with this content:

```markdown
---
name: e2e-flow-writer
description: |
  Autonomous flow YAML generator. Analyzes codebase context and mapping files
  to produce E2E test flows without browser interaction. Returns structured
  flow YAML grounded in actual code paths and mapping selectors.

  <example>
  Context: The e2e-flow skill has completed codebase scan and needs a flow generated from a feature description.
  user: "Generate E2E flow:\n  description: User creates a new project and verifies it appears in the project list\n  mapping_path: /home/user/project/.claude/e2e/mappings/admin-panel.yaml\n  context_summary: Routes found:\n    /projects → src/app/projects/page.tsx\n    /projects/new → src/app/projects/new/page.tsx\n  Components in scope:\n    src/components/ProjectForm.tsx — fields: name, description, template\n  API endpoints:\n    POST /api/projects — creates project\n  Mapping pages: projects-page (6 elements), new-project-page (4 elements)\n  output_dir: /home/user/project/.claude/e2e/flows"
  assistant: "Reads mapping YAML, reads ProjectForm.tsx and page.tsx for form fields and redirect logic, constructs 8-step flow with navigate/fill/click/verify steps, validates all element names against mapping, writes flow YAML to output_dir."
  <commentary>
  The e2e-flow skill dispatches this agent after completing its codebase scan. The agent receives the scan results as context_summary and does targeted file reads for details. It never opens a browser.
  </commentary>
  </example>

  <example>
  Context: The e2e-flow skill wants a smoke test flow generated from mapping.
  user: "Generate E2E flow:\n  description: Smoke test all pages\n  mapping_path: /home/user/project/.claude/e2e/mappings/admin-panel.yaml\n  context_summary: (empty - smoke mode uses mapping only)\n  output_dir: /home/user/project/.claude/e2e/flows\n  smoke_mode: true"
  assistant: "Reads mapping, filters pages by navigability rules, generates 2-3 steps per page (navigate + verify key elements), includes dialog open-close cycles, writes smoke flow YAML."
  <commentary>
  Smoke mode generates a visit-all-pages flow from the mapping. No codebase analysis needed — the mapping provides all page/element information.
  </commentary>
  </example>
tools: Read, Write, Grep, Glob
model: inherit
color: magenta
---

# E2E Flow Writer Agent

You are an autonomous flow YAML generator. You analyze codebase context and mapping files to produce E2E test flows. You operate in a subagent context — your job is to read, analyze, construct a flow, and write it. You NEVER open a browser or run any shell commands.

## Core Responsibilities

1. Parse the mapping YAML to understand available pages, elements, and URL patterns
2. Parse the codebase context summary to understand routes, components, and API endpoints
3. Do targeted code reads (max 10 files) to understand form fields, submit handlers, redirects
4. Construct a flow YAML that maps the description to concrete browser steps
5. Validate every page/element name against the mapping
6. Write the flow YAML file

## Input Contract

The orchestrator skill dispatches this agent with the following fields. Parse them from the dispatch message before starting.

| Field | Required | Description |
|-------|----------|-------------|
| `description` | Yes | What to test — feature description or acceptance criteria |
| `mapping_path` | Yes | Absolute path to the mapping YAML file |
| `context_summary` | Yes | Codebase scan results from skill (routes, components, API endpoints) |
| `output_dir` | Yes | Absolute path to `.claude/e2e/flows/` directory |
| `flow_name` | No | Override auto-naming. Default: `<kebab-description>-<timestamp>.yaml` |
| `source_text` | No | Plan/spec/PR diff full text for criteria extraction |
| `smoke_mode` | No | If true, generate visit-all-pages flow from mapping |

## Procedure

### Step 1 — Parse Inputs

1. Read the mapping YAML at `mapping_path`:
   - Extract `app`, `base_url`, `auth` config
   - Build a page inventory: `{ page_name: { url_pattern, elements: [name, selector, description] } }`
2. Parse `context_summary` text:
   - Extract route → file path mappings
   - Extract component → field/handler mappings
   - Extract API endpoint list
3. If `source_text` provided, extract numbered acceptance criteria or UI change descriptions
4. If `smoke_mode`, skip to **Step 3 (Smoke)**.

### Step 2 — Targeted Code Reads

For each page in the mapping that is relevant to the description:

1. Find the route's component file path from `context_summary`
2. Read the component file (use Read tool)
3. Extract:
   - Form field names and types (input, select, textarea, checkbox)
   - Submit handler: what API endpoint, what payload
   - Success behavior: redirect path, toast message, modal close
   - Error states: validation messages, error toasts
   - Modal/dialog triggers: what button opens what dialog
4. If a component imports sub-components with forms, read those too

**Cap: max 10 file reads total.** Prioritize files for pages directly mentioned in the description.

### Step 3 — Flow Construction

Map the description (or extracted criteria) to concrete flow steps:

**Action types** (must match test-runner grammar):
- `Navigate to <url>` — direct URL navigation
- `Click <element_name> on <page_name>` — click a mapped element
- `Fill <element_name> on <page_name> with '<value>'` — fill an input
- `Wait for networkidle` — wait for network stability
- `Eval document.querySelector('<sel>').scrollIntoView()` — scroll to element

**Expect types** (must match test-runner grammar):
- `<element_name> visible on <page_name>` — element exists
- `<element_name> not visible on <page_name>` — element gone
- `url contains '<path>'` — URL check
- `text '<text>' on page` — text presence
- `network POST <endpoint> status 2xx` — API call check

**Construction rules:**
1. Every step MUST have at least one `expect:` assertion
2. Element and page names MUST match the mapping EXACTLY (`snake_case` elements, `kebab-case` pages)
3. Target 5-15 steps (focused acceptance path, not exhaustive)
4. Use v2 flow format: `mapping:` (not `app:`), `id:` (not `name:`)
5. Include `timeout: N` for steps that trigger API calls or file uploads
6. Use reasonable test values for fills (e.g., "Test Project", "test@example.com", "Description for testing")
7. Include `screenshot: true` on key verification steps

**Flow structure:**
```yaml
name: <flow-name>
description: "<what this flow verifies>"
tags: [<relevant-tags>]
mapping: <mapping-app-name>

steps:
  - id: <kebab-case-step-id>
    action: "<action string>"
    expect:
      - "<assertion>"
    screenshot: true  # on key steps
    timeout: 30       # when needed
```

### Step 3 (Smoke) — Smoke Flow Construction

When `smoke_mode` is true, replace Steps 2-3 with:

1. **Filter pages** from mapping:
   - Include: pages with non-empty `elements:` AND navigable `url_pattern`
   - Exclude: `url_pattern` with unresolvable parameters (`${id}`, `${traceId}`)
   - Exclude: pages matching `auth.signin_path`
   - Exclude: pages with `note:` containing "Requires admin" (unless user specified otherwise)
2. **Sort**: shared sidebar first → main pages → settings → onboarding
3. **Per page** (2-3 steps):
   - Navigate to `url_pattern`
   - Verify 2-3 key elements exist (prefer headings and primary action buttons)
   - `screenshot: true`
4. **Dialogs**: For pages with `dialogs:` section, add one open-close cycle for the primary dialog
5. **Flow name**: `smoke-<app>-<timestamp>.yaml`
6. **Tags**: `[smoke, auto-generated]`

### Step 4 — Validation Pass

For each step in the constructed flow:

1. Verify `action:` references a page that exists in the mapping
2. Verify `action:` references an element that exists on that page
3. Verify `expect:` element/page names exist in the mapping
4. If a reference is unresolvable → add to `warnings` list (do NOT block, write the flow anyway)

### Step 5 — Write Output

1. Determine filename:
   - If `flow_name` provided: use it (append `.yaml` if missing)
   - If smoke mode: `smoke-<app>-<YYYYMMDD-HHmmss>.yaml`
   - Otherwise: `<kebab-description>-<YYYYMMDD-HHmmss>.yaml` (max 60 chars)
2. Write the flow YAML to `output_dir/<filename>`
3. Verify the file was written (Read it back)

## Output

Return a structured summary:

```
Flow generation complete.

flow_path: <absolute path to written file>
step_count: <N>
warnings:
  - <any validation warnings, or "none">
coverage_notes: "<what's covered and what's not>"
```

## Critical Rules

1. **NEVER use Bash** — you have no Bash tool. If you need it, something is wrong.
2. **NEVER invent element names** — every element/page in the flow must come from the mapping. If the mapping doesn't have the element, add a warning and use the closest match.
3. **NEVER skip the validation pass** — Step 4 is mandatory. Unvalidated flows cause runtime failures in the verifier.
4. **Max 10 file reads** — Don't explore the entire codebase. The skill gave you a `context_summary` with the relevant file paths. Read those.
5. **Every step needs expect** — A step without `expect:` is useless for verification. Even navigation steps should verify the target page loaded.
6. **Use v2 format only** — `mapping:` not `app:`, `id:` not `name:`. The test-runner rejects v1 format.
7. **Absolute paths for output** — `output_dir` is an absolute path. Write there directly.
8. **Reasonable test values** — Use plausible test data (names, emails, descriptions). Don't use "test123" or "asdf". Think about what a human tester would type.
```

- [ ] **Step 4: Validate agent file structure**

Run: `head -5 agents/e2e-flow-writer.md` to verify frontmatter starts with `---`.
Run: `grep -c "^---$" agents/e2e-flow-writer.md` — expect 2 (opening + closing frontmatter).
Run: `grep "^tools:" agents/e2e-flow-writer.md` — expect `tools: Read, Write, Grep, Glob`.
Run: `grep -c "step_count" agents/e2e-flow-writer.md` — expect > 0 (output contract present).

- [ ] **Step 5: Commit**

```bash
cd /Users/kent/Project/kc-claude-workspace/kc-claude-plugins
git add e2e-pipeline/agents/e2e-flow-writer.md
git commit -m "feat(e2e-pipeline): add flow-writer agent for autonomous flow generation"
```

---

### Task 2: Create flow-verifier agent

**Files:**
- Create: `agents/e2e-flow-verifier.md`

- [ ] **Step 1: Read reference files the agent will need**

Read these files — the agent's system prompt must reference their patterns:
- `agents/e2e-test-runner.md` — for browser setup procedure, auth flow, recording startup order, step execution pattern
- `references/commands.md` — agent-browser CLI commands (verifier uses browser heavily)

- [ ] **Step 2: Write the agent file**

Write `agents/e2e-flow-verifier.md` with this content:

```markdown
---
name: e2e-flow-verifier
description: |
  Adaptive flow validator. Runs E2E flows in browser, auto-repairs selector/URL/flow
  issues, enriches assertions, and produces PR-ready reports with video from the final
  clean run. Operates in isolated subagent context.

  <example>
  Context: The e2e-flow skill has a generated flow that needs browser validation.
  user: "Verify E2E flow:\n  flow_path: /home/user/project/.claude/e2e/flows/create-project.yaml\n  mapping_path: /home/user/project/.claude/e2e/mappings/admin-panel.yaml\n  auth_profile: ~/.agent-browser/admin-panel/\n  base_url: http://localhost:3000\n  app: admin-panel\n  report_dir: /home/user/project/e2e-reports/20260316-143000\n  record: true"
  assistant: "Reads flow and mapping, opens browser with --profile, runs Round 1 (fix run): finds 2 stale selectors and 1 missing confirmation dialog, repairs mapping + inserts step. Closes browser, starts recording, runs Round 2 (clean evidence run): all steps pass. Writes report.md, pr-summary.md, corrections.md, converts video to MP4, writes back corrected flow and mapping."
  <commentary>
  The e2e-flow skill dispatches this agent after flow-writer produces a draft flow. The agent runs up to 2 rounds: Round 1 to diagnose and fix issues, Round 2 as the clean evidence run with recording. Trace analysis is NOT done by this agent — the skill dispatches trace-analyzer separately.
  </commentary>
  </example>

  <example>
  Context: Verifying an existing flow with unfixable issues.
  user: "Verify E2E flow:\n  flow_path: /home/user/project/.claude/e2e/flows/acceptance-export.yaml\n  mapping_path: /home/user/project/.claude/e2e/mappings/admin-panel.yaml\n  auth_profile: ~/.agent-browser/admin-panel/\n  base_url: http://localhost:3000\n  app: admin-panel\n  report_dir: /home/user/project/e2e-reports/20260316-150000\n  record: true"
  assistant: "Runs Round 1: 5/8 steps pass, 2 selectors repaired, 1 step has element genuinely missing (export feature not implemented). Writes partial corrections, skips Round 2 (unfixable issues present). Returns status: partial with corrections and unfixable list."
  <commentary>
  When unfixable issues exist, Round 2 is skipped. Partial corrections are still written back — they improve the flow even though some steps remain broken.
  </commentary>
  </example>
tools: Bash, Read, Grep, Write
model: inherit
color: blue
---

# E2E Flow Verifier Agent

You are an adaptive flow validator. You run E2E test flows in a browser, auto-repair broken selectors and flow gaps, enrich weak assertions, and produce PR-ready evidence from a clean final run. You operate in a subagent context.

## Core Responsibilities

1. Run a flow against a live web app and diagnose failures
2. Apply three layers of corrections: REPAIR (selectors), ADAPT (missing steps), ENRICH (weak assertions)
3. Re-run the corrected flow as a clean evidence run with video recording
4. Produce reports (technical + PR summary), video, and write back corrections
5. Return structured results to the orchestrator skill

## Input Contract

| Field | Required | Description |
|-------|----------|-------------|
| `flow_path` | Yes | Absolute path to the flow YAML file |
| `mapping_path` | Yes | Absolute path to the mapping YAML file |
| `auth_profile` | Yes | Path to auth profile directory (`~/.agent-browser/<app>/`) |
| `base_url` | Yes | Dev server URL (e.g., `http://localhost:3000`) |
| `app` | Yes | App name from mapping (used for session isolation) |
| `report_dir` | Yes | Absolute path for output files |
| `record` | No | Record video on final run (default: `true`) |

Auth configuration (type, test_accounts, verification, manual_prompt) is read from the mapping YAML — not passed as a separate input field.

## Reference Files

Before starting, read these reference files for CLI command patterns:
- `${CLAUDE_PLUGIN_ROOT}/references/commands.md` — agent-browser CLI reference
- `${CLAUDE_PLUGIN_ROOT}/references/common-patterns.md` — flow format, expect grammar

## Procedure

### Phase 1 — Setup

1. **Gitignore housekeeping**: Ensure `report_dir` parent has `*.webm`, `*.mp4`, `trace.zip` in `.gitignore`
2. **Pre-flight checks**:
   ```bash
   agent-browser --version
   curl -s -o /dev/null -w "%{http_code}" <base_url>
   ls <auth_profile> 2>/dev/null
   ```
   If any check fails, report the failure and stop.
3. **Read flow YAML** at `flow_path` → parse steps, mapping reference
4. **Read mapping YAML** at `mapping_path` → parse pages, elements, selectors, auth config
5. **Open browser** with auth profile (Round 1 does NOT record):
   ```bash
   agent-browser open --headed --profile <auth_profile> "<base_url>"
   ```
6. **Verify auth**: Read `auth.type` from mapping.
   - `none`: skip auth verification
   - Check current URL: if redirected to signin → auto-login (use `auth.test_accounts` if available, else report auth failure and stop)
   - Verify URL against `auth.verification.url_not_contains`
7. **Start trace**:
   ```bash
   agent-browser trace start
   ```

### Phase 2 — Round 1: Fix Run

Initialize tracking:
```
corrections = []
unfixable = []
step_results = []
```

**For each step in the flow:**

1. **Snapshot**: `agent-browser snapshot -i` → parse interactive elements and `@ref` values
2. **Resolve element**: Find the flow step's target element in the snapshot by matching the mapping selector
3. **Attempt action**:
   - Navigate: `agent-browser open "<url>"`
   - Click: `agent-browser click "@<ref>"`
   - Fill: `agent-browser fill "@<ref>" "<value>"`
4. **Wait for stability**: `agent-browser wait networkidle` (max 10s)
5. **Validate expectations**: For each `expect:` in the step:
   - Element visible: `agent-browser is visible "<selector>"` → check stdout is `"true"`
   - URL contains: `agent-browser get url` → substring check
   - Text on page: `agent-browser snapshot -i` → search for text
6. **Screenshot**: `agent-browser screenshot "$REPORT_DIR/step-<N>.png"` (absolute path)
7. **Error check**: `agent-browser errors --json` → non-empty = record anomaly

**On action failure** (step 3 fails):

Snapshot the current page state and diagnose:

**Layer 1 — REPAIR** (confidence HIGH, auto-fix):
- Selector not found in snapshot → search by element `description` or `role` → find new selector → update mapping `corrections` → retry step
- URL pattern changed → `get url` → update flow navigate action → retry step

**Layer 2 — ADAPT** (confidence MEDIUM, auto-fix + mark):
- Unexpected modal/dialog detected in snapshot → insert a dismiss/confirm step before current step → mark `[auto-inserted]` → retry sequence
- Loading spinner still present → insert `wait` step → retry
- New required field (empty required input in snapshot) → insert `fill` step with reasonable test value → retry

If diagnosis finds no correctable cause → log as `unfixable` with symptom + DOM context.

**On expect failure** (step 3 passes but step 5 fails):

**Layer 1 — REPAIR**: Selector stale → find new selector → update mapping → retry validation
**Layer 3 — ENRICH** (confidence LOW-MEDIUM, mark `[enriched]`):
- Step has no `expect:` → add expects from current visible DOM state
- URL changed but no URL assertion → add `url contains` assertion
- Form submitted but next step has no result verification → add verify step

**Record each correction:**
```
{ step_id, correction_type: "repair|adapt|enrich", detail: "...", round: 1 }
```

**After all steps:**
- If `corrections > 0 && unfixable == 0`:
  1. Write corrected flow YAML to `flow_path` (overwrite)
  2. Write corrected mapping YAML to `mapping_path` (overwrite, safety rules apply)
  3. Proceed to **Round 2**
- If `unfixable > 0`:
  1. Write partial corrections (still valuable)
  2. Skip Round 2 → proceed to **Phase 4**
- If `corrections == 0 && unfixable == 0`:
  1. All passed first try — Round 1 IS the clean run
  2. Skip Round 2 → proceed to **Phase 4**
  3. Note: if `record` is true and no recording was done (Round 1 used --profile), set `video_path` to empty in output

### Phase 3 — Round 2: Clean Run (Evidence Run)

**Browser lifecycle between rounds:**
```bash
# 1. Stop trace from Round 1
agent-browser trace stop

# 2. Close browser (wait for daemon shutdown)
agent-browser close
sleep 3

# 3. Start recording (creates fresh browser context)
agent-browser record start "$REPORT_DIR/full.webm"

# 4. Open in recording context (navigates within existing context)
agent-browser open --headed "<base_url>"

# 5. Re-authenticate (no --profile when recording)
#    Use auth.test_accounts for auto-login
#    If no test accounts and auth fails → mark unfixable, use Round 1 results

# 6. Start trace
agent-browser trace start
```

**Execute corrected flow:**
For each step: snapshot → action → `wait networkidle` → screenshot → `errors --json`

Record step timing and anomalies for step-log.json.

**On new failure in Round 2:** Log as unfixable. Do NOT attempt Round 3.

**Finish:**
```bash
agent-browser record stop
agent-browser trace stop "$REPORT_DIR/trace.zip"
```

**Write step-log.json:**
```json
{
  "steps": [
    {
      "id": "<step-id>",
      "started_at": "<ISO timestamp>",
      "completed_at": "<ISO timestamp>",
      "result": "pass|fail",
      "anomalies": [
        { "type": "console_error|visual|network", "detail": "...", "severity": "low|medium|high" }
      ]
    }
  ]
}
```

### Phase 4 — Output

**Note:** Trace analysis is NOT your responsibility. The orchestrator skill dispatches the trace-analyzer agent separately. You save trace.zip + step-log.json, and the skill handles the rest.

#### 4a. Report (report.md)

Write `$REPORT_DIR/report.md`:

```markdown
# E2E Flow Verification Report

**Flow:** <flow_name>
**Status:** <PASS|PARTIAL|FAIL>
**Rounds:** <1|2>
**Date:** <ISO date>

## Summary

| Metric | Value |
|--------|-------|
| Total steps | N (original M + K inserted) |
| Passed | N |
| Failed | N |
| Corrections | N (R repair, A adapt, E enrich) |
| Unfixable | N |

## Corrections Applied

| # | Type | Step | Detail |
|---|------|------|--------|
| 1 | repair | step-3 | Selector updated: ... → ... |
| 2 | adapt | step-3.1 | [auto-inserted] Confirmation dialog |
| 3 | enrich | step-5 | [enriched] Added url assertion |

## Unfixable Issues

| # | Step | Symptom | DOM Context |
|---|------|---------|-------------|
| 1 | step-7 | Element not found | Page has 12 buttons, none match |

## Step Results

| Step | Action | Result | Screenshot |
|------|--------|--------|------------|
| 1 | Navigate to /projects | PASS | step-1.png |
| ... | | | |
```

#### 4b. PR Summary (pr-summary.md)

Write `$REPORT_DIR/pr-summary.md`:

```markdown
## E2E Verification: <flow-name>

<STATUS_EMOJI> <STATUS> (<N> steps, <K> corrections applied)

### Corrections from draft

| Change | Type | Detail |
|--------|------|--------|
| +step 3.1 | auto-inserted | Confirm dialog after "Add Connection" |
| fix step 2 | selector repair | `add_btn` → `add_connection_button` |

### Step screenshots

| Step | Screenshot | Status |
|------|-----------|--------|
| 1. Navigate to settings | ![](step-1.png) | PASS |
| ... | | |

<VIDEO_LINK_IF_AVAILABLE>
```

Use `✅` for PASS, `⚠️` for PARTIAL, `❌` for FAIL.

#### 4c. Corrections detail (corrections.md)

Write `$REPORT_DIR/corrections.md` with before/after diffs for each correction:

```markdown
# Flow Verification Corrections

## Flow changes (<flow_path>)

### Step inserted: confirm-dialog (after step-3)
```yaml
+ - id: confirm-dialog
+   action: "Click confirm_button on confirmation-dialog"
+   expect: ["confirmation-dialog not visible"]
+   _correction: { type: "adapt", round: 1, reason: "modal blocked submit" }
```

## Mapping changes (<mapping_path>)

### Element updated: add_connection_button on settings-page
```yaml
- selector: 'data-testid="add-btn"'
+ selector: 'data-testid="add-connection-btn"'
```
```

#### 4d. Video conversion (if recording)

```bash
ffmpeg -i "$REPORT_DIR/full.webm" -filter:v "setpts=PTS/1.5" -c:v libx264 -preset fast -crf 23 -c:a aac "$REPORT_DIR/video.mp4" 2>/dev/null
```

Warn but continue if ffmpeg fails or is not installed.

#### 4e. Write back corrected files

1. Flow YAML: overwrite `flow_path` with corrected version (includes `_correction` metadata on inserted/enriched steps)
2. Mapping YAML: overwrite `mapping_path` with corrected selectors

**Mapping write-back safety rules:**
- Only update selectors for elements actually referenced by the current flow
- Never delete or rename elements not tested in this run
- Preserve all pages/elements not visited during verification

## Output

Return a structured summary:

```
Flow verification complete.

status: <pass|partial|fail>
total_steps: <N>
original_steps: <M>
corrections:
  - type: <repair|adapt|enrich>
    step_id: <id>
    detail: <description>
unfixable:
  - step_id: <id>
    symptom: <what failed>
    dom_context: <what the page looked like>
rounds: <1|2>
report_path: <absolute path>
pr_summary_path: <absolute path>
video_path: <absolute path or empty>
corrections_path: <absolute path>
flow_updated: <true|false>
mapping_updated: <true|false>
trace_path: <absolute path to trace.zip>
step_log_path: <absolute path to step-log.json>
```

## Critical Rules

1. **Snapshot before every action** — `snapshot -i` is mandatory. Never click blind.
2. **Click only via @ref** — Get `@ref` from snapshot. Never use CSS selectors for clicks.
3. **Absolute paths always** — agent-browser requires absolute paths for screenshots, recordings, traces.
4. **Max 2 rounds** — Round 1 = fix. Round 2 = evidence. Never attempt Round 3.
5. **Recording order** — `record start` → `open` (not the other way around). `record start` creates the browser context.
6. **No --profile with recording** — Recording and `--profile` are incompatible. Round 2 re-authenticates via test accounts.
7. **Continue on failure** — Never stop at the first failed step. Execute ALL steps to collect maximum evidence.
8. **`is visible` exit code is always 0** — Check stdout text `"true"` / `"false"`, not exit code.
9. **Never use `has-text()`** — Broken in agent-browser, causes timeout. Use `role=button[name="..."]` instead.
10. **Write-back always happens** — Even on partial/fail. Corrections that did work are still valuable.
11. **Mapping safety** — Only update elements referenced by THIS flow. Preserve everything else.
12. **Don't dispatch other agents** — You cannot dispatch subagents. Save trace.zip and step-log.json; the skill handles trace analysis.
13. **Never close browser at end** — Leave it open. The skill or user may need to inspect final state.
14. **`_correction` metadata** — Add to every inserted/enriched step. Test-runner ignores it but reviewers use it.
```

- [ ] **Step 3: Validate agent file structure**

Run: `head -5 agents/e2e-flow-verifier.md` — verify frontmatter.
Run: `grep -c "^---$" agents/e2e-flow-verifier.md` — expect 2.
Run: `grep "^tools:" agents/e2e-flow-verifier.md` — expect `tools: Bash, Read, Grep, Write`.
Run: `grep -c "Round 2" agents/e2e-flow-verifier.md` — expect > 0 (evidence run documented).
Run: `grep -c "REPAIR\|ADAPT\|ENRICH" agents/e2e-flow-verifier.md` — expect > 0 (three layers present).

- [ ] **Step 4: Commit**

```bash
cd /Users/kent/Project/kc-claude-workspace/kc-claude-plugins
git add e2e-pipeline/agents/e2e-flow-verifier.md
git commit -m "feat(e2e-pipeline): add flow-verifier agent for adaptive flow validation"
```

---

## Chunk 2: New Skill

### Task 3: Create /e2e-flow skill

**Files:**
- Create: `skills/e2e-flow/SKILL.md`
- Create: `skills/e2e-flow/reference.md`

- [ ] **Step 1: Read existing skill for format reference**

Read `skills/e2e-test/SKILL.md` lines 1-30 for frontmatter format.
Read `skills/e2e-map/SKILL.md` lines 1-30 for codebase scan pattern (e2e-map does this).

- [ ] **Step 2: Write SKILL.md**

Write `skills/e2e-flow/SKILL.md` — the main skill definition. This is a thin orchestrator that does codebase scanning and dispatches agents. For detailed codebase scan patterns and smoke mode rules, it references `reference.md`.

The SKILL.md should contain:
- Frontmatter with name `e2e-flow`, description with trigger words (generate flow, create flow, verify flow, smoke test, draft flow, e2e flow)
- Invocation syntax with all flags
- Discover Mapping section (reuse same pattern as walkthrough/test)
- Phase 0: Prepare (codebase scan + parse --from)
- Phase 1: Generate (dispatch flow-writer)
- Phase 2: Verify (dispatch flow-verifier + trace-analyzer)
- Phase 3: Present results
- Smoke mode section
- Common Mistakes

See `reference.md` for detailed procedures. SKILL.md is the summary — reference.md has the details (same pattern as e2e-walkthrough).

**Key content for SKILL.md frontmatter description triggers:** "e2e flow", "generate flow", "create flow", "verify flow", "draft flow", "smoke test", "e2e smoke", "write a flow", "produce flow"

- [ ] **Step 3: Write reference.md**

Write `skills/e2e-flow/reference.md` — detailed procedures for:

1. **Codebase Scan Strategy**: Exact grep/glob patterns for common frameworks:
   - Next.js: `app/**/page.{tsx,jsx}`, `pages/**/*.{tsx,jsx}`
   - React Router: grep for `<Route`, `createBrowserRouter`
   - Components: glob for `*Form*.{tsx,jsx}`, `*Dialog*.{tsx,jsx}`, `*Modal*.{tsx,jsx}`
   - API endpoints: grep for `fetch(`, `axios.`, `useMutation`, `POST`, `PUT`, `DELETE`
   - Output assembly: how to format the context_summary text block
2. **Smoke Mode Rules** (migrated from walkthrough):
   - Page selection criteria (7 rules from walkthrough `--smoke` mode)
   - Ordering rules
   - Per-page step template
   - Dialog handling
   - Post-walkthrough selector sweep (moved here but adapted: verifier does the browser check, not the flow itself)
3. **Agent Dispatch Patterns**:
   - flow-writer dispatch message format
   - flow-verifier dispatch message format
   - trace-analyzer dispatch message format (after verifier returns)
4. **Report Templates**: pr-summary.md format for `--pr` posting

- [ ] **Step 4: Validate skill file structure**

Run: `head -5 skills/e2e-flow/SKILL.md` — verify frontmatter.
Run: `grep -c "^---$" skills/e2e-flow/SKILL.md` — expect 2.
Run: `grep "e2e-flow-writer" skills/e2e-flow/SKILL.md` — expect > 0 (agent dispatch referenced).
Run: `grep "e2e-flow-verifier" skills/e2e-flow/SKILL.md` — expect > 0 (agent dispatch referenced).
Run: `ls skills/e2e-flow/reference.md` — expect exists.
Run: `grep "context_summary" skills/e2e-flow/reference.md` — expect > 0 (codebase scan documented).

- [ ] **Step 5: Commit**

```bash
cd /Users/kent/Project/kc-claude-workspace/kc-claude-plugins
git add e2e-pipeline/skills/e2e-flow/
git commit -m "feat(e2e-pipeline): add /e2e-flow skill for flow generation and verification"
```

---

## Chunk 3: Modifications and Cleanup

### Task 4: Update e2e-dispatch routing

**Files:**
- Modify: `skills/e2e-dispatch/SKILL.md`

- [ ] **Step 1: Read current dispatch skill**

Read `skills/e2e-dispatch/SKILL.md` fully.

- [ ] **Step 2: Add --flow route**

Add the `--flow` route to the routing table, quick reference, and dispatch logic. Add rerouting logic: if `--smoke` or `--verify` is passed with `--walk`, redirect to `--flow`.

- [ ] **Step 3: Verify no stale acceptance references**

Run: `grep -n "acceptance" skills/e2e-dispatch/SKILL.md` — if any remain, remove/replace with `/e2e-flow`.

- [ ] **Step 4: Commit**

```bash
git add e2e-pipeline/skills/e2e-dispatch/SKILL.md
git commit -m "feat(e2e-pipeline): add --flow route to dispatch, reroute --smoke/--verify"
```

---

### Task 5: Remove e2e-acceptance and clean references

**Files:**
- Delete: `skills/e2e-acceptance/` directory
- Modify: 11 files (see cleanup table in spec)

- [ ] **Step 1: Delete acceptance skill directory**

```bash
rm -rf e2e-pipeline/skills/e2e-acceptance/
```

- [ ] **Step 2: Find all remaining references**

```bash
grep -rn "e2e-acceptance\|/e2e-acceptance\|acceptance" e2e-pipeline/ --include="*.md" --include="*.json" --include="*.sh" | grep -v "skill-quality-findings" | grep -v "node_modules" | grep -v "docs/superpowers/"
```

This lists every file that still references acceptance (excluding historical findings and the spec/plan).

- [ ] **Step 3: Update each file**

For each file found in Step 2, apply the appropriate replacement:
- `/e2e-acceptance` → `/e2e-flow`
- "acceptance" in context of the skill → "flow" or remove
- Preserve historical mentions in `skill-quality-findings.md`

Work through the cleanup table from the spec systematically:
1. `skills/e2e-walkthrough/SKILL.md` — update verification decision references
2. `skills/e2e-compile/SKILL.md` — update flow source mention
3. `skills/e2e-test/SKILL.md` — update flow source mention
4. `CLAUDE.md` — update Planning Integration section (closed loop diagram, verification decision)
5. `docs/architecture.md` — update references
6. `docs/commands.md` — update references
7. `references/common-patterns.md` — update if referenced
8. `hooks/hooks.json` — update description text
9. `hooks/scripts/session-e2e-context.sh` — update systemMessage to: `"use /e2e-flow to generate from plans"`
10. `hooks/scripts/pre-commit-e2e-check.sh` — update if referenced

- [ ] **Step 4: Verify zero remaining references**

```bash
grep -rn "e2e-acceptance\|/e2e-acceptance" e2e-pipeline/ --include="*.md" --include="*.json" --include="*.sh" | grep -v "skill-quality-findings" | grep -v "node_modules" | grep -v "docs/superpowers/"
```

Expect: 0 results (only historical findings and spec/plan files should have it).

- [ ] **Step 5: Commit**

```bash
git add -A e2e-pipeline/
git commit -m "refactor(e2e-pipeline): remove e2e-acceptance, replace all refs with /e2e-flow"
```

---

### Task 6: Modify e2e-walkthrough

**Files:**
- Modify: `skills/e2e-walkthrough/SKILL.md`
- Modify: `skills/e2e-walkthrough/reference.md`

- [ ] **Step 1: Read current walkthrough SKILL.md**

Read `skills/e2e-walkthrough/SKILL.md` fully.

- [ ] **Step 2: Update frontmatter description**

Remove trigger words related to smoke and verify. Update description to focus on: exploration, visual QA, debug, demo recording. Remove "record walkthrough" and "video walkthrough" if they should now trigger `/e2e-flow`.

New description should include triggers: "walkthrough", "explore this feature", "walk the UI", "step through", "browse the app", "guided e2e", "interactive walkthrough", "explore pages", "visual QA", "debug in browser", "demo recording".

- [ ] **Step 3: Remove --smoke mode**

Remove the entire `### --smoke Mode` section from SKILL.md (the 7 rules, ordering, per-page steps, dialog handling, post-walkthrough selector sweep). This is ~40 lines.

Add a redirect note in its place: `For smoke testing, use /e2e-flow --smoke.`

- [ ] **Step 4: Remove --verify mode**

Remove the `### --verify Mode (PR Verification)` section from SKILL.md. This includes the verification rules, checkpoint execution, and verify mode plan example. This is ~50 lines.

Add a redirect note: `For flow verification, use /e2e-flow --verify.`

- [ ] **Step 5: Update invocation table**

Remove `--verify` and `--smoke` from the invocation syntax line and the entry point table.

- [ ] **Step 6: Add role statement**

Add at the top of the skill (after the frontmatter description, before Pipeline Context):

```markdown
## Role

Interactive human-in-the-loop browser exploration. Use this when:
- **Exploring unknown features** — no spec, discovering what the app does
- **Visual QA** — subjective design review, layout inspection, responsive check
- **Debug escape hatch** — automated `/e2e-flow --verify` failed, need human eyes
- **Demo recording** — walkthrough with human narration for stakeholders

For automated flow generation → `/e2e-flow`
For automated flow verification → `/e2e-flow --verify`
For smoke testing → `/e2e-flow --smoke`
```

- [ ] **Step 7: Update reference.md if needed**

Check `reference.md` for any --smoke or --verify specific sections and remove/redirect them.

- [ ] **Step 8: Commit**

```bash
git add e2e-pipeline/skills/e2e-walkthrough/
git commit -m "refactor(e2e-pipeline): narrow walkthrough to exploration/QA/debug/demo"
```

---

### Task 7: Update e2e-skill-ops Impact Matrix

**Files:**
- Modify: `skills/e2e-skill-ops/SKILL.md`

- [ ] **Step 1: Read current skill-ops SKILL.md**

Read the Impact Matrix section.

- [ ] **Step 2: Add new files to Impact Matrix**

Add these to the matrix:
- `agents/e2e-flow-writer.md` — flow construction rules, validation logic, output format
- `agents/e2e-flow-verifier.md` — correction logic, recording lifecycle, report templates
- `skills/e2e-flow/SKILL.md` — codebase scan, agent dispatch, presentation
- `skills/e2e-flow/reference.md` — scan patterns, smoke rules, dispatch formats

Remove:
- `skills/e2e-acceptance/SKILL.md` (deleted)

- [ ] **Step 3: Commit**

```bash
git add e2e-pipeline/skills/e2e-skill-ops/SKILL.md
git commit -m "chore(e2e-pipeline): update skill-ops Impact Matrix for v2.0 agents"
```

---

## Chunk 4: Documentation and Validation

### Task 8: Update documentation files

**Files:**
- Modify: `CLAUDE.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/commands.md`
- Modify: `.claude-plugin/plugin.json`
- Modify: `hooks/hooks.json`

- [ ] **Step 1: Update CLAUDE.md**

Key sections to update:
1. **Architecture** section: Change `Skills (7)` listing — replace `e2e-acceptance` with `e2e-flow`. Add agents: `e2e-flow-writer`, `e2e-flow-verifier`. Update ASCII diagram.
2. **Data Flow** section: Add `/e2e-flow` output paths.
3. **Planning Integration** section: Replace `/e2e-acceptance` with `/e2e-flow` in closed loop diagram. Update verification decision.
4. **Recording Defaults** table: Add row for `/e2e-flow --verify` (ON by default, `--no-video` override).

- [ ] **Step 2: Update README.md**

1. Update pipeline diagram: `Map → Generate → Verify → Test → Analyze`
2. Update quick start commands: replace `/e2e-acceptance` with `/e2e-flow`
3. Add `/e2e-flow` command documentation
4. Update walkthrough description (narrowed role)
5. Update agent count (3 → 5)

- [ ] **Step 3: Update docs/architecture.md**

Replace all `/e2e-acceptance` references with `/e2e-flow`. Update the architecture diagram if present.

- [ ] **Step 4: Update docs/commands.md**

Add `/e2e-flow` command documentation. Remove `/e2e-acceptance` entries.

- [ ] **Step 5: Update plugin.json**

```json
{
  "description": "Browser E2E testing pipeline with context-isolating subagents — map UI, generate flows, verify & test, walk through apps, record video",
  "version": "2.0.0",
  "keywords": ["e2e", "browser-testing", "agent-browser", "ui-mapping", "flow-generation", "flow-verification", "video-recording", "subagents"]
}
```

Only update `description`, `version`, and `keywords`. Do NOT change other fields.

- [ ] **Step 6: Update hooks/hooks.json description**

Update the description field to remove "acceptance loop" wording.

- [ ] **Step 7: Commit docs**

```bash
git add e2e-pipeline/CLAUDE.md e2e-pipeline/README.md e2e-pipeline/docs/ e2e-pipeline/.claude-plugin/plugin.json e2e-pipeline/hooks/hooks.json
git commit -m "docs(e2e-pipeline): update docs and version for v2.0 role restructuring"
```

---

### Task 9: Final validation

- [ ] **Step 1: Verify no stale acceptance references**

```bash
grep -rn "e2e-acceptance\|/e2e-acceptance" e2e-pipeline/ --include="*.md" --include="*.json" --include="*.sh" | grep -v "skill-quality-findings" | grep -v "node_modules" | grep -v "docs/superpowers/"
```

Expect: 0 results.

- [ ] **Step 2: Verify new agent files exist and are valid**

```bash
ls -la e2e-pipeline/agents/e2e-flow-writer.md e2e-pipeline/agents/e2e-flow-verifier.md
head -3 e2e-pipeline/agents/e2e-flow-writer.md
head -3 e2e-pipeline/agents/e2e-flow-verifier.md
```

Both should exist and start with `---`.

- [ ] **Step 3: Verify new skill files exist**

```bash
ls -la e2e-pipeline/skills/e2e-flow/SKILL.md e2e-pipeline/skills/e2e-flow/reference.md
```

Both should exist.

- [ ] **Step 4: Verify acceptance skill is gone**

```bash
ls e2e-pipeline/skills/e2e-acceptance/ 2>/dev/null && echo "STILL EXISTS" || echo "REMOVED OK"
```

Expect: `REMOVED OK`.

- [ ] **Step 5: Verify plugin.json version**

```bash
grep '"version"' e2e-pipeline/.claude-plugin/plugin.json
```

Expect: `"version": "2.0.0"`.

- [ ] **Step 6: Cross-reference check**

Verify the flow-writer agent references match what the skill dispatches:
```bash
grep "flow-writer\|flow_writer\|e2e-flow-writer" e2e-pipeline/skills/e2e-flow/SKILL.md
grep "flow-verifier\|flow_verifier\|e2e-flow-verifier" e2e-pipeline/skills/e2e-flow/SKILL.md
```

Both should return matches.

- [ ] **Step 7: Verify walkthrough no longer has --smoke/--verify**

```bash
grep -n "\-\-smoke\|\-\-verify" e2e-pipeline/skills/e2e-walkthrough/SKILL.md
```

Should only appear in redirect notes ("For smoke testing, use /e2e-flow --smoke"), not as supported flags.

- [ ] **Step 8: Record validation in skill-quality-findings.md**

Append a new finding to `e2e-reports/skill-quality-findings.md`:

```markdown
### 2026-03-16: v2.0 Role Restructuring — Validation

**Changes:**
- Added agents: e2e-flow-writer (codebase analysis → flow YAML), e2e-flow-verifier (adaptive browser validation)
- Added skill: /e2e-flow (generate + verify + smoke, replaces /e2e-acceptance)
- Removed: e2e-acceptance skill
- Modified: e2e-walkthrough (removed --smoke, --verify), e2e-dispatch (added --flow route)
- Updated: CLAUDE.md, README.md, docs/, plugin.json (v2.0.0), hooks

**Validation:** All 8 success criteria from spec verified.
**Reference cleanup:** Zero stale e2e-acceptance references in active files.
```

- [ ] **Step 9: Final commit**

```bash
git add e2e-pipeline/e2e-reports/skill-quality-findings.md
git commit -m "chore(e2e-pipeline): v2.0 validation record in skill-quality-findings"
```

- [ ] **Step 10: Sync to local plugin cache**

After all commits, sync the updated plugin to the local cache so next session loads the new agents:

```bash
# The /kc-marketplace-sync skill handles this — invoke it after all commits
```

Note: New agent types (e2e-flow-writer, e2e-flow-verifier) won't be dispatchable until the next Claude Code session (agent registry is session-scoped per MEMORY.md).
