# Project Research Summary

**Project:** Nightwatch Dashboard v2.0 — Parallel Execution + Auto-Action
**Domain:** Bun-native autonomous improvement dashboard (Preact + HTM + Hono + Bun worker + IPC)
**Researched:** 2026-03-21
**Confidence:** HIGH

## Executive Summary

The Nightwatch Dashboard v2.0 is a significant capability expansion on a complete v1.1 cockpit. It changes two fundamental execution properties — from serial-global to per-target-parallel execution, and from one-global-interval to per-target scheduling — and closes the output loop by auto-creating PRs and Linear issues without human approval gates. The existing stack (Bun + Hono + Preact/HTM + Bun IPC) handles all of this without new npm packages. The parallel execution model is not a concurrency library problem; it is a queue data structure problem solvable with `Map<string, Run[]>` and Bun's single-threaded async event loop, where `Bun.spawn` already provides genuine OS-level parallelism.

The recommended approach is a 4-phase build ordered strictly by data-flow dependencies: schema + IPC shape first (everything downstream reads these), then the worker (parallel queues + per-target scheduler), then server endpoints and MCP tools, then frontend. Within this order, two independent tracks can proceed in parallel: the execution model refactor (worker queues/scheduler) and the auto-create output loop (PR/Linear wiring in executor + feedback-collector). Both tracks depend only on the schema changes in Phase 1. The Outcomes page depends on the server endpoints in Phase 3, which in turn depend on the worker state shape from Phase 2.

The three highest-risk areas are: (1) the `activePids` data structure, which must change from a `Set<number>` to a `Map<string, number>` keyed by run_id before parallelism is enabled or cancel will kill all concurrent runs simultaneously; (2) concurrent YAML writes from parallel `claude -p` processes to shared config files like `nightwatch-improvement-log.md`, which requires an audit of exactly which files the NW skill writes before enabling parallel spawning; and (3) deduplication logic for auto-created PRs and Linear issues, which must include pre-flight existence checks (`gh pr list` and Linear search) or repeated runs on the same unresolved signal will create duplicate PRs and Linear issues that erode user trust. All three are well-defined problems with clear prevention strategies.

## Key Findings

### Recommended Stack

No new npm packages are required for v2.0. All five major new feature areas — parallel execution, per-target scheduling, auto PR creation, auto Linear issue creation, and outcome tracking — are implementable with the existing stack. The `Map<string, Run[]>` parallel queue model requires zero new dependencies. `gh pr create` reuses the same `Bun.spawn` pattern already proven in `feedback-collector.ts`. Linear issue creation reuses the same `fetch()` GraphQL pattern already in `checkLinearStatus()`. A new `outcomes.yaml` store extends the existing `run-store.ts` read/append YAML pattern.

**Core technologies (unchanged from v1.0/v1.1):**
- **Bun 1.3.9**: Runtime — `setInterval` multi-timer, `Bun.spawn`, `fetch`, `Map` — all stable at current version
- **Hono 4.12.x**: HTTP server — adds `GET /api/outcomes` route; existing SSE and polling patterns unchanged
- **Preact + HTM**: Frontend — adds new `outcomes.ts` page; no new hooks or libraries needed
- **yaml + zod**: YAML persistence + schema validation — `ActionOutcome` type + `outcomes.yaml` file added; no version change

**v2.0 additions (zero new packages):**
- `worker/pr-creator.ts`: `Bun.spawn(['gh', 'pr', 'create', ...])` wrapper — mirrors `feedback-collector.ts`
- `worker/linear-creator.ts`: Direct `fetch()` to Linear GraphQL API — mirrors `checkLinearStatus()`
- `server/services/outcome-store.ts`: New YAML store for `ActionOutcome` records — mirrors `run-store.ts`
- `frontend/pages/outcomes.ts`: New Preact page — mirrors `frontend/pages/runs.ts` list pattern

### Expected Features

