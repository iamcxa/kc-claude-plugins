# Observer report: counts-name-the-run-that-produced-them

Window: 6d31cbe9c (task file added, 2026-11-04) .. a7c35bddf (state HEAD, 2026-11-10T10:29:20+08:00). Package 0.36.0. Delivery: iamcxa/kc-claude-plugins#822, ask head 4a146449de8a.

## Findings

violation | rule: "Record `title`, `status`, `variant: kc-dev-flow-2`, and the user's selected `profile`" and "Before admission and dispatch, FO holds unknown/mismatched profiles" (Schema); "FO records the choice" (`backlog`) | evidence: frontmatter has no `profile:` at 6723bb19a, e470f6dd0 (ideation dispatch), 0cf8b8c69 and bac14ff0b (implementation dispatch); `+profile: pilot` first appears in 7f074045c (2026-11-10 08:31:06) (git log -S'profile: pilot')

violation | rule: "Before an implementation dispatch, FO runs ... `number_guards.py reserve --kind migration|adr` ... when the implementation dispatch is built and not earlier ... FO records each printed ... line under `## Number guards` in the task and repeats the lines as dispatch scope notes." (FO steps: number guards) | evidence: dispatch/implementation-1.md (bac14ff0b, 2026-11-09 23:37:14) has no `ADR:` line although the approved design names an ADR; `## Number guards` / `ADR: 0072` was added in 4d870b4d4 (23:42:47); implementation report 1: "this entity has no ## Number guards / ADR: reservation ... HOLD" (4fb8ddd53)

violation | rule: "Keep `Model:` and add this header to the normal dispatch record ... `Roster: source=repository; role=...`" (references/model-roster.md, Adoption and introducing sync); "Stage workers follow `<package>/references/model-roster.md`" (Stages) | evidence: dispatch/implementation-1.md "Model: Codex" and dispatch/validation-1.md "Model: sonnet" carry no `Roster:` line, while ideation-1.md, implementation-2.md and validation-2.md do; .dev2/model-roster.json at e7c9381f2 lists validation as gpt-6-astra, and the `Reviewer:` line calls validation-1 "Astra" (bac14ff0b, 0b2f8c1c9). `dispatch_records.py` still prints "7 dispatch record(s) complete"

violation | rule: "A ruling settled at a gate, in a worker report, or mid-stage feedback — a rule about the product, a constraint, or a direction later work must respect — is landed as an ADR before the next gate is presented, at latest by the terminal approval." (FO steps: decision records) | evidence: Amendment 2 (553f285c3) rules a number after Cycle/Round/Batch/Step/Stage/Amendment/Attempt/Phase is an identifier, not a count; ADR 0072 at c5f2bf9f4 has no match for cycle, sequence, identifier or Amendment 2 (git show c5f2bf9f4:docs/adr/0072-...md | grep -i), and implementation-4 records "task amendment 2 is the correction's ruling home". Whether this ruling governs only this task is the owner's reading

violation | rule: "Each number or factual claim in a gate summary or PR body names the command that produced it and the date, or the report it repeats as `<whose> report, not run`" (Captain steps) | evidence: validation briefing summary (bc888c1f5) "External round sources: Codex reviewed 4a146449d (PR comments read by FO 2026-11-10)." names no command; "(validation-2 report, Astra, 2026-11-10, PASSED at 4a146449d)" names a report and date without "not run"; "RoboRev: clean ... (FO run 2026-11-10)" names no command

can't tell | rule: "his approval of a recommendation FO revised after pushback, also owe[s] one [Override:], on the task they concern. Otherwise the reason carries `Recommendation: followed`." (FO steps: review findings) | evidence: design D1 (a0c989fed, ideation) recommended holding the summary on the line; the ideation question's item (4) recommended the tool write it ("工人原案是擋到我抄上那一行"); the reason says "Recommendation: followed" and ledger `override: null` (01853df49). Whether FO revised its recommendation after pushback is in chat

