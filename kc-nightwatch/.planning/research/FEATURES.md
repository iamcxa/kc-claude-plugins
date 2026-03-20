# Feature Research

**Domain:** Autonomous Improvement Dashboard v2.0 — Parallel Execution + Auto-Action
**Researched:** 2026-03-21
**Confidence:** HIGH (codebase read + confirmed patterns via PROJECT.md + web research)

---

## Context

This is a v2.0 research pass. v1.0 built the full dashboard cockpit. v1.1 polished run lifecycle feedback. v2.0 changes the fundamental execution model and closes the output loop:

**What changes in v2.0:**
- Execution goes from max-1-global to per-target isolation (different targets concurrent, same target queued)
- Scheduling goes from one-global-interval to per-target intervals with global fallback
- Outputs go from "proposals on branches" to auto-created PRs and Linear issues without human approval gates
- Outcomes become visible in the UI: action cards get PR/Linear links, new Outcomes aggregate page
- NW-Claude becomes aware of outcomes (chat can answer about them)
- Feedback loop closes further: Phase 0.6 tracks whether merged PRs actually improved indicators

**What the codebase currently has (carry-forward):**
- `max_concurrent_runs: z.literal(1)` enforced at Zod schema level — must change to per-target model
- Single `ScheduleConfig` with one `interval_hours` — must extend to per-target overrides
- `RunSummaryAction` already has `pr_url?: string` and `branch?: string` fields — hooking point exists
- `ActionCard` component already renders a "View PR" link when `pr_url` is set — partially built
- `ImplementationOutcome` type already defined in `types.ts` — schema ready, just not populated
- `Run` type has `trigger: 'implementation'` variant — designed for v2 auto-action trigger

**Constraints (unchanged):**
- No build step (Preact + HTM, no Vite/webpack)
- Bun + Hono + IPC architecture unchanged
- No new frontend frameworks or state libraries
- agent-safehouse mandatory for all `claude -p` spawns

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features that users of an autonomous improvement dashboard assume exist once the system matures past single-job execution. Missing these creates visible operational friction.

| Feature | Why Expected | Complexity | Depends On |
|---------|--------------|------------|------------|
| Per-target scheduling (individual intervals) | Once a user has 3+ targets, a single global schedule forces all to run at the same cadence. A busy plugin gets the same frequency as a stable one — obviously wrong. | MEDIUM | AppConfig schema change (add `schedule` field to Target), IPC schedule message update, scheduler refactor |
| Global schedule fallback for targets without override | "Set it and forget it" — targets with no per-target schedule should inherit the global interval. Removing that would require configuring every target. | LOW | Per-target scheduling feature (precondition) |
| Minimum interval enforcement (10 min floor) | Prevents accidental tight loops that spam the LLM API. A floor users expect because it prevents costly mistakes. | LOW | Scheduler logic — add guard before enqueueing |
| Parallel execution (different targets concurrent) | Running 3 targets serially triples wall-clock time. Once targets are independent (different repos, different contexts), parallel execution is expected. | HIGH | Execution model refactor: one worker slot → per-target slots. Biggest architectural change in v2. |
| Same-target queuing (not dropped) | If a scheduled run arrives while the same target is running, it should queue, not be silently dropped. Users expect queued confirmation, not silent discard. | MEDIUM | Parallel execution (requires per-target queue map, not single global queue) |
| Auto-create PR when code changes proposed | The current nightwatch pipeline proposes changes but requires a human to manually create the PR. In an automated improvement tool, the PR creation step should be automated after acceptance. | MEDIUM | Existing `branch` field in RunSummaryAction, gh CLI or GitHub API, new `trigger: 'implementation'` run type |
| Auto-create Linear issue for improvement signals | Same as PR — nightwatch identifies signals and already creates Linear issues in some paths. Making this consistent and visible closes the loop. | MEDIUM | Linear MCP tools (already available), signal classification in nightwatch skill |
| Action cards show PR and Linear links | When NW creates a PR or issue, the dashboard action card should show a clickable link. Currently `pr_url` exists in the type but is only sometimes populated. | LOW | Auto-create PR/Linear features (precondition to have URLs), existing `ActionCard` component already renders `pr_url` |
| Outcomes aggregate page | A single page listing all PRs and Linear issues created across all runs and targets, filterable by target and status. Analogous to GitHub's PR list but scoped to NW-generated items. | MEDIUM | Action cards with PR/Linear links, new route + page component |
| NW-Claude chat awareness of outcomes | If a user asks "what PRs did NW create this week?", NW-Claude should be able to answer from the outcomes data, not just the run summaries. | MEDIUM | Outcomes stored in run summaries, MCP server tool expansion |

### Differentiators (Worth Doing Well)