**Must have (table stakes — ship in v2.0 P1):**
- Parallel execution model — per-target queue isolation (`Map<string, Run[]>` + `Map<string, boolean>`); different targets concurrent, same target queued
- Per-target scheduling — `Target.schedule?: { interval_hours }` override with global fallback; 10-min minimum enforced
- Auto-create PR — post-run `gh pr create` on actions where `branch` is set; pre-flight `gh pr list` dedup check required
- Auto-create Linear issue — auto `issueCreate` mutation when signal classified as `linear-issue`; dedup via `improvement-log.md` lookup required
- Action card PR/Linear links — `ActionCard` already renders `pr_url`; add parallel `linear_url` "View Issue" link
- Outcomes aggregate page — new `GET /api/outcomes` server endpoint + `frontend/pages/outcomes.ts` + Bottom Nav "Outcomes" tab
- NW-Claude outcomes awareness — add `nw_get_outcomes` MCP tool to `mcp-tools.ts`
- UI fix: bottom nav gap — black line between content and nav bar (carry-over from v1.1)
- Schema migration: remove `max_concurrent_runs: z.literal(1)` from `AppConfigSchema` — existing configs must start cleanly

**Should have (P2 — ship if scope allows):**
- Phase 0.6 implementation outcome tracking — PR merge status polling, indicator re-measurement, `ImplementationOutcome` population
- Per-target "next run at" display on target cards
- PR status badge (open/merged/closed) on action cards

**Defer to v2.1+:**
- Outcome analytics charts and trend visualizations
- Real-time push for outcome status updates (polling at 30s is sufficient)
- Per-target auth token management via UI

### Architecture Approach

The v2.0 architecture changes are additive to the proven 3-tier Bun worker + Hono server + Preact frontend model. The most significant change is inside the worker: the single `queue: Run[]` + `currentRun: Run | null` model becomes per-target `Map<string, Run[]>` + `Map<string, Run>`. The IPC `state` message shape widens from `{ queue, current }` to `{ targets: Record<string, { queue, current }> }`. All server and frontend consumers update to match this new shape. The `executor.ts` is untouched by parallelism — single-run execution is already correct; parallelism is a queue-routing concern.

**Major components changed in v2.0:**
1. `shared/types.ts` — MODIFIED: per-target IPC state shape; `Target.schedule`; `ScheduleConfig.per_target`; `RunSummaryAction.linear_url`; `OutcomeItem` type; `max_concurrent_runs` removed
2. `worker/index.ts` — MODIFIED: `targetQueues` + `activeRuns` Maps; new `processTarget()`; `activePids` Set→Map (critical safety fix)
3. `worker/scheduler.ts` — MODIFIED: `Map<string, Timer>` per-target timers; min interval enforcement
4. `worker/executor.ts` — MINOR: `production-auto` mode system prompt injection
5. `server/routes/api.ts` + `server/services/outcome-store.ts` — ADD `GET /api/outcomes`; ADD `outcome-store.ts`
6. `server/services/mcp-tools.ts` — ADD `nw_get_outcomes` + `nw_get_outcome_status`
7. `frontend/pages/outcomes.ts` — NEW aggregate page
8. `frontend/components/action-card.ts` + `trigger-dialog.ts` + `target-detail.ts` + `bottom-nav.ts` — UI updates for new capabilities

**4 new files total:** `worker/pr-creator.ts`, `worker/linear-creator.ts`, `server/services/outcome-store.ts`, `frontend/pages/outcomes.ts`

### Critical Pitfalls

1. **`activePids` Set kills all concurrent runs on cancel** — Change from `Set<number>` to `Map<string, number>` keyed by `run_id` before enabling any parallel execution. Cancel handler must target by run_id, not kill all. Do this first in Phase 1.

2. **IPC `state` message shape mismatch during migration** — The server's `lastWorkerState` type and all frontend consumers must update atomically with the worker's new `{ targets: Record<string, {queue, current}> }` shape. Keep deprecated `current` compat shim for one phase only, then remove.

3. **Per-target scheduler timer leak** — `startScheduler()` must call `stopAllSchedulers()` (clearing the full `Map<string, Timer>`) before rebuilding, not just `clearInterval(schedulerTimer)` (the old single-timer approach). Any update to one target's schedule must restart ALL timers from the full config.

