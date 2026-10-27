ok | rule: "FO records the choice" (backlog) | evidence: "profile: pilot"; backlog approval "Captain 「准」" (548f2ff6).
ok | rule: "FO saves those scope notes, the checklist, the model it dispatches on and the SHA it dispatches from" (Stages) | evidence: "Model: sonnet"; "Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.31.0"; three complete dispatch records (548f2ff6).
ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: "Captain 「准」", "Captain 「全准」", "Captain 「合併」", each linked to its gate question (548f2ff6).
ok | rule: "only when the gate question says so" (FO steps: review findings) | evidence: "approving accepts that recommendation and D1 as recommended" (548f2ff6).
ok | rule: "A peer's words are never the Captain's ruling" (Extensions → peers, Read) | evidence: "by: person:captain"; all three reasons quote Captain chat, no peer attribution (548f2ff6).
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (backlog, Seed check) | evidence: "Surfaces: none"; replay with --seed: exit 0, "FO alignment recorded" (4486a307).
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (ideation) | evidence: "design surfaces presentable"; artifact replay exit 0 (824de8d6).
ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Delivery authority) | evidence: ask-1 "time": "2026-10-26T17:30:12Z", "head": "c2f3e313f4c04c243f5a49b4f72b876ff35b4d9b"; briefing committed 17:30:17Z (0c1d252a).
ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: ask-1 sufficiency "the Codex reader now exits 1"; necessity "two files" (0c1d252a).
ok | rule: "FO may explicitly decline evidenced Deferred risk or Polish" (FO steps: review findings, 2) | evidence: "FO declines: Polish F1", "Deferred risk F2", with reasons and candidate bound by the briefing question (0c1d252a).
ok | rule: "FO counts rounds and records the count" (FO steps: review findings, 5) | evidence: "External rounds: Codex 1"; local RoboRev separately recorded (0c1d252a).
violation | rule: "FO records `second reviewer: <name> because <trigger>` or `second reviewer: not triggered`" (Extensions) | evidence: "absent"; the task changes review rules (548f2ff6).
violation | rule: "is landed as an ADR before the next gate is presented" (FO steps: decision records) | evidence: "SKIPPED: Version bump and ADR"; "D1 was settled at the gate"; enduring thread-resolution ruling, no reserved/landed record (548f2ff6).
can't tell | rule: "FO reads each round" (Extensions → codex, Read) | evidence: "receipt at 2026-10-26T17:24:50Z"; reader output/evidence id absent, PR outside inputs (548f2ff6).
can't tell | rule: "FO reads the result as the file says" (Extensions) | evidence: Copilot result "absent"; PR review outside inputs (548f2ff6).
can't tell | rule: "FO runs the stage's minimal acceptance script exactly as written in a fresh shell" (validation) | evidence: FO-run record "absent"; worker output cannot establish FO's shell run (548f2ff6).

Coverage: 14cfc902..548f2ff6; fully read README, task history/diff, dispatches, briefings, ledger and committed ask-1; sampled worker reports only for records. Role-trigger replay: zero events. Excluded untracked ask-2. No amendments, overrides, precedents, delegated rulings, reviewer-observation triggers or completed delivery. Chat-only exclusions omitted; remaining evidence limits above. Architecture decision record = ADR.
