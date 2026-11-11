---
title: When a story's task is archived, FO tells the Captain how much of the release remains, and the story shows the pull requests that finished it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: done
gates:
    version: 1
    records:
        - id: gate:story-done-reports-release-remaining:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:story-done-reports-release-remaining-backlog-1
              briefing:
                id: briefing:story-done-reports-release-remaining:backlog:attempt-1:revision-1
                digest: sha256:bc068bffc4730bd93d2deb7690dcb9ecf6c545c3f8ed5c5f68a3b3849b8252ab
                room-ref: ./story-done-reports-release-remaining/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:story-done-reports-release-remaining:backlog:1
                briefing: briefing:story-done-reports-release-remaining:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-11T01:18:27.351416Z"
                decision: approve
                reason: 'The Captain chose 「五張都核准（建議）」 (host question dialog, 2026-11-11), answering 「決定：第 21 批這五張要不要進設計階段。我建議五張都核准：故事做完回報切片進度、發版後鋪開到採用 repo 與法規檢查、超預算要停與重大發現先對照不做清單、工人收到的推送說明與狀態提交工具一致、拒絕一個指令不等於全停。核准代表接受每張任務檔寫的範圍、預算與停止條件，並各派一個設計工人；不代表接受任何設計或修法。前三張標了方向要先對齊，派工前我會各問你一題。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:story-done-reports-release-remaining:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:story-done-reports-release-remaining-ideation-1
              briefing:
                id: briefing:story-done-reports-release-remaining:ideation:attempt-1:revision-1
                digest: sha256:1b6df17b6496f29ccef6f634239318046832b170e1d645dbe0297e1a5f5623f9
                room-ref: ./story-done-reports-release-remaining/review/ideation/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-11-11T02:19:55.50269Z"
                reason: The Captain answered the six-design question with 「這次比較複雜，一題題過審」 (host question dialog, 2026-11-11); each design gets its own question.
            - id: gate-attempt:story-done-reports-release-remaining-ideation-2
              briefing:
                id: briefing:story-done-reports-release-remaining:ideation:attempt-2:revision-1
                digest: sha256:77a5c368d05dee83d2745855d595d4ec2b353954d7701b347a0e6eb3ea0a3c7c
                room-ref: ./story-done-reports-release-remaining/review/ideation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:story-done-reports-release-remaining:ideation:2
                briefing: briefing:story-done-reports-release-remaining:ideation:attempt-2:revision-1
                by: person:captain
                at: "2026-11-11T02:30:26.001623Z"
                decision: revise
                reason: 'The Captain chose 「退回補上「任務必須標故事」（建議）」 (host question dialog, 2026-11-11), answering 「決定：要不要核准「故事做完回報切片進度」的設計並開始實作。我建議照設計的建議核准：每張有切片的任務歸檔時，我在對話裡回報這個切片完成與剩餘的故事和每個完成故事的 PR，不自動重畫畫布；PR 連結現算、只出現在回報裡，畫布和地圖檔不變；不做故事宣告，回報裡改列「已建檔任務」的計數。核准即接受這三項；要畫布上顯示 PR 或要做故事宣告，請選對應的選項。」. Override: recommended approving the design as written; Captain chose sending it back to add that each task records its story or none; area: journey progress. After his questions 「故事宣告為何數量差異那麼大？」 and 「我確定一下故事宣告的意思，是每張任務都要宣告它屬於哪張故事是嗎？如果不強制宣告（也可能沒有對應故事）那這樣怎麼算出切片都完成了？」 FO changed its recommendation in chat to the option he chose. Ask of the ideation worker: keep the design and add one step, each task at the backlog gate records the story it belongs to or that it belongs to none with the reason, and say where it is checked.'
            - id: gate-attempt:story-done-reports-release-remaining-ideation-3
              briefing:
                id: briefing:story-done-reports-release-remaining:ideation:attempt-3:revision-1
                digest: sha256:3a29ce7da3ecda8b80495ac30c372aec0e93f20a01b1f7b181549c50b31e7091
                room-ref: ./story-done-reports-release-remaining/review/ideation/briefing-3
              resolution:
                type: Resolution
                id: resolution:spacedock:story-done-reports-release-remaining:ideation:3
                briefing: briefing:story-done-reports-release-remaining:ideation:attempt-3:revision-1
                by: person:captain
                at: "2026-11-11T03:11:17.708754Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-11), answering 「決定：要不要核准「故事做完回報切片進度」補完後的設計並開始實作。我建議核准：照你上次的要求，設計加了一步，有地圖擴充的流程裡每張任務在待辦關卡要寫一行「屬於哪個故事」或「不屬於任何故事加理由」，沒寫就擋；其他照原設計：每張有切片的任務歸檔時我在對話裡回報切片完成與剩餘的故事和每個完成故事的 PR，不自動重畫畫布，PR 連結只出現在回報裡，不做故事宣告、改列已建檔任務的計數。核准即接受這些，以及這一步上線當天 relay 有 31 張、qnow 有 11 張待辦任務會被點名要補那一行。」. Recommendation: followed. Before choosing he asked 「確認下如果沒有用故事地圖的使用者會怎樣」 and FO answered in chat from the design: the rule applies only where the workflow README lists journey-map.'
              application:
                target-stage: implementation
                state: consumed
        - id: gate:story-done-reports-release-remaining:validation
          stage: validation
          attempts:
            - id: gate-attempt:story-done-reports-release-remaining-validation-1
              briefing:
                id: briefing:story-done-reports-release-remaining:validation:attempt-1:revision-1
                digest: sha256:62597bebf43ce613e90f238e6cb16ede5d7ef73e4a8209927088164c3c65ff02
                room-ref: ./story-done-reports-release-remaining/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:story-done-reports-release-remaining:validation:1
                briefing: briefing:story-done-reports-release-remaining:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-11-11T07:41:59.115078Z"
                decision: approve
                reason: 'The Captain chose 「合併（建議）」 (host question dialog, 2026-11-11), answering 「決定：合併 #839（故事進度的前半：旅程地圖的進度工具改成回報「這個故事和這個切片各有幾張已開的任務做完」，並列出完成它的 PR）嗎？建議合併。同意即接受：這一半合併後還不會自動回報，要等後半 #843（任務必須標故事、歸檔後提醒回報）合併並發版才生效，#843 我會另外問你；在 relay 上的真實歸檔回報要等發版後才驗；Copilot 因額度不足沒有審過這個版本。 Squash merge with --match-head-commit fd1caa475f85483cf5c4031a1e58656ff5d3eaff, and removing its clean, pushed worktree. Approval also covers later external-review rounds on this PR, unless he says he merges or holds.」. Recommendation: followed.'
              application:
                target-stage: done
                state: consumed
started: 2026-11-11T01:22:31Z
worktree: .worktrees/spacedock-ensign-story-done-reports-release-remaining
pr: pr-merge:843
verdict: PASSED
completed: 2026-11-11T08:05:12Z
archived: 2026-11-11T08:05:12Z
---

## Scope

- Source: the Captain 「我有個需求/想法，我覺得每張票作完之後，如果有同時有跑地圖ext，那應該要每張故事票做完就告訴我這個切片還剩下多少，這樣我才能知道離終點多遠。因為像是relay那邊一次要做兩個切片，已經做了大概兩天，但我如果沒有主動問就沒辦法知道做到哪裡了。這裡也要評估是否每個故事做完就同步更新畫布與地圖，更快反應狀況。以及，是否地圖應該記錄某個故事是因為哪些pr完成才完成的？等於切片地圖可以連結到完成它的pr？適合嗎？」 (chat with this FO, 2026-11-11).
- Selected for batch 21: the Captain chose 「放 1 到 5（建議）」 (host question dialog, 2026-11-11), answering 「第 21 批要放哪幾張？我建議放清單的 1 到 5：故事做完回報切片進度、發版後鋪開到採用 repo 與法規檢查、超預算要停與重大發現先對照不做清單、狀態提交自動推送與派工單矛盾、拒絕一個指令不等於全停。選完後我只為被選中的建任務檔，再一次請你過待辦關卡；選進來不代表接受任何設計。」.
- Package fact (FO read 2026-11-11): kc-journey-map skill kc-journey-progress runs `lib/journey-progress.mjs <journey.yaml> --workflow-dir <dir> [--draw <room>]` only "when explicitly refreshing"; kc-dev-flow-2 0.38.1 extensions/journey-map/EXTENSION.md joins FO at three points (a ruling answering a map question, before merge guard, after archive) and none runs the progress reader or reports to the Captain. `grep -n "pr\\b\\|pull" kc-journey-map/lib/progress.mjs` printed nothing (FO run 2026-11-11), so the observation carries no pull request.
- Known dependency (the backlog task journey-map-progress-and-provenance, its relay evidence of 2026-10-14, not re-read on relay today): no relay story carried `journey-required-tasks`, so the reader reports every story unverified there. The design says how a task joins its story's declaration when it is approved into the story, or names another way the count becomes real, and says what it takes from that task and what it leaves.
- FO's assessment given to the Captain in chat (not a ruling): report after each archive and redraw the canvas; keep progress derived from task state instead of writing it into the map file; derive story-to-PR links from each task's `pr:` value instead of storing them in the map.
- Surface note: this seed records no surface. If the design adds or changes anything a person sees on the canvas (a link, a mark), ideation records the `ui` surface and what it owes before its gate.
- Non-goals: the evidence ladder, ADR references and drawing provenance of journey-map-progress-and-provenance; one journey spanning several workflows; a background refresh.

## Budget
- One PR to kc-journey-map (reader output and canvas) and one to kc-dev-flow-2 (the journey-map extension step), or one PR if the design shows they cannot be split.

## Stop condition
- On a real adopter map with at least one declared story, archiving that story's last task makes FO report done and remaining stories for the release with each finished story's pull requests; or the design shows why not and says what was learned.

## FO alignment

Alignment: needed at ideation; what FO reports, whether the map file stores anything, and how much of journey-map-progress-and-provenance this takes are the Captain's call.
Result: the Captain chose 「交給設計比較」 (host question dialog, 2026-11-11), answering 「「故事做完回報切片進度」這張任務的設計方向要怎麼定？我建議：每張故事票歸檔後 First Officer 主動回報切片完成與剩餘並重畫畫布；進度和 PR 連結都從任務狀態現算、不寫回地圖檔；並把「任務獲准進入故事時自動記進故事的宣告」包進來，讓 relay 算得出數字。這是設計的方向，細節與證明仍在設計關卡由你核准。」. FO's recommendation was not taken: the design compares the choices and he picks at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Design

