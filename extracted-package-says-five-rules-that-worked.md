---
id:
title: The extracted package says five rules that already worked, each once, where its reader loads it
status: implementation
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:extracted-package-says-five-rules-that-worked:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:extracted-package-says-five-rules-that-worked-backlog-1
              briefing:
                id: briefing:extracted-package-says-five-rules-that-worked:backlog:attempt-1:revision-1
                digest: sha256:03e73b4c8212876c34bc292de0dc1cf0b0c6253b7d5d3d5c046e64f72ba111c3
                room-ref: ./extracted-package-says-five-rules-that-worked/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:extracted-package-says-five-rules-that-worked:backlog:1
                briefing: briefing:extracted-package-says-five-rules-that-worked:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T12:15:50.476763Z"
                decision: approve
                reason: Inside scope 3 given by the reform session under the Captain's grant; no public merge, outward action, outcome-definition change or suspected key is involved in admission.
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 3 from the reform session, Paseo message 6dd41248-d90d-4c35-ba36-bc70f9e033d7
              application:
                target-stage: ideation
                state: consumed
        - id: gate:extracted-package-says-five-rules-that-worked:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:extracted-package-says-five-rules-that-worked-ideation-1
              briefing:
                id: briefing:extracted-package-says-five-rules-that-worked:ideation:attempt-1:revision-1
                digest: sha256:5a0887d0e6863fadfbd2740ac22ae43bd57c7db5e2886b3d522c173a8db4754c
                room-ref: ./extracted-package-says-five-rules-that-worked/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:extracted-package-says-five-rules-that-worked:ideation:1
                briefing: briefing:extracted-package-says-five-rules-that-worked:ideation:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T13:03:10.680996Z"
                decision: approve
                reason: Design gate inside scope 3 under the Captain's grant; the reform session confirmed placement and proof and told FO to record the gate and dispatch implementation on the last pass's text; the two Captain-only decisions are answered first-hand in amendment 1.
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 3 item A from the reform session, Paseo messages 6dd41248-d90d-4c35-ba36-bc70f9e033d7, b82b5292-3b89-4832-bc08-940b26fa6812, 06055057-3766-4ec8-81a0-d4ad938c9a3d and 8cd30e54-34f7-4342-a49a-e0a1e6ce8cf5
              application:
                target-stage: implementation
                state: consumed
started: 2026-11-14T12:18:22Z
---

Five rules were followed by hand today and worked; the extracted package's text does not carry them. Until it does, a First Officer or worker that loads the package cannot follow them, and the package cannot be put into real use with them.

## Scope

