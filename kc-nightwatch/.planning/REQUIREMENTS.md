# Requirements: Nightwatch Dashboard

**Defined:** 2026-03-25
**Core Value:** The closed-loop feedback flywheel — NW monitors, proposes, learns from feedback, and gets measurably better over time.

## v4.0 Requirements

Requirements for feedback trend visualization, signal intelligence, and forge visibility.

### Feedback Visualization

- [ ] **VIZ-01**: Health page shows per-indicator reject rate trend as a sparkline with real historical data (not fake 2-point stub)
- [ ] **VIZ-02**: Health page shows calibration table with current threshold, reject rate, total feedback count, and sample size per indicator
- [ ] **VIZ-03**: Sparkline and trend chart show tooltip with exact value and run ID on hover

### Signal Intelligence

- [ ] **SIG-01**: Each action in run detail has a numeric priority score computed as confidence weight × (1 - reject_rate), and actions are sorted by score descending
- [ ] **SIG-02**: Calibration data is hidden for indicators with fewer than 10 feedback entries (minimum sample gate)
- [ ] **SIG-03**: Calibration threshold uses EMA smoothing (α=0.3) instead of raw all-time average

### Forge Visibility

- [ ] **FORGE-01**: Health page displays forge validation results from the most recent self-repair run (status, branch, details)

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
| VIZ-01 | TBD | Pending |
| VIZ-02 | TBD | Pending |
| VIZ-03 | TBD | Pending |
| SIG-01 | TBD | Pending |
| SIG-02 | TBD | Pending |
| SIG-03 | TBD | Pending |
| FORGE-01 | TBD | Pending |

**Coverage:**
- v4.0 requirements: 7 total
- Mapped to phases: 0 (pending roadmap)
- Unmapped: 7

---
*Requirements defined: 2026-03-25*
