---
title: A merge ask for a PR whose base moved since validation carries a test run on the merge result
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: FO's own miss, filed by FO with no Captain ruling yet; the backlog gate confirms it.
- Bite (FO read 2026-11-11, `gh run view 42991036147 --repo iamcxa/kc-claude-plugins --log-failed`): PRs #843 and #841 each passed their own checks and validation; after both merged, main failed one of 226 tests in `kc-dev-flow-2/scripts/test_design_surfaces.py`, Release PR #840 could not pass, and a fix task ran 80 minutes from filing to archive. The #841 merge ask said the acceptance was not rerun on the merged result; nothing held the ask.
- Outcome: when main has moved since the validated head was dispatched, FO's merge ask is held until a test run on the result of merging that head with current main is recorded, or the Captain is told in the question that none was run.
- Open for the design: which commands count as the run and who runs them; whether the existing delivery check can carry it or GitHub's own merge queue or required up-to-date branch setting already does; what it costs per PR in minutes.
- Non-goals: changing CI definitions; rerunning validation; any rule for PRs whose base did not move.

## Budget
1 cycle per stage, in one package PR.

## Stop condition
- A replay of PR #841's merge ask at its recorded state is held by the candidate and the same ask with a recorded merge-result run passes. Return to the Captain if the design needs a CI or repository-setting change.

## FO alignment

Alignment: not needed: one observed defect with one outcome; how it is checked is compared in the design and ruled at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
