---
title: A factual claim in a question FO puts to the Captain has been checked against the record before he reads it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:gate-question-facts-are-checked-before-the-captain-reads-them:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:gate-question-facts-are-checked-before-the-captain-reads-them-backlog-1
              briefing:
                id: briefing:gate-question-facts-are-checked-before-the-captain-reads-them:backlog:attempt-1:revision-1
                digest: sha256:ab7abf3920dd5c06228fc87eabeee3a493b7bb32aea8b905da77f71bffdcd594
                room-ref: ./gate-question-facts-are-checked-before-the-captain-reads-them/review/backlog/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-11-12T05:11:42.508362Z"
                reason: The Captain answered the joint question with a change to the experiment instead of a decision (host question dialog, 2026-11-12); FO asks again with the experiment written into the question.
            - id: gate-attempt:gate-question-facts-are-checked-before-the-captain-reads-them-backlog-2
              briefing:
                id: briefing:gate-question-facts-are-checked-before-the-captain-reads-them:backlog:attempt-2:revision-1
                digest: sha256:e7c2ec3f8a86e3421463c2cdb688b335db038471b38756669febb492c3efccb8
                room-ref: ./gate-question-facts-are-checked-before-the-captain-reads-them/review/backlog/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:gate-question-facts-are-checked-before-the-captain-reads-them:backlog:2
                briefing: briefing:gate-question-facts-are-checked-before-the-captain-reads-them:backlog:attempt-2:revision-1
                by: person:captain
                at: "2026-11-12T05:15:55.668181Z"
                decision: approve
                reason: 'The Captain chose 「核准，照這個分組（建議）」 (host question dialog, 2026-11-12), answering 「決定：這五張新任務要不要都進設計階段，並照你說的做成對照實驗。我建議核准。五張是：一、合併前在合併後的結果上跑測試；二、被你擱置或關掉的任務不再像在排隊；三、每張任務記錄階段時間、重做、打斷次數；四、派工結束封存證據、刪掉暫存；五、我問你的問題裡的事實先對過紀錄。實驗分兩組：第三、五、一張的設計階段照你的說法，等於「試作加擴大計畫」，設計工人先在不推送的分支上把東西真的做出一個能跑的試作、拿真實案例跑過，再寫擴大成正式版本還要補什麼，實作工人從那個試作接著做；第二、四張的設計階段只要求把每條驗收條件的證明實際跑一次，不寫試作。對照基準是過去兩週的 67 張。核准代表接受各任務檔寫的範圍、預算（每階段一輪、一個 PR）與停止條件。不代表接受任何設計或修法。哪張進哪一組是我挑的，不是隨機：試作組放的是證據最難產生或最大的三張。五張合起來我沒有把握一天做完，超過時我連同預算回來請你取捨。」. Recommendation: followed. The experiment is his: before this question he answered the first form of it with 「我想要做一個實驗，比較一下，有幾張的構思階段就是包含實作poc，你說構思完全沒有先試驗過測試過，所以我想加過這一段試試看是否就會改善，等於構思等於poc加擴大計畫」 (same dialog), and FO withdrew and re-asked.'
              application:
                target-stage: ideation
                state: consumed
started: 2026-11-12T05:16:48Z
---

## Scope

- Source: FO's own misses, filed by FO with no Captain ruling yet; the backlog gate confirms it.
- Bite, three times in two days, each found after the Captain had answered: the #843 merge ask said already-filed tasks would not be asked to add a Story line, while the approved design has the idle look name them (observer report, 2026-11-11); the #841 merge ask said only designs not yet through the design gate would be refused, while release 0.39.0 refused approved ones and an adopter found it after release (2026-11-11); a question of 2026-11-12 described five tasks as waiting in design when the Captain had held or closed all five.
- What exists: the delivery check counts unchecked numbers in gate text and the workflow says each claim names the command and date that produced it; none of the three claims was a number, and the check passed each time.
- Outcome: a sentence in a gate or decision question that says what a change does or what state a task is in either names the record or run that shows it, or is marked as unverified where the Captain reads it.
- Open for the design: whether this can be checked at all by a script, or is a step with a record; what the cheapest version is that would have caught the three cases; what it costs FO per question in words and minutes.
- Non-goals: checking the Captain's own words; a second reviewer for every question; rewriting the question form.

