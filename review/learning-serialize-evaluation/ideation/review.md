# ideation gate — learning-serialize-evaluation

Recommendation: approve the design with D1, D2 and D3 as recommended.

## Design under review

Entity Design section at state commit `7ea6a081` (correction round 1), AC-4 amended
at `8da2de79` on the Captain's ruling.

- `claim` for a new job scans every other job in the local learning store under a
  store lock (`kc-dev-flow-2/learning.lock`, beside the learning directory) and refuses,
  naming each blocking job, while any is pending, unreadable, or completed with a
  proposal whose delivery is missing, uncertain or open and not released.
- `release --job --expected --owner --reason` writes only `release.json` for a
  proposal the Captain declines to deliver. No CLI command removes it.
- No change to completed records, `job_key` or delivery identity rules. Only `merged`
  is regression-guarded; a `closed` delivery re-recorded as `open` re-blocks at the next
  scan (pre-existing path, unchanged).

## Independent review

`kc-dev-flow-2:engineering-reviewer` (Sonnet) on `768da417`: READY-WITH-FIXES.
Stop condition confirmed not triggered by code trace; the #469/#470 shape reproduced in
a disposable repository at `32cd8890`; notice-digest compatibility confirmed for
acknowledged jobs; no scope removable without breaking an AC. Five fixes, all applied
in correction round 1: name the existing tests the hold breaks (two of fourteen, per a
`/tmp` prototype run), move the lock out of the learning directory, correct the
`closed` monotonicity claim, state the lock's dependency on D1, pin `release` check
order. The corrected revision was not re-reviewed.

## Decisions for the Captain

- **D1** — a job whose record is torn or missing blocks new claims. Cost: a crashed
  claim holds all other jobs until `recover` then `complete`. The store lock's scope
  relies on this; ruling the other way widens the lock.
- **D2** — `release` is allowed when delivery is missing, or uncertain but reconciled to
  a confirmed absent PR; unreconciled uncertain is refused.
- **D3** — a released job cannot be delivered through the recorder later.

## Evidence limits

All acceptance tests are implementation-stage checks; none exist yet. The `/tmp`
prototype that measured the two broken tests is not the candidate.
