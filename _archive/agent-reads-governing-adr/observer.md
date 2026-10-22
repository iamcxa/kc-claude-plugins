Observer report: agent-reads-governing-adr (window seed 7af4ed33 to 40924e17 on spacedock-state/dev2, 27 commits). Observer: kc-dev-flow-2:observer, sonnet, 2026-10-22.

violation | rule: "When `## FO alignment` records alignment as needed, FO records the alignment result as a `Result:` line before dispatching the worker." (ideation) | evidence: "Alignment: needed at ideation" at 7af4ed33; ideation dispatches ba1462ea and 8d181a8a carry no Result line; it first appears in 8e878014, after cycle 2 was dispatched (8e878014)
violation | rule: "A Captain ruling is his reply to the question it settles, given after that question was put. FO never records as his ruling: … consent he gave earlier to a different question" (FO steps: review findings) | evidence: the ideation-2 approval reason has no words of his answering that gate question ("This briefing binds those answers after the fact; approving enters implementation."); briefing-2 02:54:36 (ab565c3c), approval 02:54:42 (99ad582d)
violation | rule: "FO appends one entry per amendment … FO adds no words of its own and does not move or rewrite a criterion" (Captain amendments) | evidence: Amendment 1 `Design:` "refuses any ADR reference that names a branch or other ref"; his words were 「禁止指向分支」; the same commit moves AC-4 to `Superseded text:` and adds AC-8 with no dispatch record covering a worker doing it (47a7cfc5)
violation | rule: "A change he asks for while the gate that would accept it is still open is not one [an amendment]: he calls `revise`" (Captain amendments) | evidence: Amendment 1 committed 02:54:26 (47a7cfc5), before the ideation attempt-2 briefing (ab565c3c, 02:54:36)
violation | rule: "FO writes `Override: recommended <option>; Captain chose <option>; area: <area>` in the gate resolution reason" | evidence: the ideation-2 reason carries the Override inside a parenthesis, so the ledger parses area as "ADR path check)" (99ad582d)
violation | rule: "`Peer: <repository or area> = <session id>; listed as <name> (<Captain or reply>, <date>)`" (peers extension) | evidence: "Peer: kc-decision-log (renamed kc-adr) = Paseo agent 1bcf070c (Captain asked …, 2026-10-21)" with no `listed as <name>` (f13397f6)
ok | rule: design_surfaces.py check | evidence: backlog f0eec4de --seed exit 0; ideation bb205099 and 47a7cfc5 exit 0.
ok | rule: delivery_gate.py check before the merge ask | evidence: ask-1.json 07:29:32Z head 589c54e57fe969b6049bad737be8615e96b7b54e before the briefing (dae03dc3); ask-2.json 07:50:15Z after approval.
ok | rule: sufficiency and minimal necessity | evidence: both keys in ask-1.json (cca582bc).
ok | rule: "His plain approval accepts that recommendation only when the gate question says so" | evidence: backlog, ideation-2 and validation questions say so (aa39685e, 14886ca2, ab565c3c, dae03dc3).
ok | rule: delivery gate question clauses (later rounds, full head, worktree removal) | evidence: present with `--match-head-commit 589c54e5…` (dae03dc3).
ok | rule: FO declines with evidence; rounds counted | evidence: "Codex 1 (code review:5608491991 …)"; each decline carries a reason (dae03dc3).
ok | rule: second reviewer line | evidence: "second reviewer: not triggered." (dae03dc3)
ok | rule: "FO names the amendment in the next dispatch's checklist" | evidence: implementation-1 "with Captain Amendment 1" (23aba77e)
ok | rule: Package root, Send-to-main, dispatch_records.py | evidence: "4 dispatch record(s) complete"; validation-1 Candidate 589c54e5… (ba1462ea, 8d181a8a, 23aba77e, bc9f6312)
ok | rule: "A peer's words are never the Captain's ruling" | evidence: D1 reason quotes only his 「可以」 (c22b11cc)
ok | rule: role_triggers.py | evidence: "1 event(s) read at 40924e17, each with a call or a waiver."
observed | rule: Reviewer line | evidence: "Reviewer: kc-dev-flow-2:engineering-reviewer opus 2026-10-22" (95248898)
can't tell | rule: each Captain quote answering the named question | evidence: chat is outside state.

Coverage: the task file at 40924e17 and all 27 diffs from 7af4ed33; dispatch records; briefings 1 to 3 and validation; ask-1 and ask-2; four ledger rows; README FO-write sections; codex, copilot, roborev, peers EXTENSION.md; engineering-reviewer-1.md sampled. Not evaluated: product content, worker reports, chat-only rules, the merge itself. Noted: validation-1 names the 0.26.0 package root and "batch 4".
