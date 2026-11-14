---
id:
title: A first reading of whether an agent given the method does better than one given the task in plain words, on one ideation case, in a place with no copy of the package
status: backlog
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree:
pr:
---

Two readings of one cell on the operator's laptop (archived task behaviour-baseline-first-cell) could not include a no-method arm: an installed copy of the package was one skill call away, and all three control runs loaded it. The question the Captain asks first, 「該怎麼知道用我的工作方法，確實比沒用較好？」 (outcome 零 of the reform's approved outcomes, as recorded in `.context/dev2-reform/結果定義.md`), is still unanswered by any run.

## Scope

- Source: the Captain 「同意第二段範圍的三項：程式送上私有遠端且原始紀錄留筆電、主機上做第一次對照、清洗途徑並行。」 (chat with the reform session, Paseo 26215d96, 2026-11-14; relayed, not a ruling here). Admission is recorded by FO under the Captain's standing grant to the second dev2 FO (chat, 2026-11-14) and the reform session's scope 2, items 1 and 2 (message fa01bfc1).
- Ranking, as the scope states it: the number is the goal. Carrying the code to the private remote exists only to make the number possible.
- Outcome 1 (prerequisite): the private working repository's remote main carries the cell definition, grader, fixtures, table code and both earlier readings' committed reading documents and result tables, and no raw run transcript or stored agent output from the laptop runs; the tree and history to be pushed scan at zero for all five identifier classes and for token-shaped strings; the clean host's clone is fast-forwarded to it.
- Outcome 2: one table from a clean host that has no copy of the package: three runs per arm, arm N (an agent given the task itself in plain words, with no package, no rebuilt dispatch and no workflow text) against arm M (the stage dispatch rebuilt by the package's replay builder at the candidate ref), same case as the closed cell unless the design states before any run why another inventory row is better, same model and effort in both arms, and a reading committed before any launch.
- The design must settle, in the committed reading: how the grader scores "identified that the criterion cannot be proven and said so" from two differently shaped outputs without scoring format as behaviour, with falsifier fixtures for both shapes; the exact prompt arm N is given, which must not leak the answer and must not be weaker than what a real person would type; what counts as contamination on that host when the case's own task edits the package's files; the three readings (method better, no difference, cannot discriminate) and the 3-against-3 patterns that give each, with silence in arm N as an outcome decided in advance; the limits.
- Where things live: the deliverable is in the private working repository and is named here only as that, pinned by commit SHA. The clean host is named here only as "the clean host". Raw runs stay where they were made or on the laptop; nothing from a run, a case or a private adopter is written to this state branch or pushed anywhere public.
- Profile: pilot. A measurement with a small amount of glue; no production data, credential in CI, migration or unattended operation.
Non-goals: building an isolation environment or a launcher (the launch-and-kill layer stays parked on its branch); more cells; a CI workflow; tuning after the first launch; any claim of release evidence.
Budget: 2 cycles per stage
Stop condition: 8 launches in total (3 + 3 + 2 spares for invalid runs); environment work on the clean host exceeding about one hour of worker time (stop and report to the reform session; the fallback of carrying a finished dispatch file is then FO's to choose); a non-zero scan before the push; a suspected key; if no arm fails, that is the result.

## Acceptance criteria

**AC-1**: The private working repository's remote main holds the code and the committed reading documents and tables, and no raw run output; the pushed tree and history scan at zero in all five identifier classes and for token-shaped strings.
Verified by: the scan's command, exit code and counts by class over exactly the pushed range, re-run by the validator on a fresh clone of the remote; a listing that shows no stored run folder. Limit: the identifier list is only as complete as its owner keeps it.

**AC-2**: The reading is committed before the first launch and holds the grading rule for both output shapes with falsifier fixtures, arm N's exact prompt, the contamination rule, the decision patterns and the limits.
Verified by: commit order and times against each run's start, and the falsifier fixtures' grades, re-run by the validator.

**AC-3**: One table with three valid runs per arm from the clean host, within 8 launches, with minutes, launches and usage, and the verdict by the committed patterns.
Verified by: the validator regenerates the table from the stored runs and compares it; the launch count is read from the stored records. Limit: one case, three trials per arm.

**AC-4**: An independent worker agrees with each run's grade under the committed reading, or names the runs it does not.
Verified by: the validator's per-run reading of what each run left.

**AC-5**: Nothing from a run, a case or a private adopter is on this state branch or in any public repository.
Verified by: a scan of this task's folder for run and case markers, hit counts only.

## FO alignment

Alignment: not needed before ideation: the outcome, the ranking, the cap and the design questions are stated in the scope the reform session gave under the Captain's grant; the design returns at the ideation gate and goes to the reform session for confirmation first.
Surfaces: none
Visible change: none
Release review: not needed: a measurement with no release on a journey map.
