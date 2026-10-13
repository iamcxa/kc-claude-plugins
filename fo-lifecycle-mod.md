---
title: kc-dev-flow-2 ships a Spacedock mod that loads FO's merge, idle and startup steps at those moments
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Filed on the Captain's 「開」 (2026-10-14) after an observer read of the spacedock-dev/subspace-relay FO session that delivered PR #362 (task `owner-sees-all-feedback-room`, kc-dev-flow-2 0.22.0). The FO never ran `pr_watch.py` for the PR and ran `merge guard` with no observer step and no learn. Both rules were in the adopter README, but FO read it in `sed -n` ranges up to line 480; `## Delivery authority` starts at line 492 and `## Extensions` at 538. The Captain asked whether the README is too long and whether to split or index it; the direction he approved is a mod keyed to Spacedock's lifecycle points rather than a longer README or read-sized slices.

## Scope

- Spacedock 0.27 already provides the index: mods in `{workflow_dir}/_mods/` with `## Hook: startup`, `## Hook: idle` and `## Hook: merge`, opened only at that lifecycle point and run alphabetically by filename (first-officer shared core, "Mod Hook Convention"). Adopters carry Spacedock's own `_mods/pr-merge.md`, copied unchanged; its `startup`/`idle` hooks handle a MERGED PR (sentinel, then `merge guard`) and its `merge` hook handles the PR at terminal approval.
- Candidate contents of a kc-dev-flow-2 mod:
  - `merge` (approved, before the merge ask): mark ready, wait for the post-ready Codex run, check the head against the validated candidate, `delivery_gate.py`, `pr_watch.py add`, then the merge ask.
  - `idle`: every open task PR has a `pr_watch.py wait` running in the background, else start it; advance an open learning delivery.
  - `idle`/`startup` on a MERGED PR, before the sentinel: `observer_check.py`, dispatching and saving the observer when absent.
  - after the archive: learn, with its notice and the observer report presented together.
  - `startup`: unread learn notices and open learning deliveries.
- Ordering: the observer step must run before `pr-merge`'s sentinel, so the mod's filename must sort before `pr-merge.md`; learn runs after the archive (a later pass, or a second file that sorts after it).
- The README keeps the rules as the authority and points to the mod; the FO steps moved out are expected to lower `WORKFLOW_WORD_BUDGET` (`## Delivery authority` 546 words, `## Extensions` 222 at origin/main 656543f4). How much moves is ideation's count.
- Dispatch-time rules (scope-notes lines, extension worker instructions) have no hook point and stay with script checks: tasks `followup-dispatch-records-checked` and `extension-instruction-reaches-dispatch`.
- Spacedock is not changed (the Captain's ruling); `pr-merge.md` stays an unchanged copy.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation. The proof owed is a replay of the relay #362 situation showing FO starts `pr_watch` and runs the observer and learn at the right moments with the mod, and does not without it.

## FO alignment

Alignment: needed at ideation: the design changes what FO loads at three lifecycle points across every adopter.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
