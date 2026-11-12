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

Ideation evidence folder: `held-and-closed-tasks-leave-the-design-queue/ideation/` in this state checkout (state pinned at `eae5ea47cec926f35d164f8a88d31579196d7634`, package at origin/main `8ce0eb6050c889b21baccf50fec35231bc888d66`, kc-dev-flow-2 0.39.1, `spacedock 0.27.2`).

### PRFAQ

**Proposition.** When the Captain holds or closes a task at a gate, the First Officer (FO) stops seeing it as work waiting in that stage. Every time FO checks its open work (`pr_watch.py tasks`), one line names the held tasks by stage, so FO does not offer them as waiting work. Each held task carries a short `## Held` section. It quotes the Captain's own words from the hold record: what reopens the task (`Reopen when:`) or that it is closed (`Closed:`). If the hold record says neither, the same output tells FO to ask him. Spacedock already computes the held state, so this adds no new state field and no new stage.

**FAQ**

- *Does Spacedock already have this?* Mostly. `spacedock status` derives a `gate-readiness` value from the gate record, and a `hold` resolution reads as `not-applicable` (AC-1). The scheduler view `status --next` already leaves held tasks out (AC-2). Two things are missing. The stage listing FO used, `status --where status=ideation`, shows held tasks as plain `ideation` with no readiness column. FO's idle output does not mention them at all (AC-3).
- *Why not archive the closed ones as REJECTED, like earlier closed tasks?* Spacedock 0.27.2 refuses every unforced route to close a task whose current gate is held: `merge guard --verdict rejected`, a terminal `status --set` and `status --archive` (AC-5). The earlier REJECTED archives were closed from `backlog` with no gate decision. Closing a held task would need `--force` (decision D2).
- *Does anything stop FO dispatching a held task?* No. `spacedock dispatch build` builds an ideation dispatch for a held task (AC-4). This design does not add a dispatch guard. The harm on 2026-11-12 was what FO told the Captain, not a dispatch, and a guard would also block the legitimate reopen route (AC-6).
- *How is a held task reopened?* The Captain's reopen words go into a new gate attempt at the same stage. Spacedock appends a successor attempt after a hold, as `fo-interviews-extension` did at validation (AC-6). No new mechanism is needed.
- *What about a person reading `spacedock status`?* `--fields slug,status,gate-readiness` tells held from waiting today (AC-1 evidence file). The default table without that flag cannot change in this package, because Spacedock is upstream (`spacedock-dev/spacedock`, not the Captain's repository).

### Facts checked (chain order)

1. **Spacedock** (binary 0.27.2; source read from the plugin cache 0.27.3). `internal/gates` `CurrentStageReadiness` and `EvaluateEligibility` map a closed attempt whose resolution is `hold` to `not-applicable`. `internal/status` `materializeGateReadiness` fills the `gate-readiness` field when a query names it. `gate prepare` appends a successor attempt after a closed attempt (`internal/gates/prepare.go`). The field is missing from the known-field list in `status --help`. It works anyway: an unknown field would be an error, and AC-1 exits 0. The FO skill's canonical "entities in a stage" view (`fo-status-viewer`) is `--where status=<stage>`, which has no readiness column. `fo-dispatch-core.md` names `not-applicable` and `hold` as states owned elsewhere, never routed as gate candidates.
2. **kc-dev-flow-2** (origin/main 8ce0eb60). `git grep 'gate-readiness\|not-applicable' origin/main -- kc-dev-flow-2` returns no hits. `pr_watch.py` `ready_rows` reads only `status --next --json` `ready_gates`, which leaves held tasks out, so they never appear in its output. `references/sd/workflow.md` has no rule about telling held tasks apart from waiting ones.
3. **Sibling adopters** (read-only `status --limit 0 --fields slug,status,gate-readiness`). subspace-relay dev2 has 65 tasks, one of them held at ideation (`web-identity-accepts-version`, `not-applicable`), and it too lists as plain `ideation` in a stage listing. subspace-web dev2 has 15 tasks and none held (`ideation/adopter-subspace-relay-gate-readiness.txt`, `ideation/adopter-subspace-web-gate-readiness.txt`). Neither has a held-task convention to borrow. The package change reaches relay's held task the same way.
4. **Past rulings.** `git grep -n 'Override:'` over this state finds two in this area. On `fo-write-checks-parse-top-level` the Captain chose closing over building two fixes. On `gate-summary-names-each-decline` he chose a hold plus a replacement task over approving D1-D3. Both prefer closing to adding mechanism, and the small design and the "Closed" recommendations below follow that. ADR 0062 (a gate approval grants what its quoted question says) means D2 must be written into the gate question if a plain approval is to accept it.

### Existing-code check

The capability exists in Spacedock (`gate-readiness`) and is unused by the package. The smallest working change repairs `pr_watch.py tasks`, which FO already runs at every idle boundary, rather than adding a status field, a stage or README text. Proportional observation: base `pr_watch.py tasks` output on the full state copy runs 157 lines and 1353 words and names none of the 10 (AC-3). The base stage listing shows 17 `ideation` rows with no readiness column (`ideation/base-status-where-ideation.txt`).

### Change (one package PR)

1. `kc-dev-flow-2/scripts/pr_watch.py` `tasks`: one extra `spacedock status --workflow-dir <wf> --where gate-readiness=not-applicable --fields slug,status --json --limit 0` call. When any row comes back, it prints one line: `fact: held by the Captain, not waiting: <stage> <slug>, <slug>; <stage> …; each ## Held section says what reopens it.` A nonzero exit or unreadable JSON prints `next: report held-task query failure to the Captain: …` and makes the exit code 2, so a renamed field in a future Spacedock fails loudly.
2. Same function: for each held task, read the newest hold resolution reason and the body. If the body has no `## Held` section, or that section has no `Reopen when: <text>` or `Closed: <text>` line whose `<text>` appears verbatim in the reason, print one `next:` line naming those slugs: `next: write ## Held in <slugs>: copy Reopen when: <his words> or Closed: <his words> verbatim from the hold reason; where the reason says neither, ask him at the next sitting.`
3. `kc-dev-flow-2/scripts/test_pr_watch.py`: cases for no held task (no line), held with a valid `## Held` (fact line only), held without one (next line), quote not in reason (next line), and status query failure (exit 2).
4. Docstring lines for the two outputs. No change to `references/sd/workflow.md`, `lint-skills.py`'s word budget, or any ADR.

**State change after the PR merges (FO, path-scoped state commits, no frontmatter edit):** FO writes `## Held` into the seven tasks whose hold reason already states a reopen condition or a close, using the quotes AC-7 checked (`ideation/ac7-proposed-held-lines.tsv`). The three that state neither go to the Captain (D1). Every gate record stays byte-identical.

### The ten held tasks

| Task | Hold date | Proposed line (verbatim from the hold reason) |
| --- | --- | --- |
| adoption-asks-which-extensions | 2026-10-25 | Reopen when: reopen when a late listing flags a live record |
| captain-ruling-sources-checked | 2026-10-28 | Reopen when: nothing is built until the peers rule of 2026-10-27 fails in an adopter that has it |
| picky-reviewers-may-run-on-gemini | 2026-11-02 | Reopen when: until Paseo offers an Antigravity mode a test shows refusing a write |
| step-back-answer-has-a-record-line | 2026-11-05 | Reopen when: after that batch, a direction change keeps the task, none deletes it (FO checks whether that trial batch has run; if it has, a ruling is owed) |
| comment-check-reaches-delivery-gate | 2026-10-20 | Closed: The task is closed with the measurement as the reason. |
| fo-write-checks-parse-top-level | 2026-10-21 | Closed: 「關掉」 |
| adr-silent-undo-probe | 2026-10-23 | Closed: this copy stays at ideation and is not dispatched again |
| seed-check-requires-alignment-result | 2026-10-29 | needs a ruling (D1): the reason says "hold and build nothing" with no reopen condition |
| gate-summary-names-each-decline | 2026-11-05 | needs a ruling (D1): held and replaced by a smaller task, no reopen condition |
| journey-canvas-hosted-poc | 2026-10-11 | needs a ruling (D1): "Design not taken; direction open" |

Four of these (adoption-asks-which-extensions, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc) were listed in this dispatch as live tasks of other sessions. Their records show a hold, and they have had no state commit since 2026-10-13 to 2026-10-25. That listing is a second instance of the same miss.

### Flow

```mermaid
flowchart TD
  C[Captain answers a gate with hold] --> R[FO: gate record --decision hold, reason quotes his words]
  R --> G{{Spacedock derives gate-readiness = not-applicable}}
  G --> N[status --next leaves the task out]
  G --> P[FO idle: pr_watch.py tasks]
  P --> F[fact: held by the Captain, not waiting: stage slugs]
  P --> H{"## Held with a verbatim Reopen when: or Closed: line?"}
  H -->|yes| OK[no further line]
  H -->|no, reason states one| W[next: write ## Held from the reason] --> OK
  H -->|no, reason states neither| A[next: ask the Captain at the next sitting] --> C2[Captain rules: reopen condition or closed] --> W
  F --> Q[FO proposes waiting work from ready gates only]
  C3[Captain reopens] --> PR[FO: gate prepare, successor attempt] --> G2{{gate-readiness leaves not-applicable}}
```

### Words FO reads at each moment (base → candidate)

Counted with `wc -w`. Base measured now; candidate projected from the line shapes above. The candidate count is not provable now (NP-3).

| Moment | Base (measured) | Candidate | Source |
| --- | --- | --- | --- |
| Startup (`references/sd/workflow.md`) | 6008 | 6008 (file unchanged) | `ideation/base-words-per-moment.txt` |
| Idle, open or merged PR (`pr_watch.py tasks` output) | 1353 | ≤ 1383 once all ten have `## Held` (one fact line of about 13 words plus 10 slugs); about +30 more while the `next:` line stands | `ideation/base-pr-watch-tasks.txt` |
| Proposing work or showing stage state | `status --where status=ideation`: 17 rows, no readiness | FO reads the fact line already in idle output; no new command | `ideation/base-status-where-ideation.txt` |
| Gate record, merge ask, after archive | unchanged | unchanged | no file in these paths changes |

### Worth questions

- **Part 1, the held fact line.** Serves 「a held or closed task is told apart from a waiting one … by FO before it proposes work」 (Scope Outcome, confirmed at the backlog gate). Without it, FO's idle output never names held tasks (AC-3), the stage listing shows them as `ideation`, and the 2026-11-12 miss repeats. The premise that would make it unneeded is that FO only proposes from the scheduler, which already hides held tasks. AC-2 checks the scheduler half, and it holds. The bite shows the other half fails: FO proposed from a listing.
- **Part 2, `## Held` with a verbatim reopen or close line.** Serves 「a held task states what would reopen it」. Without it, three of the ten rulings state neither (AC-7), and nothing makes FO ask. The premise that would make it unneeded is that hold reasons already state reopen conditions. AC-7 tests it: 7 of 10 do and 3 do not.
- **Part 3, the state change for the ten.** Serves the Stop condition. Without it, the next line stands forever on all ten. The premise is that none of the ten needs a new ruling, and AC-7 falsifies it for three (D1).
- **Reader of `spacedock status`.** Served by the existing `--fields slug,status,gate-readiness` and changed by nothing here. The default table without the flag is upstream. Every part serves the Captain's words; none is offered for cutting.

### Decisions for the Captain

- **D1 (needs his ruling, per the Stop condition).** The holds of `seed-check-requires-alignment-result`, `gate-summary-names-each-decline` and `journey-canvas-hosted-poc` state neither a reopen condition nor a close. Recommendation: record **Closed** for all three. For seed-check, its reason says the check exists since 0.31.0 and nothing is built. For gate-summary, it was replaced by the smaller task he chose. For journey-canvas, the Cloudflare design was not taken and server hosting is now carried by `journey-server-host-pilot`. What gets worse: if that pilot does not cover share-by-link with edit limited to people he allows, that need has no open task until it is filed again.
- **D2 (recommendation stated in the gate question, so a plain approval accepts it).** Closed tasks stay at their stage with a `## Held` `Closed:` line and are not archived. Spacedock 0.27.2 refuses every unforced close of a held gate (AC-5), and this design does not use `--force` to bypass that guard. What gets worse: the plain stage listing keeps showing closed tasks at `ideation`. Only the readiness column and the idle fact line tell them apart. Alternatives: archive with `--force` and verdict `REJECTED`, or ask Spacedock upstream for a supported close of a held gate. The upstream ask is an outward action that only he can approve.

### Batch overlap

Files this design changes: `kc-dev-flow-2/scripts/pr_watch.py` (`tasks`), `kc-dev-flow-2/scripts/test_pr_watch.py`. After merge, it also adds state-only `## Held` body sections in the ten held task files. It changes no `workflow.md`, `lint-skills.py` budget, ADR list or migration.

- merge-ask-tests-the-merge-result: its task file as of 2026-11-12 names none of these files; none.
- held-and-closed-tasks-leave-the-design-queue: this task.
- each-task-records-stage-time-revises-and-interruptions: no shared file is known yet (its design is in progress). Its helper counts waiting time and its two-week measurement counted these ten as open, so it should read `gate-readiness` and treat `not-applicable` as held, not waiting. That shared check is a concept, not a file.
- dispatch-close-out-archives-evidence-and-removes-scratch: none known.
- gate-question-facts-are-checked-before-the-captain-reads-them: none known. A gate question claiming that a task is "waiting" would be one of the facts it checks.
- adoption-asks-which-extensions, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc: each is one of the ten held tasks and gets a `## Held` body section (state only). adoption-asks-which-extensions and comment-check-reaches-delivery-gate name `pr_watch.py` in their held designs, so if either is reopened it overlaps on that file.
- adr-required-statement: changes `workflow.md` and `lint-skills.py`; none shared.
- journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot: none by file. journey-server-host-pilot is named in D1 as journey-canvas-hosted-poc's successor.

Recommended order: this task's `pr_watch.py` change is independent by file of the four other batch tasks and can land in any order. Land it before each-task-records-stage-time-revises-and-interruptions builds its helper, and before any reopened held task that edits `pr_watch.py`.

## Acceptance criteria

Evidence paths are relative to `held-and-closed-tasks-leave-the-design-queue/` in this state checkout. `$SB` is `/Users/kent/.local/bin/spacedock` and `$WD` is this workflow directory. Each criterion was run once on 2026-11-12.

**AC-1** Spacedock's existing `gate-readiness` field selects exactly the ten held tasks among the ideation tasks and no waiting one. Evidence: `$SB status --workflow-dir $WD --where status=ideation --where gate-readiness=not-applicable --fields slug --json`, compared as a sorted set with `ideation/held-ten.txt` by a `python3 -c` equality check. Run: query exit 0, compare exit 0 ("got 10 want 10 equal True"). Saved: `ideation/ac1-held-query.json`, `ideation/ac1-status-with-readiness.txt`. Falsifier: a held task missing or a waiting task listed makes the compare exit 1; a Spacedock without the field makes the query exit nonzero (unknown field).

**AC-2** The scheduler view already leaves every held task out. Evidence: `$SB status --workflow-dir $WD --next --json`, then a `python3 -c` check that no slug in `ready_gates` or `dispatchable` is in `ideation/held-ten.txt`. Run: exit 0, 56 rows, none held. Saved: `ideation/ac2-next.json`. Falsifier: any held slug in either list exits 1.

**AC-3** Base FO idle output names none of the held tasks, which is the gap this design closes. Evidence: origin/main 8ce0eb60 `kc-dev-flow-2/scripts/pr_watch.py --state <scratch> tasks <scratch>/docs/dev2`, with `SPACEDOCK_BIN` set, run on an origin-less copy of state eae5ea47 (`git archive | tar -x`, `git init`). A `python3 -c` check then confirms no held slug occurs in the output. Run: pr_watch exit 0, check exit 0 (1353 words, 0 held named). Saved: `ideation/base-pr-watch-tasks.txt`. Falsifier: a held slug in the output exits 1, and would show the gap already closed.

**AC-4** Spacedock does not refuse dispatching a held task (a bounded claim, for this version and this command). Evidence: in the origin-less scratch, `$SB dispatch build --workflow-dir <scratch>/docs/dev2 --entity-path <scratch>/…/adoption-asks-which-extensions.md --stage ideation --checklist-file <one line>`. Run: exit 0, envelope printed (the built dispatch file was removed). Saved: `ideation/scratch-dispatch-build-held.txt`. Falsifier: a nonzero exit or a refusal message.

**AC-5** Spacedock 0.27.2 has no unforced route to close a held task. Evidence: in the scratch, `$SB merge guard fo-write-checks-parse-top-level --verdict rejected`, `$SB status --set fo-write-checks-parse-top-level status=done verdict=REJECTED` and `$SB status --archive fo-write-checks-parse-top-level`. Run: each exits 1, the first two with `condition "not-applicable"` and the third with "merge hook(s) [pr-merge] that have not run … use --force"; no `_archive/` was created. Saved: `ideation/scratch-merge-guard-rejected-from-held.txt`, `ideation/scratch-close-held-task.txt`, `ideation/scratch-archive-held-task.txt`. Falsifier: any of the three exiting 0.

**AC-6** A held gate can be reopened by a successor attempt, and a real record shows it. Evidence: a `python3` YAML read of `_archive/fo-interviews-extension.md` gate records that exits 0 only when a `hold` attempt is followed by another attempt in the same record. Run: exit 0, with `validation-1 hold` followed by `validation-2 approve consumed`. Saved: `ideation/ac6-reopen-after-hold.txt`. Falsifier: no successor after a hold exits 1.

**AC-7** For seven of the ten, the proposed `Reopen when:` or `Closed:` text appears verbatim in the task's newest hold reason, and the other three have no such text and go to D1. Evidence: a `python3` check of `ideation/ac7-proposed-held-lines.tsv` against each task's gate records that exits 1 on any quote not found. Run: exit 0, `mismatches 0`, 7 verbatim and 3 with no line proposed. Saved: `ideation/ac7-held-lines-quote-check.txt`, `ideation/ac7-hold-reasons.txt`. Falsifier: editing any quote by one character makes it exit 1.

## Not provable now

These hold until a candidate exists, and are for the Captain to see at the design gate.

- **NP-1** At the candidate, `pr_watch.py tasks` prints exactly one `fact: held by the Captain, not waiting:` line naming exactly the held tasks by stage, and none when none is held. The script change is not built in this no-POC arm.
- **NP-2** At the candidate, a held task with no `## Held` section, or one whose quote is not in its hold reason, is named on the `next:` line, and one with a verbatim line is not. A status query failure exits 2. The tests in `test_pr_watch.py` are not written yet.
- **NP-3** Idle words at the candidate, with all ten carrying `## Held`, are at most 1383 against the base 1353, and startup stays at 6008. This needs the candidate output.
- **NP-4** After the state change, the seven tasks carry `## Held` with the AC-7 quotes and their frontmatter is byte-identical to state eae5ea47. This needs the post-merge state commits and D1's ruling for the other three.
- **NP-5** A reader of plain `spacedock status`, without `--fields`, telling held tasks from waiting ones. This needs an upstream Spacedock change, outside this package (D2).

## Stage Report: ideation

- DONE: The Captain's experiment for this task (his words are in the task's backlog gate record): this task is in the arm without a proof of concept. For every acceptance criterion, run its evidence command or procedure once now and write beside the criterion the exact command, its exit and the path of its saved output in the task folder; a criterion whose proof cannot be run now is not written under Acceptance criteria but under a 'Not provable now' list with the reason, for the Captain to see at the design gate
  AC-1..7 each list its command, exit and saved file under `ideation/`; NP-1..5 are listed under `## Not provable now`.
