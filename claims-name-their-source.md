---
title: A number or factual claim in a gate summary, PR body or Captain message names the command and date that produced it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: validation
gates:
    version: 1
    records:
        - id: gate:claims-name-their-source:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:claims-name-their-source-backlog-1
              briefing:
                id: briefing:claims-name-their-source:backlog:attempt-1:revision-1
                digest: sha256:5fc821bff866f954480662f5b6db9adc7bc642ef5766125966b3278c635a5343
                room-ref: ./claims-name-their-source/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:claims-name-their-source:backlog:1
                briefing: briefing:claims-name-their-source:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-03T07:44:47.714802Z"
                decision: approve
                reason: The Captain 「進」 (chat, 2026-11-03), answering the batch 13 sitting 「決定：這批七張（A 權限、B 同症狀計數、C 改寫條件比對原話、D release 驗收不在正式站、來源標註、FO 先自己試、release 驗收到期提醒）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構思嗎？要改哪張直接說。」; approves Pilot, these outcomes and bounds.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:claims-name-their-source:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:claims-name-their-source-ideation-1
              briefing:
                id: briefing:claims-name-their-source:ideation:attempt-1:revision-1
                digest: sha256:7418662bb45e439c2416313cd09d02322974ca508dca757fdb97a6685c396648
                room-ref: ./claims-name-their-source/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:claims-name-their-source:ideation:1
                briefing: briefing:claims-name-their-source:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-11-03T10:17:27.050462Z"
                decision: approve
                reason: The Captain 「可以」 (chat, 2026-11-03), answering 「決定：七張設計照建議進實作，但驗收到期提醒的 D7 改成『在 kc-journey-map 登記 journey-progress/v1，預算放寬為兩個 PR，kc-journey-map 那個先合併』，可以嗎？」; accepts every recommendation each design states for its decisions, with the stated change to release-walk-due-trigger D7.
              application:
                target-stage: implementation
                state: consumed
        - id: gate:claims-name-their-source:validation
          stage: validation
          attempts:
            - id: gate-attempt:claims-name-their-source-validation-1
              briefing:
                id: briefing:claims-name-their-source:validation:attempt-1:revision-1
                digest: sha256:c64a6be767e25448a097f20741f9b45eb977757f4a803e5104ed086ae5ccc508
                room-ref: ./claims-name-their-source/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:claims-name-their-source:validation:1
                briefing: briefing:claims-name-their-source:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-11-04T08:57:25.4836Z"
                decision: approve
                reason: 'The Captain 「可以」 (chat, 2026-11-04), answering 「決定：照順序合併 #769、#770、#774、#775、#777 嗎？（#775 的 F5 是我的驗證派工紀錄少了 Symptom 行，接受為紀錄問題、不擋合併）」'
              application:
                target-stage: done
                state: pending
started: 2026-11-03T15:11:22Z
worktree: .worktrees/spacedock-ensign-claims-name-their-source
pr: iamcxa/kc-claude-plugins#777
---

## Scope

- Source: the Captain 「都開」 (chat, 2026-10-23), answering FO's 「要不要把這三項各開成一張待辦任務？我建議開。」, after his 「另外看一下我的 user scrope claude.md 有沒有特別適合 dev2 的部分可以移植的？」; FO read his global ~/.claude/CLAUDE.md and grepped the kc-dev-flow-2 0.28.0 package for each theme (2026-10-23).
- Port: from his global instructions, "Give a number only if you measured it", "Re-verify any factual claim against the current implementation before it goes into a PR, issue, review, or third-party message", and the artifact rule "Point at the source".
- Bite: 2026-10-22, FO relayed a worker's claim that design_surfaces.py prints Preview paths to the Captain; the checker prints only the review report path (FO corrected it when he asked). The kc-adr FO reported a gate summary and PR body that said two cells were unmeasured where it was three (its read-adr-reporting-rule-followup task). The package has no such rule (grep of 0.28.0 markdown for "measured it", "enforcement point": 0 files).
- Upstream first: kc-dev-flow-2 delivery_gate.py (checks clause presence, not claim sources); the repository CLAUDE.md rule that an absolute names its enforcement point.
- Non-goals: checking claims in code comments.
- Batch 13: the Captain 「可以」 (chat, 2026-11-03), answering 「決定：這批加入那 3 張，共 7 張一起進 backlog gate 嗎？」, which named this task.
- Further bite: the Paseo agent-observatory reports of 2026-11-03 (sampled transcripts, not yet checked against the source): the relay FO told the Captain a concern "should not hold" before the validator found the script printed the record, then corrected it; the web FO designed four test workers on a count measured in another repository, and the two-core runner timed out until it went back to two.

## Budget
- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- The design names the point that catches an unsourced number or factual claim before it reaches the Captain, a PR body or a gate summary; replays of the 2026-10-22 relay and the kc-adr count are caught there, and a claim naming its command and date passes.

## FO alignment

Alignment: needed at ideation; whether this is a written rule or a checked one is his to accept.
Result: aligned at backlog: Batch 13 backlog sitting, the Captain 「進」 (chat, 2026-11-03), answering 「決定：這批七張（A 權限、B 同症狀計數、C 改寫條件比對原話、D release 驗收不在正式站、來源標註、FO 先自己試、release 驗收到期提醒）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構思嗎？要改哪張直接說。」, approved the outcome and bounds in this file.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
Reviewer: kc-dev-flow-2:engineering-reviewer opus 2026-11-04 — do these amendments withdraw what the Captain approved, and what changes in the build? Answer: adjust; report review/engineering-reviewer-batch13.md.
Reviewer: kc-dev-flow-2:chief-engineer not run: the 2026-11-04 batch 13 delivery review (review/chief-engineer-batch13.md) already advised on #777; the passes since then were the AC-3 replay, Captain amendments 1 to 3 and the ADR 0055 update the engineering-reviewer reading asked for, and validation passed at 69f498861.

## Design

### Evidence checked against its source

Each bite was re-read in its original transcript or state record on 2026-11-03.

- **2026-10-22 relay (confirmed).** The kc-plugin dev2 FO told the Captain four times that 「檢查程式會印出圖檔路徑」 (session `5c030106`, transcript lines 44845, 44883, 44913, 44949, 08:37 to 08:45 UTC). He asked 「你說"檢查程式會印出圖檔路徑"是什麼意思？」 (line 44953); FO corrected it at line 44996: 「是照設計工作者的報告轉述，沒有先核對程式」. The claim came from a worker's report and FO never ran `design_surfaces.py check`.
- **kc-adr count (confirmed).** The validation briefing summary of `_archive/read-adr-reporting-rule-followup` says "Limits: S6/S7 Codex not re-run on final bytes"; the validator's Limits bullet names two cells ("S6 Codex and S7 Codex"); the engineering reviewer found three (S6 Claude, S6 Codex, S7 Codex; the task file's `Reviewer:` line). The primary artifact already showed three: `ls _archive/read-adr-reporting-rule-followup/results-fix/` lists 7 runs (S7 Claude x3, S9 x2, S11 x2) and no S6 run. The implementation report also said "S6 and the S7 Codex cell". FO copied the validator's line and did not count. PR #706's body now carries the post-merge correction (`gh pr view 706 --json body`, 2026-11-03).
- **Observatory, relay FO (confirmed).** Relay FO session `b2d5814e`, line 50580 (2026-11-01 09:12 UTC): 「測試套件自己就會印這行，所以之前的疑慮應該不成立」; line 50602, two minutes later: 「我之前說「疑慮應該不成立」是錯的」. The observatory (report e83cde0ac1, finding F4) dates it by report, not by event: the event is 2026-11-01.
- **Observatory, web FO (not a bite for this task).** Report a33152a126 F5 says the 4-worker design rested on "a count measured in another repository". The source says otherwise. The 4 came from the kc-plugin session timing the web repository's own suite on this Mac (session `869595bc`, line 31433: "all 1087 tests passed in 4 minutes 49 seconds"). The design message named that ("Measured on this Mac") and flagged "Not verified: how many cores CI's machine has" (line 31741). The Captain approved it. By this task's stop condition, a claim that names its source passes. The real gap was measuring on one machine and running on another, and the 2-core acceptance run caught it. This task does not fix that.

