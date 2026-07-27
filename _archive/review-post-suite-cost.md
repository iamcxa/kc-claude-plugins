---
title: The shell suites cost ~2s per assertion, so CI time tracks assertion count
status: done
source: found while landing reconcile-degraded-mode-symmetry (sv) on 2026-07-26 — its 16 new assertions cancelled CI at the 10-minute cap
started: 2026-07-26T06:41:37Z
completed: 2026-07-27T15:41:00Z
verdict: passed
worktree: ~/mini-legs/dev-qhr529c1-suite-cost
issue:
pr: pr-merge:67
design: required
id: qhr529c1ha214hbef794dm6v
archived: 2026-07-27T15:41:00Z
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

**AC-2 — One `review-post.sh post` spawns fewer than ten `python3` processes.**
Verified by: counting spawns for a single `post` on the same scenario before and after
(`65` on `9ae5e81`). Falsified by: the count staying in double digits, or falling only because
work moved into a different interpreter spawn.

## Design determination: `required` — decided by the FO, not yet EM-reviewed

Recorded 2026-07-26 when this was dispatched to the mini. **This is an FO design call made to
unblock a headless leg; it has not passed an EM gate.** The validation gate must review the
choice itself, not only its execution. If the choice is wrong, the leg's work is the cost.

The entity named four candidates. Two are chosen, one is deferred, one is ruled out:

- **Chosen — do the RFC3339 conversion in shell.** The format is fixed
  (`%Y-%m-%dT%H:%M:%SZ`), so it needs no interpreter.
- **Chosen — batch the safe-I/O calls belonging to a single append.** Sixteen spawns per
  recorded event is the multiplier; one per append is the target.
- **Deferred — a long-lived helper process.** It is the largest change and introduces process
  lifecycle into a script that currently has none. Only if the two above miss AC-2.
- **Ruled out — the parallel-by-suite CI matrix.** It cuts wall-clock without touching cost,
  and it edits `.github/workflows/**`, which the mini's machine account cannot push (its token
  has no `workflow` scope). It stays the fallback for a human-pushed follow-up, not this slice.

Measured on the mini 2026-07-26 while siting this work: `python3` costs **25 ms** per launch
there against this MacBook's **565 ms**, and `jq` 2.5 ms against 6.8 ms. That 22× gap confirms
the 565 ms is MacBook-specific exec interception rather than a property of the suite — but it
does **not** weaken the case, because at CI's comparable per-launch cost 65 spawns still
dominate the ~2 s per assertion. It does mean the improvement ratio must be reported from a
machine whose per-launch cost resembles CI's, and the mini is such a machine.
