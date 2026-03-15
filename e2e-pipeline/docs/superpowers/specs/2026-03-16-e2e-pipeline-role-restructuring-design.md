# E2E Pipeline Role Restructuring — Design Spec

**Date:** 2026-03-16
**Version:** e2e-pipeline v1.5.0 → v2.0.0
**Scope:** Add flow-writer + flow-verifier agents, remove e2e-acceptance, restructure walkthrough role

## Problem

Flow creation is the pipeline bottleneck. Only two paths exist:
- `/e2e-acceptance` — template-based, no codebase analysis, no browser validation (shallow)
- `/e2e-walkthrough` — interactive, runs in main context, burns 120-330 lines per 10 steps (expensive)

No path is both autonomous and thorough. The verify-fix-retry loop for draft flows runs in main context, consuming 30-50K tokens across 3 iterations.

## Solution

Two new subagents that handle flow generation and verification autonomously. Main context only dispatches and reads results.

## Pipeline Architecture

### Before (v1.5.0)

```
3 agents: mapper, test-runner, trace-analyzer
7 skills: dispatch, map, acceptance, test, walkthrough, compile, skill-ops
```

### After (v2.0.0)

```
5 agents: mapper, flow-writer, flow-verifier, test-runner, trace-analyzer
7 skills: dispatch, map, flow (NEW), test, walkthrough, compile, skill-ops
                        ↑ replaces acceptance
```

### Data Flow

```
                    ┌─────────────┐
                    │  /e2e-map   │
                    │ mapper agent│
                    └──────┬──────┘
                           │
                      mapping.yaml
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
     ┌────────────┐  ┌──────────┐  ┌──────────────┐
     │ /e2e-flow  │  │/e2e-test │  │/e2e-walkthrough│
     │            │  │          │  │ (human-in-loop)│
     │ writer ──→ │  │ runner   │  │ main context   │
     │ verifier──→│  │          │  │                │
     └─────┬──────┘  └────┬─────┘  └───────┬───────┘
           │               │                │
     flow.yaml +      report.md        flow.yaml +
     pr-summary.md    trace.zip        report.md
     video.mp4
```

### Agent Responsibility Matrix

| Agent | Input | Behavior | Output | Browser | Writes Files |
|-------|-------|----------|--------|---------|-------------|
| mapper | routes, base_url | Explore UI, extract selectors | mapping.yaml | Yes | mapping |
| **flow-writer** | description + mapping + codebase summary | Read code, write flow YAML | flow.yaml | **No** | flow |
| **flow-verifier** | flow + mapping | Run flow, repair/adapt/enrich, clean run | verified flow + pr-summary + video | Yes | flow + mapping |
| test-runner | flow + mapping | Execute flow deterministically | report + trace | Yes | No |
| trace-analyzer | trace.zip | Parse API/console errors | analysis.md | No | No |

### Boundary Rules

- **flow-writer does not open browser** — pure codebase analysis + YAML generation
- **flow-verifier does not do broad codebase search** — only reads flow/mapping + browser DOM
- **test-runner does not modify flow/mapping** — deterministic, for CI/regression
- **walkthrough does not auto-generate PR reports** — human decides via Phase 4 menu

---

## `/e2e-flow` Skill Design

### Invocation

```
/e2e-flow <description> [--from <plan.md|PR#>] [--smoke] [--verify] [--pr N] [--no-video] [--mapping name]
```

| Usage | Behavior |
|-------|----------|
| `/e2e-flow "user creates project"` | writer → draft flow |
| `/e2e-flow --from plan.md` | writer (extract criteria from plan) → draft flow |
| `/e2e-flow --from pr 123` | writer (extract UI changes from PR diff) → draft flow |
| `/e2e-flow --smoke` | writer (visit-all-pages from mapping) → draft flow |
| `/e2e-flow "create project" --verify` | writer → verifier → verified flow |
| `/e2e-flow --verify acceptance-create-project` | verifier only (existing flow, skip writer) |
| `/e2e-flow --from pr 123 --verify --pr 123` | read PR diff → writer → verifier → post PR comment |

