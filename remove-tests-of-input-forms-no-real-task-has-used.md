---
title: Tests of input forms no real task has used are removed, and a test is written when a real failure asks for it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「我想要直接刪掉完全沒用的那類，真的遇到問題再寫。」 (chat, 2026-11-13), after his 「還有一個問題，目前的測試真的都是必要的嗎？有沒有已經寫的測試，是用測試來測其實不需要寫測試的內容？」 (chat, 2026-11-13). FO reads "that class" as the audit's class B below and confirms it with him in the admission question.
- Evidence (independent read-only audit, Codex Astra, 2026-11-13, pinned to origin/main; its report and per-test table are in this task's folder under `audit/`): 1,455 test functions in 29 files, 24,684 lines, against 10,731 product lines. Classes: A recorded real-failure regression 64; B constructed input edge with no recorded real occurrence 432; C wording or count pin 40; D mutation, harness or overlap 107; E ordinary unit coverage 812. Across 25 retained failed CI runs, failures after a test's introduction: A 0, B 0, C 2, D 1, E 5 (lower bounds). The CI job took 426 seconds; three test files took 51 percent of it. The auditor's cold reread disagreed with itself on 3 of 30 tests, and it states that no deletion is established as safe.
- Outcome: the class B tests are removed from the package's test files; product code is unchanged; the PR lists what was removed and what input forms are no longer exercised, so a later real failure can restore the right test from history.
- Open for the design: re-reading each class B test before removal, since one in ten may be misclassified; what to do with a class B test that is the only assertion of a behaviour real tasks use (keep it and say why); whether product branches reachable only from removed tests are listed as removal candidates for a later ruling; the CI time before and after.
- Non-goals: classes A, C, D and E; any product code change; changing what the checkers accept; a new rule about when tests are written (the Captain's sentence above is the rule and goes where the design says it must load).

## Budget
1 implementation and 2 validation cycles, in one package PR.

## Stop condition
- The remaining suite passes in CI, the PR states the count removed per file against the audit's table and every class B test kept with its reason, and CI's test job time is reported before and after. Return to the Captain if more than one in five class B tests turns out, on re-reading, to guard behaviour a real task used.

## FO alignment

Alignment: needed at ideation; which class "completely useless" names is confirmed with the Captain at admission.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
