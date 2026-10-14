Observer report for `followup-dispatch-records-checked`. The window is `f137d87b` (task file added) to `31a4c374` (state HEAD). The task's own paths last changed at `efecebec`.

ok | rule: "A Captain ruling is his reply to the question it settles, given after that question was put" (Review-finding disposition) | evidence: ledger rows resolved by `person:captain` with quotes 「approve」, 「准」, 「准」, each with its question, `conn_quote: null`, no `agent:first-officer` row, no `Override:` (ledger; `60a5a8a7`, `9f540561`, `dd6379d2`)

ok | rule: "His plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: "Approving accepts the recommendations for D1 (...) and D2 (...)" in the ideation question (`9f540561`)

ok | rule: "peers" extension: no Captain ruling quotes a peer's words (Extensions) | evidence: all three rulings carry his own words and `conn_quote: null`; no peer quote appears (ledger)

ok | rule: "`Precedent: ADR <number> — 「<that ADR's Words line>」`" (FO steps: review findings) | evidence: "Precedent: ADR 0013 — 「不等 Copilot，也要修復它額度不足時的應對方式」" (validation briefing, `6b59b983`). `origin/main:docs/adr/0013-...` has that text as the first of two Words clauses, so the quote is partial. The ADR does not cover authority, merge or money. `origin/main` is the local ref, not fetched.

ok | rule: "FO records `second reviewer: <name> because <trigger>`" and "`<name> not run: <reason>`" (Extensions) | evidence: "Second reviewer: copilot because the change adds a check FO runs on its own records (merge rules). copilot not run: Copilot refused for quota on 2026-10-13" (`6b59b983`). Whether this change falls under the "merge ... rules" trigger is a judgement the state does not settle.

ok | rule: "FO counts rounds and records the count in the committed gate summary" (step 5) | evidence: "External rounds: Codex 1 (review:5511481463) 1 P2 fixed; 2 (...) fixed; 3 (...) 1 P2, no P1, declined under the round-3 rule into backlog task followup-dispatch-records-round3-followups" (`6b59b983`). The backlog task body carries the finding and the decline reason (`7ddd2705`).

ok | rule: "Repairs require worker investigation without candidate mutation, distinct FO `fix` authorization" (step 3) | evidence: `implementation-3.md` "phase 1 investigation only" then `implementation-4.md` "FO fix authorization"; `implementation-6.md` then `-7.md` the same way (`608effed`, `f92a2e41`)

violation | rule: "FO may explicitly decline ... naming the finding, reason, candidate revision and the lines or evidence it rests on" (step 2) | evidence: "FO declines at candidate 3a981251: ...; Deferred risk, the workflow.md clause not pinned on its own;" has no reason and no lines. The other entries give reasons but no lines (`6b59b983`).

violation | rule: "every follow-up message to a live worker, also carry ``Send your completion message to `main` (the README's Dispatch facts: ...)``" (Stages) | evidence: `implementation-3.md` reads "Send your phase-1 report and your completion message to `main` (...)", and a grep for the exact sentence finds 0 matches (`608effed`). The 0.22.1 `dispatch_records.py` still passes it.

violation | rule: "before `dispatch build`, FO runs `python3 <package>/scripts/dispatch_records.py --names <record>` on the saved record and rewrites each name it lists" (Stages) | evidence: at HEAD `--names` exits 1 on `implementation-1.md:8: bare package script name test_dispatch_records.py` (also `lint-skills.py`, `roborev_gate.py`) and on `implementation-2.md:10: ... test_sd_dispatch.py`. Some of these names are candidate-repo files rather than package scripts. (`e081c5f2`, `c3935e01`)

observed | rule: step 2 decline (same) | evidence: Feedback Cycles Cycle 1 says "Polish on the added `lint-skills.py` comment is fixed in the same repair (a comment that narrates the change is deleted)". `implementation-4.md` says "Keep the budget comment ... unchanged", and the summary says "comment kept" (`7b968795`, `f92a2e41`, `6b59b983`). The Cycle 1 line was not corrected.

observed | rule: step 3 (same) | evidence: `implementation-8.md` is a fix authorization with no phase-1 investigation. The validator's cycle 2 report supplies the reproduction (`8ef3cc59`).

can't tell | rule: "Scope, value, ... changes require the Captain" (step 4) | evidence: `implementation-2.md` "The one added file follows the precedent of #632"; the summary says "authorized by FO after CI failed (precedent #632)". Not an ADR `Precedent:` line. Whether editing `test_sd_dispatch.py`, outside the design's Files list, is a scope change, and whether he ruled on it, is in chat.

can't tell | rule: "files it as a new backlog task with `spacedock new`" (step 5) | evidence: the file arrives in a "state: update" commit (`7ddd2705`); the command is not in state.

can't tell | rule: "FO confirms both goal sufficiency and minimal necessity" and "presents every step in full beside its observed output" (validation) | evidence: the summary says "every step matched"; the full presentation and the `package_version.py`, `workflow_checkout.py` and `delivery_gate.py` runs are not in state.

can't tell | rule: "A Captain ruling ... answers a question put before it" (Review-finding disposition) | evidence: the body quotes "the Captain approved on 2026-10-13 (「按建議1,3」)". The question it answered is outside state.

Coverage: read in full the README rules above, the decision ledger rows for this task, the three briefings, all 13 dispatch records, and the Feedback Cycles and gate sections of the task file. Sampled the stage reports (finding sections only). Did not apply: Delivery authority's FO-actor grant (no FO-actor record exists), Captain amendments (none), Number guards (Surfaces: none), the Reviewer line (db, stronger-model ideation and twice-rejected validation all absent), and `EXTENSION.md` reader rules. Not read: the PR, chat, and post-merge state.
