---
title: codex_review.py reads a comment-triggered run and reports a missing gh as a configuration error
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined under the round-3 rule from the third external review round (Codex) of iamcxa/kc-claude-plugins PR #593, head 602013460, 2026-10-11. Neither finding is P1 or Material, so neither started a repair cycle there; each is filed here with its decline reason, per `## FO steps: review findings` step 5.

## Scope

- Finding 1 (P2, `codex_review.py` reactions read): a review started by an `@codex review` comment puts Codex's eyes reaction on that comment, not on the PR, so a running comment-triggered review reads as the previous result or as not reviewed instead of exit 3. Decline reason: it matters only when the same head is reviewed again, which FO starts itself, and FO already counts one round per evidence id, so no round is double-counted.
- Finding 2 (P2, `gh` call): with `gh` missing from PATH, `subprocess.run` raises FileNotFoundError and the script exits 1, the findings code, instead of 2. Decline reason: the error fails closed (a round reads as blocked, never as clean), and every adopter that uses the script already has `gh` for PR delivery.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Needed at ideation: whether both land as one patch, once the Captain schedules this task.
Surfaces: none
Visible change: none
