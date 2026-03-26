---
created: 2026-03-16T07:09:44.040Z
title: Add Verify external support to e2e-flow-writer
area: e2e-pipeline
files:
  - e2e-pipeline/agents/e2e-flow-writer.md
  - e2e-pipeline/skills/e2e-flow/SKILL.md
  - e2e-pipeline/skills/e2e-flow/reference.md
---

## Problem

The e2e-test-runner agent (§ 2m) fully supports `action: "Verify external"` with curl-based API verification checkpoints. But the flow-writer agent cannot generate these steps autonomously — it doesn't know the pattern exists.

Gap found during PR #1028 review (Langfuse v5 migration): needed to hand-write `verify-langfuse-v5-tracing.yaml` because the flow-writer couldn't produce external verification steps.

**3 files missing the pattern:**

1. **e2e-flow-writer.md Step 3 — Action types**: Does not list `Verify external` as a valid action type. The writer cannot generate external verification steps.
2. **e2e-flow/SKILL.md Phase 1**: No mention of external verification as a generation pattern. The orchestrator skill doesn't prompt the flow-writer for these steps.
3. **e2e-flow/reference.md**: No section on external verification patterns or API query templates.

**Evidence:** `verify-posthog.yaml` and `verify-langfuse-v5-tracing.yaml` both had to be hand-written.

## Solution

1. Add `Verify external` to flow-writer § Step 3 action types with `verify:` block schema and examples
2. Add detection heuristic: when `source_text` mentions external services (PostHog events, Langfuse traces, Sentry errors, webhook calls), auto-generate verification checkpoint steps
3. Add "External Verification Templates" section to reference.md with curl patterns for common services (PostHog, Langfuse, generic REST API)
4. Update SKILL.md Phase 1 to mention identifying external verification opportunities from PR diffs / specs
