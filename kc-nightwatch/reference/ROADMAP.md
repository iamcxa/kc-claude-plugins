# kc-nightwatch Roadmap

## Architecture — Role Boundary

```
nightwatch = 偵察兵（discover + report）
  看: journal, e2e results, Sentry, git stats
  不看: Linear backlog（那是人類的 prioritization domain）
  產出: Linear issues, Slack alerts, Plugin PRs

agent-executor = 工兵（implement）— 未來獨立系統，不在 nightwatch scope
  輸入: Linear issues with "agent-eligible" label（人類標記）
  產出: PRs → 人類 review → merge
```

**Why not Linear backlog as source?** Issues already in Linear are known to the team. Nightwatch saying "this is stale" is nagging, not discovery. Nightwatch's value is finding problems nobody has filed yet.

**Why nightwatch doesn't execute on products?** Product code changes need domain context that nightwatch doesn't have. Nightwatch discovers and reports; humans (or future agent-executor) implement.

---

## v0.1 — Plugin-only, PR-only ✅

- Plugin structure: 2 skills (orchestrator, report), 1 agent (signal-harvester)
- Signal sources: journal, episodic memory, MEMORY.md
- Actions: quick-fix (edit-only PR), proposal (PROPOSAL.md draft PR)
- Output: PR (remote) or local branch (no remote), Slack morning report
- Safety: safety.yaml, skip guards, anti-rationalization rules
- Forge validation (Phase 1) for plugin targets

## v0.2 — Config + Product Foundation ✅

- Config migrated to `~/.claude/kc-plugins-config/nightwatch-targets.yaml`
- Target type generalized: `plugin | product`
- `linear-issue` action type (Phase 3 classify + Phase 4.3 execute)
- `--dry-run` mode (bypass skip guards)
- `--review` mode on report skill (accept/defer/reject)
- `/kc-nightwatch-config` skill (schedule/channel/plugins)
- Slack channel ask-on-first-use
- Feedback scan (Phase 0.4): scans own PR comments + Linear issue resolutions
- `kc-nightwatch` label created on kc-claude-plugins GitHub repo
- First product target enabled (linear-issue only, journal/episodic/memory sources)
- Signal quality validated: 7 actionable signals from journal alone

## v0.3 — Discovery Sources (observe, don't poll) ✅

Expand what nightwatch can **observe** — never poll backlogs humans already manage.

- [x] **Sentry as signal source**: production error spikes, new error types, regression detection
  - Architecture: separate `sentry-scanner` agent (not merged into signal-harvester) — scheme C for extensibility
  - Requires: Sentry MCP tools, `sentry_projects` (plural) field in target config
  - Output: `linear-issue` (investigation needed) or `alert` (just notify)
  - Graceful degradation: returns empty signals if Sentry MCP unavailable
- [x] **E2E reports as signal source**: test failure trends, coverage gaps, stale mappings
  - Separate `e2e-scanner` agent scans `e2e-reports/` and `.claude/e2e/`
  - Output: `linear-issue` or `e2e-flow` action (generate new flow YAML)
- [x] **Git stats as signal source**: high-churn hotspots, long-untouched code areas
  - Separate `git-scanner` agent uses `git log --since` analysis
  - Output: `linear-issue` (investigation) — "this area changes 3x/week, worth stabilizing?"
- [x] **`e2e-flow` action**: generate E2E flow YAML from failure signals
  - Requires existing `.claude/e2e/mappings/`; downgrades to `linear-issue` if missing
- [x] **`alert` action**: notify only, no issue/PR (for Sentry spikes that may self-resolve)
  - Safety: `max_per_target: 5` in safety.yaml, respects cooldown
- [x] **launchd schedule**: replaced cron with macOS native scheduler (StartCalendarInterval), runs missed jobs on wake. Templates in `config/`. Option B (pmset wake + AC power guard) documented as TODO.
- [x] **Duplicate check improvement**: `list_issues` with `includeArchived: true`, status-based routing (Open → skip, Done → skip, Canceled → 30d cooldown, Duplicate → follow to original)
- [x] **Review UX**: one-at-a-time proposal review (overview first, then individual decision prompts)
- [x] **Quick-fix pre-check**: Step 3.4 verifies fix hasn't already been applied before classifying as quick-fix
- [x] **improvement-log migration**: moved from `reference/improvement-log.md` to `~/.claude/kc-plugins-config/nightwatch-improvement-log.md` (runtime data out of plugin source)
- [x] **Dry-run validated**: 5 targets, 8 agents, 34 signals, 15 actions — full pipeline exercised
- [x] **Production mode**: launchd installed, first automatic run pending (2026-03-16 03:00)

