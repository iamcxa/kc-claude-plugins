# Phase 14: Extended Feedback - Research

**Researched:** 2026-03-24
**Domain:** Feedback pipeline extension — Slack reaction polling + PR review verdict collection
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Verdict Mapping (3-state)**
- D-01: Add `'uncertain'` as third verdict value: `verdict: 'accepted' | 'rejected' | 'uncertain'`
- D-02: Reaction mapping: 👍=accepted, 👎=rejected, 🤔=uncertain
- D-03: PR review mapping: APPROVED=accepted, CHANGES_REQUESTED=rejected, COMMENTED=uncertain, DISMISSED=skip
- D-04: Calibration impact: `reject_rate = rejected / total` — 'uncertain' counted in total but NOT in rejected, lowers reject rate, keeps threshold stable
- D-05: FeedbackEntry.source extended: add `'slack_reaction' | 'pr_review'` to existing union

**Polling Strategy**
- D-06: On-next-run polling — check Slack reactions and PR reviews from previous runs at the start of the next run, before execution begins
- D-07: Same temporal pattern as existing `collectImplicitFeedback` — ~24h delay acceptable for nightly calibration
- D-08: No new scheduling infrastructure — fits into existing run lifecycle

**Slack Reaction Collection**
- D-09: Use existing Slack MCP in nightwatch skill Phase 0 (zero new infrastructure, zero new tokens)
- D-10: Architecture must support future Slack Bot API backend — design collector interface as abstraction, not hardcoded to MCP
- D-11: Message URL stored in improvement-log when nightwatch posts to Slack — serves as input for both MCP and future Bot API implementations
- D-12: Skill Phase 0 flow: read improvement-log → find previous Slack URL → `slack_read_thread` MCP → map reactions → write FeedbackEntry to feedback.yaml
- D-13: Feedback collection split is acceptable: PR merge status stays in worker (`feedback-collector.ts`), Slack reactions in skill (Phase 0)

**PR Review Collection**
- D-14: Top-level verdict only — no inline comment content parsing
- D-15: Use `gh pr view {number} --repo {repo} --json reviews` (existing `gh` CLI pattern from `checkPrStatus`)
- D-16: Runs in worker `feedback-collector.ts` alongside existing PR merge status check — same function, extended scope
- D-17: Multiple reviews on same PR: take the LATEST review per reviewer (most recent state wins)

**FeedbackStore Extension**
- D-18: New keys in FeedbackStore: `slack_feedback` and `pr_review_feedback` alongside existing `explicit_feedback`, `pr_feedback`, `linear_feedback`
- D-19: Dashboard feedback view must show all sources including new ones — existing `/api/feedback` endpoint returns all categories

### Claude's Discretion

- `slack-reaction-collector.ts` vs extending existing `feedback-collector.ts` for PR reviews
- Whether to batch Slack MCP calls or one per message
- How to handle Slack MCP failures gracefully (skip vs error)
- Exact improvement-log field name for Slack message URL (`slack_url`? `slack_message_ts`?)
- CalibrationData code changes for 3-state verdict handling

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| EXTFEED-01 | Slack reaction parsing — read reactions on nightwatch Slack reports (👍/👎/🤔) and convert to feedback entries with signal_id correlation | D-02, D-09, D-11, D-12: MCP `slack_read_thread` → reaction map → FeedbackEntry; skill Phase 0 is the integration point |
| EXTFEED-02 | PR review comment parsing — read review comments on nightwatch-created PRs and extract actionable feedback (approve=accepted, request changes=rejected, comment=signal for next run) | D-03, D-15, D-16, D-17: `gh pr view --json reviews` → verdict map → FeedbackEntry; worker `feedback-collector.ts` is the integration point |
</phase_requirements>

---

## Summary

Phase 14 extends the existing nightwatch feedback pipeline with two new sources: Slack emoji reactions on nightwatch report messages (👍/👎/🤔) and PR review verdicts on nightwatch-created PRs. Both are read-only, polling-based, and fit into the existing "on-next-run" temporal pattern already established by `collectImplicitFeedback`.