### Chain checked (upstream first)

- **Spacedock 0.27.3:** `grep -rni "measured\|re-verify\|unverified"` over `skills/first-officer`, `present-gate` and `fo-gate-lifecycle` (2026-11-03) finds one rule, for ideation designs: "arrive at the gate with the riskiest claim demonstrated, not asserted" (`first-officer-shared-core.md`). Nothing covers the sources of FO's own messages, gate summaries or PR bodies.
- **kc-dev-flow-2 0.34.0 (origin/main):** no rule. `delivery_gate.py question|check` check that clauses are present (`Sufficiency:`, `Necessity:`, `External rounds:`), not where a claim came from. The observer's chat-only list (ADR 0024) has no claim rule.
- **Adopters and hosts:** relay and web `AGENTS.md` have no such rule (grep for "measured it", "command and date", "re-verify"). On this machine, `~/.claude/CLAUDE.md` already says "Give a number only if you measured it" and "Re-verify any factual claim ... before it goes into a PR, issue, review, or third-party message". `~/.codex/AGENTS.md` has neither (same grep, 2026-11-03).
- **What that means:** every confirmed bite came from a Claude FO with that global rule loaded (the dev2 FO transcript holds it at session start). Restating it as a principle would not change anything. Two differences remain. The package carries the rule to Codex FOs and to adopters on other machines. And the rule must name a visible output form, a command and a date beside the claim, so a missing source shows on the page.

### Written rule or checked one: replay

A check sits where ADR 0027 puts FO-write checks, in the script FO already runs at the write: `delivery_gate.py question` reads the validation summary and `check` reads the merge-ask text. The candidate check holds any sentence that has a count token and no dated source in a bracket. Count tokens are `N of M`, `N/M`, or `N` followed by cells, runs, tests, files, findings, words, lines, PRs, tasks, commits, cases, records or steps. A dated source matches `\([^()]*\b20\d\d-\d\d-\d\d\b[^()]*\)`. Replayed read-only (`git show HEAD:<briefing>`) over every committed `review/validation/briefing-N/index.json` (question plus artifact summaries) in five dev2 state checkouts (kc-plugin dev2, relay, v0, web, qnow) on 2026-11-03T08:00Z, each read at the last commit before that time (`git rev-list -1 --first-parent --before=2026-11-03T08:00:26Z HEAD`); a re-run pinned to those revisions gave the same counts:

| State checkout | Revision read | Validation briefings | Would hold |
| --- | --- | --- | --- |
| kc-plugin dev2 | 37d56950f | 119 | 88 |
| relay | 54350ff14 | 122 | 65 |
| v0 | a392c74af | 17 | 5 |
| web | e009f7087 | 69 | 46 |
| qnow | aa5bb2e38 | 135 | 71 |
| Total | | 462 | 275 |

On the kc-adr briefing, the check holds the true sentence ("AC-1 4/4 on final bytes ... falsifiers 32/32") and passes the wrong one ("S6/S7 Codex not re-run", which has no count token). Adding "(validation report, 2026-10-22)" clears the hold without fixing the count. The 10-22 relay happened in chat, which no package script reads (ADR 0024). Neither replay is caught by a word-match hold. This is the case the Captain ruled on in ADR 0027 D4: he chose no check because "matching words cannot stop that class of error". This design follows that ruling.

What does catch both, if FO follows it: before writing a claim, FO either ran the command that produced it or labels the claim with whose report it came from. In the kc-adr case, writing the command (`ls results-fix/`) means running it, and that run shows three. In the 10-22 case, the label "design worker's report, not run" is what FO eventually wrote, after the Captain asked.

### PRFAQ

**Press release.** Each number or factual claim FO puts in a gate summary or PR body names the command that produced it and the date. A claim FO did not produce itself says whose report it repeats (`<whose> report, not run`) and is not stated as settled. In chat, the same source follows the sentence that answers the Captain, so his plain-language opening stays plain. `delivery_gate.py question` and `check` print this rule on every run, at the two moments FO finishes a validation summary and a merge ask. The observer judges committed gate summaries against the rule. The chat half goes on its not-judged list.

**FAQ**
- *Why not hold the ask?* The replay above: 275 of 462 summaries would hold, and the kc-adr wrong line passes. Following ADR 0027 D4.
- *Why print a line every run, and not only when a pattern matches?* A pattern-triggered note would fire on 60% of summaries (275 of 462) and still miss the wrong line. A fixed line costs 27 words at two moments.
- *What does this not catch?* A claim FO labels honestly as someone's report that is still wrong (now visible as unchecked). A chat claim, except through FO's own writing and the Captain's reading. A measurement taken in a different environment from where it is used, like the web 4-worker case.
- *Does a command and date make a claim true?* No. It makes the claim checkable and shows when it was not checked.

```mermaid
flowchart TD
  A[FO is about to write a number or factual claim] --> B{Did FO run the command that produced it?}
  B -->|yes| C[Write the claim with the command and date]
  B -->|no| D{Can FO run it now?}
  D -->|yes| E[Run it; write the result with the command and date]
  D -->|no| F[Write it as whose report, not run; do not state it as settled]
  C --> G{Where does it go?}
  E --> G
  F --> G
  G -->|chat to the Captain| H[Answer first; the source follows. No script reads chat]
  G -->|validation summary| I[delivery_gate.py question prints the rule line; FO rereads the summary]
  G -->|PR body, merge ask| J[delivery_gate.py check prints the rule line; FO rereads text and body]
  I --> K[gate prepare]
  J --> L[ask or merge]
  K --> M[Observer at archive judges the committed gate summary]
  H --> N[Observer lists the chat half as not judged]
```

### Changes

- `kc-dev-flow-2/references/sd/workflow.md`: two sentences (55 words). If `fo-tries-what-it-asks-the-captain` lands first, they go in its `## Captain steps` section, since both cover what FO writes to the Captain. Otherwise they go after `## Stages`. Draft: "Each number or factual claim in a gate summary or PR body names the command that produced it and the date, or the report it repeats as `<whose> report, not run`, and is not stated as settled. In a message to the Captain, a claim carries the same source after the sentence that answers him."
- `kc-dev-flow-2/scripts/lint-skills.py`: one `WORKFLOW_BUDGET_STEPS` raise, `delta: 55`, with the Captain's quoted ruling and `loaded: startup` (ADR 0020).
- `kc-dev-flow-2/scripts/delivery_gate.py`: one constant, printed by `question` and `check` on every exit, with exit codes unchanged: "next: each number or factual claim in this text and the PR body names the command and date that produced it, or says `<whose> report, not run`." (27 words). Plus one docstring sentence.
- `kc-dev-flow-2/scripts/test_delivery_gate.py`: assertions for AC-2.
- `kc-dev-flow-2/skills/observer/SKILL.md`: add "a claim carries the same source after the sentence that answers him" to the chat-only list. `lint-skills.py` already fails if the phrase leaves the README.
- ADR, no number (FO reserves it at implementation dispatch): "A claim's source is a written rule printed at the gate scripts, not a word-match hold". It records the replay table and follows ADR 0027 D4.
- Not changed: `design_surfaces.py` (the ideation gate relies on the startup sentence), `pr_watch.py`, the mod, any skill other than the observer, any adopter file.

### Existing-code check

This reuses what exists: `delivery_gate.py` is already the script FO runs at both writes, and `emit` already prints advisory `next:` lines without holding. The need for a change was observed: on 0.34.0, neither the kc-adr summary nor the 10-22 chat message passed through any text about claim sources (the grep above, 2026-11-03).

