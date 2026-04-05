---
name: e2e-flow
description: Use when generating E2E test flows from plans, specs, or PRs, verifying flows in browser or CLI, running smoke tests across all mapped pages, or recording backend/API verification with asciinema. Supports browser UI flows, CLI-only flows (Execute external), and mixed flows. Triggers on "e2e flow", "generate flow", "create flow", "verify flow", "draft flow", "smoke test", "e2e smoke", "write a flow", "produce flow", "validate flow", "flow from plan", "cli flow", "backend e2e", "api test flow", "cli recording".
---

# E2E Flow — Generate & Verify

Generate and verify E2E flows — browser UI, CLI commands, or API checkpoints. Combines autonomous flow generation (codebase analysis, no browser) with adaptive verification: browser flows use auto-repair, CLI-only flows use asciinema recording.

## Pipeline Context

```
/e2e-map       → mapping.yaml        (map UI elements)
/e2e-flow      → flow.yaml + report  (generate & verify)
/e2e-test      → report.md           (replay automated)
/e2e-walkthrough → flow.yaml         (explore interactively)
```

## Invocation

```
/e2e-flow [--from <source>] [--smoke] [--verify-only] [--mapping <name>] [--issue ID] [--no-verify] [--no-video] [--no-pr] [--no-teams]
```

| Arg | Effect |
|-----|--------|
| (no args) | Generate from current conversation context |
| `--from <file>` | Read a plan file, spec, or requirements doc |
| `--from pr <N>` | Read PR diff via `gh pr diff` |
| `--smoke` | Generate visit-all-pages flow from mapping |
| `--verify-only` | Skip generation, verify an existing flow in browser |
| `--mapping <name>` | Target a specific mapping (skip selection if only one) |
| `--issue ID` | Include issue context in report header |
| `--no-verify` | Generate flow only, skip browser verification |
| `--no-video` | Skip video recording during verification |
| `--no-pr` | Skip PR auto-detection, commit, and PR comment posting |
| `--no-teams` | Force subagent mode even when Agent Teams is available |

### PR Mode (default)

PR mode is **enabled by default**. On invocation, auto-detect the current branch's PR:

```bash
gh pr view --json number,headRefName --jq '.number' 2>/dev/null
```

- **PR found** → PR mode active. Flow will be committed and results posted to PR.
- **No PR / not a git repo / `gh` unavailable** → PR mode silently skipped (no error).
- **`--no-pr`** → PR mode explicitly disabled regardless of PR existence.

## Knowledge Bootstrap (before mapping discovery)

Read accumulated patterns to inform flow generation and verification:

```
Read → ${CLAUDE_PLUGIN_ROOT}/references/learned-patterns.md
```

Use loaded patterns to:
- Apply known flow design patterns during generation (e.g., wait after modal trigger)
- Anticipate verifier correction patterns
- Avoid generating steps known to cause divergence

## Discover Mapping

1. Scan `.claude/e2e/mappings/*.yaml`
2. One file → use it. Read `app`, `base_url`, `auth` from the mapping. Set `flow_mode: browser`.
3. Multiple files + no `--mapping` → list them (show filename, `app`, `base_url`), ask user which to use. Set `flow_mode: browser`.
4. **None found → CLI-only intent check:**
   - Scan source material (conversation context, `--from` file content) for CLI signals: shell commands (`curl`, `psql`, `npm run`, `bun`, script paths), API endpoint testing, database queries, migration scripts, `Execute external` mentions
   - **CLI signals found** → set `flow_mode: cli-only`. Inform user: "No mapping found. Detected CLI/backend intent — generating CLI-only flow (Execute external / Verify external steps only)."
   - **No CLI signals** → ask user: "No mapping found. Options: (a) This is a CLI-only backend test → proceed without mapping, (b) Browser UI test → run `/e2e-map` first."
   - **`--smoke` mode** → stop: "Smoke mode requires a mapping. Run `/e2e-map` first." (smoke is inherently browser-based)
5. Parse failure → report error with line number and stop.

## Phase 0 — Prepare

### Source Parsing

**From file** (`--from <file>`):
- Read the file
- Extract acceptance criteria, user stories, verification steps, UI-facing requirements

**From PR** (`--from pr N`):
- `gh pr diff <N>` + `gh pr view <N> --json title,body`
- Identify changed UI components, routes, user-facing behavior
- Map changes to affected pages in the mapping