Features where implementation quality matters beyond basic functionality.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Implementation outcome tracking (Phase 0.6) | Closes the final loop of the flywheel: "NW proposed this, the PR merged, the indicator improved by X%. Was the intervention effective?" No generic automation tool does this. | HIGH | Requires: PR merge status polling (gh CLI), indicator re-measurement after merge, `ImplementationOutcome` type already defined in types.ts — needs population |
| Parallel execution status per target on dashboard | When 3 targets run simultaneously, the dashboard should show all 3 as "running" with independent progress indicators — not a single spinner. Users of parallel execution tools (CI/CD) expect per-job visibility. | MEDIUM | Per-target execution slots, dashboard polling must show concurrent state, `TargetDetail` component update |
| Schedule "next run at" per target | When schedules are per-target, each target card should show its own "next run at" timestamp. Currently one global "next run" shown. | LOW | Per-target scheduler state reporting back via IPC, dashboard display update |
| Outcomes filterable by target, date range, status | A PR list with 50 entries that can't be filtered is unusable. Filter by target (which repo?), date (this week?), and status (merged/open/closed) are the three most valuable axes. | MEDIUM | Outcomes page (precondition), client-side filter state in Preact component |
| Action card PR status badge (open/merged/closed) | Knowing a PR was created is useful. Knowing if it was merged is actionable feedback. A merged badge signals "someone accepted this." | LOW | GitHub API poll for PR status, existing ActionCard component — small addition |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Global parallel concurrency (all targets at once, no per-target isolation) | "Run everything simultaneously for maximum speed" | Different targets compete for the same CPU, same LLM API rate limits, and potentially the same repo paths. Unbounded parallelism hits API 429s and produces confused output. Current per-target isolation design is correct. | Keep per-target isolation model: different targets parallel, same target queued |
| Auto-merge PRs created by NW | "Full automation — why wait for review?" | NW creates proposals based on signals. Even high-confidence signals can be wrong in context. Auto-merge removes the human review step that is the safety net of the entire system. The ROADMAP.md explicitly calls out "human decides implementation." | Auto-create PR (visible, reviewable), never auto-merge. Show merge status back in dashboard. |
| Scheduling cron expressions | "I want 'every Monday at 9am', not just 'every 24h'" | Cron expressions require a parser, user-facing validation, and a UI (datetime picker or cron string input). The interval model covers 95% of use cases (every N hours). PROJECT.md explicitly lists "cron expressions" as Out of Scope. | Interval + enabled/disabled per target. If once-per-day is needed: interval_hours: 24 |
| Outcome analytics charts (trend lines, acceptance rate graphs) | "I want to see the flywheel in action visually" | Health page already has this at the indicator/proxy-signal level (sparklines, accept/reject trends). Duplicating at the outcomes level adds data that overlaps. Wait until the data model is proven before building analytics on top. | Phase 0.6 implementation outcome tracking gives the raw data. Chart layer is v3+ |
| Outcomes page with real-time push | "Update the outcomes as PRs merge" | Outcomes change on PR merge events which happen asynchronously (human reviewer action). Polling GitHub every 60s is fine for this signal — no user expects PR merge status to update in real-time in a local dashboard. | Poll PR status on outcomes page load + manual refresh button |
| Per-target auth tokens in UI | "I want to manage GitHub tokens per repo from the dashboard" | Schema prepared in TARGET type (`auth?: string`). The UI surface area to securely manage tokens in a browser (without exposing them in the DOM, handling storage safely) is significant. The use case is narrow — most users will share the same GH auth context. | Manage via YAML config directly. PROJECT.md lists this as Out of Scope. |

---

## Feature Dependencies

```
[Per-target scheduling]
    └──requires──> [AppConfig Target.schedule override field] (schema change)
    └──requires──> [Scheduler refactor: per-target setInterval map]
    └──enhances──> [Global schedule fallback] (targets without override use global)
    └──enables──> ["Next run at" per target card display]

[Parallel execution]
    └──requires──> [Per-target queue map] (replace single queue + currentRun with Map<targetName, {queue, current}>)
    └──requires──> [max_concurrent_runs schema change] (Zod literal(1) → min(1))
    └──requires──> [IPC state message update] (WorkerToServer state must carry per-target state)
    └──enables──> [Per-target status on dashboard] (concurrent running indicators)
    └──enables──> [Same-target queuing without blocking other targets]

[Auto-create PR]
    └──requires──> [gh CLI availability] (already used by feedback-collector.ts)
    └──requires──> [RunSummaryAction.branch field populated] (already in type, needs skill to set it)
    └──requires──> [Post-run PR creation step in executor.ts or skill]
    └──enables──> [Action card PR link] (pr_url already in type and rendered)
    └──enables──> [PR status badge on action card]

[Auto-create Linear issue]
    └──requires──> [Linear MCP tools in executor context] (already available via NW journal config)
    └──requires──> [signal.linear_issue_id populated in RunSummaryAction]
    └──enables──> [Action card Linear link]

[Outcomes aggregate page]
    └──requires──> [action cards with PR/Linear links populated] (auto-create features)
    └──requires──> [New /api/outcomes endpoint] (aggregate across all run summaries)
    └──requires──> [New frontend page: outcomes.ts]
    └──requires──> [Bottom nav update: add Outcomes tab]
    └──enables──> [Filter by target/status/date]

[NW-Claude outcomes awareness]
    └──requires──> [Outcomes stored in run summaries] (already in PerTargetSummary.actions)
    └──requires──> [MCP server new tool: get_outcomes] (server/services/mcp-tools.ts)
    └──enhances──> [Chat panel responses about recent PRs/issues]

[Implementation outcome tracking (Phase 0.6)]
    └──requires──> [Auto-create PR] (need pr_url to poll)
    └──requires──> [PR merge status polling] (gh pr view or GitHub API)
    └──requires──> [Indicator re-measurement after merge] (compare to Phase 0.5 baseline)
    └──requires──> [ImplementationOutcome type population] (type defined, not populated)
    └──enables──> [Health indicator trend correlation with specific PRs]
    └──note──> [Most complex v2 feature — can defer to Phase X if scope tightens]
```