## Budget
1 cycle per stage, in one package PR.

## Stop condition
- Replaying the three questions named under Bite at their recorded state, the candidate flags each false sentence, and three questions that were true are not flagged. Return to the Captain if the design finds no mechanism cheaper than a second agent reading every question.

## FO alignment

Alignment: not needed: one observed defect with one outcome; whether and how it can be checked is compared in the design and ruled at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Design

Proof-of-concept branch: `poc/gate-question-facts-are-checked-before-the-captain-reads-them`, commit `e56b2e6c36f846349acc780175a0691b63a177ae` (parent `39fb7ccfa`, base origin/main `8ce0eb605`), local only, in the workflow checkout's `.worktrees/poc-gate-question-facts`. It adds one throwaway file, `kc-dev-flow-2/scripts/gate_facts.py`, with three readers: `state`, `effect` (one model call per sentence) and `scope`. Saved runs are under `gate-question-facts-are-checked-before-the-captain-reads-them/ideation-1/`; `ideation-1/run-evidence.sh <POC worktree> <state checkout>` reruns every deterministic criterion in about 5 seconds.

### PRFAQ

**Proposition.** When FO's merge ask or gate question tells the Captain that a change does or does not affect existing tasks, designs or records, the sentence either names the saved run in the task folder that shows it, or the delivery check itself writes 「（未對過紀錄）」 after it in the text he reads. A task FO offers him as waiting work is not one he has held or closed, because the listing FO chooses work from no longer shows held tasks (owned by held-and-closed-tasks-leave-the-design-queue).

- **Why not let a model read every question against the record?** It was measured and it failed (below): it missed both false merge-ask sentences and flagged true ones.
- **Why mark instead of hold?** ADR 0072 is the nearest ruling: the Captain replaced a gate hold with a disclosure the tool writes itself. ADR 0055 and ADR 0027 D4 rejected holds that match words, because matching words cannot stop this class of error. A mark makes the claim visible as unchecked; it does not make it true.
- **What does FO pay?** On the 111 questions FO asked in this session (2026-11-10 to 2026-11-12), 11 of 505 sentences in 9 questions are existing-item sentences. Each needs a cited saved run or carries the mark.

```mermaid
flowchart TD
  Q[FO drafts a merge ask or gate question] --> C{delivery_gate.py check or question}
  C --> S[scan Chinese and English sentences for existing-item effect claims]
  S -->|none| P[text unchanged; exit as today]
  S -->|claim cites a saved file in the task folder that exists| P
  S -->|claim uncited or citing a missing file| M[tool writes 「（未對過紀錄）」 after it and prints the line; exit as today]
  M --> R[Captain reads the marked sentence]
  P --> R
  W[FO chooses work to offer] --> L{listing FO chooses from}
  L -->|held or closed task| X[not listed: held-and-closed task]
  L -->|waiting task| O[offered to the Captain]
```

### What the proof of concept showed

The six questions are saved verbatim in `ideation-1/questions/`, each with its ask time and the state commit before it. Each run reads records only at that commit through `git show`. False: case1-843 (2026-11-11T07:48Z), case2-841 (08:55Z) and case3-five-tasks (2026-11-12T03:06Z). True controls of the same kinds: control-839 and control-849 (merge asks), and control-five-new-tasks (the 04:59Z question on the five new tasks).

