---
title: The shell suites cost ~2s per assertion, so CI time tracks assertion count
status: backlog
source: found while landing reconcile-degraded-mode-symmetry (sv) on 2026-07-26 — its 16 new assertions cancelled CI at the 10-minute cap
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: qhr529c1ha214hbef794dm6v
---

`review-post.test.sh` took **4m13s for 122 assertions** on main and **~5m for 138**; the whole
`typed review runtime contract` job ran **9m07s against a 10-minute cap**, i.e. 53 seconds of
margin. `sv` added sixteen assertions and the job was cancelled mid-suite — every suite passed,
the step was killed in the same second it printed its result, and the following step never ran.
The cap has been raised to 20 minutes so the tree is not one commit away from red, but that
buys time rather than fixing anything.

Measured on 2026-07-26 rather than guessed, and the first guess in this file was wrong:
**`python3` is the entire problem and `jq` is innocent.**

| binary | per call |
|---|---|
| `python3 -c 'pass'` | **565 ms** |
| `shasum -a 256` | 18.7 ms |
| `mktemp -d` | 14.2 ms |
| `jq -n '1'` | **6.8 ms** |

Read the CPU accounting, not just the clock: 50 python3 launches took 28.3s wall at **0% CPU**.
Nothing computes — each `exec` blocks on interception (sandbox policy evaluation, signature
verification, or an EDR hook). The same launch is ~20-30 ms on the Linux CI runner, which
accounts for the whole 6-7x local/CI gap.

The multiplier is the second half. One `review-post.sh post` — a single operation appending
about four events — spawns **65 python3 processes**, roughly sixteen launches per recorded
event, all for RFC3339 conversion and the safe-I/O helper. Both are small string operations.

So the fix is high-leverage, cheap, and helps CI rather than only this machine: get 65 into
single digits. Candidates, cheapest first — hold one long-lived helper process instead of one
per call; do the date conversion in shell, where the fixed `%Y-%m-%dT%H:%M:%SZ` format allows
it; batch the safe-I/O calls belonging to a single append. Reusing a state root across scenarios
that need no isolation is a test-side win on top. A parallel-by-suite CI matrix cuts wall-clock
without touching the cost and is the fallback if the per-call cost proves irreducible.

This is maintenance economics, not correctness: every future entity in this area pays the tax,
and the 10-minute cancellation showed the failure mode is a **silent** one — a suite that passes
and is killed anyway reads as a red X with no failing assertion to point at.

**AC-1 — The full `typed review runtime contract` job completes measurably faster on the same assertion count.**
Verified by: the job's wall-clock before and after on the same commit range, plus the
per-assertion cost derived from the suite's own totals. Falsified by: no measurable improvement,
or an improvement bought by running fewer assertions.
