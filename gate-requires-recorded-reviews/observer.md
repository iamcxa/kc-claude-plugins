ok | rule: "FO records the choice" (backlog) | evidence: "profile: pilot" (f7c1ba5).
ok | rule: "FO also records a `Surfaces:` line" (backlog) | evidence: "Surfaces: none"; "Visible change: none" (f7c1ba5).
ok | rule: "A Captain ruling is his reply to the question it settles" (Review-finding disposition) | evidence: "同意這些內容"; "照建議"; "進實作"; "准合併", each with its answered question (ledger, f7c1ba5).
ok | rule: "His plain approval accepts that recommendation only when the gate question says so" (Review-finding disposition) | evidence: "approving accepts these asks and decision C" (f7c1ba5; all four questions explicit).
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (backlog/ideation) | evidence: "seed fields and FO alignment recorded"; "design surfaces presentable" (replays: 1cdfd197, 3be2d025, 15e71bdd; exits 0).
ok | rule: "FO saves those scope notes, the checklist, the model it dispatches on and the SHA" (Stages) | evidence: "Dispatched: 5725d495bb83a17ec13616bb5421bf5ffdc71f70"; "Candidate: a2317cfc55e829163e3d7fcc386968eb3eea8cf1" (f7c1ba5; four dispatch records).
violation | rule: "at a worker dispatch of its stage FO adds its instruction line to the scope notes" (Extensions; paseo) | evidence: required "Start in the assigned worktree; verify pwd and git root before edits" absent from dispatch/implementation-1.md; "Model: gpt-6.1-sol (Codex via Paseo" (f7c1ba5).
ok | rule: "FO records each printed" (FO steps: number guards) | evidence: "ADR: 0044" (b732bdcab, before implementation dispatch 6aaca91fa); "Number guards: ADR: 0044" (dispatch, f7c1ba5).
ok | rule: "FO confirms the validation ADR lint passes" (FO steps: decision records) | evidence: "adr_lint --since base --require 0044 exited 0" (f7c1ba5).
ok | rule: "FO counts rounds and records the count" (Review-finding disposition) | evidence: "External rounds: Codex 1" (f7c1ba5, validation summary; local RoboRev excluded).
ok | rule: "FO records `second reviewer: <name> because <trigger>`" (Extensions) | evidence: "Second reviewer: copilot because the change sets what a delivery gate must carry"; "answer=review:5695844356" (f7c1ba5; saved refusal matches).
ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Delivery authority) | evidence: "time": "2026-10-29T10:32:47Z", "head": "a2317cfc55e829163e3d7fcc386968eb3eea8cf1" (ask-1; briefing committed 46dc23866 at 10:37:49Z).
ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: "sufficiency": "a delivery gate's bound summary must carry its external rounds"; "necessity": "seven files" (f7c1ba5, ask-1; excerpts).
observed | rule: "Reviewer:" (Stages) | evidence: "Reviewer: kc-dev-flow-2:chief-engineer opus 2026-10-29" twice (f7c1ba5).
can't tell | rule: "wait for every member's sufficient committed evidence" (Batch gates) | evidence: "joint batch-10 delivery sitting of four gates" (f7c1ba5); other members/presentation outside task.
can't tell | rule: "FO runs the stage's minimal acceptance script exactly as written in a fresh shell" (validation) | evidence: FO execution absent (f7c1ba5); shell outside state.
can't tell | rule: "its merge hook is registered" (Delivery authority) | evidence: absent (f7c1ba5); runtime configuration outside task.

Coverage: 98655be..f7c1ba5; task/path history and diff, four dispatches/briefings, ledger, refusal and committed ask read; worker evidence sampled, not revalidated. Three artifact replays passed; scope checks unavailable outside Git. Role triggers: zero events. No agent rulings, overrides, precedents, amendments, declines or relayed peer rulings found. Uncommitted ask-2 excluded. Chat-only exclusions omitted; shell-only preflights/state-commit mechanism unverified.
