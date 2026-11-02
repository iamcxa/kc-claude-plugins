ok | rule: "FO records the choice" (backlog) | evidence: "profile: pilot"; "Result: aligned at backlog"; "Surfaces: none"; "Visible change: none" (e26a5b175).
ok | rule: "A Captain ruling is his reply to the question it settles" (Review-finding disposition) | evidence: "可以"; "照建議", each with an answering question; no peer-attributed ruling (86e7c8c).
ok | rule: "FO appends one entry per amendment" (Captain amendments) | evidence: "Amendment 1"; "Asked:"; "Supersedes: none"; validation-2 names amendment 1; criteria retained (fae0e9c5b, 86e7c8c).
ok | rule: "FO records each printed" (FO steps: number guards) | evidence: "ADR: 0048", also in implementation-1 scope notes (7b4d8f24c).
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (backlog) | evidence: "seed fields and FO alignment recorded", --seed replay exit 0 (e26a5b175).
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (ideation) | evidence: "design surfaces presentable", replay exit 0 (43190638f).
violation | rule: "nonzero holds dispatch" (Stages) | evidence: validation-1 says "End your turn with this line as that reply"; checker rejects its noncanonical completion instruction; preserved report says "Both installed and candidate checkers exit 1 on validation-1.md" (86e7c8c).
violation | rule: "`team-lead` is not registered here" (Stages, required completion sentence) | evidence: implementation-1-message-1 contains only "Send your completion message to `main`.", omitting the required parenthesis (86e7c8c).
violation | rule: "records the round in the committed gate summary with the heading line quoted" (Extensions → copilot Read) | evidence: "The copilot outcome is review:5733112447, with no line comments"; no heading quoted (86e7c8c).
ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Delivery authority) | evidence: ask-1 "time": "2026-11-02T08:13:41Z", "head": "fef0ae5fa79a77315ce6fce069c0a3ddf06e2daf"; briefing committed 08:13:45Z (969e89341).
ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: "sufficiency": "real Claude and Codex stage workers delivered completion"; "necessity": "the six files are that rule, its checker, its ADR and its tests" (18d795890).
ok | rule: "FO may explicitly decline evidenced Deferred risk or Polish" (Review-finding disposition) | evidence: "Declined:" names validation-3 F2/F3 and reasons; RoboRev 1403 goes to the Captain's item 4 (86e7c8c).
observed | rule: "Reviewer:" (observer record check) | evidence: "absent"; ideation used Opus; role_triggers: "0 event(s)" (86e7c8c).
can't tell | rule: "FO counts rounds" (Review-finding disposition) | evidence: "External rounds: 2." Complete external PR review history is outside state (86e7c8c).
can't tell | rule: "Observe the actual repository-qualified PR merge" (Delivery authority) | evidence: "state: pending"; merge proof lies outside this window (86e7c8c).

Coverage: Full FO-field history/diff e26a5b175..86e7c8c, ledger, README at 146727de, seven dispatches, three briefings, receipt; sampled worker evidence. Replayed both design artifacts. No applicable agent-authored ruling, Override, Precedent or migration. Unresolved: external round accuracy, merge/configuration, runtime fix authorization, batch completeness and state-command provenance; excluded chat-only rules not judged.
