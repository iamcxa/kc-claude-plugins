# Observer report: decline-becomes-task-only-with-a-bite

Window: FROM edb33f3cf (added the task file) to TO 0e7ef6defe02 (state HEAD). Package kc-dev-flow-2 0.35.0. RULES: adopted `docs/dev2/README.md` (extensions: roborev, codex, copilot, learn, peers, paseo, fo-feedback). Task status at TO: validation, approved-awaiting-merge; PR iamcxa/kc-claude-plugins#800.

## Findings

violation | rule: "Each number or factual claim in a gate summary or PR body names the command that produced it and the date, or the report it repeats as `<whose> report, not run`, and is not stated as settled." (README, Captain steps) | evidence: validation briefing summary "Limit: kc-dev-flow-2/scripts/test_sd_dispatch.py builds the ADR 0047 path in two parts to pass an adr_lint false positive; the lint defect is the backlog task adr-lint-tells-supersession-assertion-from-pointer." names no command, date or report; the neighbouring "Limit: one mutation run read record C differently from the other (validation-1 report)" names a report without a date (0a47ccb61, review/validation/briefing-1/index.json)

ok | rule: "A Captain ruling is his reply to the question it settles, given after that question was put." (README, FO steps: review findings) | evidence: decision_ledger rows for the task: backlog, ideation and validation each by person:captain with reason "The Captain chose 「核准（建議）」 … answering 「<question>」", and each row's `question` equals the question in `review/<stage>/briefing-1/index.json` (c0469dc23, 03323925a, fd864d251); Amendment 1 `Captain: 「補一筆案例再跑（建議）」 (host question dialog, 2026-11-07)` with an `Asked:` line (db9d4e197)

ok | rule: "His plain approval accepts that recommendation only when the gate question says so" (README, FO steps: review findings) | evidence: backlog question "核准即接受「婉拒只在出過事時開任務」任務裡寫的標準"; ideation "核准即接受 D1（另開新 ADR 取代 ADR 0010）與 D2"; validation "Approving accepts that ADR 0064 supersedes ADR 0010." (ledger, same commits)

ok | rule: "When the Captain chooses differently from the recommendation, FO writes `Override: recommended <option>; Captain chose <option>; area: <area>`" (README, FO steps: review findings) | evidence: all three resolutions chose the option marked 建議 and end "Recommendation: followed."; ledger `override: null`; absent and none owed (fd864d251)

ok | rule: "no Captain ruling in the task quotes a peer's words, or a peer's report of the Captain, in place of his own" (observer check, `peers` listed under `extensions:`) | evidence: every ruling quotes his dialog choice; none cites a peer ("The Captain chose 「合併（建議）」 (host question dialog, 2026-11-07)", fd864d251)

ok | rule: "FO appends one entry per amendment to the task's `## Captain amendments` section and changes nothing else in it. FO adds no words of its own" (README, Captain amendments) | evidence: "### Amendment 1 — 2026-11-07, chat / Captain: … / Asked: … / Supersedes: AC-4"; first write "Supersedes: AC-4 (its falsifier sentence)" (db9d4e197) was corrected to "Supersedes: AC-4" two minutes later (09b54c912); AC-4 moved verbatim under "Superseded text:" and replaced by "**AC-7**: Amended by Captain, amendment 1" (fa5ca727c)