The implementation splits across two layers: PR review collection extends `feedback-collector.ts` in the worker (same process, same `Bun.spawn` + `gh` pattern), while Slack reaction collection lives in the nightwatch skill Phase 0 (skill-layer MCP calls, outside this repo). Both produce the same `FeedbackEntry` shape with new `source` values (`'slack_reaction'` | `'pr_review'`). The 3-state verdict adds `'uncertain'` to the existing `'accepted' | 'rejected'` union, with `uncertain` counting toward total but not toward `reject_count` in calibration.

The primary engineering concern is type safety across the entire change surface: `FeedbackEntry.verdict`, `FeedbackEntry.source`, `FeedbackStore` categories, `getCalibrationData()` logic, and `appendFeedback()` routing all require coordinated updates. The dashboard and MCP feedback tool also hardcode the current 2-verdict API contract and need updating. Failing to update all sites in one pass is the primary pitfall.

**Primary recommendation:** Update `types.ts` first (verdict + source unions), then extend `feedback-store.ts` (routing + categories), then extend `feedback-collector.ts` (PR review function), then update dashboard + MCP. All changes can ship in a single wave.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Bun | (existing) | Spawn `gh` CLI, run tests | Already the runtime |
| `gh` CLI | (existing) | `gh pr view --json reviews` | Already used by `checkPrStatus` |
| Slack MCP | (existing session tool) | `slack_read_thread` for reactions | Already used in skill; zero new infra |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `yaml` (npm) | ^2.8.2 | Read/write feedback YAML | Already used via `readYamlFile`/`writeYamlFile` |
| `bun:test` | (Bun built-in) | Unit tests | All tests in this project use it |

No new dependencies required for this phase.

---

## Architecture Patterns

### Recommended Project Structure

No new files or directories needed. All changes are extensions to existing files:

```
app/
├── shared/
│   └── types.ts          # Extend FeedbackEntry.verdict + source unions, CalibrationData
├── server/
│   └── services/
│       └── feedback-store.ts  # Add slack_feedback + pr_review_feedback keys, update routing
│       routes/
│       └── feedback.ts   # Update POST validation to accept 'uncertain' verdict
├── worker/
│   └── feedback-collector.ts  # Add checkPrReviews() function
└── tests/
    ├── server/
    │   └── feedback.test.ts        # Extend for new sources + 'uncertain' verdict
    └── worker/
        ├── feedback-collector.test.ts  # New: PR review collection tests
        └── executor-feedback-wiring.test.ts  # Static wiring verification (no changes needed)

skills/kc-nightwatch/SKILL.md   # Add Step 0.4.x: Slack reaction collection
```

### Pattern 1: PR Review Collection (extends checkPrStatus)

**What:** New function `checkPrReviews()` in `feedback-collector.ts` that fetches PR review state via `gh pr view --json reviews`. Called in the executor `finally` block alongside the existing `collectImplicitFeedback`.

**When to use:** After each run, for any action that has a `pr_url`.

**Verified `gh pr view --json reviews` schema** (confirmed against real API, 2026-03-24):
```typescript
// Source: gh api repos/cli/cli/pulls/9999/reviews (verified live)
type GhReview = {
  id: string
  author: { login: string }
  state: 'APPROVED' | 'CHANGES_REQUESTED' | 'COMMENTED' | 'DISMISSED'
  submittedAt: string   // ISO 8601
  body: string
}
type GhReviewsResponse = { reviews: GhReview[] }
```

