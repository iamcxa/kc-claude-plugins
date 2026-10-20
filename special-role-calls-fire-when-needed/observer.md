Observer report: special-role-calls-fire-when-needed
Window: 0b938414 (task file added) .. 8b74d9ed (state HEAD). Rules: docs/dev2/README.md, kc-dev-flow-2 0.25.0.

violation | rule: "A change the Captain makes to what he has accepted, whether at a gate approval, during implementation or at a validation gate, is an amendment." and "FO appends one entry per amendment to the task's `## Captain amendments` section" (Captain amendments) | evidence: Scope line "Captain's scope addition, 2026-10-20: 「先加第一個，第二個列入評估」, answering FO's 「1. ER：…」" written at 8b5d694b (01:13:58), after the backlog gate 82ccd969 (01:04:48) accepted "the scope above"; `## Captain amendments`: absent. Reading note: the rule lists no ideation moment, and the "revise" path covers only a still-open accepting gate; the backlog gate was closed.

violation | rule: "A Captain ruling is his reply to the question it settles, given after that question was put." (FO steps: review findings); "Approval of a validation gate is not permission to push, create or merge a PR, except as follows." (Delivery authority) | evidence: the question says "hold Release PR #672 until this merges so 0.26.0 carries it" (f4666575 briefing); the recorded reason says the briefing "stated that approval merges #682 …, removes its worktree, then merges Release PR #672 once it carries #682" (8b74d9ed). The briefing in state does not say FO merges #672. Whether chat asked about that merge is outside state.

violation (partial) | rule: "FO may explicitly decline evidenced Deferred risk or Polish in the existing committed gate summary, naming the finding, reason, candidate revision and the lines or evidence it rests on." (FO steps: review findings, step 2) | evidence: validator F5 has two parts (60-word bound; "the replay's captain-question-load clears row is vacuous in slice 1"). The gate summary declines only the first: "Polish, an owed line can pass the 60-word bound past six amendments […]" (f4666575). The second part appears only in the followups task (d3f2ff85).

ok | rule: "His plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: ideation "Approving accepts D1 to D5 as recommended" (c2dea267); validation "Approving accepts FO's recommendation to decline the Deferred risk and three Polish below…" (f4666575). No `Override:` is needed, since every choice matched the recommendation. The ideation question says D4 is "narrower than the Captain's item 1".

ok | rule: ruling "quotes his words and answers a question put before it" | evidence: all three reasons quote his words (82ccd969, dca19109, 8b74d9ed). The backlog reason says it "binds that question and answer after the fact", and the chat question is quoted in the briefing.

can't tell | rule: "FO answers a question the Captain asks at a gate before dispatching on it" (FO steps: review findings) | evidence: Scope says FO "asked him to correct that reading if wrong", but his reply is not in state. Ideation was dispatched 34s after the backlog gate was consumed (6e6361c0 → 85b88c06). Ideation D3 「Ａ」 and 「after asking what B breaks and costs」: the state question has no A/B labels. All of this is in chat.

can't tell | rule: "Before each worker dispatch FO runs package_version.py … workflow_checkout.py" (Stages); acceptance script presented "in full beside its observed output" (validation) | evidence: absent (no record). Re-runs now: package_version exit 0, workflow_checkout exit 0, README unchanged since c60e89e1. `design_surfaces.py check --seed` at 291825e9 and `check` at cd063238 both exit 0. The briefing says FO ran the script "in env -i bash", but the full presentation was in chat.

can't tell | rule: "A follow-up message to a worker FO resumes is a dispatch too" (Stages) | evidence: worker commit c0a941f6 (01:47:43) falls between ideation-1 and ideation-2. Whether a message prompted it is not in state; only ideation-1 and ideation-2 records exist.

ok | rule: dispatch record holds scope notes, checklist, model, SHA, `Candidate:` for validation, Package root, completion line (Stages) | evidence: ideation-1, ideation-2, implementation-1 and validation-1 each carry them, with a full-SHA "Candidate: f4447396265e18e7b2cbb681b4dbfe16d396530e". `dispatch_records.py` printed "4 dispatch record(s) complete" (exit 0), and `--names` exited 0 on each.

ok | rule: "FO reserves the number when it dispatches implementation" (FO steps: decision records) | evidence: "ADR: 0026" at 184ccf70 (10:05:44), repeated in implementation-1 scope notes (3af8a2ac). No other task holds 0026, and ADR 0026 is on main.

ok | rule: FO alignment `Surfaces:` and `Visible change:` (backlog); "FO records `second reviewer: <name> because <trigger>`" (Extensions) | evidence: "Surfaces: none / Visible change: none" at creation (0b938414). Gate summary: "Second reviewer: Copilot because the PR changes the review rules; copilot not run: …" (casing differs from the rule). "RoboRev local (917, 918, clean), not counted" matches the roborev EXTENSION.md.

ok | rule: `role_triggers.py` output is a violation per `next:` line | evidence: "role triggers: 0 event(s) read at 8b74d9ed…, each with a call or a waiver."

ok | rule: peers (Extensions: `peers` listed) | evidence: no ruling quotes a peer. The channel of his words is not recorded.

Not applicable: no `Reviewer:` line exists, and none of its conditions held (Surfaces none, ideation on sonnet, validation not sent back). No `Precedent:` lines.

Coverage: read fully: the task file at TO, 4 dispatch records, 3 briefings, the 3 gate resolutions via the ledger, merge/ask-1 and ask-2, the followups file, and the README rules. Sampled: security-evaluation-stage-1.md and replay/ (worker output, not judged); ask-3.json is untracked and dated 03:03:06Z, after approval and before the merge. Not evaluable: merge, sentinel and archive (after the window), `delivery_gate.py` text shown to the Captain, and all chat exchanges. Task frontmatter has no `id:`; the same holds for sampled tasks (id-style: slug).
