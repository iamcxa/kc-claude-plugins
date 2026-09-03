# UAT: The three ship-flow guarantees are written down and pinned

Plan receipt `1016352e02231945` · approval go/3/2/2 · dispatch order DEV-90 -> DEV-91 -> DEV-92 · batch `batch-1016352e0223`

Each accepted layer is one Draft PR at one pinned candidate on top of the previous layer's candidate. DEV-91 is accepted without a PR (its goal was met by DEV-90). All Linear state untouched by the FO.


## Layer 1: DEV-90 — Write the three ship-flow contract sentences into the runtime README

- PR: (pending Captain approval) · candidate `00d2dbf5d2a2` · base `d98f40b5e208` (main) · branch `feature/dev-90-write-the-three-ship-flow-contract-sentences-into-the`
- Intent adopted on the state branch (first receipt-driven dispatch through intent-commit fencing)
- Without-it (worker one-liner, FO ran verbatim): retained 0, removed 1 · surface-map-check OK (3 files) · contract test PASS · Codex no findings
- How to verify: `docs/dev/README.md` has one pointer line where `## Ship-flow runtime` was; `docs/ship-flow/README.md` § Ship-flow runtime holds the section plus three `(DEV-67)` sentences; remove any of the three and `kc-dev-flow-contract-test.py` reddens naming it.

## Layer 2: DEV-91 — Pin the three contract sentences to the contract test

- Outcome: **accepted without PR**. Candidate `00c4c05be6ea` adds a second pin loop for the same three sentences DEV-90 already pins; its without-it cannot fail (S24) and, with only DEV-90's pins, removing a sentence still reddens the test. Minimal necessity: nothing to ship. The Issue's goal is met by DEV-90.
- How to verify: same mutation as layer 1; observe the failure message names the guarantee. That is DEV-91's AC-1 satisfied by DEV-90's code.

## Layer 3: DEV-92 — Observe three ship-flow UATs for re-derivation

- PR: (pending Captain approval) · candidate `9c05eaf86e74` · base `00d2dbf5d2a2` (DEV-90) · branch `feature/dev-92-observe-three-ship-flow-uats-for-re-derivation-of-the-three`
- Deliverable is the observation template `docs/ship-flow/evidence/uat-observations/README.md`; the three records are produced by the FO at UAT time (this batch's own three PRs count if the Captain agrees).
- Without-it: retained 0, removed 1 · surface-map-check OK · contract test PASS · FO review no findings (Codex endpoint 404 at review time, S25)
- How to verify: file exists with the field list and the verdict rule (three files, zero `rederived: yes`).

## Not handed off

- none stuck; DEV-91 is dispositioned above.

## For the Captain

- Two delivery units to approve (DEV-90 on main; DEV-92 stacked on DEV-90). Suggested: `gh stack link` DEV-90 -> DEV-92 after both PRs exist, since DEV-92's base is DEV-90's candidate.
- DEV-91: accept the disposition (goal met by DEV-90, no PR) or ask for a distinct deliverable.
- Residual outside all three Briefs: the Codex reviewer produced empty output on two layers (endpoint 404); the FO read both diffs (6 and 39 lines) instead.
