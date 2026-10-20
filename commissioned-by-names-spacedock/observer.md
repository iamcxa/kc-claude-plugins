Observer report: commissioned-by-names-spacedock (kc-dev-flow-2:observer, sonnet, 2026-10-20)
Window: 8cd642eb (task file added) .. 8f429da0 (state HEAD). Rules: docs/dev2/README.md, kc-dev-flow-2 0.26.0.

violation | rule: "Seed check: On the five-stage route, before `gate prepare`, FO runs `python3 <package>/scripts/design_surfaces.py check --seed <task>` and holds the gate until it exits 0." (`backlog`) | evidence: replay of the backlog briefing artifact (git-root://state/8cd642eb…) gives exit 1, "'Visible change:' is not 'none' but 'Surfaces:' has no 'ui'". The briefing was prepared 12:46:23, three seconds after the file was added. FO's alignment record was corrected only at a60423ca, after the ideation worker's "FO note" reported the same failure. (2983246e, 8cd642eb)

ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (`ideation`) | evidence: replay at the ideation briefing sha 350deea5 prints "design surfaces presentable", exit 0. (5b21cf29)

violation | rule: "FO counts rounds and records the count in the committed gate summary." (FO steps: review findings, step 5; codex extension "FO counts one round per `evidence=` id") | evidence: the summary says "Codex clean on the head (evidence=summary:6291599352)" and gives no round count. The other batch-4 summaries write "External rounds: Codex N". (46cfdabe)

violation (partial) | rule: "FO may explicitly decline evidenced Deferred risk or Polish in the existing committed gate summary, naming the finding, reason, candidate revision and the lines or evidence it rests on." (FO steps: review findings, step 2) | evidence: validator F2 has two parts: an adopter stamped differently conflicts on line 2, and "an adjacent line-3 edit in a later template release conflicts". The decline covers only the first part: "F2 Deferred risk, an adopter stamped differently conflicts once on line 2 (measured 0 of 6 …)". The line-3 part appears only in the stage reports. (46cfdabe, c2b43483)

ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" | evidence: merge/ask-1.json, head 187f93a534f4792f6d747288947e2e43af589ce8, time 2026-10-20T13:27:09Z, which is not after the briefing commit 46cfdabe (13:27:16Z). ask-2 (14:23:32Z) is committed in 8f429da0. The untracked ask-3 (14:31:46Z) falls after the approval (14:31:39Z) and before the PR merge, which matches the rerun the question promises.

ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation gate) | evidence: ask-1.json holds `"sufficiency": "the template, both of this repository's READMEs and a real-binary discovery assertion name spacedock@0.27.0…"` and `"necessity": "five files, 8 insertions and 3 deletions, each named in the approved design…"`.

ok | rule: "A Captain ruling is his reply to the question it settles, given after that question was put." and each ruling quotes his words (FO steps: review findings) | evidence: backlog 「要，改」 with FO's chat question 「要開這張任務、排進下一批嗎？」 quoted in the gate question; validation 「同意合併」 answering the question in briefing-1 (ab667fd7, 8f429da0). The backlog reason says it "binds that question and answer after the fact". Whether he saw the scope he approved is in chat.

can't tell | rule: "His plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: the ideation question says "accepts a decision's recommendation only where his ruling says so", and the recorded ruling is 「寫」 plus FO's gloss "D1 as recommended" (4b416ed2). The D1 question and his full reply are in chat.

ok | rule: validation approval accepting a recommendation, and "Override:" where his choice differs | evidence: the question says "FO recommends approve; approving accepts that recommendation". The reason ends "as recommended", so no Override is owed. No decision is recorded by `agent:first-officer`, and no `Precedent:` exists. (46cfdabe, 8f429da0)

ok | rule: dispatch record holds scope notes, checklist, model, SHA, `Candidate:`, `Package root:`, completion line (Stages) | evidence: ideation-1, ideation-2, implementation-1 and validation-1 each carry them, and validation-1 has the full-SHA "Candidate: 187f93a534f4792f6d747288947e2e43af589ce8". `dispatch_records.py` printed "4 dispatch record(s) complete" (exit 0), and `--names` exited 0 on each.

ok | rule: "Under the Captain's grant quoted in its dispatch, the implementation worker opens the task's Draft PR" (Delivery authority) | evidence: implementation-1 quotes "No ask on a repo Kent owns: push a branch and open a Draft PR…". (395ed417)

ok | rule: roborev "Instruction FO adds to the scope notes" (Extensions) | evidence: implementation-1 carries the `roborev_gate.py` instruction. The summary records "roborev clean (evidence=roborev:931)".

ok | rule: "FO records `second reviewer: <name> because <trigger>` or `second reviewer: not triggered`" (Extensions) | evidence: "Second reviewer: not triggered (no db surface, pilot profile, …)". Casing differs from the rule text. (46cfdabe)

ok | rule: FO `## FO alignment` records: Alignment, `Release review: not needed: <reason>`, `Surfaces:`, `Visible change:` (`backlog`) | evidence: all four present in the task file at 8cd642eb. The corrected `Visible change: none` is at a60423ca. No Captain amendment or `Reviewer:` line exists, and none was owed (no scope change, Surfaces none, sonnet, validation not sent back).

ok | rule: `role_triggers.py` prints no `next:` line | evidence: "role triggers: 0 event(s) read at 8f429da0…, each with a call or a waiver."

ok | rule: "FO commits task state only through SD commands … never by staging the state checkout with `git add -A`" (Workflow State) | evidence: all 21 window commits touch only this task's paths.

ok | rule: peers (Extensions) | evidence: none of the three rulings quotes a peer. Each cites "chat" as its source.

can't tell | rule: "A follow-up message to a worker FO resumes is a dispatch too" (Stages) | evidence: 56f06798 ("settle Compass path and limit AC-4", 16:38:41) follows 4897512f by 2.5 minutes, and 2c945a94 (21:08:02) follows c2b43483 by 1.5 minutes. Whether FO messaged the worker or edited the report is not in state; only four dispatch records exist.

can't tell | rule: "FO confirms the validation ADR lint passes before presenting the gate" (FO steps: decision records) | evidence: the worker report records "`adr_lint.py docs/adr --since ad44f0cb…` … exit 0", but FO's own confirmation leaves no record.

Coverage: read fully: the task file at TO, its diff over all 21 window commits, four dispatch records, three briefings, three ledger rows, ask-1..3, and the README rules. Replayed: `design_surfaces.py` at 8cd642eb and 350deea5; `dispatch_records.py`; `role_triggers.py`. Not evaluable: chat exchanges, the PR (CI, ready state, merge command and `--match-head-commit`, worktree removal), the sentinel, merge guard and archive (after the window), and the rules in the chat-only list.