can't tell | rule: "FO may correct design prose/Mermaid to reflect established decisions under an actual Captain grant covering that task's exact design section" (`ideation`); "FO adds no words of its own and does not move or rewrite a criterion" (Captain amendments) | evidence: 10a85c024 (2026-11-09 13:21, after the ideation report b92e76a68, before the briefing 0cf8b8c69) edits Design prose and D1 with no ideation message record; 3589cc6cb (2026-11-10 08:32:42) rewrites AC-7 and AC-8, and dispatch/validation-1.md says "FO restored two AC-7/AC-8 sentences". Commit authors are all "Kent", so state does not show who wrote either, nor a grant

can't tell | rule: "`Asked:` ... the question or proposal he answered, verbatim" (Captain amendments) | evidence: Amendment 2 `Asked: 「#822（數字寫明出處）驗證發現一個要你決定的誤擋...」` (553f285c3) has no bound briefing or other record in state; the dialog is outside state

ok | rule: "FO appends one entry per amendment to the task's `## Captain amendments` section ... Captain: 「<his words, verbatim>」 ... Asked: ..." (Captain amendments), Amendment 1 | evidence: a0c989fed (14:49:57) follows the ideation gate record 01853df49 (14:49:23); its `Asked:` equals the ideation briefing question character for character; its `Design:` paragraph is found in the Design section; AC-2 and AC-3 appear verbatim under `Superseded text:`

ok | rule: "A Captain ruling is his reply to the question it settles, given after that question was put." (FO steps: review findings) | evidence: backlog (e97bda2c8) reason `answering 「決定：第 18 批這四張（驗證回答 Captain 能不能合併...` matches question `決定：第 18 批這四張（驗證回答 Captain 能不能合併...`; ideation (01853df49) `決定：第 18 批四張設計照下列建議進實作嗎？...` matches; validation (a7c35bddf) `決定：合併 #822（學習提案引用資料裡找不到的數字就擋下...` matches; `quotes_bound_question` True for all three

ok | rule: "His plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: ideation question ends "核准即接受上列每一項建議，包括 (4) 改成工具自己寫" (0cf8b8c69); backlog question "核准即接受四張任務檔現在寫下的內容"

ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check --seed <task>`" (`backlog`) | evidence: replay at 4919046182a9 (backlog briefing uri), exit 0, "counts-name-the-run-that-produced-them.md: seed fields and FO alignment recorded"

ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (`ideation`) | evidence: replay at a53bdd88ea00 (ideation briefing uri), exit 0, "design surfaces presentable"

ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" | evidence: merge/ask-1.json time "2026-11-10T01:54:14Z", head "4a146449de8ad43f1eb67e59599215989c327645"; the validation briefing bc888c1f5 was added 2026-11-10T09:54:17+08:00 (01:54:17Z)

ok | rule: "Before recommending delivery, FO confirms both goal sufficiency and minimal necessity from the same candidate's existing route evidence." (`validation`) | evidence: ask-1.json `sufficiency`: "learn's complete refuses an add entry whose Evidence count appears in none of its referenced items..." and `necessity`: "only ADR 0072, kc-dev-flow-2/scripts/count_tokens.py, delivery_gate.py, learning.py..."

ok | rule: "FO runs the stage's minimal acceptance script under Captain steps, names its record on the summary's `Captain steps:` line" (`validation`) | evidence: captain-steps/1.md Step 1 "Ran: env -i bash --noprofile --norc ... 2026-11-10T01:52:59Z, exit 0"; summary names that path; `delivery_gate.py steps` exit 0 "captain steps complete: 2 steps, 2 left to him" (93e111e8c)

ok | rule: "FO records `second reviewer: <name> because <trigger>` or `second reviewer: not triggered` in the gate summary" (Extensions) | evidence: "Second reviewer: Copilot because the PR changes merge rules." and "copilot not run: ..." (bc888c1f5)

ok | rule: "FO's delivery gate question says approval also covers later external-review rounds on the same PR ... and removing its clean, pushed worktree" (Delivery authority) | evidence: "Regular merge with --match-head-commit 4a146449de8ad43f1eb67e59599215989c327645, ... removing its clean, pushed worktree. Approval also covers later external-review rounds on this PR, unless he says he merges or holds." (bc888c1f5)

ok | rule: no Captain ruling quotes a peer's words (Extensions lists `peers`) | evidence: all three rulings and both amendments cite "host question dialog"; none quotes a peer (a7c35bddf, 01853df49, e97bda2c8, 553f285c3)

ok | rule: "merging the full head `<package>/scripts/delivery_gate.py check` passes, with `--match-head-commit` set to it" (Delivery authority) | evidence: "carried: 26 of 41" (gh pr list, state refs)

observed | `Reviewer:` line under `## FO alignment` | evidence: "Reviewer: kc-dev-flow-2:engineering-reviewer not run 2026-11-10: amendment 1 is the Captain's own ideation-gate approval..." (e3d7e3792). No `db` surface, ideation not dispatched stronger, validation sent back once