- **Task state is mechanical.** At `c59bfffd6` all five tasks case 3 offered carry a Captain `hold` at ideation (dated 2026-10-21 to 2026-11-05). `state` flags 5 of 5 and exits 1. On the control at `2c60d50f3` it flags 0 of 5 and exits 0 (`evidence/ac1-*.log`).
- **Both false merge-ask sentences are contradicted by a saved record. Neither is merely unsupported.** Case 1: AC-13 of the approved design says "The idle look names a backlog task with no story record, and on the replays it names 31 relay and 11 qnow tasks". Case 2: `validation-2/legacy-design.json` shows the candidate refusing an old design with "stage is validation, not ideation". So the run that would have shown the truth existed in each task folder.
- **A model reading the extracted record does not catch them** (`runs/effect-*.json`, prompt in `gate_facts.py` PROMPT, raw output saved per call). Haiku, 3 runs: case 1's false sentence was flagged 0 of 3 times and case 2's 1 of 3. A true sentence was flagged 3 of 3 in each of control-839 and control-849, and a true limit in case 2 was flagged 3 of 3. Sonnet, 1 run: it called both false sentences SUPPORTED and flagged one true control sentence. Each call took 4.5–12 s and read 4.8k–7.6k input tokens. This rules out the second-reader route at this cost.
- **A deterministic existing-item scan marks exactly the false sentence in cases 1 and 2**, and nothing in control-839. It also marks one true sentence in control-849: the PR's own title, which cites nothing. With the task's saved replay cited (`validation/acceptance-result.json`), control-849 passes. A cited file absent from the folder is still marked.
- **On the whole session corpus**, the scan marks 11 sentences, and 4 of them are false. The fourth false one was not named in the Bite: the 10:23Z release question repeated case 2's claim. The other 7 describe the #849 fix itself. Corpus, run and labels: `questions/corpus-fo-session-8fcbee7d.jsonl`, `evidence/ac3-corpus.log`.
- **The existing count disclosure is blind to these questions.** `count_tokens.count_sentences` finds 0 count sentences in all 111 Chinese questions, including case 2's 「15 個同類檢查漏洞」 (`evidence/count-scan-on-chinese-questions.log`). The Scope's "What exists" check never reads what the Captain reads in the dialog.

### Existing-code check and chain

- **Spacedock 0.27.2:** `gate prepare` takes `--question`, `--summary` and `--reference` and checks no claim (`spacedock gate prepare --help`, 2026-11-12). Nothing to reuse.
- **kc-dev-flow-2 0.39.1 at origin/main `8ce0eb605`:** `delivery_gate.py` prints `CLAIM_SOURCE` (ADR 0055), and `count_disclosure` writes `Unchecked counts: N` (ADR 0072) in both `check` and `question`. That disclosure is the seam to extend: the same place, the same no-hold rule, the same "cites a file resolving within the task folder" test. A replacement is not needed.
- **Adopters:** relay, web and qnow use the same `delivery_gate.py`. Reading qnow's FO question history was refused by this session's permission classifier, so no adopter corpus was read.

### Expansion plan (POC to Pilot)

1. Move the scan into `delivery_gate.py` beside `count_disclosure`, using `count_tokens.prose_lines` and a sentence split that also splits on 。；？ and 一、…十、. It runs in `check` (ask text plus PR body) and in `question` (question plus summary). It writes 「（未對過紀錄）」 after each uncited existing-item sentence in the file FO passes, and prints `scope claims: N cited, M marked` plus one line per marked sentence. It prints nothing when no such sentence exists, and adds no new hold or exit code.
2. A citation counts only if it names a file that resolves inside the task folder, the same rule as `named_file` in `count_problems`. Reuse that, not the POC's `git show`.
3. Make the existing count scan see Chinese sentences, through the same split. Today it finds none (above). Units such as 張, 個, 次 and 項 join `NOUN`.
4. Drop the PyYAML dependency and the model reader. The state reader goes no further than a replay test against held-and-closed's listing (D2).
5. Tests in `test_delivery_gate.py` use the saved fixtures, with the three falsifiers in `run-evidence.sh` as mutants. Write an ADR draft extending ADR 0072: "existing-item effect claims cite saved output or carry the tool's mark".

The Stop condition's first clause is met for cases 1 and 2 by the scan, and for case 3 by the state reader on the POC. Its second clause is met for 2 of 3 controls on recorded text. control-849 is marked once, on a true but uncited sentence, and passes once its saved run is cited. Its return clause does not fire: the mechanism found costs no model call and about 1 s per corpus pass, not a second agent.

### Worth questions

- **Existing-item scan and tool mark (merge ask, gate question).**
  - Serves: the Scope's Outcome and Bite, FO's filing confirmed by the Captain's backlog approval 「核准，照這個分組（建議）」.
  - Without it: the three-time miss stays invisible. The count disclosure reads no Chinese sentence, so nothing marks the sentence that misled him (evidence above).
  - Premise that would make it unneeded: "FO would have noticed by citing a run". A cheap check now: in both cases the contradicting saved record already existed in the task folder, and FO still wrote the false sentence. The premise is false.
