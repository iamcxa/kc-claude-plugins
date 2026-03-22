# Phase 11: Frontend Outcomes + UI Polish - Research

**Researched:** 2026-03-22
**Domain:** Preact + HTM frontend (Bun/Hono server), Nightwatch Dashboard
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** List → detail split layout for Outcomes page (same as Runs page)
- **D-02:** Filter bar with 3 dropdowns: target, type (pr/linear_issue), status
- **D-03:** Outcome cards show: type badge, target name, status dot, created date, truncated summary
- **D-04:** Detail panel shows: full title, target, URL (clickable), signal_id, run_id, status with live-check button
- **D-05:** Sidebar status dots reflect real-time state from `active: Run[]` (running = green pulse, queued = yellow, idle = gray)
- **D-06:** Dashboard header adds summary line: "2 targets running · 1 queued" derived from IPC state
- **D-07:** No progress bars in sidebar — 240px too narrow; phase progress stays in Runs detail panel
- **D-08:** Target detail panel shows schedule info + "Next run" countdown
- **D-09:** Sidebar unchanged — no schedule text in target items
- **D-10:** Global schedule bar unchanged
- **D-11:** Action card header gains status badge on right side: open/merged/closed colors
- **D-12:** Expanded section shows clickable URL with target="_blank"
- **D-13:** Status uses last-known from outcomes.yaml (no per-card polling)
- **D-14:** Outcomes page is responsible for refreshing status (centralized polling)
- **D-15:** New wizard step: "Schedule" — optional interval_hours with "use global default" checkbox
- **D-16:** Minimum interval validation: same 10min floor as MIN_SCHEDULE_INTERVAL_HOURS
- **D-17:** Fix black line between content area and bottom nav
- **D-18:** Add 5th tab "Outcomes" to bottom-nav.ts — route: `#/outcomes`
- **D-19:** Tab ordering: Dashboard, Runs, Outcomes, Health, Config

### Claude's Discretion

- Outcome card visual styling details (spacing, truncation length)
- Exact "next run" countdown format and refresh interval
- How to handle empty Outcomes page (no outcomes yet)
- Polling interval for Outcomes page status refresh (suggest 60s)
- Schedule step placement in wizard flow

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PARA-04 | Dashboard shows per-target running status with independent progress when multiple targets execute simultaneously | sidebar.ts statusDotColor() upgrade + dashboard.ts header summary line from IPC `active: Run[]` |
| SCHED-06 | Each target card displays its own "next run at" timestamp based on its individual schedule | target-detail.ts new Schedule section; Target.schedule?.interval_hours already in types.ts |
| SCHED-07 | Add/Edit Target wizard includes schedule configuration step | add-target-wizard.ts step 4 insertion; buildTarget() must include schedule field |
| AUTO-04 | Action cards display PR status badge (open/merged/closed) via last-known status from outcomes.yaml | action-card.ts header badge; no per-card polling (cached from Outcomes page) |
| OUT-01 | Action cards show clickable PR URL and Linear issue link in run detail | action-card.ts expanded section; OutcomeRecord.url lookup by signal_id |
| OUT-02 | Dedicated Outcomes page listing all NW-created PRs and Linear issues, filterable by target and status | new outcomes.ts page + two new API routes + api.ts extension |
| OUT-04 | Phase 0.6 implementation outcome tracking — poll merged PR status, record effectiveness | OutcomeRecord type already exists; GET /api/outcomes/:id/status calls gh pr view or Linear API |
| UI-01 | Fix bottom nav gap (black line between content area and navigation bar) | app.ts line 123: `padding-bottom: 48px` → `margin-bottom: 48px` on middle flex child |
</phase_requirements>

---

## Summary

Phase 11 is entirely frontend + one new API endpoint pair. Phase 10 delivered the backend (outcome-store.ts, OutcomeRecord type, queryOutcomes, mcp-tools). This phase connects that backend to the UI in three areas: (1) a new Outcomes page with split-panel layout mirroring runs.ts, (2) surfacing outcome status on existing action-cards and target-detail, and (3) a set of small polish items (sidebar parallel dots, dashboard header summary, wizard schedule step, nav gap fix).