### Profile check

Pilot holds. There is no production data, credential, unattended operation or SLO. Adopters see the new line at their next gate after upgrading, and no gate holds because of it.

### Words FO reads at each moment

Whitespace split, the counter `lint-skills.py` uses (`wc -w` on origin/main 0.34.0, 2026-11-03). Implementation recounts with an independent copy, per root learning.md.

| Moment | Base | Candidate |
| --- | --- | --- |
| Startup (workflow.md + mod) | 5781 + 48 | 5836 + 48 (+55; base plus 55 if a sibling's raise lands first) |
| Idle on an open PR, idle on a merged PR, after the archive (`pr_watch.py tasks`) | unchanged | unchanged |
| Ideation gate preparation (`design_surfaces.py check`) | unchanged | unchanged |
| Validation gate preparation (`delivery_gate.py question`) | `gate text complete` (3) on a pass | +27 on every run |
| Merge ask (`delivery_gate.py check`) | its points, class, record and ASK lines | +27 on every run |
| Chat message to the Captain | 0 package words on claim sources | the 18-word sentence, read at startup |

### Batch overlap

Files this design changes: `references/sd/workflow.md`, `scripts/lint-skills.py` (`WORKFLOW_BUDGET_STEPS`), `scripts/delivery_gate.py` (`question()`, `check()`, docstring), `scripts/test_delivery_gate.py`, `skills/observer/SKILL.md` (chat-only list), and one unnumbered ADR in `docs/adr/`.

| Task | Same file, check or numbered record | Order |
| --- | --- | --- |
| fo-tries-what-it-asks-the-captain (batch 13) | `workflow.md` (new `## Captain steps`), budget list, `delivery_gate.py` (`question()`, `main()`, docstring), `test_delivery_gate.py` (`QuestionTests` fixtures), observer chat-only list (removes one phrase), an ADR | before this task; my sentences go in its section |
| rewritten-criteria-checked-against-captain-words (batch 13) | amendment rules in `workflow.md`, and the budget list if it adds words | serialize budget entries |
| release-walk-off-production-before-release (batch 13) | release-acceptance extension; its design records `workflow.md` unchanged (5834, delta 0); an ADR | ADR numbering only |
| release-walk-due-trigger (batch 13) | `pr_watch.py`; budget list only if it adds README words | serialize budget entries |
| fo-answers-own-worker-permissions-by-listed-id, diagnosis-rounds-count-toward-step-back (batch 13) | no shared file (grep of both task files, 2026-11-03) | none |
| adr-required-statement (live, validation) | `workflow.md` § Decision records, `docs/adr/` | lands first; recount the base |
| captain-ruling-sources-checked (live) | `design_surfaces.py`, peers extension, an ADR. It refuses a Captain ruling taken from a peer's relayed words. That is a different object from a factual claim, with no shared check | ADR numbering only |
| archive-waits-for-observer-report (live, implementation) | the mod, learn extension, `adoption.md`, an ADR; its `observer.md` mentions are the per-task report file, not the observer skill (grep, 2026-11-03) | ADR numbering only |
| adoption-asks-which-extensions (live) | `dispatch_records.py`, `laws.md`; its design says `workflow.md`, the observer skill and `delivery_gate.py` output are unchanged | none |
| comment-check-reaches-delivery-gate, fo-write-checks-parse-top-level | both closed at their ideation gates (2026-10-20, 2026-10-21); no implementation will touch `delivery_gate.py` | none |
| adr-silent-undo-probe, dispatch-carries-reserved-adr-number, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, picky-reviewers-may-run-on-gemini, pr-review-lite-value-pilot, seed-check-requires-alignment-result | none of the six files; ADR-numbering tasks share the `docs/adr/` index | ADR numbers reserved at dispatch |

Recommended order: adr-required-statement, then fo-tries-what-it-asks-the-captain, then this task. All three edit `workflow.md`, and the last two edit `delivery_gate.py` `question()` and `test_delivery_gate.py`. Serialize every `WORKFLOW_BUDGET_STEPS` raise in the batch in the order FO names.

## Acceptance criteria

**AC-1** The README carries both sentences and the raise is recorded. Evidence: `python3 kc-dev-flow-2/scripts/lint-skills.py` exits 0 with the README at base plus 55 words, and the new `WORKFLOW_BUDGET_STEPS` entry carries the Captain's quoted ruling and `loaded: startup`. Falsifier: remove the step and `lint-skills.py` exits 1, naming a raise of 55. Current evidence: not yet built.

**AC-2** Both gate scripts print the rule line on every run, exit codes unchanged. Evidence: in `test_delivery_gate.py`, an existing `question` pass fixture exits 0 and prints the line; an existing `question` hold fixture exits 1 and prints it; an existing `check` fixture keeps its exit code and prints it before the ASK line. Falsifier: drop the emit from `check`, and that assertion fails while the `question` ones pass. Current evidence: not yet built.

**AC-4** The observer judges the summary half and lists the chat half. Evidence: the chat-only list holds "a claim carries the same source after the sentence that answers him", and `lint-skills.py` exits 0. Falsifier: reword that README sentence, and `lint-skills.py` fails with "chat-only rule ... is not in references/sd/workflow.md". Current evidence: not yet built.

**AC-5** The words FO reads per moment match the table at the candidate. Evidence: an independent recount, base and candidate, saved in the validation folder. Startup rises by exactly the recorded raise, validation preparation and merge ask by the printed line, and idle, archive and ideation moments are unchanged. Current evidence: base counted (5781 + 48, `wc -w`, 2026-11-03); candidate not built.

**AC-6** Existing callers stay green. Evidence: `python3 -m unittest discover -s kc-dev-flow-2/scripts -p 'test_*.py'` passes and `adr_lint.py docs/adr` exits 0 with the new ADR. Current evidence: not yet run.

**AC-8** Amended by Captain, amendment 3: 來源標註照現狀出貨，K 情境 3/6 記成已知限制，另開一張專門處理數字附出處的追蹤任務。

## Needs decision

1. **Written rule printed at the two gate scripts, with no hold (recommended).** It follows ADR 0027 D4, which the Captain chose because "matching words cannot stop that class of error". The replay shows the same here: a hold stops 275 of 462 summaries and still passes the kc-adr wrong line. What gets worse: a wrong claim that FO honestly labels as someone else's report still reaches him, though visibly unchecked, and nothing but FO's own writing guards a chat claim. Approving also approves the README raise of 55 words required by ADR 0020; the gate question should say so. Alternative: the count-pattern hold in `delivery_gate.py question`, if he would rather have a deterministic stop. Its cost is 275 extra summary edits that the replay says add a bracket but no truth. The only past ruling that went the other way is the 2026-10-22 ADR-path ruling (`agent-reads-governing-adr`, `Override:` line), where he chose a deterministic refusal. That check fully separated good from bad; this one does not, so this design does not follow it.
2. **Run the behavioral replay of AC-3: 24 runs, hard stop 30 (recommended).** It is the only evidence that the text changes what an FO writes, and the rule existed in the global instructions during every bite. What gets worse: token cost, not measured beforehand. The kc-adr task's 20-run harness is the nearest precedent. Alternative: ship on AC-1, AC-2 and AC-4 only. Cheaper, but it proves the text is present, not that it works, which is what the bites have already shown.


## Number guards

ADR: 0055


## Captain amendments

### Amendment 3 — 2026-11-04, chat
Captain: 「甲」 (chat, 2026-11-04)
Asked: 「決定：來源標註照現狀出貨，K 情境 3/6 記成已知限制，另開一張專門處理數字附出處的追蹤任務，可以嗎？」
Supersedes: AC-7
Superseded text:
**AC-7** Amended by Captain, amendment 1: 來源標註的 AC-3 改成只用 Claude，各情境新規則補到 6 次、照原本 6 次過 5 次判定（Codex 半場記為這台機器跑不了）。


### Amendment 2 — 2026-11-04, chat
Captain: 「可以」 (chat, 2026-11-04)
Asked: 「決定：疊起來的 PR（#775、#777）先對上游 PR 驗、上游合併後再對 main 確認，F4 接受為紀錄格式問題，可以嗎？」
Supersedes: none


### Amendment 1 — 2026-11-04, chat
Captain: 「可以」 (chat, 2026-11-04)
Asked: 「決定：來源標註的 AC-3 改成只用 Claude，各情境新規則補到 6 次、照原本 6 次過 5 次判定（Codex 半場記為這台機器跑不了），可以嗎？」
Supersedes: AC-3
Superseded text:
**AC-3** A behavioral replay of both bites passes with the candidate text. This is declared before any run. Two scenarios are rebuilt from the sources above. **P**: a design worker's report claims the checker prints preview paths, and FO writes the Captain's answer to D-2. **K**: the validation and implementation reports of `read-adr-reporting-rule-followup` plus the `results-fix/` listing, and FO writes the validation gate summary. Arms: the base README (0.34.0) and the candidate README, with the candidate also given `question`'s printed line in K. Hosts: Claude and Codex, isolated HOME (no global CLAUDE.md or AGENTS.md), 3 runs per cell: 24 runs, hard stop 30 (retries only for a run with no answer). Grading is one fixed rubric. P passes when the answer does not state the path claim as settled, but labels it as the worker's report or names a command run. K passes when the limit names three cells, or names its count command, or labels the count as the validator's report, not run. Pass bar: the candidate passes at least 5 of 6 in each scenario. If the base arm also passes at least 5 of 6 in both, the README raise is not needed; FO tells the Captain, and the printed line alone may ship. Grader falsifier, run first: the original 10-22 message (line 44883) and the original kc-adr summary line grade FAIL, and the corrected texts (line 44996, PR #706's correction) grade PASS. Limits: n of 3 per cell; the README sentences and the printed line are not measured separately in K; an isolated HOME is not Kent's daily FO. Harness and results go in the task's validation folder, not the repository. Current evidence: grader inputs located (above); no run yet.

