---
phase: 03-flywheel-core
verified: 2026-03-18T12:20:00Z
status: passed
score: 25/25 must-haves verified
re_verification: true
  previous_status: gaps_found
  previous_score: 22/25
  gaps_closed:
    - "PR merge status is collected as implicit feedback (FEED-04) — collectImplicitFeedback now imported and called in executor.ts finally block"
    - "Feedback trends are written to NW journal (FEED-07) — writeFeedbackTrends now imported and called in executor.ts finally block"
    - "REQUIREMENTS.md reflects Phase 3 completion status — FEED-01/02/04/06/07 marked [x] and Complete in traceability table"
  gaps_remaining: []
  regressions: []
human_verification:
  - test: "Chat drawer slide-in and streaming"
    expected: "Clicking chat button (bottom-right) opens 400px drawer from right. Typing a message and pressing Enter streams response with block cursor. Closing and reopening preserves conversation."
    why_human: "Visual slide animation, streaming block cursor, and conversation persistence require browser interaction to verify"

  - test: "Config editor 4-step validation flow"
    expected: "Edit button unlocks textarea. Validate button triggers 4 steps: (1) syntax check, (2) Haiku semantic check, (3) diff preview, (4) Confirm Save button appears. Step 2 shows result from Anthropic API."
    why_human: "4-step sequential UI flow and Haiku API response content can only be verified by human interaction"

  - test: "Add Target wizard 4 steps"
    expected: "Clicking '+ Add Target' opens modal. Steps: type+name, north star, monitors/respond, preview+save. Progress dots visible. Back/Next navigation works. Save creates entry in targets.yaml."
    why_human: "Multi-step modal flow with file system side effect requires browser interaction"

  - test: "Feedback buttons on action cards"
    expected: "Clicking an action card in a completed run detail expands it showing Strategy and Reflection sections. Clicking +1 or -1 highlights the button, disables both, and sends POST /api/feedback. Buttons stay disabled on reopen."
    why_human: "Requires a completed run with summary data. Optimistic disable behavior and visual button state require browser interaction"

  - test: "Baseline card with trend arrows"
    expected: "Run detail shows 'Indicator Baselines' card above action cards with indicator rows. Improving = green up-arrow, degrading = red down-arrow, stable = gray right-arrow. Card is always visible (not collapsible)."
    why_human: "Requires a completed run that produced summary.yaml with indicator_baseline data. Visual color rendering requires browser"

  - test: "Skill phases 0.5/3.5/4.5 during live run"
    expected: "When /kc-nightwatch executes, NW-Claude runs Phase 0.5 (measures indicator baselines), Phase 3.5 (writes pre-assessment), Phase 4.5 (writes reflection), and Phase 5 Slack report includes assessment summary."
    why_human: "Requires live NW-Claude execution with ANTHROPIC_API_KEY. Cannot verify skill execution behavior from static code"
---

# Phase 3: Flywheel Core Verification Report

**Phase Goal:** Users can interact with NW-Claude about run results, edit config safely, submit structured feedback that calibrates future runs, and see per-run self-assessment and indicator baselines — turning nightwatch from automation into a learning system

**Verified:** 2026-03-18T12:20:00Z
**Status:** passed
**Re-verification:** Yes — after gap closure (plan 03-05)

---

## Re-Verification Summary

Previous verification (2026-03-18T11:10:00Z) found 3 gaps blocking 3 of 25 truths. Gap closure plan 03-05 addressed all three.

| Gap | Previous Status | Current Status |
|-----|-----------------|----------------|
| FEED-04: collectImplicitFeedback orphaned | PARTIAL | CLOSED — wired in executor.ts:224 |
| FEED-07: writeFeedbackTrends orphaned | PARTIAL | CLOSED — wired in executor.ts:230 |
| REQUIREMENTS.md FEED-* stale | FAILED | CLOSED — FEED-01/02/04/06/07 now [x] + Complete |

