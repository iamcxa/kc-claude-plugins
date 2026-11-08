# Observer report: adr-lint-tells-supersession-assertion-from-pointer

Window: b896d419d (task file added) .. de9b4a294 (HEAD of STATE). Package 0.35.0. Counts: violation 1, can't tell 4, ok 13, observed 1.

violation | rule: "Each number or factual claim in a gate summary or PR body names the command that produced it and the date, or the report it repeats as `<whose> report, not run`, and is not stated as settled." (Captain steps) | evidence: "Release: kc-adr and kc-dev-flow-2 each get a patch release from this PR (release-please reads both plugin folders)." with no command, date or report named (review/validation/briefing-2/index.json, 84f6adfdc)

can't tell | rule: "Where two remote reviewers are listed, frontmatter `second-reviewer:` names the one that joins only when a trigger holds: ... the change touches authority, approval, merge or review rules ... FO records `second reviewer: <name> because <trigger>`" (Extensions) | evidence: "Second reviewer: Copilot because the PR changes review rules." The form is present; whether the trigger held is a product judgment, and the task's design says "No README, workflow, skill or doc text changes" (briefing-2, 84f6adfdc; task file Design)

can't tell | rule: "Scope, value, threshold, tolerance, risk-acceptance and acceptance-criteria changes require the Captain." (FO steps: review findings, step 4) with "exit 1 or a missing record returns through the existing feedback route" (Decision records) | evidence: FO message turned the dispatched check "adr_lint.py docs/adr --since <base> exits 0" into SKIPPED: "the candidate's own checker is the one that rules here" (dispatch/implementation-1-message-1.md, 1ac3ebf10). No Captain words record this; the gate summary shows it as "Limit:" and "exit 1, the expected old false positive". Whether this is a threshold change is a reading of the rule.

can't tell | rule: "a decision by `agent:first-officer` carries the grant it relies on" (observer check) | evidence: ledger row kind=withdrawal, by agent:first-officer, validation-1, "Captain steps step 2 rerun in the candidate's clean worktree ... summary updated to match", conn_quote null (29369e27d). README names no grant for withdrawing FO's own unresolved briefing outside a design correction; whether the Captain had already seen briefing-1 is chat-only.

can't tell | rule: "Before merging or asking, FO runs `python3 <package>/scripts/delivery_gate.py check` ..." (Delivery authority), the run after approval | evidence: merge/ask-1.json and ask-2.json are the only files; no file postdates approval 2026-11-08T03:20:12Z, and the PR merged 2026-11-08T03:20:40Z (gh pr view 806, merge a3502ac1b, head f429f0fac matches the asks). Any post-approval run leaves no record in state.

ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" | evidence: merge/ask-1.json time "2026-11-08T02:07:35Z", head "f429f0fac40511c6480fd92e2cccd4c0e94b2454"; briefing-2 added 2026-11-08T10:10:32+0800 (84f6adfdc). ask-2 (02:10:37Z) is later than that commit and not used. Caveat: ask-1 predates the captain-steps/1.md rewrite and the summary update.

ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: ask-1.json "sufficiency": "a protected file that asserts a superseded ADR's Status no longer fails the lint ..."; "necessity": "the four files are the kc-adr linter and its test, the identical dev2 copy, and the one-line un-split ..." (1c5ecc188)

ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check --seed <task>`" (backlog) | evidence: replayed on the copy at ef76e28f4: "seed fields and FO alignment recorded", exit 0

ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (ideation) | evidence: replayed on the copy at 01ecc7500: "design surfaces presentable", exit 0

ok | rule: "FO also records, under a `## FO alignment` heading ... `Surfaces:` ... `Visible change:`" and "Release review: not needed: <reason>" (backlog) | evidence: "Alignment: not needed; a lint false positive with one observed bite." "Surfaces: none" "Visible change: none" "Release review: not needed: workflow maintenance, on no journey map." (task file)

