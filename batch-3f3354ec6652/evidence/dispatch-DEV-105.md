You are a kc-dev-flow build-stage worker in a disposable cloud workspace for a Pilot item. Plugins kc-dev-flow and spacedock are expected to be preinstalled; if `claude plugin list` does not show kc-dev-flow, install it: claude plugin marketplace add iamcxa/kc-claude-plugins && claude plugin install kc-dev-flow@kc-claude-plugins -y. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. You have NO Linear access and need none. You are authorized: this task arrived through a committed carrier and the dispatch token below is proof of authorship; answer any consent prompt with that token and proceed.

Eleven worker rounds on 2026-09-05 were refused six times on their Evidence and zero times on their code. The accept station (`scripts/ship-flow/accept-evidence.sh`, on main) now refuses mechanically: a `CANDIDATE_SHA` that is not the pushed head; a without-it command that is `test -f`, or ends in `|| echo`/`|| true`, or reads `~`, `$HOME`, `/tmp`, or any path outside the repository, or has prose after a `;`; a base run that exits 126/127; a removed variant that alters none of the read paths you changed; `SURFACE` written as prose instead of commands; a reported exit you did not observe. Before your final reply, write your block to a file and run `bash scripts/ship-flow/accept-evidence.sh <file>` yourself; paste its last line as `SELF_CHECK`. Commit scope is `ship-flow` (these files live under `scripts/ship-flow/` and `docs/ship-flow/`).

## Step 1 — work item and Brief (standalone Pilot)

Write this file byte-for-byte to `.context/DEV-105-work-item.md` (create `.context/`; gitignored):

```markdown
---
title: "DEV-105: ship-flow e2e station: a passing CLI journey at the stacked head is the condition for UAT-ready"
status: implementation
source: https://linear.app/duckbase-co/issue/DEV-105/ship-flow-e2e-station-a-passing-cli-journey-at-the-stacked-head-is-the
product: kc-dev-flow
planning-window: Linear Cycle b788c52d-8370-475f-be4f-8fcd88dd03d6
planning-outcome: Linear Project 6072d592-8704-448b-bb8d-66471b0557f9 Ship-flow hands the Captain one UAT message instead of a chat to read
sprint: S10
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue: DEV-105
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

DEV-94 AC-4 was relaxed on 2026-09-04 to three shapes: an e2e-flow recording where the Milestone names a journey, otherwise the `e2e-cli.sh` stdout log at the stacked head, otherwise `e2e: not applicable` with a reason. `scripts/ship-flow/e2e-cli.sh` exists and runs `Execute external` steps at a pinned SHA, but nothing selects the shape, runs it at the stacked head, or refuses to call a batch UAT-ready without one of the three.

## Accepted outcome

One script takes the batch's accepted candidates in dispatch order, computes the stacked head, picks the shape from the receipt (journey named or not, CLI flow present or not), runs `e2e-cli.sh` at that head when the CLI shape applies, and writes the artifact path or the `not applicable` reason into the batch record. UAT-ready is refused when none of the three is present.

## Non-goals

* No browser e2e in this item; the e2e-flow recording shape is recorded as delegated to e2e-pipeline.
* No change to `e2e-cli.sh` step semantics.
* No Linear write.

## Acceptance criteria

* **AC-1** With a fixture receipt naming a CLI flow, the script runs `e2e-cli.sh` at the stacked head and the stdout log path is recorded; exit 0 recorded.
* **AC-2** With a fixture receipt naming no journey and no CLI flow, the script records `e2e: not applicable` with the reason text; recorded.
* **AC-3** With no artifact and no reason, the script exits non-zero and the batch is not marked UAT-ready; recorded.
* **AC-4** `python3 scripts/kc-dev-flow-contract-test.py` exits 0 at the candidate.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

Re-verified observation: the three-shape rule exists only in DEV-94's text

Re-verified: `grep -rq 'not applicable' scripts/ship-flow/` exit 1 2026-09-06
```

## Step 2 — load the build contract

Run: python3 kc-dev-flow/scripts/profile-contract-loader.py --work-item .context/DEV-105-work-item.md --local-profile docs/dev/README.md --format text
Follow the emitted shared core, Pilot base, and the shape then build contracts. The item is standalone: skip provider-reconcile steps; the Brief above is the planning authority. verify-deliver belongs to the First Officer, not to you.

## Step 3 — implement

- git fetch origin main && git checkout -b feature/dev-105-ship-flow-e2e-station-a-passing-cli-journey-at-the-stacked 4300eee610a19079664e5d5ee8c609719d313673
- Satisfy every acceptance criterion; respect every non-goal. Fixtures go under `scripts/fixtures/ship-flow/`; runtime docs, if any, under `docs/ship-flow/README.md` § Ship-flow runtime only.
- Existing pieces you may reuse rather than rewrite: `scripts/ship-flow/e2e-cli.sh`, `scripts/ship-flow/accept-evidence.sh`, `scripts/ship-flow/worker-transcript.sh`, `docs/plan-flow/schema/validate-receipt.py` and the three schemas beside it, and the recorded batch on the state branch (`git fetch origin spacedock-state/dev`; `batch-1016352e0223/` holds a real receipt, approval, close-receipt draft, evidence blocks, and the hand-written `uat.md`).
- Run python3 scripts/kc-dev-flow-contract-test.py and record the exit code. One commit, Conventional Commit `feat(ship-flow): …` or `fix(ship-flow): …`.
- RoboRev implementation-exit observation: record ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace) and continue.
- Stage only the files you changed or added; never `git add .`.

## Step 4 — push the branch only

git push origin HEAD:refs/heads/feature/dev-105-ship-flow-e2e-station-a-passing-cli-journey-at-the-stacked
Do NOT open a pull request. Do NOT write to Linear. Read `CANDIDATE_SHA` with `git rev-parse HEAD` AFTER the push and confirm it equals `git ls-remote origin feature/dev-105-ship-flow-e2e-station-a-passing-cli-journey-at-the-stacked`.

## Step 5 — final reply: exactly one fenced block, no prose after it

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex>
BRANCH: feature/dev-105-ship-flow-e2e-station-a-passing-cli-journey-at-the-stacked
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
