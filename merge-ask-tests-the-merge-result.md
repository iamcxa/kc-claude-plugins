---
title: A merge ask for a PR whose base moved since validation carries a test run on the merge result
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:merge-ask-tests-the-merge-result:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:merge-ask-tests-the-merge-result-backlog-1
              briefing:
                id: briefing:merge-ask-tests-the-merge-result:backlog:attempt-1:revision-1
                digest: sha256:49ebaa98701d209a51e97e09e90aa390888350e8d02aef377224de98ebe6270a
                room-ref: ./merge-ask-tests-the-merge-result/review/backlog/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-11-12T05:11:28.449691Z"
                reason: The Captain answered the joint question with a change to the experiment instead of a decision (host question dialog, 2026-11-12); FO asks again with the experiment written into the question.
            - id: gate-attempt:merge-ask-tests-the-merge-result-backlog-2
              briefing:
                id: briefing:merge-ask-tests-the-merge-result:backlog:attempt-2:revision-1
                digest: sha256:09fe9a54d587cdd31282078fed3541c7e4e93362d7126e11df246e7af3164c35
                room-ref: ./merge-ask-tests-the-merge-result/review/backlog/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:merge-ask-tests-the-merge-result:backlog:2
                briefing: briefing:merge-ask-tests-the-merge-result:backlog:attempt-2:revision-1
                by: person:captain
                at: "2026-11-12T05:15:22.509496Z"
                decision: approve
                reason: 'The Captain chose 「核准，照這個分組（建議）」 (host question dialog, 2026-11-12), answering 「決定：這五張新任務要不要都進設計階段，並照你說的做成對照實驗。我建議核准。五張是：一、合併前在合併後的結果上跑測試；二、被你擱置或關掉的任務不再像在排隊；三、每張任務記錄階段時間、重做、打斷次數；四、派工結束封存證據、刪掉暫存；五、我問你的問題裡的事實先對過紀錄。實驗分兩組：第三、五、一張的設計階段照你的說法，等於「試作加擴大計畫」，設計工人先在不推送的分支上把東西真的做出一個能跑的試作、拿真實案例跑過，再寫擴大成正式版本還要補什麼，實作工人從那個試作接著做；第二、四張的設計階段只要求把每條驗收條件的證明實際跑一次，不寫試作。對照基準是過去兩週的 67 張。核准代表接受各任務檔寫的範圍、預算（每階段一輪、一個 PR）與停止條件。不代表接受任何設計或修法。哪張進哪一組是我挑的，不是隨機：試作組放的是證據最難產生或最大的三張。五張合起來我沒有把握一天做完，超過時我連同預算回來請你取捨。」. Recommendation: followed. The experiment is his: before this question he answered the first form of it with 「我想要做一個實驗，比較一下，有幾張的構思階段就是包含實作poc，你說構思完全沒有先試驗過測試過，所以我想加過這一段試試看是否就會改善，等於構思等於poc加擴大計畫」 (same dialog), and FO withdrew and re-asked.'
              application:
                target-stage: ideation
                state: consumed
started: 2026-11-12T05:16:52Z
---

## Scope

- Source: FO's own miss, filed by FO with no Captain ruling yet; the backlog gate confirms it.
- Bite (FO read 2026-11-11, `gh run view 42991036147 --repo iamcxa/kc-claude-plugins --log-failed`): PRs #843 and #841 each passed their own checks and validation; after both merged, main failed one of 226 tests in `kc-dev-flow-2/scripts/test_design_surfaces.py`, Release PR #840 could not pass, and a fix task ran 80 minutes from filing to archive. The #841 merge ask said the acceptance was not rerun on the merged result; nothing held the ask.
- Outcome: when main has moved since the validated head was dispatched, FO's merge ask is held until a test run on the result of merging that head with current main is recorded, or the Captain is told in the question that none was run.
- Open for the design: which commands count as the run and who runs them; whether the existing delivery check can carry it or GitHub's own merge queue or required up-to-date branch setting already does; what it costs per PR in minutes.
- Non-goals: changing CI definitions; rerunning validation; any rule for PRs whose base did not move.

