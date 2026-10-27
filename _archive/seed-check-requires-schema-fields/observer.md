ok | rule: "FO records the choice" (backlog) | evidence: "profile: pilot" (d35b8b9a).
ok | rule: "FO records under `## FO alignment`" (backlog) | evidence: "Release review: not needed: workflow maintenance, on no journey map." (d35b8b9a).
ok | rule: "FO also records a `Surfaces:` line" (backlog) | evidence: "Surfaces: none"; "Visible change: none" (d35b8b9a).
ok | rule: "FO records the alignment result" (ideation) | evidence: "Result: aligned 2026-10-27" (d3f7ae924;662a11c3).
ok | rule: "the gate question says so" (FO steps: review findings) | evidence: "approving accepts that recommendation"; "全准"; "其他全照建議" (d35b8b9a).
ok | rule: "never mark a peer claim direct" (peers) | evidence: "Captain 「同意開 1 到 5，第 6 項併進「GPT 夥伴」提案」 (chat, 2026-10-27)" (d35b8b9a).
ok | rule: "FO saves those scope notes" (Stages) | evidence: "Package root:"; "Model:"; "Candidate:" (d35b8b9a).
violation | rule: "repeats the lines as dispatch scope notes" (FO steps: number guards) | evidence: "absent" in implementation-1; implementation-2: "no reserved ADR number"; "ADR: 0041" added (407d1688→a869b9f9).
ok | rule: "distinct FO `fix` authorization" (FO steps: review findings) | evidence: "Phase 1 only, no commit or push"; "FO fix authorization" (d8e15c18;fdfecaa4).
ok | rule: "FO names the amendment" (Captain amendments) | evidence: "with Captain amendment 1 applied" (implementation-1,d35b8b9a).
violation | rule: "FO appends one entry per amendment to the task's `## Captain amendments` section" (Captain amendments) | evidence: "### Amendment 2 — 2026-10-28, chat" lies under "## Number guards" (169e815d;d35b8b9a).
ok | rule: "FO counts rounds" (FO steps: review findings) | evidence: "External rounds: Codex 1" (df74c954).
ok | rule: "A merge ask names each listed reviewer that was not read" (Extensions) | evidence: "copilot not run:"; "second reviewer: copilot because" (df74c954).
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (ideation) | evidence: "seed-check-requires-schema-fields.md: design surfaces presentable"; replay exit 0 (f262e0d3).
can't tell | rule: "design_surfaces.py check --seed <task>" (backlog) | evidence: "seed-check-requires-schema-fields.md: missing required body field: Non-goals"; current-schema incompatibility, event-time README unavailable (c5c3b3a5).
ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Delivery authority) | evidence: "2026-10-27T18:58:35Z"; "bd8a2c93bf1552468c5a2780c839930d3669114d", preceding briefing 18:58:36Z (df74c954).
ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: "sufficiency": "under Captain amendment 1"; "necessity": "ten files" (ask-1,df74c954).
ok | rule: "FO confirms the validation ADR lint passes" (FO steps: decision records) | evidence: "exits 0: 40 ADR files, 0 legacy" (d35b8b9a).
observed | rule: "Reviewer:" (Stages) | evidence: "Reviewer: kc-dev-flow-2:chief-engineer opus 2026-10-27" (d35b8b9a).
can't tell | rule: "FO runs the stage's minimal acceptance script" (validation) | evidence: "absent"; FO shell evidence unavailable (d35b8b9a).
can't tell | rule: "delivery_gate.py question" (Delivery authority) | evidence: "absent"; shell history outside state (d35b8b9a).
can't tell | rule: "its merge hook is registered" (Delivery authority) | evidence: "absent"; runtime configuration outside supplied inputs (d35b8b9a).
can't tell | rule: "FO commits task state only through SD commands" (Workflow State) | evidence: "absent"; shell evidence unavailable (d35b8b9a).

Coverage: 7d980111→d35b8b9a; full README/ledger/briefings/dispatches/ask-1; sampled task/diffs/reports. Both replays; role_triggers clear. Package changed; historical qualification reread. Copilot-save applicability unknown; event-time extension unavailable. Untracked ask-2 excluded.
