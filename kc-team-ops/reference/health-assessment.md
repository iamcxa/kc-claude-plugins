# Health Assessment Heuristic

Guide for assessing project health in pulse updates. Health is a communication signal to the team, not a performance metric.

## Decision Matrix

Evaluate each milestone independently, then roll up to project level (worst milestone wins). Milestones without target dates are informational — exclude from rollup unless they contain blockers or overdue issues.

### onTrack

All of:
- Milestone progress % is proportional to elapsed time (e.g., 50%+ at cycle midpoint)
- No unresolved blockers
- Remaining work is assigned and scoped
- Previous update was also onTrack or issues have been resolved

### atRisk

Any of:
- Milestone progress significantly behind timeline (e.g., <30% with <3 days to target)
- Issues on the critical path unassigned or scope unclear
- Dependencies on external teams/decisions not yet resolved
- Target date needs adjustment (even if work is progressing)
- New scope added mid-cycle without timeline extension

### offTrack

Any of:
- Milestone will definitely miss target without scope reduction or deadline extension
- Critical blocker with no resolution path
- Key contributor unavailable and no backup
- Milestone progress <10% with target within current cycle

## Nuances

### Progress % is auto-calculated
Linear computes milestone progress from issue completion ratio. A milestone at 13% might be fine if only 1 large issue exists and it's 80% code-complete. Conversely, 70% might be misleading if the remaining 30% is the hardest part.

**Always contextualize the number.** The pulse update body explains why the health assessment makes sense despite the raw %.

### Scope changes affect health
Moving issues between milestones is a legitimate planning tool, not a failure signal. **Evaluate health against the post-adjustment scope**, not the original scope. But when issues move *out* of a milestone to meet a deadline, note it explicitly. If >50% of original scope was moved out, default to atRisk regardless of remaining progress — the scope reduction itself is a signal.

> PROJ-101 moved to M2 — not feasible in this cycle. PROJ-102 provides the primary error visibility needed for now.

### atRisk is the most useful signal
Teams benefit most from early atRisk signals. Waiting until offTrack reduces options. Default to atRisk when uncertain between onTrack and atRisk.

### Target date shifts require explanation
When recommending a target shift, always include:
1. What's causing the delay (specific issues/blockers)
2. New proposed timeline (cycle number)
3. What's still being delivered on time

## Examples

### onTrack despite low %
> M1 at 50% but the only remaining item (PROJ-103, E2E validation) is assigned and scoped. Core plugin + MCP work complete. On track to close this week.

**Why onTrack:** Progress % misleading because completed items were the heavy work.

### atRisk with active work
> M1 at 25% with target tomorrow. PROJ-104 and PROJ-105 are in flight but won't close before cycle ends. Moving target to Cycle N+1.

**Why atRisk:** Work is progressing but timeline needs adjustment. Team should know.

### onTrack after scope adjustment
> M1's primary goal achieved with PROJ-102. PROJ-101 moved to M2. M1 ready to close.

**Why onTrack:** Scope was adjusted, but the adjusted scope is delivered. Transparent about what moved.