### Dependency Notes

- **Parallel execution is the biggest architectural change.** The current single `queue: Run[]` and `currentRun: Run | null` model in `worker/index.ts` must become `Map<targetName, { queue: Run[], current: Run | null }>`. The IPC `state` message must carry per-target state. The dashboard polling must render per-target status. This is foundational — do it before per-target scheduling.
- **Per-target scheduling builds on parallel execution.** If targets can run in parallel, per-target schedules are meaningful. With serial execution, per-target scheduling would create queue pile-ups with no benefit.
- **Auto-create PR/Linear can be phased independently.** These don't depend on parallel execution. They depend on the nightwatch skill emitting `branch` and `linear_issue_id` fields in `RunSummaryAction`, and on a post-run creation step in executor.ts. This path is independent.
- **Outcomes page depends on auto-create (for data).** An outcomes page with no auto-created items is empty. Build auto-create first, then build the aggregate view.
- **Phase 0.6 is the deepest item.** It requires PR creation (precondition), merge polling, and indicator re-measurement. If scope tightens, defer Phase 0.6 to v2.1 — everything else ships without it.
- **`max_concurrent_runs: z.literal(1)`** is a Zod schema constraint. Changing to `z.number().min(1)` or removing and replacing with per-target logic requires updating `AppConfigSchema` in `types.ts` and the app config YAML schema validation.

---

## MVP Definition (v2.0 scope)

### Foundational (must ship first — others depend on these)

- [ ] **Parallel execution model** — per-target queue map, concurrent different-target runs, same-target queuing. Change `max_concurrent_runs: literal(1)` to per-target model. Update IPC state message. Update dashboard to show concurrent state.
- [ ] **Per-target scheduling** — add `schedule?: { enabled: boolean; interval_hours: number }` to Target config. Scheduler creates per-target timers. Global schedule is fallback for targets without override. 10-min floor enforced.

### Auto-Action (auto-create outputs)

- [ ] **Auto-create PR** — when `branch` is set on a `RunSummaryAction`, executor post-processing (or a new skill phase) calls `gh pr create`. Writes `pr_url` back into the action. No approval gate.
- [ ] **Auto-create Linear issue** — when nightwatch skill classifies a signal as `linear-issue`, the issue is created automatically (already happens in some skill paths — make it consistent). Write `linear_issue_id` back into the action.
- [ ] **Action card links** — `ActionCard` already renders `pr_url` as a "View PR" link. Add parallel `linear_url` link. Both are conditional on data presence.

### Visibility (surface outcomes)

- [ ] **Outcomes page** — new `/api/outcomes` endpoint aggregating actions across run summaries. New `outcomes.ts` page component. Bottom nav update. Filterable by target (client-side).
- [ ] **NW-Claude outcomes awareness** — add `get_outcomes` MCP tool to `mcp-tools.ts`. Chat can answer "what PRs did NW create this week?"
- [ ] **UI fix: bottom nav gap** — black line between content and nav bar (carried from v1.1, still open).

### Outcome Tracking (v2.0 stretch — defer to v2.1 if scope tightens)

