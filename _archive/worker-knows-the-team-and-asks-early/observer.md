Window: 49ba8c8aeeae0e4a78d2d2f98ca2f6ed270d3108..8b10e91f5e93bbd2755ddb090f1d2466317ce147; task-relative paths.

violation | rule: "Stage workers run on the workflow's default model." (Stages) | evidence: "Model: gpt-6.1-sol" in dispatch/implementation-{1,2}.md; README default sonnet (8b10e91f5).
violation | rule: "when the design is hard to reverse" / "says so in the dispatch" (ideation) | evidence: "Model: gpt-6-astra" in dispatch/ideation-{1,2}.md; qualifying reason "absent" (8b10e91f5).
observed | rule: "Reviewer:" (Stages; observer condition: stronger ideation) | evidence: "absent"; role_triggers: "0 event(s)" (8b10e91f5).
ok | rule: "FO records the choice" (backlog) | evidence: "profile: pilot"; "Surfaces: none"; "Visible change: none" (8b10e91f5).
ok | rule: "FO records the alignment result" (ideation) | evidence: "Result: aligned 2026-10-26" precedes ideation dispatch decccadd5 (3fe5f2623).
ok | rule: "FO saves those scope notes" (Stages) | evidence: "Package root:"; completion-to-main throughout; "6 dispatch record(s) complete" (8b10e91f5).
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (backlog/ideation) | evidence: "FO alignment recorded"; both ideation copies: "design surfaces presentable"; exits 0 (4555e8a47, ac429e129, 0c9efba0c).
ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: "准", "全准", "合併" with corresponding questions; all say "approving accepts that recommendation" (8b10e91f5).
ok | rule: "a peer's words are never the Captain's ruling" (Extensions/peers) | evidence: "Captain 「全准」 (chat, 2026-10-27)"; Captain-sourced throughout (8b10e91f5).
ok | rule: "FO records each printed" (FO steps: number guards) | evidence: "ADR: 0037" before implementation; repeated in dispatch (df8665210, 6d4874353).
ok | rule: "FO confirms the validation ADR lint passes" (FO steps: decision records) | evidence: "37 ADR file(s) checked, 0 legacy", "exit 0" before briefing (61c99b872).
ok | rule: "FO may explicitly decline evidenced Deferred risk or Polish" (FO steps: review findings) | evidence: "FO declines: Deferred risk F1" through F7; candidate/reasons/evidence recorded (062b7bd0a).
ok | rule: "FO counts rounds" (FO steps: review findings) | evidence: "External rounds: Codex 1"; local RoboRev uncounted (062b7bd0a).
ok | rule: "A merge ask names each listed reviewer that was not read" (Extensions) | evidence: "second reviewer: copilot because the change touches approval rules"; "copilot not run" with quota quote (062b7bd0a).
ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Delivery authority) | evidence: ask-1/2 "time": "2026-10-27T03:14:11Z"/"2026-10-27T04:09:23Z", "head": "981a4309c4ac2abbccd7e5c6a0211682ca6c554c"; briefing commits 03:14:17Z/04:09:23Z (6ac99855c, 062b7bd0a).
ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: "sufficiency": "every worker dispatch now carries a 144-word Team bullet"; "necessity": "five files" (062b7bd0a).
can't tell | rule: "preserve worker reports and verdicts" (FO steps: review findings) | evidence: "on two named models and the default model" replaces "on three models"; actor attribution requires session evidence (40836e442).
can't tell | rule: "its merge hook is registered" (Delivery authority) | evidence: "absent"; runtime configuration outside state (8b10e91f5).
can't tell | rule: "FO commits task state only through SD commands" (Workflow State) | evidence: "state: update worker-knows-the-team-and-asks-early"; actual shell command outside state (062b7bd0a).

Coverage: Fully read history/net diff, dispatches, briefings, checks, ledger, README/extensions; replayed design snapshots. Sampled worker evidence. Amendments/overrides/precedents/delegated-approvals/repairs/sentinel inapplicable. Excluded uncommitted ask-3/chat-only rules. Unresolved: edit attribution, hooks, commit commands, external-review verification.