- DONE: AC-1 existing `gate-readiness` selects exactly the ten held tasks
  Query and compare both exit 0 ("got 10 want 10 equal True"); `ideation/ac1-held-query.json`.
- DONE: AC-2 `status --next` leaves every held task out
  exit 0, 56 rows, none held; `ideation/ac2-next.json`.
- DONE: AC-3 base `pr_watch.py tasks` names no held task
  exit 0, 1353 words, 0 named; `ideation/base-pr-watch-tasks.txt`.
- DONE: AC-4 `dispatch build` builds a held task's dispatch (bounded claim)
  exit 0 in the origin-less scratch; `ideation/scratch-dispatch-build-held.txt`.
- DONE: AC-5 no unforced close of a held gate in Spacedock 0.27.2
  merge guard, terminal `status --set` and `--archive` each exit 1; three `ideation/scratch-*.txt` files.
- DONE: AC-6 a successor attempt after a hold exists in a real record
  exit 0 on `_archive/fo-interviews-extension.md`; `ideation/ac6-reopen-after-hold.txt`.
- DONE: AC-7 seven proposed held lines are verbatim in their hold reasons and three need a ruling
  exit 0, `mismatches 0`; `ideation/ac7-held-lines-quote-check.txt`.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (merge-ask-tests-the-merge-result, held-and-closed-tasks-leave-the-design-queue, each-task-records-stage-time-revises-and-interruptions, dispatch-close-out-archives-evidence-and-removes-scratch, gate-question-facts-are-checked-before-the-captain-reads-them) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Every named task has a row; the files are `pr_watch.py` and `test_pr_watch.py`; it ends with a `Recommended order:` line. Four "live" tasks are in the held ten.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Measured base: startup 6008 and idle 1353 (`ideation/base-words-per-moment.txt`). The candidate is projected and listed as NP-3.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1..7 each carry a falsifier. D1 (three holds need a ruling; recommend Closed) and D2 (do not force-archive; recommend stating it in the gate question) each say what gets worse.

### Summary

Spacedock already tells a held task from a waiting one: a hold reads as `gate-readiness=not-applicable`, and `status --next` leaves it out. The miss came from FO proposing work from a plain stage listing, while its idle output never names held tasks. The design is one package PR: `pr_watch.py tasks` prints a held-tasks fact line and asks for a `## Held` section that quotes the Captain's reopen or close words verbatim. FO then writes that section for seven of the ten. The other three go to the Captain (D1). Spacedock 0.27.2 cannot close a held gate without `--force`, so closed tasks stay unarchived (D2).
