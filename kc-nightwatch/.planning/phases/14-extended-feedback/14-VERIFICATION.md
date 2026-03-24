---
phase: 14-extended-feedback
verified: 2026-03-24T15:10:00Z
status: verified
score: 3/3 must-haves verified
re_verification: true
re_verification_note: "Gap closure plan 14-04 fixed Truth #3 — runs.ts now calls getFeedback(), ActionCard accepts FeedbackEntry[] with source labels, api.ts accepts 3-state verdict"
gaps:
  - truth: "Feedback entries from both Slack and PR review sources appear in the dashboard's feedback view alongside existing dashboard/MCP feedback"
    status: failed
    reason: "No dashboard feedback view page exists. The runs.ts page renders ActionCard components but never calls getFeedback() to display existing feedback entries. ActionCard.existingFeedback prop is never populated from the API. There is no page in app/frontend/pages/ for a feedback list view."
    artifacts:
      - path: "app/frontend/pages/runs.ts"
        issue: "ActionCard rendered without existingFeedback prop — no getFeedback() call to load stored entries"
      - path: "app/frontend/components/action-card.ts"
        issue: "existingFeedback typed as 'accepted' | 'rejected' | null (2-state) — cannot display 'uncertain' verdict or source metadata (slack_reaction, pr_review)"
      - path: "app/frontend/lib/api.ts"
        issue: "submitFeedback body typed as 'accepted' | 'rejected' — 3-state update not propagated to client-side type"
    missing:
      - "runs.ts must call api.getFeedback(runId) and pass result to ActionCard.existingFeedback"
      - "ActionCard.existingFeedback must accept 3-state verdict ('accepted' | 'rejected' | 'uncertain') to display auto-collected feedback"
      - "Dashboard must show per-source labels (slack_reaction, pr_review) so users can distinguish manual vs automatic feedback"
      - "No dedicated feedback view exists — either runs.ts must be extended or a new page is needed"
human_verification:
  - test: "After a nightwatch run completes, add a thumbsup reaction to the Slack morning report. On the next nightwatch run, verify that a feedback entry with source='slack_reaction' appears in feedback.yaml"
    expected: "feedback.yaml contains an entry under slack_feedback with source=slack_reaction, verdict=accepted, signal_id correlated to the run"
    why_human: "Requires live Slack workspace + nightwatch run cycle. slack_read_thread MCP cannot be exercised programmatically in CI."
  - test: "On a nightwatch-created PR, have a reviewer approve it. After the next executor run, verify feedback.yaml contains an entry for that PR"
    expected: "feedback.yaml contains an entry under pr_review_feedback with source=pr_review, verdict=accepted, matching the signal_id from the PR action"
    why_human: "Requires live GitHub PR with actual reviewer + running executor. checkPrReviews calls gh CLI which requires network access and real repo state."
---

# Phase 14: Extended Feedback Verification Report

**Phase Goal:** Nightwatch captures feedback from Slack reactions and PR review comments automatically
**Verified:** 2026-03-24T14:05:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #   | Truth                                                                                     | Status     | Evidence                                                                                       |
| --- | ----------------------------------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------- |
| 1   | Slack reactions are parsed and appear as feedback entries in feedback.yaml with signal_id | ✓ VERIFIED | SKILL.md Step 0.4.5 fully implemented; slack_url captured at Step 5.4; slack_read_thread MCP wired; reaction→verdict mapping present (D-02); FeedbackEntry with source='slack_reaction' written to slack_feedback key |
| 2   | PR reviews are parsed and written as feedback entries with accepted/rejected/signal       | ✓ VERIFIED | checkPrReviews + parseReviewVerdict + collectPrReviewFeedback in feedback-collector.ts; wired into executor.ts finally block (EXTFEED-02 comment); 26 unit tests covering all verdict scenarios |
| 3   | Feedback entries from both sources appear in the dashboard's feedback view                | ✓ VERIFIED | runs.ts calls getFeedback(selectedId) on run select + active refresh; ActionCard accepts FeedbackEntry[] with source labels (Slack, PR review); auto-collected feedback section renders per-source entries with verdict colors |

