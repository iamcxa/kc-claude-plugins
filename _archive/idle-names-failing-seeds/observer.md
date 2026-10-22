Observer report: idle-names-failing-seeds (window 6d0a89bb to 1160a3b3 on spacedock-state/dev2). Observer: kc-dev-flow-2:observer, sonnet, 2026-10-22.

ok | rule: "A Captain ruling is his reply to the question it settles, given after that question was put." (FO steps: review findings) | evidence: backlog briefing 2026-10-21 07:26Z (f0eec4de); resolution 07:28:54Z "Captain 「繼續」 … answering FO's question 「這 5 張都批准進入設計嗎？」" (e40c3523). The briefing says "six batch-5 tasks", the reason five gates; a count difference.
ok | same rule | evidence: ideation briefing 2026-10-21 08:00Z (3f36d0de); resolution 17:16:35Z quotes D1 「可以」 and D2 「可以照建議」 (88657eed). can't tell whether his one 「可以」 for D1 answered both recommendations as put in chat.
ok | same rule | evidence: validation briefing 03:46:05Z (6a838ca2); resolution 03:52:44Z "Captain: 「合併 694」 … answering 「#694 要合併嗎？我建議合併。」", digest e505b28a matches (cf23b914).
ok | rule: "His plain approval accepts that recommendation only when the gate question says so" | evidence: each bound question says so (f0eec4de, 6a838ca2, 3f36d0de).
ok | rule: Override line | evidence: "override": null on all three gates; all three approvals match the recommendation.
ok | rule: design_surfaces.py check (backlog seed, ideation) | evidence: replays exit 0 (201ba563 --seed; 14886ca2).
ok | rule: delivery_gate.py check before the merge ask | evidence: ask-1.json 2026-10-22T03:45:59Z head 1c57c156d034fcd1a7a73efb9a70370a57c1f97f before the briefing commit; ask-2.json 03:52:50Z after approval, same head (6a838ca2, 1160a3b3).
ok | rule: sufficiency and minimal necessity | evidence: both in ask-1.json (6a838ca2).
observed | rule: "FO's delivery gate question says approval also covers later external-review rounds on the same PR, merging the full head … unless he says he merges or holds, and removing its clean, pushed worktree" (Delivery authority) | evidence: the question has the merge and worktree clauses and "FO merges this one PR only"; no external-review-rounds clause and no "unless he says he merges or holds" clause; narrower, not wider (6a838ca2).
ok | rule: FO declines evidenced Deferred risk or Polish in the committed gate summary | evidence: "FO declines: Deferred risk, Codex P2 comment:4343627800 …; Polish F1 …; Deferred risk F2 … F3 …" (6a838ca2).
violation | rule: "FO records `second reviewer: <name> because <trigger>` or `second reviewer: not triggered` in the gate summary" (Extensions) | evidence: "Second reviewer: none, the PR changes no merge, review or approval rule." The literal form is not used (6a838ca2).
violation | rule: "FO resolves `<package>` … from the `Package root:` line of `kc-dev-flow-2:dev`" (Stages) | evidence: dispatch/validation-1.md "kc-dev-flow-2 0.26.0 README" and "Package root: …/0.26.0" while the README is 0.27.0 and this task's ideation and implementation dispatches carry 0.27.0 (6618dc28, 78781070).
ok | rule: dispatch_records.py, `Candidate:` and send-to-`main` lines | evidence: "3 dispatch record(s) complete"; validation-1.md Candidate equals the ask head.
ok | rule: FO alignment Surfaces / Visible change lines (backlog) | evidence: "Surfaces: none / Visible change: none / Release review: not needed …" (6d0a89bb).
ok | rule: "FO commits task state only through SD commands" | evidence: all 17 commits are SD subjects touching only this task.
ok | rule: peers | evidence: no ruling quotes a peer.
observed | rule: `Reviewer:` line | evidence: absent; no trigger holds; role_triggers.py "0 event(s) … each with a call or a waiver" (1160a3b3).
can't tell | rule: ADR landing for rulings later work must respect | evidence: D1 and D2 rulings sit in the task; no ADR added (78781070).
can't tell | rule: observe the merge before the landed sentinel; worktree removal | evidence: after the window.
can't tell | rule: Schema `id` | evidence: no `id:`; `id-style: slug`, 36 of 38 task files lack it too (6d0a89bb).

Coverage: full task file at 1160a3b3, three dispatch files, both ask files, three briefings, ledger rows, 17 commit stats, README sections Schema, Stages, backlog, ideation, validation, Review-finding disposition, FO steps, Captain amendments, Delivery authority, Extensions, Workflow State; replays of design_surfaces.py, dispatch_records.py, role_triggers.py. Not evaluated: chat-only rules, `dispatch_records.py --names`, chat wording, FO's four-field assessment, learn, anything after 1160a3b3.