ok | rule: "FO saves those scope notes, the checklist, the model ... and the SHA it dispatches from as `<task>/dispatch/<stage>-<cycle>.md` ... (for validation a `Candidate: <full head SHA>` line)" and "FO runs `dispatch_records.py <task folder>` ... fixes each part it lists" (Stages) | evidence: five records with Dispatched/Model/Package root lines; validation-1.md "Candidate: f429f0fac40511c6480fd92e2cccd4c0e94b2454"; script run now: "5 dispatch record(s) complete", exit 0. The `main` completion sentence is replaced as the paseo extension says.

ok | rule: "After each worker report ... FO runs `dispatch_records.py --coverage <task> --stage <stage>`" | evidence: run now, ideation, implementation and validation each "dispatch coverage complete", exit 0 (the original run leaves no record)

ok | rule: "A Captain ruling ... his reply to the question it settles" and "His plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: three person:captain rows (backlog 2026-11-07T08:09:19Z, ideation 15:37:18Z, validation-2 2026-11-08T03:20:12Z), each quoting 「核准（建議）」 or 「合併（建議）」 and its question. Each briefing commit precedes its resolution. The ideation question: "核准即接受每張設計對其決定寫下的建議。要改哪件直接說。" No open Needs decision for this task.

ok | rule: "When the Captain chooses differently from the recommendation, FO writes `Override:`" | evidence: all three reasons end "Recommendation: followed."; no `Override:` line, none needed

ok | rule: "FO's delivery gate question says approval also covers later external-review rounds ... unless he says he merges or holds, and removing its clean, pushed worktree" (Delivery authority) | evidence: "Regular merge with --match-head-commit f429f0fac40511c6480fd92e2cccd4c0e94b2454 ... Approval also covers later external-review rounds on this PR, unless he says he merges or holds." (briefing-2)

ok | rule: "FO may explicitly decline evidenced Deferred risk or Polish in the existing committed gate summary, naming the finding, reason, candidate revision and the lines or evidence" (step 2) | evidence: "Declined: Deferred risk, validation-1 F1 at f429f0fac, ... (the approved design names same-line assertions only; validation-1 report)"; F2 and F3 likewise (briefing-2)

ok | rule: "FO counts rounds and records the count in the committed gate summary" (step 5) | evidence: "External rounds: 1." and "External round sources: Codex reviewed f429f0fac" (briefing-2)

ok | rule: "FO runs the stage's minimal acceptance script under Captain steps, names its record on the summary's `Captain steps:` line" (validation) | evidence: "Captain steps: .../captain-steps/1.md"; the record has Candidate, Asked, Ran, Observed and "Only he can:" for both steps (29369e27d). `delivery_gate.py steps` was not run against a message file.

ok | rule: peers listed under `extensions:`: no Captain ruling quotes a peer's words | evidence: all three reasons quote the host question dialog choice, no peer text (ledger)

observed | `Reviewer:` line | evidence: absent. Ideation ran on claude-opus-5-5 (dispatch/ideation-1.md); Surfaces none; validation not sent back twice. `role_triggers.py STATE TASK --rev HEAD`: "0 event(s) read at HEAD, each with a call or a waiver"; no `next:` lines.

Not applicable in this window: `## Captain amendments`, `### FO declines`, `Precedent:`, `Number guards` (no ADR landed, Surfaces none), release review, Result line.

Coverage: read fully the task file at HEAD, ledger rows for this task, all five dispatch records, both briefing-2 and copilot-not-run, merge/ask-1 and ask-2, captain-steps/1.md with diff, README (all 629 lines). Sampled: captain-steps logs (heads only), 236c53cbe hunk. Not read: validation/ and implementation/ evidence directories (worker evidence, out of scope), briefing-1 of validation. Chat-only rules not evaluated. Outside state: PR #806 merge facts (read by `gh pr view`), the Captain's chat, any Copilot or Codex PR comment.