4. **Concurrent YAML writes from parallel `claude -p` processes** — Audit which files the NW skill writes before enabling parallel spawning. `nightwatch-improvement-log.md` is append-only (mostly safe). `nightwatch-runs.yaml` must never be written by skill processes — only the app via `run-store.ts`. Per-target `memory/{target_name}/` and `runs/{run_id}/` are already scoped and safe.

5. **Auto PR dedup failure creates duplicate PRs** — Before any `gh pr create`, run `gh pr list --head {branch} --json url` and reuse the existing URL if found. Never fire-and-forget `gh pr create` without this pre-flight check.

6. **Auto Linear issue dedup failure creates duplicate issues** — Before `issueCreate`, check `improvement-log.md` for an existing `linear_url` for this signal. If the previous issue is still open (check via `checkLinearStatus`), skip creation. Title template `[NW] {signal_summary} [{target}]` enables search-based dedup as a secondary guard.

7. **`max_concurrent_runs: z.literal(1)` blocks app startup after upgrade** — Remove from `AppConfigSchema` and add a startup migration that silently ignores the old field if present. This is a compile-time blocker — fix it first in Phase 1.

8. **`cleanupOldRuns` deletes in-progress run artifacts under parallelism** — Pass active run IDs to `cleanupOldRuns` and skip deletion for any run in `activeRuns.keys()`. Or move cleanup to worker startup only.

## Implications for Roadmap

Based on combined research, the dependency graph maps cleanly to 4 phases with two internal parallel tracks.

### Phase 1: Schema + Safety Foundation

**Rationale:** All downstream work depends on the schema. `activePids` and `max_concurrent_runs` are code-correctness and startup blockers that must be fixed before any execution model work begins. This phase has no UI and no server changes — pure type/safety work.

**Delivers:** Updated `shared/types.ts` (per-target IPC state shape, `ActionOutcome`, `OutcomeItem`, `Target.schedule`, `RunSummaryAction.linear_url`, `max_concurrent_runs` removed); `shared/constants.ts` additions; `activePids` Set→Map in `executor.ts`; `cleanupOldRuns` safety fix; schema startup migration for old `app-config.yaml` files

**Addresses:** FEATURES.md: schema migration (table stakes); PITFALLS.md: Pitfalls 1, 5, 7, 10

**Avoids:** Type errors cascading into all downstream work; cancel-all bug in parallel mode; startup failure for existing users

**Research flag:** Standard patterns — no additional research needed.

### Phase 2: Worker — Parallel Execution + Per-Target Scheduling

**Rationale:** The two foundational execution model changes can proceed as parallel sub-tracks within this phase because they affect different files (`index.ts` vs `scheduler.ts`) with a clean interface boundary (`enqueue()` function). The parallel execution refactor is the bigger change and should be done first since the scheduler calls `enqueue()`. Both must be complete before server/frontend can use the per-target state shape.

**Delivers:** `worker/index.ts` per-target queue model (targetQueues + activeRuns); new `processTarget()` + `enqueue()` replacing `processNextRun()`; `worker/scheduler.ts` multi-timer model; per-target interval override with global fallback; 10-min minimum enforcement; `sendState()` broadcasting per-target shape

**Uses:** STACK.md patterns: `Map<string, Run[]>` native data structures, zero new deps, `setInterval` multi-timer pattern

**Avoids:** PITFALLS.md: Pitfall 3 (scheduler timer leak), Pitfall 4 (concurrent YAML writes — audit first), Pitfall 8 (schedule IPC wipes all timers), Pitfall 9 (SSE log cross-contamination), Pitfall 12 (agent-browser daemon collision)

**Research flag:** Standard patterns — verified against Bun event loop model and existing codebase. No additional research needed.

### Phase 3: Server + Auto-Action Output Loop

