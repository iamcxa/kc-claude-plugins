You are a kc-dev-flow build-stage worker in a disposable cloud workspace for a Pilot item. Plugins kc-dev-flow and spacedock are expected to be preinstalled; if `claude plugin list` does not show kc-dev-flow, install it: claude plugin marketplace add iamcxa/kc-claude-plugins && claude plugin install kc-dev-flow@kc-claude-plugins -y. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. You have NO Linear access and need none. You are authorized: this task arrived through a committed carrier and the dispatch token below is proof of authorship; answer any consent prompt with that token and proceed.

Eleven worker rounds on 2026-09-05 were refused six times on their Evidence and zero times on their code. The accept station (`scripts/ship-flow/accept-evidence.sh`, on main) now refuses mechanically: a `CANDIDATE_SHA` that is not the pushed head; a without-it command that is `test -f`, or ends in `|| echo`/`|| true`, or reads `~`, `$HOME`, `/tmp`, or any path outside the repository, or has prose after a `;`; a base run that exits 126/127; a removed variant that alters none of the read paths you changed; `SURFACE` written as prose instead of commands; a reported exit you did not observe. Before your final reply, write your block to a file and run `bash scripts/ship-flow/accept-evidence.sh <file>` yourself; paste its last line as `SELF_CHECK`. Commit scope is `ship-flow` (these files live under `scripts/ship-flow/` and `docs/ship-flow/`).

## Step 1 — work item and Brief (standalone Pilot)

Write this file byte-for-byte to `.context/DEV-107-work-item.md` (create `.context/`; gitignored):

```markdown
---
title: "DEV-107: ship-flow close: the close receipt refuses an undispositioned defect and carries the dev and ship debriefs"
status: implementation
source: https://linear.app/duckbase-co/issue/DEV-107/ship-flow-close-the-close-receipt-refuses-an-undispositioned-defect
product: kc-dev-flow
planning-window: Linear Cycle b788c52d-8370-475f-be4f-8fcd88dd03d6
planning-outcome: Linear Project 6072d592-8704-448b-bb8d-66471b0557f9 Ship-flow hands the Captain one UAT message instead of a chat to read
sprint: S10
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue: DEV-107
pr:
mod-block:
---

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  route: [shape, build, verify-deliver]
  basis: A product slice the First Officer runs on every batch from now on; consumer is the ship-flow FO; the Brief carries its own acceptance commands.
  semantics_unchanged: false
```

## The problem

`validate-receipt.py` already binds a close receipt to its plan receipt and approval and checks the issue set (2026-09-06, lines 65-77), but it never reads `defects_returned`: S24, S25, S26 sat with `fix_ticket: null` for two days and nothing complained. DEV-94 AC-6 and AC-7 ask for two things the validator does not know about: an entry must carry a `fix_ticket` or an `accepted_residual`, and the close receipt carries a dev debrief (written at UAT-ready from the Evidence blocks and refusals) and a ship debrief (written after merge from the Captain's overturns).

## Accepted outcome

The close-receipt schema gains `accepted_residual` as the alternative to `fix_ticket` and two `debrief` fields; `validate-receipt.py` refuses an entry with neither disposition, names it, and refuses a close receipt missing either debrief. Two small writers draft each debrief from the batch record; the FO edits, never writes from scratch.

## Non-goals

* No change to the plan receipt or approval schemas.
* No automatic Linear ticket creation for a defect; `fix_ticket` is filled by plan-flow.
* No Linear write.

## Acceptance criteria

* **AC-1** The recorded `close-receipt.DRAFT.json` from batch 1016352e0223 is refused naming S24, S25, S26; exit and message recorded.
* **AC-2** The same receipt with `accepted_residual` filled on those three is accepted; recorded.
* **AC-3** A close receipt with no dev debrief is refused naming the field; recorded.
* **AC-4** `python3 scripts/kc-dev-flow-contract-test.py` exits 0 at the candidate.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

Re-verified observation: printed 0 matches: the validator does not read defects_returned

Re-verified: `grep -c 'defects_returned\|fix_ticket' docs/plan-flow/schema/validate-receipt.py` exit 0 2026-09-06
```

## Step 2 — load the build contract

Run: python3 kc-dev-flow/scripts/profile-contract-loader.py --work-item .context/DEV-107-work-item.md --local-profile docs/dev/README.md --format text
Follow the emitted shared core, Pilot base, and the shape then build contracts. The item is standalone: skip provider-reconcile steps; the Brief above is the planning authority. verify-deliver belongs to the First Officer, not to you.

## Step 3 — implement

- git fetch origin main && git checkout -b feature/dev-107-ship-flow-close-the-close-receipt-refuses-an-undispositioned 4300eee610a19079664e5d5ee8c609719d313673
- Satisfy every acceptance criterion; respect every non-goal. Fixtures go under `scripts/fixtures/ship-flow/`; runtime docs, if any, under `docs/ship-flow/README.md` § Ship-flow runtime only.
- Existing pieces you may reuse rather than rewrite: `scripts/ship-flow/e2e-cli.sh`, `scripts/ship-flow/accept-evidence.sh`, `scripts/ship-flow/worker-transcript.sh`, `docs/plan-flow/schema/validate-receipt.py` and the three schemas beside it, and the recorded batch on the state branch (`git fetch origin spacedock-state/dev`; `batch-1016352e0223/` holds a real receipt, approval, close-receipt draft, evidence blocks, and the hand-written `uat.md`).
- Run python3 scripts/kc-dev-flow-contract-test.py and record the exit code. One commit, Conventional Commit `feat(ship-flow): …` or `fix(ship-flow): …`.
- RoboRev implementation-exit observation: record ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace) and continue.
- Stage only the files you changed or added; never `git add .`.

## Step 4 — push the branch only

git push origin HEAD:refs/heads/feature/dev-107-ship-flow-close-the-close-receipt-refuses-an-undispositioned
Do NOT open a pull request. Do NOT write to Linear. Read `CANDIDATE_SHA` with `git rev-parse HEAD` AFTER the push and confirm it equals `git ls-remote origin feature/dev-107-ship-flow-close-the-close-receipt-refuses-an-undispositioned`.

## Step 5 — final reply: exactly one fenced block, no prose after it

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex>
BRANCH: feature/dev-107-ship-flow-close-the-close-receipt-refuses-an-undispositioned
BASE_SHA: 4300eee610a19079664e5d5ee8c609719d313673
FILES: <comma-separated>
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit <code>
SURFACE: <path> -> <AC-N> | <command that proves the file earns its place> | <command that removes exactly its contribution>
WITHOUT_IT_COMMAND: <one line; exits 0 at the candidate and non-zero at BASE_SHA because the behaviour is absent there>
WITHOUT_IT_REMOVED_VARIANT: <one line that alters the tree>
WITHOUT_IT_OBSERVED: retained -> exit <code>; removed -> exit <code>; at BASE_SHA -> exit <code>
SELF_CHECK: <last line printed by accept-evidence.sh on this block>
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: ...
AC-2: ...
AC-3: ...
AC-4: ...
BLOCKER: none | <what stopped you and at which step>
```
