---
title: A task the Captain held or closed at a gate no longer looks like work waiting in that stage
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:held-and-closed-tasks-leave-the-design-queue:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:held-and-closed-tasks-leave-the-design-queue-backlog-1
              briefing:
                id: briefing:held-and-closed-tasks-leave-the-design-queue:backlog:attempt-1:revision-1
                digest: sha256:cff2229580a5f7be6070bdcd4e21387458f05516df089eae064cacbff26a131d
                room-ref: ./held-and-closed-tasks-leave-the-design-queue/review/backlog/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-11-12T05:11:32.038275Z"
                reason: The Captain answered the joint question with a change to the experiment instead of a decision (host question dialog, 2026-11-12); FO asks again with the experiment written into the question.
            - id: gate-attempt:held-and-closed-tasks-leave-the-design-queue-backlog-2
              briefing:
                id: briefing:held-and-closed-tasks-leave-the-design-queue:backlog:attempt-2:revision-1
                digest: sha256:10424044da7b32efe9a970fdcd509aefc7784f284cd357eecae4d77a845c3f6c
                room-ref: ./held-and-closed-tasks-leave-the-design-queue/review/backlog/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:held-and-closed-tasks-leave-the-design-queue:backlog:2
                briefing: briefing:held-and-closed-tasks-leave-the-design-queue:backlog:attempt-2:revision-1
                by: person:captain
                at: "2026-11-12T05:15:30.832146Z"
                decision: approve
                reason: 'The Captain chose 「核准，照這個分組（建議）」 (host question dialog, 2026-11-12), answering 「決定：這五張新任務要不要都進設計階段，並照你說的做成對照實驗。我建議核准。五張是：一、合併前在合併後的結果上跑測試；二、被你擱置或關掉的任務不再像在排隊；三、每張任務記錄階段時間、重做、打斷次數；四、派工結束封存證據、刪掉暫存；五、我問你的問題裡的事實先對過紀錄。實驗分兩組：第三、五、一張的設計階段照你的說法，等於「試作加擴大計畫」，設計工人先在不推送的分支上把東西真的做出一個能跑的試作、拿真實案例跑過，再寫擴大成正式版本還要補什麼，實作工人從那個試作接著做；第二、四張的設計階段只要求把每條驗收條件的證明實際跑一次，不寫試作。對照基準是過去兩週的 67 張。核准代表接受各任務檔寫的範圍、預算（每階段一輪、一個 PR）與停止條件。不代表接受任何設計或修法。哪張進哪一組是我挑的，不是隨機：試作組放的是證據最難產生或最大的三張。五張合起來我沒有把握一天做完，超過時我連同預算回來請你取捨。」. Recommendation: followed. The experiment is his: before this question he answered the first form of it with 「我想要做一個實驗，比較一下，有幾張的構思階段就是包含實作poc，你說構思完全沒有先試驗過測試過，所以我想加過這一段試試看是否就會改善，等於構思等於poc加擴大計畫」 (same dialog), and FO withdrew and re-asked.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:held-and-closed-tasks-leave-the-design-queue:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:held-and-closed-tasks-leave-the-design-queue-ideation-1
              briefing:
                id: briefing:held-and-closed-tasks-leave-the-design-queue:ideation:attempt-1:revision-1
                digest: sha256:a3a30efc77421ed02e76aecd03cf1768a9969bd1a08a6866f4a5383ee0a13d84
                room-ref: ./held-and-closed-tasks-leave-the-design-queue/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:held-and-closed-tasks-leave-the-design-queue:ideation:1
                briefing: briefing:held-and-closed-tasks-leave-the-design-queue:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-11-12T09:24:06.453635Z"
                decision: approve
                reason: 'The Captain chose 「五份都核准（建議）」 (host question dialog, 2026-11-12), answering 「決定：實驗的五份設計要不要都核准並開始實作。我建議五份都照各自設計的建議核准。核准即接受下列各項。一、計時紀錄：「重做」算同一階段第二次以後的派工；「打斷」算我在關卡以外問你的每一題，由我在問的當下記一筆；工具只報告缺漏、不擋任務；流程說明多 25 個字。二、問題裡的事實：工具只在「說現有任務或設計會不會受影響」的句子後面自動標上「未對過紀錄」，不擋任何問題；用另一個模型判讀的做法試作證明行不通、不做；這兩天的資料上 11 個標記有 7 個標在真的句子上。三、合併後結果先測：main 的頂端不是 PR 的祖先時就要求一次測試紀錄，量到約六成的 PR 會觸發、整組測試一次約 10 分鐘（只量一次）；流程說明加一行指定要跑的指令。四、擱置的任務：啟動和閒置檢查多印一行列出擱置中的任務，每張擱置任務引你的原話寫明何時重開或已關閉；已關閉的任務留在原階段、不用強制手段歸檔；其中「進場檢查要求對齊結果」那張記為已關閉、「關卡摘要逐項寫理由」那張維持擱置、「旅程畫布託管試作」那張不動，留給它所屬的工作階段問你。五、收尾清理：每次派工有自己的暫存資料夾，結束時把報告引用的證據存進任務資料夾、超過 256 KiB 的檔才壓縮、然後刪掉暫存；私人 repo 的證據一律不存，只留一行重現指令；允許不問就強制移除暫存資料夾裡的工作目錄並記下遺失的檔案數。各設計列在「目前無法證明」的項目，到實作和驗證才會被證明。不代表接受任何尚未寫出的程式。」. Recommendation: followed.'
              application:
                target-stage: implementation
                state: pending