**From conversation** (no args):
- Scan recent context for planning artifacts, feature descriptions
- If no clear criteria found → ask: "What should the E2E flow verify?"

**Smoke mode** (`--smoke`): Skip source parsing. Mapping provides everything needed.

**Verify-only** (`--verify-only`):
- List existing flows in `.claude/e2e/flows/`
- Ask user which to verify (or accept flow name as argument)
- **Detect flow type**: Read the flow YAML. If ALL steps are `Execute external` or `Verify external` → set `flow_mode: cli-only` (skip browser verifier, go to Phase 2.5 CLI recording). Otherwise → `flow_mode: browser`.
- Skip to Phase 2

### Codebase Scan

For non-smoke, non-verify-only invocations, scan the codebase to build a `context_summary` for the flow-writer agent. See [reference.md](./reference.md) § Codebase Scan Strategy for exact patterns.

**Summary:** Identify routes → component files → form fields → API endpoints → external service integrations → assemble into `context_summary` text block. Also scan for external service integrations (PostHog, Langfuse, Sentry, webhooks) — see [reference.md](./reference.md) § External Service Discovery. Include matches in the `context_summary` under "External services detected".

**Cap:** Max 20 file reads during scan. Prioritize files matching affected pages.

### Present Plan

Before dispatching agents, present what will happen:

```
Flow generation plan:
  Source: <PR #940 / plan file / conversation>
  Mapping: <app-name> (<N> pages, <M> elements)
  Criteria: <N> acceptance items extracted
  External: <N> service integrations detected
  Estimated steps: ~<N>

Proceed? (y / adjust)
```

### Flow Write Authorization

A PreToolUse hook blocks direct writes to `.claude/e2e/flows/*.yaml`. The `/e2e-flow` skill must create a sentinel file to authorize its agents (flow-writer, flow-verifier) to write flow YAML.

**Protocol:**
1. **Create sentinel** — Write `.claude/e2e/.flow-write-authorized` (content: current unix timestamp) **before** dispatching the first flow-writing agent
2. **Delete sentinel** — Delete `.claude/e2e/.flow-write-authorized` **after** the last flow-writing agent returns

**Per mode:**
- Normal: create before Phase 1 → delete after Phase 2d
- `--no-verify`: create before Phase 1 → delete after Phase 1
- `--verify-only`: create before Phase 2b → delete after Phase 2d

The sentinel has a 10-minute staleness timeout as safety net — enforced by the PreToolUse hook. If the sentinel's timestamp is older than 10 minutes, the hook treats it as absent (stale sentinel = no authorization). This covers skill crashes where the sentinel is never explicitly deleted.

## Phase 1 — Generate (dispatch flow-writer agent)

### Mode selection

> Detection logic: see `references/agent-teams.md` § 1

