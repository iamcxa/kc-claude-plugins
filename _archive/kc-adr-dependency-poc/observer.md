Observer report: kc-adr-dependency-poc (window 0637ec09..HEAD a1e126ae of the state checkout; status validation, the validation approval is recorded and its application is pending). Observer: kc-dev-flow-2:observer, sonnet, 2026-10-22.

ok | rule: "His plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: backlog question "FO recommends yes; approving accepts that recommendation." and validation question "FO recommends closing; approving accepts that recommendation." (71cceb0f, aa059f3c). The backlog reason quotes 「好，開」 and the chat question 「照這樣開 POC 嗎？」, which the briefing quotes (486da5b3).

violation | rule: "A Captain ruling is his reply to the question it settles, given after that question was put. FO never records as his ruling: … consent he gave earlier to a different question" (FO steps: review findings) | evidence: the validation reason reads "Captain 「可以」 (chat, 2026-10-22) to FO recommendation 「工具搬到 kc-adr，但用 dev2 的人只要裝 dev2 一個」", but the gate question is "Close the kc-adr dependency POC as passed on its validated report, and carry its result into a dev2 task?". The briefing was committed 4 s before the record (aa059f3c, a1e126ae), and its summary already says "The Captain then chose a different shape". The CI-sync and CI-fails-on-difference details in the reason go beyond the quoted words. Whether he also answered the close question is in chat.

violation | rule: "FO writes `Override: recommended <option>; Captain chose <option>; area: <area>` in the gate resolution reason" (FO steps: review findings) | evidence: the reason has "Override: the POC recommended run-time resolution; Captain chose a CI-synced copy … area: kc-adr packaging", but decision_ledger.py gives override null and area "none" for it (a1e126ae). He chose FO's chat recommendation, which differs from the report's.

ok | rule: "A peer's words are never the Captain's ruling" (Extensions, peers) | evidence: Scope Source relays the choice "(in the kc-adr session, relayed by Paseo agent 1bcf070c and then put to him here)", then quotes his own 「我原本想像是…」, 「先poc看看怎樣更好？」 and 「好，開」. Both resolutions quote only him (0637ec09, 486da5b3, a1e126ae). The moneyflow-second-consumer claim has no quote of his own.

violation | rule: "Preserve the approved outcome, scope, non-goals, budget and stop condition in the body" (Schema) and "approves outcome, scope and budget" (backlog) | evidence: the seed has Scope, Bar and Non-goals but no word "budget" or "stop condition", and the gate question names none (0637ec09, 71cceb0f).

ok | rule: "FO also records, under a `## FO alignment` heading in the task file, whether FO direction alignment … is needed" (Stages, backlog) | evidence: "Not needed before implementation. The Captain asked for this POC (「好，開」, 2026-10-21)…", plus "Release review: not needed: the task belongs to no release." (0637ec09).

ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (Stages backlog Seed check) | evidence: `check --seed` on the copy at the briefing sha 0637ec09 exits 0. The same copy without --seed exits 1, "missing '## Acceptance criteria' section", which is also implementation-1's FAILED line (9d0d72c0..aa059f3c).

can't tell | rule: "Scope, value, threshold, tolerance, risk-acceptance and acceptance-criteria changes require the Captain" (FO steps: review findings, 4) | evidence: FO added `## Acceptance criteria` after the backlog approval ("These restate the Scope's bar line by line and add no requirement"). It carries "Falsifier:" clauses the Scope lacks. There is no `## Captain amendments` entry (22cafcd8). Whether he read it is in chat.

ok | rule: "Every worker dispatch FO builds carries that absolute path as a `Package root:` line" and "`Candidate: <full head SHA>`" (Stages) | evidence: all three records carry both lines and "Model: sonnet"; `dispatch_records.py` exits 0 and `--names` exits 0 on each. validation-1 was saved with Candidate c29f4ab9 before cycle 2, and the Candidate line was rewritten in place to 57a411c0 (4ebf5d3a) while its checklist still says "state c29f4ab9".

ok | rule: "reported as `<name> not run: <reason>`" (Extensions, roborev) | evidence: "roborev not run: no repository diff" in all three dispatch records and stage reports.

can't tell | rule: "Before recommending delivery, FO confirms both goal sufficiency and minimal necessity" and "FO runs `delivery_gate.py check` before the merge ask" | evidence: absent; no merge/ask-N.json and no PR; delivery is report.md only.

can't tell | rule: "is landed as an ADR before the next gate is presented, at latest by the terminal approval" (FO steps: decision records) | evidence: the validation reason states a direction the move task must follow; the state shows no ADR. That is outside state.

observed | `Reviewer:` line absent. `role_triggers.py … --rev a1e126ae`: "0 event(s) read … each with a call or a waiver".

Coverage: the task file at HEAD and every state commit touching the task (0637ec09..a1e126ae, 18 commits), three dispatch records, two briefing index.json files, decision_ledger.py rows, the README sections named above and the peers EXTENSION.md. report.md sampled by headings. Not evaluated: chat-only rules, the terminal ceremony, Number guards (none reserved).