- **Count scan reading Chinese (expansion item 3).**
  - Serves: the Scope's "What exists" sentence, which assumes the count check runs on these questions.
  - Without it: numbers in every Chinese question stay unchecked (0 of 111 found).
  - This part serves no Captain words directly. It is for the Captain to keep or cut.
- **Task-state check (case 3).**
  - Serves: the Bite's third case.
  - Without it here: nothing, if held-and-closed ships its listing. Its Stop condition removes the 10 held tasks from the command FO uses to choose work.
  - Premise that would make it unneeded: held-and-closed lands. Check held-and-closed's design at its gate.

### Words FO reads at each moment

Base, from origin/main `8ce0eb605`: the workflow.md merge and gate passage is 80 words, and `CLAIM_SOURCE` printed on each call is 27 (`ideation-1/words/word-counts.txt`, `wc -w`).

| Moment | Base | Candidate |
| --- | --- | --- |
| Startup, idle on an open PR, idle on a merged PR, after the archive | unchanged | unchanged: no README or mod text is added |
| Merge ask (`check`) and gate question (`question`), no existing-item sentence | 27 printed | +0 |
| Same, with a marked sentence | 27 printed | +6 words for the `scope claims:` line, plus 2 words and up to 12 of the sentence for each marked sentence |

Measured rate: 9 of 111 questions would print the line. The candidate rises above base only at those calls. This task does not aim to cut words.

### Decisions for the Captain

- **D1, how an existing-item sentence is checked.** Recommended: the tool writes 「（未對過紀錄）」 itself and nothing is held, following ADR 0072's ruling and ADR 0055 / ADR 0027 D4.
  - Alternatives: a hold until FO cites or marks it, which those rulings rejected; or a model reader, measured above at 1 of 6 catches and repeated false flags.
  - Worse under the recommendation: a false sentence still reaches you, marked. In two days 7 of the 11 marks fell on true sentences. The word list was tuned on these same two days, and a false claim worded without 舊/已開/既有-type words passes unmarked.
- **D2, who owns case 3.** Recommended: held-and-closed-tasks-leave-the-design-queue owns it. This task adds no state check and only replays case 3 against that task's listing at implementation.
  - Alternative: this task ships the state reader for a question that names task slugs.
  - Worse under the recommendation: a plain dialog question has no script on its path, so a state claim FO writes without consulting the listing stays unchecked. This task's Stop condition for case 3 then depends on another task landing first.

## Acceptance criteria

Every evidence command below was run once on 2026-11-12 (Asia/Taipei 13:34) at POC commit `e56b2e6c3`, through `bash ideation-1/run-evidence.sh <POC worktree> <state checkout>`. That script records the head in `ideation-1/evidence/identity.txt` and writes `ideation-1/evidence/<name>.log`, each log ending with its exit code. `<gf>` below is `<POC worktree>/kc-dev-flow-2/scripts/gate_facts.py`, and `Q` is `ideation-1/questions`. At implementation, the same fixtures are replayed against the candidate's `delivery_gate.py`. For AC-1, they are replayed against the listing held-and-closed ships, per D2.

**AC-1** — Task-state replay. Case 3's question, read at state `c59bfffd6`, flags all five offered tasks as held. The control question at `2c60d50f3` flags none.
- Evidence: `python3 -B <gf> state --state <state> --question Q/case3-five-tasks.json` exits 1 with `5 of 5 tasks flagged` (`evidence/ac1-case3.log`). The same command on `Q/control-five-new-tasks.json` exits 0 with `0 of 5` (`evidence/ac1-control.log`).
- Falsifier: dropping `hold` from the stop decisions makes case 3 exit 0 (`evidence/falsifier-ac1-no-hold.log`, exit 0).