**Flag distinction:** `--from pr N` = input source (read PR diff to understand what to test). `--pr N` = output destination (post pr-summary.md as PR comment). Both can be used together.

**Intentionally dropped from e2e-acceptance:** The `--validate` mode (audit existing flows against plan coverage) is not migrated. It was never used in practice, and flow coverage can be assessed by running `/e2e-test --all` instead.

### Internal Flow (3 phases)

#### Phase 0 — Prepare

1. Discover mapping (scan `.claude/e2e/mappings/`, select by `--mapping` or interactive)
2. Codebase scan (skill-side, lightweight grep/glob):
   - Routes (Next.js pages/, React Router, etc.)
   - Form components in relevant directories
   - API endpoints (fetch/axios calls)
   - Output: `context_summary` text block (~2-4K tokens)
3. Parse `--from` source if provided (plan text or `gh pr diff`)

#### Phase 1 — Generate (skip if `--verify` + existing flow name)

1. Dispatch `e2e-flow-writer` agent with: description, context_summary, mapping_path, output_dir, flow_name, source_text, smoke_mode
2. Receive: flow_path, step_count, warnings, coverage_notes
3. Present draft summary to user

#### Phase 2 — Verify (skip if no `--verify`)

1. Dispatch `e2e-flow-verifier` agent with: flow_path, mapping_path, auth_profile, base_url, app, report_dir, record (`false` when `--no-video`, otherwise `true`)
2. Receive: status, corrections, unfixable, report_path, pr_summary_path, video_path, trace_path, step_log_path
3. Dispatch `e2e-trace-analyzer` agent with `trace_path`, `report_dir`, and `step_log_path` (enables step-correlated analysis). Skill dispatches — subagents cannot dispatch other subagents.
4. Merge trace results into verifier's report.md
5. If `--pr`: confirm with user → commit + push screenshots → `gh pr comment` with pr-summary.md
#### Phase 3 — Present

- **Generate only**: "Flow generated: N steps → path. Next: `/e2e-flow --verify <name>`"
- **Verify pass**: Status + corrections table + media links + PR posting option
- **Verify fail**: Status + unfixable table + "Try: `/e2e-walkthrough` (human debug)"

### Codebase Scan Strategy (Phase 0)

Skill runs lightweight grep/glob (not Explore agent). Output format:

```
Routes found:
  /settings → src/app/settings/page.tsx
  /settings/connections → src/app/settings/connections/page.tsx

Components in scope:
  src/components/ConnectionForm.tsx — form fields: name, type, endpoint
  src/components/ConnectionDialog.tsx — dialog with confirm/cancel

API endpoints:
  POST /api/connections — creates connection
  DELETE /api/connections/:id — deletes connection

Mapping pages matching:
  settings-page (8 elements)
  add-connection-dialog (5 elements)
```

### `--smoke` Mode

Generates visit-all-pages flow from mapping (logic migrated from walkthrough):

1. Select pages: has `elements` + navigable `url_pattern` (exclude parameterized URLs, signin path, admin-only)
2. Sort: sidebar → main pages → settings → onboarding
3. Per page: Navigate → verify 2-3 key elements → screenshot
4. Dialogs: open-close cycle for primary dialog per page
5. Output: `smoke-<app>-<timestamp>.yaml`

Composable with `--verify` for automated smoke validation.

---

## flow-writer Agent Design

### Definition

```yaml
name: e2e-flow-writer
description: >
  Autonomous flow YAML generator. Reads codebase context + mapping
  to produce E2E test flows without browser interaction.
tools: [Read, Write, Grep, Glob]
color: magenta
model: inherit
```

