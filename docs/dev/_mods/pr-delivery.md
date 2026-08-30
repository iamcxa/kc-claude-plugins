# PR Delivery

Load this only when the selected stage's `pr_delivery_selected` trigger is true:
the repository's declared delivery authority routes this work item through a
forge pull request. It adds no authority. The Captain still owns merge
authorization, and the repository's declared delivery provider still owns any
ceremony it already implements.

## Precedence

An adopter-owned provider mod, such as Spacedock `pr-merge`, keeps the delivery
ceremony it owns. This reference governs a work item only where no provider owns
that ceremony. The shared core keeps one delivery authority, so do not run both
against the same item.

## Base

`delivery-branch-base.md` owns which branch this PR targets, under its own
trigger. It loads independently of this reference, because base choice is decided
before any ceremony runs and survives a provider owning the ceremony. Take the
base from there; this reference only carries it out.

## Provider planning linkage

For provider-backed work, carry the adapter's ephemeral `delivery.branch` and
`delivery.close_line` from the same exact reconciled `source`. A non-empty
branch replaces the ordinary delivery branch byte-for-byte as the forge head;
null keeps that ordinary branch. Append the close line exactly once to the
reviewed PR body. Stop before push or PR creation when either value is missing,
malformed, or does not bind the reconciled source.

Do not infer either value from prose or maintain another planning field. Linear
supplies its exact issue branch plus `Fixes TEAM-N`; a GitHub Issue supplies a
null branch plus `Closes owner/repo#N`. Use the legacy `issue` field only for a
standalone item with no Planning Receipt.

## Approval and candidate identity

The kernel already places merge authorization with the Captain. Two delivery
specifics are not implied by it:

- Approval is explicit. Silence, acknowledgment of a summary, and the stage gate
  that preceded delivery are not approval. Wait for an explicit instruction to
  push.
- The approved thing is a revision, not a branch. Record `CANDIDATE_SHA` from
  the work tree before presenting the draft, and use that recorded value for
  every later candidate identity. Do not read ambient `HEAD` after approval.
  Re-record it after any restack, because a lower layer merging replaces every
  candidate above it.

Present the draft with title, `branch -> base`, the candidate revision, the
changed-file count and list computed against that base, and the exact body bytes
that will be submitted.

## Deliver the approved revision

1. Update the base on the remote first. If that fails — no remote, auth error —
   report it and stop; do not repair it with a force operation.
2. Test the approved commit against the current base tip without touching the
   candidate ref, index, or work tree. In git that is
   `git -C {worktree} merge-tree --write-tree "$BASE_SHA" "$CANDIDATE_SHA"`.
   Read its stdout, stderr, and exit status together; the exit status alone is a
   signal, not the verdict.
   - Clean merge: continue without rebasing.
   - Real content conflict: stop delivery, surface the conflict evidence, and
     keep the pending delivery authority. Do not rebase, auto-resolve, or force.
     Reconciliation ownership is the Captain's call.
   - Failed, incomplete, or ambiguous evidence: mergeability is unknown. Report
     it and stop. An unknown result is not a pass, and local merge is not a
     fallback for it.
3. Push the exact approved revision by SHA refspec —
   `git -C {worktree} push origin "${CANDIDATE_SHA}:refs/heads/${BRANCH}"` — so
   later local commits cannot ride along on an approval they never had.
4. Write the reviewed body to a mode-0600 temporary file and submit it with
   `--body-file`. Pass repository, branch, base, and title as separate argument
   values. Do not interpolate work-item text into shell syntax, do not use a
   shell-expanded heredoc, and do not rebuild the body after approval. Remove
   the temporary file on success or failure.

For a stacked candidate, create each layer with the same create call and its own
reviewed body, giving each the layer below as its base. The base chain alone
satisfies this contract.

GitHub additionally offers a `gh stack` CLI extension that groups the layers into
one stack object. It is optional. When it is present, join the layers bottom to
top with `gh stack link` after creating them, and read `gh stack view --json`
back to count the branches: `gh stack link` has been observed printing a forge
rejection as a warning and then reporting success anyway, so its exit status does
not prove membership. Do not create layers with `gh stack submit`: on gh 2.92.0
it exposes no title or body flag, and a non-interactive run uses auto-generated
titles and opens drafts, so the reviewed bytes never reach the forge. Grouping is
presentation; a correctly based top layer is a healthy end-state even when it is
not in a stack object.

## PR body

Lead with motivation and end-user value; audit metadata goes last, so a reviewer
sees the "why" first.

| Section | Required | Content |
|---|---|---|
| Motivation lead | yes | 1 sentence, 25 words or fewer, blending motivation and end-user value. No parentheticals. |
| `## What changed` | yes | 3-5 action-verb bullets, each 15 words or fewer. One change per bullet. Rationale belongs in the work item, not here. |
| `## Evidence` | yes when verification ran | 1-2 bullets, `N/N passed` per suite. No per-test breakdowns or enumerated suite lists. |
| `## Review guidance` | optional | 1 line naming the risky file or change, only when a stage report flagged it. |
| `---` separator + work-item link | yes | Link the exact committed work item at its exact revision. |
| Provider close line | yes for provider-backed work | Append `delivery.close_line` exactly once. |
| `Closes {issue}` | yes only for a standalone item recording an issue | Use the legacy value exactly as written. |
| `Related: {siblings}` | optional | Only when a stage report flagged follow-ups. |

Extract deterministically from the work item and its stage reports:

| Section | Source | Transformation |
|---|---|---|
| Motivation lead | The work item's own problem statement | Condense to 1-2 sentences. Lead with impact or an action verb, not "This PR". |
| What changed | The latest stage report whose declared outputs describe completed deliverable work | One action-verb bullet per meaningful unit; collapse siblings. Omit "what we did not change" bullets unless a verification report flagged them as risk. |
| Evidence | The latest stage report whose declared outputs independently verify the candidate against acceptance criteria | One bullet per suite, plus any quantitative result the report called out. Fall back to self-test evidence when the selected route declares no independent verification stage. |

Select each source report by its declared stage outputs and content, never by
requiring a stage name — the three profile routes name their stages differently.
Target total length: 60-120 words. Paraphrase; do not paste stage reports.

## After the PR exists

Delivery is not done at creation. On the next resume, recheck the PR state:

- `MERGED` — for a trunk-based PR, terminalize through the existing state owner
  and clean up the branch and work tree. Do not create a second delivery record.
  For a stacked layer, `MERGED` means it reached its parent branch, not the
  trunk: check that every predecessor in its base chain has also merged into the
  delivery target before terminalizing. An unmerged predecessor leaves this layer
  delivered but not landed, so keep it open and report the blocking layer.
- `CLOSED` without merge — report it and ask the Captain how to proceed:
  reopen, open a new PR from the same branch, fall back to local merge, or send
  the item back for rework. Do not choose for them.
- `OPEN` — no action; it is still in review.

When the forge CLI is unavailable, say so and skip the state check. An unchecked
PR is unknown, not merged.
