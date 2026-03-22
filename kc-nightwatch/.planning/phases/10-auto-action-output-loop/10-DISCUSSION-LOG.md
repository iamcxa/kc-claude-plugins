# Phase 10: Auto-Action Output Loop - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-22
**Phase:** 10-auto-action-output-loop
**Areas discussed:** Auto-create trigger scope, Dedup + outcome storage model, NW-Claude outcomes MCP tools

---

## Auto-Create Trigger Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Production only | Only production mode auto-creates. Dry-run stays preview-only. Self-repair uses its own PR flow. | ✓ (with manual opt-in) |
| Production + dry-run opt-in | Production auto-creates by default. Dry-run can opt-in with a flag. | |
| All modes except self-repair | Both production and dry-run auto-create. | |

**User's choice:** Production only + manual trigger opt-in checkbox
**Notes:** User added "手動時應該可選，例如我想快速測試行為" — manual triggers should have a toggleable auto-create checkbox for testing purposes.

---

## Dedup + Outcome Storage Model

| Option | Description | Selected |
|--------|-------------|----------|
| outcomes.yaml + branch/signal dedup | New outcomes.yaml for queryable aggregate. PR dedup via `gh pr list --head {branch}`. Linear dedup via outcomes.yaml lookup. | ✓ |
| Inline in run records only | No separate file. Query all RunSummaries. | |
| Both inline + aggregate | Duplicated data in both locations. | |

**User's choice:** outcomes.yaml + branch/signal dedup
**Notes:** User reviewed YAML preview showing outcome records with type, target, signal_id, url, status fields.

---

## NW-Claude Outcomes MCP Tools

| Option | Description | Selected |
|--------|-------------|----------|
| 2 tools: list + status | nw_get_outcomes (list with filters) + nw_get_outcome_status (poll live status). | |
| 1 tool: list only | Single tool, no live polling. | |
| 3 tools: list + status + summary | Adds nw_outcome_summary for aggregated stats. | ✓ |

**User's choice:** 3 tools (list + status + summary)
**Notes:** User chose 3 tools over recommended 2 — wants dedicated summary tool for overview questions.

---

## Claude's Discretion

- pr-creator.ts / linear-creator.ts structure
- System prompt injection approach
- outcome-store.ts implementation
- outcomes.yaml file path
- Chat manager tool registration
- Error handling for gh CLI failures

## Deferred Ideas

None — discussion stayed within phase scope