No Bash tool — prevents accidental browser or side-effect execution. Pure analysis role. If Grep/Glob prove insufficient in subagent context, prefer expanding to `[Read, Write, Bash]` rather than working around limitations.

### Input Contract

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| description | string | Yes | What to test |
| mapping_path | string | Yes | Absolute path to mapping YAML |
| context_summary | string | Yes | Codebase scan results from skill |
| output_dir | string | Yes | `.claude/e2e/flows/` absolute path |
| flow_name | string | No | Override auto-naming |
| source_text | string | No | Plan/spec/PR diff text |
| smoke_mode | boolean | No | Visit-all-pages generation |

### Behavior

```
Step 1 — Parse inputs
  Read mapping YAML → pages, elements, url_patterns, auth config
  Parse context_summary → routes, components, API endpoints
  If source_text → extract acceptance criteria

Step 2 — Targeted code reads (max 10 file reads)
  For each relevant page in mapping:
    Read route component file (paths from context_summary)
    Identify: form fields, submit handlers, redirects, modals, error states
    Identify: API calls (endpoint, payload)

Step 3 — Flow construction
  Map description/criteria → concrete steps:
    Navigate → from mapping url_patterns
    Click → from mapping elements (exact snake_case names)
    Fill → from component analysis (field names + reasonable test values)
    Expect → from component analysis (success states, redirects, toasts)

  Rules:
    - Every step MUST have expect
    - Element/page names MUST match mapping exactly
    - 5-15 steps (focused, not exhaustive)
    - v2 format (mapping: not app:, id: not name:)
    - Include timeout: for known slow operations

Step 4 — Validation pass
  Verify each page/element name exists in mapping
  Flag unresolvable references as warnings

Step 5 — Write output
  Write flow YAML to output_dir/<flow_name>.yaml
```

### Smoke Mode Variant

Step 2-3 replaced with:
- Filter mapping pages by navigability rules
- Generate 2-3 steps per page (navigate + verify key elements + screenshot)
- Include dialog open-close for primary dialogs

### Output Contract

```yaml
flow_path: "/abs/path/.claude/e2e/flows/create-project.yaml"
step_count: 8
warnings:
  - "element 'old_button' not found in mapping page 'settings'"
coverage_notes: "Covers: navigate, create, verify. Not covered: edit, delete"
```

---

## flow-verifier Agent Design

### Definition

```yaml
name: e2e-flow-verifier
description: >
  Adaptive flow validator. Runs E2E flows in browser, auto-repairs
  selector/URL/flow issues, enriches assertions, produces PR-ready
  report with video from the final clean run.
tools: [Bash, Read, Grep, Write]
color: blue
model: inherit
```

### Input Contract

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| flow_path | string | Yes | Flow YAML absolute path |
| mapping_path | string | Yes | Mapping YAML absolute path |
| auth_profile | string | Yes | `~/.agent-browser/<app>/` |
| base_url | string | Yes | Dev server URL |
| app | string | Yes | App name from mapping |
| report_dir | string | Yes | Output directory |
| record | boolean | No (default true) | Record video on final run |

### Execution Flow (2 rounds max)

#### Phase 1 — Setup

Pre-flight checks (`agent-browser --version`, `curl base_url`, auth profile check). Open browser with `--profile` (no recording in Round 1). Auth verification follows test-runner procedure: check `auth.type` from mapping, auto-login via test OTP if available, manual prompt if needed. Start trace.

#### Phase 2 — Round 1: Fix Run

For each step in flow:
1. `snapshot -i` → find `@ref`
2. Attempt action
3. On failure → diagnose → apply correction or log as unfixable
4. Record correction: `{ step_id, result, correction_type, detail }`

After all steps:
- `corrections > 0 && unfixable == 0` → write corrected files → Round 2
- `unfixable > 0` → write partial fixes → skip to Phase 4
- `corrections == 0` → all passed first try → Round 1 is the clean run → Phase 4