**Implementation:**
```typescript
// Source: extends pattern from checkPrStatus in feedback-collector.ts
export async function checkPrReviews(
  prUrl: string
): Promise<'accepted' | 'rejected' | 'uncertain' | null> {
  const match = prUrl.match(/github\.com\/([^/]+\/[^/]+)\/pull\/(\d+)/)
  if (!match) return null
  const [, repo, prNumber] = match

  const proc = Bun.spawn(
    ['gh', 'pr', 'view', prNumber!, '--repo', repo!, '--json', 'reviews'],
    { stdout: 'pipe', stderr: 'pipe' }
  )
  const stdout = await new Response(proc.stdout).text()
  await proc.exited
  if (proc.exitCode !== 0) return null

  const data = JSON.parse(stdout) as { reviews: GhReview[] }
  if (!data.reviews.length) return null

  // D-17: Latest review per reviewer (most recent state wins)
  const byReviewer = new Map<string, GhReview>()
  for (const r of data.reviews) {
    const existing = byReviewer.get(r.author.login)
    if (!existing || r.submittedAt > existing.submittedAt) {
      byReviewer.set(r.author.login, r)
    }
  }

  // D-03: Map state to verdict. DISMISSED = skip (return null, no feedback)
  // Aggregate: any APPROVED → accepted unless overridden by CHANGES_REQUESTED
  let verdict: 'accepted' | 'rejected' | 'uncertain' | null = null
  for (const review of byReviewer.values()) {
    if (review.state === 'CHANGES_REQUESTED') return 'rejected'  // strongest signal wins
    if (review.state === 'APPROVED') verdict = 'accepted'
    else if (review.state === 'COMMENTED' && verdict === null) verdict = 'uncertain'
    // DISMISSED: skip this reviewer
  }
  return verdict
}
```

### Pattern 2: Type Extension — 3-State Verdict

**What:** Extend `FeedbackEntry` and `CalibrationData` in `types.ts`.

**Implementation:**
```typescript
// Source: app/shared/types.ts (lines 166-182, extend in place)
export interface FeedbackEntry {
  signal_id: string
  target: string
  run_id: string
  verdict: 'accepted' | 'rejected' | 'uncertain'   // D-01: add 'uncertain'
  reason?: string
  source: 'user' | 'pr_status' | 'linear_status' | 'slack_reaction' | 'pr_review'  // D-05
  submitted_at: string
}

// CalibrationData: D-04 — 'uncertain' counted in total but NOT reject_count
// No schema change needed — the getCalibrationData() logic changes, not the interface
// BUT: consider adding uncertain_count for dashboard display clarity (discretion)
```

### Pattern 3: FeedbackStore Routing Extension

**What:** Add two new YAML keys and update `appendFeedback()` switch.

**Implementation:**
```typescript
// Source: app/server/services/feedback-store.ts (extend FeedbackStore interface)
interface FeedbackStore {
  explicit_feedback?: FeedbackEntry[]
  pr_feedback?: FeedbackEntry[]
  linear_feedback?: FeedbackEntry[]
  slack_feedback?: FeedbackEntry[]       // D-18: new
  pr_review_feedback?: FeedbackEntry[]   // D-18: new
}

// appendFeedback routing:
const key = entry.source === 'user' ? 'explicit_feedback'
  : entry.source === 'pr_status' ? 'pr_feedback'
  : entry.source === 'linear_status' ? 'linear_feedback'
  : entry.source === 'slack_reaction' ? 'slack_feedback'       // new
  : entry.source === 'pr_review' ? 'pr_review_feedback'        // new
  : 'linear_feedback'  // fallback (shouldn't reach)
```

### Pattern 4: Slack Reaction Collection (skill-layer, Phase 0)

**What:** A new sub-step in skill Phase 0 that reads `improvement-log.md` for previous run Slack message URLs, calls `slack_read_thread` MCP, maps reactions to verdicts, and appends to `nightwatch-feedback.yaml`.

**Integration point:** SKILL.md Step 0.4 (after existing PR/Linear feedback, before Phase 1).

**Key design (D-10 abstraction):** The skill calls a conceptual "Slack reaction collector" with three inputs: channel_id, message_ts (or URL), and a signal_id. It returns a verdict or null. The MCP backend is swappable because the skill orchestrates MCP calls directly — no coupling to a specific tool binding.

