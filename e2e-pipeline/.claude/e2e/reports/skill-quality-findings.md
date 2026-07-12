# E2E Skill Quality Findings

Persistent record of skill gaps, fixes, and feature additions. Referenced by `/e2e-skill-ops` on every invocation.

## New Features

### 2026-03-16: Verify External Support in Flow-Writer (Approach B — Active Discovery)

**Problem**: flow-writer agent couldn't generate `Verify external` checkpoint steps. Execution side (test-runner § 2m, walkthrough, compiler) fully supported the pattern since v1.5.0, but generation side was missing — flows with external verification had to be hand-written.

**Solution** (5 change points):
1. `agents/e2e-flow-writer.md` — `Verify external` action type + `verify:` schema + detection heuristic (text parsing on `source_text` + `context_summary`) + rule 8 exemption + Step 4 validation skip
2. `skills/e2e-flow/reference.md` — External Service Discovery (grep patterns for SDK calls) + External Verification Templates (analytics, tracing, generic)
3. `skills/e2e-flow/SKILL.md` — Phase 0 codebase scan includes external services + Present Plan shows count
4. `agents/e2e-flow-verifier.md` — Pass-through rule for checkpoint steps (skip browser interaction, log as skip) + Critical Rule 15

**Design spec**: `docs/superpowers/specs/2026-03-16-flow-writer-verify-external-design.md`

**Key design decisions**:
- Approach B (Active Discovery) over A (passive) or C (structured handoff): orchestrator scans via grep, passes results as free-text in `context_summary` — no input contract change, consistent with existing convention
- Detection heuristic includes explicit negative case: "If neither source_text nor context_summary contains signals, do NOT generate checkpoints"
- Soft cap on checkpoints: "prefer max 2, group if more than 2 integration points"
- Verifier pass-through in both Phase 2 per-step loop AND Critical Rules (pressure-resistance)

**Quality check** (kc-plugin-forge):
- 2 LOW issues found and fixed before applying: (1) missing negative case in heuristic, (2) missing Critical Rule 15 in verifier
- 13/13 chain verification checks passed (writer → verifier → runner field name consistency)

**Feature 1b — Execute External Checkpoints** (same session):
- **What**: `action: "Execute external"` step type — symmetric counterpart to `Verify external`. Triggers non-browser actions (CLI commands, API calls, scripts, data seeding) as part of E2E flows.
- **Schema**: `execute:` block (context-grouped, `run:` + `repeat:` + `expect:` per entry), `wait_after:` (post-execution delay), `on_fail: fail` (default)
- **Where**: 11 files — test-runner § 2n, flow-writer, flow-verifier, e2e-flow reference + SKILL.md, e2e-test SKILL.md, walkthrough reference, common-patterns, CLAUDE.md, compiler (resolver + migrate + codegen + coverage)
- **Compiler**: SKIP in CI (same as verify-external) — 470/470 tests pass
- **Impact scan gap found**: walkthrough serialization rule only mentioned Verify external — added Execute external serialization guidance
- **Key distinction**: `Execute external` = do things (default `on_fail: fail`); `Verify external` = check things (default `on_fail: warn`)

**Lesson**: When adding generation capability for a pattern that already exists on the execution side, check BOTH the generator AND all intermediate agents (verifier). The verifier sits between writer and runner — if it doesn't know about the new step type, it breaks the chain even though both endpoints are correct.

### 2026-03-16: v2.0 Role Restructuring — Validation

**Changes:**
- Added agents: e2e-flow-writer (codebase analysis → flow YAML), e2e-flow-verifier (adaptive browser validation)
- Added skill: /e2e-flow (generate + verify + smoke, replaces /e2e-acceptance)
- Removed: e2e-acceptance skill
- Modified: e2e-walkthrough (removed --smoke, --verify), e2e-dispatch (added --flow route)
- Updated: CLAUDE.md, README.md, docs/, plugin.json (v2.0.0), hooks

**Validation:** All 7 validation checks passed — zero stale references, all new files exist, cross-references correct.
**Reference cleanup:** Zero stale e2e-acceptance references in active files.

