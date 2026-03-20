---
phase: 4
slug: full-flywheel
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-18
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bun:test |
| **Config file** | app/bunfig.toml (if exists) or none — bun:test works OOTB |
| **Quick run command** | `bun test` |
| **Full suite command** | `bun test` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `bun test`
- **After every plan wave:** Run `bun test`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| TBD | 01 | 1 | MCP-01..04 | integration | `bun test tests/server/mcp.test.ts` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | FEED-03 | unit | `bun test tests/server/mcp.test.ts` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | FEED-05 | unit | `bun test tests/worker/linear-status.test.ts` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | CHAT-04, CHAT-05 | integration | `bun test tests/server/chat-tools.test.ts` | ❌ W0 | ⬜ pending |
| TBD | 02 | 2 | HEALTH-01..05 | unit | `bun test tests/server/health-api.test.ts` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `app/tests/server/mcp.test.ts` — MCP tool registration, stateless transport, tool call routing
- [ ] `app/tests/worker/linear-status.test.ts` — Linear GraphQL status mapping, URL parsing, graceful skip
- [ ] `app/tests/server/chat-tools.test.ts` — Chat tool_use handling, MCP client routing, tool_result feedback
- [ ] `app/tests/server/health-api.test.ts` — Health data aggregation, sparkline data shape, empty state

*Existing 163 tests cover Phase 1-3 infrastructure.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Health sparkline rendering | HEALTH-01 | SVG rendering needs visual inspection | Open Health page, verify sparklines appear for targets with run data |
| MCP client config in Claude session | MCP-01 | Requires external Claude session | Configure `mcpServers.nightwatch` in Claude, call `nw_get_targets` |
| Aggregate health summary bar | HEALTH-05 | Visual layout | Open Health page with data, verify summary bar shows correct overall trend |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