Every file to modify already exists and has been read. No new architectural patterns are needed — the work is purely additive: new page (outcomes.ts), new route file (outcomes.ts in routes/), two API methods in api.ts, and targeted modifications to five existing components. The UI-SPEC.md is detailed and approved, providing exact pixel values, copy strings, and color assignments — no design research needed.

The single non-trivial design question is how action-card.ts receives outcome data (since it cannot poll per-card). The decision is already locked: outcomes are passed as props from the Runs page, which pre-fetches from the Outcomes page cache. This requires a prop signature change on ActionCard and a pre-fetch call in runs.ts.

**Primary recommendation:** Implement in two plans — Plan A (Outcomes page + API routes + action-card enhancements) and Plan B (sidebar dots, dashboard summary, target-detail schedule, wizard schedule step, nav gap fix). Plan A is the high-value new surface; Plan B is polish/extension of existing components.

---

## Standard Stack

### Core (already installed — no new dependencies)

| Library | Version | Purpose | Notes |
|---------|---------|---------|-------|
| Preact | vendored | UI component model | `html` from htm/preact |
| htm | vendored | Tagged template JSX alternative | `html\`` template literals |
| @preact/signals | vendored | Reactive state (refreshTrigger) | Used in use-poll.ts |
| Hono | ^4.12.8 | Server routing | New outcomes routes follow existing pattern |
| Bun | runtime | Test runner (`bun test`) | Tests in `app/tests/server/` |

**No new packages required.** All UI work uses existing vendored libraries and inline styles.

---

## Architecture Patterns

### Project File Organization

```
app/
├── frontend/
│   ├── pages/
│   │   ├── runs.ts            # BLUEPRINT for outcomes.ts
│   │   ├── dashboard.ts       # MODIFY: add parallel summary
│   │   └── outcomes.ts        # CREATE: new page
│   ├── components/
│   │   ├── action-card.ts     # MODIFY: status badge + URL
│   │   ├── sidebar.ts         # MODIFY: multi-run status dots
│   │   ├── bottom-nav.ts      # MODIFY: 5th tab
│   │   ├── target-detail.ts   # MODIFY: schedule section
│   │   └── add-target-wizard.ts  # MODIFY: step 4 schedule
│   ├── lib/
│   │   └── api.ts             # MODIFY: getOutcomes, getOutcomeStatus
│   ├── app.ts                 # MODIFY: #/outcomes route + nav gap fix
│   └── index.html             # NO CHANGE (CSS vars sufficient)
├── server/
│   ├── routes/
│   │   └── outcomes.ts        # CREATE: GET /api/outcomes, GET /api/outcomes/:id/status
│   └── index.ts               # MODIFY: register outcomesRoutes
└── tests/server/
    └── outcomes-api.test.ts   # CREATE: route tests
```

### Pattern 1: Hash Router Extension (app.ts)

The existing router is a simple `getPage()` function returning a `Page` union type. Adding `#/outcomes` requires:

1. Extend `type Page` to include `'outcomes'`
2. Add `if (hash.startsWith('#/outcomes')) return 'outcomes'` in `getPage()`
3. Add `import { Outcomes } from './pages/outcomes.ts'` at top
4. Add render branch: `${page === 'outcomes' && html\`<${Outcomes} />\`}`
5. Fix nav gap: line 123 change `padding-bottom:48px` to `margin-bottom:48px`

**Nav gap root cause (confirmed from source):** `app.ts` line 123 uses `padding-bottom: 48px` on the flex child that contains all pages. The BottomNav is `position:fixed;bottom:0` with `border-top:1px solid var(--border)`. The padding-bottom creates space BEHIND the fixed nav, but the border of the fixed nav overlaps the padding edge, producing a visible 1px line. Changing to `margin-bottom: 48px` pushes the content above the nav without creating a painted surface behind the nav's border.

```typescript
// Source: app/frontend/app.ts line 121-128 (current)
return html`
  <div style="display:flex;flex-direction:column;height:100%;overflow:hidden;">
    <${ScheduleBar} schedule=${schedule} onToggle=${handleScheduleToggle} />
    <div style="flex:1;overflow:hidden;padding-bottom:48px;">  // ← BUG
    // Fix: margin-bottom:48px (removes painted surface behind nav border)
