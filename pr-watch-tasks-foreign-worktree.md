---
title: pr_watch.py tasks prints record-PR next lines for tasks whose worktree is not on this machine
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Filed on the Captain's 「開」 (chat, 2026-10-16), after FO's first run of the v0.23.0 lifecycle mod's idle step on this workflow.

## Scope

- Observed 2026-10-16, kc-dev-flow-2 0.23.0, `python3 <package>/scripts/pr_watch.py tasks <workflow dir>` on this workflow printed two `next:` lines: "record journey-server-host-pilot's PR with status --set journey-server-host-pilot pr=<owner/repo>#<N>; its worktree is not on this machine." and the same for pr-review-lite-value-pilot. Neither task is driven by the session that ran the mod (one is held at validation by another session, the other unchanged since 2026-09-22), and neither has a PR yet.
- The mod tells FO to do each `next:` line in order, so an FO that follows it may record a wrong PR on another session's task. Several FO sessions drive one workflow in adopters such as subspace-relay.
- Candidate fix: a task whose worktree is not on this machine is listed as a fact line, not a `next:` action; a test with such a task.
- Should land before subspace-relay syncs to the mod.
- Also seen 2026-10-16 on the same run: `next: run spacedock state commit amendment-form-check` while that task's implementation worker was still writing its report (the worker owns that commit), and `next: mark #649 ready if Delivery authority allows` before its validation had run. Both are `next:` lines an FO must not follow at that moment; whether they become facts too is for ideation.
