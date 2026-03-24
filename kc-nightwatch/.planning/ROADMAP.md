# Roadmap: Nightwatch Dashboard

## Milestones

- ✅ **v1.0 MVP** — Phases 1-4 (shipped 2026-03-19) → [archive](milestones/v1.0-ROADMAP.md)
- ✅ **v1.1 Dashboard UX Polish** — Phases 5-7 (shipped 2026-03-20) → [archive](milestones/v1.1-ROADMAP.md)
- ✅ **v2.0 Parallel Execution + Auto-Action** — Phases 8-11 (shipped 2026-03-23) → [archive](milestones/v2.0-ROADMAP.md)
- 🔄 **v3.0 Worktree Isolation + Extended Feedback** — Phases 12-14 (in progress)

## Phases

- [x] **Phase 12: Test Infrastructure + Run UX Fixes** — Fix test suite contamination and close immediate run UX gaps (completed 2026-03-24)
- [x] **Phase 13: Worktree Isolation** — Executor runs each nightwatch session in an isolated git worktree (completed 2026-03-24)
- [ ] **Phase 14: Extended Feedback** — Slack reaction and PR review comment feedback channels

## Phase Details

### Phase 12: Test Infrastructure + Run UX Fixes
**Goal**: The test suite runs reliably and basic run execution UX gaps are closed
**Depends on**: Nothing (first phase of v3.0)
**Requirements**: TEST-01, RUNUX-01, RUNUX-02, RUNUX-03
**Success Criteria** (what must be TRUE):
  1. Full test suite (`bun test`) passes without false failures — all 21 previously contaminated tests are green in full-suite run, not just isolation
  2. Completed run detail page shows actual log content fetched from file, not "Waiting for output..."
  3. Add Target wizard rejects submission when `path` is empty — user sees inline validation error
  4. Code changes to server or worker files cause the server to restart automatically without manual intervention
**Plans:** 3 plans

Plans:
- [x] 12-01-PLAN.md — Fix Bun mock.module cross-file test contamination (spyOn conversion)
- [x] 12-02-PLAN.md — Add GET /api/runs/:id/log endpoint + LogStream completed run fetch + auto-restart
- [x] 12-03-PLAN.md — Defense-in-depth path validation (wizard + server)

### Phase 13: Worktree Isolation
**Goal**: Every nightwatch run executes in a temporary git worktree, leaving the target's working directory untouched
**Depends on**: Phase 12
**Requirements**: WKTREE-01, WKTREE-02, WKTREE-03
**Success Criteria** (what must be TRUE):
  1. A run triggered against a target creates a new git worktree checked out from the target's latest main branch before execution begins
  2. When a run produces no branch (dry-run, signal-only, no proposals), the worktree is removed after the run completes
  3. When a run creates a proposal or fix branch, that branch exists in the worktree and is pushed to origin — the target's working directory has no uncommitted changes from the run
  4. After any run (with or without branch), the target's main working directory git status is identical to before the run started
**Plans:** 2 plans

Plans:
- [x] 13-01-PLAN.md — Create worktree-manager.ts with git worktree lifecycle functions + tests
- [x] 13-02-PLAN.md — Wire worktree lifecycle into executor.ts + integration tests

### Phase 14: Extended Feedback
**Goal**: Nightwatch captures feedback from Slack reactions and PR review comments automatically
**Depends on**: Phase 13
**Requirements**: EXTFEED-01, EXTFEED-02
**Success Criteria** (what must be TRUE):
  1. After a nightwatch run posts to Slack, any reaction added to that message is parsed and appears as a feedback entry in feedback.yaml with correct signal_id correlation
  2. When a reviewer approves, requests changes on, or comments on a nightwatch-created PR, that review is parsed and a corresponding feedback entry (accepted/rejected/signal) is written to feedback.yaml
  3. Feedback entries from both Slack and PR review sources appear in the dashboard's feedback view alongside existing dashboard/MCP feedback
**Plans:** 2 plans

Plans:
- [ ] 14-01-PLAN.md — Extend types, store routing, and API/MCP validation for 3-state verdict + new sources
- [ ] 14-02-PLAN.md — Implement checkPrReviews + collectPrReviewFeedback and wire into executor

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1-4 | v1.0 | 15/15 | Complete | 2026-03-19 |
| 5-7 | v1.1 | 5/5 | Complete | 2026-03-20 |
| 8-11 | v2.0 | 9/9 | Complete | 2026-03-23 |
| 12. Test Infra + Run UX | v3.0 | 3/3 | Complete | 2026-03-24 |
| 13. Worktree Isolation | v3.0 | 2/2 | Complete | 2026-03-24 |
| 14. Extended Feedback | v3.0 | 0/2 | Planning | - |
| **Total** | | **34** | | |
