# Nightwatch Dashboard

## What This Is

A web-based autonomous improvement platform that wraps the existing kc-nightwatch plugin. It replaces the current launchd cron job with a persistent Bun server + worker architecture, providing a dashboard for monitoring targets, triggering runs, viewing real-time execution logs, editing config with validation, and interacting with NW-Claude — an AI assistant that summarizes run results and takes direction. Built for Kent first, designed to be generalizable for open-source use later.

## Core Value

The closed-loop feedback flywheel: NW monitors codebases, proposes improvements, learns from human feedback, and gets measurably better over time. Without this, it's just another automation tool. With it, it's a self-improving system.

## Requirements

### Validated

Validated in v1.0 (Phases 1-4, 2026-03-18 to 2026-03-19):
- ✓ Two-process architecture (Hono server + worker) with IPC — v1.0
- ✓ Dashboard UI showing targets, run history, schedule status — v1.0
- ✓ Manual run trigger with mode selection (production/dry-run) and custom prompt — v1.0
- ✓ Real-time log streaming via `claude -p --output-format stream-json` + SSE — v1.0
- ✓ Per-target agent-safehouse execution policies — v1.0
- ✓ Interval scheduler (every N hours) + webhook trigger — v1.0
- ✓ YAML config editor with edit lock + 4-step validation (static → semantic via Haiku → diff → confirm) — v1.0
- ✓ Add/Edit/Remove target wizard — v1.0
- ✓ NW-Claude chat panel with auto-brief after runs — v1.0
- ✓ Bidirectional Claude session via Anthropic SDK — v1.0
- ✓ MCP server exposing nightwatch state to any Claude session (12 tools) — v1.0
- ✓ Multi-channel feedback collection (dashboard, MCP, PR status, Linear status) — v1.0
- ✓ Feedback → reject rate calibration + NW journal reflection — v1.0
- ✓ Two-phase self-assessment (Phase 3.5 strategy + Phase 4.5 reflection) — v1.0
- ✓ Indicator baseline measurement (Phase 0.5) with quantified values — v1.0
- ✓ Flywheel health metrics (indicator trends, reject rate, acceptance rate, per-target health arrows) — v1.0
- ✓ Per-target NW memory layer (isolated private-journal per target) — v1.0
- ✓ Localhost by default + optional remote mode with token auth — v1.0

Validated in v1.1 (Phases 5-7, 2026-03-20):
- ✓ `queued_at` timestamp on runs across all 4 enqueue paths — v1.1
- ✓ Queue visibility in target detail panel (count + position pills) — v1.1
- ✓ Toast notification system for run trigger feedback — v1.1
- ✓ Browser Notification API for run completion/failure (user-gesture-gated) — v1.1
- ✓ Runs page auto-refresh via shared `usePoll` hook (polling parity with dashboard) — v1.1
- ✓ Dead code cleanup (chat-drawer.ts deleted, phases_completed wired) — v1.1
- ✓ Sidebar Add Target button wiring — v1.1

Validated in v2.0 (Phases 8-11, 2026-03-21 to 2026-03-23):
- ✓ Per-target scheduling with global fallback (minimum 10min interval) — v2.0
- ✓ Parallel execution — per-target isolation (different targets concurrent, same target queued) — v2.0
- ✓ Auto-create PR when code changes are proposed — v2.0
- ✓ Auto-create Linear issues for improvement signals — v2.0
- ✓ Outcome visibility — action cards with PR/Linear links — v2.0
- ✓ Outcomes page — aggregate view of all PRs/issues across runs, filterable — v2.0
- ✓ NW-Claude awareness of PR/Linear outcomes (chat can answer about them) — v2.0
- ✓ Implementation outcome tracking (Phase 0.6) — did merged PRs actually help? — v2.0
- ✓ UI fix — bottom nav gap (black line between content and nav bar) — v2.0

Validated in v3.0 (Phases 12-14, 2026-03-24):
- ✓ Completed run log read from file (not SSE-only) — v3.0 (RUNUX-01)
- ✓ Target path required in wizard — v3.0 (RUNUX-02)
- ✓ Server auto-restart on code change — v3.0 (RUNUX-03)
- ✓ Test suite reliability — mock.module contamination fixed — v3.0 (TEST-01)
- ✓ Worktree isolation — runs execute in temporary worktrees — v3.0 (WKTREE-01~03)
- ✓ Slack reaction feedback with signal_id correlation — v3.0 (EXTFEED-01)
- ✓ PR review comment parsing into feedback entries — v3.0 (EXTFEED-02)
- ✓ Dashboard displays all feedback sources with source labels — v3.0
- ✓ 3-state verdict (accepted/rejected/uncertain) — v3.0

### Future (v4+)

(No items defined — start next milestone with `/gsd:new-milestone`)

### Out of Scope

