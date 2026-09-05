## What

Three rules join plan-flow's lint, each reading the project snapshot only:

| rule | refuses | first caught by |
|---|---|---|
| **L6 direction** | a `blocks` edge that points against the Issues' intended order; the order comes from the identifiers, not from the relations being checked | S22: DEV-67's fixture had every edge inverted and the DAG check passed |
| **L9 by-product** | an Issue whose every claimed surface is already claimed by an earlier Issue in dispatch order | S26: DEV-91's only surface was `scripts/kc-dev-flow-contract-test.py`, which DEV-90 also named |
| **L10 re-verified** | an Issue with no `Re-verified:` line carrying a command, an exit, and a date within 14 days | S27: two of four candidates in a plan round were already fixed |

The DEV-89 snapshot with conforming `Re-verified:` lines added is committed as a third fixture, and the contract-test pin runs it, because the recorded fixtures now correctly fail L10.

## Why the direction rule cannot reuse the relations

A lint consistent with its own input cannot catch a semantic inversion; the fixture's author and the lint shared one wrong belief about `issueRelationCreate`'s argument order. The identifier order is an independent signal. It catches S22; a Project whose intended order is not numeric would false-fail it, which is the recorded residual.

## Verified by the First Officer at the candidate

- Accept station (`accept-evidence.sh` on main): ACCEPT. `CANDIDATE_SHA` equals the remote head; the without-it pair greps for the direction rule's FAIL line on the inverted fixture and restores the base lint as its variant — exit 1 at `BASE_SHA`, 0 at the candidate.
- L6 FAILs the inverted fixture naming `(DEV-66, DEV-65), (DEV-65, DEV-64)`; PASSes the correct one.
- L9 FAILs `DEV-91: only surface scripts/kc-dev-flow-contract-test.py already claimed by DEV-90`; PASSes DEV-90 and DEV-92.
- L10 FAILs both recorded fixtures; PASSes the `-reverified` copy.
- L1–L8 outcomes on both fixtures are identical before and after (diffed by the FO; the worker's own AC-4 line said "differences" without saying which, and the difference is the new rules' lines, not the old ones').
- Mutation: with the direction comparison removed, the inverted fixture passes L6 again.

## Residual

- Round 1 was refused on its Evidence, not its rules: `SURFACE` as a bullet list, a without-it that exited 0 on both sides, a variant written as a sentence. Same commit lineage; round 2 fixed the block and the L9 message.
- The 14-day bound in L10 is a first value, stated in the rule's output, not a measured one.

Stacked on #375 (AC-5), which this depends on. Part of DEV-95 (POC 3). AC-3, AC-6, AC-7 of seven.