- **Teams mode**: TeamCreate available AND `--no-teams` not set AND `flow_mode: browser` (CLI-only flows don't need Teams)
- **Subagent mode**: TeamCreate unavailable OR `--no-teams` set OR `flow_mode: cli-only`

### Teams mode: Pre-warm verifier browser (parallel with writer)

> Shared protocol: `references/agent-teams.md` § 2-3

When Teams mode is active AND `--no-verify` is NOT set, spawn the verifier teammate BEFORE dispatching the writer. This overlaps browser startup with flow generation.

```
TeamCreate(team_name="e2e-flow", description="Flow generation + verification")

Agent(
  team_name="e2e-flow",
  name="verifier",
  subagent_type="e2e-pipeline:e2e-flow-verifier",
  prompt="TEAMS MODE. Pre-warm: open browser at <base_url> with auth profile <auth_profile>.
          App: <app>. Report dir: <report_dir>.
          After browser is ready, send BROWSER_READY and wait for VERIFY_FLOW command."
)
```

Verifier opens browser in parallel while the writer generates the flow. By the time the writer returns, the verifier's browser is already warm.

**If TeamCreate or Agent spawn fails**: see `references/agent-teams.md` § 4. Clean up partial state, fall back to subagent mode for Phase 2.

If `--no-verify`: skip verifier spawn (no browser needed).

### Verifier health check (after writer returns)

After the flow-writer subagent returns, verify the pre-warmed verifier is still alive before proceeding to Phase 2:

1. Check `~/.claude/teams/e2e-flow/config.json` — verifier member still present?
2. If verifier is gone (crashed during pre-warm): log warning, `TeamDelete()`, fall back to subagent mode for Phase 2
3. If verifier sent `BROWSER_READY` during writer execution: proceed to Phase 2b directly
4. If verifier hasn't sent `BROWSER_READY` yet: wait up to 30s. No response → treat as crash (step 2)

### Generate

**→ Create flow-write sentinel** (see § Flow Write Authorization)

Dispatch `e2e-pipeline:e2e-flow-writer` (always as subagent — no browser, read-only, benefits from blocking return) with:
- `description`: Extracted criteria or feature description
- `mapping_path`: Absolute path to mapping YAML (**omit if `flow_mode: cli-only`**)
- `context_summary`: Assembled codebase scan results
- `output_dir`: `.claude/e2e/flows/` absolute path
- `source_text`: Full plan/spec/PR diff text (if `--from` used)
- `smoke_mode`: true if `--smoke`
- `flow_name`: User-specified or auto-generated
- `cli_only`: true if `flow_mode: cli-only`

See [reference.md](./reference.md) § Agent Dispatch Patterns for exact dispatch message format.

**On return:** Read the generated flow YAML.

**Post-generation validation:**
1. If `flow_mode: browser`: verify the flow's `mapping:` field matches the `app` value from the loaded mapping. If mismatch → treat as generation error (same cleanup path as invalid YAML below).
2. If `flow_mode: cli-only`: verify ALL steps use `action: "Execute external"` or `action: "Verify external"` only. If any step has a browser action (Click, Navigate, Type, etc.) → treat as generation error. A CLI-only flow with browser steps is invalid — the writer was given `cli_only: true` but produced mixed output.

Present summary to user:

```
Flow generated: .claude/e2e/flows/<name>.yaml
  Mode: <browser | cli-only>
  Steps: N
  Warnings: <count or "none">
  Coverage: <notes>

{if browser} Proceeding to browser verification...
{if cli-only} Proceeding to CLI recording...
```

If `--no-verify` → **delete flow-write sentinel** → if PR mode active, commit flow (`git add .claude/e2e/flows/<name>.yaml && git commit -m "test(e2e): add <flow-name> flow (unverified)"`) → skip to Phase 3 (no-verify path).

**If flow-writer fails or returns invalid YAML:**
1. Delete flow-write sentinel immediately
2. If Teams mode (verifier was pre-warmed): shutdown verifier → `TeamDelete()` (see `references/agent-teams.md` § 2 Teardown)
3. Report error to user with writer's error output
4. Skip all subsequent phases — do NOT proceed to Phase 2

## Phase 2 — Verify (dispatch flow-verifier + trace-analyzer)

**CLI-only flows (`flow_mode: cli-only`)**: Skip Phase 2a-2d entirely. Jump directly to Phase 2.5 (CLI recording). Browser verifier is not dispatched — there are no browser steps to verify.

### 2a. Pre-flight (browser flows only)

```bash
agent-browser --version
curl -s -o /dev/null -w "%{http_code}" <base_url>
ls ~/.agent-browser/<app>/ 2>/dev/null
```

Dev server must be running. Auth profile should exist (run `/e2e-map` or `/e2e-walkthrough` first to create one).

**Teams mode**: pre-flight already passed during Phase 1 pre-warm. If verifier sent `BROWSER_READY`, skip pre-flight.

### 2b. Dispatch flow-verifier

**→ If `--verify-only`, create flow-write sentinel now** (see § Flow Write Authorization)

---

**Teams mode** (verifier already spawned and browser ready):

**Step 0 — Liveness re-check** (before sending any command): Verify the verifier member still exists in `~/.claude/teams/e2e-flow/config.json`. If the verifier disappeared between `BROWSER_READY` and now (e.g., crashed while idle), fall back to subagent mode immediately — do NOT send VERIFY_FLOW to a dead teammate.

**Step 1 — Send VERIFY_FLOW:**

```
SendMessage(
  to="verifier",
  message="VERIFY_FLOW\nflow_path: <path>\nmapping_path: <path>\nbase_url: <url>\nauth_profile: <path>\nrecord: <bool>",
  summary="Verify flow: <flow-name>"
)
```

**Step 2 — Wait for ROUND_1_STATUS** (verifier sends after Round 1 completes):

Parse the status field: `all_pass`, `has_corrections`, `has_unfixable`. Also parse corrections count, unfixable count, and per-step details.

**Step 3 — Present Round 1 summary to user:**

```
Round 1 complete:
  Status: <all_pass | has_corrections | has_unfixable>
  Corrections: N (R repair, A adapt, E enrich)
  Unfixable: N
  {if corrections} Details: <top 3 corrections> {endif}
```

**Step 4 — Decide and send guidance:**

| Round 1 status | Guidance | Rationale |
|----------------|----------|-----------|
| `all_pass` (0 corrections, 0 unfixable) | `SKIP_ROUND_2` | Round 1 is already clean evidence |
| `has_corrections` (corrections > 0, unfixable == 0) | `PROCEED_ROUND_2` | Need clean evidence without repair noise |
| `has_unfixable` (unfixable > 0) | `SKIP_ROUND_2` | Unfixable issues mean Round 2 would also fail at the same spots |

```
SendMessage(
  to="verifier",
  message="<PROCEED_ROUND_2 | SKIP_ROUND_2>",
  summary="Round 2: <proceed | skip>"
)
```

**Step 5 — Wait for VERIFICATION COMPLETE** containing final results (report path, trace path, corrections, status).

**Timeout/crash handling**: If no `ROUND_1_STATUS` within 120s, or no `VERIFICATION COMPLETE` within 120s after sending guidance:
1. Log warning with verifier's last known state
2. **Delete flow-write sentinel immediately**
3. `TeamDelete()` to clean up the team
4. Skip Phase 2c, 2d, 2.5 (no verifier output to process)
5. **Still present Phase 3 results** — show error status with the generated flow path and suggest re-running with `--no-teams`:
   ```
   E2E Flow: <flow-name>
   Status: ERROR (verifier crash/timeout)
   Flow:    .claude/e2e/flows/<name>.yaml (generated, unverified)
   Suggestion: Re-run `/e2e-flow --verify-only <flow-name> --no-teams`
   ```
   The generated flow YAML is kept on disk — it may be valid and only needs re-verification.

For `--verify-only` with existing team: detect existing team (`references/agent-teams.md` § 2). If verifier alive → check if the new flow's `base_url` and `auth_profile` match the verifier's current session. If they differ, include `base_url` and `auth_profile` in the `VERIFY_FLOW` command so the verifier can close and reopen the browser (see `references/agent-teams.md` § 5 — Browser state isolation on reuse). If same → send `VERIFY_FLOW` directly (no browser restart). **Sentinel**: create flow-write sentinel BEFORE sending VERIFY_FLOW to the existing verifier (same as new-verifier path).

---

**Subagent mode** (original behavior):

Dispatch `e2e-pipeline:e2e-flow-verifier` with:
- `flow_path`: Path to generated (or existing) flow YAML
- `mapping_path`: Path to mapping YAML
- `auth_profile`: `~/.agent-browser/<app>/`
- `base_url`: From mapping
- `app`: From mapping
- `report_dir`: `.claude/e2e/reports/<timestamp>/`
- `record`: `true` (unless `--no-video`)

See [reference.md](./reference.md) § Agent Dispatch Patterns for exact format.

### 2c. Dispatch trace-analyzer

After verifier returns, if `trace_path` is present:

Dispatch `e2e-pipeline:e2e-trace-analyzer` with:
- `trace_path`: From verifier output
- `report_dir`: Same as verifier
- `step_log_path`: From verifier output (if present)

### 2d. Process results

Merge verifier output + trace analysis:
- Corrections applied (repair/adapt/enrich counts)
- Unfixable issues
- Checkpoint results (external execution/verification pass/fail/skip)
- API failures and console errors from trace
- Video path

If verifier applied corrections (`flow_updated: true` or `mapping_updated: true`), present a correction diff summary before the full report:

```
Verifier corrections:
  Corrected N selectors, inserted M steps, enriched K assertions
  Flow updated: .claude/e2e/flows/<name>.yaml
  Mapping updated: .claude/e2e/mappings/<app>.yaml
```

### Phase 2.5 — Media Post-Processing

After verifier and trace-analyzer return, dispatch media processing.

**Detect flow type**: Parse the flow YAML steps. If ALL steps use `action: "Execute external"` or `action: "Verify external"` (zero browser steps), this is a **CLI-only flow**.

**Browser flow** (has browser steps):
```
Agent(subagent_type="e2e-pipeline:e2e-media-processor"):
  "Process media:
   report_dir: <report_dir>
   output_name: verification"
```

**CLI-only flow** (no browser steps):

1. Check prerequisites: `command -v asciinema && command -v agg`. If missing → warn, skip recording.
2. Record CLI execution (re-run the primary `Execute external` command):
   ```bash
   asciinema rec --cols 120 --rows 35 \
     -c "<primary execute command>" "$REPORT_DIR/recording.cast"
   ```
3. Dispatch media processor in CLI mode:
   ```
   Agent(subagent_type="e2e-pipeline:e2e-media-processor"):
     "Process media:
      report_dir: <report_dir>
      cast_path: <report_dir>/recording.cast
      output_name: verification"
   ```

Agent returns: `gif_path`, `mp4_path`, `thumbnail_path`. Use these in Phase 3 results.

**→ Delete flow-write sentinel** (all flow-writing agents have returned)

**Teams mode: Teardown verifier** — After media processing, shutdown the verifier teammate and delete team (`references/agent-teams.md` § 2). For `--verify-only` re-runs, keep verifier alive (user may re-verify).

### Phase 2.6 — Commit Flow (PR mode only)

**Skip entirely** when `--no-pr` is set or no PR was detected in the auto-detection step.

When PR mode is active (PR detected and `--no-pr` not set), commit the finalized flow YAML:

```bash
git add .claude/e2e/flows/<name>.yaml
git commit -m "test(e2e): add <flow-name> flow"
```

**Timing matters**: commit AFTER verification corrections are applied — the committed flow is the verified version, not the raw generation output. If verification updated the mapping too, include it:

```bash
git add .claude/e2e/flows/<name>.yaml .claude/e2e/mappings/<app>.yaml
git commit -m "test(e2e): add <flow-name> flow (verified)"
```

For `--verify-only` mode, only commit if the verifier made corrections (`flow_updated: true`):

```bash
git add .claude/e2e/flows/<name>.yaml
git commit -m "fix(e2e): update <flow-name> flow (re-verified)"
```

## Phase 3 — Present Results

### Summary

```
E2E Flow: <flow-name>
Status: <PASS ✅ | PARTIAL ⚠️ | FAIL ❌>
─────────────────────────────
Steps:       N (M original + K inserted)
Corrections: N (R repair, A adapt, E enrich)
Unfixable:   N
Checkpoints: N pass, M fail, K skip
Trace:       N API failures, M console errors
─────────────────────────────
Flow:    .claude/e2e/flows/<name>.yaml
Report:  .claude/e2e/reports/<ts>/report.md
Video:   .claude/e2e/reports/<ts>/verification.mp4

{if corrections}
Corrections applied:
  - step-3: selector repair (add_btn → add_connection_button)
  - step-3.1: [auto-inserted] confirmation dialog
{endif}

{if unfixable}
Unfixable issues:
  - step-7: Element not found (export feature not implemented?)
{endif}

{if checkpoint_results}
Checkpoint results:
  - trigger-sessions: PASS (cli: recce-cloud run ×3, exit 0)
  - verify-posthog: SKIP (POSTHOG_API_KEY not set)
{endif}
```

### PR Posting (default when PR detected)

When PR mode is active, post results to the PR. Ask user to confirm, then:

1. **Upload media to draft release** (private repos — `raw.githubusercontent.com` returns 403):
   ```bash
   # Create a draft release for E2E assets (reuse if tag exists)
   gh release create e2e-assets-<branch> --draft --title "E2E assets (<branch>)" --notes ""
   # Upload screenshots and video
   gh release upload e2e-assets-<branch> .claude/e2e/reports/<ts>/*.png .claude/e2e/reports/<ts>/*.mp4 --clobber
   ```
   Asset URLs: `https://github.com/<owner>/<repo>/releases/download/e2e-assets-<branch>/<filename>`

2. **Update `pr-summary.md`**: Replace relative image paths with release asset URLs.

3. **Post to PR**: `gh pr comment <N> --body-file .claude/e2e/reports/<ts>/pr-summary.md`

**Why draft release?** GitHub CLI has no API for uploading images to PR comments ([cli/cli#1895](https://github.com/cli/cli/issues/1895)). Draft releases are the only CLI-friendly method that produces stable, repo-scoped URLs for images and videos. The draft release is visible in the Releases page but does not create a real release.

**⚠️ Auth context matters**: Draft release asset URLs require GitHub authentication. They work in **PR comments** (reader is logged in) but **fail in Slack and other external services** (unfurler has no auth → 403). For Slack announcements, link to the PR comment URL instead of embedding image URLs directly. See `kc-pr-announce` skill for the correct Slack media strategy.

### Next Steps (always shown)

**After verification (normal path):**

```
Next steps:
- `/e2e-test <flow-name>` — replay this flow automatically
- `/e2e-test <flow-name> --video` — replay with recording
- `/e2e-compile <flow-name>` — compile to standalone bash script for CI
{if corrections}
- `/e2e-flow --verify-only <flow-name>` — re-verify after fixing issues
{endif}
{if unfixable}
- `/e2e-map --page <page>` — re-scan pages with missing elements
{endif}
- `/e2e-walkthrough` — explore interactively
```

**After `--no-verify` (generation only):**

When Phase 2 is skipped, present the flow-writer output summary + next steps:

```
Flow generated: .claude/e2e/flows/<name>.yaml
  Steps: N
  Warnings: <count or "none">
  Coverage: <notes>

Next steps:
- `/e2e-flow --verify-only <flow-name>` — verify in browser with auto-repair
- `/e2e-test <flow-name> --video` — replay with recording
- `/e2e-compile <flow-name>` — compile to standalone bash script
```

## Phase 4 — Learning (D1 only)

After presenting results, evaluate findings for skill-level knowledge capture.

Read → `${CLAUDE_PLUGIN_ROOT}/references/knowledge-capture.md`

### D1 candidates (auto-append)

Scan generation + verification results for general patterns:
- Flow structures that the verifier consistently corrects (indicates generation gap)
- Codebase scan strategies that yield better element coverage
- Checkpoint patterns that work/fail across services
- Smoke mode patterns for different UI frameworks

Auto-append to `${CLAUDE_PLUGIN_ROOT}/references/learned-patterns.md`. Notify: "Appended pattern: [title]"

### Skip conditions

- `--no-verify` with zero warnings → skip (generation-only, no feedback signal)
- Zero corrections AND zero unfixable AND no novel observations → skip
- All findings already in learned-patterns.md → skip (no duplicates)

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Running verify without dev server | Pre-flight checks catch this — but verify base_url is accessible |
| Element names not matching mapping | Flow-writer validates against mapping. Manual edits can drift — re-run `/e2e-flow` |
| Smoke test on app with dynamic URLs | Smoke auto-skips pages with `${id}` parameters. This is correct behavior, not a bug. |
| Skipping trace analysis | Always dispatch trace-analyzer after verifier — even on PASS. Silent API failures are invisible otherwise. |
| Re-dispatching verifier for minor fixes | Verifier does its own repair loop (2 rounds max). If it returns PARTIAL, the remaining issues are genuinely unfixable by automation. |
| Generating browser flow without mapping | Mapping must exist for browser steps. `/e2e-map` before `/e2e-flow`. CLI-only flows (all Execute/Verify external) do NOT need mapping. |
| Sending CLI-only flow to browser verifier | CLI-only flows skip Phase 2a-2d entirely. Go directly to Phase 2.5 CLI recording. |
| Adding browser steps to CLI-only flow | CLI-only mode generates ONLY Execute external / Verify external. If browser steps are needed, mapping is required — re-run with `/e2e-map` first. |
| Bypassing flow-writer for cross-boundary flows | Always dispatch flow-writer — it supports `Execute external` and `Verify external` steps for non-browser actions (CLI, API, analytics). Runner limits ≠ writer limits. Never hand-write flows to avoid the agent. |
| Duplicate D1 entry | Search learned-patterns.md before appending |
| Sending VERIFY_FLOW to dead verifier | Always re-check `config.json` for verifier presence immediately before sending VERIFY_FLOW — a verifier can crash between BROWSER_READY and the next command |
| Deleting unverified flow after crash | Keep the generated flow YAML — it may be valid. Suggest `--verify-only --no-teams` to re-verify. |
