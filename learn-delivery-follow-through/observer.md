Observer report for `learn-delivery-follow-through`, window 047ed427..db238dbb. No later state commit touches this task. The state HEAD is now e2414930, an unrelated archive of `fo-record-checks`.

ok | rule: "A Captain ruling is his reply to the question it settles, given after that question was put." (FO steps: review findings) | evidence: backlog: "Captain 2026-10-13: 「開」 to the backlog gate question \"Schedule now as Pilot and enter ideation…\"", and Pilot is inside the question (df2376ff)

ok | rule: "His plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: ideation question: "Approving accepts the recommendations for D1 (…), D2 (…) and D3 (…)"; reason quotes 「准」 (3634bba8)

ok | rule: same, plus "Gate content: … the user's pending delivery decision" (validation) | evidence: validation question "Deliver #639 head 4072363b … Approval also covers later external-review rounds"; reason "(「准」)" (db238dbb)

ok | rule: "When the Captain chooses differently from the recommendation, FO writes `Override: …`" | evidence: all three ledger rows show `"override": null`; D1 to D3 were approved as recommended

ok | rule: "`Precedent: ADR <number> — 「<that ADR's Words line>」`" (FO steps: review findings) | evidence: "Precedent: ADR 0013 — 「不等 Copilot，也要修復它額度不足時的應對方式」" (933d6b93). It matches the Words line in `docs/adr/0013-…` at origin/main 544d1743. It is not an always-asked kind.

ok | rule: "FO counts rounds and records the count in the committed gate summary" (step 5) | evidence: "External rounds: Codex 1 (review:5502750442) … 4 (review:5503441596)" (933d6b93)

ok | rule: "From round 3 a finding that is neither … FO declines it in the committed gate summary, naming the finding, and files it as a new backlog task" (step 5) | evidence: "FO declines at candidate 4072363b, filed in backlog task learn-delivery-round3-followups: Codex P2, no-check rule holds only on BLOCKED …". The task file exists with both P2s and the reasons (b4f60788). The cycle 3 Polish was declined in `### Feedback Cycles` and restated in the committed summary.

ok | rule: "FO records `second reviewer: <name> because <trigger>`"; "A listed extension that cannot run is reported as `<name> not run: <reason>`" (Extensions) | evidence: "Second reviewer: copilot because the change adds checks before the merge ask (merge rules). copilot not run: Copilot refused for quota …" (933d6b93). It differs from the quoted form only in the capital S.

ok | rule: "Before the gate, FO runs the stage's minimal acceptance script exactly as written in a fresh shell"; "FO confirms the PR head equals the candidate the latest passing validation report names" (validation; Delivery authority) | evidence: "FO ran its six acceptance steps as written in env -i bash: every step matched" (933d6b93); question names head 4072363b, equal to the "PASSED for 4072363bc134…" report

ok | rule: "Where RULES list `peers` … no Captain ruling … quotes a peer's words" (Extensions: peers) | evidence: all three rulings quote only 「開」 and 「准」 as the Captain's own words; no peer quote is present

violation | rule: "A follow-up message to a worker FO resumes is a dispatch too, and its record carries the same parts"; "Every worker dispatch FO builds carries that absolute path as a `Package root:` line" (Stages) | evidence: `dispatch/implementation-3.md`, `-5.md` and `-7.md` have no `Package root:` line, and their checklist reads "Same checklist as implementation-2." / "-4" / "-6" (1536417d, d0ca7a78, 87d5923e)

observed | rule: `Reviewer:` line under `## FO alignment` (Stages) | evidence: absent. `## FO alignment` holds only "Alignment: not needed … Surfaces: none". The task has `Surfaces: none`, ideation ran on sonnet, and validation was repaired three times after PASSED (Feedback Cycles, cycles 1 to 3). This is a record, not a requirement.

can't tell | rule: "FO runs `design_surfaces.py check --seed <task>` and holds the gate until it exits 0" (backlog) | evidence: absent from state. The backlog briefing summary does not mention it. The ideation-gate check is recorded: "design_surfaces.py check presentable". The seed run would be in chat.

can't tell | rule: "presents every step in full beside its observed output"; "Before recommending delivery, FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: the gate summary condenses the results ("16 section lines … 14 tests OK … 4 files 503+/7-"). The words "sufficiency" and "necessity" are absent from the task file and the briefing. The gate presentation was in chat.

can't tell | rule: "present the exact candidate and PR body before authorized push/create"; "FO adds each PR it opens or pushes to with `pr_watch.py add`" (Delivery authority) | evidence: absent. `implementation-1.md` told the worker "One Draft PR … Open as Draft", and the ledger has no push or create grant row. The PR body, any chat authority and the watch list are outside state.

Coverage: I read in full the three ledger rows, the three briefings, all 12 dispatch records, the task frontmatter, the Feedback Cycles section and the followups task. I sampled the stage reports for FO-authored lines only, and sampled the FO-written diffs of the `state: update` commits. No window commit touches another task's files. I did not read the Captain's chat quotes in "Captain's words" because chat is outside state. I could not evaluate `package_version.py` before each dispatch, `@codex review` after each repair push, or readiness and merge steps. The merge sentinel, the learn extension's archive step and `Asked:` and amendment rules are outside the window; no amendment exists. The dispatch records name package 0.21.0 and the README marker is 0.21.0. Run with the 0.22.0 observer skill, `package_version.py` reports the README as behind 0.22.0.