### 2026-03-14: PR Pre-Flight E2E Suggestion + External Verification Checkpoints

**Feature A — PR Pre-Flight E2E Suggestion**
- **What**: kc-create-pr Step 1.5 detects integration changes (frontend + backend in same diff) and suggests running e2e verification before PR creation
- **Where**: `kc-pr-flow/skills/kc-create-pr/SKILL.md` + `kc-pr-flow/reference/e2e-verification.md`
- **Cross-plugin**: kc-pr-flow → e2e-pipeline (soft dependency, degrades to skip)

**Feature B — External Verification Checkpoints**
- **What**: `action: "verify-external"` step type in flow YAML. Lets the LLM pause e2e execution to verify external services (PostHog, Langfuse, DB, Slack, any HTTP endpoint). Semi-structured `verify:` block with natural language `check:` / `expect:` / `note:` fields.
- **Where**: e2e-test SKILL.md (spec), e2e-test-runner agent (execution), e2e-walkthrough SKILL.md (--verify + checkpoint), common-patterns.md (examples)
- **Design source**: Natural version from `recce-cloud-infra/.claude/e2e/flows/support-escalation-with-verification.yaml` — adopted checkpoint-as-full-step pattern over field-on-browser-step

**Key design decisions**:
- Checkpoint is an independent step, not a field on browser steps
- `verify:` uses semi-structured YAML (service grouping + natural language), not pure NL strings
- `on_fail: warn` default — checkpoints don't block flow unless explicitly set to `fail` or `block`
- Config missing → SKIP with warning (flow works without external service setup)
- Walkthrough (main context) = full tool access for checkpoints; Test (subagent) = best-effort via Bash/curl

## Findings

### 2026-03-14: Impact scan gaps found and fixed

Post-implementation impact scan (Explore agent) found 7 gaps across 4 files:

| # | Gap | Severity | Fix |
|---|-----|----------|-----|
| 1 | e2e-test-runner § 2b action table missing `"Verify external"` | HIGH | Already added during implementation |
| 2 | Report template missing Checkpoint Results section | HIGH | Added to § 3c template |
| 3 | e2e-dispatch missing `--verify` routing + quick ref | HIGH | Added to --walk dispatch + quick reference |
| 4 | e2e-test SKILL.md missing execution model cross-link | MEDIUM | Added paragraph linking to test-runner § 2m |
| 5 | Flow schema exemption wording unclear | MEDIUM | Clarified: "no page/element refs, must have verify:" |
| 6 | Test-runner § 2m missing field reference | MEDIUM | Added field list (event, check, expect, properties, note) |
| 7 | Test-runner missing checkpoint critical rule | LOW | Added rule #13 about best-effort execution |

**Lesson**: Cross-skill features need explicit cross-links. The e2e-test SKILL.md defines the spec but the test-runner executes it — both must reference each other.

## New Features

### 2026-03-15: Observe-and-Continue — Walkthrough Noise Reduction + Enhanced Trace Correlation

**Problem**: e2e-walkthrough had lowest skill compliance among e2e skills. Root cause: 812 lines of instructions competing with ~1,050 lines of browser output in main context (45% noise). e2e-test and e2e-map don't have this problem because browser output is isolated in subagents.

