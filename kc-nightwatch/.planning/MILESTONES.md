# Milestones

## v4.0 Flywheel Intelligence (Shipped: 2026-03-27)

**Phases completed:** 12 phases, 25 plans, 34 tasks

**Key accomplishments:**

- activePids migrated from Set<number> to Map<string, number>, AppConfigSchema backward-compatible via .passthrough(), and WorkerToServer state shape updated to active: Run[] for parallel execution foundation
- Serial single-run-at-a-time queue replaced with Map-based per-target isolation — different targets now execute concurrently, same-target runs queue with depth 1, __all__ expands to N parallel sub-runs
- 1. [Rule 2 - Missing Dependency] Added writeTargets() to yaml-store.ts
- YAML outcome data layer (outcome-store.ts) + post-run recorder (auto-action.ts) that persists PR and Linear issue URLs with dedup to ~/.claude/kc-plugins-config/nightwatch-outcomes.yaml after production runs
- 3 MCP tools (nw_get_outcomes, nw_get_outcome_status, nw_outcome_summary) registered for NW-Claude chat awareness of nightwatch-created PRs and Linear issues
- All 299 Bun tests pass in full-suite run after converting 7 test files from mock.module to spyOn+mockRestore, eliminating permanent module registry pollution
- GET /api/runs/:id/log endpoint reading log.jsonl for completed runs, parseStreamJsonLine moved to shared/, and bun --watch auto-restart added to start script
- Defense-in-depth path validation via existsSync: Add Target wizard disables Next + shows inline error, server returns 400 for empty or non-existent paths in both Add and Edit flows, with 7 passing behavioral tests
- Bun.spawn-based git worktree lifecycle module with 6 exported async functions, tested against real tmp git repos with macOS symlink resolution
- Worktree lifecycle wired into executeRun — cwd switched from target.resolved_path to worktreePath, with create-before-spawn and cleanup-in-finally ordering
- CalibrationData updated with EMA-smoothed threshold (alpha=0.3), per-run history bucketing (30-run window), minimum N gate (null threshold below 10), plus ForgeResultData and SignalPriorityItem types
- HealthIndicatorData extended with run_ids parallel array (VIZ-03) and api.getForgeResults() added for forge card data (FORGE-01), with 2 new test cases confirming alignment
- ForgeResultCard
- Priority score badge (0.72 high) on ActionCards, sorted by confidence × north-star alignment, backed by new /api/signals/priority endpoint with 14 tests
- Phase 15 VERIFICATION.md created (10/10 truths, 3 requirements SATISFIED), and REQUIREMENTS.md updated from 4 to 6 satisfied requirements — orphaned gap from v4.0 audit formally closed
- End-to-end signal priority data flow restored: /api/signals/priority/run route registered, API client updated with runId param, priorityMap keyed by signal_id — ActionCards now display score badges and sort descending in run detail

---

## v3.0 Worktree Isolation + Extended Feedback (Shipped: 2026-03-24)

**Phases completed:** 3 phases, 9 plans | **Timeline:** 1 day | **App commits:** 17 | **+2037 / -309 lines**

**Key accomplishments:**

- Test suite reliability: fixed Bun mock.module cross-file contamination (21 false failures → 0) via spyOn conversion
- Completed run log display: GET /api/runs/:id/log endpoint + LogStream fetch for completed runs (no more "Waiting for output...")
- Add Target path validation: server-side 400 for empty/invalid paths + frontend inline error
- Git worktree isolation: each nightwatch run executes in a temporary worktree, leaving target's working directory untouched
- PR review feedback: auto-parses GitHub reviewer verdicts (approve/request-changes/comment) into calibration entries
- Slack reaction feedback: reads 👍/👎/🤔 reactions on nightwatch reports as signal-correlated feedback
- Dashboard feedback display: all 5 sources (user, PR status, Linear, Slack reaction, PR review) visible with source labels and 3-state verdict

---

## v2.0 Parallel Execution + Auto-Action (Shipped: 2026-03-23)

**Phases completed:** 4 phases, 9 plans | **Timeline:** 3 days

**Key accomplishments:**

- Parallel execution: executor runs multiple targets concurrently with configurable max_concurrent_runs
- Auto-action pipeline: nightwatch automatically creates PRs and Linear issues from proposals
- Outcome tracking: PR/Linear outcomes tracked with dedup, status polling, and dashboard display
- Outcomes page: filterable outcome list with status badges, links, and signal correlation

---

## v1.1 Dashboard UX Polish (Shipped: 2026-03-20)

**Phases completed:** 3 phases, 5 plans | **Timeline:** 1 day | **App commits:** 13

**Key accomplishments:**

- Queue awareness: `queued_at` timestamps on all 4 enqueue paths, GET /api/worker/state endpoint, run:failed SSE broadcast
- Toast notification system: signal-backed toast queue with auto-dismiss, z-index layering above dialogs
- Browser notifications: desktop alerts for run completion/failure with user-gesture-gated permission
- Unified polling: `usePoll` hook with `refreshTrigger` signal replacing inline setInterval patterns
- Dead code cleanup: orphaned chat-drawer.ts deleted, phases_completed wired into target-detail, sidebar Add Target functional

---

## v1.0 Nightwatch Dashboard MVP (Shipped: 2026-03-19)

**Phases completed:** 4 phases, 15 plans | **Timeline:** 2 days | **App LOC:** ~8.8K

**Key accomplishments:**

- Two-process architecture: Bun server + worker with native IPC, crash recovery, orphan cleanup
- Dashboard cockpit: target cards, run trigger with real-time log streaming, run history with filters
- Flywheel core: NW-Claude chat with auto-brief, YAML config editor with 4-step validation, feedback calibration
- MCP server: 12 tools exposing nightwatch state to any Claude session
- Flywheel health: indicator sparklines, reject rate charts, per-target health arrows

---