observed | `role_triggers.py` `next:` lines | evidence: "role triggers: 1 event(s) read at HEAD, each with a call or a waiver." (no `next:` line, exit 0)

observed | release PRs carry no task ask | evidence: "release: #768 #783" (gh pr list)

observed | sync PRs carry no task ask | evidence: "sync: #781 #813" (gh pr list)

observed | learning PRs carry no task ask | evidence: "learning: #782" (gh pr list)

can't tell | rule: "merging the full head" (Delivery authority) | evidence: "no ask record: #762 head 9530369cb452 merged 2026-11-05T02:41:10Z (no task in readable state)" (gh pr list, state refs)

can't tell | rule: "merging the full head" (Delivery authority) | evidence: "no ask record: #774 head b026e0d7e497 merged 2026-11-04T08:58:44Z (no task in readable state)" (gh pr list, state refs)

can't tell | rule: "merging the full head" (Delivery authority) | evidence: "no ask record: #778 head 005afcaeb68c merged 2026-11-05T08:45:11Z (no task in readable state)" (gh pr list, state refs)

can't tell | rule: "merging the full head" (Delivery authority) | evidence: "no ask record: #784 head b2d0abd778d0 merged 2026-11-05T09:00:02Z (no task in readable state)" (gh pr list, state refs)

can't tell | rule: "merging the full head" (Delivery authority) | evidence: "no ask record: #785 head 0c38dd60b562 merged 2026-11-05T15:03:18Z (no task in readable state)" (gh pr list, state refs)

can't tell | rule: "merging the full head" (Delivery authority) | evidence: "no ask record: #789 head c37417313a12 merged 2026-11-05T15:31:50Z (no task in readable state)" (gh pr list, state refs)

can't tell | rule: "merging the full head" (Delivery authority) | evidence: "no ask record: #792 head 87b60b466acc merged 2026-11-06T03:41:19Z (no task in readable state)" (gh pr list, state refs)

can't tell | rule: "merging the full head" (Delivery authority) | evidence: "no ask record: #795 head 80515bcdd105 merged 2026-11-06T06:30:55Z (no task in readable state)" (gh pr list, state refs)

can't tell | rule: "merging the full head" (Delivery authority) | evidence: "no ask record: #796 head e7bdee42bf56 merged 2026-11-06T14:27:19Z (no task in readable state)" (gh pr list, state refs)

can't tell | rule: "merging the full head" (Delivery authority) | evidence: "no ask record: #798 head 74cde7e09fb6 merged 2026-11-07T01:39:57Z (no task in readable state)" (gh pr list, state refs)

## Coverage

Read fully: the task file at HEAD (frontmatter, Scope, Design, ACs, Captain amendments, stage reports), all seven dispatch records, review/*/briefing-1/index.json, merge/ask-1.json, captain-steps/1.md, README sections Schema through Extensions, the diffs of every task-file commit in the window that is not a report/evidence commit, and the ledger rows for this task. Sampled: evidence folders under validation/ (names, commit times, validation-1 cycle-record.json grep), not read line by line. Not judged: product content, worker reports, design quality.

`merge_audit.py . counts-name-the-run-that-produced-them --from 6d31cbe9c --rev HEAD` saved exit status: 1 (no stderr, no fetch warning; `head differs:` empty, `already reported:` empty). Missing ask records may mean a chat approval or state outside this repository; the window also spans PRs of other tasks.

Chat-only rules from the skill's list were not reported. Rules left `can't tell` name their missing evidence above (chat for the Override and Amendment 2 `Asked:` rows; commit authorship, which is "Kent" for every state commit, for the design and AC edits).
