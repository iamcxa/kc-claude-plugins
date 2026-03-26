# Phase 16: Health Page Enrichment - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-26
**Phase:** 16-health-page-enrichment
**Areas discussed:** Page Layout, ForgeResultCard Design, Calibration Table Placement, Tooltip Interaction Design

---

## Page Layout

| Option | Description | Selected |
|--------|-------------|----------|
| Forge → Targets → Calibration | Forge card at top (system-level), target cards middle, calibration table bottom, reject rate charts last | ✓ |
| Targets → Calibration → Forge | Target cards first, calibration middle, forge at bottom | |
| 3 Tabs (Health / Calibration / Forge) | Each tab focuses one aspect | |

**User's choice:** Forge → Targets → Calibration
**Notes:** User selected recommended option. Rationale: system-level health check first for quick glance, per-target detail in the middle, cross-target summary at bottom.

---

## ForgeResultCard Design

| Option | Description | Selected |
|--------|-------------|----------|
| Expandable card | Collapsed = status line (icon + pass/fail + time), click to expand branch + details. Stale = muted color. | ✓ |
| Simple status line | One line: icon + status + date. Compact but insufficient for failure details. | |
| Fixed size card | Always shows all info (status + branch + details). No click needed but takes space. | |

**User's choice:** Expandable card
**Notes:** Balances space efficiency (pass = one line) with detail availability (fail = expand for branch + details).

---

## Calibration Table Placement

| Option | Description | Selected |
|--------|-------------|----------|
| Single flat table | All indicators in one table sorted by reject rate. Matches API response shape. | ✓ |
| Per-target grouped table | Sub-tables per target. Requires extra indicator→target mapping not in CalibrationData. | |
| Embedded in target card | Table inside each target card. Makes cards too long, mixes concerns. | |

**User's choice:** Single flat table
**Notes:** CalibrationData API returns flat list without target grouping. Indicator names are self-descriptive. Table positioned below targets implies summary/aggregate view.

---

## Tooltip Interaction Design

| Option | Description | Selected |
|--------|-------------|----------|
| Custom tooltip div | Invisible SVG hit areas + absolute positioned div. Full style control, multi-line (value + run ID). | ✓ |
| Native SVG title | Browser native tooltip via `<title>`. Simple but uncontrollable style, delayed, single line. | |

**User's choice:** Custom tooltip div

### Sub-decision: Data Shape for Run IDs

| Option | Description | Selected |
|--------|-------------|----------|
| Parallel arrays | Add `runIds?: string[]` to Sparkline Props. Minimal change, LineChart untouched. | ✓ |
| Structured array | Change to `data: {value, runId}[]`. Cleaner but larger refactor, affects LineChart too. | |

**User's choice:** Parallel arrays
**Notes:** Minimum viable change — optional `runIds` prop, tooltip degrades gracefully when absent.

---

## Claude's Discretion

- Tooltip positioning logic (above/below/auto)
- Sparkline hit area sizing
- ForgeResultCard animation
- Calibration table empty state
- Section dividers between page regions

## Deferred Ideas

- Tooltip on LineChart (reject rate charts)
- Calibration table column sort toggle
- ForgeResultCard → GitHub PR link (needs safehouse `gh` auth verification)