#### Phase 3 — Round 2: Clean Run (evidence run)

**Browser lifecycle between rounds:**
1. Stop trace from Round 1: `agent-browser trace stop`
2. Close browser: `agent-browser close`, wait 3s for daemon shutdown
3. Start recording: `agent-browser record start "$REPORT_DIR/full.webm"` (creates fresh context)
4. Open browser: `agent-browser open --headed "$base_url"` (navigates within recording context)
5. Re-authenticate: use `auth.test_accounts` from mapping for auto-login (no `--profile` when recording). If no test accounts available and auth fails, mark Round 2 as unfixable with reason "auth expired in recording context" and use Round 1 results as final output.
6. Start trace: `agent-browser trace start`

**Execution:**
- Re-run full flow with corrected flow/mapping
- Per-step: snapshot → action → wait → screenshot → `errors --json`
- Write step-log.json at end (for trace-analyzer consumption by skill)
- New failure in Round 2 → log as unfixable, do NOT attempt Round 3
- Stop recording (`record stop`), stop trace (`trace stop "$REPORT_DIR/trace.zip"`)

#### Phase 4 — Output

**Note:** Trace analysis is NOT dispatched by the verifier (subagents cannot dispatch other subagents). The verifier saves trace.zip + step-log.json, and the `/e2e-flow` skill dispatches trace-analyzer after receiving verifier results.

1. Write `report.md` — full technical report with corrections history
2. Write `pr-summary.md` — PR reviewer version (status + corrections table + screenshots + video)
3. MP4 video conversion (1.5x speed) from recording
4. Write `corrections.md` — detailed diff of all flow/mapping changes
5. Write back corrected flow YAML + mapping YAML (overwrite originals)

**Mapping write-back safety rules:**
- Only update selectors for elements actually referenced by the current flow
- Never delete or rename elements not tested in this run
- Preserve all pages/elements not visited during verification
- Write a comment at top of mapping noting last verifier update timestamp

**Write-back on partial/fail status:** Write-back always happens, even when status is `partial` or `fail`. Corrections from Round 1 that passed in Round 2 are kept. Steps that failed in Round 2 are marked unfixable in the output, but their Round 1 corrections are still applied (they improved the flow even if other steps remain broken). The `status` field reflects overall outcome; `flow_updated`/`mapping_updated` reflect whether any writes occurred.

**Auth config:** The verifier reads auth configuration (type, test_accounts, verification, manual_prompt) from the mapping YAML at `mapping_path` — not passed as a separate input field.

### Three-Layer Correction Logic

#### Layer 1: REPAIR (confidence: HIGH — auto-fix, no marker)

| Symptom | Diagnosis | Fix |
|---------|-----------|-----|
| Selector not found | snapshot → match by description/role → find new selector | Update mapping |
| URL pattern changed | `get url` → compare with flow expectation | Update flow navigate action |
| Element renamed | snapshot → semantic match against mapping description | Update mapping name + selector |

#### Layer 2: ADAPT (confidence: MEDIUM — auto-fix, mark `[auto-inserted]`)

| Symptom | Diagnosis | Fix |
|---------|-----------|-----|
| Modal/dialog blocking | snapshot → detect dialog role | Insert confirm/dismiss step |
| Loading spinner | snapshot → detect progressbar/spinner | Insert wait step |
| Toast/banner covering element | snapshot → obstruction detection | Insert dismiss step |
| New required field | snapshot → empty required input | Insert fill step (reasonable test value) |

#### Layer 3: ENRICH (confidence: LOW-MEDIUM — attempt, mark `[enriched]`)

| Symptom | Diagnosis | Fix |
|---------|-----------|-----|
| Step passes but no expect | Check flow step expect array | Add expect from visible DOM state |
| Redirect without verification | URL changed but no expect | Add `url contains` assertion |
| Form submit without result check | POST success but next step has no verify | Add navigate + verify step |

