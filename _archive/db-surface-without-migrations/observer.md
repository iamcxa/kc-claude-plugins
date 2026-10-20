Observer report: db-surface-without-migrations (kc-dev-flow-2:observer, sonnet, 2026-10-20)
Window: d194ccdc (task file added) .. eb4921df (state HEAD). Rules: docs/dev2/README.md (kc-dev-flow-2 0.26.0).

ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (backlog Seed check; ideation Gate content) | evidence: replay in empty temp dirs: backlog sha 93062db4 with `--seed` printed "FO alignment recorded", exit 0; ideation sha 5b21cf29 printed "design surfaces presentable", exit 0 (briefings fbd2ab1b, d710989d)

ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Delivery authority) | evidence: merge/ask-1.json head 8c3a60e1312b289a768a7156af771bd3df49bb7e, time 2026-10-20T13:27:34Z, one second before the briefing commit 4d31a1ca (13:27:35Z). ask-2 (14:32:30Z) and untracked ask-3 (14:33:17Z) came after approval (14:33:11Z), before the 14:33:25Z merge.

ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: ask-1.json holds "sufficiency": "a db task in a repository that declares `migrations-path: none` passes the number guard…" and "necessity": "number_guards.py, its tests, one workflow.md bullet…" (4d31a1ca)

ok | rule: "A Captain ruling is his reply to the question it settles, given after that question was put." (FO steps: review findings) | evidence: ideation reason quotes "D1 「可以」 … D2 「要」", briefing d710989d precedes the resolution (b8b3daca); validation reason quotes "Captain 「合併」 (chat, … question 19)", briefing 4d31a1ca precedes eb4921df.

can't tell | rule: same ruling rule, backlog gate | evidence: the reason quotes 「按你建議」. The file was created at d194ccdc (12:56:10), the briefing at fbd2ab1b (12:56:35) and the resolution at 47d0967c 3 seconds later, with "this briefing binds that question and answer after the fact". Whether the scope he approved in chat matches the file text is in chat.

ok | rule: "His plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: ideation question "An approval accepts a decision's recommendation only where his ruling says so"; validation question "FO recommends approve; approving accepts that recommendation". Every choice matched the recommendation, so no `Override:` is owed (ledger: override null on all three).

violation (partial) | rule: "FO counts rounds and records the count in the committed gate summary." (FO steps: review findings, step 5) | evidence: summary says "Codex clean on the head (evidence=summary:6291610625)". It gives no round count; one evidence id is the only trace (4d31a1ca briefing summary).

ok | rule: "FO may explicitly decline evidenced Deferred risk or Polish in the existing committed gate summary, naming the finding, reason, candidate revision and the lines or evidence it rests on." (step 2) | evidence: "FO declines: Deferred risk, roborev:932 High, … (outside the Captain's D2 … measured 0 such files in relay, web and this repository, and qnow declares a real directory); Polish, the help test is renamed and extended beyond AC-5's one named exception" (4d31a1ca). The head 8c3a60e1 is named in the same summary, not in the decline sentence. The roborev EXTENSION.md says this local gate is never an external round, so no P1 waiver applies.

ok | rule: "FO records `second reviewer: <name> because <trigger>` or `second reviewer: not triggered`" (Extensions) | evidence: "Second reviewer: not triggered (Surfaces none, pilot profile, no merge, approval, authority or review rule changed)" (4d31a1ca); capital S differs from the rule text.

ok | rule: dispatch record holds scope notes, checklist, model, SHA, `Candidate:` for validation, `Package root:`, completion line (Stages) | evidence: ideation-1, ideation-2, implementation-1, validation-1 each carry them; "Candidate: 8c3a60e1312b289a768a7156af771bd3df49bb7e". `dispatch_records.py` printed "4 dispatch record(s) complete"; `--names` exit 0 on each. implementation-1 carries the roborev extension line.

can't tell | rule: "FO may correct design prose/Mermaid … under an actual Captain grant covering that task's exact design section" and "A follow-up message to a worker FO resumes is a dispatch too" (ideation; Stages) | evidence: 81ffa518 (16:31:21, 3 minutes after the worker's 694c0a36) edits the Mermaid, counter wording and report form, before any gate. State shows no Captain grant and no third dispatch record; only ideation-1 and ideation-2 exist. Commits are all authored "Kent", so who wrote it is outside state.

ok | rule: "FO confirms the validation ADR lint passes before presenting the gate." (FO steps: decision records) | evidence: the validation report records `adr_lint.py docs/adr --since ad44f0cb…` "26 ADR file(s) checked, 0 legacy", exit 0 (88b9a864), before the briefing (4d31a1ca). No ADR number was reserved; the design says "No new ADR number is reserved".

ok | rule: FO records `## FO alignment`, `Surfaces:`, `Visible change:`, `Release review:` (backlog) | evidence: "Surfaces: none / Visible change: none / Release review: not needed: workflow maintenance, on no journey map." (d194ccdc). Content not judged.

ok | rule: "FO's delivery gate question says approval also covers … merging the full head" (Delivery authority) | evidence: the question names `gh pr merge 686 --squash --match-head-commit 8c3a60e1312b289a768a7156af771bd3df49bb7e`, "FO merges this one PR only … every other PR, the Release PR included, is asked one at a time" (4d31a1ca). Worktree removal is not in the question; no removal appears in state.

ok | rule: peers (Extensions: `peers` listed) | evidence: no ruling quotes a peer; no `Peer:` line. The channel of his words is "chat".

observed | `Reviewer:` line: absent. None of the conditions held (Surfaces none; ideation on sonnet per ideation-1/2; validation not sent back). `role_triggers.py` printed "role triggers: 0 event(s) read at HEAD, each with a call or a waiver." No `next:` lines.

Not applicable in the window: `## Captain amendments`, `Asked:`, `Precedent:`, `Override:`, `### FO declines`, Number guards (Surfaces none, no ADR number), round 3 rules.

Coverage: read fully: the task file at HEAD, all 4 dispatch records, 3 briefings, 3 gate resolutions via the ledger, merge/ask-1 to ask-3, the full diffs of the gate and dispatch commits, and the README. Sampled: the worker stage reports (not judged), and the diff 81ffa518. Not evaluable: chat exchanges, `package_version.py`/`workflow_checkout.py` runs, the acceptance-script presentation, the Captain's view of `delivery_gate.py` output, the PR itself (Codex, CI, ready mark), the merge, sentinel and archive. ask-3.json is untracked.