**Improvement-log Slack URL field** (discretion): Use `slack_message_ts` since Slack's native identifier for a message is its timestamp (`ts`) field, which is also the value in Slack message URLs (e.g., `https://infuseai.slack.com/archives/C0ALTGB9F1A/p1234567890`). However, storing the full URL as `slack_url` is more readable and sufficient for `slack_read_thread` MCP calls. Recommendation: use `slack_url` — simpler, self-documenting.

**Failure handling (discretion):** Skip on MCP failure (not error). The skill should catch any MCP tool failure and log a warning, then continue. Rationale: Slack reactions are supplemental feedback; a missed collection window is recoverable on the next run. Never let Slack collection block Phase 1+.

**Batching (discretion):** One MCP call per message URL. Do not batch. Rationale: improvement-log typically has 1 Slack message per run, so batching adds complexity with zero benefit.

### Pattern 5: CalibrationData — 3-State Impact (D-04)

**What:** Update `getCalibrationData()` in `feedback-store.ts` to count `uncertain` in `total` but not `reject_count`.

**Current code (line 57-60):**
```typescript
current.total++
if (entry.verdict === 'rejected') current.rejected++
```

**Updated code — no change needed.** The existing code already only increments `rejected` when `entry.verdict === 'rejected'`. Adding `'uncertain'` to the type union automatically satisfies D-04 — `uncertain` entries will increment `total` but not `rejected`. Zero logic change required in `getCalibrationData()`.

### Pattern 6: Dashboard + API Contract

**What:** The POST `/api/feedback` endpoint in `feedback.ts` currently validates `verdict` as exactly `'accepted' | 'rejected'` and returns 400 otherwise. With `'uncertain'` as a valid verdict, the validation must be updated.

**Also:** `action-card.ts` currently renders only `+1` / `-1` buttons (2-state). The 3-state verdict needs a `?` / uncertain button. However, the dashboard does NOT create `slack_reaction` or `pr_review` feedback via the UI — those come from external sources. The existing +1/-1 buttons remain for user-submitted feedback (`source: 'user'`). Only the verdict validation in the API endpoint needs updating.

### Anti-Patterns to Avoid

- **Partial type update:** If `FeedbackEntry.verdict` is updated in `types.ts` but `feedback.ts` POST validation still rejects `'uncertain'`, runtime errors surface only at feedback submission time. Update all sites in one pass.
- **Tightly coupling Slack collection to MCP tool name:** The skill should call `slack_read_thread` by name (standard Slack MCP), not hardcode a specific tool prefix. Use `ToolSearch "+slack read thread"` pattern if prefix discovery is needed.
- **Storing improvement-log entries for Slack BEFORE the URL is known:** The nightwatch skill posts to Slack at Phase 5 (end of run). The improvement-log entry must be written AFTER the Slack post, with the URL field populated. If Phase 5 Slack delivery fails, the improvement-log entry should record that no URL is available (null/omit field) — don't store a placeholder.
- **Breaking the fire-and-forget contract:** The executor finally block pattern requires that all feedback collection errors are caught and logged, never re-thrown. The new PR review check must follow the same try/catch pattern as `collectImplicitFeedback`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PR review state fetch | Custom GitHub API client | `gh pr view --json reviews` | Already used by `checkPrStatus`; same Bun.spawn pattern |
| YAML read/write | Custom parser | `readYamlFile()`/`writeYamlFile()` | Already in `yaml-store.ts` |
| Slack API calls | Custom webhook/HTTP client | Slack MCP `slack_read_thread` | Zero new infra; matches D-09 |
| TypeScript union exhaustiveness | Manual string checks | TypeScript discriminated union | Compile-time safety for source/verdict values |

**Key insight:** This phase has almost no new infrastructure to build. The complexity is in correctly wiring existing pieces together across multiple files that must all be updated atomically.

---

## Common Pitfalls