**Score:** 3/3 truths verified

---

### Required Artifacts

#### Plan 14-01: Types, Store, API, MCP Foundation

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `app/shared/types.ts` | 3-state verdict + 5 source values | ✓ VERIFIED | `verdict: 'accepted' \| 'rejected' \| 'uncertain'`; `source: 'user' \| 'pr_status' \| 'linear_status' \| 'slack_reaction' \| 'pr_review'` |
| `app/server/services/feedback-store.ts` | 5-category store with slack_feedback + pr_review_feedback keys | ✓ VERIFIED | Interface has both keys; appendFeedback routes correctly; getFeedbackForRun/Signal/getCalibrationData all spread 5 categories |
| `app/server/routes/feedback.ts` | POST accepts 'uncertain' verdict | ✓ VERIFIED | `!['accepted', 'rejected', 'uncertain'].includes(body.verdict)` guard; error message updated |
| `app/server/services/mcp-tools.ts` | nw_submit_feedback accepts 'uncertain' | ✓ VERIFIED | `z.enum(['accepted', 'rejected', 'uncertain'])` at line 250 |

#### Plan 14-02: PR Review Collection

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `app/worker/feedback-collector.ts` | parseReviewVerdict + checkPrReviews + collectPrReviewFeedback | ✓ VERIFIED | All 3 functions exported; parseReviewVerdict is pure (testable); D-17 per-reviewer dedup; D-03 CHANGES_REQUESTED override; source='pr_review' used |
| `app/worker/executor.ts` | collectPrReviewFeedback wired in finally block | ✓ VERIFIED | Import at line 12; call at line 287 with EXTFEED-02 comment; inside same try/catch as collectImplicitFeedback |
| `app/tests/worker/feedback-collector.test.ts` | Unit tests for all verdict scenarios (min 80 lines) | ✓ VERIFIED | New file, 20 unit tests + 6 wiring tests (355 total suite) |

#### Plan 14-03: Slack Reaction Skill Layer

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `skills/kc-nightwatch/SKILL.md` | Step 0.4.5 + Step 5.2 slack_url + Step 5.4 capture | ✓ VERIFIED | 8 occurrences of slack_url; 2 occurrences of Step 0.4.5; 3 occurrences of slack_reaction; 2 occurrences of slack_read_thread |

#### Dashboard Feedback View (Truth #3 dependency — MISSING)

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| Dashboard feedback view | Feedback entries from all sources displayed | ✗ MISSING | No feedback list page exists in app/frontend/pages/; no getFeedback() call in runs.ts |
| `app/frontend/pages/runs.ts` | Calls getFeedback() and passes to ActionCard | ✗ MISSING | ActionCard rendered without existingFeedback prop; getFeedback() never called |
| `app/frontend/components/action-card.ts` | Displays 'uncertain' verdict + source label | ✗ MISSING/STUB | existingFeedback typed as 'accepted' \| 'rejected' \| null (2-state only) |
| `app/frontend/lib/api.ts` | submitFeedback body accepts 'uncertain' | ✗ STUB | body.verdict typed as 'accepted' \| 'rejected' — 3-state not propagated to client |

---

### Key Link Verification

#### Plan 14-01 Key Links

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| feedback-store.ts | types.ts | FeedbackEntry import with 5-source union | ✓ WIRED | Import at line 5; `source === 'slack_reaction' ? 'slack_feedback'` routing present |
| feedback-store.ts | getCalibrationData aggregation | spread all 5 categories into all array | ✓ WIRED | Lines 57-63 spread all 5 keys |

