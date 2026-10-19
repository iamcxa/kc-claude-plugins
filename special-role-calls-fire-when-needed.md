---
title: A chief-engineer or engineering-reviewer call fires when the work needs one, not only when a cycle count or a Supersedes line says so
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain, 2026-10-20: 「在特定時候應該要徵招特殊角色來諮詢，目前似乎做的不是那麼得好？」. Evidence collected the same day by four read-only observers over the dev2 state of kc-claude-plugins, subspace-relay, subspace-web and qnow (reports in `fo-batch-sittings/dogfood/`).
- Bite, measured on those reports (window: gates from 2026-10-17):
  - engineering-reviewer: `role_triggers.py` owes it 4 times here, 8 in relay and 2 in web; 0 calls were made in those three repositories inside the window; the only two engineering-reviewer calls found are web's on 2026-10-15 and 10-16.
  - chief-engineer: owed by the script 3 times here (2 calls made but worded "third repair cycle", so the script does not count them; 1 filed under the wrong heading), 1 in relay (waived after the merge); qnow and web have none.
  - Script blind spots: qnow and web track cycles in `## Stage Report: ... (cycle N)` headings, not `- Cycle N` lines under `### Feedback Cycles`, so the script reads 0 events there; qnow has no `## Captain amendments` section in any window task; an amendment marked `Supersedes: none` that changes the merge rule (captain-question-load) fires nothing.
  - Owed by judgment, no call: two or more review rounds finding new gaps in one file or sentence (here: special-role-triggers, fo-write-checks, extension-instruction-reaches-dispatch, captain-question-load; qnow: production-operations with seven rounds on one scrubber, cash-at-pickup); a design or amendment reversing an earlier Captain ruling (here: merge-gatekeeper, delivery-gate-settles-skipped-checks, prod-security-review-gates; relay: account-publish-ceiling, spacedock-install-beta); merge, authority or hard-to-reverse rule changes (captain-question-load; qnow: production-go-live).
- Consumer: every FO on the dev2 route (this repository, relay, web, qnow) and the Captain, who otherwise asks FO 「找誰問？」.
- Upstream first: `role_triggers.py` and the README `Reviewer:` rule (0.25.0, special-role-triggers #664); the chief-engineer and engineering-reviewer agent descriptions, which already name drift and contested, high-risk or hard-to-reverse claims.
- Captain's design direction, 2026-10-20: 「設計時不應該過度依賴關鍵字，而是可能要依靠犯錯字數觸發，合理嗎？」 FO reads 犯錯字數 as a count of mistakes (findings, rejected validations, holds, overrides) and asked him to correct that reading if wrong. Triggers are to come from counts read from structured records (review comments and their paths, gate records, Feedback Cycle and stage-report headings), not from phrase matching; ideation measures each candidate count over the four repositories' records before choosing thresholds.
- Order: runs in parallel with delivery-gate-settles-skipped-checks; the release does not wait for it.
- Non-goals: to be set at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain raised the problem.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
