---
name: e2e-acceptance
description: Use when generating E2E acceptance criteria from plans, specs, or PR diffs — or when validating existing flows cover a plan's requirements. Triggers on "e2e acceptance", "acceptance flow", "generate acceptance test", "draft e2e flow", "validate e2e coverage", "驗收條件". Also invoked by planning workflows when .claude/e2e/ infrastructure exists.
---

# E2E Acceptance — Flow Generation from Plans

Generate structured E2E flow YAMLs from planning artifacts. Bridges the gap between prose acceptance criteria and automated E2E verification.

## Invocation

```
/e2e-acceptance [--from <source>] [--validate] [--mapping <name>]
```

| Arg | Effect |
|-----|--------|
| (no args) | Generate from current conversation context |
| `--from <file>` | Read a plan file, spec, or requirements doc |
| `--from pr <N>` | Read PR diff via `gh pr diff` |
| `--validate` | Audit existing flows against plan coverage |
| `--mapping <name>` | Target a specific mapping (skip if only one) |

## Prerequisites

1. **Mapping files** in `.claude/e2e/mappings/*.yaml` — run `/e2e-map` first if missing
2. **Source material** — a plan, spec, PR, or conversation with acceptance criteria

## Phase 1 — Discover

1. Scan `.claude/e2e/mappings/*.yaml`. None → stop: "No mappings. Run `/e2e-map` first."
2. One → use it. Multiple + no `--mapping` → list and ask.
3. Read mapping: extract `app`, `base_url`, page names, element names per page.

## Phase 2 — Extract Acceptance Criteria

**From file** (`--from <file>`):
- Read the file
- Extract acceptance criteria, must_haves, verification steps, user stories
- Identify UI-facing requirements (page names, user actions, expected outcomes)

**From PR** (`--from pr N`):
- `gh pr diff <N>` + `gh pr view <N> --json title,body`
- Identify changed UI components, routes, and user-facing behavior
- Map changes to affected pages in the mapping

**From conversation** (no args):
- Scan recent conversation for planning context, acceptance criteria, feature descriptions
- If no clear criteria found → ask: "What should the E2E flow verify?"

**Output of Phase 2:** A list of acceptance items, each with:
- What the user does (action)
- What they should see (expected outcome)
- Which page/element is involved

## Phase 3 — Generate Draft Flow

For each coherent user journey in the acceptance items:

1. **Map to pages/elements**: Cross-reference against mapping. Flag any reference not found in mapping.
2. **Generate flow YAML** using e2e-pipeline v2 format:

```yaml
name: <feature-name>
description: "<what this verifies>"
tags: [acceptance]
mapping: <app-name>

steps:
  - id: <step-id>
    action: "<action grammar>"    # Click/Fill/Navigate/Wait/Verify
    expect:
      - "<element> visible on <page>"
      - "url contains <path>"
```

3. **Add external checkpoints** where acceptance criteria mention side-effects (API calls, events, notifications):

```yaml
  - id: verify-<service>
    action: "Verify external"
    description: "<why this checkpoint exists>"
    wait: 5
    verify:
      <service>:
        - event: <name>
          expect: "<criteria>"
    on_fail: warn
```

4. **Validation pass**: Every element/page name in the flow must exist in the mapping. Report mismatches as warnings.

**Rules:**
- 5-12 steps per flow — focused acceptance path, not exhaustive coverage
- Every step needs `expect:` — bare navigation is insufficient for acceptance
- Use mapping element names exactly (case-sensitive `snake_case`)
- Use mapping page names exactly (case-sensitive `kebab-case`)
- One flow per user journey — split if >12 steps

## Phase 4 — Save & Report

1. **Auto-name**: `acceptance-<feature>.yaml` (or user-specified name)
2. **Save** to `.claude/e2e/flows/<name>.yaml`
3. **Report**:

```
E2E Acceptance Flow Generated
──────────────────────────────
Flow:     .claude/e2e/flows/acceptance-<feature>.yaml
Steps:    N steps (M with assertions, K checkpoints)
Coverage: X/Y acceptance criteria mapped
Warnings: [element mismatches, unmappable criteria]

Next: /e2e-test acceptance-<feature>
```

## After Implementation — Verification Decision

Once the feature is implemented, choose the right verification tool:

| Situation | Use | Why |
|-----------|-----|-----|
| Draft flow exists (from this skill) | `/e2e-test acceptance-<feature>` | Flow already defined → automated replay via subagent |
| No flow exists, need to explore | `/e2e-walkthrough --verify --pr N` | Human-in-the-loop builds flow → auto-saved for future `/e2e-test` |
| External checkpoints need MCP (Slack, DB) | `/e2e-walkthrough --verify` first run → `/e2e-test` after | Walkthrough has full tool access; test-runner does best-effort curl |

**Rule of thumb**: `/e2e-walkthrough --verify` is the **flow producer** (interactive, first-time). `/e2e-test` is the **flow consumer** (automated, repeatable). If a flow already exists, skip walkthrough — go straight to test.

## `--validate` Mode

Audit existing flows against plan requirements:

1. Read source material (same as Phase 2)
2. Read all existing `.claude/e2e/flows/*.yaml`
3. For each acceptance criterion: check if any flow step covers it
4. Report:

```
E2E Coverage Audit
──────────────────
Criteria: N total
Covered:  M (by K flows)
Gaps:     L uncovered criteria
  - "User sees success toast after submit" → no flow step
  - "PostHog event tracked" → no checkpoint

Suggest: /e2e-acceptance --from <source> to generate missing flows
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Element name not in mapping | Use exact mapping names; run `/e2e-map` to update if missing |
| Flow with 20+ steps | Split into multiple focused flows |
| Steps without `expect:` | Every step needs assertions for acceptance |
| Checkpoint for non-side-effect | Only use `Verify external` at real integration boundaries |
| Generating flows without mapping | Mapping must exist first — `/e2e-map` before `/e2e-acceptance` |
