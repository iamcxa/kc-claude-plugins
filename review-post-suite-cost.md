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

Roughly two seconds per assertion is the real number to attack. Each recorded event forks
`python3` (RFC3339 conversion, safe I/O) and several `jq` invocations, and each scenario pays
two `mktemp -d` plus a state-root teardown. Nothing here is algorithmically expensive; it is
process startup, paid hundreds of times.

Worth measuring before choosing a fix — the cheapest candidates are batching the python3 date
conversions (or replacing them with shell arithmetic where the format allows), reusing one
state root across scenarios that do not need isolation, and collapsing the per-event `jq`
pipelines. A parallel-by-suite CI matrix would cut wall-clock without touching the cost, and is
the fallback if the per-assertion cost turns out to be irreducible.

This is maintenance economics, not correctness: every future entity in this area pays the tax,
and the 10-minute cancellation showed the failure mode is a **silent** one — a suite that passes
and is killed anyway reads as a red X with no failing assertion to point at.

**AC-1 — The full `typed review runtime contract` job completes measurably faster on the same assertion count.**
Verified by: the job's wall-clock before and after on the same commit range, plus the
per-assertion cost derived from the suite's own totals. Falsified by: no measurable improvement,
or an improvement bought by running fewer assertions.