## Budget
1 cycle per stage, in one package PR.

## Stop condition
- A replay of PR #841's merge ask at its recorded state is held by the candidate and the same ask with a recorded merge-result run passes. Return to the Captain if the design needs a CI or repository-setting change.

## FO alignment

Alignment: not needed: one observed defect with one outcome; how it is checked is compared in the design and ruled at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Design

Proof of concept: local branch `poc/merge-ask-tests-the-merge-result`, commit
`e348d05b7` (parent origin/main `8ce0eb605`, kc-dev-flow-2 0.39.1), in the workflow
checkout's `.worktrees/poc-merge-ask-tests-the-merge-result`. Never pushed; no PR.
It changes `kc-dev-flow-2/scripts/delivery_gate.py` (+109) and
`kc-dev-flow-2/scripts/test_delivery_gate.py` (+3, the stub `gh` answers the new
compare call). Evidence is under `merge-ask-tests-the-merge-result/poc/`.

### What the proof of concept showed

- **The Bite reproduces exactly.** `git merge-tree --write-tree eeee0023 6da9a765`
  (trunk at the #841 ask, 2026-11-11T08:52:08Z, and the #841 head) gives tree
  `3ba40948`, the same tree as the squash commit that landed, `571a7bd8^{tree}`.
  `test_design_surfaces.py` on that tree fails 1 of 226; on the head alone it passes
  224 of 224 (`poc/runs/red-result.log`, `poc/runs/head-only-test_design_surfaces.log`,
  `poc/ac_tree_and_scratch.log`).
- **GitHub did test a merge result, against an old trunk.** The #841 PR run checked
  out `Merge 6da9a765 into 546a1363` at 07:24; #843 merged at 07:55, so CI never saw
  the pair. Branch protection has `strict: false` and the repository has no ruleset
  or merge queue (`poc/github-settings-and-pr-ci-base.txt`). Nothing in GitHub's
  current settings holds the ask.
- **The #841 acceptance script would not have caught it.** It runs six named tests in
  `test_dispatch_stage` and `test_role_triggers` and never runs `test_design_surfaces.py`
  (`poc/acceptance-script-scope.txt`). So "rerun acceptance on the merge result" is not
  enough; the run must be the package's own unit tests for the changed package.
- **The check holds the replayed ask and only for this reason.** Replaying the #841
  ask at its recorded state (task at state commit `b3e749c2`, the validation briefing's
  question and summary, PR facts saved in `poc/pr841-facts/`): origin/main's
  `delivery_gate.py check` exits 0; the candidate exits 1, and the diff of the two
  outputs is the one new problem line and its `next:` line
  (`poc/replay-control-base.log`, `poc/replay-candidate-no-run.log`).
- **A run recorded at the asked trunk lets the ask through; a run at any other trunk
  does not.** A green run of the same head on trunk `546a1363` (the trunk CI saw,
  exit 0, `poc/runs/green-result.json`) passes an ask at that trunk and is refused for
  the ask at `eeee0023`; the red run at `eeee0023` holds with its exit shown.
- **How often it fires.** Of the last 40 squash-merged feature PRs on main, 24 merged
  onto a trunk that was not an ancestor of their head (GitHub compare `diverged`),
  16 onto one that was (`poc/trunk-moved-at-merge-40prs.txt`, 2026-11-12).
- **Cost of the run.** `test_design_surfaces.py` alone: about 15 s on the merge result.
  The full local unit-test list from `kc-dev-flow-2-tests.yml` (25 scripts, not the
  three that need the pinned Spacedock): see `poc/runs/full-suite-result.json`. Local
  FO minutes only; no CI minutes.
- **Existing tests.** `test_delivery_gate.py` on the PoC: 208 run, 2 failures, both the
  subtests of `test_required_check_read_adds_one_gh_call`, which count `gh` calls and see
  one more (`poc/test_delivery_gate-poc.log`).

### PRFAQ

**Proposition.** When main has moved past the head the Captain is asked to merge,
the First Officer (FO) cannot ask until it has run the package's tests on the result
of merging that head into today's main, or until the question says plainly that no
such run was made. The run is FO's, on its own machine, and leaves a record beside
the task.

- *What counts as "main moved"?* Main's tip is not an ancestor of the PR head. Only
  then does the merged tree differ from the tree validation tested.
- *Which tests?* The commands the workflow names (decision D1). #841 shows why the
  acceptance script is not enough.
- *What if main moves again after the run?* The record names the trunk it ran on; a
  different trunk at ask time holds again.
- *What does the Captain see?* One `point: merge-result:` line with the command, exit
  and tree, or the question's own `Merge result: not run: <reason>` line.
- *Does CI change?* No. No repository setting changes either.

```mermaid
flowchart TD
  A[FO runs delivery_gate.py check before the merge ask] --> B{GitHub compare: trunk tip an ancestor of PR head?}
  B -->|yes: ahead or identical| P[no merge-result rule; other checks as today]
  B -->|no: diverged or behind| C{merge/result-N.json with this head and this trunk?}
  C -->|yes, exit 0| G[point: merge-result line; ask may proceed]
  C -->|yes, exit not 0| H1[hold: the run on this trunk failed]
  C -->|none| D{gate text has 'Merge result: not run: reason'?}
  D -->|yes| N[point: merge-result not run; ask may proceed and says so]
  D -->|no| H2[hold: next line names merge-run or the not-run line]
  H2 --> R[FO runs delivery_gate.py merge-run task --pr ... -- command]
  R --> M[git merge-tree --write-tree trunk head; git archive tree into a temp dir; run command; remove temp dir]
  M --> W[write merge/result-N.json and .log]
  W --> A
```

### Chain checked, and the existing-code check

- **Spacedock 0.27.3:** `mods/pr-merge.md` runs `git merge-tree --write-tree "$BASE_SHA" "$CANDIDATE_SHA"`
  at push time as a conflict signal only; `merge guard` takes the verdict in and runs
  nothing. No test on the merge result. The PoC reuses its `merge-tree` mechanism.
- **kc-dev-flow-2 0.39.1 (origin/main):** `delivery_gate.py check` holds on head,
  CI, draft, `mergeable`, base and file list; `mergeable` is a textual-conflict signal.
  No merge-result run anywhere (`git grep -i "merge result\|merge-tree" origin/main -- kc-dev-flow-2`: 0 hits).
- **Adopters (read only):** qnow and subspace-relay carry Spacedock's `pr-merge.md`
  `merge-tree` step; no test run. subspace-web: no hit.
- **GitHub (its own API):** required-checks `strict` and merge queue would make GitHub
  do it, but both are repository-setting changes (Stop condition: Captain), and
  `strict` forces an update-branch that changes the head, which breaks the dispatched
  `Candidate:` match on 60% of PRs here.
- Conclusion: repair the existing seam, `delivery_gate.py check`, which FO already runs
  before every merge ask; add one subcommand that writes the record. No new script.

### Expansion plan (PoC to the Pilot bar and the Stop condition)

1. Fix the command source per D1: read `merge-test:` from the workflow README and
   require the record's command to equal it; refuse `merge-run` with no command.
2. Fold the merge-result point into the 12-point cap in `points_for` instead of
   prepending it, and save `merge_result` (record name or `not run`) in `ask-N.json`.
3. `question`: when the newest ask record says `not run`, require the
   `Merge result: not run:` line in the question file itself, not only the summary
   (Outcome: "told in the question").
4. `merge-run` fetch path: fetch `refs/pull/N/head` and the trunk only when an object
   is missing (PoC does); hold with exit 2 on a `merge-tree` conflict instead of a
   string exit in the record.
5. Tests in `test_delivery_gate.py`: the six replay cases as unit cases with the stub
   `gh` compare answer; update the two `gh`-call counts by one; a `merge-run` case on a
   two-commit fixture repository.
6. Docstring: one usage paragraph for `merge-run` and one hold sentence in `check`.
   No `references/sd/workflow.md` change: the hold's `next:` line carries the step at
   the moment it is due.
7. ADR, titled "A merge ask on a moved trunk carries a test run on the merge result"
   (number reserved by FO at dispatch), recording D1 and D2.
8. Adopters: one `merge-test:` line each at their next workflow sync; until then each
   moved-trunk ask in that adopter needs the not-run line.

### Worth questions

- **The hold at the merge ask.** Captain words: none yet; FO filed it from its own
  miss and the backlog gate approved the scope (「核准，照這個分組（建議）」). What breaks
  without it: a pair of PRs that each pass validation can still break main; #841 plus
  #843 broke 1 of 226 tests, blocked Release PR #840 and cost an 80-minute fix task.
  Premise that would make it unneeded: semantic collisions between concurrently merged
  PRs are rare enough to fix after the fact. Cheap test now: the 40-PR count shows the
  trunk moved under 24 of 40 merges; the collision itself was observed once in that
  window (this Bite), so the rule fires often and has caught one break in about two
  weeks. The Captain may judge that rate not worth a run per ask; that is D1/D2's cost.
- **The `merge-run` subcommand and its record.** Serves the same scope. Without it the
  hold has nothing to read and FO's run is a claim in prose. Premise that would make it
  unneeded: GitHub could be made to run CI on the new merge result without changing the
  head. Cheap test: a re-run of a `pull_request` run reuses its original merge commit
  (checked: run 42979280852 merged into `546a1363`), so a new run needs a new event or
  a setting change.
- **The not-run line.** Serves the Outcome's "or the Captain is told in the question".
  Without it every moved-trunk ask in an adopter without `merge-test:` is blocked.

### Words FO reads at each moment

Counted with `wc -w` over the check output lines (header lines of the replay log
excluded), base origin/main `8ce0eb605` against the PoC, on the #841 replay
(`poc/words.txt`):

| Moment | Base | Candidate |
| --- | --- | --- |
| Startup, idle on open PR, idle on merged PR, after archive | unchanged | unchanged: no README, mod or `pr_watch.py` change |
| Merge ask, trunk not moved | 187 | 187 (no new line) |
| Merge ask, trunk moved, FO runs `merge-run` first | 187 | 17 (`merge-run`) + 197 (`check`) = 214 |
| Merge ask, trunk moved, FO did not know (hold, run, re-check) | 187 | 117 + 17 + 197 = 331 |
| Merge ask with the not-run line | 187 | 195 |

`delivery_gate.py --help` stays 1227 words in the PoC; the expansion adds about 60.
FO's reading rises at the merge ask on a moved trunk; this task adds a step and does
not claim a reduction.

### Batch overlap

Files the design would change: `kc-dev-flow-2/scripts/delivery_gate.py` (`check`,
`points_for`, `write_record`, `question`, new `merge_run`, `main`, docstring),
`kc-dev-flow-2/scripts/test_delivery_gate.py`, a new ADR file in `docs/adr/` (one
number from the shared ADR index), and the workflow README `merge-test:` key of
`docs/dev2/README.md` (kc-dev-flow-2's adopted copy here; adopters at their sync).

| Task | Shared file or check | Order |
| --- | --- | --- |
| comment-check-reaches-delivery-gate (other session, ideation) | `delivery_gate.py` `check` (a new hold) and `write_record` (a new key); `test_delivery_gate.py` (`file_pages`, gh stub) | one after the other; either first, the second rebases |
| gate-question-facts-are-checked-before-the-captain-reads-them (batch) | its Scope names the delivery check's gate-text counting; if its design lands there, the same `check`/`question` text path | after this one if it touches `delivery_gate.py` |
| dispatch-close-out-archives-evidence-and-removes-scratch (batch) | its Scope asks how the delivery check tells a removed path from missing evidence; `merge-run` writes `merge/result-N.log` and removes its own temp dir | none shared yet; its rule should keep `merge/result-*` |
| held-and-closed-tasks-leave-the-design-queue (batch) | `pr_watch.py` only | none |
| each-task-records-stage-time-revises-and-interruptions (batch) | no file named yet | none known |
| adoption-asks-which-extensions (other session) | reads `delivery_gate.py` output for a word count only | none |
| adr-required-statement, adr-silent-undo-probe (other sessions) | the shared ADR number index | FO reserves numbers |
| journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (other sessions) | none found (`grep delivery_gate\|workflow.md\|merge ask` over each task file: 0 hits) | none |

Recommended order: comment-check-reaches-delivery-gate and this task one at a time
(either first); then gate-question-facts if it edits `delivery_gate.py`.

### Decisions for the Captain

- **D1. Which commands count as the run.** Recommend a `merge-test:` line in the
  workflow README naming the command, which the check requires the record to match.
  Why: #841's acceptance script would not have caught its break, so letting FO pick
  per ask invites the narrow choice; your past rulings leaned the same way (an
  `Override:` chose refusing branch refs over the flexible option). What gets worse:
  each adopter adds one README line at its next sync, and until then every moved-trunk
  ask there needs the not-run line. Alternative: FO names the command per ask, shown in
  the point line; no README key, weaker.
- **D2. When the rule applies.** Recommend "main's tip is not an ancestor of the PR
  head". Why: that is exactly when the merged tree differs from the validated one, and
  it needs no new dispatch field. What gets worse: it fires on about 60% of PRs (24 of
  40), wider than the Non-goals' reading "base did not move since validation"; a PR
  whose base moved before validation was dispatched is included, because validation
  still tested only the head. Alternative: record main's tip in each validation dispatch
  and fire only when it moved after that; narrower, and misses the pre-dispatch case.
- Not recommended, no ruling needed unless you want it: turning on "require branches
  to be up to date" or a merge queue (repository settings; both re-trigger validation
  through a changed head).

## Acceptance criteria

Paths are relative to the task folder `merge-ask-tests-the-merge-result/`. `CAND` is
the candidate's `kc-dev-flow-2/scripts/delivery_gate.py` (today: the PoC worktree's
copy at `e348d05b7`); `BASE` is origin/main `8ce0eb605`'s, extracted with
`git archive 8ce0eb605 kc-dev-flow-2/scripts | tar -x -C <dir>`. Each was run once on
the PoC on 2026-11-12; the implementation re-runs them on its candidate.

