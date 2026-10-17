## Delivery authority

The adopted `_mods/pr-merge.md` is the unmodified mod from the activated SD
package. Before delivery, confirm the file still matches the reviewed source
(or an explicitly approved project customization) and its merge hook is
registered. Missing/changed delivery configuration requires a hold: `merge: pr`
alone does not block SD's no-hook local-finalize route.

Project and Captain authority constrain hook instructions: present the exact candidate
and PR body before authorized push/create; create a Draft PR where required, and request
ready only after the required CI is green. Required CI is green only when its test jobs
have finished on the PR head. Where CI skips drafts, FO marks the PR ready under the
Captain's authority and waits for those jobs to finish before asking for merge. Approval
of a validation gate is not permission to push, create or merge a PR, except as follows.
FO's delivery gate question says that approval also covers later external-review rounds
on the same PR. Under that approval, a repair whose validation passes with no Material
or Needs decision finding is recorded by FO under that grant (`gate record --actor
agent:first-officer` with `--conn-quote` and `--conn-source` naming his approval) and
pushed to that PR's branch, after FO confirms the pushed commit is the candidate the
report names. A rejected repair, a Needs decision, a scope change and the merge still go
to him. Preserve manual merge authority. Do not invoke local fallback, push the trunk,
merge, or clean up an owned worktree unless the specific action is authorized. An
upstream hook's default fallback is not that grant. A failure holds delivery pending an
explicit choice.

Under the Captain's grant quoted in its dispatch, the implementation worker opens the task's
Draft PR before validation; that grant stands in for a presented body. Observe the actual
repository-qualified PR merge before recording its landed sentinel and running SD merge guard
to finalize/archive. Where `learn` is listed, the sentinel waits for a committed observer report.
CI green, PR creation, gate approval and a locally manufactured sentinel do not prove merge.
FO's startup and idle steps are in `_mods/kc-dev-flow-2.md`, copied from `<package>/references/sd/mods/`.

Before the merge ask, a head other than the latest
validation record's `Candidate:` is revalidated or its difference told to the Captain. Before the
`gate prepare` that asks for merge, FO runs `python3 <package>/scripts/delivery_gate.py check <task>
--pr <owner/repo>#<N> --text-file <question and summary>`; exit 1 or 2 holds the ask and FO shows the
Captain what it printed.

`merge guard --rework` supersedes the approval and routes the task back, but its
help names no commit or publish step, unlike the archive path. After it, FO runs
`spacedock state commit <slug> --workflow-dir <dir>`, publishes, and reads the task
back from the state remote before dispatching the repair; otherwise durable state
can still show the task awaiting merge.

