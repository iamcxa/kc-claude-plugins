# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.1 — Dashboard UX Polish

**Shipped:** 2026-03-20
**Phases:** 3 | **Plans:** 5 | **Sessions:** ~3

### What Was Built
- Queue awareness: `queued_at` timestamps across all enqueue paths + worker state endpoint + queue display in target detail
- Toast/notification system: signal-backed toasts for trigger feedback + browser Notification API for background completion alerts
- Unified polling: `usePoll` hook with `refreshTrigger` signal, replacing scattered setInterval patterns
- Dead code cleanup: orphaned chat-drawer.ts removed, phases_completed wired into target detail, sidebar Add Target functional

### What Worked
- **Phase 5 → 6 → 7 dependency chain clean**: each phase had clearly defined provides/requires, no surprises
- **Proactive cleanup during Phase 6**: CLEAN-02 (sidebar wiring) and CLEAN-03 (Add Target button) were done during Phase 6 integration work — Phase 7 only needed CLEAN-01 (dead file) + CLEAN-02 (phases_completed)
- **Plan checker caught real issues**: Phase 7 plan checker flagged "bun typecheck" criterion (no typecheck script exists) and CLEAN-02 needing actual implementation — both would have caused verification failures
- **UAT found 3 real bugs**: vendor import path, htm fragment syntax, type mismatch — all fixed before milestone audit

### What Was Inefficient
- **Summary one-liner extraction failed**: `gsd-tools summary-extract` returned null for all SUMMARY.md files — the YAML frontmatter format didn't include a `one_liner` field. Had to manually read summaries.
- **Phase 7 scope overlap**: Some cleanup items were naturally absorbed by Phase 6, making Phase 7 smaller than planned. Could have merged into Phase 6.

### Patterns Established
- **Module-level callback registration**: `registerToastHandler`/`showToast` pattern avoids prop drilling for cross-cutting concerns like notifications
- **fnRef anti-stale-closure**: ref updated each render so interval/timer always calls latest version without restarting
- **refreshTrigger signal**: SSE consumers increment a signal to trigger immediate fetch, decoupling SSE handling from polling logic
- **htm fragment workaround**: use `html\`<div>...</div>\`` instead of `<>...</>` — htm doesn't support fragment shorthand

### Key Lessons
1. **Vendor import paths are invisible until first consumer**: @preact/signals vendor had hardcoded import from `preact.module.js` (core) instead of `preact-hooks.module.js`. Bug was dormant until first real consumer — always verify vendored imports against the import map.
2. **htm template literal quirks are real**: `<>...</>` fragment syntax produces undefined type that crashes Preact diff. Need explicit `Fragment` or restructure the component.
3. **Plan checker is worth the cost**: Caught 2 blockers in Phase 7 that would have silently failed verification. Small investment, high ROI.

### Cost Observations
- Model mix: ~90% opus, ~10% haiku (config validation only)
- Sessions: ~3 (Phase 5+6 combined, Phase 7+audit, UAT+bugs)
- Notable: Entire v1.1 milestone completed in a single day — small focused scope is fast

---

## Milestone: v1.0 — Nightwatch Dashboard MVP

**Shipped:** 2026-03-19
**Phases:** 4 | **Plans:** 15 | **Sessions:** ~8

### What Was Built
- Two-process architecture (Bun server + worker) with native IPC, crash recovery, orphan cleanup
- Full dashboard cockpit: target cards, run trigger, real-time log streaming, run history with filters
- Flywheel core: NW-Claude chat, YAML config editor with 4-step validation, feedback calibration
- MCP server with 12 tools exposing nightwatch state to any Claude session
- Flywheel health: indicator sparklines, reject rate charts, per-target health arrows

### What Worked
- **Design spec first**: 812-line design spec with 2 review rounds gave clear requirements before any code
- **Phase dependency chain**: each phase had testable success criteria — no ambiguity about "done"
- **Bun native IPC**: eliminated socket file management, EADDRINUSE, reconnection logic. Strictly simpler.
- **No build tooling**: Preact + HTM + import maps = zero build step, instant dev refresh

### What Was Inefficient
- **Chat panel iterations**: Went through ChatDrawer → inline ChatPanel → API-only backend. 3 implementations before settling.
- **Content block normalization**: Anthropic SDK tool_use returns ContentBlock arrays, not strings. SSE consumers broke silently. Should have normalized earlier.
- **Import side-effect trap**: Top-level `Bun.serve()` in server/index.ts caused test hangs. Had to refactor testable functions to leaf modules.

### Patterns Established
- **Import map vendoring**: separate ESM files for core/hooks, import map resolution, no build step
- **signal-backed UI state**: @preact/signals for cross-component state (toast queue, refresh triggers)
- **SSE fan-out**: global broadcast from server, per-page listeners in frontend components

### Key Lessons
1. **Bun IPC works fine**: `process.send()` IS available in Bun child processes. Test hypotheses experimentally.
2. **esm.sh combined files have var collisions**: Always vendor core and hooks as separate ESM files.
3. **Browser `.ts` = `video/mp2t`**: Need `Bun.Transpiler` to serve TypeScript as JavaScript with correct MIME type.

### Cost Observations
- Model mix: ~85% opus, ~15% haiku
- Sessions: ~8 across 2 days
- Notable: 15 plans at ~30 min/plan = ~7.5 hours total execution. 167 tests at completion.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Plans | Key Change |
|-----------|----------|--------|-------|------------|
| v1.0 | ~8 | 4 | 15 | Design spec → phased execution |
| v1.1 | ~3 | 3 | 5 | Smaller scope, faster turnaround |

### Cumulative Quality

| Milestone | Tests | UAT Issues | Bug Fixes |
|-----------|-------|------------|-----------|
| v1.0 | 167 | 1 (chat SSE) | Multiple (IPC, content blocks) |
| v1.1 | 167+ | 0 | 3 (vendor, fragment, type) |

### Top Lessons (Verified Across Milestones)

1. **Vendor module paths are fragile**: Both milestones hit vendor import issues (esm.sh collision in v1.0, hardcoded path in v1.1). Always verify imports against the import map after vendoring.
2. **Plan checker pays for itself**: Catches criterion issues before execution — verified in both v1.0 gap closure phases and v1.1 Phase 7.
3. **Small focused milestones ship fast**: v1.1 (12 requirements, 3 phases) completed in 1 day vs v1.0 (73 requirements, 4 phases) in 2 days. Smaller scope = less context thrash.