ok | rule: "FO names the amendment in the next dispatch's checklist." (README, Captain amendments) | evidence: "1. Apply Captain amendment 1 in the task file …" (dispatch/implementation-1-message-5.md, e5ada82b4, 30 seconds after db9d4e197's follow-up commits); `dispatch_records.py --names` on all records exits 0

can't tell | rule: "`Asked:` is required when his words do not name what they settle … <the question or proposal he answered, verbatim, or the commit holding it>" (README, Captain amendments) | evidence: Asked line ends "Option chosen: 「補一筆案例再跑（建議）」 — 「在反證裡加一筆『只有重複出現、沒有傷害』的案例…」"; whether that option description is the dialog's own text is in the host question dialog, outside state (db9d4e197)

can't tell | rule: "A Captain ruling quotes his words" for chat-sourced scope lines (README, FO steps: review findings) | evidence: "Source: the Captain 「可以，但是該怎樣紀錄合理的followup」 (chat, 2026-11-05), answering 「…」" and "Batch 16: the Captain 「可以，就這樣」 (chat, 2026-11-06), answering 「這批做 2、3、4、5、9 這 5 張，可以嗎？」"; the chat is outside state (edb33f3cf, a1e4f4dc4)

ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check --seed <task>`" (README, backlog, Seed check) | evidence: replay on the copy at the backlog briefing sha 9ffc665bb, exit 0: "decline-becomes-task-only-with-a-bite.md: seed fields and FO alignment recorded" (c0469dc23 briefing)

ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (README, ideation, Gate content) | evidence: replay on the copy plus `<TASK>/` at the ideation briefing sha ff5932e96, exit 0: "design surfaces presentable" (2394b7eef briefing)

ok | rule: "On the five-stage route, FO also records a `Surfaces:` line … and next to it a `Visible change:` line" (README, backlog) | evidence: "Surfaces: none / Visible change: none / Release review: not needed: workflow maintenance, on no journey map." (edb33f3cf)

ok | rule: "When `## FO alignment` records alignment as needed, FO records the alignment result as a `Result:` line before dispatching the worker." (README, ideation) | evidence: "Result: aligned at backlog: Batch 16 backlog gate …" committed 22:29:17 (72af3affe); dispatch/ideation-1.md first committed 22:29:58 (79af09021)

ok | rule: "FO records each printed `Migration: NNNN` / `ADR: NNNN` line under `## Number guards` in the task and repeats the lines as dispatch scope notes." (README, FO steps: number guards) | evidence: "## Number guards / ADR: 0064" committed 00:12:08 (0821f2e42) before the dispatch commit 00:12:12 (ce4f1ef54); "Number guards: ADR: 0064" in implementation-1.md and validation-1.md

ok | rule: "FO runs `python3 <package>/scripts/dispatch_records.py <task folder>` before committing" and "`--coverage <task> --stage <stage>`" (README, Stages) | evidence: replay at TO: "10 dispatch record(s) complete"; coverage "dispatch coverage complete: ideation / implementation / validation"; every follow-up record carries a `Symptom:` header and its checklist

ok | rule: "A ruling settled at a gate … is landed as an ADR before the next gate is presented, at latest by the terminal approval." (README, FO steps: decision records) | evidence: ask-1.json points "path: 'docs/adr/0064-a-round-three-declined-finding-becomes-a-backlog-task-only-with-a-'" and "docs/adr/0010-…" at the validation briefing (98b6d5e1c)

ok | rule: "FO may explicitly decline evidenced Deferred risk or Polish in the existing committed gate summary, naming the finding, reason, candidate revision and the lines or evidence it rests on." (README, FO steps: review findings, step 2) | evidence: "Declined: Polish, validation-1 F1 the PR body listed the superseded AC-4 falsifier as open (FO replaced that paragraph in the PR body on 2026-11-07; no candidate change)." and "Declined: Polish, validation-1 F2 the candidate observer wrote a draft violation label and withdrew it in the same report (its final verdict is the one judged; raw report kept unedited)."; thin on evidence, the head ae7750375 is in the same question and summary but not on these lines (0a47ccb61)

ok | rule: "A merge ask names each listed reviewer that was not read, and the Captain decides." (README, Extensions) | evidence: "copilot not run: \"Copilot was unable to review this pull request because the user who requested the review has insufficient remaining quot\"; answer=review:5809308135 / Copilot retry: available when the Captain confirms quota is back."; `review/copilot-not-run.txt` holds the same quote and id (0a47ccb61)

ok | rule: "FO records `second reviewer: <name> because <trigger>` or `second reviewer: not triggered` in the gate summary" (README, Extensions) | evidence: "Second reviewer: Copilot because the PR changes review rules." (0a47ccb61)

can't tell | rule: "FO counts rounds and records the count in the committed gate summary." (README, FO steps: review findings, step 5) with "FO counts one round per `evidence=` id it prints" (codex EXTENSION.md) | evidence: "External rounds: 1." and "Codex reviewed ae7750375 (PR comments read by FO 2026-11-07)" carry no `evidence=` id; whether the RoboRev run "evidence=roborev:1576 (FO run 2026-11-06)" was posted on the PR (an external round) or local (not one) is outside state; codex_review.py output is not recorded (0a47ccb61)

ok | rule: "FO's delivery gate question says approval also covers later external-review rounds on the same PR, merging the full head `<package>/scripts/delivery_gate.py check` passes, with `--match-head-commit` set to it, unless he says he merges or holds, and removing its clean, pushed worktree." (README, Delivery authority) | evidence: "Regular merge with --match-head-commit ae7750375bc19e482f829edc9a041d95fb280693, the batch 16 validation sitting, and removing its clean, pushed worktree. … Approval also covers later external-review rounds on this PR, unless he says he merges or holds." (0a47ccb61)

can't tell | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (README, Delivery authority) | evidence: `merge/ask-1.json` is the only file for head ae7750375; its time "2026-11-07T01:52:57Z" is after the briefing commit 0a47ccb61 (2026-11-07T09:52:11+08:00 = 01:52:11Z), so it cannot show a check before presenting

ok | rule: "FO confirms both goal sufficiency and minimal necessity" (README, validation, Gate content) | evidence: ask-1.json sufficiency "with the new step 5 a repeat-only declined finding requires a backlog task in 2/2 Sonnet readings and in 0/2 with the bite clause deleted, and the observer judges the archived round-3 decline a violat"; necessity "the four files are ADR 0010, the new ADR 0064, workflow.md and test_sd_dispatch.py (gh pr view 800 --json files, FO 2026-11-07)." (98b6d5e1c)

can't tell | rule: "Before the validation `gate prepare`, FO runs `python3 <package>/scripts/delivery_gate.py question …`; nonzero holds preparation." (README, Delivery authority) | evidence: absent in state; a replay of `question` on the committed briefing question and summary prints "gate text complete", exit 0, so it would have passed (0a47ccb61)

ok | rule: "FO runs the stage's minimal acceptance script under Captain steps, names its record on the summary's `Captain steps:` line" (README, validation, Gate content; Captain steps) | evidence: `captain-steps/1.md` "Ran: env -i bash --noprofile --norc … 2026-11-07T01:51:31Z, exit 0"; replay `delivery_gate.py steps` prints "captain steps complete: 1 steps, 1 left to him"; summary line "Captain steps: …/captain-steps/1.md" (0a47ccb61)

can't tell | rule: "returns an output that differs from the script through feedback" (README, validation, Gate content) | evidence: `captain-steps/1.md` "an earlier run at 01:51:22Z with macOS Python 3.9.6 first on PATH exited 1 on tarfile extractall(filter=)"; the recorded passing run changed PATH to Homebrew Python 3.15, no feedback return exists; which python3 the Captain's shell resolves is outside state

ok | rule: "At each next gate, wait for every member's sufficient committed evidence, then present the batch in one sitting." (README, Batch gates) | evidence: the five batch 16 tasks have validation briefings committed 00:49 to 10:01 and their validation approvals recorded 10:04:21 to 10:04:35 (f12c5cca2, d62d8781e, fd864d251, 9f0a2e7fa, 0e7ef6def)

can't tell | rule: "present the exact candidate and PR body before authorized push/create" (README, Delivery authority) | evidence: `pr: iamcxa/kc-claude-plugins#800` set at 00:41:35 with no gate record or amendment naming a push or PR grant; dispatch says "FO owns those steps"; any grant or body presentation was in chat (d67775504)

can't tell | rule: "FO runs `python3 <package>/scripts/number_guards.py check … on the PR head before FO asks for merge`" (README, Number guards) | evidence: absent; only the worker's `number-guards.log` (exit 0) exists

can't tell | rule: "FO may correct design prose/Mermaid to reflect established decisions under an actual Captain grant covering that task's exact design section" (README, ideation, Gate content) | evidence: commit f78d6992f "ideation: … names the ADR's protected path" changed one line of `### Change` after the ideation report; every state commit has the same author, and no dispatch record names a request, so who wrote it is outside state

observed | rule: "Record chief-engineer and engineering-reviewer calls under `## FO alignment` as `Reviewer: <agent> <model> <date> — <question>`" (README, Stages) | evidence: "Reviewer: kc-dev-flow-2:engineering-reviewer not run 2026-11-07: Amendment 1 replaces only AC-4's falsifier record …" (2eea9bdae); ideation ran on claude-opus-5-5, no `db` surface, validation not sent back

## Counts

violation 1, can't tell 9, ok 17, observed 1 (the three findings with `ok` and a "thin" note stay `ok`).

## Coverage

Read fully: the task file history over the window (`git log -p` of `<TASK>.md`, 28 commits), the three briefings, `merge/ask-1.json`, `review/copilot-not-run.txt`, all ten dispatch records, `captain-steps/1.md`, the ledger rows for the task, the README at STATE's checkout, and the codex, copilot and roborev `EXTENSION.md`. Sampled: nothing in the stage reports was judged (worker output). Replays run: both design checks (copies under /tmp, removed), `dispatch_records.py` folder and `--coverage` modes, `delivery_gate.py steps` and `question`, `role_triggers.py STATE TASK --rev TO` (printed no `next:` line). Not evaluated: the chat-only rules; PR body and PR state (outside state); `learn` sentinel and merge rules (not yet applied in the window); the step 5 round-3 decline rule did not apply (external rounds: 1).
