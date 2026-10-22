Observer report: merge-ask-holds-missing-clauses (window seed to the task's last commit before the merge sentinel, spacedock-state/dev2, 31 commits). Observer: kc-dev-flow-2:observer, sonnet, 2026-10-22.

violation | rule: "A Captain ruling is his reply to the question it settles, given after that question was put. FO never records as his ruling: … consent he gave earlier to a different question, or a choice he raised but did not make." (FO steps: review findings) | evidence: ideation attempt 3 "Approve the narrowed ideation design … (cycle 3: hold C only) to enter implementation?" is recorded `by: person:captain, approve` with a reason quoting the narrowing 「可以」 (attempt-2 revise reason) and D2 「按建議**不算**」, ending "This briefing binds those answers after the fact; approving enters implementation." Briefing 03:12:11 (c54ef149), approval 03:12:14 (aff48e4f); no reply to this briefing question is quoted.
ok | rule: "His plain approval accepts that recommendation only when the gate question says so" | evidence: backlog and validation questions say so; rulings quote 「繼續」 (9576225f) and 「合併」 (254a8cef); validation briefing 17:55:03 (a66d57c3) precedes the record 17:57:52.
ok | rule: Override line | evidence: "Override: recommended building A, B (option a) and C (design); Captain chose C only, on FO revised recommendation; area: merge-ask holds." (f76b638d)
ok | rule: design_surfaces.py check (backlog, ideation) | evidence: replays exit 0 at 32856ea7, 5b29f5b1, 13358772, c54ef149.
ok | rule: delivery_gate.py check before the merge ask | evidence: ask-1.json 09:54:48Z head 1e47b8c6108371ec379ad4fae18a80df2cdd0b81 (8cff2051) before the briefing (a66d57c3); ask-2 09:57:58Z after approval (77f067b6).
ok | rule: sufficiency and minimal necessity | evidence: both in ask-1.json (8cff2051).
ok | rule: delivery gate question clauses | evidence: later rounds, full head, worktree removal, `--match-head-commit 1e47b8c6…` (a66d57c3).
ok | rule: rounds counted; second reviewer; unread reviewer named | evidence: "External rounds: Codex 1 …"; "Second reviewer: copilot because the PR changes merge rules. copilot not run: …" (a66d57c3).
can't tell | rule: "A merge ask names each listed reviewer that was not read" (roborev listed) | evidence: the summary does not mention roborev; only a RoboRev review posted on the PR is a round.
can't tell | rule: "present the exact candidate and PR body before authorized push/create" | evidence: grant and quote recorded (e81c328d); whether head and body were shown is chat only.
can't tell | rule: "A follow-up message to a worker FO resumes is a dispatch too, with the same check and a checklist"; "do not edit the worker's report" | evidence: the implementation Stage Report was rewritten after 75da9cac (FAILED to DONE) in 21d34b92; dispatch/ holds no record for that follow-up.
can't tell | rule: "FO runs the stage's minimal acceptance script exactly as written in a fresh shell" | evidence: the validator ran it (b1742360); no record of FO's run.
ok | rule: dispatch records | evidence: "5 dispatch record(s) complete"; validation-1.md Candidate 1e47b8c6… (2e99486b).
ok | rule: state commits path-scoped | evidence: 31 commits touch only this task.
observed | rule: Reviewer line | evidence: "Reviewer: engineering-reviewer opus 2026-10-21 — do holds A, B and C …" (adee32da); role_triggers.py 0 events owed.
observed | evidence: ideation attempt 1 withdrawn by `agent:first-officer`: "engineering-reviewer-1 (reviews/) requires design changes before the ideation gate; a fold cycle follows" (db7374b8).

Coverage: README in full; task file at HEAD; seed, gate, dispatch, delivery and validation commit diffs; four ideation worker commits by stat; 5 dispatch records; 2 ask files; 4 briefings; engineering-reviewer-1.md; ledger, role_triggers, dispatch_records replays (0.28.0 scripts; README 0.27.0). Not evaluated: chat-only rules, design quality, worker reports, PR #703, the merge and sentinel.
