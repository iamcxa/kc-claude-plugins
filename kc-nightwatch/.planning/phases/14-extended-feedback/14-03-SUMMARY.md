---
phase: 14-extended-feedback
plan: 03
subsystem: skill
tags: [slack, feedback, reactions, skill, extfeed-01]
dependency_graph:
  requires: [14-01]
  provides: [slack-reaction-collection, slack-url-capture, step-0.4.5]
  affects: [kc-nightwatch-skill, improvement-log, feedback-yaml]
tech_stack:
  added: []
  patterns: [slack-mcp-graceful-degradation, feedback-loop-closure, abstraction-boundary-documentation]
key_files:
  created: []
  modified:
    - skills/kc-nightwatch/SKILL.md
decisions:
  - "slack_url stored at run-date level in improvement-log (not per-target) — one Slack message covers all targets in a run"
  - "D-10 abstraction boundary: only Step 0.4.5 Step 2 needs changing for Bot API swap — Steps 3-5 are backend-agnostic"
  - "Graceful degradation: absent/null slack_url skips silently; MCP failures log [WARN] but never block Phase 1+"
  - "Dedup rule: rejected > uncertain > accepted when same user reacts with multiple emojis"
metrics:
  duration: 3min
  completed: "2026-03-24"
  tasks: 2
  files: 1
requirements_covered: [EXTFEED-01]
---

# Phase 14 Plan 03: Slack Reaction Collection Skill Layer Summary

## One-liner

Slack message URL captured after posting (Step 5.4) and reactions collected on next run (Step 0.4.5) — closing the feedback loop from emoji to FeedbackEntry with source 'slack_reaction'.

## What Was Built

Skill-layer collection logic for EXTFEED-01 Slack reaction feedback. The type foundation (slack_reaction source, slack_feedback store key) was built in Plan 14-01. This plan adds:

1. **Step 5.2 improvement-log format** — `slack_url` field added at run-date level (not per-target). Includes note explaining null semantics (webhook fallback, delivery failure).
2. **Step 5.4 URL capture** — After successful `slack_send_message` MCP delivery, construct full URL from `ts` value. Webhook fallback sets `null`. Failed delivery sets `null`.
3. **Step 0.4.5: Collect Slack Reaction Feedback** — New step inserted between Step 0.4 (PR/Linear feedback) and Phase 0.5 (indicator baseline):
   - Step 1: Reads `slack_url` from most recent improvement-log entry; skips silently if absent or null
   - Step 2: Calls `slack_read_thread` MCP; logs `[WARN]` on failure but never blocks Phase 1+
   - Step 3: Maps thumbsup→accepted, thumbsdown→rejected, thinking_face→uncertain per D-02; ignores other reactions; dedup favors strongest signal per user
   - Step 4: Writes FeedbackEntries with `source: "slack_reaction"` to `slack_feedback` store
   - Step 5: Logs result count summary

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Add slack_url capture to Step 5.2 and Step 5.4 | b837968 | SKILL.md |
| 2 | Add Step 0.4.5 — Slack Reaction Collection | e132160 | SKILL.md |

## Acceptance Criteria Verification

- `grep -c "slack_url" SKILL.md` → 8 (requires 5+)
- `grep -c "Step 0.4.5" SKILL.md` → 2 (requires 2+)
- `grep -c "slack_reaction" SKILL.md` → 3 (requires 3+)
- `grep -c "slack_read_thread" SKILL.md` → 2 (requires 2+)
- `grep -q "D-10"` → FOUND (abstraction note present)
- `grep -q "D-02"` → FOUND (reaction mapping references decision)
- `grep -q "thumbsup.*accepted"` → FOUND (reaction mapping table exists)
- `grep -q "skip silently"` → FOUND (graceful skip when no slack_url)

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — the skill instructions are complete. The FeedbackEntry writes use the `slack_feedback` store key created in Plan 14-01. The full feedback loop is closed:
1. Step 5.4 posts to Slack → captures URL
2. Step 5.2 writes URL to improvement-log
3. Step 0.4.5 (next run) reads URL → collects reactions → writes FeedbackEntries

## Self-Check: PASSED

- [x] `skills/kc-nightwatch/SKILL.md` exists and contains 8 occurrences of 'slack_url'
- [x] `skills/kc-nightwatch/SKILL.md` contains 3 occurrences of 'slack_reaction'
- [x] `skills/kc-nightwatch/SKILL.md` contains 2 occurrences of 'slack_read_thread'
- [x] `skills/kc-nightwatch/SKILL.md` contains 2 occurrences of 'Step 0.4.5'
- [x] D-10 abstraction note present
- [x] D-02 reaction mapping reference present
- [x] Commit b837968 exists (Task 1)
- [x] Commit e132160 exists (Task 2)