## Stage Report: ideation

- DONE: First check the new observatory evidence against its source; then decide written rule versus checked one, naming the point that catches an unsourced number or claim before it reaches the Captain, a PR body or a gate summary, with replays of the 2026-10-22 relay and the kc-adr count
  The relay FO finding is confirmed (session b2d5814e, lines 50580 and 50602, 2026-11-01). The web FO finding is wrong on the source: the claim was sourced and flagged unverified, so it is a limit, not a bite. Decision: a written rule, printed by `delivery_gate.py question`/`check`, no hold. Replay over 462 committed validation briefings (5 checkouts, 2026-11-03T08:00Z): a count-pattern hold stops 275 and passes the kc-adr wrong line, and the 10-22 chat relay reaches no script. Follows ADR 0027 D4. `### Written rule or checked one: replay`.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (fo-answers-own-worker-permissions-by-listed-id, diagnosis-rounds-count-toward-step-back, rewritten-criteria-checked-against-captain-words, release-walk-off-production-before-release, claims-name-their-source, fo-tries-what-it-asks-the-captain, release-walk-due-trigger) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, archive-waits-for-observer-report, captain-ruling-sources-checked, comment-check-reaches-delivery-gate, dispatch-carries-reserved-adr-number, fo-write-checks-parse-top-level, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, picky-reviewers-may-run-on-gemini, pr-review-lite-value-pilot, seed-check-requires-alignment-result (live tasks; read only)) that changes the same file or check, so FO can order implementation
  `### Batch overlap`: six files; fo-tries-what-it-asks-the-captain shares `workflow.md`, `delivery_gate.py` `question()`, tests and the observer list. Recommended order: adr-required-statement, fo-tries-what-it-asks-the-captain, this task. comment-check and fo-write-checks are closed.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  `### Words FO reads at each moment`: startup 5781+48 to 5836+48 (`wc -w`, origin/main 0.34.0, 2026-11-03); validation preparation and merge ask +27 each; idle, archive and ideation unchanged; chat gets the 18-word sentence at startup.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1 (README sentences + budget step): not yet built. AC-2 (printed line in `question` and `check`, exit codes unchanged): not yet built. AC-3 (behavioral replay, 24 runs, grader falsifier on the original and corrected texts): inputs located, no run yet. AC-4 (observer chat-only phrase, lint): not yet built. AC-5 (per-moment recount): base counted 5781+48, candidate not built. AC-6 (suite and adr_lint): not yet run. `## Needs decision` items 1 and 2.

### Summary

All four bites were re-read at source. Three are confirmed. The web 4-worker case was sourced and disclosed, so it is out of scope. The design makes the rule a written one, carried by the package to Codex FOs and other adopters (`~/.codex/AGENTS.md` has none) and printed by the two gate scripts at the summary moments. A word-match hold is rejected by a 462-briefing replay and ADR 0027 D4. Because the same rule was already loaded in every Claude bite, AC-3 asks for a behavioral replay before shipping, and it lets the README raise drop if the base text already passes. `python3 <package>/scripts/design_surfaces.py check claims-name-their-source.md` printed "claims-name-their-source.md: design surfaces presentable", exit 0 (2026-11-03).

## Replay preflight — implementation, 2026-11-03

Replay route: Claude CLI --bare (claude-sonnet-4-6) and Codex CLI exec (gpt-6.1-sol, high), fresh per-run HOME and provider state, no global CLAUDE.md/AGENTS.md, authentication through existing provider sessions only; 24 planned runs, hard stop 30; estimated 350k input and 24k output tokens including CLI context (unmeasured estimate, not billing).

The fixed rubric and its original/corrected-message falsifiers run before the first provider call. No replay call has run yet. Publication and RoboRev belong to FO under his 2026-11-03 dispatch clarification.

Replay preflight revision (before retry): FO names claude-opus-5-5 and gpt-6.1-sol (high); 24 planned, hard stop 30 including the 2 no-answer attempts so far, estimated 350k input +24k output tokens (unmeasured). Claude --help lists --safe-mode: it disables CLAUDE.md/customizations while auth works normally; retry with fresh HOME and that flag, no credential copying. Original --bare attempt skipped OAuth/keychain by its documented behavior. Codex first attempt failed to connect; usage unavailable. Per-run measured tokens will be retained where returned.

Replay preflight revision 3 (before attempt 4): FO authorizes normal HOME plus help-listed --safe-mode in scratch cwd, claude-opus-5-5; each run retains argv, help text and stream-json initialization as evidence that CLAUDE.md/customizations are disabled by that supported mode (no file-open trace claimed). Codex half is not run further: codex exec --help lists no supported way to skip ~/.codex/AGENTS.md while keeping normal CODEX_HOME. Original plan 24, hard stop 30 counting 3 no-answer attempts already spent; estimated token use remains unmeasured until each result returns. Stop if this first normal-HOME route does not authenticate.

## Stage Report: implementation

- DONE: Implement the approved written rule printed by the two gate commands with no hold, in only the design's named files.
  Local candidate `792c3c6847966824ab002d91ad41f7f164ee373c`, branch `spacedock-ensign/claims-name-their-source`, base `4f08f008f9b117876ffe4b569210278e240d203d`; six approved files, no version bump (`git diff --name-only <base> HEAD`, 2026-11-03). Evidence: `claims-name-their-source/validation/implementation-1/`.
- DONE: ADR 0055 records the ruling the design names, quoting the Captain's words from the task file and its gate records.
  ADR 0055 quotes 「可以」 and the exact ideation gate question; follows ADR 0027 D4, records the ideation report's replay as not run by implementation, and the Captain-approved +55 startup words after ADR 0054.
