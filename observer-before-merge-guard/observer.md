Findings for `observer-before-merge-guard`, window `a4c4a84b..1cc43015` (the commit that added the task file to state HEAD).

violation | rule: "Before asking for merge, FO confirms the PR head equals the candidate the latest passing validation report names." (Delivery authority) | evidence: validation cycle 3 "Verdict PASSED at 40c714a6" (61acd8ab). The attempt-2 gate summary reads "Head 7679ab7a is the validated 40c714a6 plus a merge of origin/main a8fe8d39" (c74ca02c). No validation report names 7679ab7a; the last stage report is implementation cycle 4. The question and summary disclose the difference, and the Captain approved the head named in the question (f507067c).

violation | rule: "FO applies it and states it in the gate summary as `Precedent: ADR <number> — 「<that ADR's Words line>」`" (FO steps: review findings) | evidence: "copilot not run: Copilot refused for quota on 2026-10-13 and the Captain has not said the quota is back (ADR 0013, D2)" (70222b56, c74ca02c). `Precedent:` appears nowhere in the task. ADR 0013 has a Words line and has been on origin/main since 6d0f8da9 (2026-10-13 16:13 +0800), before the first gate summary (16:59).

violation | rule: "A checklist or scope-notes line that names a package script writes `<package>/scripts/NAME.py` with the absolute root substituted, never the bare script name." (Stages) | evidence: "roborev_gate.py evidence= line, CI green on the PR head, lint-skills.py green" (implementation-1.md, 89dc2075). "adr_lint.py docs/adr --since <base> run with its exit code" appears in validation-1.md, validation-2.md and validation-3.md (e3b19ec5, 433ad92e, 051e8d9d). Bare names also appear in implementation-2/4/5/6/7.

ok | rule: "His plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: ideation question "Approving accepts the recommendations for D2 (...) and D3 (...). D1 (a user-level guard ...) is a separate Captain-owned step" (fd29da2d). D1 was left out of the approval and is not recorded as a ruling.

ok | rule: "A Captain ruling is his reply to the question it settles, given after that question was put." (FO steps: review findings) | evidence: briefings were committed before each resolution (backlog 15:12:44 before 15:17:09; ideation 15:30:53 before 15:40:10; validation-2 17:57:01 before 18:03:37). Reasons quote 「准」 and 「批准632」 with the full question.

ok | rule: "FO's delivery gate question says that approval also covers later external-review rounds on the same PR." (Delivery authority) | evidence: "Approval also covers later external-review rounds on this PR, per Delivery authority." (f507067c, validation-2 question).

ok | rule: "FO counts rounds and records the count in the committed gate summary ... files it as a new backlog task" (review findings, step 5) | evidence: "Codex 3 (round 1 review:5500580111 ... round 3 review:5501097974, 1 P2, no P1)" and "filed as observer-check-round3-followups" (70222b56). The task file exists, with the finding and decline reason (bbd728c0).

ok | rule: "FO may explicitly decline evidenced Deferred risk or Polish in the existing committed gate summary, naming the finding, reason, candidate revision" (review findings, step 2) | evidence: "FO declines at candidate 40c714a6" with four named items (70222b56). roborev:609 is declined in the Cycle 1 entry, "on #632 0830a3be (roborev:609 confirmed a false positive by the validator; FO declines it)" (ddee0a07 range). The roborev extension says a local gate is never an external round.

ok | rule: "A listed extension that cannot run is reported as `<name> not run: <reason>`" and "`second reviewer: <name> because <trigger>`" (Extensions) | evidence: "Second reviewer: copilot because the change touches the merge path ...; copilot not run: ..." (70222b56).

ok | rule: "FO saves those scope notes, the checklist, the model ... as `<task>/dispatch/<stage>-<cycle>.md`" (Stages) | evidence: `dispatch_records.py` printed "12 dispatch record(s) complete", exit 0. A fix authorization is recorded as its own record (implementation-3, -5).

ok | rule: FO records the backlog `## FO alignment`, `Surfaces:` and `Visible change:` lines (backlog) | evidence: "Alignment: not needed ...; Release review: not needed ...; Surfaces: none; Visible change: none" (a4c4a84b).

ok | rule: a decision by `agent:first-officer` carries its grant (checklist item) | evidence: the only FO-recorded row is kind "withdrawal", reason "PR head moved from 40c714a6 to 7679ab7a" (eaf2d123). It supersedes no Captain resolution.

ok | rule: no Captain ruling quotes a peer's words (`peers` listed in `extensions:`) | evidence: all four ledger rows are `person:captain` or `agent:first-officer`, and none quotes a peer's report.

ok | rule: `Override:` where his choice differs from the recommendation | evidence: all ledger rows show `"override": null`; he accepted the recommendations.

observed | `Reviewer:` line | evidence: absent. Validation was sent back twice (Feedback Cycles, Cycle 1 and Cycle 2). Surfaces are `none`, and ideation ran on `Model: sonnet`.

can't tell | rule: "Captain 2026-10-13: 「准」 to the combined ideation gate question" | evidence: the recorded question is task-specific. The combined question's text and the parenthetical 「三個都批准，接受下列建議，照 1 → 2 → 3 實作」 are in chat only (fd29da2d). Also, the backlog reason quotes 「1-3 回報，且立即排修，順序該怎麼列？」 but the task's "Captain's words" and the briefing quote only 「1-3 回報，且立即排修」; the verbatim words are in chat.

can't tell | rule: "A merge ask names each listed reviewer that was not read" (Extensions); the codex extension says no verdict on the head means merge is not asked for | evidence: the attempt-2 summary lists no Codex round on 7679ab7a ("round 3 review:5501097974") and does not say Codex is unread there (c74ca02c). Codex's verdict on that head is on GitHub.

can't tell | rule: "Scope ... changes require the Captain" (step 4), and the cycle 3 report's "fix authorized ("a", README untouched)" and "untouched per ruling" | evidence: FO authorized the extra file `scripts/test_sd_dispatch.py` (gate summary, 70222b56). No `## Captain amendments` entry exists. Whose ruling "per ruling" cites is in chat.

can't tell | rule: "Before recommending delivery, FO confirms both goal sufficiency and minimal necessity" and "FO runs the stage's minimal acceptance script exactly as written" (validation) | evidence: the summary says "FO ran its acceptance steps as written" and nothing records sufficiency or necessity. The script in the task names a checkout at 40c714a6. Chat holds the full presentation.

Coverage: I read the task file in full (630 lines), all four gate records and briefings, the dispatch record files and the FO-written hunks. I sampled the 20 "state: update" commits by stat and read the hunks that FO wrote. I read README sections Stages, backlog, ideation, validation, Review-finding disposition, Captain amendments, Delivery authority and Extensions, plus the roborev, codex and copilot extension files at the pinned 0.21.0 and ADR 0013. I did not evaluate these rules, because their evidence is outside state: the `package_version.py` run before each dispatch, the `design_surfaces.py check --seed` run, `pr_watch.py add`, and the `@codex review` comment. The learn extension's observer-before-sentinel step, `### FO declines` and `Precedent:` for D2/D3 did not apply in this window.