**AC-2** — Existing-item scan on the recorded false merge asks. Each recorded question gets exactly one marked sentence, and it is the false one: case 1's 「已經開好的舊任務不會被要求補標」 and case 2's 「升級後，還沒過設計關卡…的舊設計會被擋下」.
- Evidence: `python3 -B <gf> scope --state <state> --question Q/case1-843.json` exits 1 (`evidence/ac2-scope-case1-843.log`). The same command on `Q/case2-841.json` exits 1 (`evidence/ac2-scope-case2-841.log`).
- Falsifier: an English-only trigger (`existing`) leaves case 1 unmarked, exit 0 (`evidence/falsifier-ac2-english-only.log`).

**AC-3** — Controls, citation and mark.
- control-839 is not marked: exit 0 (`evidence/ac2-scope-control-839.log`).
- control-849 as recorded marks its one uncited title sentence: exit 1 (`evidence/ac2-scope-control-849.log`).
- control-849 with that sentence citing its task's saved `validation/acceptance-result.json` passes: exit 0 (`evidence/ac2-scope-control-849-cited.log`).
- Citing a file absent from the task folder at that state is still marked: exit 1 (`evidence/ac2-scope-control-849-badcite.log`).
- Case 2's sentence carrying 「（未驗證）」 passes: exit 0 (`evidence/ac2-scope-case2-841-marked.log`).
- Falsifier: accepting any cited name without checking that the file exists lets the bad citation pass, exit 0 (`evidence/falsifier-ac2-no-exists.log`).

**AC-4** — Cost on the session corpus. The scan reads 111 questions with 505 sentences and finds 11 existing-item sentences in 9 questions. The 4 false ones among them (07:48Z, 08:52Z, 08:55Z, 10:23Z on 2026-11-11) are all marked.
- Evidence: `python3 -B <gf> scope --question Q/corpus-fo-session-8fcbee7d.jsonl` exits 1, and its last line reads `scope: 111 questions, 505 sentences, 11 existing-item sentences, 9 questions flagged` (`evidence/ac3-corpus.log`). The falsity labels come from case 1's AC-13 and case 2's `validation-2/legacy-design.json`; the 10:23Z sentence repeats case 2.
- Falsifier: the english-only mutant above marks none of the four.

### Not provable now

- The tool writing 「（未對過紀錄）」 into the text file in `delivery_gate.py check` and `question`, with exit codes unchanged. There is no candidate yet; the implementation proves it with the fixtures above.
- The scan on a second corpus. Reading qnow FO's question history was refused by this session's permission classifier on 2026-11-12, and the word list was tuned on the same two days it was measured on.
- Whether a marked sentence changes the Captain's answer. This is behaviour, observable only in use.
- Case 3 on a plain dialog question. No script runs on that path; the fix lives in held-and-closed's listing (D2).
- The model reader as a criterion. A model call is neither deterministic nor free of machine dependency (CLI login). Its measured runs are decision evidence, not a criterion.

### Batch overlap

- **merge-ask-tests-the-merge-result:** likely changes `kc-dev-flow-2/scripts/delivery_gate.py` `check` (merge-ask hold) and `test_delivery_gate.py`, the same files this design changes (`count_disclosure` neighbourhood, `count_tokens.py`).
- **held-and-closed-tasks-leave-the-design-queue:** owns the listing case 3 depends on (D2). No shared file unless it chooses `pr_watch.py` or a state reader this task would replay.
- **each-task-records-stage-time-revises-and-interruptions, dispatch-close-out-archives-evidence-and-removes-scratch:** no shared file found in their current task files.
- **comment-check-reaches-delivery-gate** (held): its design changes `delivery_gate.py check` and `test_delivery_gate.py`.
- **adoption-asks-which-extensions** (held): names `delivery_gate.py` four times in its design.
- **adr-required-statement, ops-inbox-r1-setup-and-isolation, adr-silent-undo-probe, journey-canvas-hosted-poc:** they touch `design_surfaces.py` or `number_guards.py`, not files this design changes.
- **pr-review-lite-value-pilot:** no shared file found.
- **journey-server-host-pilot:** not a live task file in this state at `eae5ea47c`.
- **ADR list:** one ADR draft extending ADR 0072. Its number is reserved by FO at dispatch, so it shares the index with every task that lands an ADR.