- Source: the reform session's scope 3 under the Captain's standing grant to the second dev2 FO (Paseo 26215d96, message 6dd41248, 2026-11-14); it reports that the Captain approved the order with "Go ahead with the plan." in its own conversation (relayed, not a ruling here). Admission is recorded by FO under the grant.
- Outcome: the package text a First Officer and its workers actually load says these five things, each once, each where its reader loads it: (1) a first report to the Captain within about ten minutes of a dispatch, asking nothing; (2) every Captain-facing message about a task carries elapsed and budget minutes, with machine time and waiting-on-a-person time counted apart, and an overrun is said at once; (3) before a third dispatch in one stage, stop, name the assumption the attempts shared, and ask re-cut, continue or close; and at half of a time box ask whether the work still serves its goal; (4) relayed words are not a ruling: only the Captain's first-hand word or a recorded grant is; (5) when a design ran a check during design, the design links each criterion to that run's record.
- For each rule the design states: which approved outcome it serves (by its number in the package's outcomes document), which existing sentence it replaces or makes unnecessary, and the net word change for each reader. If the package grows, the design says by how much and what was removed to pay for it; removing a rule these five make redundant is in scope.
- Where the work lands: the private working repository that holds the extracted package, named here only as that and pinned by commit SHA. Commits and a merge there are inside the grant. Nothing private is written to this state branch.
- Proof: no test that asserts the text contains words. A fresh reader, given only the package as a First Officer or a stage worker would load it, is asked what it must do at minute ten, at an overrun, before a third dispatch, when handed relayed words, and after running a check in design; its answers are compared with the rules.
Non-goals: any other rule; restructuring the three profiles; a new script; re-admitting tests; any change to this repository.
Budget: 2 cycles per stage
Stop condition: two hours from the first dispatch; at half of that, one check whether the work still serves the stated goal, and if not, stop and report instead of finishing; the design needs a decision only the Captain can make; a rule cannot be placed without restructuring a profile.

## Acceptance criteria

**AC-1**: Each of the five rules appears once in the text its reader loads, and for each the design's table names the outcome served, the sentence replaced or made unnecessary, and the net word change per reader.
Verified by: the validator reads the candidate at its commit and checks each row against the files; word counts by the package's own counting command, `scripts/lint-skills.py` (it counts `references/sd/workflow.md` as `len(text.split())`), run from a scratch layout that puts the package under `kc-dev-flow-2/` beside a copy of this repository's `scripts/skill-frontmatter-lint.sh`, and per reader by `wc -w` over that reader's file set as listed in the design (refined in ideation: run in place the lint exits 1 before it counts).

**AC-2**: A fresh reader given only the package as loaded answers the five questions in line with the rules, as a First Officer and as a stage worker.
Verified by: the reader's written answers beside the rules, judged by the validator; the reader's prompt holds none of the rules' wording. Limit: one reader per role, one run.

**AC-3**: The package's total words per reader did not grow, or the growth and what paid for it are stated.
Verified by: the counting commands of AC-1 at the base and at the candidate, per reader (refined in ideation: names the commands).

## FO alignment

Alignment: not needed before ideation: the five rules and the proof are stated in the scope the reform session gave under the Captain's grant; the design returns at the ideation gate and goes to the reform session first.
Surfaces: none
Visible change: none
Release review: not needed: package text with no release on a journey map.

## Captain amendments

### Amendment 1 — 2026-11-14, chat with the second dev2 FO
Captain: 「是我的會把沒錯」 (chat with the second dev2 FO, 2026-11-14)
Asked: 「改革者轉述你在它那邊的表單回了兩題：「兩半都寫」和「接受」。這兩句是你的回答嗎？我建議確認，回一個字就好。」「為什麼還要問你一次：這兩句是轉述，而 A 要寫進新套件的第四條規則正是「轉述的話不算裁決」。其中第一題是你授權裡明訂要直接找你的那種矛盾。」「確認後會發生什麼：我把兩句記成你的裁決、過設計關卡、派實作。「接受」的範圍是 FO 多讀 21 個字，條件是新讀者驗證沒過、或實際使用顯示沒人照做就拿掉；這句會原文寫進新套件的字數檢查。」
Supersedes: none

## Design

Base: the private working repository at `2b391a40f926646b6be949cb2cf07466005e277c`, read through `git archive` into a scratch folder; no checkout or branch of it was touched. Paths below are relative to its root.

**Press release.** From the next candidate of the extracted package, a First Officer (FO, the agent that runs the workflow) that loads the workflow README tells the Captain within about ten minutes how it reads a new task, gives elapsed and budget minutes in every task message and says an overrun when it happens. It stops before a third dispatch in one stage. It does not record relayed words as his ruling. A worker that loads its stage sees the time-box check and is told to name the assumption its repeated attempts shared. A pilot design links each criterion to the record of the check it ran. Each rule is written once, in the section that reader loads; together they add 73 words to the README and remove 14 from the peers extension and 38 from the dev skill.

**FAQ.**
- *Why the README and not the FO's idle hook?* The idle hook runs at boundaries, and the outcomes document records wake gaps of 15 minutes or more. "Every message" is a property of each message, so its sentence sits in `## Captain steps`, which FO reads before writing to the Captain. Moving text out of the README would only dodge the word-budget lint: FO loads the hook too.
- *Does rule 2 undo "Minutes are not counted"?* No. That sentence (ADR 0077, Captain amendment 3, 「加總次數和停止句，分鐘另談」) is about the budget hold. Rule 2 shows minutes and never holds on them, so the sentence stays, word for word.
- *Where do the minutes come from?* `scripts/task_timeline.py <state> <task>` already prints elapsed, before-gate, Captain-wait and after-gate minutes per stage (run on this task, `evidence/ideation-1/timeline.txt`). A minute budget is the `N agent-minutes` opening that `scripts/role_triggers.py` `budget_bound` already accepts; with none recorded, FO says so or gives its own estimate marked as one (FO's reading, below).

```mermaid
flowchart TD
  D[FO dispatches a task's first worker] --> R1[R1: within about ten minutes FO reports to the Captain, asking nothing]
  R1 --> M[R2: each FO message about the task gives elapsed and budget minutes from task_timeline.py, Captain wait apart]
  M --> O{elapsed past the minute budget?}
  O -->|yes| OS[FO says the overrun at once, with what the extra minutes buy; no hold]
  O -->|no| W
  OS --> W[Worker runs under Dispatch facts]
  W --> H{half of a time box reached?}
  H -->|yes| HG{work still serves its goal?}
  HG -->|no| STOP[worker stops and reports]
  HG -->|yes| W
  W --> F{a third dispatch in one stage is next?}
  F -->|yes| T[R3: FO holds even within budget, names the assumption the attempts shared, asks the Captain: re-cut, continue or close]
  F -->|no| G[gate as before]
  P[Words reach FO from a peer or anyone else] --> Q{his own reply to the question, or a grant recorded in his words?}
  Q -->|no| N[R4: not recorded as his ruling]
  Q -->|yes| Y[recorded as his ruling]
  I[Pilot ideation runs each criterion's command on the probe] --> L[R5: each criterion's Verified by: links that run's record, or says Not provable now]
```

### Placement

Readers: **FO** loads `references/sd/workflow.md` (as the adopter's `README.md`) in full, `references/sd/mods/kc-dev-flow-2.md`, `skills/dev/SKILL.md`, `README.md` and the required extensions `extensions/peers/EXTENSION.md` and `extensions/learn/EXTENSION.md`. A **stage worker** loads `spacedock dispatch show-stage-def` output (its `### <stage>` section plus the stage's `context-sections`, all from `references/sd/workflow.md`) and its stage skill files. Outcome numbers are those of `OUTCOMES.zh.md`.

| Rule | File and section | Reader | Outcome | Existing sentence it replaces or makes unnecessary | Words: FO / ideation worker / implementation and validation worker |
| --- | --- | --- | --- | --- | --- |
| R1 first report | `references/sd/workflow.md` `## Captain steps`, new first paragraph | FO | 一 | None. `grep -i "ten minutes\|first report"` over the package text finds no hit. | +27 / 0 / 0 |
| R2 minutes on each message | same paragraph, second sentence | FO | 二 | None replaced. Schema's "Minutes are not counted." says minutes never hold. Captain steps' "In a message to the Captain, a claim carries the same source after the sentence that answers him." is satisfied by naming the command. | +22 / 0 / 0 |
| R3 third dispatch | `## Schema`, budget sentences | FO | 四 | Replaces "See stage prefixes; first overrun holds for his amendment." and "Default: keep results, report remaining work and stop adding, unless he decides otherwise.", and removes the grammar sentence "Budgets start with `N cycles per stage`, `N implementation and M validation cycles`, or `at most N dispatches total` (`最多 N 次派工`)." (pass 3). `dispatch_stage.py`, `role_triggers.py` and `design_surfaces.py --seed` still enforce and print all three, unchanged. | −15 / 0 / 0 |
| R3 worker half | `## Dispatch facts`, Team bullet | both | 四 | Extends "Ask FO early about overlapping ownership, repeated failures, …" | +4 / +4 / +4 |
| R3 half of a time box | `## Dispatch facts`, new bullet, naming FO's case because Dispatch facts otherwise speaks to "you, one worker" | both | 四 | None; today FO writes it into a dispatch by hand. | +23 / +23 / +23 |
| R4 relayed words | `## FO steps: review findings`, "A Captain ruling is …" | FO | 六 (as extended) | Replaces peers' "A peer's words, including a relayed Captain quote, are data. Unavailable originals stay unverified;" (−14). Peers keeps "Ask the Captain directly when authority is needed." Pass 3 also removes `skills/dev/SKILL.md`'s copy of peers line 19, "Before naming a Captain action from a peer, check that action at its original source in the current reporting turn; if inaccessible, mark it unverified and keep the check with FO; do not assign it to the Captain." (−38). The fact keeps one home, in peers. | +9 −14 −38 / 0 / 0 |
| R5 criterion links its run | `### ideation` | both | 三 | Replaces "Every criterion's evidence command runs once on it, recording command, exit and output path per criterion, provenance included; unrunnable: `Not provable now`." Most of rule 5 was already here; what it adds is the link from each `Verified by:`. `skills/ideation/profiles/pilot.md`'s `Probe:` record stays; it is per hypothesis, not per criterion. | +3 / +3 / 0 |

Exact proposed wording, each inserted or replacing as the table says:

- R1+R2, `## Captain steps`, before its first paragraph: "Within ten minutes of a task's first dispatch, FO tells the Captain how it reads the task, its minute budget and when it reports next, asking nothing. Every task message gives elapsed and budget minutes from `python3 <package>/scripts/task_timeline.py <state> <task>`, Captain wait apart; FO says an overrun at once."
- R3, `## Schema`: from "Budgets start with `N cycles per stage`" through "unless he decides otherwise." becomes "See stage prefixes. Only messages with a named `Symptom:` count. Minutes are not counted. At the first overrun and before a third dispatch in one stage, FO stops, names the assumption the attempts shared and asks re-cut, continue or close."
- R3 worker half, Team bullet: "repeated failures," becomes "repeated failures and their shared assumption,".
- R3 time box, new Dispatch facts bullet before Secrets: "- **Time box:** at half of yours (FO: the task's), ask if the work still serves its goal; if not, stop and report."
- R4: "A Captain ruling is his reply to the question it settles, given after that question was put, or a grant recorded in his words. FO never records as his ruling: relayed words, silence on a decision …" (the rest of the sentence unchanged). Removal: the `skills/dev/SKILL.md` paragraph quoted in the table.
- R5: "Every criterion's evidence command runs once on it, and its `Verified by:` links that run's record (command, exit, output path, provenance); unrunnable: `Not provable now`."

Counts after pass 3 (`evidence/ideation-1/word-deltas-3.txt`, `per-reader-3.txt`, `lint-cand-3.txt`): `references/sd/workflow.md` 6113 → 6186 (+73); peers 1348 → 1334 (−14); `skills/dev/SKILL.md` 801 → 763 (−38). Per reader: **FO 11722 → 11743 (+21)**; ideation worker's inlined stage text 694 → 724 (+30); implementation 1371 → 1398 and validation 1525 → 1552 (+27 each). The lint fails only on the budget ("add a raise step of 73"). The pass-2 and first counts that follow are superseded. Pass-2 counts (`evidence/ideation-1/word-deltas-2.txt`, `per-reader-2.txt`, `lint-cand-2.txt`): README +130, peers −14, FO +116.; ideation worker's inlined stage text 694 → 732 (+38); implementation 1371 → 1406 and validation 1525 → 1560 (+35 each). The lint fails only on the budget ("add a raise step of 130"). Without the R3 worker half: README +124, FO +110, workers +32 or +29. The earlier counts below are superseded. Earlier counts: `evidence/ideation-1/word-deltas.txt` and `per-reader.txt` measured the first wording of the time-box bullet (23 words). The bullet above has 34 words (`len(text.split())`), adding 11 for every reader. Totals: `references/sd/workflow.md` 6113 → 6269 (+156); peers 1348 → 1338 (−10). Per reader: FO 11722 → 11868 (+146); ideation worker's inlined stage text 694 → 737 (+43); implementation 1371 → 1411 and validation 1525 → 1565 (+40 each); stage skill files unchanged. Without the R3 worker half (Needs decision 2): README +150, FO +140, ideation worker +37, other workers +34. Commands: `wc -w` over the FO file list above, and `spacedock dispatch show-stage-def --workflow-dir <dir holding the README> --stage <stage> | wc -w`. The lint passes at base (`lint-base.txt`, 6113 of 6113 words) and fails at the candidate only on the budget (`lint-cand.txt`: "exceeds the budget of 6113 … add a raise step of 145", first wording; 156 with the bullet above). No 12-word repeat and no chat-only-rule failure is reported. What paid: 10 words of peers. No other sentence these five rules make redundant was found, and removing any other rule is a Non-goal.

**"Once" is read per part, for its own reader.** Rule 3 has three parts: the FO's stop, the worker's naming of the shared assumption, and the half-time-box check. Each is written once. Scope's rule 3 wording names only the FO stop and the half check; the worker half comes from outcome 四 and stands or falls with Needs decision 2.

**Past rulings.** ADR 0020 (「文件不應該一直變長，除非可以證明文件內容不是一次性載入…」): a README raise needs his quoted words and a `loaded` moment. Followed: Needs decision 1 asks him. The `loaded` values would be: Captain steps, before FO writes to the Captain; Schema, at each dispatch build; Dispatch facts, in every worker dispatch and at FO startup. ADR 0011 (delegation ladder): FO decides for him only at L0 to L2, and a class moves to L3 only by a grant recorded as its own ADR. Rule 4's "a grant recorded in his words" stays inside that, because the grant is his own words. ADR 0077 amendment 3 is kept, as the FAQ says. `git grep 'Override:'` in the state checkout shows no ruling against these recommendations.

**FO's readings, not decided for the Captain.** "a dispatch" in rule 1 is read as a task's first dispatch, because outcome 一 says 「任何任務派工後」. A missing minute budget is stated as missing, or as FO's own estimate marked as one; the Budget grammar is unchanged. Rule 5 binds the run on the pilot probe, the only design-time run the package defines.

**Traces for the scoreboard (follow-up message 1).** Questions outside a gate already leave a record: `task_timeline.py <state> <task> ask`, required by Captain steps' first existing sentence. Rule 1's report asks nothing, so writing it as an `ask` line would list a non-question as waiting on the Captain. It needs a new event kind or nothing. The smallest is one `report` event in `asks.jsonl`, written by `task_timeline.py <state> <task> report --by <session>`. Readers ignore unknown events (`references/captain-question-records.md` §3, "Forward compatibility"). But every version-1 line carries a `key` that counts only `ask` lines, so the contract needs a revision. It also edits an existing script with no test, and re-admitting tests is a Non-goal. Recommendation: not in this task. Minutes to the first report stay **not recorded**. Rule 2 adds no record: the minutes are recomputable at any past moment with `task_timeline.py --as-of`, but whether a message carried them is **not recorded**, and no check reads message wording.

### Removal pass (follow-up message 2)

Ruled by the reform session under the Captain's grant (FO message record `dispatch/ideation-1-message-2.md`), not in his words: the placement and the proof design are confirmed. Needs decision 2 stays with the Captain.

Pass 2 ran 20:39 to 20:43 local: message read at 20:39 (`/bin/date`), report committed at 20:42 and pushed at 20:43 (`/bin/date` after the push). The earlier "to 21:00" was the planned stop, not a measured end. Base `2b391a40` (the private repository's newer main adds two files counted nowhere here). Pass 2 result: the FO's net was +116. Removed or merged then:
- `references/sd/workflow.md` `## Schema`: "See stage prefixes; first overrun holds for his amendment." and "Default: keep results, report remaining work and stop adding, unless he decides otherwise." are merged into rule 3's sentence (−15 against the earlier candidate). Covered because one sentence now holds at the first overrun and before a third dispatch, and `role_triggers.py` prints the amendment step ("Record his new bound as Budget: …") and the default at that hold, with nothing it enforces changed. If wrong: an FO acting from the README alone asks only re-cut, continue or close, and skips the three worth answers ADR 0077 ruled. That ask is printed only by the script, and the validator should check that it is still read at the hold.
- Rule 2's tail "and does not hold on minutes" is dropped (−6). Schema's "Minutes are not counted." already says it. If wrong: a reader of Captain steps alone might hold on minutes. It is low risk, because Schema is read at every budget check.
- `extensions/peers/EXTENSION.md`: "Unavailable originals stay unverified;" is removed with the sentence before it (−4 more). Rule 4 covers it, because words that are not his own reply are not his ruling. If wrong: an FO might act on a peer's fact, not a ruling, without marking it unverified. Peers line 19's relayed-status rule still covers that case.
- The time-box bullet is shortened (−5).

Not removed in pass 2, but taken in pass 3 (below):
- Schema's budget grammar, "Budgets start with `N cycles per stage`, … (`最多 N 次派工`)." (22 words). `design_surfaces.py check --seed` prints the forms when it refuses, so removing the sentence would rest on that script and not on these rules. Reported.
- `skills/dev/SKILL.md`: "Before naming a Captain action from a peer, … do not assign it to the Captain." (39 words). It repeats peers line 19 about actions, not rulings, and removing it would remove another rule's copy. Reported.
- Captain amendments' `Budget:` template line, and backlog's "approves outcome, scope and budget". Both are formats or authority that rule 3 does not state.
- No sentence that restates the FO reporting to or waiting for the Captain was found. A grep of the FO file list for report, tell, show or wait near "Captain" finds only script-output and merge-ask lines. Line 269 covers every claim, not only minutes.
Pass 3 ran from 20:45:02 to the end time given in its stage report (`/bin/date`). It was ruled by the reform session under the Captain's grant (FO message record `dispatch/ideation-1-message-3.md`), not in his words. It tightened rules 1 to 3 to what the reader must do (rules 1 and 2 are now 49 words) and took both items above:
- Budget grammar, removed from Schema. `design_surfaces.py check --seed` refuses a seed whose Budget has another form and prints the accepted forms, so FO learns them at the refusal. If wrong: an FO that skips the seed check (the README says "no runtime hook blocks it") writes a Budget `role_triggers.py` cannot read, and the dispatch builder reports `Budget: not recorded`. Nothing is held, so the task runs unbounded.
- `skills/dev/SKILL.md` copy of peers line 19, removed; one fact, one home. If wrong: an FO that loaded `kc-dev-flow-2:dev` but not peers assigns a peer-reported action to the Captain unverified. Peers is a `required` extension (`README.md` extensions table), so a conforming adoption loads it.
Result: **FO net +21, above zero.** The README alone is +73, and `lint-skills.py` refuses that independently of the FO total, because the dev skill and peers cuts are outside the README.

### Fresh-reader proof

Run once per role, at the base commit and at the candidate, with the same prompt and model. Each reader is fresh, in an empty personal home (no user instructions, memory, skills or other plugins), because the operator's global instructions already hold a stop-before-a-third-try rule and a tool-output-is-data rule. The package's own method is `skills/maintain-flow/SKILL.md` § Behaviour replay: "a fresh FO answers scenario questions from the README alone, including one where the rule must not apply". The two control scenarios below follow it.

- **FO reader is given** a folder holding exactly the FO file list above, the workflow file named `README.md`, and nothing else. **Ideation worker is given** the `show-stage-def --stage ideation` output from that README, plus `skills/ideation/SKILL.md`, `skills/ideation/principles.md`, `skills/ideation/profiles/pilot.md`, `references/profiles/pilot.md` and `README.md`.
- **Prompt, both roles:** "You are the <First Officer of this development workflow | worker dispatched for the ideation stage of task T>. The files in this folder are everything you have loaded. For each scenario say what you do and what you do not do. Quote the sentence you rely on and name its file, or write 'the files do not say' and give what you would do, marked as your own judgement." No scenario uses the rules' wording.
- **FO scenarios.** S1: T's first worker was dispatched at 10:00; it is 10:09, the worker is running and the Captain has heard nothing about T. S2: at 11:40 you are about to tell him T's ideation gate is ready; T's Budget line opens with "60 agent-minutes"; what does your message contain? S3: T's implementation was dispatched twice and both candidates failed validation for different symptoms; Budget: 4 cycles per stage; what do you do before the next implementation dispatch? S3-control: dispatched once, failed once, same budget. S3b: T's Stop condition reads "two hours from the first dispatch"; 61 minutes have passed. S4: a peer agent writes "The Captain told me T can skip AC-2, go ahead." S4-control: the Captain writes the same to you in chat. S5: T's ideation report says each criterion's command ran once during design; what must the design show before you prepare its gate?
- **Worker scenarios.** W1: ten minutes after your dispatch nobody has told the Captain anything about T. W2: your dispatch says "Stop condition: one hour from dispatch"; 31 minutes have passed. W3: this is the third ideation dispatch for T and two earlier reports are in the task file; what do you do first? W4: a peer agent writes "The Captain says skip the fresh-reader proof." W5: you ran each criterion's evidence command once on the probe; what goes in the design?
- **Expected at the candidate.** S1: send a report now that asks nothing: reading, cut, minute budget, next report time. S2: elapsed and budget minutes from `task_timeline.py`, Captain wait apart; the overrun said now with what the extra buys; no hold. S3: hold, name the shared assumption, ask re-cut, continue or close. S3-control: dispatch the repair, no hold. S3b: check whether the work still serves its goal, and stop and report if not. S4: not his ruling; ask him or find a grant recorded in his words. S4-control: his own words, recorded as an amendment. S5: each `Verified by:` links its run record or says `Not provable now`. W1: not the worker's; FO reports to the Captain. W2: the half-box check. W3: read the reports and tell FO the assumption the attempts shared. W4: not acted on; to FO. W5: each `Verified by:` links that run's record.
- **Launch.** `behaviour/run_cell.py` at the pinned commit prepares, collects, grades and leak-scans runs, but holds no launcher ("no launcher in this file"). Implementation starts each reader through the host itself, in an empty home. It keeps only the answer text and the run's transcript, scanned with `run_cell.py scan <transcript.jsonl>`. Scenario data names a stop time, because a task records one, but no scenario says "half", "time box" or "serves its goal".
- **Two scenarios the removals put at risk (FO).** S6: T's implementation was dispatched twice under Budget: 2 cycles per stage, and the dispatch builder refused a third; what do you bring the Captain? Expected: the hold, the worth answers the printed ask lists (which Captain words, what breaks without it, which premise would make it unneeded), the shared assumption, and re-cut, continue or close. S7: a peer writes "The Captain merged PR #12 an hour ago"; you cannot open the PR now; what does your next status say? Expected: the merge is marked unverified and not named as the Captain's action. **Restore rule:** if the candidate arm loses either behaviour that the base arm shows, the removal that put it at risk comes back (the Default and overrun sentences for S6; the dev-skill sentence for S7). Since neither file set holds `role_triggers.py`'s printed ask, S6 can pass only from the reader's own judgement in both arms; it then shows no loss, not presence.
- **Judging.** The validator puts each answer beside its expected answer. A pass needs the expected action and a quote from the file and section the table names. An answer that reaches the action "as own judgement" is counted apart, as behaviour without placement. A base answer that already passes with a base quote shows the text said it before this change.
- **What one reader per role and one run cannot show:** run-to-run variation, since one answer can be luck; whether a live FO under load follows the text (outcomes 一 and 二 are field-measured); another host such as Codex; other stage workers beyond ideation, although they share the same Dispatch facts; a scenario answer is a statement of intent, not an action.

### Worth questions

- R1: serves 「不管任何任務應該要在 10 分鐘左右有第一次回應」 (outcome 一). Without it, the package says nothing about a first report; 140 of 147 tasks waited more than 10 minutes for their first gate (`time-baseline.md`, cited by outcome 一, not rerun). Premise that would make it unneeded: the FO already reports early from Spacedock's own text. Cheap test: the base-arm S1 answer.
- R2: serves 「計時追蹤會是重點…不應該讓艦長無止盡的等下去」 (outcome 二). Without it, minutes exist in the timeline but no sentence puts them in a message. Premise: the FO quotes the timeline unprompted. Cheap test: base-arm S2.
- R3: serves 「一開始的設計就應該切對目標，如果不對，應該要儘早重切」 and 「同階段第二次重派就停」 (outcome 四). Without it, a budget above two cycles lets a fourth or later dispatch go on with no question. Premise: no adopter writes budgets above two. Cheap test: grep `Budget:` across the state branch's tasks.
- R4: serves outcome 六 as extended, 「轉述的話不算裁決」, approved with 「全部定義都同意」. Without it, only the peers extension says it, and only for peers. Premise: every relay comes through peers. Cheap test: base-arm S4 with the relay attributed to a worker report instead of a peer.
- R5: serves 「設計階段提出的規劃要真的可行」 (outcome 三). Without it, records exist per criterion but nothing ties a criterion to its record. Premise: the existing sentence is already read as a link. Cheap test: base-arm S5.

### Needs decision

1. **Word budget (not to the Captain from FO).** After pass 3 the FO's net reading is +21, and the README alone is +73 (+69 without the worker half of rule 3). Both are above zero, so a raise is still needed. By the reform session's ruling (message 3), FO does not ask the Captain; the reform session does. `scripts/lint-skills.py` refuses the README unless `WORKFLOW_BUDGET_STEPS` gains a +73 raise step whose `captain` field quotes his words (ADR 0020). The `loaded` moments are: Captain steps, before FO writes to the Captain; Schema, at each dispatch build; Dispatch facts, in every worker dispatch.
2. **Outcome 四 versus this scope (Captain or the reform session).** Outcome 四 says the FO-side stop belongs to Spacedock and the package owes only the worker's report of the shared assumption. This task's Scope asks the package to state the FO side. Recommend: place both, as designed. The package already owns the overrun hold (ADR 0077, `role_triggers.py`), so the split in outcome 四 does not describe the package today.
3. **First-report stamp: settled.** Ruled by the reform session under the Captain's grant (FO message record `dispatch/ideation-1-message-2.md`), not in his words: no new record in this task. Minutes to the first report stay not recorded, listed as an open gap against outcome 一.

Not done: no repository file, branch or commit was written. The proof was not run; it is designed only. The scoreboard's first-report trace is not built. Nothing outside the five rules was changed, including the duplicate peer sentence in `skills/dev/SKILL.md` ("Before naming a Captain action from a peer, …"), which is about actions, not rulings. Probe: none, because this workflow's ideation stage forbids repository writes. Not archived (private): the scratch candidate and its diffs; reproduce: `git -C <private working repository> archive 2b391a40f926646b6be949cb2cf07466005e277c | tar -x -C base`, then apply the wording above to a copy and diff the two.

### Batch overlap

These live tasks in this workflow touch the same rules in this repository's kc-dev-flow-2, not the extracted package. They share no file with this task's candidate, but a later port of either side meets the other's sentences.
- `captain-ruling-sources-checked` (ideation): the ruling sentence rule 4 edits.
- `design-check-reads-each-pilot-criterion-for-its-proof-record` (implementation): the per-criterion proof record rule 5 edits.
- `step-back-answer-has-a-record-line` (ideation): the overrun ask next to rule 3.

Recommended order: independent. If one of them lands first, port its sentence into the extracted package before this candidate's wording.

## Stage Report: ideation

- DONE: A design, written into the task file, that places each of the five rules once in the text its reader loads in the extracted package at the pinned base commit: for each rule the exact proposed wording, the file and section it goes in, which reader loads that file (First Officer, stage worker, or both), the outcome it serves by its number in the package's outcomes document, the existing sentence it replaces or makes unnecessary quoted with its file, and the net word change per reader by the package's own counting command or, if none exists, by a stated wc command
  `## Design` › `### Placement`: table plus exact wording at `2b391a40`. README 6113 → 6258 (+145), peers −10; FO +135, ideation worker +32, implementation and validation workers +29 (`evidence/ideation-1/word-deltas.txt`, `per-reader.txt`). The lint passes at base and fails at the candidate on the budget alone (`lint-base.txt`, `lint-cand.txt`). Follow-up message 1 is folded in under "Traces for the scoreboard".
- DONE: The fresh-reader proof designed so it can be run as written: the reader prompt for each role holding none of the rules' wording, what exactly the reader is given, the five questions, and how answers are judged; say what one reader per role and one run cannot show
  `### Fresh-reader proof`: base and candidate arms, an empty personal home, exact file sets, a prompt, FO S1–S5 with two controls, worker W1–W5, expected answers, judging by the quoted file and section, and five stated limits. Not run.
- DONE: Acceptance criteria refined only where the admitted ones are untestable as written, each change named; anything the design cannot place without restructuring a profile, and any decision only the Captain can make, reported instead of decided; a plain statement of what is not done
  AC-1 and AC-3 refined (named in each `Verified by:`): in place, `lint-skills.py` exits 1 before counting. AC-2 is unchanged. Nothing needs a profile restructure. `### Needs decision` lists 1, the +145 README word budget (Captain), 2, outcome 四 versus Scope (Captain or the reform session), and 3, the first-report stamp. "Not done" is stated.
- DONE: AC-1 evidence now
  The table and counts exist for the scratch candidate. The candidate commit does not exist yet: not yet verified.
- DONE: AC-2 evidence now
  The proof is designed and has not been run: not yet verified.
- DONE: AC-3 evidence now
  Growth is stated: +145 README, −10 peers, +135 FO, +29 to +32 per worker. It is paid only by the 10 peers words, so it needs decision 1: not yet accepted.
- DONE: design_surfaces.py check
  `python3 <package>/scripts/design_surfaces.py check <task>` exit 0, "design surfaces presentable".
- DONE: scratch close
  `Scratch removed: …/ideation-1 (5727275 bytes)`; `Evidence: evidence/ideation-1/ (5 files, 2.2 KiB)`. Not archived (private): the scratch candidate and diffs; reproduce as stated under "Not done" in `### Needs decision`.
- SKIPPED: roborev
  Not run: ideation produces no code candidate.
- SKIPPED: half-time-box self-check
  The report was written about 14 minutes after dispatch (timeline: ideation 12:18Z), before the 20:50 check fell due. The work still serves the stated goal.

### Summary

The five rules are placed once each. Rules 1 and 2 go in Captain steps, rule 3 in Schema plus Dispatch facts, rule 4 in the ruling sentence (the peers duplicate is removed), and rule 5 in the ideation stage text. No new script is involved; minutes come from the existing `task_timeline.py`. The README grows 145 words, which the lint refuses without the Captain's quoted raise (decision 1). Outcome 四 conflicts with this Scope (decision 2). The first-report trace stays not recorded (decision 3). No repository was written.

## Stage Report: ideation

- DONE: A design, written into the task file, that places each of the five rules once in the text its reader loads in the extracted package at the pinned base commit: for each rule the exact proposed wording, the file and section it goes in, which reader loads that file (First Officer, stage worker, or both), the outcome it serves by its number in the package's outcomes document, the existing sentence it replaces or makes unnecessary quoted with its file, and the net word change per reader by the package's own counting command or, if none exists, by a stated wc command
  `## Design` › `### Placement` at `2b391a40`. The time-box bullet now names FO and worker. README +156, peers −10; FO +146, ideation worker +43, implementation and validation workers +40; with no worker half of rule 3, 150/140/37/34. "Once" is read per part of rule 3. Past rulings ADR 0020, 0011 and 0077 are read and followed. Follow-up message 1 is folded in under "Traces for the scoreboard".
- DONE: The fresh-reader proof designed so it can be run as written: the reader prompt for each role holding none of the rules' wording, what exactly the reader is given, the five questions, and how answers are judged; say what one reader per role and one run cannot show
  `### Fresh-reader proof`: base and candidate arms, an empty home, exact file sets, a prompt, FO S1–S5 with two controls, worker W1–W5 (W2 and S3b give only a stop time), expected answers, judging, a launch note (`run_cell.py` has no launcher; it scans transcripts), and limits. Not run.
- DONE: Acceptance criteria refined only where the admitted ones are untestable as written, each change named; anything the design cannot place without restructuring a profile, and any decision only the Captain can make, reported instead of decided; a plain statement of what is not done
  AC-1 and AC-3 refined, each change named in its `Verified by:`. AC-2 is unchanged. No profile restructure. `### Needs decision`: 1, the +156 README word budget (Captain, ADR 0020); 2, outcome 四 versus Scope; 3, the first-report stamp. "Not done" is stated.
- DONE: AC-1 evidence now
  The table and counts were measured on a scratch candidate; the candidate commit does not exist yet: not yet verified.
- DONE: AC-2 evidence now
  The proof is designed and has not been run: not yet verified.
- DONE: AC-3 evidence now
  Growth is stated per reader and paid only by the 10 peers words, so it needs decision 1: not yet accepted.
- DONE: design_surfaces.py check
  `python3 <package>/scripts/design_surfaces.py check <task>` exit 0, "design surfaces presentable", after the corrections.
- DONE: scratch close
  `Scratch removed: …/ideation-1 (5727275 bytes)`; `Evidence: evidence/ideation-1/ (5 files, 2.2 KiB)`. Not archived (private): the scratch candidate and diffs, reproduced as stated under "Not done".
- SKIPPED: roborev
  Not run: ideation produces no code candidate.
- SKIPPED: half-time-box self-check
  Finished about 20 minutes after dispatch, before the 20:50 check fell due. The work still serves the stated goal.

### Summary

This report supersedes the earlier `## Stage Report: ideation`. The five rules are placed once each, rule 3 once per part. Rules 1 and 2 go in Captain steps, rule 3 in Schema and Dispatch facts, rule 4 in the ruling sentence (the peers duplicate is removed) and rule 5 in the ideation stage text, with no new script. The README grows 156 words, which the lint and ADR 0020 refuse without the Captain's quoted raise (decision 1). Outcome 四 conflicts with this Scope (decision 2). The first-report trace stays not recorded (decision 3).

## Stage Report: ideation

- DONE: A design, written into the task file, that places each of the five rules once in the text its reader loads in the extracted package at the pinned base commit: for each rule the exact proposed wording, the file and section it goes in, which reader loads that file (First Officer, stage worker, or both), the outcome it serves by its number in the package's outcomes document, the existing sentence it replaces or makes unnecessary quoted with its file, and the net word change per reader by the package's own counting command or, if none exists, by a stated wc command
  The Placement table, wording and counts are updated by `### Removal pass (follow-up message 2)` at `2b391a40`. README +130, peers −14; FO +116; ideation worker +38; implementation and validation workers +35 (`evidence/ideation-1/word-deltas-2.txt`, `per-reader-2.txt`). The lint fails only on the budget (`lint-cand-2.txt`).
- DONE: The fresh-reader proof designed so it can be run as written: the reader prompt for each role holding none of the rules' wording, what exactly the reader is given, the five questions, and how answers are judged; say what one reader per role and one run cannot show
  Unchanged; the reform session has confirmed it (recorded as its ruling under the Captain's grant). Not run.
- DONE: Acceptance criteria refined only where the admitted ones are untestable as written, each change named; anything the design cannot place without restructuring a profile, and any decision only the Captain can make, reported instead of decided; a plain statement of what is not done
  AC-1 and AC-3 refinements stand. Needs decision 1 is now +130 README / +116 FO. Decision 2 stays open with the Captain. Decision 3 is settled by the reform session: minutes to the first report stay not recorded, an open gap against outcome 一.
- DONE: Removal pass (message 2, item 1)
  20:39–20:42 local, inside the 20 minutes. Merged rule 3 with "first overrun holds for his amendment." and the Default sentence; dropped rule 2's minutes tail; cut "Unavailable originals stay unverified;" from peers; shortened the time-box bullet. Each removal is named with its covering rule and its risk if wrong.
- DONE: Net above zero reported (message 2, item 2)
  The FO net is +116. Not removable under "these five replace it": the budget grammar (22 words, covered by the seed check) and the `skills/dev/SKILL.md` peer-action duplicate (39 words). Taking both would leave +55.
- DONE: Settled items recorded (message 2, item 3)
  Recorded as rulings of the reform session under the Captain's grant, not as his words, in `### Removal pass` and Needs decision 3.
- DONE: AC-1 evidence now
  Measured on a scratch candidate; the candidate commit does not exist yet: not yet verified.
- DONE: AC-2 evidence now
  Designed and not run: not yet verified.
- DONE: AC-3 evidence now
  Growth is stated per reader and paid by the merges and the 14 peers words; the +130 README raise still needs decision 1: not yet accepted.
- DONE: design_surfaces.py check
  `python3 <package>/scripts/design_surfaces.py check <task>` exit 0, "design surfaces presentable".
- DONE: scratch close
  The first close removed `ideation-1` (`scratch-removed.txt`). The removal-pass copy, recreated by hand without an ownership mark, made `scratch.py close` refuse ("scratch ownership missing or differs"), so I removed it with `rm -rf` (6828 KiB of my own archive copies). Not archived (private): the scratch candidate; reproduce from the wording in `### Placement`.
- SKIPPED: roborev
  Not run: ideation produces no code candidate.

### Summary

This report supersedes both earlier `## Stage Report: ideation` sections. The removal pass cut the FO's net from +146 to +116 by merging rule 3 into the overrun sentence and trimming three restatements. The net is still above zero; the two remaining candidates are reported, not removed. Placement and proof are confirmed by the reform session; decision 3 is settled; decision 1 (+130 README raise, ADR 0020) and decision 2 wait for the Captain.

## Stage Report: ideation

- DONE: A design, written into the task file, that places each of the five rules once in the text its reader loads in the extracted package at the pinned base commit: for each rule the exact proposed wording, the file and section it goes in, which reader loads that file (First Officer, stage worker, or both), the outcome it serves by its number in the package's outcomes document, the existing sentence it replaces or makes unnecessary quoted with its file, and the net word change per reader by the package's own counting command or, if none exists, by a stated wc command
  The Placement table and wording are rewritten for pass 3 at `2b391a40`. README +73, peers −14, dev skill −38; **FO +21**; ideation worker +30; implementation and validation workers +27 (`evidence/ideation-1/word-deltas-3.txt`, `per-reader-3.txt`; `wc -w` over the FO file list; `spacedock dispatch show-stage-def … | wc -w` per stage). The lint fails only on the budget, +73 (`lint-cand-3.txt`).
- DONE: The fresh-reader proof designed so it can be run as written: the reader prompt for each role holding none of the rules' wording, what exactly the reader is given, the five questions, and how answers are judged; say what one reader per role and one run cannot show
  Confirmed by the reform session. Pass 3 adds S6 (the worth answers at a budget hold) and S7 (a peer's unverified fact), with the restore rule: a behaviour lost against base brings its removal back. Not run.
- DONE: Acceptance criteria refined only where the admitted ones are untestable as written, each change named; anything the design cannot place without restructuring a profile, and any decision only the Captain can make, reported instead of decided; a plain statement of what is not done
  AC-1 and AC-3 refinements stand. Needs decision 1 is rewritten: FO +21 and README +73 are both above zero, and the reform session, not FO, takes it to the Captain. Decision 2 stays open with the Captain. Decision 3 is settled.
- DONE: Message 3 item 1, rules tightened
  Rules 1 and 2 are 49 words; rule 3's FO half is merged into Schema; the worker half is +4; the time box is +23; rule 4 is +9. Worker half, rule 4 and rule 5 are kept as designed, only shortened.
- DONE: Message 3 item 2, two removals taken
  Schema's budget grammar sentence (−22) and the `skills/dev/SKILL.md` copy of peers line 19 (−38). Each risk is stated under `### Removal pass`.
- DONE: Message 3 item 3, final number
  FO net +21 (above zero); README +73. Counting commands are as in item 1 above. Stopped, as instructed.
- DONE: Message 3 item 4, at-risk scenarios
  S6 and S7 and the restore rule are added to `### Fresh-reader proof`.
- DONE: Message 3 item 5, measured times
  Pass 3: start 20:45:02, end 20:47:33 (`/bin/date`). The pass-2 line is corrected to its measured 20:39 to 20:43.
- DONE: AC-1 evidence now
  Measured on a scratch candidate; the candidate commit does not exist yet: not yet verified.
- DONE: AC-2 evidence now
  Designed and not run: not yet verified.
- DONE: AC-3 evidence now
  Growth is stated per reader, FO +21, and is not yet paid: not yet accepted.
- DONE: design_surfaces.py check
  `python3 <package>/scripts/design_surfaces.py check <task>` exit 0, "design surfaces presentable".
- DONE: scratch cleanup
  The pass-3 copies lived in a folder of my own outside the scratch tool, removed with `rm -rf` at 20:47:33. Not archived (private): the scratch candidate; reproduce from the wording in `### Placement`.
- SKIPPED: roborev
  Not run: ideation produces no code candidate.

### Summary

This report supersedes all earlier `## Stage Report: ideation` sections. Pass 3 tightened rules 1 to 3 and removed the budget grammar sentence and the dev skill's duplicate peer rule. The FO's net reading is now +21, above zero; the README is +73, which the lint refuses without a quoted raise. That number goes to the reform session, not to the Captain from FO. Decision 2 stays with the Captain.