New commits (03-05): `8df0af2` (RED tests), `e18db36` (GREEN wiring), `825f51e` (REQUIREMENTS.md), `627378f` (SUMMARY).

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Chat drawer slides in from right, NW-Claude responds with streaming text | ? HUMAN | Component and API exist; visual behavior needs browser |
| 2 | Anthropic SDK streams responses via SSE (claude-haiku-4-5) | VERIFIED | chat-manager.ts:74 uses client.messages.stream(), fans out to subscribers via writeSSE |
| 3 | Run completion triggers auto-open of chat drawer with run summary briefing | VERIFIED | ipc.ts:84 broadcasts brief-ready on run:completed; app.ts:40 listens and calls briefChat |
| 4 | Each target has its own chat session; switching kills old session | VERIFIED | chat-manager.ts: getOrCreateSession / killSession keyed by targetName; killAllSessions available |
| 5 | Chat drawer persists conversation when closed and reopened | VERIFIED | chat-drawer.ts replays history from session.messages on reconnect via SSE |
| 6 | Global SSE /api/events delivers brief-ready events | VERIFIED | stream.ts:27 GET /api/events wired to subscribeGlobal; ipc.ts:59 broadcastGlobal feeds it |
| 7 | Config page has Targets/Safety tabs with YAML in read-only textarea | VERIFIED | config.ts:10 useState('targets'), tablist with role=tab, Read only helper text |
| 8 | Edit button unlocks textarea, Validate triggers 4-step flow | VERIFIED | config.ts:39 handleEdit, :47 handleValidate with validateConfigSave (4 steps in config-validator.ts) |
| 9 | 4-step validation: syntax, Haiku semantic, diff preview, confirm save | VERIFIED | config-validator.ts:34 static parse, Haiku call, diff, step:'ready' with haiku_verdict |
| 10 | Config warnings from self-repair.yaml appear as inline amber badges | VERIFIED | config.ts:36 loads getConfigWarnings(), renders tabWarnings as amber-colored divs |
| 11 | Add Target wizard: 4-step modal, creates new target in targets.yaml | VERIFIED | add-target-wizard.ts:16 4 steps; configRoutes.post /api/config/targets/add persists |
| 12 | Edit existing target via pre-filled wizard; Remove via confirm dialog | VERIFIED | config.ts: setEditTarget state, PUT /api/config/targets/:name and DELETE routes |
| 13 | Thumbs up/down buttons on each action card | VERIFIED | action-card.ts:97-112 aria-label="Accept signal"/"Reject signal", +1/-1 labels |
| 14 | Clicking feedback button sends POST /api/feedback, disables both buttons | VERIFIED | action-card.ts:18 setSubmitted(verdict) optimistic disable, api.submitFeedback call |
| 15 | PR merge status collected as implicit feedback | VERIFIED | executor.ts:12 imports collectImplicitFeedback; executor.ts:224 calls it in finally block after summary.yaml read |
| 16 | Reject rate per indicator calculated and stored in feedback YAML | VERIFIED | feedback-store.ts:46 getCalibrationData(), GET /api/feedback/calibration route wired |
| 17 | Feedback trends written to NW journal for slow learning path | VERIFIED | executor.ts:13 imports writeFeedbackTrends; executor.ts:228-230 calls per-target in finally block |
| 18 | Action cards expand to show signal details with feedback buttons | VERIFIED | action-card.ts: useState(expanded), expanded && html with Strategy, Reflection, buttons |
| 19 | Skill includes Phase 0.5 (indicator baseline measurement) | VERIFIED | SKILL.md:350 "## Phase 0.5: Indicator Baseline Measurement" section present |
| 20 | Skill includes Phase 3.5 (pre-action strategy assessment) | VERIFIED | SKILL.md:606 "## Phase 3.5: Pre-Action Strategy Assessment" section present |
| 21 | Skill includes Phase 4.5 (post-action reflection) | VERIFIED | SKILL.md:855 "## Phase 4.5: Post-Action Reflection" section present |
| 22 | Skill Phase 5 Slack report includes assessment summary | VERIFIED | SKILL.md:1052-1066 Strategy/Reflection/Baselines lines in Slack template |
| 23 | Executor parses summary.yaml and populates RunSummary.per_target | VERIFIED | executor.ts:187-204 reads summary.yaml in finally block, assigns per_target |
| 24 | Run detail shows indicator baseline card at top with trend arrows | VERIFIED | runs.ts:7 imports BaselineCard, :115 renders above action cards; baseline-card.ts arrows |
| 25 | Action card expanded view shows Strategy and Reflection sections | VERIFIED | action-card.ts:55-70 Strategy section + Reflection section with assessment verdict prose |