Recommended order: held-and-closed-tasks-leave-the-design-queue first (it owns case 3), merge-ask-tests-the-merge-result before this task (both edit `delivery_gate.py check`; this task rebases onto it), then this task.

## Stage Report: ideation

- DONE: The Captain's experiment for this task (his words are in the task's backlog gate record): ideation is a proof of concept plus an expansion plan. First build a working throwaway proof of concept of this task's outcome on a local branch poc/gate-question-facts-are-checked-before-the-captain-reads-them in a worktree you create under the workflow checkout's .worktrees/ from origin/main, commit it locally, never push it and open no PR; run it against the real cases the task's Bite names and save what it showed in the task folder. Then write the design as what the proof of concept showed, the expansion plan (what it lacks to meet the Pilot bar and the task's Stop condition), and the acceptance criteria. Record the branch name and commit in the design so the implementation worker can start from it. For every acceptance criterion, run its evidence command or procedure once now and write beside the criterion the exact command, its exit and the path of its saved output in the task folder; a criterion whose proof cannot be run now is not written under Acceptance criteria but under a 'Not provable now' list with the reason, for the Captain to see at the design gate, run on the proof of concept
  Branch poc/gate-question-facts-are-checked-before-the-captain-reads-them at e56b2e6c3 (local, `--no-track`, unpushed, no PR) in `.worktrees/poc-gate-question-facts`. All three Bite cases plus three true controls were replayed at pinned state commits. The runs, fixtures and `run-evidence.sh` are in `ideation-1/`, and 5 items are listed under Not provable now.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (merge-ask-tests-the-merge-result, held-and-closed-tasks-leave-the-design-queue, each-task-records-stage-time-revises-and-interruptions, dispatch-close-out-archives-evidence-and-removes-scratch, gate-question-facts-are-checked-before-the-captain-reads-them) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Shared `delivery_gate.py check` with merge-ask-tests-the-merge-result, comment-check-reaches-delivery-gate and adoption-asks-which-extensions. Case 3 depends on held-and-closed. Recommended order: held-and-closed first, then merge-ask, then this task.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  `### Words FO reads at each moment`: +0 at startup, idle and archive, and +0 at the merge ask and gate question unless a sentence is marked. A marked call adds 6 words plus 2 and up to 12 per marked sentence; 9 of 111 questions would mark. Counts are in `ideation-1/words/word-counts.txt`.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1: `evidence/ac1-case3.log` exit 1 (5 of 5 held), `ac1-control.log` exit 0; falsifier-ac1-no-hold exit 0.
  AC-2: `ac2-scope-case1-843.log` and `ac2-scope-case2-841.log` exit 1, each on the false sentence only; falsifier-ac2-english-only exit 0.
  AC-3: control-839 exit 0; control-849 exit 1 (one true, uncited sentence); cited exit 0; badcite exit 1; marked exit 0; falsifier-ac2-no-exists exit 0.
  AC-4: `ac3-corpus.log` exit 1, with 11 sentences in 9 of 111 questions, all 4 false ones marked.
  D1 (mark, no hold; follows ADR 0072 and ADR 0055 / ADR 0027 D4) and D2 (case 3 owned by held-and-closed) each state what gets worse. `design_surfaces.py check` exit 0, "design surfaces presentable" (`evidence/design-surfaces-check.log`).

### Summary

The proof of concept shows that a task-state claim is checkable mechanically: case 3 flags 5 of 5 held tasks, and the control flags 0. A model reading the record does not catch the false merge-ask sentences: haiku caught 1 of 6, sonnet 0 of 2, and both flagged true sentences. A deterministic scan for sentences about existing items, with a cited saved file or a tool-written 「（未對過紀錄）」, marks both false sentences, all 4 false ones in two days of questions, and one true but uncited control sentence.

It also found that the existing count disclosure reads no Chinese sentence: 0 of 111 questions. The design therefore extends that seam, marking without a hold per ADR 0072, and leaves case 3 to held-and-closed.

Timing (Asia/Taipei): the proof of concept ran 13:23:51 to about 13:34 (about 11 minutes, including the model runs and evidence script). The design and report ran about 13:34 to 13:38 (about 4 minutes), after about 6 minutes of orientation from 13:17:46.