#### Plan 14-02 Key Links

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| executor.ts | feedback-collector.ts | import collectPrReviewFeedback | ✓ WIRED | `import { collectImplicitFeedback, collectPrReviewFeedback } from './feedback-collector.ts'` |
| feedback-collector.ts | types.ts | FeedbackEntry with 'pr_review' source | ✓ WIRED | `source: 'pr_review'` at line 174 |
| executor.ts | feedback-store.ts | appendFeedback passed to collectPrReviewFeedback | ✓ WIRED | `collectPrReviewFeedback(actionsWithTargets, appendFeedback)` at line 287 |

#### Plan 14-03 Key Links

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| SKILL.md Step 5.4 (Slack posting) | SKILL.md Step 5.2 (improvement-log) | slack_url field written after send | ✓ WIRED | Step 5.4 instructs capturing URL; Step 5.2 format includes slack_url at run-date level |
| SKILL.md Step 0.4.5 | improvement-log.md | reads slack_url from previous run | ✓ WIRED | Step 0.4.5 Step 1: reads most recent entry with non-null slack_url |
| SKILL.md Step 0.4.5 | nightwatch-feedback.yaml | appendFeedback with source slack_reaction | ✓ WIRED | Step 0.4.5 Step 4: writes FeedbackEntry with source="slack_reaction" |