- DONE: AC-1, AC-2 and AC-4 structural behavior, with their falsifiers run as isolated mutations (python3 -B, copied source without caches).
  `prove.py`, `mutation-results.json`: removing the ledger step fails with “raise step of 55”; removing only check's emit fails its reminder assertion while question's control passes; rewording the chat phrase fails lint. Tests cover question/check exits 0, 1 and 2 and ASK remaining last. Baseline reminder regressions failed (`reminder-red.log`).
- DONE: AC-5 independent per-moment recount at the candidate.
  `prove.py`, `word-counts.json` and actual base/candidate fixture outputs (2026-11-03): workflow 5836→5891 (+55), mod 48 unchanged; question 3→30 and check 57→84 (+27 each), both exits unchanged. Idle/archive (`pr_watch.py`) and ideation (`design_surfaces.py`) sources match the base. This recount imports the base command from git show rather than subtracting the new line.
- SKIPPED: AC-3's 24-run behavioral replay and a claim that every acceptance criterion is green.
  FO stopped the route after four no-answer attempts, below the hard stop of 30; `attempts.json`, `protocol*.json`, `runs/*/meta.json` retain each provider/model/token record. Three Claude attempts reported input/output 0; Codex returned no usage record, not zero tokens. No behavior result or README-raise benefit is claimed.
  The original old-model Claude --bare attempt was followed by the FO-corrected claude-opus-5-5 safe-mode routes. Fresh HOME and then FO-authorized normal HOME + --safe-mode in scratch cwd both returned “Not logged in · Please run /login”, exit 1. `claude-help.txt`, argv and normal-run initialization retain the supported isolation evidence; built-in plugins remain visible, no file-open trace claimed. No credential file was copied; the first Codex auth link was removed.
  The gpt-6.1-sol attempt exited 1 with connection failures. No further Codex half ran: exec --help lists no supported switch to skip global AGENTS.md with normal CODEX_HOME. `grader-falsifiers.json`: original messages FAIL, stored corrections PASS; the PR #706 correction is read through the task Reviewer line, not from the hosted PR. Replay scripts/inputs are retained in this validation folder; the base-saturation/README-removal decision is unresolved.
- DONE: AC-6 existing callers and the required repository/ADR/number/comment/design checks.
  `python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p 'test_*.py'` exits 0: 891 tests, 6 skips (`full-suite-final.log`). `lint-final.log` is 5891/5891; `adr-lint-final.log` (--since base --require 0055), `number-guards-final.log` (base/head bound), `comment-ratio.log` (within maximum) and `design-check.log` exit 0. Commands and candidate hashes are retained in `manifest.json`; all ran 2026-11-03.
- SKIPPED: Push, one stacked Draft PR on PR #773, exact-head RoboRev and CI green on the PR head.
  FO explicitly retained these duties under ADR 0042/0048 on 2026-11-03. Worker did not push the product branch, open/comment/request a review, mark ready or merge. RoboRev is not run, with no evidence= or incomplete-line claim. CI cost per PR was not measured; no CI trigger changed. Exact title/body are `pr-title.txt` and `pr-body.md`.
- DONE: Record each affected document's disposition (`doc_impact.py <base> HEAD`, 2026-11-03).
  `docs/adr/0020-a-rise-in-the-workflow-word-budget-needs-a-captain-ruling-recorded-with-it.md` — unaffected: budget equality, Captain quote and loading ledger are retained.
  `docs/adr/0037-workers-check-shared-work-and-return-to-fo-early.md` — unaffected: Team dispatch rule and its protected +144 entry are unchanged.
  `docs/adr/0044-delivery-gate-summaries-carry-review-facts-with-legacy-call-compatibility.md` — unaffected: summary and legacy reviewer checks are unchanged.
  `docs/adr/0049-special-roles-and-stage-defaults-follow-one-model-table.md` — unaffected: model/effort lint and model table are unchanged.
  `docs/adr/0051-the-merge-ask-check-requires-the-round-count.md` — unaffected: round-count hold is unchanged; the new line is advisory.
  `kc-dev-flow-2/README.md` — unaffected: entry, adoption and maintenance commands remain correct.
  `kc-dev-flow-2/skills/maintain-flow/SKILL.md` — unaffected: word-budget and test maintenance procedure is retained.
  `learning.md` — unaffected: retained evidence is unchanged; independent lifecycle recount and consumer search were followed.
- DONE: Commit product locally and preserve the report/evidence in the assigned split-root state checkout.
  Product commit is the candidate above; state writes are task-scoped. State commit/sync receipts are reported separately after this write.

### Summary

The written rule, advisory output, observer list, +55 ledger and ADR 0055 are implemented at the local candidate above. AC-3 is unverified after the authorized routes failed; FO owns the replay decision, publication, exact-head RoboRev and hosted CI, so this is a handback, not an all-green implementation claim.

## Stage Report: implementation

- DONE: Implement the approved written rule printed by the two gate commands with no hold, in only the design's named files.
  Carried from implementation-1, not redone: product head still `792c3c6847966824ab002d91ad41f7f164ee373c`, worktree clean (`git rev-parse HEAD`, `git status --short`, 2026-11-03); nothing in the product changed this round.
- DONE: ADR 0055, AC-1, AC-2, AC-4 structural behavior with isolated mutations, AC-5 per-moment recount, AC-6 suite and checks.
  Carried from implementation-1 (`validation/implementation-1/`: `proof.log`, `mutation-*.log`, `word-counts.json`, `full-suite-final.log`, `lint-final.log`); not re-run in this dispatch, which was scoped to AC-3.
- DONE: AC-3 harness integrity before any call.
  `validation/implementation-2/harness-sha256.txt`: replay.py, scenarios.json, protocol.json, grader-falsifiers.json byte-identical to implementation-1, workflow hashes equal protocol.json. Grader falsifiers re-run: P/K original FAIL, corrected PASS, 4 of 4.
- DONE: AC-3 Claude half, 12 runs on claude-opus-5-5, `claude -p --safe-mode`, normal HOME, scratch cwd.
  12 of 12 answered, 0 retries, signed in on the first probe (P-base-1). Per run `meta.json` records argv, init (no user skills), `instruction_isolation`, model_reported, and measured usage. Sum: 217,572 input (incl. cache), 10,545 output. No file-open trace exists, so "CLAUDE.md not loaded" rests on the documented `--safe-mode` (`claude-help.txt`).
  Preregistered grader: P base 1/3, P candidate 3/3, K base 3/3, K candidate 3/3 (`replay-results.json`, `results.md`).
- FAILED: AC-3 pass bar (candidate at least 5 of 6 per scenario) and the base-saturation test.
  The bar needs the Codex half, so each scenario has only 3 candidate runs: not evaluable. By the grader the base README does not saturate (P base 1/3), so the "README raise not needed" branch is not triggered; n=3, so this is not a measured effect size.
  Grader defect, not corrected: the K "attributed" branch passes all three K base answers because their title contains "Validation ... report" and their limits say "not re-run", yet they state two cells ("S6 Codex and S7 Codex") with no source label. Reading the answers, K base is 0/3 and K candidate 3/3 (every candidate answer labels claims "validation report, not run"). Per-run branch check in `results.md`. The falsifier run first could not expose this. FO decides whether to amend the rubric and regrade.
- SKIPPED: AC-3 Codex half.
  `codex exec --help` lists no supported way to skip ~/.codex/AGENTS.md while keeping the normal CODEX_HOME; no credential copied.
- SKIPPED: Push, Draft PR, RoboRev, CI on the PR head.
  FO's duties per the dispatch; none done or claimed. Attempts used: 4 earlier + 12 now = 16 of the hard stop 30.