Profile: pilot. Recommended route: after FO archives a task that names a journey release,
FO runs one kc-journey-map command and puts its five-to-seven lines in the archive message:
how many of the release's stories are done and which, with their pull requests, which are
in progress and which have no task. Progress and pull request links
are computed from task state at that moment and are never written into the map file. The
canvas is not redrawn by this step. The story declaration step is not taken; instead the
reader adds a second count, from the tasks filed under each story, beside the declared
status it has today. Three choices below are the Captain's (`### Decisions for the
Captain`); everything else follows from measured facts.

### PRFAQ

**After this ships**, when FO archives a story's task on relay, its archive message says,
for example: "release owner-account: 1 of 4 stories have every filed task done; 1 in
progress; 2 have no task. Story inbox-home: 1 of 1 filed tasks done; pull requests:
spacedock-dev/subspace-relay#999." The Captain learns how far the slice is from its end
without asking, at each archive.

- **Q: Why not just run today's progress reader?** On relay it reads 182 of 184 stories
  as unverified, and on qnow all 190. Its count needs one task per story to declare the
  story's full task list, and relay's declarations go stale (measured below).
- **Q: Is "every filed task done" the same as "story done"?** No. Work not yet filed
  cannot be counted. The report says "filed", and the declared status, the canvas colours
  and the release-walk prompt keep today's meaning.
- **Q: Does the map file change?** No (D2 B1). A map-file record is option B3; ADR 0031,
  a related ruling, rejected a story field written without the Captain accepting an edit.
- **Q: What about qnow?** Of 78 tasks that name the qnow journey, 4 name a story and 21 a
  release. The report counts the release-only tasks on their own line, which tells the
  Captain the count is incomplete there. From now on, the added step makes each new qnow
  task name its story or say it has none; old tasks are not backfilled.
- **Q: How does a slice read complete if some tasks belong to no story?** Every new task
  says its story or "none" before its gate (`### Added step`). A task with no story is
  outside the story count; one that names the release but no story gets its own line. The
  release reads "complete by filed tasks" when every story's filed tasks and every such
  release task are done.

### Facts checked (chain order, 2026-11-11)

- **Spacedock 0.27.2** (`spacedock --help`; `merge guard` in fo-merge-core.md of plugin
  0.27.3). Archiving is the merge guard's finalize step, and it prints no story or release
  progress. `spacedock status --set` on an archived task refuses with "archived entity is
  read-only" (scratch copy of relay). No unarchive or reopen command is listed or answers
  `--help`.
- **kc-dev-flow-2 0.38.1** (origin/main). The journey-map extension joins FO after the
  archive only for the footprint fold (50 words, `### Words` below). The progress reader
  runs only inside `release_acceptance.py due`, called by `pr_watch.py tasks`. It prints a
  line only when a whole release reads `pending delivery acceptance` (ADR 0056).
- **kc-journey-map 1.10.0** (origin/main and the installed cache are the same version).
  `lib/progress.mjs` takes six fields, and `pr` is not among them. A story counts only with
  exactly one declaring member whose list equals the members. `journey-progress.mjs` takes
  `--draw <room>`. Its draw check (`drawn.status < 200 || drawn.status >= 300`) does not
  catch `renderToRoom`'s `{refused}` result, which carries no `status`, so a refused
  redraw of a hand-edited room would print as success. This was read in the code, not
  exercised.
- **Siblings.** Relay's interim practice is a "belongs to story <card> (<release>)" line at
  each backlog gate (relay evidence in journey-map-progress-and-provenance). No adopter
  README names a canvas room or `JOURNEY_API`.

### Measurements (read-only clones in a scratch directory, 2026-11-11)

Pins: relay `main` 0fce8229, relay `spacedock-state/dev2` 13ef3567; qnow `next`
ebc59cf9, qnow `spacedock-state/dev2` 78a76aa2; this repository origin/main with state
f55ce76e. Copy the state clone to `<code>/docs/dev2/.spacedock-state`, then count with
`spacedock status --workflow-dir <code>/docs/dev2 --archived --all-fields --limit 0 --json`.
Read progress with `node <kc-journey-map 1.10.0>/lib/journey-progress.mjs <map>
--workflow-dir <code>/docs/dev2`.

| Repository (map) | Map stories | Tasks on the journey | Declaring tasks | Reader today | Counted by filed tasks |
| --- | --- | --- | --- | --- | --- |
| relay (`spacedock-review.yaml`) | 184 | 62 (41 name a story) | 5 | 2 gap, 182 unverified, 27 orphans | 11 all done, 6 in progress, 167 no task |
| qnow (`qnow.yaml`) | 190 | 78 (4 name a story, 21 a release) | 0 | 190 unverified, 77 orphans | 0 all done, 1 in progress (branch-price-copy, implementation, r14/copy-prices-from-branch: the only task on a map story) |
| this repository (`kc-decision-log/journey.yaml`) | 30 | 0; dev2 does not list `journey-map` | 0 | not run: no journey task | none |

- **Why relay's declarations are stale** (full-history clone, `git log --reverse -G`).
  Each of the 3 stale declarations was written on 10-13 before its declaring task was
  archived the same day. Every extra member joined after that archive. For example, for
  get-started-page the declaration was written at 10:34 and the declarer archived at 14:07;
  limit-observability joined at 19:37. agent-reviews-from-link gained 3 members after its
  declarer was archived at 18:57, and owner-sees-all gained 2 after 14:48.
