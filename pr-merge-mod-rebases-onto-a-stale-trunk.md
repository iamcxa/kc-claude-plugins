---
title: "The pr-merge mod's delivery step syncs the wrong branch and rebases onto a stale local trunk"
status: backlog
source: Captain ruling 2026-09-14 in FO session, after the defect bit during PR #444 delivery
product: repo-platform
planning-window:
planning-outcome:
sprint:
sprint-readiness: defer
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: ab8tk40pm0t0wv2jpt7551d6
---

## The problem

`docs/dev/_mods/pr-merge.md` line 73 opens the on-approval delivery sequence with `git push origin
"$BASE"`, justified as pushing "the trunk to ensure the remote is up to date with local state
commits". That reason only holds for an inline workflow, where entity state lives on the trunk. This
workflow is split-root: its README declares `state: .spacedock-state`, and `spacedock state commit`
publishes to `spacedock-state/dev`. No state commit ever reaches `main`, so the step syncs nothing
the workflow owns while pushing whatever the local trunk happens to hold to a shared branch.

The same line then rebases with `git rebase "$BASE"`. `$BASE` comes from `spacedock dispatch trunk`,
which emits a bare branch name, so this rebases onto the **local** trunk ref rather than the fetched
remote one. Both defects were observed during the `retire-the-provider-backed-planning-path`
delivery on 2026-09-14: the trunk push was refused non-fast-forward because the local trunk was
stale, which is exactly the state in which the following line would have rebased the candidate onto
an old base and opened a pull request already behind the trunk. The First Officer deviated and
rebased onto `origin/main`, which is what surfaced three real conflicts; the literal sequence would
have deferred them to the merge on GitHub.

Line 73 sits before the `<!-- kc-dev-flow runtime extension:start -->` marker at line 119, so this
is the repository's own policy half of the mod, not the package-owned extension.

## Accepted outcome

The delivery sequence fetches the remote trunk and rebases the candidate onto it, and no longer
pushes the trunk. A reader of the mod cannot come away believing this workflow's state lives on the
trunk.

## Non-goals

- Editing anything between the `kc-dev-flow runtime extension` start and end markers.
- Weakening or moving the captain-approval guardrail that precedes the push.
- Changing the fall-back-to-local-merge clause.
- Changing any other repository's mod.

## Acceptance criteria

- **AC-1** The local half of `docs/dev/_mods/pr-merge.md` contains no `git push origin "$BASE"`, and
  no remaining sentence claims the trunk carries this workflow's state commits.
- **AC-2** The delivery sequence fetches before it rebases, and the rebase names the remote-tracking
  ref rather than the bare branch name.
- **AC-3** `python3 scripts/kc-dev-flow-contract-test.py` exits 0, proving the package-owned
  extension block is byte-identical after the edit.
- **AC-4** Replaying the corrected sequence by hand against a deliberately stale local trunk rebases
  the candidate onto the remote tip, shown by the resulting merge-base equalling `origin/main`.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names
the changed premise, affected acceptance evidence, and recommended change or stop.