**Solution**: Three-part design:
1. **Phase 3 observe-and-continue**: Replace per-step `console --json` + `errors --json` + health report with lightweight `errors --json` only + visual anomaly observation. Record anomalies + notify (don't stop). One-line per-step report. Context noise: ~1,050 → ~50 lines (-95%).
2. **step-log.json**: New artifact written at end of Phase 3 with step timestamps + anomaly records. Feeds enhanced trace analyzer for step-correlated analysis.
3. **Enhanced trace-analyzer**: New `step_log_path` input (optional, backward-compatible). Produces 3 new sections: Step-Correlated Issues, Anomaly × Trace Cross-Reference, Anomalies Without Trace Evidence. Detects silent failures (UI success + API error).

**Where**:
- `agents/e2e-trace-analyzer.md` — step_log_path input, Step 3.5 cross-reference logic, enhanced output template
- `skills/e2e-walkthrough/SKILL.md` — Phase 3 observe-and-continue summary, Phase 4 checklist (13 items), anomaly review step
- `skills/e2e-walkthrough/reference.md` — Per-step loop rewrite, anomaly observation rules, step-log.json spec, anomaly review procedure, enhanced trace dispatch

**Design spec**: `docs/plans/2026-03-15-observe-and-continue-design.md`

**Key design decisions**:
- `step_log_path` is optional — trace-analyzer without it produces identical output (zero regression for e2e-test)
- Only auth expiration pauses walkthrough — all other anomalies record + continue
- `console --json` removed from per-step loop — trace.zip has complete console with better coverage
- `snapshot -i` (interactive-only) replaces full `snapshot` as default
- Silent failure detection is conservative: requires BOTH positive UI indicator text + API error in same time window
- Common Mistakes split into "Top 5" + "gotchas" for better attention allocation under context pressure

**Backward compatibility**:
- e2e-test skill dispatch unchanged (no step_log_path → standard output)
- e2e-map skill unaffected
- e2e-dispatch routing unaffected
- common-patterns.md has no obsolete references

## Findings

### 2026-03-15: Impact scan for Observe-and-Continue

Post-implementation impact scan (Explore agent) found 2 items:

| # | Gap | Severity | Fix |
|---|-----|----------|-----|
| 1 | SKILL.md Phase 4 step 3 missing prerequisite guard for step-log.json | LOW | Added: "If missing, write it now before dispatching" |
| 2 | Anomaly detail length: reference.md says ≤100 chars, agent says ≤200 | VERY LOW | Acceptable variance — 100 is conservative limit, agent handles up to 200 |

**False positive**: Explorer reported "checklist step 3.5 missing" but step 4 in checklist IS "anomaly review presented" — renumbered from design doc's 3.5 to final checklist's 4.

**Lesson**: When adding optional input to a shared agent (trace-analyzer), Rule 9 ("additive, never breaking") is the critical safety net. Always verify the dispatch from ALL orchestrators that use the agent, not just the one being modified.

### 2026-03-15: REFACTOR round — combined pressure test findings

Writing-skills TDD REFACTOR with combined pressures (authority + exhaustion + sunk cost, bulk errors, mode transition, cascading failure + re-run) found 1 BREAK + 4 CRACKs:

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| 1 | Re-run/retry has zero step-log specification | BREAK | Added: `superseded_by` field, retry entry id scheme, trace-analyzer re-run awareness |
| 2 | Bulk errors (>5 from `errors --json`) no aggregation | CRACK | Added: aggregate recording (≤3 representative + summary), raw output to file |
| 3 | Smoke mode batch errors no step-log destination | CRACK | Added: record on last step with `source: "errors --json (batch)"` |
| 4 | Per-step loop has no late-stage integrity guarantee | CRACK | Added: "All 7 substeps mandatory for EVERY step" + context-critical escape |

**Deferred (not over-engineering for this iteration):**
- Anomaly observation vacuousness — cognitive check has inherent limits. Could add `observation_scope` field in future.
- Combined-pressure synthesis paragraph — defense is adequate from individual rules.

**Lesson**: Single-pressure tests pass easily. Combined pressures (authority + real error + late stage, OR bulk data + ambiguity + exhaustion) expose gaps that unit-style tests miss. Always run at least 2 combo scenarios in the REFACTOR phase.

### 2026-03-15: Evaluate — Walkthrough Phase 3 subagent feasibility

**Question**: Can e2e-walkthrough dispatch a subagent for agent-browser execution (like e2e-test / e2e-map do) to save main context?

**Verdict**: NOT recommended. Walkthrough's interactive nature is fundamentally incompatible with subagent isolation.

**Key factors**:
1. Observe-and-continue already reduced Phase 3 context noise by 95% (1,050 → ~50 lines). Remaining consumption (~120-330 lines for 10 steps) is necessary for @ref extraction + anomaly observation.
2. Six core features break under subagent: ad-hoc commands, step mode, external checkpoints (--verify), dynamic plan modification, debug pivot, Phase 4 anomaly review.
3. Alternative approaches evaluated and rejected: auto-mode-only subagent (rare use, dual-path maintenance cost), per-step dispatch (overhead > savings), batch dispatch (loses interactivity = becomes e2e-test).

**Architecture principle**: e2e-test/e2e-map are automated (zero human interaction during execution) → subagent. e2e-walkthrough is collaborative (human participates during execution) → main context. This is a category distinction, not a cost optimization target.

**Future alternatives if context pressure recurs**: Targeted snapshot compression (output only step-relevant @ref lines from `snapshot -i`), not subagent migration.

**Follow-up documentation**: Added "Verification Decision" table to `e2e-acceptance` SKILL.md (after Phase 4) and updated `e2e-pipeline` CLAUDE.md closed-loop diagram. Clarifies: draft flow exists → `/e2e-test`; no flow → `/e2e-walkthrough --verify` (produces flow for future `/e2e-test`).

### 2026-03-16: Recording startup — eliminate dual-context (orphan browser window)

**Problem**: `agent-browser open <url>` + `agent-browser record start <path>` created two browser contexts — `open` creates context #1, `record start` creates context #2 with recording. Agent operates on #2 while context #1 remains as a visible orphan window. Users reported confusion.

**Root cause**: `record start` uses Playwright's `recordVideo` which must be set at context creation time, so it always creates a new context. Documentation said "Start AFTER `open`", implying `open` must come first.

**Discovery**: Testing revealed `record start` can launch the daemon independently — `open` is not a prerequisite. When `record start` is called first and `open` called after, `open` navigates within the existing recording context instead of creating a new one.

**Fix**: Reverse the startup order for recording-enabled sessions:
- **Old**: `open <url>` → `record start` → `trace start` (two contexts, two windows)
- **New**: `record start` → `open <url>` → `trace start` (one context, one window)

**Verification**: Tested full flow — `record start` → `open --headed` → `snapshot -i` → `trace start` → `record stop` → `trace stop`. Video output: 1280×720 VP8, same quality as old flow. Single browser window confirmed.

**Files changed**: `agents/e2e-test-runner.md` (§ 1b-1f), `skills/e2e-walkthrough/reference.md` (Startup), `references/commands.md` (Recording rules).

**Also investigated (rejected)**: Using trace screencast frames for video. Trace captures at 800×450 / ~1fps (event-driven) — too low quality for PR reviews. `record start` remains the correct approach for video.

### 2026-07-12: Compiler negative assertions masked browser failures

**Problem**: Generated `element-not-visible` assertions collapsed unavailable browser evidence into an ordinary timeout, while `text-not-visible` could treat a failed snapshot as confirmed absence and pass.

**Root cause**: `|| true` erased the command-status channel before the assertion interpreted stdout. This is unsafe for negative assertions because empty output can look like evidence that the target is absent.

**Fix**:
- `_poll_not_visible` succeeds only on literal `false`, times out with status 1 for literal `true`, and returns status 2 for command or protocol failure.
- Generated callers map status 2 to a visibility-probe infrastructure message while retaining the ordinary timeout message for status 1.
- Text assertions use a session-aware snapshot helper and route snapshot failure through `_handle_failure` before grep evaluation.
- Continue-on-error failure accumulation deduplicates repeated expectation failures by step ID without collapsing failures from different steps.
- The dedup loop checks array length before expanding an empty array, avoiding Bash 3.2 `set -u` failure and EXIT-trap status masking.
- Added runtime tests forced through `/bin/bash` when available, with a fake `agent-browser` for command failure, invalid output, session routing, cleanup exit status, and successful positive/negative assertions.

**Verification**: `node --test compiler/test/*.test.js` -> 511/511 PASS. `npm run lint` -> exit 0 with warnings and no errors.

**Impact scan**: Reviewed e2e-test, e2e-map, e2e-walkthrough, e2e-flow, their references, all browser agents, and shared command/common-pattern references. No action grammar or agent execution contract changed, so no skill or agent edits were required. This plugin repo has no project mapping fixtures in the impact-matrix locations; compiler fixtures cover the behavior instead.