### Architecture Note (v0.3)
Originally planned to expand signal-harvester with new sources. Instead chose **scheme C** — each data source gets its own discovery agent. Benefits: independent tool sets, parallel dispatch, future extensibility (PostHog = just another agent). Signal ID namespacing (`sig-sentry-`, `sig-e2e-`, `sig-git-`) prevents collisions across agents.

### Explicitly NOT in v0.3
- ~~Linear backlog as signal source~~ — removed. Known issues are the team's domain. Nightwatch discovers, doesn't nag.
- ~~Product code changes~~ — nightwatch reports findings, doesn't fix product code.

## v0.4 — Self-Repair + Feedback ✅

- [x] `--self-repair` mode: dedicated session for config validation + feedback + own forge check
- [x] Config auto-fix: Linear team/project name resolution (exact → case-insensitive → substring)
- [x] Feedback collection: scan own PRs (gh) + Linear issues for accept/reject/correct
- [x] Feedback adjusts pipeline: reject rate > 50% raises confidence threshold, rejected signals get 30d cooldown
- [x] Own forge check: validate kc-nightwatch itself, PR for structural FAIL items (circuit breaker: 1 PR/run)
- [x] Cron wrapper: two-session model (self-repair 5min → pipeline 30min)
- [x] Plugin/config separation: all runtime files in `~/.claude/kc-plugins-config/`, plugin source stays distributable
- [x] `nightwatch-self-repair.yaml` + `nightwatch-feedback.yaml` output schemas

## v0.5 — Multi-Session + Analytics

- [ ] **Multi-session architecture**: cron wrapper orchestrates target-per-session for isolation
- [ ] **Linear workspace identity**: config-level `linear_workspace_id` field, self-repair validates workspace match before any Linear operations. Prevents silent failures when Claude account switches cause MCP to connect to a different Linear workspace.
  - Research needed: does Claude OAuth token auth preserve claude.ai MCP access? If not, self-hosted Linear MCP (with dedicated API token) may be more reliable for cron automation.
- [ ] **Improvement-log analytics**: trend dashboard via `/kc-nightwatch-report --trends`
  - Per-target signal health over time
  - Most effective proxy signals
  - Reject ratio trends
- [ ] **Explicit feedback command**: `/kc-nightwatch-config feedback` — manual signal calibration

## v1.0 — Mature Pipeline

- [ ] **Multi-team routing**: different Slack channels per product/team
  - Route signals to the team that owns the affected code area
- [ ] **Plugin code changes for products**: with explicit human gate
  - Only for targets with `code_changes: true` in config
  - Requires passing tests + validation

## Future — Agent Executor (separate system)

Not nightwatch. A separate system that implements changes based on human-assigned tickets.

```
Linear issue (human creates or nightwatch creates)
    │
    ├── Human labels "agent-eligible"
    │       │
    │       ▼
    │   agent-executor picks up ticket
    │   → reads issue context + codebase
    │   → creates PR with implementation
    │   → human reviews + merges
    │
    └── No label → human implements
```

**Key principle:** The classification responsibility (which tickets are agent-appropriate) stays with humans. Agents don't self-assign — they lack the hidden context ("wait for billing team confirmation", "this touches a regulated flow").

---

## Design Principles (all versions)

1. **Discover, don't nag** — nightwatch finds NEW problems, doesn't remind about known ones
2. **Find cracks, don't tear down walls** — patches, never rewrites
3. **Safety boundaries in config, not code** — safety.yaml is the single source of truth
4. **Conservative classification** — when in doubt, linear-issue over code change
5. **Cooldown prevents repetition** — same signal not re-processed within 7 days
6. **Human decides implementation** — proposals and issues are suggestions, not instructions
7. **Feedback closes the loop** — rejected signals inform future classification
8. **Separation of concerns** — nightwatch discovers, agent-executor implements (future)