started: 2026-11-12T05:16:56Z
---

## Scope

- Source: FO's own miss, filed by FO with no Captain ruling yet; the backlog gate confirms it.
- Bite (FO read 2026-11-12 from gate records in this workflow's state): of 12 tasks with `status: ideation`, 10 carry a Captain `hold` or close ruling dated 2026-10-20 to 2026-11-05 and are not waiting for anything. FO offered five of them to the Captain as tasks waiting in design and he approved redispatching them before FO read the rulings; no dispatch was made. The two-week measurement of 2026-11-12 counted them as open tasks.
- Outcome: a held or closed task is told apart from a waiting one by a reader of `spacedock status` and by FO before it proposes work, and a held task states what would reopen it.
- Open for the design: whether Spacedock's own verdicts, archive or an existing field already express this (read its README and source first); whether closed tasks are archived as rejected, as two were; what happens to the 10 tasks named above.
- Non-goals: reopening or rebuilding any held task; changing what a hold ruling means.

## Budget
1 cycle per stage, in one package PR or none if the design finds an existing mechanism and only state changes are owed.

## Stop condition
- The 10 tasks are no longer listed as waiting in ideation by the command FO uses to choose work, each with its Captain ruling intact. Return to the Captain if any of the 10 needs a new ruling.

## FO alignment

Alignment: not needed: one observed defect with one outcome; the mechanism is compared in the design and ruled at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Design

Ideation evidence folder: `held-and-closed-tasks-leave-the-design-queue/ideation/` in this state checkout (state pinned at `eae5ea47cec926f35d164f8a88d31579196d7634`, package at origin/main `8ce0eb6050c889b21baccf50fec35231bc888d66`, kc-dev-flow-2 0.39.1, `spacedock 0.27.2`). The exact commands for every criterion, and the origin-less scratch recipe, are in `ideation/commands.md`.

### PRFAQ

**Proposition.** When the Captain holds or closes a task at a gate, the First Officer (FO) stops seeing it as work waiting in that stage. Every time FO runs `pr_watch.py tasks` at startup and at idle, one line names the held tasks by stage, so FO does not offer them as waiting work. Each held task carries a short `## Held` section. It quotes the Captain's own words for what reopens the task (`Reopen when:`) or that the task is closed (`Closed:`). If his words say neither, the same output tells FO to ask him. Spacedock already computes the held state, so this adds no new state field and no new stage.

**FAQ**

- *Does Spacedock already have this?* Mostly. `spacedock status` derives a `gate-readiness` value from the gate record, and a `hold` resolution reads as `not-applicable` (AC-1). The scheduler view `status --next` already leaves held tasks out (AC-2). Two things are missing. The stage listing FO used, `status --where status=ideation`, shows held tasks as plain `ideation` with no readiness column. FO's startup and idle output does not mention them at all (AC-3).
- *Why not archive the closed ones as REJECTED?* Spacedock 0.27.2 refuses every unforced close of a task whose current gate is held: `merge guard --verdict rejected`, a terminal `status --set` and `status --archive` each exit 1, and the first two name condition `not-applicable` (AC-5). No REJECTED archive in this workflow carries a hold resolution. The only two archives with a hold (`fo-interviews-extension`, `paseo-codex-dispatch-practice`) were reopened and closed PASSED. Closing a held task would therefore need `--force` (D2).
- *Does anything stop FO dispatching a held task?* No. `spacedock dispatch build` builds an ideation dispatch for a held task (AC-4). This design adds no dispatch guard. The harm on 2026-11-12 was what FO told the Captain, not a dispatch, and a guard would also stand in front of the reopen route (AC-6).
- *How is a held task reopened?* The Captain's reopen words go into a new gate attempt at the same stage. Spacedock appends a successor attempt after a hold, as `fo-interviews-extension` did at validation (AC-6). No new mechanism is needed.
- *What about a person reading `spacedock status`?* `--fields slug,status,gate-readiness` tells held from waiting today (`ideation/ac1-status-with-readiness.txt`). The default table without that flag cannot change in this package, because Spacedock is upstream (`spacedock-dev/spacedock`, not the Captain's repository).

### Facts checked (chain order)

1. **Spacedock** (binary 0.27.2; source read from the plugin cache 0.27.3). `internal/gates` `CurrentStageReadiness` and `EvaluateEligibility` map a closed attempt whose resolution is `hold` to `not-applicable`. `internal/status` `materializeGateReadiness` fills `gate-readiness` when a query names the field. `internal/gates/prepare.go` appends a successor attempt after a closed one. The field is missing from the known-field list in `status --help`, but a query naming it exits 0 (AC-1). The FO skill's canonical "entities in a stage" view (`fo-status-viewer`) is `--where status=<stage>`, which has no readiness column. `fo-dispatch-core.md` lists `not-applicable` and `hold` among states that are never routed as gate candidates.
2. **kc-dev-flow-2** (origin/main 8ce0eb60). `git grep 'gate-readiness\|not-applicable' origin/main -- kc-dev-flow-2` returns no hits. `pr_watch.py` `ready_rows` reads only `status --next --json` `ready_gates`, which leaves held tasks out, so its output never names them. The adopted mod `_mods/kc-dev-flow-2.md` (48 words, the same as the package's `references/sd/mods/kc-dev-flow-2.md`) runs `pr_watch.py tasks` at both startup and idle. `references/sd/workflow.md` has no rule that tells held tasks apart from waiting ones.
3. **Sibling adopters** (read-only `status --limit 0 --fields slug,status,gate-readiness`). subspace-relay dev2 has 65 tasks, one held at ideation, and that one also lists as plain `ideation` in a stage listing. subspace-web dev2 has 15 tasks, none held (`ideation/adopter-*.txt`, counts only). Neither has a held-task convention to borrow. The package change reaches relay's held task the same way.
4. **Past rulings.** `git grep -n 'Override:'` over this state finds two in this area. On `fo-write-checks-parse-top-level` the Captain chose closing over building two fixes. On `gate-summary-names-each-decline` he chose a hold plus a replacement task over approving D1-D3. The replacement, `_archive/decline-becomes-task-only-with-a-bite.md` (PASSED 2026-11-07), was approved with 「…擱置中的 gate-summary-names-each-decline 恢復時拿掉它的第 3 條」. That ruling expects the held task to resume, so this design does not recommend closing it. ADR 0062 (a gate approval grants what its quoted question says) means D2 must be written into the gate question if a plain approval is to accept it.

### Existing-code check

The capability exists in Spacedock (`gate-readiness`), and the package does not use it. The smallest working change repairs `pr_watch.py tasks`, which FO already runs at startup and idle, rather than adding a status field, a stage or README text. Proportional observation: the base `pr_watch.py tasks` output on the full state copy runs 157 lines and 1353 words and names none of the ten (AC-3). The base stage listing shows 17 `ideation` rows with no readiness column (`ideation/base-status-where-ideation.txt`).

### Change (one package PR)

1. `kc-dev-flow-2/scripts/pr_watch.py` `tasks` makes one extra call: `spacedock status --workflow-dir <wf> --where gate-readiness=not-applicable --fields slug,status --json --limit 0`. When any row comes back, it prints one line: `fact: held by the Captain, not waiting: <stage> <slug>, <slug>; <stage> …; each ## Held section says what reopens it.` If the call exits nonzero or its JSON cannot be read, it prints `next: report held-task query failure to the Captain: …` and exits 2, so a field renamed in a future Spacedock fails loudly.
2. Same function, for each held task. FO must have written a `## Held` section holding one `Reopen when: <text>` or `Closed: <text>` line. `<text>` must appear verbatim in the newest hold resolution reason, or in a `Captain:` line under the task's `## Captain amendments`, which covers a new ruling given without a new gate attempt. Otherwise the function prints one `next:` line naming those slugs: `next: write ## Held in <slugs>: copy Reopen when: <his words> or Closed: <his words> verbatim from the hold reason or a Captain amendment; where neither states one, ask him at the next sitting.`
3. `kc-dev-flow-2/scripts/test_pr_watch.py` covers five cases:
   - no held task prints no line;
   - a held task with a valid `## Held` prints only the fact line;
   - a held task with no `## Held` is named on the next line;
   - a quote not found in the reason or an amendment is named on the next line;
   - a status query failure exits 2.
4. Docstring lines for the two outputs. No change to `references/sd/workflow.md`, the mod text, `lint-skills.py`'s word budget, or any ADR.

**State change after the PR merges (FO, path-scoped state commits, no frontmatter edit):** FO writes `## Held` into the seven tasks whose hold reason already states a reopen condition or a close. It uses the quotes AC-7 checked (`ideation/ac7-proposed-held-lines.tsv`), after the Captain confirms the labels (D1). For the other three, FO records his D1 ruling as a `Captain:` amendment and then writes `## Held`. Every gate record stays byte-identical.

### The ten held tasks

The labels are this worker's reading of each hold reason, for the Captain to confirm at the gate. AC-7 proves only that each quote is verbatim.

| Task | Hold date | Proposed line (verbatim from the hold reason) |
| --- | --- | --- |
| adoption-asks-which-extensions | 2026-10-25 | Reopen when: reopen when a late listing flags a live record |
| captain-ruling-sources-checked | 2026-10-28 | Reopen when: nothing is built until the peers rule of 2026-10-27 fails in an adopter that has it |
| picky-reviewers-may-run-on-gemini | 2026-11-02 | Reopen when: until Paseo offers an Antigravity mode a test shows refusing a write |
| step-back-answer-has-a-record-line | 2026-11-05 | Reopen when: after that batch, a direction change keeps the task, none deletes it (FO checks whether that trial batch has run; if it has, a ruling is owed) |
| comment-check-reaches-delivery-gate | 2026-10-20 | Closed: The task is closed with the measurement as the reason. |
| fo-write-checks-parse-top-level | 2026-10-21 | Closed: 「關掉」 |
| adr-silent-undo-probe | 2026-10-23 | Closed: this copy stays at ideation and is not dispatched again (a reading: the work moved to dev2-poc; the ruling never says "closed") |
| seed-check-requires-alignment-result | 2026-10-29 | no line: the reason says "hold and build nothing" and names no reopen condition (D1) |
| gate-summary-names-each-decline | 2026-11-05 | no line in its own reason; a 2026-11-07 ruling on its replacement expects it to resume without its point 3 (D1) |
| journey-canvas-hosted-poc | 2026-10-11 | no line: "Design not taken; direction open" (D1) |

This dispatch listed four of the ten (adoption-asks-which-extensions, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc) as live tasks of other sessions. In this state checkout, each carries a hold resolution and has had no state commit since 2026-10-13 to 2026-10-25. Whether another session drives them elsewhere was not checked.

### Flow

```mermaid
flowchart TD
  C[Captain answers a gate with hold] --> R[FO: gate record --decision hold, reason quotes his words]
  R --> G{{Spacedock derives gate-readiness = not-applicable}}
  G --> N[status --next leaves the task out]
  G --> P[FO startup or idle: pr_watch.py tasks]
  P --> F[fact: held by the Captain, not waiting: stage slugs]
  P --> H{"## Held with a verbatim Reopen when: or Closed: line?"}
  H -->|yes| OK[no further line]
  H -->|no, his words state one| W[next: write ## Held from his words] --> OK
  H -->|no, his words state neither| A[next: ask the Captain at the next sitting] --> C2[Captain rules; FO records a Captain: amendment] --> W
  F --> Q[FO proposes waiting work from ready gates only]
  C3[Captain reopens] --> PR[FO: gate prepare, successor attempt] --> G2{{gate-readiness leaves not-applicable}}
```

### Words FO reads at each moment (base → candidate)

Counted with `wc -w`. The base was measured now. The candidate is projected from the line shapes above and is not provable now (NP-3). The mod runs `pr_watch.py tasks` at startup and at idle, so its output counts at both moments.

| Moment | Base (measured) | Candidate (projected) | Source |
| --- | --- | --- | --- |
| Startup: `workflow.md` 6008 + mod 48 + `pr_watch.py tasks` output 1353 | 7409 | ≤ 7439 once all ten have `## Held`; about +30 more while the `next:` line stands | `ideation/base-words-per-moment.txt`, `ideation/base-pr-watch-tasks.txt` |
| Idle, open or merged PR: mod 48 + `pr_watch.py tasks` output 1353 | 1401 | ≤ 1431 under the same condition | same |
| Proposing work or showing stage state | `status --where status=ideation`: 17 rows, no readiness | the fact line already in startup and idle output; no new command | `ideation/base-status-where-ideation.txt` |
| Gate record, merge ask, after archive | unchanged | unchanged | no file read at these moments changes |

Every moment rises by one line (about 26 words for ten held tasks). This task adds a line rather than cutting text, so the learning's "each moment below its base" test does not apply. The bound is ≤ 30 words.

### Worth questions

- **Part 1, the held fact line.** Serves 「a held or closed task is told apart from a waiting one … by FO before it proposes work」 (Scope Outcome, confirmed at the backlog gate). Without it, FO's startup and idle output never names held tasks (AC-3), the stage listing shows them as `ideation`, and the 2026-11-12 miss repeats. The premise that would make it unneeded is that FO proposes work only from the scheduler, which already hides held tasks. AC-2 checks the scheduler half, and it holds. The bite shows the other half fails: FO proposed from a listing.
- **Part 2, `## Held` with a verbatim reopen or close line.** Serves 「a held task states what would reopen it」. The premise that would make it unneeded is that hold reasons already state reopen conditions. AC-7 shows seven of ten carry a verbatim phrase this worker reads as a reopen condition or a close. In the other three, this worker found none. Without Part 2, nothing makes FO ask about those three.
- **Part 3, the state change for the ten.** Serves the Stop condition. Without it, the next line stands on every one of the ten. The premise is that none of the ten needs a new ruling. By this reading three do (D1).
- **Reader of `spacedock status`.** Served by the existing `--fields slug,status,gate-readiness` and changed by nothing here. The default table without the flag is upstream (NP-5). Every part serves the Captain's words; none is offered for cutting.

### Decisions for the Captain

- **D1 (needs his ruling, per the Stop condition).** By this worker's reading, three holds state neither a reopen condition nor a close. Recommendation per task:
  - *seed-check-requires-alignment-result:* **Closed**. Its reason says the check has existed since 0.31.0 and nothing is built.
  - *gate-summary-names-each-decline:* **keep held**, and he names what reopens it. His 2026-11-07 approval of the replacement expects it to resume without its point 3.
  - *journey-canvas-hosted-poc:* he says whether `journey-server-host-pilot` carries it. That pilot, authorized 2026-10-13 two days after this hold, is a shared kc-jmap server on Node and Cloudflare for one private journey. This worker did not confirm it covers share-by-link with edit limited to people he allows. If it does, record **Closed**; if not, he names the reopen condition.
  
  The gate also asks him to confirm the seven labels in the table. What gets worse: closing seed-check means reviving it needs a new task, and the journey-canvas answer costs him one more read.
- **D2 (recommendation stated in the gate question, so a plain approval accepts it).** Closed tasks stay at their stage with a `## Held` `Closed:` line and are not archived. Spacedock 0.27.2 refuses every unforced close of a held gate (AC-5), and this design does not use `--force` to bypass that guard. What gets worse: the plain stage listing keeps showing closed tasks at `ideation`. Only the readiness column and the startup and idle fact line tell them apart. Alternatives: archive with `--force` and verdict `REJECTED`, or ask Spacedock upstream for a supported close of a held gate. The upstream ask is an outward action only he can approve.

### Batch overlap

Re-grepped for `pr_watch` across the four batch task files and their folders at the end of this pass. Files this design changes: `kc-dev-flow-2/scripts/pr_watch.py` (`tasks`) and `kc-dev-flow-2/scripts/test_pr_watch.py`. After merge, FO also adds state-only `## Held` body sections, and for D1 `Captain:` amendments, in the ten held task files. No change to `workflow.md`, the mod, the `lint-skills.py` budget, the ADR list or a migration.

- merge-ask-tests-the-merge-result: its design states no `pr_watch.py` change and lists this task as "none" shared; none.
- held-and-closed-tasks-leave-the-design-queue: this task.
- each-task-records-stage-time-revises-and-interruptions: no shared file found in its task file or `poc/`. Its helper counts waiting time, and its two-week measurement counted these ten as open. It should read `gate-readiness` and count `not-applicable` as held, not waiting. That is a shared check, not a shared file.
- dispatch-close-out-archives-evidence-and-removes-scratch: **shared file `pr_watch.py` `tasks`** (and `test_pr_watch.py`). Its design adds an independent block there that sweeps scratch roots. Each block adds its own lines, so the later one rebases. Its design recommends landing first, and this design agrees.
- gate-question-facts-are-checked-before-the-captain-reads-them: no shared file. Its D2 recommends that this task owns its case 3 (a held task offered as waiting work), and its implementation replays case 3 against this task's listing. The listing it should replay is the fact line in NP-1, or the AC-1 query. Shared check: this task lands first.
- adoption-asks-which-extensions, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc: each is one of the ten held tasks and gets a `## Held` body section (state only). adoption-asks-which-extensions and comment-check-reaches-delivery-gate name `pr_watch.py` in their held designs, so if either reopens it overlaps on that file.
- adr-required-statement: changes `workflow.md` and `lint-skills.py`; none shared.
- journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot: none by file. journey-server-host-pilot is named in D1.

Recommended order: dispatch-close-out-archives-evidence-and-removes-scratch, then this task (rebasing its `pr_watch.py` `tasks` block), then gate-question-facts-are-checked-before-the-captain-reads-them and each-task-records-stage-time-revises-and-interruptions. merge-ask-tests-the-merge-result can land in any order. Any reopened held task that edits `pr_watch.py` goes after this one.

## Acceptance criteria

All seven criteria below pass at base: they prove the existing mechanism and the gap. Nothing here defines done for implementation; the implementation's acceptance is NP-1 to NP-4 under `## Not provable now`, each written for FO to promote unchanged. Evidence paths are relative to `held-and-closed-tasks-leave-the-design-queue/` in this state checkout. The exact command for each criterion is under its heading in `ideation/commands.md`. Each was run once on 2026-11-12.

**AC-1** Spacedock's existing `gate-readiness` field selects exactly the ten held tasks among the ideation tasks, and no waiting one. Evidence: `$SB status --workflow-dir $WD --where status=ideation --where gate-readiness=not-applicable --fields slug --json`, compared as a sorted set with `ideation/held-ten.txt` (`commands.md` § AC-1). Run: query exit 0, compare exit 0 ("got 10 want 10 equal True"). Saved: `ideation/ac1-held-query.json`, `ideation/ac1-status-with-readiness.txt`. Falsifier: a held task missing or a waiting task listed makes the compare exit 1. A Spacedock without the field makes the query exit nonzero (unknown field).

**AC-2** The scheduler view already leaves every held task out. Evidence: `$SB status --workflow-dir $WD --next --json`, then a check that no slug in `ready_gates` or `dispatchable` is in `ideation/held-ten.txt` (§ AC-2). Run: exit 0, 56 rows, none held. Saved: `ideation/ac2-next.json`. Falsifier: any held slug in either list exits 1.

**AC-3** Base FO startup and idle output names none of the held tasks, which is the gap this design closes. Evidence: origin/main 8ce0eb60 `pr_watch.py --state <scratch file> tasks <scratch>/docs/dev2`, run on an origin-less copy of state eae5ea47, then a check that no held slug occurs (§ AC-3; GitHub calls are reads only). Run: pr_watch exit 0, check exit 0 (1353 words, 0 held named). Saved: `ideation/base-pr-watch-tasks.txt`. Falsifier: a held slug in the output exits 1, which would show the gap already closed.

**AC-4** Spacedock 0.27.2 `dispatch build` does not refuse a held task (a bounded claim for this version and this command). Evidence: `dispatch build` for held `adoption-asks-which-extensions` at ideation in the origin-less scratch (§ AC-4). Run: exit 0, envelope printed; the dispatch file it wrote was removed. Saved: `ideation/scratch-dispatch-build-held.txt`. Falsifier: a nonzero exit or a refusal.

**AC-5** Spacedock 0.27.2 has no unforced route to close a held task. Evidence: `merge guard … --verdict rejected`, `status --set … status=done verdict=REJECTED` and `status --archive …` on held `fo-write-checks-parse-top-level` in the scratch (§ AC-5). Run: each exits 1. The first two cite `condition "not-applicable"`; the third cites the unrun `pr-merge` hook and offers `--force`. No `_archive/` was created. Saved: `ideation/scratch-merge-guard-rejected-from-held.txt`, `ideation/scratch-close-held-task.txt`, `ideation/scratch-archive-held-task.txt`. A control on a non-held task was inconclusive: it was refused for a missing-history reason (`ideation/scratch-close-non-held-control.txt`). Falsifier: any of the three exiting 0.

**AC-6** A held gate can be reopened by a successor attempt, as a real record shows. Evidence: a YAML read of `_archive/fo-interviews-extension.md` gate records that exits 0 only when a `hold` attempt is followed by another attempt in the same record (§ AC-6). Run: exit 0, `validation-1 hold` then `validation-2 approve consumed`. Saved: `ideation/ac6-reopen-after-hold.txt`. Falsifier: no successor after a hold exits 1.

**AC-7** Each of the seven proposed `Reopen when:` or `Closed:` texts appears verbatim in its task's newest hold reason. Evidence: a check of `ideation/ac7-proposed-held-lines.tsv` against each task's gate records that exits 1 on any quote not found (§ AC-7). Run: exit 0, `mismatches 0`, seven verbatim, three with no line proposed. Saved: `ideation/ac7-held-lines-quote-check.txt`, `ideation/ac7-hold-reasons.txt`. Falsifier: changing any quote by one character exits 1. This proves verbatim quoting only. The labels, and the reading that the other three state neither, are for the Captain to confirm (D1).

## Not provable now

These need the candidate. Each is written with its planned command and falsifier so FO can promote it to an acceptance criterion unchanged. They are for the Captain to see at the design gate.

- **NP-1** At the candidate, `pr_watch.py tasks` prints exactly one `fact: held by the Captain, not waiting:` line naming exactly the held tasks by stage, and none when none is held. Planned evidence: `SPACEDOCK_BIN=$SB python3 -B <candidate>/kc-dev-flow-2/scripts/pr_watch.py --state <tmp> tasks <origin-less copy>/docs/dev2`, then a check that the fact line's slugs equal the AC-1 query's slugs; plus a unit case with no held task. Falsifier: a missing, extra or duplicated slug, or a line printed with no held task.
- **NP-2** At the candidate, a held task with no `## Held` section, or whose quoted text is in neither its hold reason nor a `Captain:` amendment, is named on the `next:` line, and one with a valid line is not. A failed status query exits 2. Planned evidence: `python3 -B -m pytest kc-dev-flow-2/scripts/test_pr_watch.py -k held` with the five cases in Change item 3. Falsifier: deleting the verbatim comparison, or the exit-2 branch, makes a case fail.
- **NP-3** With all ten carrying `## Held`, idle words at the candidate are at most 1431 (base 1401) and startup at most 7439 (base 7409). Planned evidence: the NP-1 command on a copy where the ten carry `## Held`, then `wc -w` added to the unchanged 48 mod words and 6008 `workflow.md` words. Falsifier: more than 30 added words at either moment.
- **NP-4** After the state change, each of the ten carries a `## Held` line passing the NP-2 rule, and each task's frontmatter is byte-identical to state eae5ea47. Planned evidence: `git -C <state> diff eae5ea47 -- <ten files>` shows body-only hunks, and the NP-1 command prints no `next: write ## Held` line. Falsifier: any frontmatter hunk, or a remaining `next:` line. This needs D1's ruling for three tasks.
- **NP-5** A reader of plain `spacedock status`, without `--fields`, telling held tasks from waiting ones. This needs an upstream Spacedock change outside this package (D2), so no planned command.

## Stage Report: ideation

- DONE: The Captain's experiment for this task (his words are in the task's backlog gate record): this task is in the arm without a proof of concept. For every acceptance criterion, run its evidence command or procedure once now and write beside the criterion the exact command, its exit and the path of its saved output in the task folder; a criterion whose proof cannot be run now is not written under Acceptance criteria but under a 'Not provable now' list with the reason, for the Captain to see at the design gate
  AC-1..7 each give their command, exit and saved file; the exact commands are in `ideation/commands.md`. All seven pass at base. NP-1..5 carry planned commands and falsifiers.
- DONE: AC-1 existing `gate-readiness` selects exactly the ten held tasks
  Query and compare both exit 0 ("got 10 want 10 equal True"); `ideation/ac1-held-query.json`.
- DONE: AC-2 `status --next` leaves every held task out
  exit 0, 56 rows, none held; `ideation/ac2-next.json`.
- DONE: AC-3 base `pr_watch.py tasks` names no held task
  exit 0, 1353 words, 0 named; `ideation/base-pr-watch-tasks.txt`; its GitHub calls are reads only.
- DONE: AC-4 `dispatch build` builds a held task's dispatch (bounded claim)
  exit 0 in the origin-less scratch; `ideation/scratch-dispatch-build-held.txt`.
- DONE: AC-5 no unforced close of a held gate in Spacedock 0.27.2
  merge guard, terminal `status --set` and `--archive` each exit 1, with the non-held control inconclusive; four `ideation/scratch-*.txt` files.
- DONE: AC-6 a successor attempt after a hold exists in a real record
  exit 0 on `_archive/fo-interviews-extension.md`; `ideation/ac6-reopen-after-hold.txt`.
- DONE: AC-7 seven proposed held lines quote their hold reasons verbatim
  exit 0, `mismatches 0`; `ideation/ac7-held-lines-quote-check.txt`. The labels are for the Captain to confirm (D1).
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (merge-ask-tests-the-merge-result, held-and-closed-tasks-leave-the-design-queue, each-task-records-stage-time-revises-and-interruptions, dispatch-close-out-archives-evidence-and-removes-scratch, gate-question-facts-are-checked-before-the-captain-reads-them) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Shared `pr_watch.py` `tasks` with dispatch-close-out (lands first) and the shared case-3 check with gate-question-facts; `Recommended order:` given. Four of the "live" tasks are among the held ten.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Base: startup 7409 (workflow.md 6008 + mod 48 + pr_watch output 1353), idle 1401. Candidate: at most +30 per moment, projected (NP-3).
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  Every AC carries a falsifier. D1 rules on three holds per task (seed-check Closed, gate-summary kept held, journey-canvas his call) and confirms the seven labels. D2: no `--force` archive, stated in the gate question.
- DONE: Design surfaces and criteria grammar checked
  `design_surfaces.py check` exit 0, "design surfaces presentable"; `status --read --ac-scan` exit 0, AC-1..AC-7 each `unevidenced=false`.

### Summary

Spacedock already tells a held task from a waiting one: a hold reads as `gate-readiness=not-applicable`, and `status --next` leaves it out. The miss came from FO proposing work from a plain stage listing, while its startup and idle output never names held tasks. The design is one package PR. `pr_watch.py tasks` prints a held-tasks fact line, and asks for a `## Held` section that quotes the Captain's reopen or close words verbatim. FO then writes that section for seven of the ten. Three go to the Captain (D1), and gate-summary stays held because a later ruling expects it to resume. Spacedock 0.27.2 cannot close a held gate without `--force`, so closed tasks stay unarchived (D2). All seven ACs prove the base and the gap; the candidate's acceptance is NP-1..4.
