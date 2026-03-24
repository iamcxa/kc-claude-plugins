# Phase 14: Extended Feedback - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-24
**Phase:** 14-extended-feedback
**Areas discussed:** Reaction → verdict mapping, Polling strategy, Slack MCP scope, PR review comment depth

---

## Reaction → Verdict Mapping

| Option | Description | Selected |
|--------|-------------|----------|
| Add 'uncertain' verdict | 3-state: accepted/rejected/uncertain — maps all reactions and PR review states | ✓ |
| Binary only, ignore 🤔 | Skip uncertain reactions — simplest but loses data | |
| Binary, 🤔 = rejected | Treat uncertainty as negative — over-penalizes ambiguous signals | |

**User's choice:** Add 'uncertain' verdict (recommended)
**Notes:** No additional notes.

---

## Polling Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| On-next-run | Check reactions/reviews at start of next run — same as existing PR status polling | ✓ |
| Post-run delayed check | 4h timer after each run — faster but needs scheduling infrastructure | |
| Manual trigger only | User-initiated — breaks 'automatic' requirement | |

**User's choice:** On-next-run (recommended)
**Notes:** No additional notes.

---

## Slack MCP Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Skill-side via MCP | Use existing Slack MCP in nightwatch skill Phase 0 — zero new tokens/setup | ✓ |
| Slack Web API in worker | Direct fetch() with SLACK_BOT_TOKEN — all feedback in worker but significant setup | |
| Spawn Claude session | Worker spawns lightweight Claude session for MCP — expensive and unreliable | |

**User's choice:** Skill-side via MCP, with explicit requirement that architecture supports future Slack Bot API backend
**Notes:** User concerned about Slack API complexity. Chose MCP-first approach but insisted on abstraction layer so Bot API can be swapped in later for bot-identity operations.

---

## PR Review Comment Depth

| Option | Description | Selected |
|--------|-------------|----------|
| Top-level verdict only | approve=accepted, request-changes=rejected, comment=uncertain | ✓ |
| Top-level + comment count | Verdict + inline comment count — low complexity increase | |
| Full content parsing | Parse inline comment bodies — needs NLP, far beyond scope | |

**User's choice:** Top-level verdict only (recommended)
**Notes:** No additional notes.

---

## Claude's Discretion

- Collector interface design for MCP → Bot API swap
- Batch vs individual Slack MCP calls
- Slack MCP failure handling
- Improvement-log field naming for Slack message URL
- CalibrationData changes for 3-state verdict

## Deferred Ideas

None — discussion stayed within phase scope.