- Cron expression scheduling — interval is sufficient
- File watch triggers — not needed with interval + manual + webhook
- Multi-user auth / RBAC — single user for now
- Cross-machine sync / cloud dashboard — local only
- channels.yaml / language.yaml editing in UI — keep using CLI
- Custom MCP/plugin per target — use user-scope MCPs + project .mcp.json
- Per-target auth token management — schema prepared, not implemented
- Mobile responsive design — desktop-first local tool
- Toast library (react-toastify, sonner) — breaks no-build constraint; handroll is ~70 lines

## Context

- **Shipped versions**: v1.0 MVP (2026-03-19), v1.1 UX Polish (2026-03-20), v2.0 Parallel + Auto-Action (2026-03-23), v3.0 Worktree + Feedback (2026-03-24)
- **Existing plugin**: kc-nightwatch v0.4.0 with 3 skills + 4 agents
- **Execution**: launchd plist at 03:00 daily; dashboard provides alternative manual/webhook triggers
- **Config files**: All in `~/.claude/kc-plugins-config/` — targets.yaml, runs.yaml, feedback.yaml, improvement-log.md, self-repair.yaml
- **Design spec**: `docs/superpowers/specs/2026-03-18-nightwatch-dashboard-design.md`
- **Field renaming**: App introduces `monitors`/`watch`/`respond`/`indicators` (replacing `sources`/`keywords`/`actions`/`proxy_signals`) with compatibility layer
- **Pipeline phases**: 0 → 0.4.5 (Reactions) → 0.5 (Measure) → 0.6 (Outcomes) → 1 → 2 → 3 → 3.5 (Assess) → 4 → 4.5 (Assess) → 5
- **Codebase**: ~12K LOC TypeScript (Bun + Hono + Preact/HTM), zero build tooling, 373 tests

## Constraints

- **Runtime**: Bun — matches existing 1on1 report engine, native TS support
- **Framework**: Hono (server) + Preact/HTM (frontend) — lightweight, no heavy deps
- **Execution**: agent-safehouse mandatory for all `claude -p` spawns
- **Concurrency**: Per-target isolation — different targets run in parallel, same target queues (v2.0 change from max 1)
- **Config validation budget**: $0.05 cap (Haiku model) for semantic validation
- **Always-on**: Must be stable enough for mprocs integration (crash recovery, graceful shutdown)
- **Compatibility**: Existing nightwatch skills/agents unchanged — app wraps them

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Server + Worker (2 processes) | UI stays responsive regardless of execution load; worker can crash without losing dashboard | ✓ Good — worker crashes don't affect dashboard |
| Preact + HTM over vanilla TS | Need component model + hooks for chat/forms; HTM avoids build step | ✓ Good — 8.8K LOC, zero build tooling |
| Per-target NW journal isolation | Prevent cross-target memory leakage; each target has its own learning context | ✓ Good — clean per-target memory |
| Feedback loop as highest priority | It's the engine of the flywheel — without it, other features are "do once and stop" | ✓ Good — calibration working |
| Field renaming with compat layer | Better naming (monitors/watch/respond) without breaking existing skills | ✓ Good — zero migration needed |
| Anthropic SDK for chat (not CLI) | `--input-format stream-json` unreliable; SDK gives direct tool_use control | ✓ Good — stable multi-turn tool loops |
| Indicator measurement in Phase 0.5 | Data-backed self-assessment instead of qualitative LLM guessing | ✓ Good — baselines with quantified values |
| Queue state via GET endpoint (not SSE) | Keep lifecycle SSE channel clean; polling for queue is fine at 5s intervals | ✓ Good — simple and reliable |
| Browser Notification on user gesture | Permission on page load is anti-pattern; trigger button click is natural gesture | ✓ Good — no surprise permission prompts |
| Handroll toast (no library) | No-build constraint; signal-backed toast is ~70 lines | ✓ Good — lightweight, no deps |
| Proposal → Implementation pipeline | Closes the flywheel: accepted proposals get implemented, outcomes tracked | ✓ Good — v2.0 shipped auto-action |

## Current Milestone: v4.0 Flywheel Intelligence

**Goal:** Make the feedback flywheel visible and self-adjusting — users see improvement trends, system auto-calibrates from feedback data

**Target features:**
- Feedback trend visualization (accept/reject rate over time, per-target charts)
- Auto-calibration (feedback-driven confidence threshold adjustment)
- Signal prioritization (confidence × historical success ranking)
- Forge results in dashboard (self-repair output visibility)
- Per-indicator trend sparklines (health arrows → mini charts)

## Current State: v3.0 Shipped

All four milestones complete. 14 phases, 38 plans, 51 requirements validated across v1.0 + v1.1 + v2.0 + v3.0.

**v4.0 in progress** — Flywheel Intelligence.

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-24 after v4.0 milestone started*
