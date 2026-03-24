# Phase 15: Data Layer Foundations - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.

**Date:** 2026-03-25
**Mode:** Interactive (discuss)

## Gray Areas Discussed

### 1. Trend Bucketing Strategy
**Options presented:** Per-run-id (recommended), Per-week, Per-day
**Selected:** Per-run-id + 30-run window cap
**Rationale:** Natural alignment with existing run-based architecture. Cap prevents unbounded growth.

### 2. EMA Calibration Tuning
**Options presented:** Raw average (current), EMA α=0.3 (recommended), Windowed average
**Selected:** EMA α=0.3 + minimum N=10 gate
**Rationale:** Standard signal processing. Gate prevents small-N volatility. α not configurable (premature).

### 3. Forge Data Source
**Options presented:** New /api/forge/results (recommended), Extend /api/config/warnings
**Selected:** New /api/forge/results endpoint
**Rationale:** Semantic separation — forge results are quality checks, not config warnings.

### 4. New API Surface Design
**Options presented:** 3 new endpoints, Extend existing, 2 new + 1 extend (recommended)
**Selected:** Trends extends calibration endpoint, forge and priority are new endpoints
**Rationale:** Trends and calibration share data source (feedback.yaml). Forge and priority are different domains.

## Notes

- User requested recommendations with pros/cons analysis for all areas
- All recommendations accepted without modification
- Discussion mode: "給我建議與理由正反" (give me recommendations with pros/cons)
