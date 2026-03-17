# Nightwatch Dashboard

## What This Is

A web-based autonomous improvement platform that wraps the existing kc-nightwatch plugin. It replaces the current launchd cron job with a persistent Bun server + worker architecture, providing a dashboard for monitoring targets, triggering runs, viewing real-time execution logs, editing config with validation, and interacting with NW-Claude — an AI assistant that summarizes run results and takes direction. Built for Kent first, designed to be generalizable for open-source use later.

## Core Value

The closed-loop feedback flywheel: NW monitors codebases, proposes improvements, learns from human feedback, and gets measurably better over time. Without this, it's just another automation tool. With it, it's a self-improving system.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Two-process architecture (Hono server + worker) with IPC
- [ ] Dashboard UI showing targets, run history, schedule status
- [ ] Manual run trigger with mode selection (production/dry-run) and custom prompt
- [ ] Real-time log streaming via `claude -p --output-format stream-json` + SSE
- [ ] Per-target agent-safehouse execution policies
- [ ] Interval scheduler (every N hours) + webhook trigger
- [ ] YAML config editor with edit lock + 4-step validation (static → semantic via Haiku → diff → confirm)
- [ ] Add/Edit/Remove target wizard
- [ ] NW-Claude chat panel with auto-brief after runs
- [ ] Bidirectional Claude session via `--input-format stream-json`
- [ ] MCP server exposing nightwatch state to any Claude session (query + trigger + feedback)
- [ ] Multi-channel feedback collection (dashboard, MCP, PR status, Linear status)
- [ ] Feedback → reject rate calibration + NW journal reflection
- [ ] Two-phase self-assessment (Phase 3.5 strategy + Phase 4.5 reflection)
- [ ] Indicator baseline measurement (Phase 0.5) with quantified values
- [ ] Implementation outcome tracking (Phase 0.6) — did merged PRs actually help?
- [ ] Flywheel health metrics (indicator trends, reject rate, acceptance rate, effectiveness)
- [ ] Proposal → implementation pipeline (accept → spawn implementation run → code PR)
- [ ] Per-target NW memory layer (isolated private-journal per target)
- [ ] Localhost by default + optional remote mode with token auth

### Out of Scope

- Cron expression scheduling — interval is sufficient for MVP
- File watch triggers — not needed with interval + manual + webhook
- Multi-user auth / RBAC — single user for now
- Cross-machine sync / cloud dashboard — local only
- channels.yaml / language.yaml editing in UI — keep using CLI
- Custom MCP/plugin per target — use user-scope MCPs + project .mcp.json
- Per-target auth token management — schema prepared, not implemented
- Slack reaction feedback — requires Slack MCP read (v2)
- PR review comment parsing — requires gh API parsing (v2)

## Context

- **Existing plugin**: kc-nightwatch v0.4.0 with 3 skills (nightwatch, report, config) + 4 agents (signal-harvester, sentry-scanner, e2e-scanner, git-scanner)
- **Current execution**: launchd plist at 03:00 daily via `nightwatch-cron.sh` (two-session model: self-repair 5min → pipeline 30min)
- **Config files**: All in `~/.claude/kc-plugins-config/` — targets.yaml, runs.yaml, feedback.yaml, improvement-log.md, self-repair.yaml
- **Design spec**: `docs/superpowers/specs/2026-03-18-nightwatch-dashboard-design.md` (812 lines, 2 review rounds passed)
- **Field renaming**: App introduces `monitors`/`watch`/`respond`/`indicators` (replacing `sources`/`keywords`/`actions`/`proxy_signals`) with compatibility layer
- **Pipeline phases**: 0 → 0.5 (Measure) → 0.6 (Outcomes) → 1 → 2 → 3 → 3.5 (Assess) → 4 → 4.5 (Assess) → 5

## Constraints

- **Runtime**: Bun — matches existing 1on1 report engine, native TS support
- **Framework**: Hono (server) + Preact/HTM (frontend) — lightweight, no heavy deps
- **Execution**: agent-safehouse mandatory for all `claude -p` spawns
- **Concurrency**: Max 1 concurrent run (queue if busy)
- **Config validation budget**: $0.05 cap (Haiku model) for semantic validation
- **Always-on**: Must be stable enough for mprocs integration (crash recovery, graceful shutdown)
- **Compatibility**: Existing nightwatch skills/agents unchanged in MVP — app wraps them

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Server + Worker (2 processes) | UI stays responsive regardless of execution load; worker can crash without losing dashboard | — Pending |
| Preact + HTM over vanilla TS | Need component model + hooks for chat/forms; HTM avoids build step | — Pending |
| Per-target NW journal isolation | Prevent cross-target memory leakage; each target has its own learning context | — Pending |
| Feedback loop as highest priority | It's the engine of the flywheel — without it, other features are "do once and stop" | — Pending |
| Field renaming with compat layer | Better naming (monitors/watch/respond) without breaking existing skills | — Pending |
| `--input-format stream-json` for chat | Bidirectional streaming via CLI; API fallback if unreliable | — Pending |
| Indicator measurement in Phase 0.5 | Data-backed self-assessment instead of qualitative LLM guessing | — Pending |
| Proposal → Implementation pipeline | Closes the flywheel: accepted proposals get implemented, outcomes tracked | — Pending |

---
*Last updated: 2026-03-18 after initialization*
