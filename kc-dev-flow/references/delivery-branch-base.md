# Delivery Branch Base

Load this when the selected stage's `delivery_artifact_review` trigger is true:
this work item is delivered through a reviewable delivery artifact — a pull
request, a merge request, or the equivalent on the repository's forge.

It decides one thing: what branch the work is based on. That decision is made
before any delivery ceremony runs, and no delivery provider owns it. This
reference therefore loads even when a provider mod owns the ceremony itself, and
it stays forge-neutral: the rule is target-branch mechanics, which behave the
same for a GitHub pull request and a GitLab merge request.

## PR-review evidence index

At this boundary, a delivery route may write one optional
`kc-dev-flow-pr-review-handoff/v1` index **outside the checkout and delivery PR
content** for a later `kc-pr-review` invocation. It is review context, not a
delivery record or authority. Bind the exact work-item reference, selected
profile, base SHA, candidate SHA, PR repository/number/head SHA, accepted
outcome and acceptance criteria, falsifiers, evidence references, changed-file
list, scope exclusions, and residuals. The candidate SHA and PR head SHA must
be identical.

Use the installed `kc-dev-flow/scripts/pr-review-handoff.py create` helper with
one repeated option per list item; write its `--output` to an operator-owned
mode-0600 path outside the checkout. Never put credentials, browser data,
cookies, raw tool logs, agent prompts, posting/merge instructions, or authority
claims in the index. The helper has no network, GitHub, execution, workflow
state, Ready, merge, or posting operation.

Pass the resulting path to `kc-pr-review` only after the PR exists. A reviewer
must validate it against a fresh repository, PR number, expected PR base SHA,
head SHA, and candidate SHA through the same helper before treating it as
context. A missing, malformed, base-mismatched, or otherwise identity-drifted
index is not evidence and cannot alter the review event,
confirmation, posting, merge, Ready, or workflow state.

## Prefer a stacked base

Choose the base before creating the branch, not after the work is done.

Through the repository's declared delivery provider, list the open delivery
artifacts and identify any that share this item's lineage: an open artifact whose
source branch carries work this candidate builds on, depends on, or would
otherwise re-deliver.

- When such an artifact exists, branch from the topmost open layer's source
  branch and target that same branch. A sibling branch is a valid target, not an
  error. Each layer then carries only its own diff and can be reviewed and merged
  on its own.
- Target the trunk only when the candidate is independent of every open artifact
  by the evidence you actually checked — no shared file, no reliance on unmerged
  behavior. Record that reason with the delivery evidence.
- Do not wait for a parent artifact to merge before starting dependent work, and
  do not copy a parent's commits into a trunk-targeted artifact to avoid
  stacking. Both produce a review diff that misstates the change.
- When a lower layer merges, the layer above needs its target moved to what is
  now below it, and its candidate revision re-recorded. Some forges retarget
  automatically. Verify what yours did; do not assume either way.
- A layer whose predecessors have all merged is complete. Do not move its target
  back onto a merged branch to tidy a stack record; a forge may reject that
  target outright.

## When the repository cannot stack

A repository may declare that every delivery artifact targets the trunk —
required linear history, a release train, a forge or review policy that cannot
handle a moving target branch. That is a legitimate local policy. Record it once
in the repository's delivery binding rather than re-deciding per work item, and
base on the trunk.

Do not treat "stacking would be inconvenient here" as that policy. The cost this
rule avoids is a review diff that contains someone else's unmerged work.

## Check the ceremony accepts a sibling base

A delivery provider that resolves its base as "the configured trunk" will
undo a stacked branch: it rebases onto the trunk and opens an artifact whose diff
carries the parent's work. Before relying on a stacked base, confirm the
repository's delivery ceremony accepts a sibling branch as the target. If it does
not, that is a provider defect to fix or a declared trunk-only policy to record —
not a reason to silently deliver a misstated diff.
