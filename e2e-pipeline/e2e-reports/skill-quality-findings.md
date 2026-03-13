# E2E Skill Quality Findings

Persistent record of skill gaps, fixes, and feature additions. Referenced by `/e2e-skill-ops` on every invocation.

## New Features

### 2026-03-14: PR Pre-Flight E2E Suggestion + External Verification Checkpoints

**Feature A — PR Pre-Flight E2E Suggestion**
- **What**: kc-create-pr Step 1.5 detects integration changes (frontend + backend in same diff) and suggests running e2e verification before PR creation
- **Where**: `kc-pr-flow/skills/kc-create-pr/SKILL.md` + `kc-pr-flow/reference/e2e-verification.md`
- **Cross-plugin**: kc-pr-flow → e2e-pipeline (soft dependency, degrades to skip)

**Feature B — External Verification Checkpoints**
- **What**: `action: "verify-external"` step type in flow YAML. Lets the LLM pause e2e execution to verify external services (PostHog, Langfuse, DB, Slack, any HTTP endpoint). Semi-structured `verify:` block with natural language `check:` / `expect:` / `note:` fields.
- **Where**: e2e-test SKILL.md (spec), e2e-test-runner agent (execution), e2e-walkthrough SKILL.md (--verify + checkpoint), common-patterns.md (examples)
- **Design source**: Natural version from `recce-cloud-infra/.claude/e2e/flows/support-escalation-with-verification.yaml` — adopted checkpoint-as-full-step pattern over field-on-browser-step

**Key design decisions**:
- Checkpoint is an independent step, not a field on browser steps
- `verify:` uses semi-structured YAML (service grouping + natural language), not pure NL strings
- `on_fail: warn` default — checkpoints don't block flow unless explicitly set to `fail` or `block`
- Config missing → SKIP with warning (flow works without external service setup)
- Walkthrough (main context) = full tool access for checkpoints; Test (subagent) = best-effort via Bash/curl

## Findings

### 2026-03-14: Impact scan gaps found and fixed

Post-implementation impact scan (Explore agent) found 7 gaps across 4 files:

| # | Gap | Severity | Fix |
|---|-----|----------|-----|
| 1 | e2e-test-runner § 2b action table missing `"Verify external"` | HIGH | Already added during implementation |
| 2 | Report template missing Checkpoint Results section | HIGH | Added to § 3c template |
| 3 | e2e-dispatch missing `--verify` routing + quick ref | HIGH | Added to --walk dispatch + quick reference |
| 4 | e2e-test SKILL.md missing execution model cross-link | MEDIUM | Added paragraph linking to test-runner § 2m |
| 5 | Flow schema exemption wording unclear | MEDIUM | Clarified: "no page/element refs, must have verify:" |
| 6 | Test-runner § 2m missing field reference | MEDIUM | Added field list (event, check, expect, properties, note) |
| 7 | Test-runner missing checkpoint critical rule | LOW | Added rule #13 about best-effort execution |

**Lesson**: Cross-skill features need explicit cross-links. The e2e-test SKILL.md defines the spec but the test-runner executes it — both must reference each other.
