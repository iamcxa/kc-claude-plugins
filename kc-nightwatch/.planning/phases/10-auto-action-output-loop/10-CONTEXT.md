# Phase 10: Auto-Action Output Loop - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

The worker automatically creates PRs and Linear issues after runs that produce actionable output, skipping creation when duplicates already exist. NW-Claude can answer questions about outcomes via MCP. No frontend changes — the Outcomes page and action card links are Phase 11.

</domain>

<decisions>
## Implementation Decisions

### Auto-Create Trigger Scope
- **D-01:** Production mode auto-creates PRs and Linear issues by default (no opt-out needed)
- **D-02:** Dry-run and self-repair modes do NOT trigger auto-create — actions are recorded in RunSummary but no external side effects
- **D-03:** Manual triggers (dashboard) get an "Auto-create PRs/issues" checkbox — defaults ON for production, OFF for dry-run. User can toggle for testing
- **D-04:** Self-repair has its own PR creation flow (CLAUDE.md: "creates PR for structural FAIL items") — auto-create must NOT conflict with it

### Outcome Storage
- **D-05:** New `outcomes.yaml` in `~/.claude/kc-plugins-config/` — append-only YAML, same pattern as `runs.yaml` and `feedback.yaml`
- **D-06:** Each outcome record: `{ id, type: 'pr'|'linear_issue', target, signal_id, run_id, url, branch?, status, created_at }`
- **D-07:** `RunSummaryAction.pr_url` and `.linear_url` fields remain as the source of truth from the skill's output — `outcomes.yaml` is the queryable index

### Dedup Strategy
- **D-08:** PR dedup: `gh pr list --head {branch} --json url` — if PR exists on the same branch, skip creation and reuse existing URL
- **D-09:** Linear issue dedup: check `outcomes.yaml` for an existing open Linear issue with the same `signal_id + target` — if found, skip creation
- **D-10:** Dedup runs BEFORE create, not after — never create then check

### NW-Claude MCP Tools
- **D-11:** 3 MCP tools: `nw_get_outcomes`, `nw_get_outcome_status`, `nw_outcome_summary`
- **D-12:** `nw_get_outcomes` — list with optional filters: `target?`, `type?`, `status?`, `since?` (date range). Returns array from `outcomes.yaml`
- **D-13:** `nw_get_outcome_status` — poll a specific outcome's live status via GitHub/Linear API (reuses existing `checkPrStatus`/`checkLinearStatus`)
- **D-14:** `nw_outcome_summary` — aggregated stats: count by type+status, count by target, recent activity. NW-Claude uses this for overview questions

### Claude's Discretion
- `pr-creator.ts` and `linear-creator.ts` internal structure
- System prompt injection approach for `executor.ts` (how to tell the skill to produce parseable output)
- `outcome-store.ts` implementation (read/append/query functions)
- `outcomes.yaml` file path (recommend `~/.claude/kc-plugins-config/nightwatch-outcomes.yaml` to match existing config files)
- Chat manager tool registration for `nw_get_outcomes`, `nw_get_outcome_status`, `nw_outcome_summary`
- Error handling for `gh` CLI failures (timeout, auth issues)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Auto-create patterns
- `.planning/research/SUMMARY.md` §Phase 3 — Architecture approach, `pr-creator.ts` + `linear-creator.ts` file specs, dedup strategies
- `.planning/research/PITFALLS.md` — Pitfall 6 (gh pr create on existing PR), Pitfall 7 (duplicate Linear issues)
- `.planning/REQUIREMENTS.md` — AUTO-01, AUTO-02, AUTO-03, OUT-03

### Existing code (read before modifying)
- `app/worker/feedback-collector.ts` — `checkPrStatus()` (gh CLI pattern), `checkLinearStatus()` (Linear GraphQL pattern) — reuse for dedup and status polling
- `app/worker/executor.ts` — `executeRun()` post-run hook point; already calls `collectImplicitFeedback`
- `app/shared/types.ts` — `RunSummaryAction` (pr_url, linear_url, branch fields), `ImplementationOutcome` type
- `app/server/services/mcp-tools.ts` — Existing MCP tool registration pattern (12 tools currently)
- `app/server/services/chat-manager.ts` — Chat tool registration pattern
- `app/server/services/yaml-store.ts` — YAML read/write pattern for config files

### Prior phase decisions (carry forward)
- Phase 8 CONTEXT.md — D-01 (flat IPC), D-07 (per-target schedule merge logic)
- Phase 9 CONTEXT.md — D-04 (queue depth 1), D-06 (scheduled trigger skip-if-busy)

### kc-nightwatch skill conventions
- `CLAUDE.md` — Branch naming convention (`kc-nightwatch/{date}-{target}-{type}`), self-repair PR flow, file ownership

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `checkPrStatus()` in `feedback-collector.ts`: gh CLI `pr view` pattern — reuse for `nw_get_outcome_status` polling
- `checkLinearStatus()` in `feedback-collector.ts`: Linear GraphQL query pattern — reuse for issue status polling
- `Bun.spawn(['gh', ...])` pattern: already proven in `checkPrStatus` — extend for `gh pr create` and `gh pr list`
- `yaml-store.ts` read/write pattern: `readYamlFile()` / YAML append — extend for `outcome-store.ts`
- `mcp-tools.ts` tool registration: `server.registerTool()` with Zod schema — follow for 3 new outcome tools

### Established Patterns
- `feedback-collector.ts` runs after `executeRun()` completes — auto-create should follow the same lifecycle position
- `RunSummary.per_target[name].actions` contains all actions with `pr_url`, `linear_url`, `branch` — the data source for auto-create
- MCP tools use `getLastWorkerState()` or `yaml-store.ts` reads — outcome tools read from `outcome-store.ts`
- Config files live in `~/.claude/kc-plugins-config/` — outcomes.yaml follows this convention

### Integration Points
- `worker/executor.ts` post-run: after `collectImplicitFeedback`, add auto-create step
- `server/services/mcp-tools.ts`: register 3 new tools
- `server/services/chat-manager.ts`: register 3 new chat tools (mirror MCP tools)
- STATE.md blocker: verify `gh` CLI auth inside safehouse before building PR creation flow

</code_context>

<specifics>
## Specific Ideas

- User wants manual trigger to have opt-in auto-create checkbox for testing ("手動時應該可選，例如我想快速測試行為")
- Research recommends `[NW] {signal_summary} [{target}]` as PR/issue title template
- `outcomes.yaml` follows same path convention as other config: `~/.claude/kc-plugins-config/nightwatch-outcomes.yaml`
- PR dedup via `gh pr list --head {branch}` is most reliable (branch names are deterministic from CLAUDE.md convention)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 10-auto-action-output-loop*
*Context gathered: 2026-03-22*