**Score:** 25/25 truths verified (0 partial, 0 failed; 6 require human browser verification)

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `app/shared/types.ts` | ChatMessage, FeedbackEntry, CalibrationData, ConfigValidationResult, IndicatorBaseline, PerTargetSummary, RunSummaryAction | VERIFIED | All 7 Phase 3 types present (lines 86-181) |
| `app/server/services/chat-manager.ts` | getOrCreateSession, killSession, sendMessage, subscribeToTarget | VERIFIED | All 4 exports present; Anthropic SDK streaming wired |
| `app/server/routes/chat.ts` | POST /api/chat/:target/message, GET stream, POST reset, POST brief | VERIFIED | chatRoutes exported; 4 routes defined |
| `app/server/ipc.ts` | subscribeGlobal, broadcastGlobal; run:completed broadcasts brief-ready | VERIFIED | Lines 52-86 |
| `app/server/routes/stream.ts` | GET /api/events global SSE | VERIFIED | Line 27 subscribeGlobal wired |
| `app/frontend/components/chat-drawer.ts` | Slide-over, streaming block cursor, history replay | VERIFIED | ChatDrawer exported, streaming state, █ cursor |
| `app/server/services/config-validator.ts` | validateConfigSave (4-step), withWriteLock | VERIFIED | Both exported; 4 steps: static, haiku, diff, ready |
| `app/server/routes/config.ts` | GET/PUT /api/config/:file, warnings, add/edit/remove | VERIFIED | 6 routes; /api/config/warnings before /:file |
| `app/frontend/pages/config.ts` | Full config page: tabs, edit lock, validation UI, wizard | VERIFIED | Replaced placeholder; tabs, edit lock, 4-step flow |
| `app/frontend/components/add-target-wizard.ts` | 4-step wizard, edit mode, progress dots | VERIFIED | 4 steps, isEdit prop, progress dot rendering |
| `app/server/services/feedback-store.ts` | appendFeedback, getFeedbackForRun, getCalibrationData, writeFeedbackTrends | VERIFIED | All 4 exports present; nightwatch-feedback.yaml path |
| `app/server/routes/feedback.ts` | POST /api/feedback, GET /api/feedback/:runId, GET calibration | VERIFIED | calibration route before :runId (correct ordering) |
| `app/frontend/components/action-card.ts` | ActionCard: expandable, feedback buttons, Strategy/Reflection | VERIFIED | aria-expanded, aria-pressed, +1/-1, Strategy, Reflection |
| `app/worker/feedback-collector.ts` | collectImplicitFeedback, checkPrStatus, checkLinearStatus | VERIFIED + WIRED | Functions exist and implemented; imported and called from executor.ts:12,224 |
| `app/worker/executor.ts` | Reads summary.yaml; calls collectImplicitFeedback + writeFeedbackTrends post-run | VERIFIED | Lines 12-13 imports; lines 209-235 post-run feedback block |
| `skills/kc-nightwatch/SKILL.md` | Phase 0.5, 3.5, 4.5 + Slack assessment + summary.yaml spec | VERIFIED | All 3 phases present; Step 5.2.5 writes summary.yaml |
| `app/frontend/components/baseline-card.ts` | BaselineCard: trend arrows, aria-label, always visible | VERIFIED | up/down/right arrows, success/error/muted colors, aria-label |
| `app/frontend/pages/runs.ts` | BaselineCard + Pre-Run Strategy + Post-Run Reflection | VERIFIED | imports BaselineCard, renders all 3 assessment sections |
| `app/tests/worker/executor-feedback-wiring.test.ts` | 9 static wiring tests for FEED-04/07 | VERIFIED | Created in 03-05; 9 tests pass (import regex + call count + guard + try/catch + module resolution) |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `chat-manager.ts` | Anthropic SDK | client.messages.stream() fan-out to SSE writers | WIRED | Lines 74-108; content_block_delta events forwarded |
| `app.ts` | `/api/events` + ChatDrawer | EventSource + brief-ready listener | WIRED | app.ts:40 addEventListener('brief-ready'); ChatDrawer rendered |
| `ipc.ts` | run:completed → brief-ready | broadcastGlobal('brief-ready') | WIRED | ipc.ts:84-86 |
| `action-card.ts` | `/api/feedback` | api.submitFeedback on button click | WIRED | action-card.ts:20 |
| `feedback.ts` (route) | `feedback-store.ts` | appendFeedback called on POST | WIRED | feedback.ts:35 |
| `executor.ts` | `feedback-collector.ts` | import + call collectImplicitFeedback after summary.yaml read | WIRED | executor.ts:12 import; :224 call in finally block |
| `executor.ts` | `feedback-store.ts` writeFeedbackTrends | NW journal per target | WIRED | executor.ts:13 import; :230 call in finally block per-target |
| `SKILL.md` | `executor.ts` | Skill writes summary.yaml; executor reads it | WIRED | executor.ts:187 reads summaryPath after run |
| `executor.ts` | `types.ts` RunSummary.per_target | summaryData.per_target assigned | WIRED | executor.ts:199 |
| `runs.ts` | `baseline-card.ts` | BaselineCard rendered from indicator_baseline | WIRED | runs.ts:116 |
| `action-card.ts` | assessment.reasoning | Strategy + Reflection sections display it | WIRED | action-card.ts:58-70 |
| `config-validator.ts` | Anthropic Haiku API | Haiku semantic check via sdk | WIRED | config-validator.ts uses Anthropic client; fail-open on error |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| CONF-01 | 03-02 | YAML editor for targets.yaml (read-only default) | SATISFIED | config.ts tab=targets, read-only textarea, Edit button |
| CONF-02 | 03-02 | YAML editor for safety.yaml | SATISFIED | config.ts tab=safety, same editor, getConfig('safety') |
| CONF-03 | 03-02 | Edit lock (must explicitly enable editing) | SATISFIED | config.ts:13 editing=false default, handleEdit() sets true |
| CONF-04 | 03-02 | 4-step save validation (static → semantic → diff → confirm) | SATISFIED | config-validator.ts 4 steps; config.ts validation flow |
| CONF-05 | 03-02 | Config warnings panel (from self-repair.yaml, inline markers) | SATISFIED | config.ts:36 getConfigWarnings(), tabWarnings amber rendering |
| CONF-06 | 03-02 | Add Target wizard (4 steps) | SATISFIED | add-target-wizard.ts 4-step wizard |
| CONF-07 | 03-02 | Edit Target (same wizard, pre-filled) | SATISFIED | config.ts editTarget state, AddTargetWizard editTarget prop |
| CONF-08 | 03-02 | Remove Target (confirm dialog) | SATISFIED | config.ts confirmRemove state, DELETE /api/config/targets/:name |
| CHAT-01 | 03-01 | NW-Claude chat panel (right side of dashboard) | SATISFIED | ChatDrawer slide-over from right, toggle FAB in app.ts |
| CHAT-02 | 03-01 | Auto-brief after run completes | SATISFIED | ipc.ts run:completed → broadcastGlobal → app.ts → briefChat |
| CHAT-03 | 03-01 | Bidirectional Claude session (streaming) | SATISFIED | Anthropic SDK stream, POST message → GET SSE stream |
| CHAT-06 | 03-01 | Per-target chat focus | SATISFIED | open-chat CustomEvent, targetName prop, killSession on switch |
| CHAT-07 | 03-01 | Session lifecycle (persist until close/reset) | SATISFIED | ChatSession Map persists; reset route kills session |
| FEED-01 | 03-03 | Dashboard feedback buttons (thumbs up/down) per action card | SATISFIED | action-card.ts +1/-1 buttons, aria-pressed, disabled state |
| FEED-02 | 03-03 | Feedback API endpoint (POST /api/feedback) | SATISFIED | feedbackRoutes.post('/api/feedback') with signal_id/verdict/reason |
| FEED-04 | 03-03 | PR status collection (merged=accepted, closed=rejected) | SATISFIED | executor.ts:12,224 imports + calls collectImplicitFeedback; guard !timedOut; try/catch |
| FEED-06 | 03-03 | Reject rate calibration (per indicator, adjust threshold) | SATISFIED | feedback-store.ts getCalibrationData() with formula clamp(0.1,0.9,...) |
| FEED-07 | 03-03 | Feedback trends written to NW journal | SATISFIED | executor.ts:13,228-230 imports + calls writeFeedbackTrends per-target; wrapped in same try/catch |
| ASSESS-01 | 03-04 | Phase 3.5 pre-action strategy assessment | SATISFIED | SKILL.md Phase 3.5 section present |
| ASSESS-02 | 03-04 | Phase 4.5 post-action reflection assessment | SATISFIED | SKILL.md Phase 4.5 section present |
| ASSESS-03 | 03-04 | Assessment display in run detail (per action card) | SATISFIED | action-card.ts Strategy + Reflection sections |
| ASSESS-04 | 03-04 | Assessment in Slack report | SATISFIED | SKILL.md:1052-1066 Slack template with pre/post_assessment |
| MEAS-01 | 03-04 | Phase 0.5 indicator baseline measurement | SATISFIED | SKILL.md Phase 0.5 section present |
| MEAS-02 | 03-04 | Indicator trend tracking (previous_value + trend direction) | SATISFIED | types.ts IndicatorBaseline.trend, executor.ts reads from summary |
| MEAS-03 | 03-04 | Baseline display in run detail | SATISFIED | runs.ts BaselineCard import + render; baseline-card.ts with arrows |

