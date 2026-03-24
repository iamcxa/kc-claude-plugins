# Phase 14: Extended Feedback - Context

**Gathered:** 2026-03-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Nightwatch captures feedback from two new channels automatically: Slack reactions on nightwatch messages (👍/👎/🤔) and PR review verdicts (approve/request-changes/comment). Both feed into the existing `feedback.yaml` with correct signal_id correlation, extending the current `pr_status`/`linear_status` implicit feedback system.

</domain>

<decisions>
## Implementation Decisions

### Verdict Mapping (3-state)
- **D-01:** Add `'uncertain'` as third verdict value: `verdict: 'accepted' | 'rejected' | 'uncertain'`
- **D-02:** Reaction mapping: 👍=accepted, 👎=rejected, 🤔=uncertain
- **D-03:** PR review mapping: APPROVED=accepted, CHANGES_REQUESTED=rejected, COMMENTED=uncertain, DISMISSED=skip
- **D-04:** Calibration impact: `reject_rate = rejected / total` — 'uncertain' counted in total but NOT in rejected, lowers reject rate, keeps threshold stable
- **D-05:** FeedbackEntry.source extended: add `'slack_reaction' | 'pr_review'` to existing union

### Polling Strategy
- **D-06:** On-next-run polling — check Slack reactions and PR reviews from previous runs at the start of the next run, before execution begins
- **D-07:** Same temporal pattern as existing `collectImplicitFeedback` — ~24h delay acceptable for nightly calibration
- **D-08:** No new scheduling infrastructure — fits into existing run lifecycle

### Slack Reaction Collection
- **D-09:** Use existing Slack MCP in nightwatch skill Phase 0 (zero new infrastructure, zero new tokens)
- **D-10:** Architecture must support future Slack Bot API backend (`fetch` + `SLACK_BOT_TOKEN`) — design collector interface as abstraction, not hardcoded to MCP
- **D-11:** Message URL stored in improvement-log when nightwatch posts to Slack — serves as input for both MCP and future Bot API implementations
- **D-12:** Skill Phase 0 flow: read improvement-log → find previous Slack URL → `slack_read_thread` MCP → map reactions → write FeedbackEntry to feedback.yaml
- **D-13:** Feedback collection split is acceptable: PR merge status stays in worker (`feedback-collector.ts`), Slack reactions in skill (Phase 0)

### PR Review Collection
- **D-14:** Top-level verdict only — no inline comment content parsing
- **D-15:** Use `gh pr view {number} --repo {repo} --json reviews` (existing `gh` CLI pattern from `checkPrStatus`)
- **D-16:** Runs in worker `feedback-collector.ts` alongside existing PR merge status check — same function, extended scope
- **D-17:** Multiple reviews on same PR: take the LATEST review per reviewer (most recent state wins)

### FeedbackStore Extension
- **D-18:** New keys in FeedbackStore: `slack_feedback` and `pr_review_feedback` alongside existing `explicit_feedback`, `pr_feedback`, `linear_feedback`
- **D-19:** Dashboard feedback view must show all sources including new ones — existing `/api/feedback` endpoint returns all categories

### Claude's Discretion
- `slack-reaction-collector.ts` vs extending existing `feedback-collector.ts` for PR reviews
- Whether to batch Slack MCP calls or one per message
- How to handle Slack MCP failures gracefully (skip vs error)
- Exact improvement-log field name for Slack message URL (`slack_url`? `slack_message_ts`?)
- CalibrationData code changes for 3-state verdict handling

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing feedback infrastructure (modify/extend)
- `app/worker/feedback-collector.ts` — `collectImplicitFeedback()`, `checkPrStatus()`, `checkLinearStatus()` — PR review collection extends this file
- `app/server/services/feedback-store.ts` — `appendFeedback()`, `FeedbackStore` interface, `FEEDBACK_YAML_PATH` — add new source categories
- `app/shared/types.ts` — `FeedbackEntry` interface (line 166): verdict union + source union need extending
- `app/shared/types.ts` — `CalibrationData` (line 176): may need `uncertain_count` field

### Execution lifecycle (integration points)
- `app/worker/executor.ts` — `executeRun()` finally block: PR review check goes here alongside existing `collectImplicitFeedback`
- Nightwatch skill Phase 0: Slack reaction collection goes here (skill source, not in this repo)

### Dashboard (display changes)
- `app/server/routes/feedback.ts` — API endpoint returning feedback entries
- `app/frontend/components/action-card.ts` — feedback display component

### Configuration
- `~/.claude/kc-plugins-config/nightwatch-improvement-log.md` — Slack message URLs stored here
- `~/.claude/kc-plugins-config/nightwatch-feedback.yaml` — feedback data file
- `~/.claude/kc-plugins-config/channels.yaml` — Slack channel config

### Prior phase patterns
- Phase 10 CONTEXT.md D-01~D-04: run mode behavior (dry-run doesn't trigger auto-create — same applies to feedback collection)
- Phase 13 CONTEXT.md: worktree isolation doesn't affect feedback (runs after worktree cleanup)

### Requirements
- `.planning/REQUIREMENTS.md` — EXTFEED-01 (Slack reactions), EXTFEED-02 (PR review comments)
- Out of scope: "Slack message posting (write)", "Real-time Slack webhook"

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `checkPrStatus()` in `feedback-collector.ts`: `gh pr view --json state,mergedAt` pattern — extend with `--json reviews` for review state
- `checkLinearStatus()`: `fetch()` + GraphQL pattern — same pattern for future Slack Bot API
- `appendFeedback()`: source-routed append to YAML — add 'slack_reaction' and 'pr_review' routes
- `FeedbackStore` categories: `explicit_feedback`, `pr_feedback`, `linear_feedback` — add `slack_feedback`, `pr_review_feedback`

### Established Patterns
- All implicit feedback collection runs post-execution in `finally` block (fire-and-forget, errors MUST NOT block run)
- `Bun.spawn(['gh', ...])` for GitHub API calls — reuse for review data
- `readYamlFile()`/`writeYamlFile()` for feedback persistence
- FeedbackEntry is the universal unit — all sources produce the same shape

### Integration Points
- `executor.ts` finally block (line 257~287): add PR review check alongside existing PR merge check
- Nightwatch skill Phase 0: add Slack reaction check (separate from this codebase — skill modification)
- `types.ts` FeedbackEntry: verdict + source unions need extending
- `feedback-store.ts` `appendFeedback()`: add routing for new source values
- Dashboard: `feedback.ts` route + `action-card.ts` component may need updates for new sources

</code_context>

<specifics>
## Specific Ideas

- Slack reaction collector designed as interface/abstraction so MCP backend can be swapped for Bot API later without changing the calling code
- Improvement-log already captures run metadata — adding Slack message URL is a natural extension
- PR review check is a simple extension of existing `checkPrStatus()` — same `gh` CLI, different `--json` fields
- 3-state verdict (accepted/rejected/uncertain) creates a symmetric model across both new channels

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 14-extended-feedback*
*Context gathered: 2026-03-24*
