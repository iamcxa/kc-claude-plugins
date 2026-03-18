---
phase: 03-flywheel-core
plan: 02
subsystem: ui
tags: [config-editor, yaml, hono, preact, haiku, write-lock, wizard]

# Dependency graph
requires:
  - phase: 03-01
    provides: "Chat system, global SSE, frontend lib/api.ts, shared/types.ts ConfigValidationResult"
  - phase: 02-core-cockpit
    provides: "Frontend component patterns (TriggerDialog modal), yaml-store.ts utilities"
provides:
  - "Config page: Targets/Safety tabs with YAML editor and 4-step validation flow"
  - "config-validator.ts: validateConfigSave (static YAML -> Haiku semantic -> diff -> ready)"
  - "config routes: GET/PUT /api/config/:file, GET /api/config/warnings, add/edit/remove targets"
  - "AddTargetWizard: 4-step modal for create/edit targets"
  - "Remove Target confirm dialog (alertdialog)"
  - "write lock via withWriteLock for concurrent safety"
affects: [03-03, 03-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Write lock pattern: in-memory Map<string, Promise<void>> serializes concurrent YAML writes per file"
    - "Fail-open semantic validation: Haiku check failure allows save with WARN verdict (never blocks)"
    - "Route ordering: /api/config/warnings before /api/config/:file to prevent param capture"
    - "JSON preview in frontend wizard: YAML stringify not available in browser; JSON.stringify as preview"

key-files:
  created:
    - app/server/services/config-validator.ts
    - app/server/routes/config.ts
    - app/frontend/pages/config.ts (replaced placeholder)
    - app/frontend/components/add-target-wizard.ts
    - app/tests/server/config-validator.test.ts
    - app/tests/server/config-editor.test.ts
    - app/tests/server/target-wizard.test.ts
  modified:
    - app/server/index.ts (added configRoutes)
    - app/frontend/lib/api.ts (added 7 config methods)

key-decisions:
  - "Write lock per file (in-memory Map) serializes concurrent config writes — prevents race corruption"
  - "Fail-open for Haiku semantic check: if API unavailable, warn but allow save — config editor must never be blocked by LLM availability"
  - "/api/config/warnings route registered before /api/config/:file — Hono param routes are greedy"
  - "Wizard Step 4 uses JSON.stringify preview (not YAML) — yaml package is server-side only, not available in browser bundle"

patterns-established:
  - "Modal wizard pattern: 4 steps with dot progress indicator, Back/Next/action buttons, pre-fill for edit mode"
  - "alertdialog for destructive confirm vs dialog for constructive forms"

requirements-completed: [CONF-01, CONF-02, CONF-03, CONF-04, CONF-05, CONF-06, CONF-07, CONF-08]

# Metrics
duration: 18min
completed: 2026-03-18
---

# Phase 3 Plan 02: Config Editor Summary

**YAML config editor with 4-step Haiku validation, write-lock concurrency safety, and 4-step AddTargetWizard modal — replaces Phase 3 placeholder**

## Performance

- **Duration:** 18 min
- **Started:** 2026-03-18T10:41:00Z
- **Completed:** 2026-03-18T10:59:00Z
- **Tasks:** 3
- **Files modified:** 9 (2 modified, 7 created)

## Accomplishments

- Config validation service with 4-step flow: static YAML parse -> Haiku semantic check ($0.05 cap, max_tokens 200) -> line diff -> ready
- Full config page replacing placeholder: Targets/Safety tabs, YAML editor with edit lock, 4-step inline validation, amber warnings from self-repair.yaml
- AddTargetWizard 4-step modal for create/edit (type+name -> north star -> monitors/respond -> preview), Remove Target confirm dialog
- Write lock (in-memory Promise chain per file) prevents concurrent YAML corruption
- All 140 tests pass (up from 104 at start of Phase 3)

## Task Commits

1. **Task 1: Config validation service + config API routes + tests** - `79b217f` (feat)
2. **Task 2: Config page UI (tabs, YAML editor, edit lock, 4-step validation, warnings)** - `8962e61` (feat)
3. **Task 3: AddTargetWizard + Edit/Remove target flows + Config page integration** - `c701377` (feat)

## Files Created/Modified

- `app/server/services/config-validator.ts` — validateConfigSave (4-step flow), withWriteLock
- `app/server/routes/config.ts` — GET/PUT /api/config/:file, GET /api/config/warnings, add/edit/remove targets
- `app/server/index.ts` — registered configRoutes
- `app/frontend/lib/api.ts` — getConfig, validateConfig, saveConfig, getConfigWarnings, addTarget, editTarget, removeTarget
- `app/frontend/pages/config.ts` — full Config component (was placeholder)
- `app/frontend/components/add-target-wizard.ts` — AddTargetWizard 4-step modal
- `app/tests/server/config-validator.test.ts` — 5 tests for validateConfigSave and withWriteLock
- `app/tests/server/config-editor.test.ts` — 2 tests for config route setup
- `app/tests/server/target-wizard.test.ts` — 3 tests for YAML generation logic

## Decisions Made

- Write lock per file key (not global) — allows targets and safety to write concurrently with each other, but serializes writes to the same file
- Fail-open for Haiku: Haiku unavailable → WARN verdict, save proceeds — config editor is not gated by LLM availability
- Route ordering fix: /api/config/warnings before /api/config/:file — Hono matches param routes greedily; warnings would have been captured as `file=warnings`
- JSON.stringify preview in wizard Step 4 — yaml package is server-side; browser frontend has no YAML serializer in import map

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed withWriteLock return type error — resolve! non-null assertion**
- **Found during:** Task 1 (config-validator.ts creation)
- **Issue:** Plan code used `resolve!()` (definite assignment assertion) which is valid but TypeScript strict may flag. Used explicit initialization pattern instead.
- **Fix:** Changed `let resolve: () => void` + `resolve = r` to `let resolve!: () => void` matching strict initialization
- **Files modified:** app/server/services/config-validator.ts
- **Verification:** Tests pass (withWriteLock serialization test verifies correct ordering)
- **Committed in:** 79b217f

**2. [Rule 1 - Bug] Fixed configRoutes add/edit/remove returning early from withWriteLock**
- **Found during:** Task 1 (config routes creation)
- **Issue:** Plan code used `return c.json(...)` inside `withWriteLock` callback — but withWriteLock returns `T`, not a Hono Response. The `return` inside the callback exits the callback, not the route handler.
- **Fix:** Used flag variables (`conflict`, `notFound`) inside callbacks, check flags after lock resolves, then return from route handler
- **Files modified:** app/server/routes/config.ts
- **Verification:** Route logic correct — no false 409/404 errors
- **Committed in:** 79b217f

**3. [Rule 1 - Bug] Fixed config-editor.test.ts — removed require() in favor of direct import**
- **Found during:** Task 1 (test file creation)
- **Issue:** Plan used CommonJS `require()` for TARGETS_YAML_PATH, but Bun test environment uses ESM
- **Fix:** Changed to direct ES import at top of file
- **Files modified:** app/tests/server/config-editor.test.ts
- **Verification:** Test passes (TARGETS_YAML_PATH resolves correctly)
- **Committed in:** 79b217f

**4. [Rule 1 - Bug] Fixed SAFETY_YAML_PATH using import.meta.dir**
- **Found during:** Task 1 (config routes)
- **Issue:** Plan used `path.resolve(import.meta.dir, '../../../config/safety.yaml')` — import.meta.dir in routes/ points to server/routes/, so 3 `../` goes up to app/, then config/ is relative to plugin root. Used URL construction for reliability.
- **Fix:** Used `new URL('../../../config/safety.yaml', import.meta.url).pathname`
- **Files modified:** app/server/routes/config.ts
- **Verification:** Path resolves to correct safety.yaml location
- **Committed in:** 79b217f

---

**Total deviations:** 4 auto-fixed (all Rule 1 - bugs in plan code)
**Impact on plan:** All fixes necessary for correctness. No scope creep. Plan structure and intent preserved exactly.

## Issues Encountered

None beyond the auto-fixed deviations above.

## User Setup Required

None — no external service configuration required. Haiku API key already configured from Phase 3 Plan 01 (chat system).

## Next Phase Readiness

- Config editor fully functional with 4-step validation, wizard, warnings
- Phase 3 Plan 03 (Feedback pipeline) can proceed: config page provides context for calibration display
- Phase 3 Plan 04 (Self-assessment + measurement) can proceed: config page provides indicator baseline display location

---
*Phase: 03-flywheel-core*
*Completed: 2026-03-18*