**Rationale:** Two parallel sub-tracks here too. Track A: server endpoints + MCP tools (depend on Phase 1 schema + Phase 2 worker state shape). Track B: auto PR/Linear creation in worker (depends only on Phase 1 schema, not Phase 2 queue model — can run in parallel with Phase 2). In practice, do Track B first (it's simpler) and Track A second.

**Delivers:** Track A — `server/ipc.ts` per-target state shape; `GET /api/outcomes`; `server/services/outcome-store.ts`; `nw_get_outcomes` + `nw_get_outcome_status` MCP tools; `server/routes/schedule.ts` per-target schedule acceptance; Track B — `worker/pr-creator.ts`; `worker/linear-creator.ts`; `worker/executor.ts` auto-create system prompt injection; `worker/feedback-collector.ts` linear_url wiring

**Implements:** FEATURES.md P1: auto-create PR, auto-create Linear issue, outcomes aggregate data layer, NW-Claude outcomes awareness

**Avoids:** PITFALLS.md: Pitfall 6 (gh pr create on existing PR fails silently — pre-flight check), Pitfall 7 (duplicate Linear issues — dedup check), Pitfall 11 (outcomes chicken-and-egg — phase ordering)

**Research flag:** `gh` CLI non-interactive mode and Linear GraphQL `issueCreate` mutation are both verified HIGH confidence. No additional research needed.

### Phase 4: Frontend Outcomes + UI Polish

**Rationale:** All server endpoints exist; worker state is correct. Frontend changes are purely additive consumers. Five independent sub-tasks with no dependencies between them — parallelize freely.

**Delivers:** `frontend/pages/outcomes.ts` (NEW); `frontend/lib/api.ts` `getOutcomes()`; `frontend/app.ts` `#/outcomes` route; `frontend/components/action-card.ts` "View Issue" `linear_url` link; `frontend/components/trigger-dialog.ts` auto-create toggle; `frontend/pages/runs.ts` `implementation_outcomes` section; `frontend/components/target-detail.ts` per-target schedule display; `frontend/components/bottom-nav.ts` Outcomes tab + nav gap CSS fix

**Avoids:** PITFALLS.md: UX pitfall — outcomes page without grouping (group by target + status); UX pitfall — generic PR title (use `[NW] {signal} [{target}]` template)

**Research flag:** Standard Preact/HTM patterns. Outcomes page follows `runs.ts` list pattern exactly. No additional research needed.

### Phase Ordering Rationale

- Schema changes are compile-time prerequisites — every other phase has TypeScript imports that depend on the new types
- `activePids` and `max_concurrent_runs` are safety/startup blockers — fixing them in Phase 1 before execution model work prevents both data corruption and startup failure
- Worker changes before server changes — server needs to consume the new `WorkerToServer.state` per-target shape; premature consumption would read `undefined`
- Auto-create PR/Linear is independent of the parallel execution model but shares the Phase 3 slot because it produces the outcome data that the Phase 4 UI consumes
- Frontend last — standard dependency ordering; all API endpoints and data must exist before consumers are wired

### Research Flags

All 4 phases use well-documented patterns with HIGH-confidence sources. No `/gsd:research-phase` is needed for any phase.

- **Phase 1:** Schema migrations + type changes — standard TypeScript/Zod, no research needed
- **Phase 2:** Worker queue model — verified against Bun event loop; `Map` + `setInterval` multi-timer confirmed in Bun 1.3.9 docs; STACK.md has code-level implementation patterns
- **Phase 3:** `gh pr create` non-interactive flags verified against gh 2.83.2 official manual; Linear `issueCreate` mutation verified against Apollo schema; auth pattern (no Bearer prefix) confirmed in existing codebase
- **Phase 4:** Preact/HTM page patterns established in v1.0/v1.1; `usePoll` hook already exists; outcomes page is `runs.ts` clone

One deferred item to flag during Phase 4 planning: Phase 0.6 implementation outcome tracking (P2). The `ImplementationOutcome` type and `per_target.implementation_outcomes` field exist in the schema. The measurement logic belongs in the kc-nightwatch skill. The app only needs to surface the data. Decision: include Phase 0.6 as a stretch task in Phase 4 or defer to v2.1 based on scope.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All v2.0 features confirmed implementable with existing stack; zero new packages; verified via Bun 1.3.9 docs, gh 2.83.2 official manual, Linear Apollo schema, and direct codebase inspection of feedback-collector.ts + run-store.ts |
| Features | HIGH | Derived from direct codebase read of all affected files + authoritative PROJECT.md v2.0 requirements; schema hooks (`pr_url`, `ImplementationOutcome`, `linear_url` stub) already exist confirming design intent |
| Architecture | HIGH | Based on direct inspection of all 18 modified/new files with line-level specificity; complete file change matrix + 11-step build order provided; data flow diagrams for all 4 major feature tracks |
| Pitfalls | HIGH | Mix of project-specific pitfalls from direct codebase inspection (activePids, YAML concurrent writes, cleanupOldRuns) + verified API behaviors (gh exit codes, Linear GraphQL) + MEMORY.md known patterns (ToolSearch, Linear team requirement, Bun IPC) |

**Overall confidence:** HIGH

### Gaps to Address

- **NW skill writes audit**: Before enabling parallel execution, confirm exactly which files `kc-nightwatch` skill writes during a run. The ARCHITECTURE research identifies `memory/{target}/` and `runs/{run_id}/` as per-target/per-run scoped (safe). `nightwatch-improvement-log.md` is append-only (low risk). Any other shared writes need a coordination strategy. This is a 30-min audit task, not a research gap.
- **Phase 0.6 scope decision**: Implementation outcome tracking (`ImplementationOutcome` population + health page correlation) is the highest-complexity v2 feature. The type exists; the measurement logic is in the skill. Decision: include in v2.0 Phase 4 as a stretch goal or explicitly defer to v2.1. Flag this as a planning decision, not a technical gap.
- **`gh` auth in safehouse context**: The safehouse may restrict `~/.config/gh/` access. Verify `buildSafehouseFlags` in `policy.ts` grants read access to `~/.config/gh/`. One `gh repo view` dry-run test from within a safehouse-wrapped process confirms this before building the auto-create PR flow.

## Sources

### Primary (HIGH confidence)
- Direct codebase inspection (2026-03-21): `app/worker/index.ts`, `app/worker/executor.ts`, `app/worker/scheduler.ts`, `app/worker/feedback-collector.ts`, `app/worker/policy.ts`, `app/server/ipc.ts`, `app/server/routes/api.ts`, `app/server/services/run-store.ts`, `app/server/services/mcp-tools.ts`, `app/shared/types.ts`, `app/shared/constants.ts`, `app/frontend/components/action-card.ts`, `app/frontend/pages/runs.ts`, `app/frontend/lib/api.ts`
- `.planning/PROJECT.md` — v2.0 requirements list (authoritative)
- `reference/ROADMAP.md` — v2.0 milestone definition
- Bun 1.3.9 docs (bun.sh/reference/globals/setInterval) — multi-timer pattern confirmed
- Bun GitHub Issue #15050 — no native PQueue; `Map` pattern is idiomatic
- gh 2.83.2 official manual (cli.github.com/manual/gh_pr_create) — `--title --body --head --base` confirmed non-interactive
- Linear API docs (linear.app/developers/graphql) — `issueCreate` mutation structure
- Linear Apollo schema (studio.apollographql.com/public/Linear-API) — `issue.url` field on mutation response

### Secondary (MEDIUM confidence)
- Bun IPC throughput under parallel load — Bun docs state Node-compatible message passing; no official throughput limit; empirical evidence from existing NW runs
- Linear issue dedup pattern — derived from kc-sentry-insight `date-based cleanup` lesson in MEMORY.md
- LogRocket — UI patterns for async workflows (parallel job dashboard patterns)
- Per-target scheduler reference implementations: Cronicle, Dkron (similar domain, different scale)

### Tertiary (LOW confidence)
- Outcome tracking patterns — Linear + GitHub integration docs, DORA metrics background (general patterns; exact v2.0 design is project-specific, not borrowed)

---
*Research completed: 2026-03-21*
*Ready for roadmap: yes*
