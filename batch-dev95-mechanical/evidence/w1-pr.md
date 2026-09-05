## What

plan-flow's eight-rule lint moves from a POC's evidence directory on the state branch into `docs/plan-flow/plan-lint.py`, and gains an offline mode: `fetch <project-id> <snapshot.json>` runs the same GraphQL query it always did and saves the result; `lint <snapshot.json> [receipt.json]` runs the rules over a saved snapshot with no network. The close-receipt schema joins the two schemas already under `docs/plan-flow/schema/`. Two real Linear project snapshots become fixtures under `scripts/fixtures/plan-flow/`, and the contract test pins every new path and runs `lint` over one of them.

## Why

Every plan round so far began by copying files out of state-branch evidence by hand, and the lint could only run by whoever held the Linear API key. Nothing pinned any of it: a refactor could have deleted the lint and no check would have said so.

## Rules do not change

The eight `rule()` calls are byte-identical to v0 (checked by the First Officer at the candidate). Two known defects are reproduced and recorded here as the baseline a separate item fixes against:

- L6 passes the DEV-67 fixture whose `blocks` relations are inverted (S22) — a DAG check cannot see a semantic inversion.
- Nothing refuses a by-product Issue (S26) or an Issue with no re-verified observation (S27).

## Verified by the First Officer

- Accept station (`scripts/ship-flow/accept-evidence.sh`): ACCEPT. `CANDIDATE_SHA` equals the remote head; the without-it pair is `plan-lint.py lint <fixture>`, which exits 2 at `BASE_SHA` because python cannot open a file that does not exist there, and 0 at the candidate.
- `lint` over the correct-relations fixture reproduces the recorded DEV-89 run rule-for-rule (all eight PASS, order DEV-90, DEV-91, DEV-92); the receipt hash differs because the snapshot is normalized JSON, not the live response.
- Contract test: exit 0 at the candidate; exit 1 naming `docs/plan-flow/plan-lint.py` when it is deleted.

## Residual

Round 1 of this item was refused on its Evidence, not its code: its without-it line ended in `&& echo PASS || echo FAIL`, which exits 0 whatever happens. The code is the same commit in both rounds.

Part of DEV-95 (POC 3: plan-flow end to end). AC-5 of seven.