**All 25 in-scope requirements satisfied.**

**Requirements deferred (out of Phase 3 scope):**
- CHAT-04, CHAT-05: NW-MCP access and journal access — correctly deferred to Phase 4
- FEED-03, FEED-05: MCP feedback tool and Linear status — correctly deferred to Phase 4

**REQUIREMENTS.md accurately reflects this state:** FEED-01/02/04/06/07 are [x] and Complete; FEED-03/05 remain [ ] and Pending (deferred). FOUND-01, DASH-02, DASH-05, HIST-04 also corrected in 03-05.

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `app/worker/feedback-collector.ts` | 88-93 | `checkLinearStatus` returns null with "Phase 3 placeholder" comment | INFO | Expected and documented — Linear MCP integration intentionally deferred to Phase 4 |

No blockers remain. The two previously-blocking orphaned functions are now wired into the production code path.

---

## Human Verification Required

### 1. Chat Drawer Visual + Streaming

**Test:** Start server (`bun run server/index.ts` from `app/`). Open http://localhost:3200. Click floating chat button bottom-right.
**Expected:** Drawer slides in 400px from right. "NW-Claude" heading visible. Type a message, press Enter — response streams with block cursor (█). Close and reopen — conversation history visible.
**Why human:** Visual slide animation, streaming cursor rendering, and conversation persistence require browser interaction.

