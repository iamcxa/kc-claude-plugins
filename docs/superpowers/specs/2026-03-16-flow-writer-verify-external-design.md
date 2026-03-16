# Design: Add Verify External Support to e2e-flow-writer

**Date**: 2026-03-16
**Origin**: `.planning/todos/pending/2026-03-16-add-verify-external-support-to-e2e-flow-writer.md`
**Approach**: B — Active Discovery (orchestrator scans, flow-writer generates)

## Problem

The e2e-test-runner (§ 2m) fully supports `action: "Verify external"` checkpoints, but the flow-writer agent cannot generate them — it doesn't know the pattern exists. Flows requiring external verification (PostHog events, Langfuse traces, webhooks) must be hand-written.

Evidence: `verify-posthog.yaml` and `verify-langfuse-v5-tracing.yaml` were both manually authored.

## Design Decision

**Why Approach B over A (passive) or C (structured handoff)**:

- A leaves a blind spot: conversation-mode invocations (no `source_text`) give the flow-writer zero external service context. The orchestrator's codebase scan currently only discovers routes, components, and API endpoints.
- C requires a new `external_hints` field in the input contract, coupling the orchestrator to service-specific semantics and adding maintenance burden.
- B extends the existing `context_summary` free-text convention with an "External services detected" section — no contract change, consistent with existing patterns.

## Changes (5 points)

### 1. `agents/e2e-flow-writer.md` — Step 3 + Step 4

Add `Verify external` to the action types list with:

- `verify:` block schema: service-grouped checks with `event:`, `check:`, `expect:`, `properties:`, `on_fail:`
- Detection heuristic (text parsing): parse `source_text` (if provided) and the "External services detected" section of `context_summary` for analytics/tracing/webhook signals. The flow-writer does NOT run grep itself — it reads text assembled by the skill.
- Cap: prefer max 2 checkpoint steps per flow. If the feature has more than 2 integration points, group related checks into a single checkpoint step using multiple service groups.
- Construction rule 8: `Verify external` steps are **exempt from rule 1** (`expect:` requirement). They MUST have `description:` and `verify:` (not `expect:`). No page/element refs needed.
- Step 4 (Validation Pass): Skip page/element cross-check for `Verify external` steps. Validate that `verify:` block is present and non-empty instead.

Step schema:

```yaml
- id: verify-<service>-<what>
  action: "Verify external"
  description: "<why this checkpoint exists>"
  wait: 10
  verify:
    <service-name>:
      - event: <event_name>
        expect: "<natural language assertion>"
      - check: "<natural language description>"
  on_fail: warn  # warn (default) | fail | block
```

### 2. `skills/e2e-flow/reference.md` — Two new sections

**(A) Codebase Scan Strategy > External Service Discovery**

Grep patterns for common SDK integrations:

```
posthog\.capture|posthog\.identify|analytics\.track
langfuse\.trace|langfuse\.generation|langfuse\.span
sentry\.captureException|sentry\.captureMessage
webhook|sendWebhook|notifyExternal
fetch\(.*(slack|discord|sendgrid|twilio)
SLACK_WEBHOOK|DISCORD_WEBHOOK|SENDGRID_API|TWILIO_
```

Uses grep only (no file reads) to stay within the 20 file-read budget. Results added to `context_summary`:

```
External services detected:
  PostHog: src/lib/analytics.ts — capture('cta_clicked', { page, variant })
  Langfuse: src/lib/tracing.ts — langfuse.trace({ name: 'ai-chat' })
```

**(B) External Verification Templates**

Three generation templates for the flow-writer:

1. **Analytics** (PostHog, Mixpanel) — `event:` + `expect:` + `properties:`
2. **Tracing** (Langfuse, Sentry) — `check:` natural language
3. **Generic** (REST, webhook, database) — `check:` natural language with `custom:` service key

These parallel `references/common-patterns.md` execution patterns but are framed as generation guidance.

### 3. `skills/e2e-flow/SKILL.md` — Phase 0 additions

**(A) Codebase Scan paragraph**: Add sentence referencing `reference.md § External Service Discovery`.

**(B) Present Plan template**: Add `External: <N> service integrations detected` line.

### 4. Impact Matrix Verification

Files already supporting `Verify external` (no changes needed):

| File | Status |
|------|--------|
| `skills/e2e-test/SKILL.md` § External Verification | Complete |
| `skills/e2e-walkthrough/reference.md` serialization | Complete |
| `agents/e2e-test-runner.md` § 2m | Complete |
| `references/common-patterns.md` | Complete |
| `CLAUDE.md` draft flow template | Complete |

### 5. `agents/e2e-flow-verifier.md` — Pass-through rule

The flow-verifier runs generated flows in a real browser for validation. It currently has **zero awareness** of `Verify external` steps and would attempt element resolution on them, causing failures.

Add a pass-through rule to the step execution logic: when `action` is `"Verify external"`, skip all browser interaction (snapshot, click, element resolution), log as `status: skip` with reason "External checkpoint — handled by test-runner at execution time", and continue to the next step.

This mirrors the test-runner's checkpoint concept but without attempting any curl/API calls — the verifier's job is browser validation, not external service checks.

## Out of Scope

- No changes to the compiler (`resolver.js`, `migrate.js`) — already handles `verify-external` type
- No changes to `e2e-test-runner.md` — already has full § 2m support
- No changes to flow-writer input contract — `context_summary` is free-text, no schema change needed
- No new service-specific detection beyond grep patterns — flow-writer uses natural language, not structured matching

## Addendum: Execute External (added during implementation)

During evaluation of the Recce Cloud test case (browser → CLI → browser → PostHog), a gap was identified: `Verify external` is passive (check things) but the case needed active execution (do things). Added `Execute external` as a symmetric counterpart.

**Schema**: `execute:` block with `run:`, `repeat:`, `expect:` per entry. `wait_after:` for post-execution delay. Default `on_fail: fail`.

**Additional files changed** (11 total, beyond original 5):
- `agents/e2e-test-runner.md` — § 2b action table + § 2n execution logic
- `skills/e2e-test/SKILL.md` — action syntax line
- `skills/e2e-walkthrough/reference.md` — serialization rule
- `references/common-patterns.md` — CLI, API, data seeding patterns
- `CLAUDE.md` — draft flow template
- `compiler/` — resolver.js, migrate.js, codegen.js, coverage.js (all SKIP in CI, 470/470 tests pass)

## Implementation

Used `/e2e-skill-ops --add-feature` + `superpowers:writing-skills` TDD cycle (RED → GREEN → REFACTOR).