- **Can a stale declaration be repaired?** Not by FO under Spacedock 0.27.2 with reader
  1.10.0. In scratch, setting a superset declaration on the live member
  agent-front-door-publish left get-started-page unverified ("One confirmed complete
  mapping is required"), because the archived declaration cannot be cleared.
- **Positive path.** In scratch, `--set inbox-home status=done pr=pr-merge:999` moved
  owner-account from 0 of 4 stories (2 gap, 2 unverified) to 1 of 4, with inbox-home
  `exists`. Each read took 13.6 to 14.7 s and printed 5186 words of JSON. FO cannot be
  asked to read that at every archive, so this design adds `--report`.
- **`pr:` values on relay's 62 journey tasks.** 40 are `pr-merge:N`, 1 is `owner/repo#N`,
  1 is a URL and 20 are empty. `pr-merge:842` (spacedock-install-beta) is a Spacedock pull
  request; `gh pr view 842 --repo spacedock-dev/subspace-relay` finds none. So a
  `pr-merge:N` value carries no repository, and a link built from the workflow's remote is
  wrong for 1 of 40 values.
- **Was today's after-archive fold step run on relay?** The state cannot say: 12 archived
  `footprints.jsonl` files exist, and no task body records a `journey-map fold:` line,
  because the archive message lives in chat.

### Existing-code check

This change adds a capability: a progress report at archive, and pull request references.
- **Need.** The Captain's words in Scope, and he is the consumer, at each archive.
- **Completeness.** The progress reader works end to end (exercised above). An FO step
  that reports progress was not found, by two bounded searches: `git grep -n
  journey-progress origin/main -- kc-dev-flow-2` finds only `release_acceptance.py due` via
  `pr_watch.py`, and the extension's after-archive bullet names only the fold. Pull request
  data in progress was not found either: `git grep -c '\bpr\b' origin/main --
  kc-journey-map/lib/progress.mjs` prints nothing.
- **Use or repair.** Extend the reader in place (a `--report` mode and an additive
  `members` count). Reuse the extension's existing after-archive join point. Add no new
  tool, schema family or README key.
- **Exclusions.** A manual refresh by a person (kc-journey-progress) remains, and is not a
  consumer FO can rely on.

### Change (recommended choices: D1 A1, D2 B1, D3 C3)

**kc-journey-map PR (merges first, as the producer; ADR 0056 precedent).**
- `lib/progress.mjs` gives every story a `members` object: `{tasks, done, prs}`, counted
  from every task carrying that journey, release and story tuple, whether or not a
  declaration exists. `prs` is a list of `{task, ref}` for done members with a nonempty
  `pr:`. `status`, `requiredTasks`, `doneTasks`, `taskIds`, the release `status` and
  `acceptance` are computed exactly as in 1.10.0.
- Each release row gets `members: {storiesDone, storiesOpen, storiesEmpty}`, from the
  story `members` counts.
- `ref` rules:
  - `pr-merge:N`, `N` or `#N` becomes `<owner>/<repo>#N`, with owner and repo taken from
    the workflow checkout's GitHub `origin` (ssh or https); without one it stays `#N`.
  - `owner/repo#N` is kept as it is.
  - `https://github.com/o/r/pull/N` becomes `o/r#N`.
  - `local-merge:<sha>` becomes `local merge <first 7 of sha>`.
  - Any other nonempty value is kept verbatim.
- `journey-progress.mjs <map> --workflow-dir <dir> --report <slug>` prints text, not
  JSON, built from the same observation:

  ```
  journey progress: <journey>/<release> after <slug> (<status>)
  story <story>: <done> of <tasks> filed tasks done; declared: <exists | gap | unverified | none>
  pull requests: <ref>, <ref>            (or: pull requests: none recorded)
  release <release>: <a> of <n> stories have every filed task done; <p> in progress; <z> have no task
  done: <story> (<ref>, <ref>), ... (stories with every filed task done; at most 5, each with at most 3 refs, then "and <x> more")
  in progress: <story> <done>/<tasks>, ... (at most 5, then "and <x> more")
  release tasks with no story: <done> of <n> done   (only when n > 0)
  not on the map: <k> tasks name a story this map does not hold   (only when k > 0)
  canvas: not redrawn; draw it with kc-journey-progress
  ```

  The two `story`/`pull requests` lines are omitted for a task with a release and no story.
  Exit codes:
  - 0: the report is printed, unverified stories included.
  - 1: the task read failed; it prints one line, `journey progress not run: <diagnostic>`.
  - 2: invalid arguments, or a slug that names no release of this map.
- `lib/schemas.mjs` and `lib/contract-versions.json`: the journey-progress field table
  gains the `members` rows, and its version moves from 1.0.0 to 1.1.0 (an additive change;
  the wire string stays `journey-progress/v1`, whose pin is major only).
  `skills/kc-journey-progress/SKILL.md` gains one paragraph on `--report` and on
  `members` ("filed tasks, not an exhaustive scope").
- `lib/progress.test.mjs` covers the new behavior; `lib/schemas.test.mjs` pins the exact
  story and release keys and `journey-progress 1.0.0`, so it changes with the table.
- Consumer check, unchanged: kc-dev-flow-2's `test_release_acceptance.py` runs the in-repo
  `journey-progress.mjs` and asserts the `acceptance` meaning (its `live_producer` case);
  its fixture `journey-progress-v1.json` carries no `members` and stays valid under an
  additive change.

**kc-dev-flow-2 PR.**
- `extensions/journey-map/EXTENSION.md`: the Needs line names `lib/journey-progress.mjs`
  with `--report` (9 words). "at three points on a journey task" becomes "at four points",
  and the journey-task definition sentence ends ", except the progress report" (5 words),
  because the new step also runs for a task with a release and no story. The Joins list
  gains one bullet after the fold bullet (50 words):

  > Right after archiving a task that has `journey` and `journey-release`, FO runs `node
  > <kc-journey-map>/lib/journey-progress.mjs <journey file> --workflow-dir <dir> --report
  > <slug>` and puts its lines in the archive message to the Captain. A missing
  > kc-journey-map, one without `--report` (exit 2) or a failed read is `journey progress
  > not run: <reason>`.

  kc-journey-map 1.10.0 run with `--report` exits 2 with its usage line (run 2026-11-11),
  so an adopter still on 1.10.0 gets the `not run` line, not a silent pass.
- Added step (see `### Added step`):
  - `scripts/design_surfaces.py`: the seed-mode `Story:` rule, gated on the workflow
    README listing `journey-map`.
  - `scripts/design_surfaces.py` default check: the `Story:` and frontmatter consistency
    rule.
  - `scripts/test_design_surfaces.py`: its cases.
  - `scripts/test_pr_watch.py`: the idle-look case (AC-13).
  - `extensions/journey-map/EXTENSION.md`: one backlog bullet (46 words). "four points"
    becomes "five points", and the definition sentence ends ", except the progress report
    and the story line" (+4 more).
  - `docs/adr/<number>-a-journey-workflows-new-seed-records-its-story-or-none.md` (number
    reserved by FO).
- Unchanged: `references/sd/workflow.md`, `pr_watch.py`, `map_footprint.py` and the
  release-acceptance extension.

### Added step: each task records its story or none (Captain revise, 2026-11-11)

The Captain sent the design back at the ideation gate: 「退回補上「任務必須標故事」（建議）」,
after asking 「如果不強制宣告（也可能沒有對應故事）那這樣怎麼算出切片都完成了？」. D1 to D3
stand. One step is added. Every new task, before its backlog gate, says which map story it
belongs to, or that it belongs to none and why. Both answers pass; only a missing answer is
refused. With the step in force, a release's count of filed tasks covers every task FO has
admitted since the step landed.

- **Record.** One line under `## FO alignment`, written by FO before the seed check:
  `Story: <story id> (<release id>)` or `Story: none: <reason>`, for example
  `Story: none: workflow maintenance`. Relay already writes this form freely (2 of its 137
  tasks, e.g. `Story: entry-random-name ("…", Release 2.1)`), so the check reads only the
  first token. When the Captain approves the task into the story, FO still sets
  `journey`, `journey-release` and `journey-story` as the Release review bullet says. The
  reader and the report read only those frontmatter fields, never the `Story:` line.
- **Where it is checked (recommended W1): the seed check.** `design_surfaces.py check
  --seed` gains the rule, applied only when the workflow README (the nearest ancestor
  `README.md` whose frontmatter has `stages:`) lists `journey-map` under `extensions:`. FO
  already runs that command before `gate prepare`. The idle look already runs it on every
  backlog task that still needs preparation (`seeds()` in `pr_watch.py`), and prints the
  existing `next: the seed check fails …` line. So a skipped step surfaces without a new
  FO command.
  - It refuses: no `Story:` line; an empty value; `none` with no reason; a line inside a
    code fence.
  - It accepts any other `Story: <token> …`.
  - It does not check that the story is on the map; the Release review owns membership.
- **The line and the counted fields stay together: a consistency rule in the design
  check.** The report counts frontmatter, not the line. So the default `design_surfaces.py
  check`, which FO runs before every ideation gate, refuses when:
  - a `Story: <id> …` line's `<id>` differs from the frontmatter `journey-story`, or
    `journey-story` is empty (FO approved it into a story but never set the fields);
  - `Story: none: …` sits beside a non-empty `journey-story`.

  It applies only where `journey-map` is listed. Its refusal is "'Story:' names `<id>`
  but journey-story is `<value>`", 9 words plus the values. Limit: a task on the POC
  route has no ideation gate, so its line and fields are not compared.
  - Other places considered:
    - W2, an FO alignment line with no check. It costs no code, but it is a prose step FO
      can skip, the same failure as today.
    - W3, a separate journey-map extension command at backlog. It is one more command for
      FO to remember, and the idle look would not run it.
- **Applies to.** Workflows that list `journey-map`: relay and qnow today. This workflow
  does not list it, so none of its 230 tasks would need a line. Relay's suggestion was
  every task in every workflow; this design keeps it to workflows with a map, because
  outside them a `Story:` line has no reader.
- **Cost per task.** FO writes one line of 2 to 10 words. For a task outside the map it
  writes the reason; for a task on the map it looks up the story id in the journey file,
  which the Release review already reads for a journey task. The seed check adds no
  measurable time. The refusal prints 20 words, only when the line is missing.
- **How the report counts a task that records no story.**
  - A task with `Story: none` and no journey fields is outside every release, and the
    report does not count it.
  - A task with `journey-release` but no `journey-story` (a release task with no story)
    is counted on its own line: `release tasks with no story: <done> of <n> done`.
  - A task naming a story the map does not hold stays under `not on the map`.
  - The report's release line says `complete by filed tasks` only when every story has
    every filed task done and every release task with no story is done. It still says
    "filed", which is not delivery acceptance.
- **Reach and rollout.** The rule reaches what the seed check already reaches: every
  backlog task that still needs preparation. Archived tasks and tasks past backlog are not
  checked or backfilled; relay's interim practice already chose not to backfill completed
  tasks. Existing backlog tasks are reached too, not only new ones. On the day it ships,
  the idle look names relay's 31 and qnow's 11 backlog tasks that have FO alignment and
  no `Story:` line (measured below), and keeps naming them at every look until each gets
  one. Rollout step: when an adopter takes the release, its FO writes the line on each
  named task in one pass (31 lines on relay, 11 on qnow).
  - Profiles: `seeds()` does not filter by profile, so POC-profile tasks in these
    workflows are reached (relay 2, qnow 1 among the named).
  - A separate POC workflow (no ideation stage) is not reached: `seeds()` returns
    nothing there.
- **What it takes from journey-map-progress-and-provenance.** All of Gap 1: relay's
  suggestion "every task records its story or `no story: <reason>` at the backlog gate,
  and the seed check refuses neither". It leaves:
  - Gap 2: the declaration at approval (D3 kept C3).
  - Gap 3: several workflows.
  - The backfill proposal in its relay evidence: 20 relay dev2 tasks proposed for a
    story, 12 infra, 2 with no story, across 49 tasks on 2026-10-14.
  - The evidence ladder, ADR references and drawing provenance.
- **ADR draft** (the seed check's required records change, which is the reopen condition
  in ADR 0041's Consequences; FO reserves the number at implementation). Short title: "a
  journey workflow's new seed records its story or none".
  - Words: the Captain's 「退回補上「任務必須標故事」（建議）」, in the ideation gate
    resolution of this task, with the question it answered.
  - Options considered: W1 the seed check (chosen); W2 a prose line only; W3 a separate
    extension command; every workflow instead of journey-map workflows.
  - Protects: `kc-dev-flow-2/scripts/design_surfaces.py`, the seed check's `Story:` rule.
  - Decision: in a workflow listing `journey-map`, a new seed needs `Story: <story id>
    (<release id>)` or `Story: none: <reason>` under `## FO alignment`. Both pass. The
    check reads presence and form only. ADR 0041 otherwise stands.
  - Consequences: skipping the seed check still bypasses the refusal, but the idle look
    names the task. A wrong story id passes until the Release review. Archived tasks keep
    no record. Existing backlog tasks are named until each gets its line.
  - Lands ADR: ruling "in a journey-map workflow a backlog task records its story or
    none, and both pass", short title "a journey workflow's new seed records its story or
    none".

```mermaid
flowchart TD
  S[FO files a new task in a workflow listing journey-map] --> L[FO writes Story: story id with release, or Story: none: reason]
  L --> C{seed check: Story line present, not fenced, value non-empty, none has a reason?}
  C -- no --> R[seed check exit 1; the idle look prints the seed-check next: line]
  R --> L
  C -- yes --> G[backlog gate prepared and put to the Captain]
  G --> A{Captain approves the task into a story?}
  A -- yes --> F[FO sets journey, journey-release, journey-story]
  A -- no story --> N[no journey fields: outside every release count]
  F --> P[report counts it under its story]
```

**Would have been refused** (replay over every task, live and archived; the step itself
checks only backlog tasks that still need preparation). Command: `python3 -I` over each state's `*.md`, `*/index.md` and
`_archive/` with PyYAML frontmatter, at relay state 77f5bb4e, qnow state 03838f9 and this
workflow's state 10149f1c5, 2026-11-11.

| Workflow | Tasks (live / archived) | No `Story:` line today | Of those, also no `journey-story` and no "belongs to story", "infra:" or "no story" wording: live / archived | Live backlog tasks the idle look would name (upper bound) |
| --- | --- | --- | --- | --- |
| relay dev2 | 137 (55 / 82) | 135 | 35 / 45 | 33 (23 by substance) |
| qnow dev2 | 163 (94 / 69) | 163 | 90 / 58 | 81 (79 by substance) |
| this workflow (journey-map not listed: 0 refused) | 230 (79 / 151) | 230 | 77 / 145 | 55 if it were listed |

Measured reach of the idle look (`spacedock status --next --json` `ready_gates` rows at
`backlog` / `needs-preparation`, on the replays with each adopter's README; relay code
0fce822 state 77f5bb4e, qnow code ebc59cf state 03838f9):
- relay: 33 rows. 31 have FO alignment and no `Story:` line (pilot 22, prod 5, poc 2, no
  profile 2) and would be named. 2 have no FO alignment, which `seeds()` skips.
- qnow: 80 rows. 11 would be named (pilot 9, prod 1, poc 1). 69 have no FO alignment and
  are skipped.

Both relay `Story:` lines sit under `## FO alignment`, unfenced
(`_archive/entry-without-name-field.md`, `_archive/own-comments-follow-account.md`), and
each agrees with its frontmatter `journey-story`; so 135 stands for the stricter rule.

### Flow

```mermaid
flowchart TD
  A[FO: merge guard archives a task] --> B{task has journey and journey-release?}
  B -- no --> Z[no progress step]
  B -- yes --> C{kc-journey-map with --report present?}
  C -- no, exit 2 --> N[archive message: journey progress not run: reason]
  C -- yes --> D[reader observes tasks via spacedock status]
  D -- read failed, exit 1 --> N
  D -- exit 0 --> E[report lines: release a of n done, in progress, no task, not on the map]
  E --> F{task names a story?}
  F -- yes --> G[story line: filed tasks done, declared status; pull request refs]
  F -- no --> H[release lines only]
  G --> I[FO puts the lines in the archive message to the Captain]
  H --> I
  I --> J[canvas unchanged until someone runs kc-journey-progress --draw]
```

### Words FO reads at each lifecycle moment (`wc -w`, origin/main, 2026-11-11)

| Moment | Before | After (recommended) | Under C1 instead |
| --- | --- | --- | --- |
| Startup: `references/sd/workflow.md` | 5939 | 5939 | 5960 (+21: a drafted 48-word sentence replaces the 27-word split-step sentence); needs a budget raise in `lint-skills.py` |
| Startup: journey-map `EXTENSION.md` | 612 | 726 (+50 archive bullet, +9 Needs, +46 backlog bullet, +9 definition) | 726 |
| Backlog seed check, each new task (journey-map workflows) | 0 for a story | 0 when the line is present; 20 words of refusal when it is missing | same |
| Idle look: existing seed-check `next:` line | fires on a missing bound | same words; also fires for a backlog task with no `Story:` line (upper bound 33 relay, 81 qnow at first look) | same |
| Backlog gate on a journey task: Release review bullet, plus the new EXTENSION.md backlog bullet | 420 | 466 (+46) | 487 |
| Ideation gate: design check output | unchanged | 0 when line and fields agree; 9 words plus values when they differ | same |
| After the archive: instructions | 50 (fold bullet) | 100 | 100 |
| After the archive: script output | fold draft diff (not measured); no progress output | + report, at most 9 lines and 160 words | same |
| Idle looks (`pr_watch.py tasks`) | unchanged | unchanged | unchanged |

Reading the raw JSON instead would add 5186 words at each relay archive. This task adds
reading by design, so the learning.md rule is applied as the per-moment count above, not
as a reduction target.

### Limits

- "Every filed task done" can read done while unfiled work remains. Declared status keeps
  the exhaustive meaning where a declaration exists.
- 1 of 40 relay `pr-merge:` refs names the wrong repository (`#842`). The reader cannot
  tell which, so the report prints `<origin repo>#N` and the limit stands.
- A prose step can be skipped. No check catches a missing report, which is the same
  weakness as today's fold step (see D1).
- About 14 s per archive on relay.
- One workflow per read: relay's subspace-v0 and subspace-web tasks are not counted (gap 3
  of journey-map-progress-and-provenance).
- The `Story:` line is checked for presence and form, not truth: a wrong story id passes
  the seed check and is caught only at the Release review. Skipping the seed check
  bypasses it; the idle look still names the task.
- What this takes from journey-map-progress-and-provenance: all of its Gap 1 (the added
  step); nothing else of its scope. Its gap 2
  (declaration at approval) is left to it, with the archived-declarer finding above as new
  input. Its gap 3, the relay backfill, the evidence ladder, ADR references and drawing
  provenance stay there.

### Batch overlap

Read at state commit 045694484 (2026-11-11, after a re-pull), and again at 10149f1c5 for the added step. Files the recommended design changes:
- `kc-journey-map/lib/progress.mjs`, `lib/journey-progress.mjs`, `lib/progress.test.mjs`,
  `lib/schemas.mjs`, `lib/schemas.test.mjs`, `lib/contract-versions.json`,
  `skills/kc-journey-progress/SKILL.md`.
- `kc-dev-flow-2/extensions/journey-map/EXTENSION.md`, `kc-dev-flow-2/scripts/design_surfaces.py`,
  `kc-dev-flow-2/scripts/test_design_surfaces.py`, `kc-dev-flow-2/scripts/test_pr_watch.py`,
  `docs/adr/<number>-a-journey-workflows-new-seed-records-its-story-or-none.md`.
- Budget: still two PRs. The kc-journey-map PR holds the reader. The kc-dev-flow-2 PR
  holds the extension bullets, the seed and design rules, their tests and the ADR file.
- Shared index: the ADR numbers FO reserves (one number for this task).

| Task | Its files or checks (from its task file) | Shared with this design |
| --- | --- | --- |
| release-rollout-reaches-adopters-and-laws-pin (ideation) | release rollout to adopters; mentions workflow.md and `lint-skills.py` as unchanged | no file; this task's stop condition needs the new kc-journey-map and kc-dev-flow-2 to reach relay |
| budget-overrun-holds-and-findings-meet-non-goals (ideation) | `references/sd/workflow.md`, `design_surfaces.py` (seed `Budget:`), `test_design_surfaces.py` | `design_surfaces.py` seed mode and its test file; the second to land rebases; under C1 also workflow.md |
| worker-push-words-match-state-commit (ideation) | `extensions/paseo/EXTENSION.md`, workflow.md Dispatch facts, `lint-skills.py` | none (a different EXTENSION.md); under C1, workflow.md and `WORKFLOW_BUDGET_STEPS` |
| denied-command-denies-only-that-command (ideation) | `extensions/paseo/EXTENSION.md`, Dispatch facts; its overlap note names this task's journey-map EXTENSION.md as "no shared file" | none |
| journey-map-progress-and-provenance (backlog, read only) | `progress.mjs`, `journey-progress.mjs`, the journey-progress schema | same files and schema; this task first, so that one designs on journey-progress 1.1.0 |
| adr-required-statement (validation) | workflow.md, `docs/dev2/README.md`, `lint-skills.py`, `design_surfaces.py`, an FO `Product ruling:` line at backlog, the ADR index | `design_surfaces.py` and another FO backlog alignment line; the ADR numbers; under C1 also workflow.md and the budget |
| dispatch-carries-reserved-adr-number (ideation) | `pr_watch.py` (and its test), learning.md; notes `design_surfaces.py` is imported by dispatch checking | `test_pr_watch.py` (one added case here); the ADR number reservation; rerun its dispatch tests after the `design_surfaces.py` change; the D1 `pr_watch.py` alternative would share `tasks` |
| journey-server-host-pilot (validation) | `render.mjs`, kc-journey-map README, host scripts, `JOURNEY_API` | none; A2 or B2 would share `render.mjs` or `records.mjs` and the host seam |
| merge-guard-stops-unasked-merges (validation) | workflow.md, learning.md, `lint-skills.py`, `docs/adr/` | the ADR numbers |
| ops-inbox-r1-setup-and-isolation (implementation) | kc-ops-inbox's own `contract-versions.json` (cites kc-journey-map's as precedent), `docs/adr/` | the ADR numbers |
| pr-review-lite-value-pilot (implementation) | `kc-journey-map/lib/storymap.test.mjs`, `kc-journey-map/package.json` | no file; both bump the kc-journey-map component in the same Release PR |

