Observer report: codex-reader-counts-code-review-only (window 229615a9 to f7ad5f6e on spacedock-state/dev2, 24 commits; scripts from 0.28.0). Observer: kc-dev-flow-2:observer, sonnet, 2026-10-23.

No violation found.
ok | rule: FO alignment record (backlog) | evidence: "Alignment: not needed before ideation; the Captain set the constraint. / Surfaces: none / Visible change: none / Release review: not needed …" (229615a9)
ok | rule: design_surfaces.py check --seed and check | evidence: replays exit 0 at 229615a9 and 0d9d7600; artifact rev matches (b5743e37, 835dd949)
ok | rule: "His plain approval accepts that recommendation only when the gate question says so" | evidence: all three gate questions carry it (fc274cdc, b5743e37, 835dd949)
can't tell | rule: "A Captain ruling is his reply to the question it settles, given after that question was put." | evidence: backlog and ideation briefings bound seconds before the record with "this briefing binds that question and answer after the fact"; whether the chat question carried the acceptance sentence is outside state. Validation briefing (fc274cdc, 10:35:40) precedes the record (372ad53b, 10:36:18).
ok | rule: Override line | evidence: ledger override null on all three; each approval matches the recommendation (ebd60e0d, dc74197b, 372ad53b)
ok | rule: dispatch records (Candidate, Package root, main line) | evidence: "6 dispatch record(s) complete"; validation-2 Candidate 28807397841eff05cb4b8bd06992001584d73fec (dd279389)
ok | rule: repair = investigation, distinct FO fix authorization, independent validation (step 3) | evidence: implementation-2 phase 1 (10086eab); implementation-3 FO fix authorization (37e4a5bd); validation-2 after (dd279389)
ok | rule: P1 fixed and revalidated; rounds counted (step 5) | evidence: "External rounds: Codex 2 (round 1 review:5609156241 one P1, fixed in Cycle 1; round 2 review:5612945788 on this head, one P2, declined below)" (fc274cdc)
ok | rule: FO declines with finding, reason and evidence (step 2) | evidence: "FO declines: Deferred risk, Codex P2 comment:4347371821 … Material if FO's round limit needs two clean verdicts on one head" (fc274cdc)
can't tell | rule: second reviewer trigger "the change touches authority, approval, merge or review rules" | evidence: "second reviewer: not triggered" (fc274cdc); whether the round-counting reader touches "review rules" is a judgment state does not show.
ok | rule: delivery_gate.py check before the merge ask | evidence: ask-1.json 02:35:30Z head 28807397… before the briefing; ask-2.json 02:36:24Z after approval (7534630c, f7ad5f6e)
ok | rule: sufficiency and minimal necessity | evidence: both in ask-1.json (7534630c)
ok | rule: delivery gate question clauses | evidence: `--match-head-commit 28807397…`, later rounds, full head, worktree removal (fc274cdc)
can't tell | rule: ADR landing for a ruling later work must respect | evidence: "ADR: none. The design lands no ADR." (28cd5da4); no reason on whether the Captain's optional-security-review constraint is task-only.
ok | rule: peers | evidence: all reasons quote only his words (ebd60e0d, dc74197b, 372ad53b)
observed | rule: Reviewer line | evidence: absent; role_triggers.py "0 event(s) read at HEAD …"
observed | rule: landed sentinel after the observed merge | evidence: at HEAD pr: iamcxa/kc-claude-plugins#702, status validation; merge 8bfac961 is after the window (f7ad5f6e)
can't tell | rule: FO design prose corrections need a Captain grant (ideation) | evidence: 451f1834 changes one Delivery-shape line two minutes after the worker's design commit; author not recorded.

Coverage: task file at HEAD, every diff in the window, six dispatch records, three briefings, ask-1 and ask-2, ledger rows, README, roborev, codex, copilot, peers EXTENSION.md; replays of design_surfaces.py, dispatch_records.py, role_triggers.py, decision_ledger.py. Not evaluated: chat-only rules, PR-side facts, worker report content, the merge itself.