### Pitfall 1: Split Type Update (Partial Migration)
**What goes wrong:** `FeedbackEntry.verdict` type is extended to `'accepted' | 'rejected' | 'uncertain'` in `types.ts`, but the POST `/api/feedback` route still validates only `'accepted' | 'rejected'`. The MCP tool `nw_submit_feedback` also has a hardcoded `z.enum(['accepted', 'rejected'])`. Both will reject `'uncertain'` verdicts submitted by users.
**Why it happens:** The type union is in one file; validation logic is duplicated in `feedback.ts` and `mcp-tools.ts`.
**How to avoid:** Update `FeedbackEntry.verdict` in `types.ts` AND update all places that validate/enumerate verdict values: `feedback.ts` POST validation, `mcp-tools.ts` `nw_submit_feedback` schema.
**Warning signs:** TypeScript will NOT catch this — the runtime validation is a plain string comparison, not typed. Test by POSTing `{"verdict":"uncertain"}` to `/api/feedback`.

### Pitfall 2: Missing Improvement-Log Slack URL on Silent Night
**What goes wrong:** If a run produces no actions (all targets skipped — "silent night"), no Slack post is sent. The next run's Phase 0 reads improvement-log looking for a Slack URL that was never written. If the code expects a URL to always exist, it will throw or produce garbage feedback.
**Why it happens:** The improvement-log entry for a "silent night" run (e.g., 2026-03-24 run 9) contains only skip reasons — no `slack_url` field. The skill's Phase 0 Slack collector must gracefully handle missing `slack_url`.
**How to avoid:** In skill Phase 0, check for `slack_url` existence before calling `slack_read_thread`. If absent, skip Slack reaction collection silently (no warning — it's expected behavior for silent nights).
**Warning signs:** Errors in Phase 0 that mention undefined URL or MCP tool call failure with empty/null channel.

### Pitfall 3: Multiple Reviews — Wrong Aggregation
**What goes wrong:** A PR has two reviewers: one APPROVED, one CHANGES_REQUESTED. Naive code might take the first review or average states. Decision D-17 says "latest review per reviewer" (each reviewer's most recent state wins), but doesn't specify cross-reviewer aggregation.
**Why it happens:** The decision document specifies per-reviewer dedup but leaves cross-reviewer aggregation implicit.
**How to avoid:** Treat CHANGES_REQUESTED as the strongest signal (immediate `return 'rejected'`). Rationale: if any reviewer requests changes, the PR needs work — consistent with the PR lifecycle. Only emit `'accepted'` if at least one APPROVED and no CHANGES_REQUESTED. Emit `'uncertain'` if only COMMENTED reviews exist.
**Warning signs:** Test with mixed-review scenarios: APPROVED + CHANGES_REQUESTED should yield `'rejected'`.

### Pitfall 4: CalibrationData Function Has Hardcoded All-Category Aggregation
**What goes wrong:** `getCalibrationData()` in `feedback-store.ts` currently spreads `explicit_feedback`, `pr_feedback`, and `linear_feedback` into one `all` array. With two new categories, this list must be updated to include `slack_feedback` and `pr_review_feedback`. If not updated, new feedback entries are invisible to calibration.
**Why it happens:** The aggregation list is hardcoded — it's not derived from the `FeedbackStore` keys dynamically.
**How to avoid:** Update `getCalibrationData()`, `getFeedbackForRun()`, and `getFeedbackForSignal()` to include all five categories. Also update `feedback-store.ts` `appendFeedback()` routing.
**Warning signs:** `getCalibrationData()` returns 0 entries for signals that only have `slack_feedback`/`pr_review_feedback` entries.

### Pitfall 5: 'uncertain' Verdict Breaks Frontend Feedback State
**What goes wrong:** `action-card.ts` maintains `submitted` state as `'accepted' | 'rejected' | null`. If a `FeedbackEntry` is loaded as `existingFeedback` with `verdict: 'uncertain'`, the `submitted` state becomes a non-null value that doesn't match either `'accepted'` or `'rejected'` — buttons may render incorrectly.
**Why it happens:** The `existingFeedback` prop type mirrors the old 2-state verdict.
**How to avoid:** The dashboard action-card only handles user-submitted feedback (source: 'user'). User-submitted feedback currently only allows accepted/rejected. `'uncertain'` is reserved for automated sources. The `existingFeedback` prop should stay typed as `'accepted' | 'rejected' | null` — the dashboard shows automated feedback as a separate display (not via action-card buttons). This is a display concern, not a blocking issue, but must be documented in the plan.
**Warning signs:** Type error when passing `uncertain` verdict to `existingFeedback` prop.

---

## Code Examples

### checkPrReviews — new function in feedback-collector.ts

```typescript
// Source: extends checkPrStatus pattern (lines 57-84 of feedback-collector.ts)
// Verified gh pr view --json reviews schema: { reviews: Array<{ author: {login}, state, submittedAt, body }> }
// state values: 'APPROVED' | 'CHANGES_REQUESTED' | 'COMMENTED' | 'DISMISSED'

export async function checkPrReviews(
  prUrl: string
): Promise<'accepted' | 'rejected' | 'uncertain' | null> {
  try {
    const match = prUrl.match(/github\.com\/([^/]+\/[^/]+)\/pull\/(\d+)/)
    if (!match) return null
    const [, repo, prNumber] = match

    const proc = Bun.spawn(
      ['gh', 'pr', 'view', prNumber!, '--repo', repo!, '--json', 'reviews'],
      { stdout: 'pipe', stderr: 'pipe' }
    )
    const stdout = await new Response(proc.stdout).text()
    await proc.exited
    if (proc.exitCode !== 0) return null

    const data = JSON.parse(stdout) as {
      reviews: Array<{ author: { login: string }; state: string; submittedAt: string }>
    }
    if (!data.reviews.length) return null

    // Latest review per reviewer (D-17)
    const byReviewer = new Map<string, { state: string; submittedAt: string }>()
    for (const r of data.reviews) {
      const existing = byReviewer.get(r.author.login)
      if (!existing || r.submittedAt > existing.submittedAt) {
        byReviewer.set(r.author.login, r)
      }
    }

    // Cross-reviewer aggregation: CHANGES_REQUESTED wins over all
    let verdict: 'accepted' | 'rejected' | 'uncertain' | null = null
    for (const { state } of byReviewer.values()) {
      if (state === 'CHANGES_REQUESTED') return 'rejected'
      if (state === 'APPROVED') verdict = 'accepted'
      else if (state === 'COMMENTED' && verdict === null) verdict = 'uncertain'
      // DISMISSED: skip
    }
    return verdict
  } catch {
    return null
  }
}
```

### executor.ts finally block — add PR review check

```typescript
// Source: executor.ts lines 270-302 (fire-and-forget pattern)
// Add inside the existing try block after collectImplicitFeedback:

// EXTFEED-02: Collect PR review feedback
if (actionsWithTargets.length > 0) {
  await collectPrReviewFeedback(actionsWithTargets, appendFeedback)
}
```

### Slack reaction collection — skill Phase 0 (pseudocode for SKILL.md addition)

```markdown
### Step 0.4.x: Collect Slack Reaction Feedback

Read `~/.claude/kc-plugins-config/nightwatch-improvement-log.md` — find the most recent run entry that has a `slack_url` field.

If no `slack_url` found → skip silently (silent night or Slack was unavailable).

If `slack_url` found:
1. Extract channel ID from channels.yaml (`nightwatch` key)
2. Call `slack_read_thread` with the message URL
3. For each reaction in the response:
   - 👍 (`+1`, `thumbsup`) → `accepted`
   - 👎 (`-1`, `thumbsdown`) → `rejected`
   - 🤔 (`thinking_face`) → `uncertain`
   - Other reactions → skip
4. For each mapped reaction, append a FeedbackEntry to nightwatch-feedback.yaml:
   - `signal_id`: derived from improvement-log entry for that run
   - `source: 'slack_reaction'`
   - `verdict`: mapped from reaction
   - `run_id`: from improvement-log entry

If `slack_read_thread` fails → log warning, skip. Never block Phase 1+.
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| 2-state verdict (accepted/rejected) | 3-state (accepted/rejected/uncertain) | Phase 14 | Uncertain reactions no longer inflate reject rate |
| PR status only (merge/close) | PR status + PR review verdicts | Phase 14 | Catch CHANGES_REQUESTED before merge/close |
| Implicit feedback from PR/Linear only | + Slack reactions (👍/👎/🤔) | Phase 14 | Human feedback captured within the run cycle |
| FeedbackStore: 3 categories | FeedbackStore: 5 categories | Phase 14 | `slack_feedback` + `pr_review_feedback` added |

**Nothing deprecated/removed** — all additions are backwards-compatible (new YAML keys don't break existing readers, new source union values don't break existing comparisons).

---

## Open Questions

1. **`collectPrReviewFeedback` as separate function vs integrating into `collectImplicitFeedback`**
   - What we know: D-16 says "Runs in worker `feedback-collector.ts` alongside existing PR merge status check — same function, extended scope"
   - What's unclear: "same function, extended scope" could mean extending `collectImplicitFeedback` to also call `checkPrReviews`, OR adding a second function called from the executor finally block.
   - Recommendation: Add a separate `collectPrReviewFeedback` function (mirrors the existing `collectImplicitFeedback` signature) and call both from the executor finally block. Reason: keeps each function's responsibility clean; avoids making `collectImplicitFeedback` aware of two different `checkPr*` functions.

2. **Dedup: Should PR review feedback suppress PR status feedback for the same signal?**
   - What we know: A merged PR (accepted via `pr_status`) that also had reviews (accepted via `pr_review`) will produce two FeedbackEntry records for the same signal_id.
   - What's unclear: Double-counting in calibration?
   - Recommendation: Allow both entries. They are from different sources and each may represent a real signal. The calibration logic groups by indicator derived from signal_id — having two accepted entries for the same signal is fine (it reinforces the signal). Dedup at the signal level would require knowing whether a signal already has a `pr_status` entry, which adds complexity without clear benefit.

3. **Improvement-log Slack URL field name**
   - What we know: Discretion item — `slack_url` vs `slack_message_ts`.
   - Recommendation: Use `slack_url` (full URL string, e.g., `https://infuseai.slack.com/archives/C0ALTGB9F1A/p1711234567890`). Rationale: readable, self-documenting, directly usable by both MCP calls and future HTTP clients. The `ts` value is embedded in the URL path.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `gh` CLI | PR review fetch | Already in use | (existing) | — |
| Bun | Worker test runner | Already in use | (existing) | — |
| Slack MCP | Skill Phase 0 reaction collection | Session-dependent | n/a | Skip silently (D-09 already accounts for this) |

**All dependencies already present** — no new tooling required.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | bun:test (Bun built-in) |
| Config file | none — Bun auto-discovers `tests/**/*.test.ts` |
| Quick run command | `cd /Users/kent/Project/kc-claude-workspace/kc-claude-plugins/kc-nightwatch/app && bun test tests/worker/feedback-collector.test.ts tests/server/feedback.test.ts` |
| Full suite command | `cd /Users/kent/Project/kc-claude-workspace/kc-claude-plugins/kc-nightwatch/app && bun test` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| EXTFEED-01 | Slack reaction parsed to FeedbackEntry with correct verdict | unit (skill-layer, manual only) | Manual — skill executes in Claude session | N/A — skill behavior |
| EXTFEED-01 | `source: 'slack_reaction'` routes to `slack_feedback` key in appendFeedback | unit | `bun test tests/server/feedback.test.ts` | Extend existing |
| EXTFEED-01 | `slack_feedback` entries included in getCalibrationData() | unit | `bun test tests/server/feedback.test.ts` | Extend existing |
| EXTFEED-02 | `checkPrReviews` returns `accepted` for APPROVED state | unit | `bun test tests/worker/feedback-collector.test.ts` | Wave 0 — new file |
| EXTFEED-02 | `checkPrReviews` returns `rejected` for CHANGES_REQUESTED | unit | `bun test tests/worker/feedback-collector.test.ts` | Wave 0 — new file |
| EXTFEED-02 | `checkPrReviews` returns `uncertain` for COMMENTED | unit | `bun test tests/worker/feedback-collector.test.ts` | Wave 0 — new file |
| EXTFEED-02 | `checkPrReviews` returns `null` for DISMISSED-only reviews | unit | `bun test tests/worker/feedback-collector.test.ts` | Wave 0 — new file |
| EXTFEED-02 | `checkPrReviews` takes latest review per reviewer (D-17) | unit | `bun test tests/worker/feedback-collector.test.ts` | Wave 0 — new file |
| EXTFEED-02 | `checkPrReviews` CHANGES_REQUESTED wins over APPROVED | unit | `bun test tests/worker/feedback-collector.test.ts` | Wave 0 — new file |
| EXTFEED-02 | `source: 'pr_review'` routes to `pr_review_feedback` key | unit | `bun test tests/server/feedback.test.ts` | Extend existing |
| EXTFEED-02 | `pr_review_feedback` entries included in getCalibrationData() | unit | `bun test tests/server/feedback.test.ts` | Extend existing |
| D-01/D-04 | `uncertain` verdict counted in total, not in reject_count | unit | `bun test tests/server/calibration.test.ts` | Extend existing |
| D-01 | POST `/api/feedback` accepts `uncertain` verdict | unit | `bun test tests/server/feedback.test.ts` | Extend existing |
| D-04 | CalibrationData threshold stable with uncertain entries | unit | `bun test tests/server/calibration.test.ts` | Extend existing |

### Sampling Rate
- **Per task commit:** `bun test tests/worker/feedback-collector.test.ts tests/server/feedback.test.ts tests/server/calibration.test.ts`
- **Per wave merge:** `bun test` (full suite — 322 tests currently)
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] New test file `tests/worker/feedback-collector.test.ts` — covers `checkPrReviews()` function (EXTFEED-02 unit tests). File `tests/server/feedback-polling.test.ts` covers `collectImplicitFeedback` but not `checkPrReviews`.
- [ ] Extend `tests/server/feedback.test.ts` — add tests for `slack_reaction` source routing, `pr_review` source routing, `uncertain` verdict in calibration
- [ ] Extend `tests/server/calibration.test.ts` — add test for `uncertain` verdict not counted in `reject_count`

*(Existing `feedback-polling.test.ts` and `feedback.test.ts` cover current behavior; gaps are the new additions only)*

---

## Sources

### Primary (HIGH confidence)
- Direct source read: `app/worker/feedback-collector.ts` — current `checkPrStatus` and `collectImplicitFeedback` implementation
- Direct source read: `app/shared/types.ts` — current `FeedbackEntry` (line 166) and `CalibrationData` (line 176) interfaces
- Direct source read: `app/server/services/feedback-store.ts` — current `appendFeedback`, `getCalibrationData`, `FeedbackStore` interface
- Direct source read: `app/worker/executor.ts` (lines 270-303) — existing finally block feedback wiring pattern
- Live CLI verification: `gh api repos/cli/cli/pulls/9999/reviews` + `gh pr view 9999 --repo cli/cli --json reviews` — confirmed `reviews` JSON schema with real data

### Secondary (MEDIUM confidence)
- `skills/kc-nightwatch/SKILL.md` (Step 0.4) — existing PR/Linear feedback collection pattern and improvement-log format
- `~/.claude/kc-plugins-config/nightwatch-improvement-log.md` — actual improvement-log format (9 runs of real data)
- `~/.claude/kc-plugins-config/channels.yaml` — Slack `nightwatch` channel ID confirmed

### Tertiary (LOW confidence)
- None — all findings are from first-party source code and live tool verification.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; all tooling already in use
- Architecture: HIGH — extends established patterns with minimal new code surface
- Pitfalls: HIGH — all identified by reading actual source code, not speculation
- Skill-layer (EXTFEED-01): MEDIUM — Slack MCP tool names (`slack_read_thread`) are session-dependent; verify tool availability at plan execution time

**Research date:** 2026-03-24
**Valid until:** 2026-04-24 (stable stack; only risk is Slack MCP tool name changes)