Recommended order: this task's kc-journey-map PR before its kc-dev-flow-2 PR, and before
journey-map-progress-and-provenance is designed. adr-required-statement (in validation)
lands before this task's `design_surfaces.py` change, and this one rebases on it;
budget-overrun-holds-and-findings-meet-non-goals goes either way, the second rebasing. The
ADR number comes from FO's reservation at implementation dispatch.

### Decisions for the Captain

D1 and D2 are coupled: a pull request link on the canvas only stays current if the
canvas is redrawn.

**D1: what FO reports after a story's task is archived, and whether the canvas is redrawn.**
- **A1 (recommended).** Report at every archive of a task with a journey release; no
  redraw. Worse: the canvas stays stale until someone runs kc-journey-progress `--draw`.
  The step is prose FO can skip; no check catches a missing report.
- **A2.** A1, plus a redraw at every archive. Worse:
  - It needs a canvas service up and a room name; neither adopter README names one, so a
    new README key is owed.
  - A refused redraw of a hand-edited room prints as success today, so the draw check
    needs a fix.
  - It shares the host seam journey-server-host-pilot is changing.
  - It adds a network write at each archive.
- **A3.** Report only when a story completes. Worse: the two days of silence during a slice
  that the Captain described remain.
- **Alternative trigger home** (applies to A1 or A2): a `next:` line from `pr_watch.py
  tasks` instead of the prose bullet. Worse: it needs a once-per-archived-task marker or it
  repeats at every idle look, and it shares `pr_watch.py` with
  dispatch-carries-reserved-adr-number.

**D2: where progress and story-to-pull-request links live.**
- **B1 (recommended).** Computed from task state at read time; shown in the report and
  the JSON; map file and canvas unchanged. Worse: the canvas does not link a story to its
  pull requests, and a person without the workflow checkout cannot see them.
- **B2.** B1, plus the refs drawn on each story card. Worse: it adds a `ui` surface.
  Choosing it sends this task back through ideation for a `UI proposal:`, an operable
  preview and the design-director review. It needs A2 to stay current.
- **B3.** Written into the map file (a story field listing pull requests) through a
  docs-only map PR. Worse:
  - It is one more PR for the Captain to merge per story.
  - Map and tasks can disagree.
  - Related ruling, not a governing one: ADR 0031 rejected a story field written without
    the Captain accepting an edit and with no consumer; B3 goes through a PR he merges and
    he is its consumer.

**D3: the story declaration step.**
- **C3 (recommended).** Do not take it. Add a count of filed tasks beside the unchanged
  declared status. Worse: two counts exist (filed and declared), and "every filed task
  done" can read done while unfiled work remains. The canvas still shows most stories as
  unverified while the report counts them.
- **C1.** Take it: at each backlog approval into a story, FO sets the story's
  `journey-required-tasks` to all current members, plus a reader rule that a nested,
  newer declaration supersedes an archived one. Worse:
  - It adds a third surface (`references/sd/workflow.md`, +21 words by the drafted
    sentence, a budget raise and `test_sd_dispatch.py` strings) beyond "one PR each".
  - It is forward-only: today's 3 stale relay stories stay unverified until a new task
    joins, and owner-sees-all, whose members are all archived, never recovers.
  - The list FO writes asserts only "approved so far", the same weakness as C3, at more
    cost.
- **C2.** Leave both to journey-map-progress-and-provenance. Worse: the report this task
  adds would read "unverified" for 182 of 184 relay stories and all of qnow, so the
  Captain's question stays unanswered.