- [ ] **Phase 0.6 implementation outcomes** — PR merge status polling, indicator re-measurement, `ImplementationOutcome` population, health page correlation display.

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Parallel execution model | HIGH (core v2 value prop) | HIGH | P1 — foundational |
| Per-target scheduling | HIGH (core v2 value prop) | MEDIUM | P1 — foundational |
| Auto-create PR | HIGH (closes output loop) | MEDIUM | P1 |
| Auto-create Linear issue | HIGH (closes output loop) | MEDIUM | P1 |
| Action card PR/Linear links | HIGH (visibility of outputs) | LOW | P1 — carry-over |
| Outcomes aggregate page | HIGH (aggregate visibility) | MEDIUM | P1 |
| NW-Claude outcomes awareness | MEDIUM (chat quality) | LOW | P1 |
| UI fix: bottom nav gap | LOW (cosmetic) | LOW | P1 — quick win |
| Phase 0.6 outcome tracking | HIGH (flywheel completion) | HIGH | P2 — stretch |
| Per-target "next run at" display | MEDIUM (UX quality) | LOW | P2 |
| PR status badge (open/merged) | MEDIUM (action card quality) | LOW | P2 |
| Outcomes filter by date range | LOW (advanced UX) | MEDIUM | P3 |

**Priority key:**
- P1: Ship in v2.0 phases
- P2: Ship if scope allows, otherwise v2.1
- P3: Future consideration

---

## Implementation Pattern Notes

### Parallel Execution Model

The key change is from a single slot model to a per-target slot map:

```typescript
// Current (worker/index.ts)
const queue: Run[] = []
let currentRun: Run | null = null

// v2.0 target
const perTargetState: Map<string, { queue: Run[]; current: Run | null }> = new Map()
```

The IPC `WorkerToServer` state message must carry this per-target map. The server exposes it via `/api/worker/state`. The dashboard polls this and renders each target's current state independently.

Concurrency ceiling: use `safety.yaml` to set `max_concurrent_targets` (e.g., 5). The worker checks the count of active runs across all targets before starting a new one. Same-target runs always queue.

### Per-Target Scheduling

Each target in `nightwatch-targets.yaml` gets an optional `schedule` block:
```yaml
targets:
  my-plugin:
    schedule:
      enabled: true
      interval_hours: 6
```

Targets without a `schedule` block fall back to the global `AppConfig.schedule`. The scheduler maintains a `Map<targetName, ReturnType<typeof setInterval>>` for per-target timers. On config reload (SIGHUP or API update), all timers are cleared and rebuilt.

### Auto-Create PR Flow

After a nightwatch run completes, `executor.ts` iterates `summary.per_target[name].actions` and for each action where `branch` is set but `pr_url` is not yet set:
1. Call `gh pr create --base main --head {branch} --title "{summary}" --body "..."` in the target's repo path
2. Parse the output URL, write it back to the action in the run's `summary.yaml`
3. Emit an IPC message so the server can notify the dashboard

This runs as a post-run step in executor.ts — no new worker needed.

### Outcomes API Design

`GET /api/outcomes` aggregates across run summaries:
- Reads `runs/*/summary.yaml` for all completed runs
- Extracts `per_target.*.actions` where `pr_url` or `linear_url` is set
- Returns a flat array sorted by run date
- Optional query params: `?target=X&status=open|merged&since=ISO_DATE`

The outcomes page fetches on mount and on manual refresh. No real-time push needed — this data changes only when runs complete.

### Phase 0.6 — Implementation Outcome Tracking

For each action with a `pr_url` that was previously recorded:
1. Call `gh pr view {pr_url} --json merged,mergedAt,state`
2. If merged: re-measure the indicator using the same Phase 0.5 measurement logic
3. Compare `after` vs `before` (from the original `IndicatorBaseline` for that run)
4. Write `ImplementationOutcome` to run summary
5. Surface in health page trend with annotation "PR merged, indicator moved from X to Y"

This is the highest-complexity v2 feature. The `ImplementationOutcome` type is already defined in `types.ts` — population is what's missing.

---

## Sources

- Codebase analysis: `app/shared/types.ts`, `app/worker/index.ts`, `app/worker/executor.ts`, `app/worker/scheduler.ts`, `app/server/routes/api.ts`, `app/frontend/components/action-card.ts` — HIGH confidence (direct read)
- PROJECT.md v2.0 requirements: `.planning/PROJECT.md` — HIGH confidence (authoritative)
- kc-nightwatch ROADMAP.md: `reference/ROADMAP.md` — HIGH confidence
- Parallel job dashboard patterns: [LogRocket — UI patterns for async workflows](https://blog.logrocket.com/ui-patterns-for-async-workflows-background-jobs-and-data-pipelines) — MEDIUM confidence
- Per-target scheduler reference implementations: [Cronicle](https://github.com/jhuckaby/Cronicle), [Dkron](https://dkron.io/) — MEDIUM confidence (similar domain, different scale)
- Outcome tracking patterns: [Linear + GitHub integration docs](https://linear.app/docs/github-integration), [DORA metrics background](https://www.browserstack.com/guide/software-engineering-metrics) — LOW confidence (general patterns, not exact domain)

---

*Feature research for: Nightwatch Dashboard v2.0 — Parallel Execution + Auto-Action*
*Researched: 2026-03-21*
