Observer report: new-work-starts-from-a-story-map (window seed 047eb709 to 1095ca51 on spacedock-state/dev2, 52 task-path commits). Observer: kc-dev-flow-2:observer, sonnet, 2026-10-23.

violation | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check --seed <task>` and holds the gate until it exits 0" (backlog, Seed check) | evidence: replay at the backlog artifact sha 047eb709 exits 1: "'Visible change:' is not 'none' but 'Surfaces:' has no 'ui'" (275ba914); fixed after the gate was approved (94c41e13).
ok | rule: design_surfaces.py check (ideation) | evidence: replay at e81c328d exit 0 (6dc9dda4).
violation | rule: "When `## FO alignment` records alignment as needed, FO records the alignment result as a `Result:` line before dispatching the worker" (ideation) | evidence: ideation-1 dispatched (09d70ca1) with no Result line; the worker held (e5aec638); Result added later (eb0ed645).
violation | rule: "When the Captain chooses differently from the recommendation, FO writes `Override: …` in the gate resolution reason" | evidence: D1, D2, D4 Override lines sit under ## FO alignment "(to be bound at the ideation gate)" (56be1df8); the ideation gate reason does not carry them; ledger "override": null (ac097d79).
violation | rule: "Preserve the approved outcome, scope, non-goals, budget and stop condition in the body" (Schema) | evidence: the seed has no budget or stop condition; non-goals "to be set at ideation" (047eb709).
violation | rule: "Scope, value, threshold, tolerance, risk-acceptance and acceptance-criteria changes require the Captain" (step 4) | evidence: AC-13 is headed "(Amended by Captain, amendment 2; replaces AC-2)" but its Source line adds the FO fix authorization's lens arm and source kinds; Amendment 2's Design names only the date rule (3c9d5802).
violation | rule: "files it as a new backlog task with `spacedock new` … or names the backlog task that already holds it" (step 5) | evidence: Codex round 4 P2 comment:4355609818 declined in the gate summary with no task named (3254ce89).
violation | rule: "FO declines it in the committed gate summary, naming the finding" (step 5) | evidence: Cycle 3 says the three #704 round-3 P2 are declined "in the merge ask" (70e28976); no #704 merge ask was committed (3146f4c5); the #705 briefing names the backlog task but not 4347244844, 4347244848, 4347244851 (3254ce89).
ok | rule: delivery_gate.py check before the merge ask | evidence: ask-1.json 03:07:19Z head 32ad029f… before the briefing 03:07:33Z (3254ce89).
ok | rule: sufficiency and minimal necessity | evidence: both in ask-1.json (5bb6397a).
ok | rule: delivery gate question clauses | evidence: later rounds, full head, worktree removal (3254ce89).
ok | rule: rounds counted | evidence: "External rounds: Codex 4 (…)" (3254ce89).
ok | rule: repair = investigation, FO fix authorization, independent validation (step 3) | evidence: 1c77e9ee, 44b05334, 6ab7ab6e; Cycle 2 9f4c00a2, 04e6eec4.
ok | rule: amendments recorded and named in the next dispatch | evidence: Amendment 2 (90c4776c); implementation-3 checklist (44b05334).
ok | rule: "exit 1 or 2 holds the ask" | evidence: the #704 hold recorded; the Captain merged #704 himself (3146f4c5).
ok | rule: dispatch records | evidence: "11 dispatch record(s) complete".
ok | rule: decision-ledger rows | evidence: 3 rows by person:captain (ac097d79, 8e6e255e, e6032068).
ok | rule: role_triggers | evidence: "2 event(s) read at HEAD, each with a call or a waiver."
observed | rule: Reviewer lines | evidence: engineering-reviewer opus (eca4a766); chief-engineer opus (4dfb2816).
ok | rule: peers | evidence: rulings quote his own words (047eb709).
can't tell | rule: "A Captain ruling is his reply to the question it settles" | evidence: D1 to D4 questions are chat only (e6032068, 56be1df8).
can't tell | rule: "FO answers a question the Captain asks at a gate before dispatching on it" | evidence: Result quotes 「照建議，但是這四題有細節要讓我知道的嗎」 (eb0ed645); ideation-2 followed 17 s later (1740a1dd); the answered-note is dated the next day (e09e1a7d).
can't tell | rule: one entry per amendment (scope growth) | evidence: Result point 4 scope growth named only in the note and gate question (e09e1a7d).
can't tell | rule: Precedent line for a decision an accepted ADR settles | evidence: D5 asked while citing ADR 0028 D3 (17a95bcc).
can't tell | rule: second reviewer trigger | evidence: "second reviewer: not triggered." (3254ce89).
can't tell | rule: present the exact candidate and PR body before authorized push/create | evidence: chat only (6da8cca3).
can't tell | rule: RoboRev High counts as P1 (step 5) | evidence: roborev:1044 High on #705 not re-run and not named in the gate summary (3c9d5802, 3254ce89).

Coverage: README rules; 52 task-path commits (FO hunks in full); 11 dispatch records; both briefings and merge asks; ledger rows; engineering-reviewer file. Sampled worker reports and Design. Replayed decision_ledger.py, design_surfaces.py, role_triggers.py, dispatch_records.py. Not evaluated: chat-only rules, design quality, PR facts, anything after 1095ca51.
