# Observer report: delivery-gate-ignores-url-paths-and-data-fences

Window 94fd7dbcb (task added) to 6cd2f42d9 (state HEAD audited; task last changed at 882edd500).

ok | rule: "A Captain ruling is his reply to the question it settles, given after that question was put." (FO steps: review findings) | evidence: backlog, ideation and validation-2 reasons each contain `answering 「決定：…` with the whole bound question; `quotes_bound_question` True for all three (882edd500)
ok | rule: "His plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: ideation question ends "核准即接受上列每一項建議，包括 (4) 改成工具自己寫" (089b3c2ee)
ok | rule: "Otherwise the reason carries `Recommendation: followed`." (FO steps: review findings) | evidence: all three reasons end "Recommendation: followed"; he chose 「核准（建議）」/「合併（建議）」, so no `Override:` owed and none exists (882edd500)
ok | rule: no Captain ruling quotes a peer (`peers` listed under `extensions:`) | evidence: every reason cites "host question dialog, 2026-11-09" (882edd500)
observed | rule: "a decision by `agent:first-officer` carries the grant it relies on" (ledger check) | evidence: only FO row is the validation-1 withdrawal, "Candidate 6f2fe8f33 superseded by the merge of main at b8362fb90; validation-2 PASSED there."; no grant, and a withdrawal is not a ruling (882edd500)
observed | rule: "A Needs decision put to the Captain at a gate carries FO's recommendation." (FO steps: review findings) | evidence: D2 is labelled "(FO)", absent from the ideation question; implementation-1 dispatch says "D2 is FO's, filed as backlog task delivery-gate-pr-body-attribution-link", which is `status: backlog`, "no Captain words yet" (40bb73ebf, b63df43d5)
ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (backlog, ideation) | evidence: replay exit 0, backlog `--seed` at d1fd04dab "seed fields and FO alignment recorded", ideation at 8fff5c85e "design surfaces presentable"
ok | rule: "FO also records ... `Surfaces:` ... `Visible change:`" (backlog) | evidence: "Surfaces: none", "Visible change: none", "Release review: not needed: workflow maintenance, on no journey map." (task file)
ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Delivery authority) | evidence: merge/ask-1.json time "2026-11-09T14:47:41Z", head "b8362fb901cd27bd367be1cd5b826f21fefad70e"; briefing-2 added d4467a794 at 14:47:54Z
ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: ask-1.json keys `sufficiency` and `necessity` both present (90839fcb0)
can't tell | rule: same check, attempt 1 (withdrawn, head 6f2fe8f33) | evidence: no merge/ask file for that head; the task may predate the record (1dc5773a7)
ok | rule: "`delivery_gate.py steps <record> --text-file <message>` prints the record's form; nonzero holds the ask" (Captain steps) | evidence: replayed on captain-steps/1.md and 2.md with each briefing text: "captain steps complete: 2 steps, 2 left to him", exit 0 (6f2d65169)
ok | rule: "merging the full head `<package>/scripts/delivery_gate.py check` passes, with `--match-head-commit` set to it" (Delivery authority) | evidence: "carried: 2 of 3" (gh pr list, state refs)
observed | sync PRs carry no task ask | evidence: "sync: #813" (gh pr list)
observed | rule: "reported as `<name> not run: <reason>`" (Extensions) | evidence: briefing-2 "copilot not run: \"Copilot was unable to review this pull request"; "Copilot not read: b8362fb901cd27bd367be1cd5b826f21fefad70e" (d4467a794)
observed | rule: `Reviewer:` line (ideation ran on a stronger model) | evidence: ideation-1 "Model: claude-opus-5-5"; `Reviewer:` line absent (6ce1a42f7)
observed | rule: "Where `learn` is listed, the sentinel waits for a committed observer report." (Delivery authority) | evidence: frontmatter `pr: iamcxa/kc-claude-plugins#818`, `status: validation`, validation gate `state: pending`; no `pr-merge:` sentinel (882edd500)

`role_triggers.py` printed no `next:` line ("0 event(s) read at 882edd500, each with a call or a waiver"), so no violation rows.

Coverage: read fully: frontmatter, Scope, Design, Decisions, ACs, ledger rows, five dispatch records, both captain-steps records, ask-1.json, four briefings, the D2 task. Sampled: Stage Report headings and summaries; about 190 evidence files untouched. `merge_audit.py` exit 0, no fetch warnings. Missing records may mean chat approval or state outside this repository; PR #818 and the squash merge were not read from GitHub. Not evaluated: `dispatch_records.py --coverage` runs, the gate-summary claim-source rule (enforced by `question`, run record not in state), extension steps for `learn`, `peers`, `paseo`, `fo-feedback`.
