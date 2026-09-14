---
title: "The boot message names the delivery order and the forbidden actions: push and open the Draft PR before preparing validation; never create repositories, change settings or branch protection, or run CI off the PR branch"
status: backlog
source: "measured on ship-cloud-wrapper-r3, 2026-09-14/15 (questions log on spacedock-state/ship); Captain 2026-09-15 「r4 現在開」"
product: kc-ship-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r4
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: v9mf30n3s03ev5dvtn08vsed
---

bite: (1) 2026-09-14, two of five r3 workers (`pr-merge-released-body-pin-per-mod-version`, `ship-watch-runs-without-conductor-sql`) prepared their validation gate with the candidate existing only in the sandbox — no branch on origin, no PR — so the ship FO could not verify at a pinned SHA and had to message each worker to push first (two extra rounds, ~20 minutes each). (2) 2026-09-14, the `adopter-contract-test-ships-with-the-package` worker pushed a fixture branch to iamcxa/kc-claude-plugins for a live Actions probe (two runs, Kent pays the minutes), attempted `gh repo create` (403) and `PUT repos/…/branches/main/protection` (403); nothing changed only because the token lacked scope. The boot message (dispatch.sh 0.2.0 + #445 wording) forbids merging and gate decisions but says nothing about repository settings, repository creation, or CI runs outside the PR's own branch, and does not order delivery before validation.

consumer: every cloud worker booted by `kc-ship-flow/scripts/dispatch.sh` (`--message-file` boot) and `--resume`; the ship FO's watch, which reads the state branch expecting a pinned candidate at validation.

## Accepted outcome

A worker that reaches validation has already pushed its branch and opened the Draft PR, and no worker attempts an outward-facing repository action.

## Acceptance criteria

* **AC-1** The boot header (both dispatch and resume) carries, verbatim: "Before preparing the validation gate: push your branch to origin and open the Draft PR through the pr-merge mod; the gate question names the PR number and the candidate SHA." Verified by: `dispatch.sh --dry-run` boot output contains the sentence; `dispatch.test.sh` asserts it for both modes. Falsified by: either boot lacking it.
* **AC-2** The boot header carries, verbatim: "Never create a repository, change repository settings or branch protection, add secrets, or run CI on any branch other than this task's own; a needed permission is a `Q:` line, not an attempt." Verified and falsified as AC-1.
* **AC-3** `watch.sh` reports `question` (not `gate-prepared`) when a validation gate is prepared while the entity's `pr:` field is empty, with a one-line reason. Verified by: a fixture state with a prepared validation gate and empty `pr:`. Falsified by: `gate-prepared` on that fixture.
* **AC-4** No new fixture copies an existing file; comment lines added stay under the repository's 3% baseline or each carries a fact the code cannot state.

## Non-goals

- No token-scope or GitHub-side enforcement (Kent's tokens, not this package).
- No change to the conn/gate-authority wording #445 landed.

## Route-back conditions

- Back to backlog if `dispatch.sh`'s boot text moves into a template file under another task; re-point AC-1/AC-2 at that file.

Profile recommendation: pilot.