Past rulings read: ADR 0031 (related: it rejected an acceptance field written without the
Captain's edit and with no consumer; B3 differs on both); ADR
0056 (directory discovery, producer-first registration, idle-look walk prompt: C3 keeps
its trigger unchanged); `git grep -n '^Override:'` in state finds 5 lines, none in this
area.

## Acceptance criteria

Replay workspace: the pinned clones above, with the state copied under
`<code>/docs/dev2/.spacedock-state`; `<cand>` is the candidate kc-journey-map checkout
with `npm ci` done.

**AC-1** — A declared story's last task completing is reported with its release's remaining stories and its pull requests. Evidence: on the relay replay, run `spacedock status --workflow-dir <relay>/docs/dev2 --set inbox-home status=done pr=pr-merge:999`, then `node <cand>/lib/journey-progress.mjs <relay>/docs/journey/spacedock-review.yaml --workflow-dir <relay>/docs/dev2 --report inbox-home`. It exits 0 and prints `story inbox-home: 1 of 1 filed tasks done; declared: exists`, `pull requests: spacedock-dev/subspace-relay#999`, `release owner-account: 1 of 4 stories have every filed task done; 1 in progress; 2 have no task`, `done: inbox-home (spacedock-dev/subspace-relay#999)` and `in progress: switch-any-account 0/1`. Falsifier: without the `--set`, the same command prints `0 of 1` and `0 of 4`.

**AC-2** — Declared status, release acceptance and the walk prompt are unchanged. Evidence: on the unmodified relay and qnow replays, the `status`, `requiredTasks`, `doneTasks`, `taskIds` of every story and the `status`, `acceptance` of every release from `<cand>` equal kc-journey-map 1.10.0's output field for field (a jq or python diff prints nothing). `release_acceptance.py due` prints the same lines with either `--progress` (continuity-latest is unclaimed, so a status change would add a `next:` line), and kc-dev-flow-2's `test_release_acceptance.py` passes against the candidate checkout. Falsifier: a reader that sets `exists` from member counts changes relay's continuity-latest release (2 stories with only done members) to `pending delivery acceptance`, and the diff names it.

**AC-3** — Filed-task counts match task state. Evidence: on the unmodified relay replay, the `<cand>` JSON `members` gives 11 stories with every member done, 6 in progress and 167 with no task, matching the table in `### Measurements`. agent-reviews-from-link reads `{tasks: 6, done: 5}`. Falsifier: counting only declared members gives 3 for agent-reviews-from-link.

**AC-4** — Pull request refs follow the stated rules. Evidence: `node --test <cand>/lib/progress.test.mjs` includes one case per form (`pr-merge:N`, `N`, `#N`, `owner/repo#N`, a GitHub URL, `local-merge:<sha>`, other, empty) with an ssh and an https `origin`, and one with no `origin`; each asserts the exact `ref`. Falsifier: dropping the URL rule makes the URL case print the raw URL and fail.

**AC-5** — A release task with no story, and a story not on the map, are reported on their own lines. Evidence: on the qnow replay, `--report production-operations` (archived, release r12, no story) exits 0, prints no `story` line, and prints `release tasks with no story: <d> of <n> done`, where n is the count of r12 tasks with an empty `journey-story` and d the count of those done, both from the `spacedock status` listing. A replay task set to a story id absent from the map is counted under `not on the map`. Falsifier: counting release tasks with no story under `not on the map`, or dropping them, changes the line.

**AC-6** — The report stays short. Evidence: on the relay replay, `--report` for a task of second-opinion-later (28 stories) prints at most 9 lines and 160 words (`wc -l -w`); the done and in-progress lists each stop at 5 names with `and <x> more`, and each done story shows at most 3 refs. Falsifier: listing every story or every ref exceeds 160 words.

**AC-7** — FO's step cannot pass silently. Evidence: kc-journey-map 1.10.0 run with `--report inbox-home` exits 2 with its usage line (observed 2026-11-11). `<cand>` with `spacedock` removed from PATH exits 1 and prints exactly one line starting `journey progress not run:`. The candidate EXTENSION.md bullet names both cases. Falsifier: a `<cand>` that prints the report on a failed read with exit 0.

**AC-8** — The schema version moves with the field table. Evidence: `node <cand>/lib/schemas.mjs journey-progress` prints the `members` rows; `contract-versions.json` names `journey-progress` current 1.1.0 with a new hash and keeps 1.0.0. The kc-journey-map schema test exits 0. Falsifier: removing the version entry while keeping the rows makes that test fail.

**AC-9** — The kc-dev-flow-2 steps are as designed, and nothing else in the FO reading changes. Evidence: `git diff origin/main -- kc-dev-flow-2/` touches only `extensions/journey-map/EXTENSION.md`, `scripts/design_surfaces.py`, `scripts/test_design_surfaces.py` and `scripts/test_pr_watch.py`; `wc -w` of EXTENSION.md is 612 before and at most 726 after, and its Joins line says five points; `references/sd/workflow.md` is byte-identical. FO's after-archive step is run by hand on the relay replay of AC-1 by copying the bullet's command verbatim, and it prints AC-1's lines. Falsifier: a candidate that also edits workflow.md fails the diff check.

**AC-10** (stop condition, real use) — On relay, after both releases reach it, the next archive of a task on a declared story has FO's archive message carrying the report lines, or `journey progress not run: <reason>`. Evidence: the archive message quoted with its task slug. Not yet verified: this needs the release and rollout (see release-rollout-reaches-adopters-and-laws-pin); validation may record it as an unverified future check.

**AC-11** — In a workflow listing `journey-map`, the seed check refuses a new seed with no story record and accepts both forms. Evidence: `python3 kc-dev-flow-2/scripts/test_design_surfaces.py` at the candidate includes these cases with a README whose frontmatter lists `journey-map`:
- no `Story:` line under `## FO alignment` → exit 1 with the `needs a 'Story:' line` message;
- `Story: inbox-home (owner-account)` → exit 0;
- `Story: none: workflow maintenance` → exit 0;
- `Story: none` and `Story: none:` → exit 1;
- a `Story:` line only inside a code fence → exit 1.

The same seed without a `Story:` line under a README that does not list `journey-map` exits 0. Falsifier: dropping the README condition makes that last case exit 1, and a check that accepts `Story: none` without a reason passes the case that must fail.

**AC-12** — The replay counts match. Evidence: with the candidate `design_surfaces.py check --seed` run over every task of the relay replay (state 77f5bb4e with relay's README), the qnow replay (state 03838f9 with qnow's README) and this workflow (state 10149f1c5), the number of tasks whose output carries the `Story:` refusal is 135, 163 and 0. Falsifier: a check that applies to every workflow prints 230 for this one.

**AC-13** — The idle look names a backlog task with no story record, and on the replays it names 31 relay and 11 qnow tasks. Evidence: a `test_pr_watch.py` case at the candidate: a workflow listing `journey-map` with one backlog task that needs preparation and has every seed bound but no `Story:` line. `pr_watch.py tasks` prints the existing `next: the seed check fails for these backlog tasks (<slug>)` line. With `Story: none: test` added, it prints no seed line. Falsifier: a seed check that ignores `Story:` leaves the first run silent.

**AC-15** — The line and the counted fields agree before the ideation gate. Evidence: `test_design_surfaces.py` default-mode cases in a journey-map workflow: `Story: inbox-home (owner-account)` with `journey-story: inbox-home` exits 0; with `journey-story` empty, or `switch-any-account`, exits 1 with the `'Story:' names` message; `Story: none: infra` with `journey-story: inbox-home` exits 1; the same files under a README without `journey-map` exit 0. Replay: the default check on relay's two archived tasks that carry `Story:` reports no `Story:` error. Falsifier: a check that compares only presence passes the empty-field case.

**AC-14** — The ADR lands with the rule. Evidence: the kc-dev-flow-2 PR adds `docs/adr/<reserved number>-a-journey-workflows-new-seed-records-its-story-or-none.md` with the Captain's words from this task's ideation resolution and `Protects:` naming `design_surfaces.py`, and the repository's ADR lint exits 0 on it. Falsifier: the rule merged without that file fails the ADR check the PR runs.

## Number guards

ADR: 0076

## Captain amendments

### Amendment 1 — 2026-11-11, host question dialog
Captain: 「更新樣本檔，測試不動（建議）」 (host question dialog, 2026-11-11)
Asked: 「「故事回報進度」的實作要不要多改一個設計沒列的檔案？進度工具的輸出多了欄位後，dev2 切片驗收擴充裡那個「實跑進度工具並和樣本檔逐字比對」的測試會失敗。我建議：同意多改，但改的是那份樣本檔（加入新欄位），測試本身不動、維持逐字比對；不採用工人提議的「把測試改成容許多出來的欄位」。」
Supersedes: none

### Amendment 2 — 2026-11-11, host question dialog
Captain: 「照做，重新驗證（建議）」 (host question dialog, 2026-11-11)
Asked: 「「故事做完回報切片進度」第一次驗證留了一個待裁示的發現（第二半要登記成候選版並重新驗證），要不要照做？我建議照做：把 #839 和疊在它上面的 #843 都登記成候選版，重新派一次獨立驗證，驗證要把 CI 會跑的每個指令都跑過並列出結果，因為第一次驗證漏跑了一組後來失敗 9 項的測試。」
Supersedes: none

## Stage Report: ideation

- DONE: Per the Captain's Result line, compare the choices side by side for him to pick at the gate, each with what gets worse: (a) what FO reports after a story task is archived and whether the canvas is redrawn then; (b) progress and story-to-PR links derived from task state versus written into the map file; (c) taking the story declaration step (a task joins its story's journey-required-tasks when approved into the story) into this task versus leaving it to journey-map-progress-and-provenance. Measure today's declared and undeclared stories on subspace-relay, qnow and this repository read-only, and run the progress reader on at least one real map
  `### Decisions for the Captain` D1 A1–A3, D2 B1–B3, D3 C1–C3, each with what gets worse. `### Measurements`: relay 5 declarations, 2 gap and 182 unverified; qnow 0 declarations, 190 unverified; this repo has no journey task. The reader ran on relay and qnow at the pinned SHAs.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (story-done-reports-release-remaining, release-rollout-reaches-adopters-and-laws-pin, budget-overrun-holds-and-findings-meet-non-goals, worker-push-words-match-state-commit, denied-command-denies-only-that-command) and live task of other sessions (journey-map-progress-and-provenance (backlog, read only), adr-required-statement, dispatch-carries-reserved-adr-number, journey-server-host-pilot, merge-guard-stops-unasked-merges, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions or held; read only)) that changes the same file or check, so FO can order implementation
  The design's 8 files plus 11 task rows, re-read at state 045694484. The only shared files under the recommended choices are with journey-map-progress-and-provenance (`progress.mjs` and the schema). The recommended order is given.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  The `### Words FO reads` table: EXTENSION.md 612→676, after-archive instructions 50→100, report output at most 160 words (against 5186 words of JSON), workflow.md 5939 unchanged; the C1 column is measured from a drafted sentence (+21 words).
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1..AC-10 below, each with a command and a falsifier; D1–D3 each carry a recommendation and its cost.
- DONE: AC-1 report on a declared story's completion: not yet verified (needs `--report`). The underlying count was exercised: in scratch, inbox-home set done moved owner-account from 0 to 1 of 4 stories with inbox-home `exists`.
- DONE: AC-2 declared status, acceptance and walk prompt unchanged: not yet verified. The falsifier's premise was measured: continuity-latest has 2 stories whose members are all done, and no task claims its walk.
- DONE: AC-3 filed-task counts: not yet verified on the candidate. The expected values (11, 6, 167; agent-reviews-from-link 6 and 5) come from the current state listing.
- DONE: AC-4 pull request ref rules: not yet verified. The measured `pr:` shapes on relay are 40 `pr-merge:N`, 1 `owner/repo#N`, 1 URL and 20 empty.
- DONE: AC-5 release-only and incomplete maps: not yet verified. qnow has 77 orphans (57 with no release, 17 with a release and no story, 3 off the map), and production-operations is release r12 with no story.
- DONE: AC-6 report length (at most 9 lines, 160 words): not yet verified (no candidate yet).
- DONE: AC-7 cannot run silently: partly verified. kc-journey-map 1.10.0 with `--report` exits 2 with its usage line (2026-11-11). The candidate's exit 1 is not yet verified.
- DONE: AC-8 schema version moves: not yet verified. journey-progress is at 1.0.0 in `contract-versions.json` at origin/main.
- DONE: AC-9 kc-dev-flow-2 diff limited to the extension: not yet verified. The base counts were measured: EXTENSION.md 612 words, bullet 50.
- DONE: AC-10 real archive on relay: not yet verified. It is a future check after release and rollout.
- DONE: design_surfaces.py check
  `python3 <package>/scripts/design_surfaces.py check <task>` printed "design surfaces presentable" and exit 0. Surfaces stays `none`, because the recommended choices draw nothing new; B2 would add `ui`.

### Summary

