# 0034. An acceptance task closes like a dev2-poc task, with the walk record in its task folder and a local-merge sentinel

Date: 2026-10-23

## Status

Accepted

## Context

A release walk's output is its own evidence, not a change to the product or the package. `workflow.md` Delivery authority treats a local finalize as an exception ("Do not invoke local fallback ... unless the specific action is authorized"). Spacedock's `mods/pr-merge.md` treats `pr:` values `pr-merge:` and `local-merge:` as merged and `merge guard --help` says the sentinel is retained through archive as delivery proof. The dev2-poc task `roborev-threshold-catches-pr-findings-poc` closed that way on a `merge: pr` task (state commits 4326d8fb and b5462eeb). `learn` SKILL.md says a `local-merge:SHA` does not satisfy its original-GitHub-PR route, so such a task is outside the learning loop.

## Decision

**Words:** 「好」 — Captain, 2026-10-23, chat, answering 「D1 改成「像 POC 一樣本機結案，地圖要改才開地圖 PR」，可以嗎？」 which he raised by asking 「可以，但退一步想，這是最好的嗎？」 about the first recommendation.

**Options considered:**
- An acceptance task closes like a dev2-poc task: the record stays in `<task folder>/walk/` on the state branch, no pull request is opened, and the validation gate question states that approving closes the task with `pr: local-merge:<sha>` and `merge guard --verdict passed`; a map edit the walk proposes goes in its own journey pull request (chosen)
- A docs-only pull request carrying the record (recommended by FO; not chosen, the Captain chose the local finalize)
- The record in the code worktree and a normal feature pull request (not chosen: nothing in the product changes)

**Recommended:** the second option, a docs-only record pull request; the Captain chose the first.

`<sha>` is the validated `Candidate:` state commit, or the observer report's commit where `learn` is listed. A plain approval authorizes that exact action because the gate question states it, the pattern ADR 0023 uses for the merge of a validated head. The exception Delivery authority names is met by that statement and `workflow.md` is not edited.

## Consequences

Acceptance tasks produce no learning evaluation. Screenshots in the state branch grow it; the size was not measured. The code worktree stays unchanged and no pull request exists to carry review rounds, so independent checking rests on the validation worker re-running `release_acceptance.py check --tier final` and `render --check` and re-performing the non-`works` stories. A `local-merge:` close of a `merge: pr` pilot task has precedent only on a proof-of-concept task, and is exercised by the scratch merge guard run in this change's stage report. Reopen if a walk record is lost with its state branch, or if a record needs a reviewer outside the Captain.