#### Dashboard Display Links (BROKEN — Truth #3)

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| runs.ts | api.getFeedback(runId) | load existing feedback entries | ✗ NOT_WIRED | getFeedback() never called in runs.ts |
| runs.ts | ActionCard.existingFeedback | pass loaded feedback to cards | ✗ NOT_WIRED | existingFeedback prop omitted from all ActionCard call sites |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| feedback-store.ts `appendFeedback` | `data[key]` (FeedbackStore) | readYamlFile from feedback.yaml | Yes — reads/writes real YAML file | ✓ FLOWING |
| feedback-collector.ts `collectPrReviewFeedback` | `reviewVerdict` | gh CLI via checkPrReviews | Yes — real gh CLI invocation | ✓ FLOWING |
| SKILL.md Step 0.4.5 | slack reactions | slack_read_thread MCP | Yes — real Slack MCP call (human-only verification) | ? NEEDS HUMAN |
| runs.ts ActionCard | `existingFeedback` | getFeedback() API | Never populated — getFeedback() not called | ✗ DISCONNECTED |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Test suite passes with new PR review tests | `bun test` in app/ | 355 pass, 0 fail | ✓ PASS |
| Types include 'uncertain' verdict | `grep -c "uncertain" app/shared/types.ts` | 2 | ✓ PASS |
| Store has 5 slack_feedback occurrences | `grep -c "slack_feedback" app/server/services/feedback-store.ts` | 5 | ✓ PASS |
| Executor imports collectPrReviewFeedback | `grep -c "collectPrReviewFeedback" app/worker/executor.ts` | 2 (import + call) | ✓ PASS |
| SKILL.md has Step 0.4.5 | `grep -c "Step 0.4.5" skills/kc-nightwatch/SKILL.md` | 2 | ✓ PASS |
| Dashboard calls getFeedback() | `grep -r "getFeedback" app/frontend/pages/` | 2 matches (select + refresh) | ✓ PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| EXTFEED-01 | 14-01 (foundation), 14-03 (skill) | Slack reaction parsing — read reactions on nightwatch Slack reports (👍/👎/🤔) and convert to feedback entries with signal_id correlation | ✓ SATISFIED (backend) / ✗ BLOCKED (dashboard display) | SKILL.md Step 0.4.5 fully implements collection. Backend types/store accept slack_reaction source. Dashboard cannot display these entries (Truth #3 gap). |
| EXTFEED-02 | 14-01 (foundation), 14-02 (collection) | PR review comment parsing — read review comments on nightwatch-created PRs and extract actionable feedback | ✓ SATISFIED (backend) / ✗ BLOCKED (dashboard display) | checkPrReviews + collectPrReviewFeedback fully implemented, wired into executor. Dashboard cannot display these entries (Truth #3 gap). |

**Note:** Both requirements are marked PENDING in REQUIREMENTS.md (no checkboxes). The traceability table also shows Phase 14 as Pending. REQUIREMENTS.md must be updated once verification passes.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| `app/frontend/lib/api.ts` | 93 | `verdict: 'accepted' \| 'rejected'` in submitFeedback — 3-state not propagated to client | ⚠️ Warning | User-submitted uncertain feedback cannot be sent from dashboard |
| `app/frontend/components/action-card.ts` | 10, 42, 44 | `existingFeedback?: 'accepted' \| 'rejected' \| null` — excludes 'uncertain' from display; also auto-collected feedback (pr_review, slack_reaction) is never shown because prop is never passed | ✗ Blocker | Automatically collected feedback from Slack/PR reviews is invisible to dashboard users |
| `app/frontend/pages/runs.ts` | 183-190 | `<ActionCard>` rendered without existingFeedback prop — existing feedback from feedback.yaml never loaded or displayed | ✗ Blocker | Truth #3 of Success Criteria unachieved |

---

### Human Verification Required

#### 1. Slack Reaction → feedback.yaml End-to-End

**Test:** Run `/kc-nightwatch`. After the run posts to Slack, add a 👍 reaction to the morning report message. On the next nightwatch run, check `~/.claude/kc-plugins-config/nightwatch-feedback.yaml`.
**Expected:** A new entry under `slack_feedback:` with `source: slack_reaction`, `verdict: accepted`, `reason: "Slack reaction: thumbsup by {user}"`, and a `run_id` matching the run that posted the message.
**Why human:** Requires a live Slack workspace with slack_read_thread MCP available in session, plus a nightwatch run cycle. Cannot be exercised in CI.

#### 2. PR Review → feedback.yaml End-to-End

**Test:** After a nightwatch run creates a PR, have a GitHub user approve the PR. On the next executor run, check `~/.claude/kc-plugins-config/nightwatch-feedback.yaml`.
**Expected:** A new entry under `pr_review_feedback:` with `source: pr_review`, `verdict: accepted`, and `signal_id` matching the signal that created the PR.
**Why human:** Requires a live GitHub PR with a real reviewer action and a running executor. The `gh pr view --json reviews` call requires network access and real repo state.

---

### Gaps Summary

**Root cause:** Phase 14 was scoped as "capture feedback from Slack reactions and PR review comments automatically." Plans 14-01 through 14-03 successfully built the backend collection pipeline (types, store routing, collection functions, executor wiring, skill layer). However, Success Criterion #3 — "Feedback entries from both Slack and PR review sources appear in the dashboard's feedback view" — was not implemented.

The gap is concentrated in the dashboard layer:

1. **No feedback view page** — `app/frontend/pages/` has runs.ts, dashboard.ts, health.ts, outcomes.ts, config.ts but no feedback.ts. The API endpoint `GET /api/feedback/:runId` exists but is never called by the frontend.

2. **ActionCard does not display auto-collected feedback** — The component has an `existingFeedback` prop but it is never passed in runs.ts. Manually-submitted feedback from the dashboard buttons works; automatically-collected entries from Slack reactions and PR reviews are stored in feedback.yaml but never shown.

3. **2-state type mismatch in frontend** — `api.ts:submitFeedback` and `action-card.ts:existingFeedback` still use the old `'accepted' | 'rejected'` union. The backend was updated to 3-state but the frontend types were not.

The PR review collection (Truth #2) is fully functional at the backend level. The Slack reaction collection (Truth #1) is fully implemented at the skill level. Both store entries correctly in feedback.yaml. The missing piece is exposing those entries to the dashboard user.

---

_Verified: 2026-03-24T14:05:00Z_
_Verifier: Claude (gsd-verifier)_