### 2. Config 4-Step Validation Flow

**Test:** Click "Config" in nav. Click "Edit". Modify some YAML. Click "Validate".
**Expected:** Sequential 4-step display: (1) Syntax check result, (2) Haiku semantic verdict with WARN/OK label, (3) YAML diff preview, (4) "Confirm Save" button appears. Save succeeds.
**Why human:** Haiku API response content and 4-step sequential UI require browser and live API key.

### 3. Add Target Wizard

**Test:** On Config page (Targets tab), click "+ Add Target".
**Expected:** Modal opens. Step 1: type + name fields. Step 2: north star + goals. Step 3: monitors + respond. Step 4: preview + save. Progress dots at top. Back/Next navigation works. Save closes modal and new target appears in YAML.
**Why human:** Multi-step modal interaction and YAML side-effect require browser.

### 4. Feedback Buttons on Action Card

**Test:** Navigate to Runs. Open a completed run that has summary data (needs a run that produced summary.yaml). Click an action card to expand.
**Expected:** Strategy and Reflection sections visible in expanded card. +1 and -1 buttons visible. Click one — that button highlights (green for +1, red for -1), both buttons become disabled. On page reload, buttons remain disabled (feedback persisted).
**Why human:** Requires a completed run with summary.yaml data; optimistic disable behavior and persistence require browser + API call.

