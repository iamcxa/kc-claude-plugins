Observer report: design-director-runs-ui-design-review (window seed 40afa5a1 to f40eb07f on spacedock-state/dev2). Observer: kc-dev-flow-2:observer, sonnet, 2026-10-23.

violation | rule: "FO records the alignment result as a `Result:` line before dispatching the worker." (ideation) | evidence: no Result line at the ideation dispatch 4deaa0f8; first present at 2ac35725, after the ideation report e28710f3.
violation | rule: "When the Captain chooses differently from the recommendation, FO writes `Override: …` in the gate resolution reason" | evidence: the ideation resolution reason points to FO alignment and the ledger row has "override": null; the Override lines sit in FO alignment (D-2 712e1b66, D-4 b750561c, D-6 55604578); for D-2, D-4 and D-6 the ruling answered FO's revised proposal.
violation | rule: "Preserve the approved outcome, scope, non-goals, budget and stop condition in the body." (Schema) | evidence: no budget or stop condition in the seed or at the backlog gate (ee50dacb).
violation | rule: "FO adds no words of its own and does not move or rewrite a criterion"; `Design:` (Captain amendments) | evidence: Amendment 1 Design is FO's summary plus an Evidence field (4a32ba14); Amendment 2 Design is FO's paraphrase (0f9f7567).
can't tell | rule: "A Captain ruling is his reply to the question it settles, given after that question was put." | evidence: D-6 quotes no question (55604578); amendment Asked lines paraphrase (4a32ba14, 0f9f7567); chat is outside state.
can't tell | rule: repairs require worker investigation, distinct FO fix authorization, then independent validation (step 3) | evidence: Feedback Cycles say "FO authorizes the fix directly" (50eea40b, 02bba774) while dispatches read "phase 2 … FO fix authorization" (f20fc34a); no phase-1 record, none for the Cycle 0 record named in implementation-2.
observed | rule: workers' classifications are advisory (step 1) | evidence: Cycle 1 calls F5 Polish (50eea40b); validation-1 classed it Deferred risk (fa4b4fc3); FO's reclassification not recorded.
can't tell | rule: criteria changes require the Captain (step 4) | evidence: Cycle 2 narrows where built-screen lines may sit (87fb9daa); validation judged it inside the design and F9 was declined (e26c1bc4).
observed | rule: Package root line | evidence: README labels and package roots differ across dispatches (0.27.0 vs 0.28.0) (d965779b, ece3e684).
observed | rule: Schema `id` | evidence: no `id:` (40afa5a1, f40eb07f).
ok | rule: design_surfaces.py check | evidence: --seed exit 0 at 893e4e8c; ideation exit 0 at 23820639 (ee50dacb, f860c238).
ok | rule: delivery_gate.py check before the merge ask; sufficiency and necessity | evidence: ask-1.json 06:06:19Z head e033956e… before the briefing; ask-2.json after approval (c8a83d7f, f40eb07f).
ok | rule: dispatch records | evidence: "10 dispatch record(s) complete"; validation-3 Candidate equals the asked head (d965779b).
ok | rule: approval accepts the recommendation only when the question says so | evidence: all three questions carry it; reasons quote his words (ee50dacb, f860c238, e26c1bc4).
ok | rule: round 3 declined and filed | evidence: built-screen-check-round3-followups created before the briefing (44ab1d31); second reviewer recorded (e26c1bc4).
ok | rule: peers | evidence: paseo intake marked relayed (110813f5).
observed | rule: Reviewer lines | evidence: three lines (a3a0163d); role_triggers no next: line.
can't tell | rule: number_guards.py check on the PR head before the merge ask | evidence: ADR 0030 reserved (f4228111); workers ran the check at validation.

Coverage: README, ledger rows, 10 dispatch records, both merge asks, three briefings, amendments, FO alignment, Feedback Cycles, Number guards, validation findings; sampled implementation and validation bodies and the design. Not read: most intake and replay files, the engineering-reviewer files, the PR. Not evaluated: chat-only rules, product content, anything after f40eb07f.