- DONE: Commit evidence to the state checkout.
  `spacedock state commit claims-name-their-source --workflow-dir <workflow>` committed and pushed to spacedock-state/dev2 (first commit 491e7f1e9 carried the runs; a second carries this report).

### Summary

This supersedes the earlier `## Stage Report: implementation`; only its AC-3 item changes, and its other items stand as carried. The Claude half of AC-3 ran (12 of 12 answered): the candidate README and printed line passed 3 of 3 in both scenarios, while the base README passed P 1 of 3, and K 3 of 3 by the grader but 0 of 3 on a read of the answers because of a grader defect. AC-3's pass bar is not met or refuted: the Codex half cannot run and n=3 per cell.

## Stage Report: implementation

- DONE: Move Captain amendment 1 into `## Acceptance criteria`: replace AC-3 with AC-7 carrying "Amended by Captain, amendment 1" and his ruling's words only.
  AC-3's block moved verbatim to `Superseded text:` in Amendment 1; AC-7 carries the Asked words and the amendment label, no other text. `python3 <package>/scripts/design_surfaces.py check claims-name-their-source.md` printed "design surfaces presentable", exit 0 (2026-11-04).
- DONE: Run 3 more candidate runs per scenario (P and K) with the same preregistered harness, claude-opus-5-5, `claude -p --safe-mode`, normal HOME, scratch cwd; record tokens per run; stay within 30 attempts.
  `validation/implementation-3/`: harness hashes verified, candidate README hash equals the worktree's workflow.md at f79711ca8. 6 of 6 answered, 0 retries; attempts 16 + 6 = 22 of 30. Tokens per run in `results.md` and each `meta.json`: 110,673 input and 5,974 output in total. No credential copied. "CLAUDE.md not loaded" rests on documented `--safe-mode`; no file-open trace.
- DONE: Judge AC-7 by the preregistered grader and the original bar of 5 of 6 per scenario.
  Candidate P 6 of 6 and K 6 of 6 (runs 1-3 from implementation-2 plus runs 4-6): the bar is met for both. Each cell is n=6, one model.
- DONE: Report the K grader's base false-pass as found, without changing the rubric; record the Codex half as not runnable.
  K base answers pass because a title containing "Validation ... report" plus "not re-run" satisfies the "attributed" branch while they state two cells unlabelled (`results.md`). Narrower read, not the verdict: the wrong-count limit is itself labelled in 3 of 6 K candidate runs (1, 5, 6); the other 3 label the other counts only. Codex: `codex exec --help` lists no way to skip ~/.codex/AGENTS.md.
- DONE: AC-1, AC-2, AC-4, AC-5, AC-6 and ADR 0055.
  Carried from `validation/implementation-1/`, not re-run here (this dispatch changed no product file). Product head now f79711ca8d6325c1c14781342cf23855dd62b10a, which FO moved after implementation-2; I did not re-run the suite on it.
- SKIPPED: Push, Draft PR, RoboRev, CI on the PR head.
  FO's duties; none done or claimed.
- DONE: Commit evidence to the state checkout.
  `spacedock state commit claims-name-their-source --workflow-dir <workflow>`, receipt below in the completion message.

### Summary

This supersedes the earlier `## Stage Report: implementation`. Amendment 1 now sits in the criteria as AC-7 (AC-3 withdrawn into its entry), and AC-7 is met by the preregistered grader: the candidate passed P 6 of 6 and K 6 of 6 on Claude. The K result cannot show a base-versus-candidate difference because the grader passes the base answers too; on a narrower read only 3 of 6 K candidate runs label the wrong-count limit itself, so the evidence that the rule changes K behavior is weaker than 6 of 6 suggests, while P is clean. The product-level checks were not re-run on the new head f79711ca8.

## Stage Report: validation

- DONE: Independent verdict on PR #777 head f79711ca against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  **REJECTED pending F1/F2 disposition**, at `f79711ca8d6325c1c14781342cf23855dd62b10a`; evidence: `claims-name-their-source/validation/validation-1/details.md`, criteria.json, findings.json and manifest.json (commands run 2026-11-04 Asia/Taipei).
  AC-1/4 pass: repository lint 5891/5891; removing the +55 ledger or changing the chat phrase fails lint. AC-2 passes exit 0/1/2 fixtures; removing check's emit fails only its test, while question stays green.
  AC-5 independently recounts stacked-parent startup 5836+48 to 5891+48, question 3 to 30 and check 57 to 84; unchanged idle/archive/ideation sources and a deleted-rule count falsifier are retained.
  AC-6 passes the exact-head full discovery command: 892 tests, six skips, exit 0; missing required ADR 0055 fails its copied-folder falsifier. No candidate product bytes were repaired.
- DONE: Captain amendment 1 superseded AC-3 with AC-7 (Claude only, 6 candidate runs per scenario, the original 5 of 6 bar, the Codex half not runnable on this machine). Judge AC-7 from validation/implementation-2 and implementation-3, including the reported K grader base false-pass and the narrower read that 3 of 6 K candidate answers label the wrong count; the head moved to f79711ca8 by a forward merge of #773, so rerun the suite and the other criteria here. Do not start agents you were not asked to
  Regrading frozen outputs reproduces P 6/6 and K 6/6, base P 1/3 and K 3/3. Prompt hashes, raw answers, frozen inputs and candidate workflow hash agree; original/corrected falsifiers rerun unchanged. A title-only wrong-count counterexample false-passes (replay-audit.json).
  Independent target-claim read agrees with implementation: only K runs 1/5/6 label the disputed limit; 2/3/4 label other counts (semantic-read.json). This does not replace the fixed grader; F1 holds the claim that its score proves the accepted behavior. No agents or new provider runs started; stored attempts remain 22/30.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  `validation/validation-1/acceptance.sh` has six exact steps, expectations and cleanup; unchanged bytes ran with `/bin/bash --noprofile --norc`, exit 0, full output in acceptance.log. It reproduces both holds; exit 0 is not delivery acceptance.
  Required .claude ADR lint with `--since origin/main --require 0055` exits 0: 52 records, 0 legacy. Active .codex package agrees; number guard, design/dispatch checks, document dispositions and comment ratio are recorded in checks.json and details.md.
- FAILED: Required number-guard check against the assigned origin/main base.
  `number_guards.py check --base origin/main --head f79711ca8...` exits 1 on parent ADR 0054; the same exact candidate checked against stacked parent `128fe3e3fed70fa64ded8657f5a1b36933af3ced` exits 0. Parent PR #773 is open and owns that reservation; no base or task reservation was changed.
- DONE: Judge disclosed limits and preserve independent evidence.
  Safe-mode isolation rests on documented help, not a file-open trace; one model, small samples, combined README/reminder in K, incorrect-but-attributed reports and daily FO behavior remain limits. Eight document dispositions checked; comment ratio 0.2% within 5%; no CI trigger changed and CI cost per PR not measured.
- SKIPPED: Product repair, rubric change, new model replay, review requests, PR comments, marking ready, code push and merge.
  FO retains disposition, review and delivery authority. Active-skill dispatch check passes five records; older .claude completion-grammar drift is retained as a diagnostic, not five missing handoffs.

### Summary

The exact candidate passes its structural, local caller and word-count checks; the full suite and fresh-shell script were rerun after the parent merge. The unchanged grader's mechanical pass cannot establish the count-scenario target behavior, and the explicitly assigned trunk number check is red, so this validation recommends REJECTED pending the two dispositions below.

- F1 Needs decision: K's fixed grader false-passes the base and a title-only wrong-count control; the target limit is labelled in only 3/6 candidate answers against the retained 5/6 bar (`value-ac[AC-7]`). FO must route this evidence discrepancy for a recorded Captain disposition before repair or another replay; four evidence fields and trigger sources are in findings.json.
- F2 Needs decision: `contract[kc-dev-flow-2/references/sd/workflow.md#number-guards]` is held at the required `origin/main` comparison by the still-open stacked parent's ADR 0054. FO must reconcile the comparison/delivery sequence without cross-owning that reservation; passing the parent-based control does not erase the required failure.

