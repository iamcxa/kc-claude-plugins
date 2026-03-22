# Phase 11: Frontend Outcomes + UI Polish - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

The dashboard visually reflects parallel execution, all run detail views surface PR and Linear links, a dedicated Outcomes page aggregates all created PRs and issues, and the nav gap visual bug is gone. Backend is complete (Phase 10) — this is purely frontend + one new API endpoint.

</domain>

<decisions>
## Implementation Decisions

### Outcomes Page Layout
- **D-01:** List → detail split layout, same pattern as Runs page (left: filterable list, right: detail panel)
- **D-02:** Filter bar at top with 3 dropdowns: target, type (pr/linear_issue), status (open/merged/closed/completed/cancelled)
- **D-03:** Outcome cards in list show: type badge, target name, status dot, created date, truncated summary
- **D-04:** Detail panel shows: full title, target, URL (clickable → new tab), signal_id, run_id, status with live-check button, created_at

### Parallel Execution Visibility
- **D-05:** Sidebar status dots upgrade — color reflects real-time state from `active: Run[]` (running = green pulse, queued = yellow, idle = gray)
- **D-06:** Dashboard header adds summary line: "2 targets running · 1 queued" (derived from IPC state)
- **D-07:** No progress bars in sidebar — too narrow (240px); per-target phase progress stays in Runs detail panel

### Per-Target Schedule Display
- **D-08:** Target detail panel shows schedule info: "Schedule: every 24h (global) / every 6h (custom)" + "Next run: 15:30 (in 2h 15m)"
- **D-09:** Sidebar unchanged — no schedule text in target items (too narrow, most targets share global schedule)
- **D-10:** Global schedule bar unchanged — retains toggle + global countdown

### Action Card PR/Linear Enhancement
- **D-11:** Action card header gains status badge on right side: open (blue/accent), merged (green/success), closed (red/error)
- **D-12:** Expanded section shows clickable URL with `target="_blank"` — PR: "github.com/..." / Linear: "linear.app/..."
- **D-13:** Status uses **last-known** from outcomes.yaml — no per-card polling (avoids gh rate limit with many cards)
- **D-14:** Outcomes page is responsible for refreshing status (centralized polling), action cards read cached status

### Schedule in Add/Edit Target Wizard
- **D-15:** New step in wizard: "Schedule" — optional interval_hours input with "use global default" checkbox
- **D-16:** Minimum interval validation: same 10min floor as server-side (MIN_SCHEDULE_INTERVAL_HOURS)

### Nav Gap Fix
- **D-17:** Fix black line between content area and bottom nav — CSS border/gap issue in app.ts or bottom-nav.ts layout

### Bottom Nav Extension
- **D-18:** Add 5th tab "Outcomes" to bottom-nav.ts — route: `#/outcomes`
- **D-19:** Icon/label ordering: Dashboard, Runs, Outcomes, Health, Config

### Claude's Discretion
- Outcome card visual styling details (spacing, truncation length)
- Exact "next run" countdown format and refresh interval
- How to handle empty Outcomes page (no outcomes yet)
- Polling interval for Outcomes page status refresh (suggest 60s)
- Schedule step placement in wizard flow

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 10 outputs (backend ready)
- `app/server/services/outcome-store.ts` — readOutcomes, appendOutcome, queryOutcomes API
- `app/shared/types.ts` — OutcomeRecord interface (id, type, target, signal_id, run_id, url, branch?, status, created_at)
- `app/server/services/mcp-tools.ts` — nw_get_outcomes, nw_get_outcome_status, nw_outcome_summary tools

### Frontend patterns (copy from)
- `app/frontend/pages/runs.ts` — List → detail pattern, filter controls, hash sub-routing
- `app/frontend/components/action-card.ts` — Expandable card pattern, feedback buttons, confidence badges
- `app/frontend/components/sidebar.ts` — Target list with status dots and health arrows
- `app/frontend/components/bottom-nav.ts` — Tab navigation with hash routing
- `app/frontend/components/schedule-bar.ts` — Global schedule toggle and countdown
- `app/frontend/components/target-detail.ts` — Target detail panel with queue info
- `app/frontend/components/add-target-wizard.ts` — Multi-step wizard pattern

### Hooks and lib
- `app/frontend/lib/use-poll.ts` — Polling with SSE-triggered refresh
- `app/frontend/lib/use-toast.ts` — Toast notification system
- `app/frontend/lib/api.ts` — API client (needs new endpoints)
- `app/frontend/app.ts` — Hash router, page switching, layout structure

### Prior phase decisions (carry forward)
- Phase 8 CONTEXT.md — D-01 (flat IPC `active: Run[]`), D-05/D-06/D-07 (per-target schedule in targets.yaml)
- Phase 9 CONTEXT.md — D-07 (flat IPC arrays support multi-target), D-08/D-09 (multi-timer scheduler)
- Phase 10 CONTEXT.md — D-06 (OutcomeRecord schema), D-12/D-13/D-14 (MCP tool specs)

### Styling reference
- `app/frontend/index.html` — CSS variables (--bg, --panel, --border, --text, --accent, --success, --error, --warn)
- All components use inline styles with CSS variables — no external CSS files

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `runs.ts` list → detail pattern: exact blueprint for outcomes.ts page structure
- `action-card.ts` expand/collapse + feedback buttons: extend with status badge + URL link
- `sidebar.ts` statusDotColor(): upgrade to read from `active: Run[]` for multi-target status
- `usePoll` hook: reuse for outcomes data polling
- `schedule-bar.ts` countdown logic: adapt for per-target "next run" calculation in target-detail
- `add-target-wizard.ts` multi-step pattern: add schedule step

### Established Patterns
- Hash routing: `#/page` → `#/page/:id` for list → detail
- `useState` + `useEffect` for data fetching, `usePoll` for live updates
- Inline styles with CSS variables — no CSS classes
- HTM template literals: `html\`<div>...</div>\``
- API client: `api.getX().then(setX).catch(console.error)`

### Integration Points
- `app.ts` router: add `#/outcomes` case
- `bottom-nav.ts`: add 5th tab
- `sidebar.ts`: upgrade status dot logic from single-run to multi-run
- `target-detail.ts`: add schedule display section
- `action-card.ts`: add badge + link rendering
- `add-target-wizard.ts`: add schedule configuration step
- `api.ts`: add `getOutcomes()`, `getOutcomeStatus()` endpoints
- Server: add `GET /api/outcomes` and `GET /api/outcomes/:id/status` routes

</code_context>

<specifics>
## Specific Ideas

- Outcomes page follows Runs page split-panel pattern exactly — users already know the interaction
- Status badges use existing CSS variables: `--accent` (open), `--success` (merged/completed), `--error` (closed/cancelled)
- "Last-known status" approach avoids gh API rate limits — Outcomes page centralizes polling
- Bottom nav 5 tabs: Dashboard, Runs, Outcomes, Health, Config
- Parallel indicator is minimal (dot color + summary text) — avoids sidebar overload

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 11-frontend-outcomes-ui-polish*
*Context gathered: 2026-03-22*