```

### Pattern 2: List→Detail Split Panel (outcomes.ts from runs.ts blueprint)

`runs.ts` is the exact blueprint. Key structural elements to replicate:

- `useState<OutcomeRecord[]>([])` + `useState<string | null>(null)` for selection
- `useCallback` wrapping `loadOutcomes` to avoid stale closures
- `usePoll(loadOutcomes, 60_000, true)` — always poll (not gated on active runs)
- Filter bar: `padding:12px 16px`, 3 `<select>` elements with `onChange` handlers
- List: `flex:1;overflow-y:auto`, each item `onClick` sets selected ID
- Detail panel: conditional render on `selectedId` — `if (selectedId && selectedOutcome)`

The split-panel structure for the list view (no selection active) matches exactly:
```typescript
// Outer: height:100%;display:flex;flex-direction:column;overflow:hidden
// Filter bar: border-bottom + flex-shrink:0
// List: flex:1;overflow-y:auto
// When selectedId: full-height detail replaces split (same as runs.ts lines 108–196)
```

### Pattern 3: Sidebar Status Dots Upgrade

Current `statusDotColor(run: Run | undefined)` takes a single last run. The upgrade adds `active: Run[]` from IPC state as a second parameter, with this logic order:

1. Check `active.filter(r => r.target === target.name)` — if any `running` → accent + pulse
2. If any `queued` → warn (no pulse)
3. Fallback to existing `lastRun` color logic

The `pulse` keyframe is already defined in `index.html` (line 92–95: `@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }`).

```typescript
// Dot element: add animation inline style when running
<div style="width:8px;height:8px;border-radius:50%;
  background:${dotColor};
  flex-shrink:0;
  ${isRunning ? 'animation:pulse 1.5s ease-in-out infinite;' : ''}
" title=${...}></div>
```

`active: Run[]` is already available in `dashboard.ts` via `api.getWorkerState().then(state => setWorkerQueue(state.queue))` — the state also returns `active: Run[]`. The Dashboard currently only reads `state.queue` — it must also read `state.active` and pass it to `Sidebar`.

### Pattern 4: ActionCard Outcome Status

The challenge: ActionCard currently has `Props { action, target, runId, existingFeedback }`. It needs outcome status for the action's `signal_id`. Options per locked decisions:

- **D-13 says:** status uses last-known from outcomes.yaml — no per-card fetch
- **D-14 says:** Outcomes page is responsible for refreshing status

This means ActionCard gets a new optional prop: `outcomeStatus?: { status: OutcomeRecord['status']; url: string } | null`. The Runs page fetches all outcomes once and passes down the relevant entry per action.

```typescript
// In runs.ts: fetch outcomes map
const [outcomesMap, setOutcomesMap] = useState<Record<string, OutcomeRecord>>({})
// Load outcomes keyed by signal_id
api.getOutcomes().then(list => {
  const map = Object.fromEntries(list.map(o => [o.signal_id, o]))
  setOutcomesMap(map)
}).catch(console.error)

// Pass to ActionCard:
<${ActionCard}
  action=${action}
  target=${targetName}
  runId=${selectedId}
  outcomeStatus=${outcomesMap[action.signal_id] ?? null}
/>
```

ActionCard header: insert status badge between type chip and confidence label (line 47-48 currently).

### Pattern 5: Server Route Addition

New file `app/server/routes/outcomes.ts` following `api.ts` pattern:

```typescript
import { Hono } from 'hono'
import { queryOutcomes, readOutcomes } from '../services/outcome-store.ts'
import type { OutcomeRecord } from '../../shared/types.ts'

export const outcomesRoutes = new Hono()

// GET /api/outcomes — filterable list
outcomesRoutes.get('/api/outcomes', async (c) => {
  const target = c.req.query('target')
  const type = c.req.query('type')
  const status = c.req.query('status')
  const records = await queryOutcomes({
    target: target ?? undefined,
    type: type ?? undefined,
    status: status ?? undefined,
  })
  return c.json(records)
})