The measurements show today's progress count is almost entirely unverified on the real adopters. Relay's declarations went stale because members joined after the declarer was archived, and Spacedock 0.27.2 cannot edit an archived task. The recommended design is: a `--report` text mode plus additive filed-task counts and pull request refs in kc-journey-map (journey-progress 1.1.0), and one after-archive bullet in kc-dev-flow-2's journey-map extension. The canvas and the map file stay unchanged, and the declaration step is left to journey-map-progress-and-provenance. Three decisions (D1 report and redraw, D2 where links live, D3 the declaration step) go to the Captain; D2's B2 would add a `ui` surface and another ideation round.

## Stage Report: ideation (cycle 2)

- DONE: The Captain sent the design back at the ideation gate (read the gate resolution reason in the task file; pull the state checkout first): keep D1 to D3 as designed and add one step, each task at the backlog gate records the story it belongs to, or that it belongs to no story with the reason, and neither is refused; say where it is checked (the seed check in kc-dev-flow-2/scripts/design_surfaces.py, FO's backlog alignment lines, or another place), what it costs each task, and how the report counts tasks that record no story
  `### Added step` covers it. D1–D3 are unchanged. The `Story:` line goes under `## FO alignment`, and the `design_surfaces.py check --seed` rule applies only where `journey-map` is listed; the idle look already runs that check. A design-check rule keeps the line and the counted frontmatter in agreement (AC-15). It costs one line of 2–10 words per task, plus 20 refusal words only when the line is missing. The report gains a "release tasks with no story" line and "complete by filed tasks". An ADR draft extends ADR 0041.
- DONE: Read the backlog task journey-map-progress-and-provenance, its Gap 1 and the relay evidence it holds, say what this step takes from it and what it leaves, and measure on relay, qnow and this workflow how many live and archived tasks would have been refused
  It takes all of Gap 1 and leaves Gap 2, Gap 3, the relay backfill (20/12/2 of 49 tasks) and the evidence ladder. Would have been refused, with no `Story:` line: relay 135 of 137, qnow 163 of 163, this workflow 0 (journey-map not listed; 230 if it were). By substance: relay 35 live and 45 archived, qnow 90 and 58.
- DONE: Update the acceptance criteria, the batch overlap and the words FO reads for the added step, and append a complete new ideation stage report that supersedes the earlier one
  AC-5, AC-9 and AC-13 are updated and AC-11–AC-15 added; the idle look would name relay 31 and qnow 11 existing backlog tasks (measured with `--next --json`), and the rollout step is one pass. The overlap was re-read at 10149f1c5: `design_surfaces.py` is shared with adr-required-statement and budget-overrun, and the ADR numbers with 4 tasks. EXTENSION.md 612→726. There is a seed-check row and an idle-look row. This report supersedes the first.
- DONE: Per the Captain's Result line, compare the choices side by side for him to pick at the gate, each with what gets worse (D1–D3, measured on relay, qnow and this repository, reader run on a real map)
  Unchanged from cycle 1; the Captain kept D1 to D3 as designed.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task and live task of other sessions that changes the same file or check
  The 12 changed files and 11 task rows, with a recommended order: kc-journey-map first, after adr-required-statement for `design_surfaces.py`.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md
  EXTENSION.md 612→726, after-archive 50→100 plus a report of at most 160 words, seed refusal 20 words only on a miss, workflow.md 5939 unchanged.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1–AC-15 below. No new Captain decision: where the step is checked (W1) is recommended inside the design with W2 and W3, as the dispatch asked.
- DONE: AC-1 declared story completion report: not yet verified (needs `--report`). The count it reads was exercised in cycle 1: owner-account went from 0 to 1 of 4.
- DONE: AC-2 status, acceptance and walk prompt unchanged: not yet verified. continuity-latest is all done and unclaimed (measured).
- DONE: AC-3 filed-task counts: not yet verified (expected 11/6/167 from the state listing).
- DONE: AC-4 ref rules: not yet verified (the relay shapes were measured).
- DONE: AC-5 release tasks with no story on their own line: not yet verified (qnow: 17 release-only orphans measured).
- DONE: AC-6 report length: not yet verified.
- DONE: AC-7 cannot run silently: partly verified (1.10.0 `--report` exits 2).
- DONE: AC-8 schema version: not yet verified (1.0.0 today).
- DONE: AC-9 kc-dev-flow-2 diff limits: not yet verified (base 612 words).
- DONE: AC-10 real archive on relay: future check after release and rollout.
- DONE: AC-11 seed check accepts both forms and refuses a missing line: not yet verified (no candidate yet). Relay's 2 existing `Story:` lines match the accepted form.
- DONE: AC-12 replay counts 135/163/0: the expected values were measured on 2026-11-11 by the count above; the candidate run is not yet verified.
- DONE: AC-13 idle look names a backlog task with no story record: not yet verified on the candidate. The `seeds()` path in `pr_watch.py` was read at origin/main; the expected 31/11 come from the replay `--next --json` rows.
- DONE: AC-14 ADR lands: not yet verified (the draft is in `### Added step`; number unreserved).
- DONE: AC-15 line and fields agree at the design check: not yet verified. Relay's 2 existing `Story:` lines agree with their `journey-story` (read 2026-11-11).
- DONE: design_surfaces.py check
  Cycle 2 run printed "story-done-reports-release-remaining.md: design surfaces presentable", exit 0; `spacedock status --read --ac-scan` lists AC-1–AC-15 all `unevidenced=false`.

This report supersedes the first ideation report above. Dispatch: `dispatch/ideation-1-message-1.md`, after the Captain's revise.

### Summary

The design is kept and one step added on the Captain's revise. Every new task in a workflow listing journey-map writes `Story: <story id> (<release id>)` or `Story: none: <reason>` under FO alignment; the existing seed check refuses only a missing line, and the idle look already runs that check. Measured on today's state, the line would be missing on 135 of 137 relay tasks and 163 of 163 qnow tasks; this workflow is unaffected. The rule reaches backlog tasks that still need preparation (31 existing relay and 11 qnow tasks are named on the day it ships, then one rollout pass), a design-check rule keeps the line and the counted fields together, and it takes Gap 1 of journey-map-progress-and-provenance whole, and comes with an ADR draft that extends ADR 0041.

## Stage Report: implementation

- DONE: Two pull requests, as the approved design says: prepare the producer and dev2 changes on their assigned branches, based on freshly fetched origin/main.
  Base e8664a72b0f904e5dda3c391d52ab3abaca876b4; producer spacedock-ensign/story-done-reports-release-remaining at fd1caa475f85483cf5c4031a1e58656ff5d3eaff; dev2 spacedock-ensign/story-done-reports-release-remaining-dev2 at fa485f008562f00ebf91deed19e58ea52bb4b4dc; both clean, exact hashes in implementation-1/evidence/candidates.json.
- DONE: Write one Conventional Commit PR text per branch and report both branches, bases and candidate SHAs.
  /tmp/impl-story-done-reports-release-remaining-pr.md and /tmp/impl-story-done-reports-release-remaining-dev2-pr.md; durable copies producer-pr.md and dev2-pr.md under implementation-1/evidence/.
- SKIPPED: Product branch pushes, Draft PR creation, RoboRev, hosted CI, reviews, ready and merge.
  FO owns publication and local review; no PR opened: no push grant. Delegated checks were not run, not clean; CI cost not measured and CI definitions unchanged.
- DONE: D1 A1, D2 B1, D3 C3 and the added Story step, limited to the design's files plus Captain amendment 1's sample.
  Seven producer files and six dev2/ADR files; workflow.md, test_release_acceptance.py and the consumer contract-versions.json are byte-identical to base. The canvas/map are not written.
- DONE: ADR 0076 records the ruling the design names, quoting the Captain's words from the task file and its gate records.
  docs/adr/0076-a-journey-workflows-new-seed-records-its-story-or-none.md quotes ideation attempts 2/3, names the options/recommendation and protects check_story_record; adr-lint.log exits 0, requiring 0076.
- DONE: AC-1, AC-3, AC-5, AC-6, AC-7 and AC-9: run the report through native pinned replays and its fixture control.
  progress-replay-result.json and AC1-before/after.stdout: inbox-home 0/1→1/1, owner-account 0/4→1/4 with PR #999; all-story counts 11/6/167; agent-reviews 6/5; qnow r12 has 8 release-only tasks; real 28-story report 7 lines/52 words; missing CLI prints one not-run line and exits 1; old CLI exits 2.
- DONE: AC-2: declared status, required/done task fields, task IDs, release acceptance and walk prompts are unchanged.
  replay_progress.py compares both native JSON snapshots to base field for field and both due commands print identical output; turning all-done members into declared exists fails AC2-members-as-declared.log.
- DONE: AC-4 and AC-8: ref rules and the additive journey-progress 1.1.0 contract.
  progress/schema tests cover all eight ref forms with ssh/https/no origin, and retain the v1 wire string and 1.0.0 hash; dropping URL conversion or the version bump fails the recorded mutants; progress-schema.log prints members rows.
- DONE: AC-11, AC-12, AC-13 and AC-15: seed form, workflow scope, idle reach and story/field agreement.
  seed-replay.json: relay 135/137 refused, qnow 163/163, local 0/230; idle names 31/11; both old relay records agree. Missing/fenced/empty/none-without-reason records fail, both forms and unlisted workflows pass; reverse mutations fail the tests and forcing all workflows refuses local 230.
- DONE: AC-14 and every runnable falsifier, with python3 -B and fresh/cleared mutant caches.
  mutations.json (11), remaining-mutations.json (3), AC12-force-all-workflows.json (1), plus the native archive status control; missing ADR exits 1 and the workflow-edit mutation is excluded by the same path/byte check that passes on both candidates.
- SKIPPED: AC-10: the next real relay archive after both releases reach the adopter.
  Explicit future check: release-rollout-reaches-adopters-and-laws-pin and FO's real archive message are still owed; scratch replay is not rollout or delivery acceptance.
- DONE: Captain amendment 1: update only fixtures/journey-progress-v1.json; keep the whole-document assertion and consumer contract registry.
  The design's unchanged-sample claim was wrong: assertEqual(doc, self.document) rejects additive members. The combined exact-byte pair passes all 122 unchanged tests; amendment-1-mutant.log rejects an unrecorded producer field at that same assertion. No consumer registry/test edit was needed.
- DONE: Build replay copies under /tmp from the local relay/qnow clones at the criteria's commits, keeping originals read only after fetch.
  /tmp/opencode-story-done/replays; relay code 0fce82296710d7bf3b89c2871adefd71db2e2957/state 77f5bb4e0e286467ec7078038e8bb9d680baddde; qnow code ebc59cf96fdd5303e0dfccb1559d6048724e33ae/state 03838f912be5a74c972750128955524d03b5a6b6; local state 10149f1c5. README.md in evidence records reproduction and limits.
- DONE: Keep the 30-second reader limit; satisfy repository skill lint, ADR lint, number guards and comment ratio at both candidate heads.
  No limit change: later sequential traces read successfully at base/candidate; earlier timeouts are retained as limits. Repository lint and required ADR lint exit 0; fresh-fetch number guards exit 0 on both heads; comments 0.0%/1.2% below 5%; corresponding logs saved.
- DONE: Run the affected producer, design, watch, dispatch and consumer tests.
  21 producer tests; 222 design tests (4 existing conditional skips); 136 watch tests; 125 dispatch tests (1 conditional skip); 122 integrated consumer tests. Named negative mutations catch the corresponding false behavior, rather than relying on pass counts alone.
- DONE: Record affected-document dispositions and FO reading cost.
  Producer doc_impact: none. ADR 0041 unaffected: its bounds remain and 0076 adds the story rule; ADR 0057 unaffected: amendment comparison is unchanged; ADR 0076 updated. words.json: extension 612→713 (max 726), archive instructions 50→100 plus report, seed instruction 40; workflow remains 5939 words.

### Summary

Implemented the approved Pilot route as two local product commits; FO owns pushing, opening the two Draft PRs (producer first), RoboRev and CI. The only added file outside the original design is the sample Captain amendment 1 authorized; its whole-document assertion stays intact. All current implementation checks pass; AC-10 awaits real release/rollout and the assembled reproduction wrapper is syntax-checked but not run end to end.

## Stage Report: validation

- DONE: Independent verdict on PR #839 head fd1caa47 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  PASSED for the combined exact heads; validation-1/evidence/README.md maps every AC to its half, primary output and independently rerun falsifier; AC-10 remains an explicitly allowed future check.
- DONE: This task delivers two pull requests: the candidate above is the kc-journey-map half (PR #839); the kc-dev-flow-2 half is local commit fa485f008562f00ebf91deed19e58ea52bb4b4dc on branch spacedock-ensign/story-done-reports-release-remaining-dev2 in the worktree /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-story-done-reports-release-remaining-dev2, not yet pushed because its sample test needs the first half on its base. Judge every criterion on the two halves together (export both and overlay, or apply the second commit on the first), say for each criterion which half carries it, and run the release-acceptance suite on the combined tree and on the second half alone to show what hosted CI would do before the first half merges; Captain amendment 1 allows the sample file change; placement: the Captain approved dispatching workers from the First Officer's workspace until the task-workspace sandbox is repaired (host question dialog, 2026-11-11)
  Producer fd1caa475f85483cf5c4031a1e58656ff5d3eaff + dev2 fa485f008562f00ebf91deed19e58ea52bb4b4dc, base e8664a72b0f904e5dda3c391d52ab3abaca876b4; validation-1/evidence/exact-bytes.json binds the exported overlay; consumer-combined.log passes 122 tests while consumer-dev2-alone.log fails one at the unchanged full-document assertion.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  validation-1/evidence/acceptance.sh ran unchanged in fresh Bash, exit 0 (acceptance-final.log); six steps include native archive before/after and required ADR lint; adr-lint.log records python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1/scripts/adr_lint.py docs/adr --since e8664a72b0f904e5dda3c391d52ab3abaca876b4 --require 0076, exit 0.
- DONE: AC-1 / AC-2 — producer report and unchanged declared acceptance; combined consumer.
  validation-1/evidence/AC1-before.stdout and AC1-after.stdout prove the native archive control; scripts/replay_progress.py compares both corpora field-for-field and due outputs; replay-falsifiers.json shows the wrong status mutation changes continuity-latest.
- DONE: AC-3 / AC-4 — producer filed counts and exact refs.
  validation-1/evidence/progress-replay-result.json gives 11/6/167 and agent-reviews 6/5; journey-tests.log covers all ref forms/origins; replay-falsifiers.json gives the wrong count 3 and mutations.json rejects dropped URL conversion.
- DONE: AC-5 / AC-6 — producer release-only/off-map separation and short reports.
  validation-1/evidence/off-map-replay.log separates the native off-map control from r12's 4/8 release-only tasks; AC6-short.stdout is 7 lines/52 words; mutations.json rejects dropped release-only rows and unbounded lists.
- DONE: AC-7 / AC-8 — producer failure signals and additive schema, with dev2's reporting instruction.
  validation-1/evidence/replay-runs.json records old CLI exit 2 and missing CLI exit 1; schema.log prints 1.1.0 with members; mutations.json rejects silent failure and an unchanged version.
- DONE: AC-9 and Captain amendment 1 — dev2 scope, reading cost and unchanged consumer assertion.
  validation-1/evidence/dev2.diff and words.json show only approved files plus the allowed sample/ADR, 612 to 713 extension words, and unchanged workflow/test/consumer registry; remaining-mutations.json rejects workflow drift and an extra producer field.
- SKIPPED: AC-10 — real adopter archive after both releases reach Relay.
  Not yet verified, as the criterion permits; no real archive message or real-use falsifier is claimed. Release, rollout and FO's archive message are still owed.
- DONE: AC-11 / AC-12 / AC-13 / AC-15 — dev2 story forms, workflow scope, idle reminder and field agreement.
  validation-1/evidence/seed-replay.json and seed-replay-restored.log show 135/137, 163/163, 0/230 refusals and 31/11 idle names; mutations.json/AC12-force-all-workflows.json reject each opposite rule; both archived Story records agree.
- DONE: AC-14 — dev2 ADR 0076 carries the ruling and Protects.
  validation-1/evidence/adr-lint.log passes; AC14-missing-adr.log refuses its removal; the Captain's words were compared with the task's ideation records.
- DONE: Stage guards, affected documents, exact bytes and relevant suites.
  validation-1/evidence/guard-results.json, number-guards-fresh.log and exact-bytes.json record the checks; test-results.json points to 21 producer, 222 design, 136 watch and 125 dispatch tests. ADR 0041/0057 unaffected, 0076 updated; producer doc impact empty; added comment is an ADR pointer.
- DONE: Judge implementation limits, sufficiency and minimal necessity.
  validation-1/evidence/README.md retains filed-scope/PR-origin/prose-step/single-workflow/reader-deadline limits, dependency prerequisite and environment reruns; each retained change maps to an AC, falsifier or ADR. CI cost not measured; CI definitions unchanged.
- SKIPPED: Product publication, second-PR hosted CI, RoboRev, merge, release and rollout.
  FO-owned. validation-1/evidence/pr-839.json confirms the first Draft PR head; the second half needs the producer on its base and a fresh-head check. No product push or PR comment was made.

### Summary

PASSED for the combined product behavior at fd1caa475f85483cf5c4031a1e58656ff5d3eaff and fa485f008562f00ebf91deed19e58ea52bb4b4dc; this is not delivery acceptance. The six-step script passed in a fresh shell with the declared preinstalled dependencies; AC-10 stays unverified until release/rollout and a real archive.

- F1 Needs decision: FO owns the missing formal sibling Candidate record. validation-1/evidence/sibling-dispatch-check.json exercises delivery_gate.py's real parser: the newest dispatch recognizes only fd1caa475f85483cf5c4031a1e58656ff5d3eaff, although its checklist authorizes the dev2 head. contract[docs/adr/0036-a-reserved-adr-may-land-on-a-named-sibling-pr-of-the-same-task.md#decision] requires that header line for a sibling to supply ADR 0076; FO must record the sibling and arrange revalidation of any rebased head before the delivery ask. No Material product finding is established by the current accepted checks.

## Stage Report: implementation

- DONE: Merge the pushed first-half branch into the second-half branch with a merge commit, without rebase, history rewrite or manual product-file changes.
  e079d0c555fde855527a82c7a497a4d07e6e4c04 has parents fa485f008562f00ebf91deed19e58ea52bb4b4dc and fd1caa475f85483cf5c4031a1e58656ff5d3eaff; worktree/branch stayed assigned and clean; implementation-1-round4/evidence/merged-head.json and no-manual-change-proof.json bind the bytes.
- DONE: Report the new head and compare its kc-dev-flow-2/docs/adr diff against origin/spacedock-ensign/story-done-reports-release-remaining with the earlier dev2 commit's diff.
  Stacked base fd1caa475f85483cf5c4031a1e58656ff5d3eaff; dev2-original.diff and dev2-stacked.diff are byte-identical six-file patches. The producer subtree also equals #839's head; the merge changes no accepted feature bytes by hand.
- DONE: Run the kc-dev-flow-2 suites the hosted workflow runs on the combined head and report their results.
  All 28 Python command steps ran to completion; hosted-suites.json records direct exits: 27 pass, 1 fails. The 122-test consumer and all three pinned native Spacedock suites pass. Local macOS/Python 3.15 replay only; actual hosted CI not run; runtime.json records CLI 0.27.2 and source pin 4d158a484ec73e184861067f8ed1e20087fdc26a.
- FAILED: A fully green local hosted-workflow command matrix on the combined head.
  test_laws_check.py: 9 of 84 tests fail (1 skip), exit 1. Its sandbox() at line 54 omits workflow_extensions.py while copying design_surfaces.py; the new import raises ModuleNotFoundError. 24-test_laws_check.log and findings.json retain this open Needs decision finding.
- DONE: Reproduce and isolate that failure before proposing any repair.
  laws-baseline-control.json: the same narrow case exits 0 at producer base and 1 at e079d0c555. laws-helper-probe.json: leaving assertions/product bytes unchanged, copying the existing helper only into the temporary fixture makes it pass. This is a new candidate regression, not a baseline-equal failure or sandbox denial.
- SKIPPED: Repair the law-check test fixture or change any assertion/product source by hand.
  Message 4 forbids manual changes and test_laws_check.py is outside the design's file list; FO was asked for scope authorization. proposed-fixture-fix.diff is an unapplied one-line proposal; candidate remains e079d0c555 and clean.
- DONE: Update /tmp/impl-story-done-reports-release-remaining-dev2-pr.md to identify the stack and sibling.
  The Conventional Commit title remains scoped to kc-dev-flow-2; the body names PR #839 as the kc-journey-map sibling and its branch as the PR base, records the merge head and failed workflow, and is copied to implementation-1-round4/evidence/dev2-pr.md.
- DONE: Recheck ADR, reservation, comment and document guards with the stacked PR base.
  ADR lint --since fd1caa475 --require 0076, fresh-fetch number guards --base fd1caa475 and comment ratio exit 0 (1.2%, max 5%); ADR 0041/0057 unaffected and 0076 retained/updated. No new ADR or workflow change; CI cost not measured.
- SKIPPED: Product push, second Draft PR creation, RoboRev, hosted CI, new-head independent validation, release/rollout and AC-10.
  FO owns these steps. No PR opened: no push grant. The local failing matrix must not be promoted to a passing hosted run or delivery acceptance.

### Summary

This supersedes the earlier implementation report for the active stacked candidate and publication preparation: dev2 is now a merge descendant of the pushed producer at e079d0c555fde855527a82c7a497a4d07e6e4c04. Both halves' accepted product bytes are preserved, but the complete local workflow exposes a previously unrun law-check fixture regression; repair scope remains with FO/Captain, and no product push occurred.

## Stage Report: implementation

- DONE: Repair the candidate in kc-dev-flow-2/scripts/design_surfaces.py by loading workflow_extensions only inside the check that uses it.
  Candidate 01d23393ebe5bfd63d8bcafc01859c3b146021d2 on spacedock-ensign/story-done-reports-release-remaining-dev2 has parent e079d0c555fde855527a82c7a497a4d07e6e4c04; implementation-1-round5/evidence/candidate-proof.json and authorized-repair.diff prove the sole change is moving the import into check_story_record.
- DONE: Keep a test that fails if the import moves back to module top; do not change the test or its fixture.
  The unchanged laws copied-script fixture is the regression: laws-before-fix.log exits 1 with ModuleNotFoundError, laws-after-fix.log exits 0 for the same ExitContractTest case; red-green.json binds both heads. Restoring the eager import reproduces the failure before the expected subprocess exit 2.
- DONE: Preserve the Story rule wherever seed and default checks run.
  story-after-fix.log runs both JourneyStoryTests; full design suite passes 222 tests (4 existing conditional skips). Removing the Story check or its workflow scope would fail missing-record/mismatched-field or unlisted-workflow controls.
- DONE: Re-run all 28 hosted workflow commands on the new head and report them.
  hosted-suites.json and numbered logs record all 28 direct exits as 0, including 84 laws tests (1 existing conditional skip), 122 unchanged consumer tests and the three native Spacedock command suites; runtime.json pins CLI 0.27.2 and source 4d158a484ec73e184861067f8ed1e20087fdc26a. This is local macOS/Python 3.15 execution, not hosted CI.
- DONE: Say validation-1 passed the combined tree without this suite failing being reported, and what its record shows about whether that suite was run.
  validation-1-coverage.json: its test-results.json/README list producer, design, watch, dispatch, combined consumer and the fresh-shell script, but retained evidence contains no laws-suite run record. It does not establish that laws ran; the earlier validation report is unchanged and is not a full-matrix pass.
- DONE: Preserve the merge history and compare the stacked dev2/docs/adr diff with the original dev2 patch.
  Stacked base fd1caa475f85483cf5c4031a1e58656ff5d3eaff (#839); merge parents remain fa485f008562f00ebf91deed19e58ea52bb4b4dc and fd1caa475f85483cf5c4031a1e58656ff5d3eaff. dev2-original.diff/dev2-stacked.diff differ only by the authorized import relocation; every other original dev2/ADR file and the producer subtree are byte-identical.
- DONE: Retain the approved two-PR design, additive progress contract, archive report and Story admission behavior within the named files plus Captain amendment 1's sample.
  candidate-proof.json preserves all seven producer files, the other five dev2/ADR files, unchanged consumer assertion/registry, reading file and workflow. The 122-test whole-document consumer suite passes; no map/canvas write or version bump is added.
- DONE: Retain the pinned replay and runnable falsifier evidence for AC-1 through AC-9 and AC-11 through AC-15.
  implementation-1/evidence and validation-1/evidence retain native counts, short-report, ref/contract and mutation controls; candidate-proof.json bounds this repair to import timing, and seed/default plus the full command matrix are rerun here. Prior historical replay/mutation results are not represented as new-head executions.
- DONE: Recheck ADR 0076, reserved numbers, comment ratio and affected documents against the stacked PR base.
  guard-results.json records all exits 0: ADR lint --since fd1caa475 --require 0076; fresh-ref number guards --base fd1caa475; comment ratio 1.2%, max 5%; repository skill lint is matrix step 1. document-verdicts.json retains ADR 0041/0057 unaffected and 0076 correct, quoting the unchanged Captain ruling.
- DONE: Update /tmp/impl-story-done-reports-release-remaining-dev2-pr.md with the new head, stack, sibling and checks.
  dev2-pr.md is the durable copy; the scoped Conventional Commit title is retained and #839's branch is the proposed base. It describes the candidate dependency repair without changing tests or their fixtures.
- DONE: Append a complete superseding implementation stage report and commit/sync the scoped state evidence.
  This report and implementation-1-round5/evidence contain the actual commands, direct exits, byte proofs and remaining limits; state commit is path-scoped and synchronized separately from the unpushed product branch.
- SKIPPED: Repeat the earlier native historical replays and all prior mutations on the new head.
  This narrowly authorized repair rechecks the failing import surface, both Story modes and all 28 workflow commands; earlier scoped evidence remains retained rather than silently promoted to new-head evidence.
- SKIPPED: AC-10: the next real adopter archive after both releases and rollout.
  This remains the explicit future check; a local replay or green test matrix is not that real archive message.
- SKIPPED: Product push, second Draft PR creation, RoboRev, hosted CI, independent new-head validation, review, ready, merge, release and rollout.
  FO owns these actions; no PR opened: no push grant. Local tests of RoboRev wiring do not constitute a RoboRev review. CI cost per PR was not measured; CI definitions are unchanged.

### Summary

This supersedes the earlier implementation reports for the active candidate and publication preparation: 01d23393ebe5bfd63d8bcafc01859c3b146021d2 corrects the candidate's eager dependency on top of the preserved merge, with tests and fixtures unchanged. All 28 local hosted-workflow command steps pass on that exact head; validation-1's retained record does not establish a laws-suite run. The second product branch remains unpushed, and FO-owned publication, independent revalidation and real-use acceptance remain open.

## Stage Report: validation

- DONE: Independent verdict on PR #839 head fd1caa47 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  PASSED at #839 fd1caa475f85483cf5c4031a1e58656ff5d3eaff plus stacked #843 01d23393ebe5bfd63d8bcafc01859c3b146021d2; validation-2/evidence/criteria.json maps every criterion and independently rerun falsifier; AC-10 remains the permitted future check.
- DONE: Second validation, on Captain amendment 2: two pushed candidates, PR #839 (kc-journey-map half, head unchanged since validation-1) and its stacked sibling PR #843 (kc-dev-flow-2 half, head 01d23393ebe5bfd63d8bcafc01859c3b146021d2, a merge of the first half plus one repair commit that defers an import in kc-dev-flow-2/scripts/design_surfaces.py). Validation-1 passed the combined tree but its retained record shows no run of the laws suite, and that suite then failed 9 tests on the merged head before the repair. Run every command the hosted workflows for kc-dev-flow-2 and kc-journey-map run, on #843's head, list each with its exit code, and say which of them validation-1 did not run; judge the repair and Captain amendment 1 (the sample file); export the #843 head for all checks; placement: the Captain approved dispatching workers from the First Officer's workspace until the task-workspace sandbox is repaired (host question dialog, 2026-11-11)
  validation-2/evidence/workflow-results.md lists all commands/exits and prior coverage: 28 dev2 commands plus five journey commands on each required Node version all exit 0; runtime/setup substitutions are explicit. The full laws suite is 84 tests, one existing skip; repair-red-green.json rejects the unchanged pre-repair import surface. Both amendments and formal sibling identity pass.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  validation-2/evidence/acceptance.sh ran unchanged in fresh Bash, exit 0 in acceptance-final.log/final-native-results.json; six steps finish within five minutes. adr-lint.log records python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1/scripts/adr_lint.py docs/adr --since fd1caa475f85483cf5c4031a1e58656ff5d3eaff --require 0076, exit 0. No new classified finding; earlier F1 is closed by sibling-dispatch-check.json.
- DONE: AC-1 / AC-2 / AC-3: native archive, preserved acceptance and filed counts.
  validation-2/evidence/AC1-before.stdout and AC1-after.stdout show 0/1 to 1/1 and 0/4 to 1/4 with the completed PR; both old-field projections and due outputs match. progress-replay-result.json gives 11/6/167 and 6/5; replay-falsifiers.json detects changed acceptance and the wrong count of 3.
- DONE: AC-4 / AC-5 / AC-6 / AC-7 / AC-8: refs, separate rows, short report, failures and schema.
  validation-2/evidence/workflow-tests.json records 276 model tests per Node; off-map-replay.log keeps r12 4/8 separate, AC6-short.stdout is 7 lines/52 words, failure-signals.json records exits 2/1, and schema.log prints 1.1.0. mutations.json rejects dropped URL/no-story rules, unbounded lists, silent read failure and a missing version bump.
- DONE: AC-9 and Captain amendment 1: bounded scope, reading and the unchanged consumer assertion.
  validation-2/evidence/exact-bytes.json and history-preservation.json preserve all approved bytes and 612-to-713 extension words; workflow/consumer tests/registry remain unchanged. The 122-test consumer passes; remaining-mutations.json rejects a workflow edit and an unrecorded producer field.
- DONE: AC-11 / AC-12 / AC-13 / AC-15: Story admission, historical scope, idle reminder and field agreement.
  validation-2/evidence/seed-replay.json/log records 135/137, 163/163, 0/230 refusals and 31/11 idle names, with both archived Story records agreeing. mutations.json and AC12-force-all-workflows.json reject missing scope, reason, rule and field comparison; the latter wrongly refuses all 230 local tasks.
- DONE: AC-14, reserved numbers, affected documents, added comments and dispatch guards.
  validation-2/evidence/guard-results.json passes; AC14-missing-adr.log rejects removal of required 0076. document-verdicts.json judges all three listed ADRs; comment ratios 0.0%/1.2% meet 5%, with only the required ADR pointer added.
- DONE: Judge the import repair, complete command coverage, both Captain amendments and prior validation limits.
  validation-2/evidence/repair-red-green.json shows the same 13 unchanged cases fail before and pass after; the full repaired laws suite passes. validation-1-coverage.json identifies 23 dev2 commands with no prior run record and the missing full journey command coverage. The sample changes only by additive fields; the full-document assertion still catches drift.
- DONE: Exact artifact identity, goal sufficiency, minimal necessity and retained runtime failures.
  validation-2/evidence/candidate-all-tracked-bytes.log confirms all exported tracked bytes unchanged; README.md maps retained changes to criteria and reverse controls. Earlier base/candidate timeouts and the first failed acceptance are preserved; final-native-results.json records successful final sequential replays and acceptance with the same data, expectations and 30-second reader deadline.
- SKIPPED: AC-10: real adopter archive after release and rollout.
  Explicitly permitted future check; validation-2/evidence/limit-judgments.json records it. Scratch native replay does not establish the real FO archive message or adoption.
- SKIPPED: Literal Linux setup shell blocks and hosted-run execution by this worker.
  validation-2/evidence/workflow-setup.json records native macOS Spacedock 0.27.2 and pinned source substitutions; actual hosted green results were read in hosted-dev2.json/hosted-journey.json. Local checks do not claim Ubuntu execution; CI cost per PR is unmeasured and definitions are unchanged.
- SKIPPED: Product push, PR comments, reviews, merge, release and rollout.
  FO-owned; only this task entity and validation-2 evidence are written and synced. Both PRs remain open at the exact dispatched heads.

### Summary

PASSED for the current bounded outcome at fd1caa475f85483cf5c4031a1e58656ff5d3eaff and 01d23393ebe5bfd63d8bcafc01859c3b146021d2; this complete second validation report supersedes validation-1 for candidate identity and command coverage. All 38 local check invocations and the fresh six-step acceptance pass, with setup substitutions and earlier timeout failures preserved; AC-10, delivery approval, release and rollout remain open.
