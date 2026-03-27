# Requirements: Nightwatch Dashboard

**Defined:** 2026-03-25
**Core Value:** The closed-loop feedback flywheel — NW monitors, proposes, learns from feedback, and gets measurably better over time.

## v4.0 Requirements

Requirements for feedback trend visualization, signal intelligence, and forge visibility.

### Feedback Visualization

- [x] **VIZ-01**: Health page shows per-indicator reject rate trend as a sparkline with real historical data (not fake 2-point stub)
- [x] **VIZ-02**: Health page shows calibration table with current threshold, reject rate, total feedback count, and sample size per indicator
- [x] **VIZ-03**: Sparkline and trend chart show tooltip with exact value and run ID on hover

### Signal Intelligence

- [ ] **SIG-01**: Each action in run detail has a numeric priority score computed as confidence weight × (1 - reject_rate), and actions are sorted by score descending
- [x] **SIG-02**: Calibration data is hidden for indicators with fewer than 10 feedback entries (minimum sample gate)
- [x] **SIG-03**: Calibration threshold uses EMA smoothing (α=0.3) instead of raw all-time average

### Forge Visibility

- [x] **FORGE-01**: Health page displays forge validation results from the most recent self-repair run (status, branch, details)

## Future (v4.1+)

- Auto-calibration wire-up: propagate computed thresholds back to kc-nightwatch skill pipeline
- Signal priority influence on pipeline execution order

## Out of Scope

| Feature | Reason |
|---------|--------|
| Multi-user / sharing | Deferred to v5.0 — requires auth, RBAC, remote access |
| Historical run comparison | Data structure doesn't support diff; high cost, low ROI |
| Smart scheduling | Interval scheduling is sufficient for single user |
| Charting library (uPlot, Chart.js, D3) | No-build constraint; extend existing SVG components instead |
| Auto-calibration skill wire-up | Crosses app/plugin boundary; display-only in v4.0 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| VIZ-01 | Phase 15 (verified in Phase 18) | Complete |
| SIG-02 | Phase 15 (verified in Phase 18) | Complete |
| SIG-03 | Phase 15 (verified in Phase 18) | Complete |
| VIZ-02 | Phase 16 | Complete |
| VIZ-03 | Phase 16 | Complete |
| FORGE-01 | Phase 16 | Complete |
| SIG-01 | Phase 17 → **Phase 19** (wire fix) | Pending |

**Coverage:**
- v4.0 requirements: 7 total
- Satisfied: 6 (VIZ-01, VIZ-02, VIZ-03, SIG-02, SIG-03, FORGE-01)
- Pending: 0
- Unsatisfied: 1 (SIG-01 — code gap, Phase 19)
- Mapped to phases: 7

---
*Requirements defined: 2026-03-25*
*Traceability updated: 2026-03-27 (Phase 18 verification closure complete)*