// GET /api/outcomes/:id/status — single outcome status refresh
// Looks up gh pr view for PR type, or returns cached for linear_issue
outcomesRoutes.get('/api/outcomes/:id/status', async (c) => {
  const id = c.req.param('id')
  const records = await readOutcomes()
  const record = records.find(r => r.id === id)
  if (!record) return c.json({ error: 'not found' }, 404)
  // Return current cached status (live gh check is done by worker, not this endpoint)
  return c.json({ status: record.status })
})
```

Register in `server/index.ts`:
```typescript
import { outcomesRoutes } from './routes/outcomes.ts'
// After existing route registrations:
app.route('/', outcomesRoutes)
```

### Pattern 6: Wizard Step Insertion (4 → 5 steps)

Current wizard: 4 steps, dots rendered as `[1,2,3,4].map(...)`. Insert schedule step as step 4 (preview becomes step 5):

1. Change dot render to `[1,2,3,4,5].map(...)`
2. Add state: `const [useGlobalSchedule, setUseGlobalSchedule] = useState(true)` and `const [customIntervalHours, setCustomIntervalHours] = useState('')`
3. Rename existing step 4 check to `step === 5` in JSX
4. Change `step < 4` to `step < 5` in navigation buttons
5. Change `step === 4` to `step === 5` for "Validate & Save"
6. Add schedule validation before advancing from step 4 to step 5
7. Update `buildTarget()` to include schedule field if !useGlobalSchedule

```typescript
// In buildTarget():
...((!useGlobalSchedule && customIntervalHours) ? {
  schedule: { interval_hours: parseFloat(customIntervalHours) }
} : {}),
```

### Pattern 7: Target Detail Schedule Section

Schedule data is already in `Target.schedule?.interval_hours` (types.ts line 16-18). Global interval is available if passed as prop or fetched via `api.getSchedule()`.

The countdown logic mirrors `schedule-bar.ts` exactly but uses `lastRun.started_at + interval_hours` as the base (not "now"):

```typescript
// Countdown from last run start time
const lastRunMs = lastRun?.started_at ? new Date(lastRun.started_at).getTime() : null
const intervalMs = effectiveIntervalHours * 3_600_000
const nextRunMs = lastRunMs ? lastRunMs + intervalMs : null
// Remaining = nextRunMs - Date.now()
```

`TargetDetail` currently receives `lastRun` as a prop. It needs `globalSchedule?: ScheduleConfig` added — the simplest approach is to add it to the Dashboard's data fetch and pass down, OR fetch it inside target-detail with `api.getSchedule()` on mount.

### Anti-Patterns to Avoid

- **Per-card outcome polling:** D-13 explicitly prohibits this. ActionCard must read from props, not fetch.
- **Modifying BottomNav type from outside:** The `Page` type is defined in both `app.ts` and `bottom-nav.ts` independently — both must be updated.
- **Forgetting to register outcomesRoutes in server/index.ts:** Pattern is consistent across all route files.
- **Wizard step renumbering off-by-one:** Existing step 4 conditional `step === 4` must become `step === 5`; `step < 4` becomes `step < 5`. Missing any one causes broken navigation.
- **padding-bottom vs margin-bottom on nav gap:** `padding-bottom` paints a surface behind the fixed nav; `margin-bottom` creates space without a painted surface.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Outcome status refresh | Custom polling per-card | `usePoll(loadOutcomes, 60_000, true)` in Outcomes page | D-13/D-14 locked decision; gh rate limit |
| Schedule countdown | New timer system | Adapt `schedule-bar.ts` pattern (useEffect + setInterval(60_000)) | Already battle-tested in codebase |
| Filter state management | Custom filter reducer | `useState('')` per filter + inline filter function | Established pattern in runs.ts |
| Status colors | New color palette | Existing CSS variables (`--accent`, `--success`, `--error`, `--warn`, `--muted`) | Design system defined in UI-SPEC.md |
| Pulse animation | New keyframe | Existing `@keyframes pulse` in index.html | Already defined, already works |
| Hash sub-routing for outcomes | React Router / custom router | Simple `location.hash = '#/outcomes'` + `hashchange` listener | Established pattern in runs.ts |

---

## Common Pitfalls

### Pitfall 1: Double Page Type Definition

**What goes wrong:** `type Page` is defined independently in `app.ts` (line 16) AND `bottom-nav.ts` (line 3). Adding `'outcomes'` to only one causes TypeScript type errors or runtime mismatches.

**How to avoid:** Update both files when adding `'outcomes'` to Page type.

**Warning signs:** TypeScript error `Argument of type '"outcomes"' is not assignable to parameter of type Page` in one of the two files.

### Pitfall 2: OutcomesMap Not Passed to ActionCard

**What goes wrong:** If Runs page doesn't pre-fetch outcomes and pass them to ActionCard, the badge and URL link silently don't render (no prop → no badge). Looks "done" in tests but status badges never appear.

**How to avoid:** In runs.ts, add `loadOutcomes()` call alongside `loadRuns()`, build a `signal_id → OutcomeRecord` map, and pass `outcomeStatus` to every ActionCard.

**Warning signs:** Action cards render without status badges; no error in console because `outcomeStatus` is optional and defaults to null rendering.

### Pitfall 3: Wizard Step Number Off-by-One

**What goes wrong:** Adding step 4 (schedule) pushes preview to step 5, but if the condition `step === 4` for "Preview" and `step < 4` for "Next" are missed, the wizard skips the preview or shows both schedule and preview simultaneously.

**How to avoid:** Systematically replace ALL occurrences: `step === 4` → `step === 5`, `step < 4` → `step < 5` (navigation), dot render `[1,2,3,4]` → `[1,2,3,4,5]`.

**Warning signs:** Wizard shows wrong step count; "Validate & Save" appears on wrong step.

### Pitfall 4: active[] vs queue[] Confusion in Dashboard

**What goes wrong:** `api.getWorkerState()` returns `{ queue: Run[], active: Run[] }`. Dashboard currently only destructures `state.queue`. If `state.active` isn't also extracted and passed to Sidebar, the dot upgrade has no data.

**How to avoid:** In dashboard.ts `loadRuns()`, extract both: `const { queue, active } = state`. Add `activeRuns` state variable and pass to Sidebar as new prop.

**Warning signs:** Sidebar dots never show running/queued colors even during active runs.

### Pitfall 5: outcomesRoutes Not Registered in server/index.ts

**What goes wrong:** Creating `routes/outcomes.ts` but forgetting the `app.route('/', outcomesRoutes)` line in `server/index.ts` causes 404 on all `/api/outcomes` calls. No error at startup.

**How to avoid:** Check server/index.ts imports and route registrations immediately after creating the new route file.

### Pitfall 6: Global Schedule Unavailable in Target Detail

**What goes wrong:** Target detail schedule section needs `effectiveIntervalHours`. If `target.schedule?.interval_hours` is undefined (global schedule applies), it needs the global schedule value. If not fetched/passed, "Every Xh (global)" shows "Every undefinedh (global)".

**How to avoid:** Either pass `globalSchedule: ScheduleConfig` as prop to TargetDetail from Dashboard (which already fetches `api.getSchedule()`), or add a `useEffect` + `api.getSchedule()` call inside TargetDetail. Passing as prop is simpler and avoids duplicate fetching.

---

## Code Examples

### Outcomes Page Structure (from runs.ts blueprint)

```typescript
// Source: app/frontend/pages/runs.ts (full file read)
export function Outcomes() {
  const [outcomes, setOutcomes] = useState<OutcomeRecord[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [targetFilter, setTargetFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const loadOutcomes = useCallback(() => {
    api.getOutcomes().then(setOutcomes).catch(console.error)
  }, [])

  useEffect(() => { loadOutcomes() }, [])
  usePoll(loadOutcomes, 60_000, true)  // always poll — outcome status changes async

  const filtered = outcomes.filter(o => {
    if (targetFilter && o.target !== targetFilter) return false
    if (typeFilter && o.type !== typeFilter) return false
    if (statusFilter && o.status !== statusFilter) return false
    return true
  })
  // ...split panel render
}
```

### Status Dot Color with Pulse

```typescript
// Source: adapted from app/frontend/components/sidebar.ts statusDotColor()
function statusDotColor(
  targetName: string,
  lastRun: Run | undefined,
  activeRuns: Run[]
): { color: string; animate: boolean } {
  const targetActive = activeRuns.filter(r => r.target === targetName)
  if (targetActive.some(r => r.status === 'running')) {
    return { color: 'var(--accent)', animate: true }
  }
  if (targetActive.some(r => r.status === 'queued')) {
    return { color: 'var(--warn)', animate: false }
  }
  // fallback to last run
  if (!lastRun) return { color: 'var(--muted)', animate: false }
  const colors: Record<string, string> = {
    completed: 'var(--success)',
    failed: 'var(--error)',
    running: 'var(--accent)',
    queued: 'var(--warn)',
    cancelled: 'var(--muted)',
  }
  return { color: colors[lastRun.status] ?? 'var(--muted)', animate: false }
}
```

### Action Card Status Badge (header)

```typescript
// Source: based on app/frontend/components/action-card.ts line 47
// Insert between type chip and confidence label
${outcomeStatus && html`
  <span style="
    padding:2px 6px;border-radius:4px;font-size:11px;font-weight:600;
    background:${badgeBg(outcomeStatus.status)};
    color:${badgeColor(outcomeStatus.status)};
  ">${badgeText(outcomeStatus.status)}</span>
`}
// Where:
const badgeBg = (s: OutcomeRecord['status']) => ({
  open:      'rgba(88,166,255,0.15)',
  merged:    'rgba(63,185,80,0.15)',
  completed: 'rgba(63,185,80,0.15)',
  closed:    'rgba(248,81,73,0.15)',
  cancelled: 'rgba(139,148,158,0.15)',
}[s] ?? 'transparent')
```

### API Client Extension

```typescript
// Source: based on app/frontend/lib/api.ts
getOutcomes(filter?: { target?: string; type?: string; status?: string }): Promise<OutcomeRecord[]> {
  const params = new URLSearchParams()
  if (filter?.target) params.set('target', filter.target)
  if (filter?.type) params.set('type', filter.type)
  if (filter?.status) params.set('status', filter.status)
  const qs = params.toString()
  return get<OutcomeRecord[]>(`/api/outcomes${qs ? `?${qs}` : ''}`)
},

getOutcomeStatus(id: string): Promise<{ status: OutcomeRecord['status'] }> {
  return get<{ status: OutcomeRecord['status'] }>(`/api/outcomes/${id}/status`)
},
```

### Dashboard Parallel Summary

```typescript
// Source: 11-UI-SPEC.md section 4
// Insert between ScheduleBar and main split div in app.ts render
${(() => {
  const running = activeRuns.filter(r => r.status === 'running').length
  const queued = activeRuns.filter(r => r.status === 'queued').length
  if (running === 0 && queued === 0) return null
  return html`
    <div style="padding:6px 16px;border-bottom:1px solid var(--border);background:var(--panel);font-size:12px;color:var(--muted);flex-shrink:0;">
      ${running > 0 && html`
        <span style="color:var(--success);">${running}</span>
        <span> target${running !== 1 ? 's' : ''} running</span>
      `}
      ${running > 0 && queued > 0 && html`<span> · </span>`}
      ${queued > 0 && html`
        <span style="color:var(--warn);">${queued}</span>
        <span> queued</span>
      `}
    </div>
  `
})()}
```

---

## Validation Architecture

> nyquist_validation is enabled (config.json).

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Bun test (built-in) |
| Config file | none — Bun discovers `app/tests/**/*.test.ts` automatically |
| Quick run command | `cd /Users/kent/Project/kc-claude-workspace/kc-claude-plugins/kc-nightwatch/app && bun test tests/server/outcomes-api.test.ts` |
| Full suite command | `cd /Users/kent/Project/kc-claude-workspace/kc-claude-plugins/kc-nightwatch/app && bun test` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| OUT-02 | GET /api/outcomes returns filterable list | unit (route) | `bun test tests/server/outcomes-api.test.ts` | ❌ Wave 0 |
| OUT-04 | GET /api/outcomes/:id/status returns cached status | unit (route) | `bun test tests/server/outcomes-api.test.ts` | ❌ Wave 0 |
| PARA-04 | Sidebar statusDotColor() returns accent + animate for running target | unit (component logic) | `bun test tests/server/outcomes-api.test.ts` | ❌ Wave 0 (or inline in route test) |
| SCHED-06 | Schedule section renders "Every Xh" with fallback | manual visual | n/a — frontend Preact component | manual |
| SCHED-07 | Wizard step 4 validates interval floor | manual visual | n/a — frontend Preact component | manual |
| AUTO-04 | Action card renders status badge from prop | manual visual | n/a — frontend Preact component | manual |
| OUT-01 | Action card renders clickable URL from outcomeStatus prop | manual visual | n/a — frontend Preact component | manual |
| UI-01 | No black line between content and nav | manual visual | n/a — CSS layout | manual |

### Sampling Rate

- **Per task commit:** `bun test tests/server/outcomes-api.test.ts -t "GET /api/outcomes"`
- **Per wave merge:** `bun test` (full suite — currently ~471 tests across 23 files)
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `app/tests/server/outcomes-api.test.ts` — covers OUT-02 (GET /api/outcomes filter), OUT-04 (GET /api/outcomes/:id/status), and route 404 behavior
- [ ] Framework already installed — no setup needed

*(Existing test infrastructure: bun test, 23 test files, outcome-store.test.ts already exists as reference)*

---

## Open Questions

1. **Does `GET /api/outcomes/:id/status` need to trigger a live `gh pr view` call?**
   - What we know: D-13 says "last-known status"; D-14 says Outcomes page is responsible for refreshing. The UI-SPEC says "Check status" button calls this endpoint.
   - What's unclear: Should this endpoint return only cached status, or actively call `gh` to refresh?
   - Recommendation: Return cached status only for the endpoint. The "Check status" button's value is that it triggers a fresh read from the YAML (after a potential background update). A live `gh` call in a frontend-facing route would introduce latency and auth complexity. If live checking is needed, it can be a Phase 11.1 enhancement.

2. **Should `activeRuns` be managed in App (app.ts) or Dashboard?**
   - What we know: Dashboard fetches `api.getWorkerState()` in `loadRuns()`. App.ts doesn't currently fetch worker state.
   - What's unclear: The parallel summary line (D-06) is described as being on the "Dashboard header" — is it inside Dashboard.ts or in App.ts above Dashboard?
   - Recommendation: Keep it in Dashboard.ts. The summary line is in the dashboard page context, not a global layout element. Dashboard already has `workerQueue` and `hasActiveRuns` state — add `activeRuns` state alongside.

3. **`summary` field on OutcomeRecord?**
   - What we know: OutcomeRecord type (types.ts lines 216-226) does NOT have a `summary` field. The UI-SPEC says outcome list items show "truncated summary."
   - What's unclear: What text serves as the summary? The URL? The `signal_id`?
   - Recommendation: Use the URL as the display summary (truncated to 60 chars) since OutcomeRecord has no title/summary field. Or use `type + target` as the natural summary. Confirm in Plan A.

---

## Sources

### Primary (HIGH confidence)

- Direct source code read — `app/frontend/pages/runs.ts` (blueprint for outcomes.ts)
- Direct source code read — `app/frontend/components/action-card.ts` (badge extension target)
- Direct source code read — `app/frontend/components/sidebar.ts` (statusDotColor upgrade target)
- Direct source code read — `app/frontend/components/bottom-nav.ts` (5th tab target)
- Direct source code read — `app/frontend/components/target-detail.ts` (schedule section target)
- Direct source code read — `app/frontend/components/add-target-wizard.ts` (step 4 insertion target)
- Direct source code read — `app/frontend/app.ts` (router + nav gap root cause confirmed at line 123)
- Direct source code read — `app/frontend/lib/api.ts` (extension pattern)
- Direct source code read — `app/frontend/lib/use-poll.ts` (polling hook interface)
- Direct source code read — `app/server/services/outcome-store.ts` (backend API — Phase 10 complete)
- Direct source code read — `app/shared/types.ts` (OutcomeRecord type confirmed)
- Direct source code read — `app/server/routes/api.ts` (route registration pattern)
- Direct source code read — `app/server/index.ts` (route registration — app.route('/', X) pattern)
- Direct source code read — `app/frontend/index.html` (CSS variables, pulse keyframe confirmed)
- Direct source code read — `.planning/phases/11-frontend-outcomes-ui-polish/11-UI-SPEC.md` (approved design contract)
- Direct source code read — `.planning/phases/11-frontend-outcomes-ui-polish/11-CONTEXT.md` (locked decisions)

### Secondary (MEDIUM confidence)

- Inferred from codebase patterns — nav gap root cause (padding-bottom vs margin-bottom)
- Inferred from OutcomeRecord schema — "summary" field gap (not in type, UI-SPEC references it)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries already vendored/installed, confirmed from package.json and index.html
- Architecture patterns: HIGH — all derived from direct source code reads, not assumptions
- Pitfalls: HIGH — derived from actual code inspection (nav gap confirmed from line 123, double Page type confirmed from two files)
- Open questions: MEDIUM — flagged gaps that require plan-level decisions

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable codebase, no fast-moving dependencies)
