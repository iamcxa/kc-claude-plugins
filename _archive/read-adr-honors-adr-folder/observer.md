ok | rule: "FO records the choice" (backlog) | evidence: "profile: pilot"; "Captain 「全准」" (1eb9b20e9).
ok | rule: "FO also records, under a `## FO alignment` heading" (backlog) | evidence: "Alignment: not needed: a reviewer finding in shipped text" (d6b77cbfd).
ok | rule: "FO also records a `Surfaces:` line" (backlog) | evidence: "Surfaces: none"; "Visible change: none" (d6b77cbfd).
ok | rule: "FO records under `## FO alignment` either" (backlog) | evidence: "Release review: not needed: workflow maintenance, on no journey map." (d6b77cbfd).
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (backlog/ideation) | evidence: "FO alignment recorded"; "design surfaces presentable"; archive replays exit 0 (ea8f1b816, bd5da7a9c).
ok | rule: "FO saves those scope notes" (Stages) | evidence: "Candidate: 813e0b09cb641b82b8ca04630879cc69e922288e"; four complete dispatches (d6b77cbfd).
observed | rule: "Record chief-engineer and engineering-reviewer calls" (Stages) | evidence: "Reviewer: kc-dev-flow-2:chief-engineer opus 2026-10-27"; role_triggers: no next lines (d6b77cbfd).
ok | rule: "A Captain ruling is his reply to the question it settles" (review findings) | evidence: "Captain 「其他全照建議」"; three question-bound replies, no peer-attributed ruling (d6b77cbfd).
ok | rule: "only when the gate question says so" (review findings) | evidence: "FO recommends approve; approving accepts that recommendation" in all three questions (d6b77cbfd).
ok | rule: "FO names the amendment in the next dispatch's checklist" (Captain amendments) | evidence: "with Captain amendment 1 applied" (93e267588).
violation | rule: "and changes nothing else in it." (Captain amendments) | evidence: "after FO's explicit Supersedes-id repair."; existing Supersedes changed (95fe8ce1b, d6b77cbfd).
violation | rule: "FO appends one entry per amendment" (Captain amendments) | evidence: "accepts F1 as a host limit" approved; amendment for that accepted AC-8 exception: absent (a1e142109, d6b77cbfd).
ok | rule: "FO may explicitly decline evidenced Deferred risk or Polish" (review findings) | evidence: "FO declines: Polish F2"; "Polish F3"; reasons/candidate bound (789493ef1).
ok | rule: "FO counts rounds and records the count" (review findings) | evidence: "External rounds: Codex 1 (round 1 on this head" (789493ef1).
ok | rule: "FO records `second reviewer: <name> because <trigger>`" (Extensions) | evidence: "second reviewer: copilot because the change governs how Captain rulings are read"; refusal/retry recorded (789493ef1).
ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Delivery authority) | evidence: ask-1 "time": "2026-10-27T17:34:55Z", "head": "813e0b09cb641b82b8ca04630879cc69e922288e"; briefing commit same second (789493ef1).
ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: "sufficiency": "read-adr lists the ADR folder its caller names"; "necessity": "two files" (789493ef1).
can't tell | rule: "FO confirms the validation ADR lint passes" (decision records) | evidence: "39 ADR file(s) checked, 0 legacy"; FO confirmation outside state (d6b77cbfd).
can't tell | rule: "confirm the file still matches the reviewed source" (Delivery authority) | evidence: absent; hook/source comparison outside task records (d6b77cbfd).
can't tell | rule: "FO commits task state only through SD commands" (Workflow State) | evidence: "state: update read-adr-honors-adr-folder"; command provenance outside state (789493ef1).

Coverage: 60e360686..d6b77cbfd: full log/diff, changed sections, dispatches, briefings, ledger, ask-1, role triggers; sampled worker evidence. Replay omits scope-history. Uncommitted ask-2 excluded. No agent-rulings/overrides/precedents/numbering/repairs/archive. PR/provider unexamined.