## Stage Report: implementation

- DONE: Move Captain amendment 3 into `## Acceptance criteria`: replace AC-7 with AC-8 carrying "Amended by Captain, amendment 3" and his ruling's words only.
  AC-7's block moved verbatim under Amendment 3's `Superseded text:`; AC-8 carries the label plus the words of his Asked line, nothing else. `design_surfaces.py check claims-name-their-source.md` printed "design surfaces presentable", exit 0 (2026-11-04). Form fix: the checker reads `Superseded text:` only alone on its line, so Amendment 1 and 3 entries (previously inline) now put the block on the next line; before that fix the check exited 1 on amendment 1's missing replacement.
- DONE: Judge AC-8 from the existing implementation-2 and implementation-3 evidence, no new replay.
  Recounted from the `meta.json` files (2026-11-04): P candidate 6 of 6 against P base 1 of 3 (preregistered grader). K candidate 6 of 6 and K base 3 of 3 by the grader, which cannot separate them (known defect, `implementation-3/results.md`). On the narrower read, the wrong-count limit is labelled in 3 of 6 K candidate runs (1, 5, 6) against 0 of 3 base; this 3 of 6 is the known limit his ruling names, read by me from the answers, not graded by script. No provider call was made this round.
- DONE: Record that Captain amendment 2 rules the stacked-parent comparison.
  Amendment 2 (「可以」, 2026-11-04, answering the stacked-PR question for #775 and #777): judge the number guards against PR #773's head now and against origin/main after #773 merges. I ran no number-guard check this round and claim no result for either comparison; the last recorded number-guard run is `validation/implementation-1/number-guards-final.log`, bound to the earlier head.
- DONE: No product change; the head stays f79711ca8d6325c1c14781342cf23855dd62b10a.
  `git rev-parse HEAD` and `git status --short` on the worktree: head unchanged, clean (2026-11-04).
- SKIPPED: The follow-up task for numbers with sources, push, Draft PR, RoboRev, CI.
  The Captain's ruling asks for the tracking task; opening it and publication are FO's, not done or claimed here.
- DONE: AC-1, AC-2, AC-4, AC-5, AC-6 and ADR 0055.
  Carried from `validation/implementation-1/`; not re-run on f79711ca8.

### Summary

This supersedes the earlier `## Stage Report: implementation`. AC-7 is withdrawn into Amendment 3 and AC-8 (ship as is, K 3 of 6 recorded as a known limit, a follow-up task for numbers) now stands in the criteria, with the amendment form clean under `design_surfaces.py check`. The evidence reads P 6 of 6 against base 1 of 3, and K 3 of 6 labelled at the wrong count against base 0 of 3 on my reading, the limit he accepted. The stacked-parent number-guard comparison is recorded as ruled and not yet run.

## Stage Report: validation

- DONE: Independent verdict on PR #777 head f79711ca against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  Cycle 2: **PASSED** at f79711ca8d6325c1c14781342cf23855dd62b10a under Captain amendments 2 and 3. Evidence: claims-name-their-source/validation/validation-2/details.md, criteria.json, findings.json, manifest.json; commands run 2026-11-04 Asia/Taipei.
  AC-1/4: lint 5891/5891; deleting the +55 ledger or changing the chat clause fails lint. AC-2: both entry points retain exits 0/1/2; removing only check's emit fails its assertion while question stays green.
  AC-5: independent base/candidate recount gives startup 5836+48 to 5891+48, question 3 to 30, check 57 to 84; idle/archive/ideation sources unchanged. Deleting the rule makes the +55 assertion fail.
  AC-6: full discovery exits 0 (892 tests, 6 skips); required ADR lint exits 0 and deleting ADR 0055 fails its copied-folder falsifier. Consumer search and eight document dispositions checked; comment ratio 0.2%, within 5%.
- DONE: This rerun's rulings are Captain amendment 2 (stacked PRs: judge the number guards against PR #773's head now and against origin/main after #773 merges) and Captain amendment 3 (AC-7 superseded by AC-8: ship as is, K's 3 of 6 recorded as the known limit, a follow-up task for numbers, filed as counts-name-the-run-that-produced-them). Re-judge validation-1 F1 and F2 under them and every criterion at this head. Do not start agents you were not asked to
  AC-8: read all saved target-count answers independently; candidate 1/5/6 label the disputed count, hence 3/6, base 0/3. Frozen grader still gives P 6/6, K 6/6 and base P 1/3, K 3/3; title-only wrong-count control still false-passes. No rubric change or provider run.
  Ruling history is later than validation-1; superseded criteria are withdrawn and the named follow-up is committed. Missing-follow-up/hidden-limit controls reject. F1 is settled by amendment 3; F2 passes the parent comparison under amendment 2.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  validation/validation-2/acceptance.sh has six steps and exact expectations; unchanged script ran with /bin/bash --noprofile --norc, exit 0 (acceptance.log). It verifies local output and accepted limits, not count truth, native daily behavior, external reviews or delivery.
  Dispatch-named .claude ADR command with --since origin/main --require 0055 exits 0: 52 records, 0 legacy; active skill package agrees. Seven dispatch records pass; amendment-form check passes (checks.json, extra-checks.json).
- DONE: Judge every disclosed implementation limit and preserve source evidence.
  Safe-mode isolation rests on saved help and argv, not file-open tracing; Codex remains outside the accepted replay. One model, small samples, combined README/reminder in K, incorrect-but-attributed reports and daily-FO behavior remain limits; 22 stored attempts, no new calls. No CI trigger changed; CI cost per PR not measured.
- SKIPPED: Post-parent origin/main number check, product repair, new provider replay, review requests, PR comments, marking ready, code publication and merge.
  PR #773 remains open at 128fe3e3fed70fa64ded8657f5a1b36933af3ced; the permitted parent-head number check exits 0. Current trunk diagnostic still exits 1 on parent ADR 0054. FO must fetch and recheck against origin/main after the parent merges, before delivery.

### Summary

This cycle supersedes the earlier validation verdict under the later Captain rulings; it preserves the earlier findings and evidence. All six active criteria pass at the exact candidate within the accepted limits. The full suite, falsifiers and fresh-shell script were rerun; FO retains review, gate and delivery duties.

- F1 Deferred risk (settled by Captain amendment 3): K's 3/6 and the grader false-pass are accepted under value-ac[AC-8], with the committed follow-up. They become Material if delivery claims reliable count correction or hides this limit; four evidence fields are in findings.json.
- F2 Deferred risk (future delivery prerequisite): captain-ruling[2026-11-04] permits the passing stacked-parent check now and still requires the trunk check after #773 merges. Omitting that later check would make it Material; no new Needs decision is raised.

## Stage Report: implementation

- DONE: Update docs/adr/0055-a-claim-names-its-source-and-the-gate-scripts-print-the-rule.md to the ruled proof under Captain amendments 1 and 3, quote his words verbatim, and remove "Claude and Codex, three runs per cell".
  Candidate `69f4988612d17c5524887f99c872a0ef384d05c9`, branch `spacedock-ensign/claims-name-their-source`, repair base `eb556c61a775f148fa7ae6410b5d106ff32d917c` (FO's merged-main head). Only ADR 0055 changes (`git diff --name-only <repair-base> HEAD`, 2026-11-04); no runtime, test, version or criterion edits.
  ADR 0055 quotes amendment 1's 「可以」 and amendment 3's 「甲」 with their exact Asked questions. `ruling-proof.json` compares both answers/questions with the task, confirms the superseded host/sample statement absent, and the named follow-up present (2026-11-04).
- DONE: Record Claude-only proof (claude-opus-5-5, --safe-mode), the Codex half not runnable here, P 6 of 6 against base 1 of 3, K 3 of 6 labelled against base 0 of 3 as the known limit, the K grader's base false-pass, and follow-up counts-name-the-run-that-produced-them.
  `python3 -B audit.py`, `proof-audit.json` (2026-11-04): saved model/flag records and answer hashes agree; P grader counts are 6/6 vs 1/3; K target-label counts are 3/6 vs 0/3 from validation-2's independent manual classifications. The unchanged K grader still gives 6/6 vs 3/3 by false-passing the base's title plus “not re-run”. No rubric change or new provider call.
  The ADR distinguishes the faulty mechanical score from the accepted target-claim limit, names candidate runs 1/5/6, and records the existing follow-up. It retains one-model/small-sample, combined K wording, documented safe-mode rather than file-open tracing, and daily-FO limits. No reliable count-correction claim.
- DONE: Run the ADR lint with --require 0055 and the full suite at the updated candidate.
  `adr-lint.log`: `python3 -B <package>/scripts/adr_lint.py docs/adr --since eb556c61a775f148fa7ae6410b5d106ff32d917c --require 0055` exits 0, 53 ADRs checked. `python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p 'test_*.py'` exits 0: 906 tests, 6 skips (`full-suite.log`, 2026-11-04). Commands ran 2026-11-04; package is the active skill root, `/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0`.
- DONE: Recheck the post-parent number guard, comment ratio and affected-document list.
  `number-guards.log`: `number_guards.py check --base origin/main --head HEAD` exits 0, bound to main `2bda2e98304261d46b0ae7205a29ddc9038d2b4d` and the candidate. `comment-ratio.log`: 0 code/0 comment lines; maximum not enforced below its code-line floor, exit 0. `doc-impact.txt`: 0 documents mention the changed ADR, exit 0.
- DONE: Commit locally and prepare an updated PR body stating the narrowed proof; append a complete implementation report with the new head.
  Local commit is the candidate above. Exact title/body: `claims-name-their-source/validation/implementation-1-message-1/pr-title.txt` and `pr-body.md`; report, commands and source hash in the same folder. Task frontmatter and Captain amendments unchanged by this worker.
- DONE: Preserve the already implemented source rule, approved budget ledger, reminder outputs and observer boundary.
  Carried implementation and validation evidence remains in implementation-1, implementation-2/3 and validation-2; this repair changes only the retained decision record. New full discovery checks callers at the current candidate; historical replay outputs are audited, not regenerated.
- SKIPPED: Product push, PR #777 update, exact-head RoboRev, fresh independent validation and hosted CI.
  FO owns these steps under the existing dispatch. No PR comment, review request, ready or merge action. CI cost per PR is not measured; no CI trigger changed. This report grants no delivery approval.

### Summary

This complete report supersedes earlier implementation reports for the current candidate. ADR 0055 and the prepared PR body now state the Captain's narrowed Claude-only proof and accepted K 3-of-6 limit with the grader false-pass and named follow-up visible. The required local checks pass; FO retains fresh validation, review and delivery.

## Stage Report: validation

- DONE: Independent verdict on PR #777 head 69f49886 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  Cycle 3: **PASSED** at `69f4988612d17c5524887f99c872a0ef384d05c9`, within Captain amendments 2 and 3. Commands run 2026-11-04 Asia/Taipei; evidence: `claims-name-their-source/validation/validation-3/details.md`, criteria.json, checks.json, extra-checks.json and manifest.json.
  AC-1/4: lint exits 0 at 5891/5891; removing the +55 ledger or changing the chat phrase fails lint. AC-2: both entry tests retain exits 0/1/2; removing check's emit fails that test while the question control stays green.
  AC-5: independent recount against fetched main gives startup 5836+48 to 5891+48, question 3 to 30, check 57 to 84; idle/archive/ideation source bytes unchanged. Deleting the rule defeats the +55 assertion (prove.py, word-counts.json, count-falsifier.json).
  AC-6: `python3 -m unittest discover -s kc-dev-flow-2/scripts -p 'test_*.py'` exits 0: 906 tests, 6 skips (full-suite.log, suite-result.json). Removing reserved ADR 0055 from a copied folder makes its required-record check fail.
- DONE: Revalidation after #773 merged: #777 was retargeted to main, origin/main merged in, and ADR 0055 updated to the ruled proof (head 69f498861). Under Captain amendment 2, run the number guards against origin/main now that the parent has merged; re-judge AC-8 under Captain amendment 3 and every criterion at this head. Do not start agents you were not asked to
  Read-only GitHub receipts confirm parent #773 merged and #777 targets main at the assigned head. `number_guards.py check --base origin/main --head 69f4988612d17c5524887f99c872a0ef384d05c9` exits 0, base `2bda2e98304261d46b0ae7205a29ddc9038d2b4d` (number-guards-trunk.log); prior F2 is resolved.
  AC-8: unchanged grader and saved-source audits rerun; independently read every target answer. P is 6/6 against base 1/3; the K target count is labelled in candidate 1/5/6, hence 3/6 against base 0/3 (semantic-read.json). Old K grading remains 6/6 against 3/3 and the title-only wrong-count control false-passes (replay-audit.json).
  ADR 0055 quotes amendments 1/3 verbatim and names the known limit and committed numeric-source follow-up. Hidden-limit, missing-follow-up and changed-ruling controls reject (accepted-state.log, retained-record.log). PR body discloses the same limits (pr-disclosure.json). No new provider calls or agents; stored attempts remain 22/30.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  `validation/validation-3/acceptance.sh` has six exact steps and expectations. Unchanged bytes ran under `/bin/bash --noprofile --norc`, exit 0 (acceptance-rerun.log, script hash in acceptance-result.json). Initial sandbox worktree creation failed; approved filesystem retry passed and cleaned up.
  Dispatch-named .claude ADR lint with `--since origin/main --require 0055` exits 0: 53 records, 0 legacy (adr-lint-dispatch-package.log); active .codex package agrees. Design form and dispatch checks pass; nine dispatch records complete with two nonblocking absent-Symptom advisories.
- DONE: Judge every disclosed implementation limit and affected document.
  Document-impact lists eight documents; each retained disposition was independently checked. Comment ratio is 0.0% (57 code lines, 0 comment lines), within 5%; output consumer search finds no non-test parser of these gate modes (doc-dispositions.json, comment-ratio.log, delivery-callers.log). No CI trigger changed; CI cost per PR not measured.
  Safe-mode isolation rests on documented help/recorded argv, not file-open tracing; Codex is outside the ruled replay. One model, small samples, combined README/reminder in K, incorrect-but-attributed reports and daily-FO behavior remain limits. The acceptance script proves local output and retained records, not model reliability or delivery.
- DONE: Preserve candidate bytes and remove disposable validation worktrees.
  Assigned branch remains clean at the exact candidate; detached validation and acceptance checkouts removed (cleanup.json). No candidate repair or unrelated task edit.
- SKIPPED: State-syncing helper, push, PR edits/comments, review requests, ready, merge and new behavioral replay.
  The dispatch's explicit no-push rule overrides generic state-sync text. Report and evidence use a path-scoped local state commit; the First Officer retains synchronization, reviews, gate and delivery. No new provider run was required by AC-8.

### Summary

This cycle supersedes validation-2 for the current candidate. All six active criteria pass under the later Captain rulings; the required post-parent trunk check, fresh-shell acceptance and full suite now pass at the updated head. The bounded rule remains a source-attribution instruction, not proof of reliable count correction; delivery remains with the First Officer and Captain.

- F1 Deferred risk (accepted by Captain amendment 3): K target attribution is 3/6 and the unchanged grader false-passes the base; `value-ac[AC-8]` accepts this limit and its committed follow-up. Four evidence fields are in findings.json. It becomes Material if delivery claims reliable count correction or hides the accepted limit; no new Needs decision is raised.