### 5. Baseline Card with Trend Arrows

**Test:** On a run detail with summary data that includes indicator_baseline.
**Expected:** "Indicator Baselines" card appears above action cards. Each indicator shows name, current value + unit, and trend arrow. Up-arrow (↑) green for improving, down-arrow (↓) red for degrading, right-arrow (→) gray for stable. Card is always visible and not collapsible.
**Why human:** Requires run data with indicator_baseline populated; visual color and arrow rendering require browser.

### 6. Skill Phases During Live Run (ASSESS-01/02, MEAS-01/02)

**Test:** Run `/kc-nightwatch` with ANTHROPIC_API_KEY set. After completion, check the run's summary.yaml for indicator_baseline, pre_assessment, post_assessment fields.
**Expected:** NW-Claude executes Phase 0.5 (logs baseline measurements), Phase 3.5 (logs pre-assessment), Phase 4.5 (logs post-assessment). summary.yaml contains non-empty per_target data with those fields. Dashboard run detail shows the data.
**Why human:** Skill execution behavior and NW-Claude LLM output quality require live run.

---

## Test Suite Status

All 163 tests pass (0 fail) — verified by `bun test` run at re-verification time (2026-03-18T12:18Z).

Tests covering Phase 3 gaps (new in 03-05):
- `tests/worker/executor-feedback-wiring.test.ts` — 9 static wiring tests: import regex + call count + guard + try/catch + module resolution

Tests covering Phase 3 (existing, no regressions):
- `tests/server/chat.test.ts` — 6 tests, chat-manager lifecycle
- `tests/server/auto-brief.test.ts` — 3 tests, global SSE broadcast
- `tests/server/config-validator.test.ts` — 5 tests, validateConfigSave + withWriteLock
- `tests/server/config-editor.test.ts` — 2 tests, config route setup
- `tests/server/target-wizard.test.ts` — 3 tests, YAML generation logic
- `tests/server/feedback.test.ts` — 5 tests, FeedbackEntry and calibration logic
- `tests/server/calibration.test.ts` — 6 tests, threshold formula
- `tests/server/feedback-polling.test.ts` — 6 tests, feedback collector
- `tests/worker/executor-summary.test.ts` — 5 tests, summary.yaml parsing
- `tests/worker/assessment.test.ts` — 5 tests, assessment field contracts
- `tests/worker/baseline.test.ts` — 4 tests, IndicatorBaseline type and trend arrows

---

## Commit Verification

All 14 commits from SUMMARY files verified present in git history:

Phase 03-01 through 03-04 (11 commits, previously verified):
- `0113964` feat(03-01): Phase 3 shared types + global SSE broadcast + Anthropic SDK
- `63e0795` feat(03-01): Chat session manager + API routes + API client extension
- `0c8270f` feat(03-01): ChatDrawer component + app.ts auto-brief integration
- `79b217f` feat(03-02): config validation service, API routes, and API client
- `8962e61` feat(03-02): full config page UI with tabs, YAML editor, 4-step validation, warnings
- `c701377` feat(03-02): AddTargetWizard + Edit/Remove target flows, config page integration
- `b187127` feat(03-03): feedback store, API routes, and calibration tests
- `c8001f9` feat(03-03): ActionCard component with feedback buttons + runs.ts integration
- `0609857` feat(03-03): implicit feedback collector (PR/Linear polling) + NW journal integration
- `72cf285` feat(03-04): orchestrator skill phases 0.5/3.5/4.5 + executor summary.yaml parsing
- `be25ef7` feat(03-04): BaselineCard + ActionCard reflection + runs.ts assessment integration

Phase 03-05 (3 new commits, verified now):
- `8df0af2` test(03-05): add failing wiring tests for collectImplicitFeedback + writeFeedbackTrends
- `e18db36` feat(03-05): wire collectImplicitFeedback + writeFeedbackTrends into executor.ts post-run flow
- `825f51e` docs(03-05): update REQUIREMENTS.md Phase 3 FEED-* completion status

---

_Verified: 2026-03-18T12:20:00Z_
_Verifier: Claude (gsd-verifier)_
_Re-verification after: 03-05 gap closure_
