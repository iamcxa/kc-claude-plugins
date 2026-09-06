You are a kc-dev-flow build-stage worker running as a LOCAL subagent (not a cloud workspace) for a Pilot item, DEV-106. Work only inside your own git worktree; never touch the repository checkout you were launched from. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. Do NOT read or write Linear even though a key may be in the environment. Do NOT open a pull request. Do NOT run `git add .`. Do NOT send any Slack message to a real channel: `notify.sh` must take the channel and a `--dry-run` flag, and every run you record uses `--dry-run` writing the message it would send to a file; the First Officer sends the real one.

Set up first:
- REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1 ; git -C "$REPO" fetch origin main spacedock-state/dev
- WT=$(mktemp -d)/wt ; git -C "$REPO" worktree add "$WT" 4300eee610a19079664e5d5ee8c609719d313673 ; cd "$WT" — every command below runs in $WT.
- The batch record you consume lives on the state branch: `git show origin/spacedock-state/dev:batch-1016352e0223/evidence/uat.md` (the hand-written document AC-1 compares against), `…/receipt/plan-receipt.json`, `…/receipt/plan-approval.json`, `…/evidence/worker-evidence-DEV-9*.md`, `…/receipt/close-receipt.DRAFT.json`; and the current batch under `batch-e56e9f09873c/` (README.md holds the `defaults` decisions list, `evidence/claim-*.txt`, `evidence/worker-evidence-*-accepted.md`). Read them with `git show`; do not check out the state branch.
- When done, push your branch with `git push origin HEAD:refs/heads/<branch>` and leave the worktree in place.

The accept station (`scripts/ship-flow/accept-evidence.sh`, present in your worktree) refuses mechanically: a `CANDIDATE_SHA` that is not the pushed head; a without-it command that is `test -f`, or ends in `|| echo`/`|| true`, or reads `~`, `$HOME`, `/tmp`, or any path outside the repository, or has prose after a `;`; a base run that exits 126/127; a removed variant that alters none of the read paths you changed; `SURFACE` written as prose instead of commands; a reported exit you did not observe. Before your final reply, write your block to a file inside the worktree and run `bash scripts/ship-flow/accept-evidence.sh <file>` yourself; paste its last line as `SELF_CHECK`. Commit scope is `ship-flow`.

## Step 1 — work item and Brief (standalone Pilot)

Write this file byte-for-byte to `.context/DEV-106-work-item.md` (create `.context/`; gitignored):

```markdown
---
title: "DEV-106: ship-flow handoff: one UAT document and one Slack message, generated from the batch record"
status: implementation
source: https://linear.app/duckbase-co/issue/DEV-106/ship-flow-handoff-one-uat-document-and-one-slack-message-generated
product: kc-dev-flow
planning-window: Linear Cycle b788c52d-8370-475f-be4f-8fcd88dd03d6
planning-outcome: Linear Project 6072d592-8704-448b-bb8d-66471b0557f9 Ship-flow hands the Captain one UAT message instead of a chat to read
sprint: S10
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue: DEV-106
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

The UAT document for batch 1016352e0223 was written by hand; `uat-doc.py` survives only in DEV-67's evidence directory on the state branch. No Slack message has ever been sent by ship-flow; the Captain learned a batch was ready by reading the chat. The Captain's stated day shape ends with 'one UAT document and one Slack ping'.

## Accepted outcome

`scripts/ship-flow/uat-doc.py` moves into the repository and reads the batch record (accepted blocks, PR numbers and SHAs, review dispositions, e2e artifact, every decision the `defaults` made) into one markdown document; `scripts/ship-flow/notify.sh` sends exactly one Slack message carrying the document link, idempotent on the batch id so a re-run sends nothing.

## Non-goals

* No Slack for anything other than UAT-ready.
* No change to the UAT document's meaning: it lists, it does not decide.
* No Linear write.

## Acceptance criteria

* **AC-1** Run on batch 1016352e0223's recorded evidence the generator reproduces the hand-written `uat.md` section for section; diff recorded.
* **AC-2** The generated document lists every `defaults` decision from the batch record; count recorded against the record.
* **AC-3** `notify.sh` run twice for the same batch id sends one message; both runs and the message id recorded.
* **AC-4** `python3 scripts/kc-dev-flow-contract-test.py` exits 0 at the candidate.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

Re-verified observation: the generator is not in the repository; grep -rqi slack scripts/ship-flow/ also exits 1

Re-verified: `test -f scripts/ship-flow/uat-doc.py` exit 1 2026-09-06
```

## Step 2 — load the build contract

Run: python3 kc-dev-flow/scripts/profile-contract-loader.py --work-item .context/DEV-106-work-item.md --local-profile docs/dev/README.md --format text
Follow the emitted shared core, Pilot base, and the shape then build contracts. The item is standalone: skip provider-reconcile steps; the Brief above is the planning authority. verify-deliver belongs to the First Officer, not to you.

## Step 3 — implement

- git fetch origin main && git checkout -b feature/dev-106-ship-flow-handoff-one-uat-document-and-one-slack-message 4300eee610a19079664e5d5ee8c609719d313673
- Satisfy every acceptance criterion; respect every non-goal. Fixtures go under `scripts/fixtures/ship-flow/`; runtime docs, if any, under `docs/ship-flow/README.md` § Ship-flow runtime only.
- Existing pieces you may reuse rather than rewrite: `scripts/ship-flow/e2e-cli.sh`, `scripts/ship-flow/accept-evidence.sh`, `scripts/ship-flow/worker-transcript.sh`, `docs/plan-flow/schema/validate-receipt.py` and the three schemas beside it, and the recorded batch on the state branch (`git fetch origin spacedock-state/dev`; `batch-1016352e0223/` holds a real receipt, approval, close-receipt draft, evidence blocks, and the hand-written `uat.md`).
- Run python3 scripts/kc-dev-flow-contract-test.py and record the exit code. One commit, Conventional Commit `feat(ship-flow): …` or `fix(ship-flow): …`.
- RoboRev implementation-exit observation: record ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace) and continue.
- Stage only the files you changed or added; never `git add .`.

## Step 4 — push the branch only

git push origin HEAD:refs/heads/feature/dev-106-ship-flow-handoff-one-uat-document-and-one-slack-message
Do NOT open a pull request. Do NOT write to Linear. Read `CANDIDATE_SHA` with `git rev-parse HEAD` AFTER the push and confirm it equals `git ls-remote origin feature/dev-106-ship-flow-handoff-one-uat-document-and-one-slack-message`.

## Step 5 — final reply: exactly one fenced block, no prose after it

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex>
BRANCH: feature/dev-106-ship-flow-handoff-one-uat-document-and-one-slack-message
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
