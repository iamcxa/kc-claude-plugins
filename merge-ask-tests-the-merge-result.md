---
title: A merge ask for a PR whose base moved since validation carries a test run on the merge result
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:merge-ask-tests-the-merge-result:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:merge-ask-tests-the-merge-result-backlog-1
              briefing:
                id: briefing:merge-ask-tests-the-merge-result:backlog:attempt-1:revision-1
                digest: sha256:49ebaa98701d209a51e97e09e90aa390888350e8d02aef377224de98ebe6270a
                room-ref: ./merge-ask-tests-the-merge-result/review/backlog/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-11-12T05:11:28.449691Z"
                reason: The Captain answered the joint question with a change to the experiment instead of a decision (host question dialog, 2026-11-12); FO asks again with the experiment written into the question.
            - id: gate-attempt:merge-ask-tests-the-merge-result-backlog-2
              briefing:
                id: briefing:merge-ask-tests-the-merge-result:backlog:attempt-2:revision-1
                digest: sha256:09fe9a54d587cdd31282078fed3541c7e4e93362d7126e11df246e7af3164c35
                room-ref: ./merge-ask-tests-the-merge-result/review/backlog/briefing-2
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