### Correction Metadata in Flow YAML

```yaml
steps:
  - id: confirm-dialog
    action: "Click confirm_button on confirmation-dialog"
    expect: ["confirmation-dialog not visible"]
    _correction: { type: "adapt", round: 1, reason: "modal blocked submit" }
```

`_correction` is metadata — test-runner ignores it, corrections.md and PR reviewers use it.

### Output Contract

```yaml
status: "pass" | "partial" | "fail"
total_steps: 10
original_steps: 8
corrections:
  - type: "repair|adapt|enrich"
    step_id: "step-3"
    detail: "selector updated: [data-testid='add-btn'] → [data-testid='add-connection-btn']"
unfixable:
  - step_id: "step-7"
    symptom: "Element 'export_button' not found on settings page"
    dom_context: "Page has 12 buttons, none match semantically"
rounds: 2
report_path: "/abs/path/report.md"
pr_summary_path: "/abs/path/pr-summary.md"
video_path: "/abs/path/video.mp4"
corrections_path: "/abs/path/corrections.md"
flow_updated: true
mapping_updated: true
trace_path: "/abs/path/trace.zip"
step_log_path: "/abs/path/step-log.json"
```

---

## Skill Changes

### Remove: e2e-acceptance

**Delete:** `skills/e2e-acceptance/` directory.

**Clean up references (e2e-skill-ops impact scan scope):**

| File | Reference | Action |
|------|-----------|--------|
| `skills/e2e-dispatch/SKILL.md` | Routing to acceptance; `--smoke`/`--verify` forwarded to `--walk` | Remove acceptance route, add `/e2e-flow` route. Route `--smoke`/`--verify` to `--flow` instead of `--walk` |
| `skills/e2e-walkthrough/SKILL.md` | `--verify` mentions acceptance verification decision | Update to point to `/e2e-flow --verify` |
| `skills/e2e-compile/SKILL.md` | "Create flows with `/e2e-acceptance`" | Change to `/e2e-flow` |
| `skills/e2e-test/SKILL.md` | Mentions acceptance-generated flows | Change to `/e2e-flow` |
| `CLAUDE.md` | Planning Integration, closed loop diagram, draft flow template | Full section update |
| `docs/architecture.md` | References to e2e-acceptance | Update to `/e2e-flow` |
| `docs/commands.md` | References to e2e-acceptance | Update to `/e2e-flow` |
| `references/common-patterns.md` | If acceptance referenced | Update |
| `hooks/hooks.json` | Description: "E2E acceptance loop" | Update description text |
| `hooks/scripts/session-e2e-context.sh` | systemMessage mentions `/e2e-acceptance` | Change to: `"use /e2e-flow to generate from plans"` |
| `hooks/scripts/pre-commit-e2e-check.sh` | If acceptance referenced | Update |
| `e2e-reports/skill-quality-findings.md` | Historical records | No change (preserve history) |

### Modify: e2e-walkthrough

**Remove:**
- `--smoke` mode (migrated to `/e2e-flow --smoke`)
- `--verify` mode (migrated to `/e2e-flow --verify`)
- Smoke plan generation logic (7 rules + post-walkthrough selector sweep)

**Retain:**
- `--pr N`, `--issue ID`, `--sites`, `--no-video`
- `--mode guided|step|auto`
- Phase 1-4 full flow (plan → approve → execute → output)
- Phase 4 checklist (13 items)
- Mapping self-repair, all common mistakes

**Add:**
- Explicit role statement: "For exploration, visual QA, debug, and demo recording"
- Updated skill description (remove verify/smoke trigger words)

### Modify: e2e-dispatch

**Add route:** `--flow` → Skill: e2e-flow

**Reroute from `--walk`:** If `--smoke` or `--verify` is passed with `--walk`, redirect to `--flow` with appropriate flags. `--walk` no longer accepts these flags.

