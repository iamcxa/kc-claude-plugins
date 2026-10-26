fo-written-lines-checked-before-dispatch
Window: 664867ac–e0cdb3e0; 0.30.0.

ok | rule: "selected profile matches this workflow's actual ordered stages" (Schema) | evidence: "profile: pilot" (e0cdb3e0).
ok | rule: "FO also records a `Surfaces:` line" (backlog) | evidence: "Surfaces: none"; "Visible change: none" (664867ac).
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check --seed <task>`" (backlog) | evidence: "FO alignment recorded", replay fb50327e exit 0 (59180e25).
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (ideation) | evidence: "design surfaces presentable", replay ffa0f4a0 exit 0 (3310896b).
violation | rule: "before dispatching the worker" (ideation, Result) | evidence: "Recorded after the first ideation dispatch"; absent at dispatch 7038101e (fb59e618).
ok | rule: "FO saves those scope notes" (Stages) | evidence: "10 dispatch record(s) complete" (e0cdb3e0).
can't tell | rule: "A follow-up message to a worker FO resumes is a dispatch too" (Stages) | evidence: ideation resume record "absent"; message outside state (e0cdb3e0).
ok | rule: "Captain's grant quoted in its dispatch" (Delivery authority) | evidence: implementation-1 "No ask on a repo Kent owns" (043d9022).
ok | rule: "given after that question was put" (Review-finding disposition) | evidence: ledger "全准", "全准", "合併"; briefings precede resolutions (e0cdb3e0).
ok | rule: "only when the gate question says so" (Review-finding disposition) | evidence: all questions "approving accepts that recommendation" (e0cdb3e0).
violation | rule: "FO appends one entry per amendment" (Captain amendments) | evidence: accepted non-goal "changing what the README requires"; approved D3 "README gains the 14 words"; amendment "absent" (dee2eea3).
can't tell | rule: "Scope ... changes require the Captain" (review findings, 4) | evidence: extra test_sd_dispatch.py "with FO's yes"; Captain chat outside state (3e4d5737).
ok | rule: "distinct FO `fix` authorization" (review findings, 3) | evidence: implementation-3/4/6 "FO fix authorization"; validation-2/3 (e0cdb3e0).
ok | rule: "FO counts rounds" (review findings, 5) | evidence: "External rounds: Codex 3" (a12d5b5e).
violation | rule: "with the printed quote, and offers a retry" (Extensions→copilot) | evidence: only "not run (quota)"; quote/retry absent (a12d5b5e).
ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Delivery authority) | evidence: ask-1 "2026-10-25T20:17:47Z", head b0b2cbf3; briefing committed 20:17:53Z (a12d5b5e).
ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: sufficiency "checks now refuse"; necessity "twelve files" (a12d5b5e).
violation | rule: "sentinel waits for a committed observer report" (Delivery authority) | evidence: "pr: pr-merge:724"; observer.md absent (e0cdb3e0).
observed | rule: "Reviewer:" (Stages) | evidence: "kc-dev-flow-2:chief-engineer opus"; role_triggers: no next lines (f9f9b8dd).

ok | rule: "FO may explicitly decline evidenced Deferred risk or Polish" (review findings, 2) | evidence: "FO declines: Polish F1", F6, F4 reasoned (a12d5b5e).
ok | rule: "A peer's words are never the Captain's ruling" (Extensions→peers) | evidence: ledger rulings quote Captain (e0cdb3e0).
can't tell | rule: "FO runs the stage's minimal acceptance script" (validation) | evidence: "absent"; shell outside state (e0cdb3e0).
can't tell | rule: "FO commits task state only through SD commands" (Workflow State) | evidence: "absent"; shell outside state (e0cdb3e0).

Coverage: Full FO-history/diffs, dispatches, briefings/ledger, asks, README/extensions; sampled reports/design. Replayed checks. Inapplicable: agent-rulings/Overrides/Precedent/db/release.