**AC-1** The #841 merge ask replayed at its recorded state is held for the merge result alone.
Evidence: `python3 -B poc/replay_841.py "$BASE" poc/replay-control-base.log` exits 0,
and `python3 -B poc/replay_841.py "$CAND" poc/replay-candidate-no-run.log` exits 1 with
`the trunk moved since this head (diverged, trunk eeee002303ac) and no merge-result run is recorded`;
the two outputs differ only by that line and its `next:` line.
Falsifier: remove the merge-result call from `check` and the candidate exits 0.
Ran: base exit 0, candidate exit 1; `poc/replay-control-base.log`, `poc/replay-candidate-no-run.log`.

**AC-2** The same ask with a passing run recorded at its head and the asked trunk passes and shows the run.
Evidence: `python3 -B poc/replay_841.py "$CAND" poc/replay-candidate-green-record-at-its-trunk.log --result poc/runs/green-result.json --trunk 546a136386c94c58e430c91a6f3457b38bd73880`
exits 0 and prints `point: merge-result: 'python3 -B kc-dev-flow-2/scripts/test_design_surfaces.py' exit 0 on 0cea91ffa2eb`.
The record is a real run (head `6da9a765` merged onto `546a1363`, the trunk #841's CI
used); #841's run at its real ask trunk is red, so the pass case cannot be shown on it.
Falsifier: change the record's `exit` to 1 and the replay exits 1.
Ran: exit 0; `poc/replay-candidate-green-record-at-its-trunk.log`.

