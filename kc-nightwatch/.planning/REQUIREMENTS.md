# Requirements: Nightwatch Dashboard

**Defined:** 2026-03-23
**Core Value:** The closed-loop feedback flywheel — NW monitors, proposes, learns from feedback, and gets measurably better over time.

## v3.0 Requirements

Requirements for run execution reliability, worktree isolation, extended feedback, and test infrastructure.

### Run Execution UX

- [x] **RUNUX-01**: Completed run detail reads log from file via GET /api/runs/:id/log — SSE-only display shows "Waiting for output..." when page opens after run completes
- [x] **RUNUX-02**: Target `path` field required in Add Target wizard — optional path falls back to nonexistent directory, causing silent execution failures
- [x] **RUNUX-03**: Server auto-restart on code change via Bun --watch or file watcher — currently requires manual restart after every code edit

### Worktree Isolation

- [ ] **WKTREE-01**: Executor creates a temporary git worktree from target's latest main branch before each run — run executes in isolated worktree, not target's working directory
- [ ] **WKTREE-02**: Worktree cleanup after run — remove worktree when run has no branch to preserve; keep worktree if proposal/fix branch was created
- [ ] **WKTREE-03**: Proposals and fixes create branches inside the worktree — branches are pushed to origin but worktree is cleaned up; main working directory is never modified by nightwatch

### Extended Feedback

- [ ] **EXTFEED-01**: Slack reaction parsing — read reactions on nightwatch Slack reports (👍/👎/🤔) and convert to feedback entries with signal_id correlation
- [ ] **EXTFEED-02**: PR review comment parsing — read review comments on nightwatch-created PRs and extract actionable feedback (approve = accepted, request changes = rejected, comment = signal for next run)

### Test Infrastructure

- [x] **TEST-01**: Fix Bun mock.module cross-file contamination — 21 false failures in full suite due to module cache pollution between test files; all pass in isolation

## Out of Scope

| Feature | Reason |
|---------|--------|
| Cron expression scheduling | Interval scheduling is sufficient; cron adds complexity without value for single user |
| Auto-merge PRs | Safety net requires human review; auto-create is the boundary |
| Worktree per-target persistence | Worktrees are ephemeral per-run, not persistent per-target — avoids disk bloat |
| Slack message posting (write) | Read-only reactions for now; posting is already handled by nightwatch skill |
| Real-time Slack webhook | Polling reactions after run is sufficient; webhook adds infra complexity |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| TEST-01 | Phase 12 | Complete (12-01) |
| RUNUX-01 | Phase 12 | Complete (12-02) |
| RUNUX-02 | Phase 12 | Complete (12-03) |
| RUNUX-03 | Phase 12 | Complete (12-02) |
| WKTREE-01 | Phase 13 | In Progress (13-01 worktree-manager built) |
| WKTREE-02 | Phase 13 | In Progress (13-01 cleanupWorktree built) |
| WKTREE-03 | Phase 13 | In Progress (13-01 push-before-remove built) |
| EXTFEED-01 | Phase 14 | Pending |
| EXTFEED-02 | Phase 14 | Pending |

**Coverage:**
- v3.0 requirements: 9 total
- Mapped to phases: 9
- Unmapped: 0

---
*Requirements defined: 2026-03-23*
*Traceability updated: 2026-03-24 (Phase 13 plan 01 complete — worktree-manager built)*
