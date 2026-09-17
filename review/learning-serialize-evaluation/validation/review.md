# validation gate — learning-serialize-evaluation

Recommendation: approve. Validation attempt 3 recommends PASSED on candidate `93258e23`
(branch `spacedock-ensign/learning-serialize-evaluation`, base `32cd8890`).

## Candidate

Diff from `32cd8890`: `kc-dev-flow-2/scripts/learning.py`,
`kc-dev-flow-2/scripts/test_learning.py`, `kc-dev-flow-2/skills/learn/SKILL.md`,
`kc-dev-flow-2/README.md`. Full suite 21 tests OK; `lint-skills.py` PASS (FO re-ran the
suite at `93258e23`).

## Evidence that decided it

- AC-1..AC-4: at least one named mutation per criterion re-run by an independent
  validator on a scratch copy, each failing its catching test; F1 and F2 mutations each
  isolate to exactly their own new test.
- The #469/#470 shape reproduced and refused through CLI calls in a disposable
  repository; release, stale digest, re-claim and 12-process concurrent claims exercised.
- AC-4 amendment: zero lines removed from the `32cd8890` test file; the old test file
  fails exactly the two tests whose setup changed.
- `job_key`, `inspect`, `delivery_plan`, `observation`, `inspect_delivery` carry no
  removed lines; completed-record immutability and delivery boundary tests pass.

## Rounds

1. Attempt 1 (`b2984a12`): F1, F2 Material (committed tests missing for AC-4 and D3
   mutations); F3–F5 Polish. Captain returned it; fixed in `6b511198`.
2. Attempt 2 (`6b511198`): F6, F7 Polish (docs contradicted code); F8 declined. Captain
   returned it; fixed in `93258e23` (docs only).
3. Attempt 3 (`93258e23`): no new findings.

## Recorded limits

- The store lock has no timeout; a frozen claimer holds new claims until it exits.
- A corrupted `release.json` leaves the job blocking; only manual repair clears it.
- F8: `release`'s explicit open/merged/closed refusal is redundant with the next check;
  behaviour is tested, that message is not.
- Coordination across clones or machines is out of scope.