**AC-3** A run recorded on another trunk does not satisfy the ask.
Evidence: `python3 -B poc/replay_841.py "$CAND" poc/replay-candidate-stale-green-record.log --result poc/runs/green-result.json`
(green run on `546a1363`, ask at `eeee0023`) exits 1 with the no-run line.
Falsifier: drop the `trunk` comparison in `merge_result_problem` and it exits 0.
Ran: exit 1; `poc/replay-candidate-stale-green-record.log`.

**AC-4** A failing run on the asked trunk holds the ask and names the exit.
Evidence: `python3 -B poc/replay_841.py "$CAND" poc/replay-candidate-red-record.log --result poc/runs/red-result.json`
exits 1 with `the merge-result run result-1.json on trunk eeee002303ac exited '1'`.
Falsifier: accept any matching record regardless of exit and it exits 0.
Ran: exit 1; `poc/replay-candidate-red-record.log`.

**AC-5** With no run, a `Merge result: not run: <reason>` line lets the ask through and shows it.
Evidence: `python3 -B poc/replay_841.py "$CAND" poc/replay-candidate-not-run-line.log --not-run`
exits 0 with `point: merge-result: not run (the ask says so)`.
Falsifier: without the line the same replay exits 1 (AC-1); the #841 text's own
sentence ("the acceptance script was not rerun on the merged result") is in every
replay and does not count as the line.
Ran: exit 0; `poc/replay-candidate-not-run-line.log`.

