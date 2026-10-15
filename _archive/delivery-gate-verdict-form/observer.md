Window: `13942e2e` (task file added) to `d2a39f73` (HEAD, validation approval recorded). There are four gate rulings, two amendments and 13 dispatch records. The ledger shows every ruling as `by: person:captain` with `override: null`.

ok | rule: "A Captain ruling is his reply to the question it settles, given after that question was put" (Review-finding disposition) | evidence: each briefing commit precedes its resolution (a5ebe691→a00ce24b, 1ae2ebeb→45a414eb, 72754dfa→17a5ff85, bff02bf3→d2a39f73); each reason quotes 「准」 | ledger rows 4–7

ok | rule: "His plain approval accepts that recommendation only when the gate question says so" (Review-finding disposition) | evidence: "Approving accepts FO's recommendations: drop the 26-word workflow.md sentence ... and decline findings F1 to F5" (d2a39f73 briefing); ideation-2: "Approving accepts D1 as recommended" | ok

ok | rule: "FO's delivery gate question says that approval also covers later external-review rounds on the same PR" (Delivery authority) | evidence: "Approval also covers later external-review rounds on this PR, per Delivery authority." (bff02bf3)

ok | rule: "FO records `second reviewer: <name> because <trigger>` ... in the gate summary"; "<name> not run: <reason>"; round count (Extensions; review findings step 5) | evidence: "Second reviewer: copilot because the change alters the check FO runs before a merge ask (merge rules). copilot not run: Copilot refused for quota"; "External rounds: Codex 4" (bff02bf3)

ok | rule: "`Precedent: ADR <number> — 「<that ADR's Words line>」`" (review findings) | evidence: "Precedent: ADR 0013 — 「不等 Copilot，也要修復它額度不足時的應對方式」" (bff02bf3). ADR 0013's Words line holds that quote plus a second one (「准」); only the first is quoted.

ok | rule: "Where RULES list `peers` ... no Captain ruling quotes a peer's words" (Extensions) | evidence: both amendments quote only 「都按建議核准」 and 「好」 (e04ed03a, d911f371)

ok | rule: "FO names the amendment in the next dispatch's checklist" (Captain amendments) | evidence: "Move AC-4 verbatim under Captain amendment 1" (implementation-4); "Captain amendment 2 applied" (ideation-2)

ok | rule: sending a task back "is recorded as an amendment ... FO then runs `status --set`, and that stage's gate is approved again" | evidence: `-status: validation / +status: ideation` in d911f371; ideation-2 gate approved 17a5ff85

violation | rule: "FO adds no words of its own" (Captain amendments) | evidence: Amendment 2 `Design:` reads "The bite is unchanged ... Reading PASSED or REJECTED stays FO's judgement at the gate." Neither sentence is in his `Asked:` question or his 「好」 (d911f371). AC-12's Limit later attributes the second sentence to "(Captain, amendment 2)".

violation | rule: "writes any replacement as a new `**AC-N**` ... that says 'Amended by Captain, amendment N'" (Captain amendments) | evidence: AC-8 carries the phrase; AC-9 to AC-14, which replace AC-1 to AC-3 and AC-5 to AC-8 under amendment 2, do not (7326e2a1). The ideation-2 checklist does not ask for it. Each superseded entry also ends with a line the format does not list: "Replaced by AC-8." and "Replaced by AC-9 to AC-14."

can't tell | rule: "acceptance-criteria changes require the Captain" (FO steps: review findings, step 4) | evidence: AC-8 was edited in place from "latest section that carries a counting form" to "newest validation section decides" (122d4c90, a validation-report commit). The implementation report says "edited in place on FO's instruction (id kept)" (3502bdb2). No Captain quote for it in state. Amendment 1's `Asked:` says "最新一次的驗證結論為準". Any chat approval is outside state.

violation | rule: "FO declines ... in the existing committed gate summary, naming the finding, reason, candidate revision and the lines or evidence it rests on" (step 2) | evidence: the summary gives F1's reason and the revision aa6fcc91, but for F2 to F5 only "(each with its reason there)". The reasons sit in backlog task `delivery-gate-candidate-followups` (fbb1f3d8), which cites "step 5" and the "round-3 rule" for validator findings, not an external reviewer's round.

violation | rule: "A checklist or scope-notes line that names a package script writes `<package>/scripts/NAME.py` ... never the bare script name" (Stages) | evidence: "Inside delivery_gate.py and test_delivery_gate.py." (implementation-3, d6182ead). `dispatch_records.py --names` exits 1 on that file. The other 12 records pass it. State does not show whether FO ran the check before building.

ok | rule: the dispatch-record parts and the "Send your completion message to `main`" line | evidence: all 13 records carry `Dispatched:` (full SHA), `Model:`, `## Checklist`, `## Scope notes` and `Package root:`. implementation-5 words the send line differently ("Send your phase-1 report and your completion message to `main` (the README's Dispatch facts ...)").

can't tell | rule: "the instruction a worker followed outlives the session" (Stages) | evidence: validation-3 had its candidate head and checklist rewritten 23 seconds after creation (ae63c4db→385aedda), and implementation-4 was rewritten about a minute after (b96254ed). State does not show which text each worker received.

can't tell | rule: "FO confirms both goal sufficiency and minimal necessity"; the acceptance script's "every step in full beside its observed output"; `delivery_gate.py check` before the merge `gate prepare`; `package_version.py`, `workflow_checkout.py` and `pr_watch.py add` | evidence: "necessity" and "sufficiency" are absent from the task file and all four briefings. The validation-gate summary carries only "FO ran the six-step acceptance script ... every step matched" and lists results in a parenthesis. The `delivery_gate.py` run in state is the validator's. FO's own runs and what the Captain saw are in chat or the shell.

can't tell | rule: backlog "Gate content" lists `Surfaces:`, `Visible change:` and the `## FO alignment` need | evidence: absent from the backlog briefing summary. The artifact it points to, the task file, holds them (`Surfaces: none`, `Visible change: none`).

observed | rule: `Reviewer:` line under `## FO alignment` | evidence: absent in the task file at HEAD, and `git log -S'Reviewer:'` finds none. Validation was rejected once (cycle 1) and the task was sent back from validation to ideation once (amendment 2).

Coverage: Read in full: README rules, ledger rows for the task, all 13 dispatch records, all four briefings, the amendments, FO alignment, Feedback Cycles, the ideation, implementation and validation reports and the follow-up task. Sampled: the first design text only as superseded history. Not evaluable from state: chat exchanges, PR #647, FO's shell runs, and the `design_surfaces.py check --seed` run (only the briefing text names it).
