---
title: A repair's validation recheck waits for the repair, and a failed push does not freeze a migration
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Two wording defects in kc-dev-flow-2 0.10.0 `references/sd/workflow.md`, found by an external review of an adopter's workflow sync (qnow PR #1248, 2026-09-30).

## Scope

Captain 2026-09-30: 「同意」 to the FO's proposal: fix both in the package, release 0.10.1, then re-sync the two adopter workflow READMEs (kc-claude-plugins #542, qnow #1248, both held).
Evidence (origin/main c3b3d5ad, `references/sd/workflow.md`):
- P1, `## Stages` lane paragraph: "A feedback-reflow repair, the validation recheck of that repair, and an FO fix authorized under Review-finding disposition step 3 are dispatched at once in the entity's own worktree". Read as "concurrently", a validator can inspect a pre-repair or partly written checkout and pass bytes the repair then changes. Intended meaning (review-cadence design): none of them waits for another entity's worker; the recheck is dispatched after the repair has completed and committed its candidate.
- P2, `## Number guards` Applied bullet: "Before any push of a candidate to a persistent shared environment ... FO records `Applied at:`". If the push is rejected or the deploy never runs, nothing was applied but the migration is frozen, and a renumber then needs a Captain-authorized branch reset. Direction: keep recording before the push (a record forgotten after a successful push is the undetected case), and let FO remove that one `Applied at:` line when the push or deploy is confirmed not to have run, stating the evidence.
Non-goals: any Spacedock change; any change to `number_guards.py` beyond what the wording requires; other sections.

## Acceptance criteria

To be written at ideation.

## FO alignment

Needed at ideation: exact replacement wording for both passages; whether `test_sd_dispatch.py`'s asserted lane phrase changes with it; what evidence a confirmed failed push must carry before the `Applied at:` line is removed, and whether `number_guards.py` needs any change.
Result: the FO delegates these questions to ideation, which decides each with its source and returns any ruling that needs the Captain.
Surfaces: none
Visible change: none