**Update quick reference:**
```
Available operations:
  --map       Create/update UI mappings
  --flow      Generate or verify E2E flows      ← NEW
  --test      Run E2E test flows
  --walk      Interactive walkthrough (explore, visual QA, debug, demo)
  --compile   Compile flows to bash scripts
  --ops       Debug/maintain pipeline skills
```

### Modify: e2e-test

No core logic changes. Update references from `/e2e-acceptance` to `/e2e-flow`.

### Modify: plugin.json

```json
{
  "description": "Browser E2E testing pipeline with context-isolating subagents — map UI, generate flows, verify & test, walk through apps, record video",
  "version": "2.0.0",
  "keywords": ["e2e", "browser-testing", "agent-browser", "ui-mapping", "flow-generation", "flow-verification", "video-recording", "subagents"]
}
```

### Modify: CLAUDE.md

- Architecture: 7 skills + 5 agents inventory
- Data Flow: add `/e2e-flow` output paths
- Planning Integration: closed loop diagram `/e2e-acceptance` → `/e2e-flow`
- Verification decision: draft flow → `/e2e-flow --verify`, no flow → `/e2e-flow "desc" --verify`
- Recording Defaults: add `/e2e-flow --verify` row (ON by default)

### Modify: README.md

- Pipeline diagram: Map → Generate → Verify → Test → Analyze (5 agents)
- Quick start: replace acceptance examples with `/e2e-flow`
- Commands section: add `/e2e-flow` full usage
- Update walkthrough description (narrowed role)

### Modify: e2e-skill-ops Impact Matrix

Add to scan scope:
- `agents/e2e-flow-writer.md`
- `agents/e2e-flow-verifier.md`
- `skills/e2e-flow/SKILL.md`

---

## Version & Naming

- Plugin version: `1.5.0` → `2.0.0` (breaking: acceptance removed, new agents, walkthrough scope changed)
- Skill name: `e2e-flow` (not `e2e-generate` — "flow" is the artifact, covers both generate and verify)
- Agent names: `e2e-flow-writer`, `e2e-flow-verifier` (clear role in name)

## Implementation Order

1. Create `e2e-flow-writer` agent (`agents/e2e-flow-writer.md`)
2. Create `e2e-flow-verifier` agent (`agents/e2e-flow-verifier.md`)
3. Create `/e2e-flow` skill (`skills/e2e-flow/SKILL.md` + `reference.md`)
4. Update `e2e-dispatch` routing (add `--flow`, reroute `--smoke`/`--verify` from `--walk`)
5. Remove `e2e-acceptance` (`skills/e2e-acceptance/` directory)
6. Update all references (cleanup table above — 12 files)
7. Modify `e2e-walkthrough` (remove `--smoke`/`--verify`, update role statement)
8. Update `e2e-skill-ops` Impact Matrix (add 3 new files)
9. Update docs (`CLAUDE.md`, `README.md`, `docs/architecture.md`, `docs/commands.md`)
10. Update `plugin.json` (version 2.0.0, description, keywords)
11. Run `/e2e-skill-ops --maintain` for full impact scan validation

Steps 1-3 are independent (can parallelize). Steps 5-8 depend on step 3. Step 11 is the final verification gate.

## Success Criteria

1. `/e2e-flow "description"` produces a valid flow YAML grounded in codebase + mapping
2. `/e2e-flow --verify <flow>` runs flow, auto-fixes selector/gap issues, produces PR-ready report with video
3. `/e2e-flow "desc" --verify --pr N` does end-to-end: generate → verify → post PR comment
4. `/e2e-flow --smoke` generates visit-all-pages flow from mapping
5. `/e2e-walkthrough` no longer has `--smoke` or `--verify` flags
6. No references to `e2e-acceptance` remain in active skill/agent files
7. README.md reflects new 5-agent pipeline
8. All existing `/e2e-test` and `/e2e-map` functionality unchanged (zero regression)
