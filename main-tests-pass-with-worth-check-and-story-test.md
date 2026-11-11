---
title: main's kc-dev-flow-2 tests pass again with the Worth questions check and the Story record test both merged
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:main-tests-pass-with-worth-check-and-story-test:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:main-tests-pass-with-worth-check-and-story-test-backlog-1
              briefing:
                id: briefing:main-tests-pass-with-worth-check-and-story-test:backlog:attempt-1:revision-1
                digest: sha256:f5f45e2c049769237934fa09f12e14bce71a10d6bcbc1f6e87cd3ff31a94024b
                room-ref: ./main-tests-pass-with-worth-check-and-story-test/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:main-tests-pass-with-worth-check-and-story-test:backlog:1
                briefing: briefing:main-tests-pass-with-worth-check-and-story-test:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-11T09:01:51.264926Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-11), answering 「決定：要不要讓「修好 main 上壞掉的那一項測試」這張任務插隊進入設計階段。我建議核准。核准代表接受任務檔寫的範圍（只修造成這次失敗的地方，不動你在 #841 已接受不修的那四件事）、預算（設計、實作、驗證各一輪，一個 PR）與停止條件（PR 的測試全過，而且我在請你合併前，先在「合併進 main 之後的結果」上重跑同一組測試），並派一個設計工人查清楚錯在測試還是錯在檢查本身。不代表接受任何修法。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: the Captain chose 「開優先修正任務（建議）」 (host question dialog, 2026-11-11), answering 「main 上壞掉的那一項測試要怎麼修？我建議：開一張優先修正任務插進這批，派工人查清楚「找不到 spacedock 程式時檢查該怎麼反應」，只修造成這次失敗的地方，走完整的驗證再請你合併；發版等它。另一個做法是先把 #841 退回（revert）讓 main 變綠、優先修正先發版給 qnow，預算任務修好後再送一次。」
- Bite (FO read 2026-11-11, `gh run view 42991036147 --repo iamcxa/kc-claude-plugins --log-failed`): on main 571a7bd8a, the squash of PR #841, the `kc-dev-flow-2 tests` workflow fails one of 226 tests in `kc-dev-flow-2/scripts/test_design_surfaces.py`: `JourneyStoryTests.test_design_compares_story_record_to_counted_field_only_in_map_workflows` expects no refusal and gets `task.md: cannot read stage for Worth questions: [Errno 2] No such file or directory: 'spacedock'`. The run on eeee00230, the commit before, passed. The test came with PR #843 and the Worth questions check with PR #841; each PR's own checks passed, and FO did not rerun acceptance on the merged result before the #841 merge ask (stated in that ask).
- Effect: main is red, so Release PR #840 cannot pass its required check, and the fix in PR #844 that an adopter waits for cannot ship.
- Outcome: the `kc-dev-flow-2 tests` workflow passes on main with both changes in place, and what PR #841's accepted criteria say about a stage that cannot be read (the check refuses) still holds.
- Open for the design: whether the defect is the test's setup (it runs the design check where no `spacedock` program exists) or the check's behaviour when the program is absent in real use; the design shows which by running both, and names every other test or caller that reaches the Worth questions check without the program.
- Non-goals: the two Codex findings and the Deferred risk the Captain accepted as not repaired at the #841 merge ask; the fifteen sibling findings; cumulative agent minutes; any change to what the Story record rule or the Budget rule decides.

## Budget
- One ideation, one implementation and one validation cycle, in one package PR to the file or files the design names under `kc-dev-flow-2/scripts/`.

## Stop condition
- The `kc-dev-flow-2 tests` workflow is green on the PR head and FO has run the same test command on the result of merging the head with main at the time of the merge ask. Return to the Captain if the fix needs a change to what the Worth questions check refuses, or to a file outside `kc-dev-flow-2/scripts/`.

## FO alignment

Alignment: not needed: the Captain chose the forward fix and its bound in the question quoted under Scope; no direction is open that he has not ruled.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