**AC-6** When main's tip is an ancestor of the head, nothing new is asked.
Evidence: `python3 -B poc/replay_841.py "$CAND" poc/replay-candidate-trunk-not-moved.log --status ahead --trunk e8664a72b0f904e5dda3c391d52ab3abaca876b4`
exits 0 with no `merge-result` line and 187 output words, equal to base (`poc/words.txt`).
Falsifier: treat `ahead` as moved and it exits 1.
Ran: exit 0; `poc/replay-candidate-trunk-not-moved.log`, `poc/words.txt`.

**AC-7** `merge-run` tests the tree that lands and reproduces the #841 break.
Evidence: `bash poc/ac_tree_and_scratch.sh "$CAND" <code repo> <workflow dir>` prints
equal trees `3ba409485baf…` for `merge-tree eeee0023 6da9a765` and `571a7bd8^{tree}`;
`python3 -B "$CAND" merge-run <task> --pr iamcxa/kc-claude-plugins#841 --head 6da9a765… --trunk eeee0023… -- python3 -B kc-dev-flow-2/scripts/test_design_surfaces.py`
exits 1 with 1 failure in 226, while the head alone passes 224.
Falsifier: run on `--trunk 546a1363` and it exits 0 (AC-2's record).
Ran: script exit 0; merge-run exit 1; `poc/ac_tree_and_scratch.log`, `poc/runs/red-result.json`, `poc/runs/red-result.log`, `poc/runs/head-only-test_design_surfaces.log`.

**AC-8** `merge-run` removes its temporary directory.
Evidence: the same script runs `merge-run ... -- true` with `TMPDIR` set to a fresh
empty directory and counts 0 entries left.
Falsifier: remove the `shutil.rmtree` in `merge_run`'s `finally` and the count is 1.
Ran: exit 0, 0 entries left; `poc/ac_tree_and_scratch.log`.

### Not provable now

- `test_delivery_gate.py` fully green on the candidate: the PoC fails the two
  `test_required_check_read_adds_one_gh_call` subtests (one more `gh` call); the
  expansion updates them (`poc/test_delivery_gate-poc.log`).
- The `merge-test:` README match (D1) and the `question` check that the not-run line
  sits in the question itself (expansion items 1 and 3): not built in the PoC.
- A live merge ask on an open PR in this workflow or an adopter after release: needs a
  real PR whose trunk moved; first possible after the package release.
- The three CI tests that need the pinned Spacedock were not run in the cost
  measurement; the local run does not equal CI.
