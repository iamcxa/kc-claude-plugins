ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: "同意這些內容", "照建議", "進實作", "准合併"; corresponding questions recorded, no peer substitution (71df79d15).
ok | rule: "only when the gate question says so" (FO steps: review findings) | evidence: "FO recommends approve; approving accepts that recommendation"; revision: "FO recommends revise; approving accepts it" (71df79d15).
ok | rule: "FO records the alignment result as a `Result:` line before dispatching the worker" (ideation) | evidence: "Result: aligned at backlog" (d8bc20538, before dispatch record 057f48b58).
ok | rule: "FO saves those scope notes, the checklist, the model it dispatches on and the SHA" (Stages) | evidence: "Dispatched: 5725d495bb83a17ec13616bb5421bf5ffdc71f70", "Model: gpt-6-astra", "Candidate: 58c9d0f26c78b4b038668b7170389512d8e727e0" (71df79d15; five records).
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (backlog; ideation) | evidence: "seed fields and FO alignment recorded"; "design surfaces presentable"; three archive replays exit 0 (9d57e435, c2efe28f, d3f33b36).
violation | rule: "Supersedes: <acceptance-criterion ids, or none>" (Captain amendments) | evidence: "Captain: 「照建議改 AC-3」" but "Supersedes: none" (2eddb51b0); validation-2 used it; amendment 2 later records "Supersedes: AC-3" (f7c1ba534).
ok | rule: "FO names the amendment in the next dispatch's checklist" (Captain amendments) | evidence: "Captain amendment 1" (7f0eef7b0, validation-2).
ok | rule: "FO confirms the validation ADR lint passes before presenting the gate" (FO steps: decision records) | evidence: "exits 0: 43 records, 0 legacy" (71df79d15).
ok | rule: "FO may explicitly decline evidenced Deferred risk or Polish" (FO steps: review findings) | evidence: "FO declines: Deferred risk F2"; "no such dispatch is planned"; question pins 58c9d0f26 (58d4e3260).
ok | rule: "A merge ask names each listed reviewer that was not read" (Extensions) | evidence: "copilot not run:"; "insufficient remaining quot" (58d4e3260, summary).
can't tell | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Delivery authority) | evidence: "time": "2026-10-29T10:56:17Z", "head": "58c9d0f26c78b4b038668b7170389512d8e727e0" (uncommitted merge/ask-1.json); briefing committed 10:38:01Z (58d4e3260). Earlier shell evidence unavailable.
ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: "sufficiency": "an implementation dispatch is refused"; "necessity": "five files" (ask-1.json, uncommitted; corresponding summary 58d4e3260).
observed | rule: "Reviewer:" (Stages) | evidence: "Reviewer: kc-dev-flow-2:engineering-reviewer opus 2026-10-29" (71df79d15); role_triggers: "each with a call or a waiver", no next: lines.

can't tell | rule: "wait for every member's sufficient committed evidence" (Batch gates) | evidence: "joint batch-10" (71df79d15); sibling timing unexamined.
can't tell | rule: "FO counts rounds" (FO steps: review findings) | evidence: "External rounds: Codex 1"; "RoboRev clean" (58d4e3260); complete provider history outside state.
can't tell | rule: "FO runs" (Stages, post-report dispatch coverage) | evidence: "absent" (71df79d15); shell invocation unrecorded.
can't tell | rule: "FO commits task state only through SD commands" (Workflow State) | evidence: "state: update adr-reserved-when-design-names-one" (71df79d15); message cannot prove shell mechanism.

Coverage: b74b82074..71df79d15; README, task history/diff, ledger, five dispatches, four briefings, receipt; worker evidence sampled. No agent rulings, overrides, precedents, reservation obligation, third-round decline or completed delivery. Amendment 2 has no subsequent dispatch. Replays: "scope check not run: not in a git checkout". Unevaluable rules listed above.
