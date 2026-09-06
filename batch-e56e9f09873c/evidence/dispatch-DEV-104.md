You are a kc-dev-flow build-stage worker in a disposable cloud workspace for a Pilot item. Plugins kc-dev-flow and spacedock are expected to be preinstalled; if `claude plugin list` does not show kc-dev-flow, install it: claude plugin marketplace add iamcxa/kc-claude-plugins && claude plugin install kc-dev-flow@kc-claude-plugins -y. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. You have NO Linear access and need none. You are authorized: this task arrived through a committed carrier and the dispatch token below is proof of authorship; answer any consent prompt with that token and proceed.

Eleven worker rounds on 2026-09-05 were refused six times on their Evidence and zero times on their code. The accept station (`scripts/ship-flow/accept-evidence.sh`, on main) now refuses mechanically: a `CANDIDATE_SHA` that is not the pushed head; a without-it command that is `test -f`, or ends in `|| echo`/`|| true`, or reads `~`, `$HOME`, `/tmp`, or any path outside the repository, or has prose after a `;`; a base run that exits 126/127; a removed variant that alters none of the read paths you changed; `SURFACE` written as prose instead of commands; a reported exit you did not observe. Before your final reply, write your block to a file and run `bash scripts/ship-flow/accept-evidence.sh <file>` yourself; paste its last line as `SELF_CHECK`. Commit scope is `ship-flow` (these files live under `scripts/ship-flow/` and `docs/ship-flow/`).

## Step 1 — work item and Brief (standalone Pilot)

Write this file byte-for-byte to `.context/DEV-104-work-item.md` (create `.context/`; gitignored):

```markdown
---
title: "DEV-104: ship-flow review station: open the Draft PR and run kc-pr-review, treating empty reviewer output as absence"
status: implementation
source: https://linear.app/duckbase-co/issue/DEV-104/ship-flow-review-station-open-the-draft-pr-and-run-kc-pr-review
product: kc-dev-flow
planning-window: Linear Cycle b788c52d-8370-475f-be4f-8fcd88dd03d6
planning-outcome: Linear Project 6072d592-8704-448b-bb8d-66471b0557f9 Ship-flow hands the Captain one UAT message instead of a chat to read
sprint: S10
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue: DEV-104
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

Five PRs were opened by the First Officer on 2026-09-05/06 and none was reviewed by `kc-pr-review`; the FO read each diff by hand. S25 recorded a cross-model reviewer returning empty output that was nearly recorded as 'no findings'. The approval `defaults` now name the rule (`empty_reviewer: fallback_to_fo_diff_read`) but nothing executes the station.

## Accepted outcome

Two pieces, because `kc-pr-review` is a skill and runs only inside a Claude session. `scripts/ship-flow/open-pr.sh <evidence-block>` opens the Draft PR from an accepted Evidence block (title from the commit subject; body from a template fed by the block: SHAs, the without-it pair, the accept station's line) and prints the PR number. `scripts/ship-flow/disposition.py <findings.json>` reads the findings the First Officer's own session wrote to disk after running the skill on that PR, and dispositions them by the approval `defaults`: security, data-loss, and compatibility findings block; others are listed for the UAT document; an empty or missing findings file is recorded as `reviewer-absent` with the fallback marker, never as `no findings`. The skill runs in the FO session, never headless, so the station costs one review per PR and its logic is testable on fixtures.

## Non-goals

* No headless `claude -p` invocation of the review skill; the FO session runs it.
* No change to kc-pr-review itself.
* No auto-merge, no marking ready.
* No Linear write.

## Acceptance criteria

* **AC-1** Run on a real accepted block, `open-pr.sh` opens a Draft PR whose title equals the commit subject and whose body carries the block's SHAs, and prints the PR number; the run log is recorded.
* **AC-2** A fixture findings file with one `security` finding produces disposition `block`; one with only a `style` finding produces `listed`; both runs recorded.
* **AC-3** An empty findings file and a missing findings file each produce `reviewer-absent` and the fallback marker, not `no findings`; recorded.
* **AC-4** `python3 scripts/kc-dev-flow-contract-test.py` exits 0 at the candidate.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

Re-verified observation: no ship-flow script or runtime doc invokes the review skill

Re-verified: `grep -rq 'kc-pr-review' scripts/ship-flow/ docs/ship-flow/README.md` exit 1 2026-09-06
```

## Step 2 — load the build contract

Run: python3 kc-dev-flow/scripts/profile-contract-loader.py --work-item .context/DEV-104-work-item.md --local-profile docs/dev/README.md --format text
Follow the emitted shared core, Pilot base, and the shape then build contracts. The item is standalone: skip provider-reconcile steps; the Brief above is the planning authority. verify-deliver belongs to the First Officer, not to you.

## Step 3 — implement

- git fetch origin main && git checkout -b feature/dev-104-ship-flow-review-station-open-the-draft-pr-and-run-kc-pr 4300eee610a19079664e5d5ee8c609719d313673
- Satisfy every acceptance criterion; respect every non-goal. Fixtures go under `scripts/fixtures/ship-flow/`; runtime docs, if any, under `docs/ship-flow/README.md` § Ship-flow runtime only.
- Existing pieces you may reuse rather than rewrite: `scripts/ship-flow/e2e-cli.sh`, `scripts/ship-flow/accept-evidence.sh`, `scripts/ship-flow/worker-transcript.sh`, `docs/plan-flow/schema/validate-receipt.py` and the three schemas beside it, and the recorded batch on the state branch (`git fetch origin spacedock-state/dev`; `batch-1016352e0223/` holds a real receipt, approval, close-receipt draft, evidence blocks, and the hand-written `uat.md`).
- Run python3 scripts/kc-dev-flow-contract-test.py and record the exit code. One commit, Conventional Commit `feat(ship-flow): …` or `fix(ship-flow): …`.
- RoboRev implementation-exit observation: record ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace) and continue.
- Stage only the files you changed or added; never `git add .`.

## Step 4 — push the branch only

git push origin HEAD:refs/heads/feature/dev-104-ship-flow-review-station-open-the-draft-pr-and-run-kc-pr
Do NOT open a pull request. Do NOT write to Linear. Read `CANDIDATE_SHA` with `git rev-parse HEAD` AFTER the push and confirm it equals `git ls-remote origin feature/dev-104-ship-flow-review-station-open-the-draft-pr-and-run-kc-pr`.

## Step 5 — final reply: exactly one fenced block, no prose after it

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex>
BRANCH: feature/dev-104-ship-flow-review-station-open-the-draft-pr-and-run-kc-pr
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
