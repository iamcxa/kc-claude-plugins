---
title: A goal change marks a release changed, any shared non-production database freezes its migrations, and five workflow gaps close
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: done
gates:
    version: 1
    records:
        - id: gate:patch-0102:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:patch-0102-backlog-1
              briefing:
                id: briefing:patch-0102:backlog:attempt-1:revision-1
                digest: sha256:4d758e558ed98c10fb64213b9f75657770cd87cd85b4ae91fd03ceabaa4c283a
                room-ref: ./patch-0102/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:patch-0102:backlog:1
                briefing: briefing:patch-0102:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-30T17:15:34.507831Z"
                decision: approve
                reason: 'Captain 2026-10-01: 「准」 — fix the five package findings as 0.10.2 with the collision rule: applied task keeps its number, the unapplied one renumbers; recreate only when both are applied to a non-resettable database'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:patch-0102:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:patch-0102-ideation-1
              briefing:
                id: briefing:patch-0102:ideation:attempt-1:revision-1
                digest: sha256:5b6840a0dd6beb4dbaa316a30165c2d9b2fce2e5183878d8523f17f21ba805a4
                room-ref: ./patch-0102/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:patch-0102:ideation:1
                briefing: briefing:patch-0102:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-01T00:59:28.494893Z"
                decision: approve
                reason: 'Captain 2026-10-01: 「可以」 — design approved with the coupled rule: a migration on the base branch counts as applied; of two applied unmerged tasks the first to merge keeps its number'
              application:
                target-stage: implementation
                state: consumed
        - id: gate:patch-0102:validation
          stage: validation
          attempts:
            - id: gate-attempt:patch-0102-validation-1
              briefing:
                id: briefing:patch-0102:validation:attempt-1:revision-1
                digest: sha256:6a1ab7dc81fbc126e7bf70aaaf2d1f713cbbb12314b49e34742067cda907d806
                room-ref: ./patch-0102/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:patch-0102:validation:1
                briefing: briefing:patch-0102:validation:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-10-01T01:14:30.314549Z"
                decision: approve
                reason: Validation PASSED on 581991fa plus the FO-authorized one-line ADR fix b88732c2 (diff read by the FO); two Polish declined; opening a Draft PR only; merge stays with the Captain
                conn:
                    quote: 'No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar'
                    source: ~/.claude/CLAUDE.md, Autonomous action boundaries
              application:
                target-stage: done
                state: consumed
started: 2026-09-30T17:15:41Z
worktree: .worktrees/spacedock-ensign-patch-0102
pr: pr-merge:549
verdict: PASSED
completed: 2026-10-01T02:10:03Z
archived: 2026-10-01T02:10:03Z
---

Five gaps in kc-dev-flow-2 0.10.1 `references/sd/workflow.md`, found by an external review of an adopter's workflow sync (qnow PR #1248, round 2, 2026-10-01); patch release 0.10.2.

## Scope

Captain 2026-10-01: 「准」 to the FO's proposal: fix the five package findings in one patch release, fill the adopter's secret-wrapper value in qnow #1248 separately, then re-sync #1248; and the collision rule below.
Findings (text at kc-dev-flow-2-v0.10.1):
- P1, release review skip check: a Captain ruling that changes a release's goal (or a task's or story's goal) without changing the release's story ids is seen as "unchanged" by the skip shortcut, which defeats signal 2 ("changes its goal"). The freshness check must include a goal or scope revision, not only membership.
- P1, Number guards Applied bullet: freezing is limited to "a non-production database branch", but an adopter's staging can be a separate hosting project whose database is that project's production database; it is then never frozen, and the renumber recovery (reset a non-production branch) cannot apply to it. Captain's ruling on the design: every shared non-production environment freezes its migrations, whether a database branch or a separate project; on a number collision the task whose migration is already applied keeps its number and the other, unapplied task renumbers, so no reset is needed; only when both are applied to a database that cannot be reset does the Captain delete and recreate that database.
- P2, release fields: when signal 2 moves a task out of a release, no step clears `journey`, `journey-release` and `journey-story` or repairs an affected story's `journey-required-tasks` declaration.
- P2, backlog gate revise: a revise at the backlog gate is routed to "that stage's worker", but backlog dispatches no worker; route it to FO or the proposal's author.
- P2, number guards fetch: bare `git fetch` before `reserve` and before the pre-merge `check` updates the current directory's repository, not the `--repo` the script inspects; use `git -C <repo> fetch`.
Non-goals: the adopter secret-wrapper value (adopter-owned, fixed in #1248); any Spacedock change; `number_guards.py` logic changes beyond what the wording requires.

## Acceptance criteria

**AC-1**: A task already on the map passes the release-review skip check only while the journey file holds the same story ids and the same release and story goal text and no Captain ruling has changed the goal of the release, a story or a task; a goal ruling with unchanged story ids is signal 2 and marks the release changed.
Verified by: `FIXES["goal-change"]` in `scripts/test_sd_dispatch.py` holds two phrases of the 0.10.2 text and reports both missing, plus the 0.10.1 phrase present, when the passage is put back at its 0.10.1 wording. Limit: the skip check is prose FO applies and no script detects a goal ruling, as for the `Release review:` line itself.

**AC-2**: The Applied bullet freezes migrations applied to every persistent shared non-production environment, a database branch or a separate hosting project such as a staging project whose database is that project's own production database.
Verified by: `FIXES["shared-environment"]` (same falsifier form). Limit: which deploys FO records as `Applied at:` is unchanged; an unrecorded deploy is still not detected.

**AC-3**: On a migration number collision the applied task keeps its number and the unapplied task renumbers without a reset; a renumbering task that is itself applied holds for the Captain, who resets a database branch or deletes and recreates a shared non-production database that cannot be reset, and FO then records `Not applied: <environment> <sha> - database reset` so `check` accepts the renumber.
Verified by: `FIXES["collision"]`; `test_a_task_that_loses_a_collision_reserves_again_above_the_one_that_keeps_its_number` and `test_an_applied_task_whose_number_the_base_took_renumbers_once_its_line_is_replaced` in `scripts/test_number_guards.py`; mutation: replacing `taken |= task_facts(sibling)[args.kind]` in `reserve` with `pass` fails both ReserveTests, and ignoring `Applied at:` lines in `check` fails five AppliedFreezeTests. Limit: nothing compares task files, so two in-flight tasks holding one number surface only as R3 or R5 on the later candidate.

**AC-4**: When signal 2 moves a task out of a release, the workflow gives FO the command that clears the five release fields and the repair of the story's `journey-required-tasks` declaration, and kc-journey-progress reports the story unverified until the declaration matches its members.
Verified by: `FIXES["clear-release-fields"]`; `spacedock status --set <task> journey= journey-release= journey-story= journey-required-tasks= journey-mapping-complete=` run in a disposable workflow leaves the keys empty and a listing omits them (run 2026-10-01, spacedock 0.27.2); the four-case script in the Design section, run against `kc-journey-map/lib/progress.mjs` at origin/main, prints `unverified` for a stale declaration and for a removed declaring task, and `exists` once the declaration is repaired.

**AC-5**: A `revise` at the backlog gate is routed to FO or the proposal's author, and a stage that dispatches a worker still routes it to that worker.
Verified by: `FIXES["backlog-revise"]`; `python3 -m unittest test_poc_readme` passes, because the POC derivation refuses a line that names `ideation` outside the ideation stage definition (the first draft of this wording failed it).

**AC-6**: FO fetches with `git -C <repo> fetch` before `reserve` and before the pre-merge `check`, and the `number_guards.py` usage text says the same.
Verified by: `FIXES["fetch-the-inspected-repo"]`; `python3 scripts/number_guards.py --help` prints `git -C <repo> fetch`.

**AC-7**: The patch is the one the Design lists and breaks no existing check: all package tests pass, added comments stay at or under the 5 percent default, ADR 0002 carries one amendment line and passes `adr_lint.py`, and `docs/dev2/README.md` is unchanged.
Verified by: on the spike of this design, `test_sd_dispatch.py` six PASS lines, `test_number_guards` 20 tests OK, `test_poc_readme`, `test_adr_doc_checks`, `test_design_surfaces` and `lint-skills.py` pass; `comment_ratio.py` reported 2 comment lines of 90 code lines (2.2 percent); `adr_lint.py docs/adr --require 2` exit 0 (all 2026-10-01). Implementation re-runs them on its candidate; `git diff --stat origin/main` names the six files below and nothing else.

## FO alignment

Needed at ideation: replacement wording for each of the five passages; which asserted phrases in `test_sd_dispatch.py` change and a falsifier holding the 0.10.1 text for each; whether `number_guards.py` or `journey-progress` needs any change for the collision rule and the field clearing; whether ADR 0002, ADR 0004 or the #520 ADR (0006) needs an amendment line.
Result: the FO delegates these questions to ideation, which decides each with its source and returns any ruling that needs the Captain.
Surfaces: none
Visible change: none


## Design

### PRFAQ

**Headline.** A goal change marks a release changed, every shared non-production database freezes its migrations, and a number collision costs the unapplied task a renumber instead of a database reset.

**Who and why.** FO and the Captain, when an adopter's flow hits one of five gaps an external reviewer found in qnow PR #1248 (round 2, Codex comments on commit `2155bed`, read 2026-10-01 with `gh api repos/iamcxa/qnow/pulls/1248/comments`). The same review's two comments on commit `488ac87` were fixed in 0.10.1.

**FAQ.**
- Does any script change? `number_guards.py` gets one docstring line; no rule, parser or exit code changes. `reserve` already skips every number a sibling task file holds, so a task that deletes its `Migration:` line and reserves again lands above the keeper (mutation-proved, AC-3). `check` already accepts a renumber once `Not applied:` replaces the `Applied at:` line (new test, AC-3). `--set field=` already clears a field, and the progress reader already reports a mismatched declaration as unverified (AC-4). kc-journey-progress needs no change.
- Existing-code check (`implementation/principles.md` existing-code capability check): each fix reuses a mechanism that is already shipped; nothing new is built.
- Which ADRs change? Only ADR 0002, by one amendment line (below). ADR 0004 records review rounds and the repair lane, which these five passages do not touch. ADR 0006 records the slice-size advisory; no ADR records the release-review signals, so nothing there to amend. ADR 0005 states the amendment record, not the `revise` routing.
- Out of scope: the adopter's secret-wrapper value (fixed in #1248), any Spacedock change, and syncing `docs/dev2/README.md` (an identical copy of `workflow.md`, checked with `diff` against origin/main 2026-10-01), which follows the release as its own chore PR the way #542 followed 0.10.1.

### Collision decision

```mermaid
flowchart TD
    A["Two tasks hold migration number N (check R3 or R5 on the later candidate)"] --> BIs either applied?<br/>Applied at line, or on the base branch
    B -- neither --> C["The candidate check flagged renumbers"]
    B -- one --> D["The applied task keeps N;<br/>the unapplied task renumbers, no reset"]
    B -- both --> E["The one that merges first keeps N;<br/>the other renumbers"]
    C --> F["Renumbering task deletes its Migration line;<br/>FO runs reserve again"]
    D --> F
    E --> F
    F --> GDoes the renumbering task<br/>have an Applied at line?
    G -- no --> H["Return to implementation<br/>with the new number in scope notes"]
    G -- yes --> I["FO holds for the Captain"]
    I --> JCan the database be reset?
    J -- "yes, a database branch" --> K["Captain resets the branch"]
    J -- "no, a separate project's own database" --> L["Captain deletes and recreates it"]
    K --> M["FO replaces the line with<br/>Not applied: env sha - database reset"]
    L --> M
    M --> H
```

### Replacement wording

Files: `kc-dev-flow-2/references/sd/workflow.md` (five passages), `scripts/number_guards.py` (docstring), `scripts/test_sd_dispatch.py`, `scripts/test_number_guards.py`, `docs/adr/0002-...` (one line). The 0.10.1 text is at tag `kc-dev-flow-2-v0.10.1`; each block below replaces the passage that begins at its first words. Whole-passage text as it stands after the change, line breaks as in the file:

1. Release review, backlog (the signal 2 clause and the skip check):

```
  or out of a release or changes the goal of the release, a story or a task; (3) a UAT
  failure that crosses two or more tasks; ...
  reason. A task whose `journey-story` is already on the map in that release passes with
  that one check and marks nothing when, since its latest `Release review:` line, the
  journey file still holds the same story ids and the same release and story `goal`
  text and no Captain ruling has changed the goal of the release, a story or a task.
  A changed goal is signal 2 although no story id moved; FO marks the release
  changed in that task's `## FO alignment` reason. Signal 4 is the single checkpoint: ...
```

2. Number guards, Applied bullet (with the Reserve bullet's `git -C <repo> fetch`, the fifth finding):

```
- **Reserve.** Before an implementation dispatch, FO runs `git -C <repo> fetch`, then
...
- **Applied.** Before any push of a candidate to a persistent shared non-production
  environment (a database branch, or a separate hosting project such as a staging
  project whose database is that project's own production database), FO records `Applied at: <environment> <sha>`
  for the commit being pushed. A migration in that commit is then frozen for the
  task: edit, delete and renumber fail `check`. When the push is rejected or the
  deploy is confirmed not to have run for that commit (the push's non-zero output,
  or the environment's own deploy record showing no deploy of it), FO replaces that
  one line with `Not applied: <environment> <sha> - <evidence>` and the migration is
  no longer frozen. Without that confirmation the line stays and the migration counts
  as applied. Git cannot see what a database applied, so an unrecorded deploy is
  not detected.
```

3. Number guards, Collision bullet (replaces the Renumber bullet; `check` bullet carries the other fetch change):

```
- **Collision.** When two tasks hold one migration number (`check` reports R3 or R5 on
  the later candidate; nothing compares task files), the task whose migration is applied
  keeps it and the other, unapplied task renumbers, so no reset is needed. A migration
  counts as applied when its task has an `Applied at:` line or it is on the base branch;
  when both tasks are applied and neither is on the base branch, the one that merges
  first keeps the number. The renumbering task deletes its `Migration:` line, FO runs
  `reserve` again, and the task returns to implementation with the new number in its
  scope notes. When the renumbering task has an `Applied at:` line, its environment's
  database holds a migration no branch will carry, and FO holds for the Captain: a
  database branch is reset, and a shared non-production database that cannot be reset
  (a separate project's own database) is deleted and recreated by the Captain. FO then
  replaces the line with `Not applied: <environment> <sha> - database reset` so that
  `check` accepts the renumber. A branch reset is one Netlify Open API call,
  `netlify api resetSiteDatabaseBranch --data '{"site_id":"<site>","branch_id":"<branch>"}' > /dev/null`
  (`netlify api --list` shows the method). The response carries connection
  strings, so redirect it to `/dev/null` and read the result from the next
  deploy. This step is documented, not wrapped in a tool.
```

The Check bullet's clause becomes `at validation and, after \`git -C <repo> fetch\`, on the PR head before FO asks for merge.`

4. Release review, field clearing (appended to the same bullet after the `journey-required-tasks` sentence):

```
  When signal 2 moves a task out of a release, FO clears its release fields with
  `spacedock status --workflow-dir <dir> --set <task> journey= journey-release= journey-story= journey-required-tasks= journey-mapping-complete=`
  (a field set to nothing is cleared) and, where kc-journey-progress is tracking,
  removes the task's full id from `journey-required-tasks` on the declaring task of
  its old story; when the cleared task was the declaring one, FO moves that list and
  `journey-mapping-complete: true` to another member of the story. A task moved to
  another story gets the new values from the set command above and its id is added to
  that story's list. kc-journey-progress reports a story unverified until its
  declaration matches its members.
```

5. Captain amendments, first paragraph's last clause:

```
while the gate that would accept it is still open is not one: he calls `revise`; at a stage
that dispatches a worker, that stage's worker reworks it, and at `backlog`, which
dispatches no worker, FO revises the recorded outcome, scope or budget, or asks the
proposal's author to.
```

The wording avoids the literal `ideation` on that line because `test_poc_readme` derives the POC route by refusing it.

ADR 0002, appended after its Consequences paragraph:

```
Amended 2026-10-01 (Captain: 「准」): a shared non-production environment is a database branch or a separate hosting project whose database is that project's own production database, and its applied migrations freeze; on a number collision the task whose migration is applied (an `Applied at:` line, or on the base branch) keeps its number and the other renumbers without a reset, and only a renumbering task that is itself applied needs the Captain to reset the branch or to delete and recreate a shared non-production database that cannot be reset (`workflow.md` Number guards).
```

`number_guards.py` docstring: `run 'git fetch' first` becomes `run 'git -C <repo> fetch' first`.

Write the netlify reset sentence into `workflow.md` with the Edit tool and keep it byte-for-byte (the Bash guard refuses a heredoc that names that API; ideation hit this). No other file names `Renumber`: `git grep` of origin/main finds it only in `workflow.md` and the identical `docs/dev2/README.md`.

### Test changes

`scripts/test_sd_dispatch.py` (spike: +64 lines, 2 comment lines):
- Add the `FIXES` table below, `fix_gaps(text)` (for each fix, the missing 0.10.2 phrases and the 0.10.1 phrases still present) and `at_0_10_1(text, name)` (put one fix's 0.10.1 passage back by regex swap, asserting each swap matched once).
- In the lane block: the regex that builds the 0.10.0 fixture ends at `the migration counts as applied\. ` instead of `Renumber holds for the Captain\. `; `LANE_RULE`'s two Applied phrases (`replaces that one line with ...`, `Without that confirmation the line stays`) are unchanged.
- After it: assert no fix reports a gap on the current text, and for every fix that the text with only that fix reverted reports exactly that fix's phrases missing and its 0.10.1 phrases present, and no other fix's.
- Extend the `PASS:` line for the lane to name the six fixes.
- The `collision` swap puts back the 0.10.1 Renumber sentences that changed; the reset-call sentence is carried over unchanged into the new bullet, so the falsifier omits it (and the implementation writes that sentence with Edit, not a heredoc).

```python
FIXES = {
    "goal-change": dict(
        need=("the same story ids and the same release and story `goal` text",
              "changes the goal of the release, a story or a task"),
        old=("with the release's story set unchanged since its latest `Release review:` line",),
        swaps=((r"A task whose `journey-story` is already on the map in that release passes with that one check.*?"
                r"in that task's `## FO alignment` reason\.",
                "A task whose `journey-story` is already on the map in that release, with the release's story set "
                "unchanged since its latest `Release review:` line, passes with that one check and marks nothing."),
               (r"changes the goal of the release, a story or a task", "changes its goal"))),
    "shared-environment": dict(
        need=("persistent shared non-production environment",
              "a separate hosting project such as a staging project"),
        old=("persistent shared environment (a non-production database branch)",),
        swaps=((r"persistent shared non-production environment \(a database branch, or a separate hosting project.*?"
                r"own production database\)",
                "persistent shared environment (a non-production database branch)"),)),
    "collision": dict(
        need=("the task whose migration is applied keeps it and the other, unapplied task renumbers",
              "deletes its `Migration:` line", "a shared non-production database that cannot be reset", "is deleted and recreated by the Captain",
              "the one that merges first keeps the number",
              "`Not applied: <environment> <sha> - database reset`",
              "the line stays and the migration counts as applied"),
        old=("Renumber holds for the Captain", "- **Renumber.**"),
        swaps=((r"- \*\*Collision\.\*\*.*?(?= ## Delivery authority)",
                "- **Renumber.** A candidate whose number was taken (R3, R5) renumbers and returns to implementation. "
                "When an `Applied at:` commit holds the migration, FO holds for the Captain: reset that non-production "
                "database branch, then renumber. It applies to non-production branches only; the production branch "
                "cannot be reset."),
               (r"the line stays and the migration counts as applied", "the line stays and Renumber holds for the Captain"))),
    "clear-release-fields": dict(
        need=("journey= journey-release= journey-story= journey-required-tasks= journey-mapping-complete=",
              "moves that list and `journey-mapping-complete: true` to another member of the story"),
        old=(),
        swaps=((r"When signal 2 moves a task out of a release, FO clears.*?declaration matches its members\.", ""),)),
    "backlog-revise": dict(
        need=("at `backlog`, which dispatches no worker, FO revises",),
        old=("he calls `revise` and that stage's worker reworks it",),
        swaps=((r"he calls `revise`; at a stage that dispatches a worker.*?asks the proposal's author to\.",
                "he calls `revise` and that stage's worker reworks it."),)),
    "fetch-the-inspected-repo": dict(
        need=("FO runs `git -C <repo> fetch`, then", "after `git -C <repo> fetch`, on the PR head"),
        old=("FO runs `git fetch`, then", "after `git fetch`, on the PR head"),
        swaps=((r"FO runs `git -C <repo> fetch`, then", "FO runs `git fetch`, then"),
               (r"after `git -C <repo> fetch`, on the PR head", "after `git fetch`, on the PR head"))),
}
```

Falsifier evidence (2026-10-01, spike): on the 0.10.1 `workflow.md` every fix reports all its phrases missing (2, 2, 7, 2, 1, 2) and its old phrases present; on the spike text each single-fix regression reports only that fix.

`scripts/test_number_guards.py` (spike: +2 tests, in `AppliedFreezeTests` and `ReserveTests`):

```python
    def test_an_applied_task_whose_number_the_base_took_renumbers_once_its_line_is_replaced(self):
        self.fx.git("checkout", "-q", "main")
        self.fx.commit("other landed", **{mig(6, "other"): "SELECT 2;\n"})
        self.fx.git("checkout", "-q", "feature")
        code, out = self.fx.check(task=task_file(self.task_dir.name, "Migration: 0006", self.line))
        self.assertEqual((code, "FAIL R3" in out), (1, True), out)
        self.fx.commit("renumber", **{mig(6, "op"): None, mig(7, "op"): "SELECT 6;\n"})
        code, out = self.fx.check(task=task_file(self.task_dir.name, "Migration: 0007", self.line))
        self.assertEqual((code, "FAIL R2" in out), (1, True), out)
        reset = f"Not applied: uat {self.applied} - database reset"
        self.assertEqual(self.fx.check(task=task_file(self.task_dir.name, "Migration: 0007", reset))[0], 0)

    def test_a_task_that_loses_a_collision_reserves_again_above_the_one_that_keeps_its_number(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as state:
            fx = base_repo(tmp, top=12)
            fx.git("checkout", "-q", "main")
            keeps, loses = Path(state, "keeps.md"), Path(state, "loses.md")
            keeps.write_text("## Number guards\nMigration: 0013\nApplied at: uat " + "a" * 40 + "\n")
            loses.write_text("## Number guards\nMigration: 0013\n")

            def reserve(task):
                return fx.run("reserve", "--kind", "migration", "--repo", tmp, "--migrations-path", MIGRATIONS,
                              "--base", "main", "--state-dir", state, "--task", str(task))

            self.assertEqual(reserve(loses), (0, "Migration: 0013\n"))
            loses.write_text("## Number guards\n")
            self.assertEqual(reserve(loses), (0, "Migration: 0014\n"))
            self.assertEqual(reserve(keeps), (0, "Migration: 0013\n"))
```

The first test's middle step is the one that matters: with the `Applied at:` line kept, the renumber is refused (R2), so the collision text must tell FO to replace the line, which it does.

### Progress-reader check (AC-4)

Run from any directory with `progress.mjs` copied from `origin/main:kc-journey-map/lib/progress.mjs` (no dependencies; Node 22):

```js
import { calculateProgress } from './progress.mjs'
const model={journey:'j',releases:[{id:'r1'}],steps:[{stories:[{id:'s1',release:'r1'}]}]}
const t=(id,extra={})=>({id,status:'done',journey:'j','journey-release':'r1','journey-story':'s1',...extra})
const decl={'journey-required-tasks':JSON.stringify(['A','B']),'journey-mapping-complete':'true'}
const cleared={id:'B',status:'ideation',journey:'','journey-release':'','journey-story':''}
const show=(n,tasks)=>{const r=calculateProgress(model,tasks)[0];console.log(n,r.status,r.diagnostic??'')}
show('removed B, declaration stale',[t('A',decl),cleared])
show('removed B, declaration repaired',[t('A',{...decl,'journey-required-tasks':'["A"]'}),cleared])
show('removed declaring A, list not moved',[{...cleared,id:'A','journey-required-tasks':decl['journey-required-tasks'],'journey-mapping-complete':'true'},t('B')])
show('removed declaring A, list moved to B',[{...cleared,id:'A'},t('B',{'journey-required-tasks':'["B"]','journey-mapping-complete':'true'})])
```

Observed 2026-10-01: `unverified` (Required mapping differs from readable task membership), `exists`, `unverified` (One confirmed complete mapping is required), `exists`.

### Decisions

Needs the Captain beyond 「准」: one, and it is coupled. His rule says the applied task keeps its number; it does not say what counts as applied or who wins when both are. This design reads a migration already on the base branch as applied (a merged task cannot renumber) and lets the first of two applied, unmerged tasks to merge keep the number. A reset or recreation still holds for him, as ADR 0002 gave it. The design follows his rule otherwise. Release, merge and any Release PR stay his; the adopter pins a published tag only after release-please cuts it, never the predicted 0.10.2.

Stated limit: a renumbering task that is already applied still costs a reset or recreation, so "no reset is needed" holds only for the unapplied side.

### Captain acceptance script

Run from a checkout of the candidate, in `kc-dev-flow-2/`:

1. `python3 scripts/test_sd_dispatch.py --sd-plugin-root <activated Spacedock plugin root>` prints six `PASS` lines then `Not run:` and exits 0; the lane line names the six fixes.
2. `python3 -m unittest test_number_guards` (from `scripts/`) ends `Ran 20 tests` and `OK`.
3. `python3 scripts/adr_lint.py ../docs/adr --require 2` prints `7 ADR file(s) checked, 0 legacy` and exits 0.
4. `git diff --stat origin/main` lists exactly `workflow.md`, `number_guards.py`, the two test files and ADR 0002.

## Stage Report: ideation

- DONE: Design, in the task file, the five fixes in the task's Scope (read the Codex comments on commit 2155bed: `gh api repos/iamcxa/qnow/pulls/1248/comments`), keeping it small: exact replacement wording for each passage, including the Captain's collision rule; which `test_sd_dispatch.py` phrases change, with a falsifier fixture holding the 0.10.1 text for each; whether number_guards.py (for "the applied task keeps its number") or kc-journey-map's journey-progress (for field clearing) needs any code change; which ADRs get one amendment line.
  `## Design` holds the five passages word for word and a collision Mermaid; the `FIXES` table is six fixes with 0.10.1 swaps, and on the 0.10.1 text all six report every phrase missing while a single-fix revert shows only its own gaps (spike, 2026-10-01). number_guards.py: docstring only (reserve and check already behave as the rule needs, two new tests, mutation-proved); journey-progress: no change (four-case reader run); ADR 0002 only.
- DONE: ACs with evidence plans; what needs the Captain beyond his 「准」; the Captain-run minimal acceptance script.
  Seven `**AC-n**` with evidence plans; one coupled Captain confirmation (a base-branch migration counts as applied; first of two applied tasks to merge keeps its number); four-command script; `design_surfaces.py check` printed `patch-0102.md: design surfaces presentable` (exit 0).
- SKIPPED: AC-1 not yet verified; implementation writes the passage and `FIXES["goal-change"]`, and only the spike text passed the six-fix assertion so far.
  Current evidence: spike run on an origin/main worktree, 0.10.1 text reports both phrases missing.
- SKIPPED: AC-2 not yet verified; implementation writes the Applied wording and `FIXES["shared-environment"]`.
  Current evidence: spike run, 0.10.1 text reports both phrases missing.
- SKIPPED: AC-3 not yet verified on the candidate; the two new number_guards tests and the collision falsifier passed on the spike only.
  Current evidence: `test_number_guards` 20 OK on the spike; `reserve` mutation fails 2 tests, ignoring `Applied at:` in `check` fails 5.
- SKIPPED: AC-4 not yet verified on the candidate; the clearing command and reader cases ran in a disposable workflow and a scratch script.
  Current evidence: `--set ... journey= ...` cleared all five keys; reader printed unverified, exists, unverified, exists (spacedock 0.27.2, origin/main `progress.mjs`).
- SKIPPED: AC-5 not yet verified on the candidate; the spike text passes `test_poc_readme` and `FIXES["backlog-revise"]`.
  Current evidence: the first draft naming `ideation` failed `test_poc_readme`; the reworded line passes.
- SKIPPED: AC-6 not yet verified on the candidate; the spike carries both fetch edits and the docstring line.
  Current evidence: spike run, 0.10.1 text reports both fetch phrases missing.
- SKIPPED: AC-7 not yet verified on the candidate; the spike passed the listed checks.
  Current evidence: `test_sd_dispatch.py` six PASS, `test_number_guards` 20 OK, `test_poc_readme`/`test_adr_doc_checks`/`test_design_surfaces`/`lint-skills.py` pass, `comment_ratio.py` 2.2 percent, `adr_lint.py --require 2` exit 0.

### Summary

Six spike-proven edits: five workflow passages (goal change, shared-environment freeze, collision rule, field clearing, backlog revise) plus the fetch fix, one docstring line, six falsifier fixtures, two tests and one ADR 0002 amendment line, with no logic change in `number_guards.py` or `journey-progress`. Spike output is in `/tmp` and is removed; the task file holds the wording and test text to rebuild it. The Captain decides one thing: whether a base-branch migration counts as applied and the first applied task to merge keeps its number.

## Stage Report: implementation

- DONE: Implement patch-0102's approved design (Captain 2026-10-01 「准」 and 「可以」: the five fixes, the collision rule, a base-branch migration counts as applied, of two applied unmerged tasks the first to merge keeps its number) exactly as the design's spike describes, touching only kc-dev-flow-2/** and docs/adr/0002-*.md (one amendment line; quoted words unchanged).
  Candidate 581991faaf6645348f056f660fa8d469b4ae955a on spacedock-ensign/patch-0102, one commit on base a12de3119bb1fe451cb2b5e436519b6132fc3d05 (origin/main); `git diff --stat a12de311 581991fa` lists exactly workflow.md, number_guards.py (docstring line), test_sd_dispatch.py, test_number_guards.py and ADR 0002 (+2 lines, quoted 「准」 unchanged); docs/dev2/README.md untouched; no version edit.
- DONE: Every AC with the evidence its "Verified by" names, including the six falsifier fixtures holding the 0.10.1 text and the two new number_guards tests.
  AC-1,2,3,5,6: `test_sd_dispatch.py --sd-plugin-root <SD 0.27.0 cache>` prints six PASS and `Not run:` (exit 0); on a12de311's workflow.md `fix_gaps` reports missing/old-present 2/1, 2/1, 7/2, 2/0, 1/1, 2/2 for goal-change, shared-environment, collision, clear-release-fields, backlog-revise, fetch-the-inspected-repo, and the test asserts each single-fix revert reports only that fix.
  AC-3 mutation: `taken |= task_facts(sibling)[args.kind]` replaced by `pass` fails both ReserveTests; dropping the `Applied at:` facts in `check` fails five AppliedFreezeTests; unmutated `test_number_guards.py` Ran 20 tests OK.
  AC-4: `spacedock status --set probe journey= journey-release= journey-story= journey-required-tasks= journey-mapping-complete=` in a disposable inline workflow left all five keys empty (spacedock 0.27.2); the four-case script on `origin/main:kc-journey-map/lib/progress.mjs` printed unverified, exists, unverified, exists.
  AC-6: `python3 scripts/number_guards.py --help` prints `git -C <repo> fetch`; AC-5: `test_poc_readme.py` exit 0.
- DONE: Follow this repo's CLAUDE.md: `fix(kc-dev-flow-2): …`, no version edits, stage files explicitly; the CI suite list green; the candidate's own `kc-dev-flow-2/scripts/comment_ratio.py` from the base exits 0; doc_impact.py reported; exact candidate SHA; the Captain-run minimal acceptance script rewritten against the shipped text.
  Commit `fix(kc-dev-flow-2): close five release-review and number-guard workflow gaps` with five files staged by name; all nine workflow-listed commands exit 0 (lint-skills, test_lint_skills, test_design_surfaces, test_adr_doc_checks, test_poc_readme, test_comment_ratio, test_number_guards, test_learning, test_sd_dispatch); `comment_ratio.py a12de311 HEAD` printed `code lines 89, comment lines 0, 0.0%`, `maximum 5% (package default) met`, exit 0; `adr_lint.py ../docs/adr --require 2` printed `7 ADR file(s) checked, 0 legacy`, exit 0; `design_surfaces.py check` on this task: presentable. No `## Number guards` section (Surfaces: none; ADR 0002 amended, none added), so number_guards.py check not run.
  doc_impact.py a12de311 HEAD (installed 0.10.1 copy) listed two documents: kc-dev-flow-2/README.md unaffected: it only lists the unchanged test_number_guards.py and test_sd_dispatch.py commands; kc-dev-flow-2/references/sd/adoption.md unaffected: it describes test_sd_dispatch.py's graph, mod and handoff checks, none of which changed.
  Acceptance script, from a checkout of 581991fa: (1) in `kc-dev-flow-2/` run `python3 scripts/test_sd_dispatch.py --sd-plugin-root <activated Spacedock plugin root>`: six PASS lines, the fifth naming the six fixes, then `Not run:`, exit 0; (2) in `kc-dev-flow-2/scripts/` run `python3 -m unittest test_number_guards`: `Ran 20 tests`, `OK`; (3) in `kc-dev-flow-2/` run `python3 scripts/adr_lint.py ../docs/adr --require 2`: `7 ADR file(s) checked, 0 legacy`, exit 0; (4) `git diff --stat a12de311 581991fa` lists five files: workflow.md, number_guards.py, the two test files, ADR 0002.

### Summary

Five workflow passages, the fetch fix, one docstring line, the six falsifier fixtures, two number_guards tests and one ADR 0002 amendment line are committed as 581991fa on the task branch with no logic change in number_guards.py or journey-progress. Material note: AC-7 and the design's Files line say "six files" but the design lists five (the sixth, docs/dev2/README.md, is deliberately unchanged), so the acceptance step 4 above names five. Not pushed; the first-to-merge tie-break and base-branch-counts-as-applied rules are prose FO applies, with no script detecting a collision between two task files.

## Stage Report: validation

- DONE: Independent verdict on candidate 581991faaf6645348f056f660fa8d469b4ae955a (branch spacedock-ensign/patch-0102, base a12de311) against patch-0102's approved design, its ACs and the Captain's rulings (「准」 with the collision rule; 「可以」: a base-branch migration counts as applied, of two applied unmerged tasks the first to merge keeps its number)
  PASSED, recommended: AC-1 to AC-7 hold at the candidate (evidence in the next two items); the shipped Collision text states both 「可以」 rules (applied incl. base-branch keeps its number; of two applied unmerged the first to merge keeps it); two Polish findings and one AC wording slip are listed in the Summary, none blocks.
- DONE: Reproduce on a `git archive` copy: the kc-dev-flow-2 CI suite list (test_sd_dispatch.py with the Spacedock v0.27.2 plugin root); `fix_gaps` on the 0.10.1 workflow.md and on the candidate, and each single-fix revert; the two new number_guards tests and the named mutations; the five-file scope
  Archive of 581991fa in /tmp/v0102: all nine CI commands exit 0 (test_sd_dispatch.py against spacedock-dev/spacedock at 4d158a48 = tag v0.27.2: six PASS, `Not run:`, exit 0); `fix_gaps` missing/old-present on the 0.10.1 file (byte-equal to a12de311's) 2/1, 2/1, 7/2, 2/0, 1/1, 2/2 and 0/0 for all six on the candidate, each single-fix revert reports exactly its own phrases and no other fix's; the two new tests pass; mutation `taken |= task_facts(sibling)[args.kind]` -> `pass` fails 2 (the new ReserveTest and test_reserve_never_collides_and_never_fills_a_gap), dropping `facts["applied"]` in `check` fails 5 AppliedFreezeTests including the new one; `git diff --name-status a12de311 581991fa` is five M files (workflow.md, number_guards.py, two tests, ADR 0002), docs/dev2/README.md and every manifest untouched; worktree `git status --short` empty.
- DONE: Read each of the five rewritten passages and the fetch fix against the six Codex comments on qnow #1248 commit 2155bed (`gh api repos/iamcxa/qnow/pulls/1248/comments`) and say for each whether it is closed; ADR 0002's amendment line (quoted words unchanged) with adr_lint; every added comment line; the candidate's own comment_ratio.py from a12de311; run the Captain acceptance script as written
  Of the six comments five are closed and one (the `<wrapper>` secret placeholder) is open by Scope non-goal; ADR 0002 diff is +2 -0 with 「准」 unchanged and `adr_lint.py ../docs/adr --require 2` prints `7 ADR file(s) checked, 0 legacy` exit 0; the candidate adds 0 comment lines and `comment_ratio.py a12de311 581991fa --workflow-dir docs/dev2` prints `code lines 89, comment lines 0, 0.0%`, `maximum 5% (package default) met`, exit 0; the four-step Captain script ran as written, all four observations matched.

### Summary

Verdict: PASSED. Candidate 581991fa passes the whole CI suite at the pinned v0.27.2 plugin root, every falsifier and the named mutations behave as the design claims, and five of the six Codex comments on 2155bed are closed.

Codex comments on 2155bed (read 2026-10-01 via `gh api`, line numbers are the adopter's copy):
- 4147220442 (P1, goal change suppressed by the skip check): closed. The skip check needs the same story ids, the same release and story `goal` text and no Captain goal ruling; a goal ruling with unchanged ids is now signal 2. See Polish 1.
- 4147220471 (P1, staging project's own production database not frozen): closed. The Applied bullet freezes a separate hosting project's database, and the Collision bullet gives the recovery the comment asked for (the unapplied task renumbers, no reset; an applied renumberer holds for the Captain, who resets a branch or deletes and recreates the project database; FO then records `Not applied: ... - database reset`). The new AppliedFreezeTests test shows R3, then R2 with the `Applied at:` line kept, then exit 0 once it is replaced.
- 4147220459 (P2, clear release fields): closed. I ran `spacedock status --set probe journey= journey-release= journey-story= journey-required-tasks= journey-mapping-complete=` (0.27.2, disposable workflow): all five keys stay present and empty and the listing omits them. The four-case reader script on `kc-journey-map/lib/progress.mjs` (identical to origin/main) printed unverified, exists, unverified, exists, and the same for omitted keys.
- 4147220429 (P2, backlog revise has no worker): closed. The backlog stage definition says "this boundary has no worker"; the sentence now routes it to FO or the proposal's author, and `test_poc_readme.py` exits 0.
- 4147220478 (P2, bare `git fetch`): closed at both sites (Reserve, Check) and in the `number_guards.py --help` text.
- 4147220413 (P2, `<wrapper>` secret placeholder): not closed here by Scope non-goal (adopter-owned, fixed in qnow #1248); `workflow.md` still carries the literal `<wrapper>` in Dispatch facts.

Findings (my classification is advisory; FO decides disposition):
- Polish 1: the skip check says the same "release and story `goal` text", but `canvas.md` gives stories `card:` and only releases `goal:`; a story-wording change without a Captain ruling is not compared. Observable harm is low because the same sentence adds "no Captain ruling has changed the goal of ... a story".
- Polish 2: when neither colliding task has an `Applied at:` line and neither is on the base branch, the Collision bullet gives no rule (the design's flowchart says the task `check` flags renumbers; 0.10.1 said the same). The text covers applied-vs-unapplied and both-applied only.
- AC wording: AC-7 says "the six files below"; the Design lists five and the Captain script, the diff and this check use five. ADR 0002's amendment attributes the whole line to 「准」 though the base-branch and first-to-merge rules came with 「可以」; the quoted words themselves are unchanged.

Limits: the first-to-merge and base-branch-counts-as-applied rules are prose FO applies and no script compares two task files; which deploys FO records as `Applied at:` is unchanged, so an unrecorded deploy is still not detected; a renumbering task that is itself applied still costs a reset or recreation; the installed spacedock cache only had 0.27.0, so the v0.27.2 root was cloned at the pinned commit.

Captain acceptance script (from a checkout of 581991fa; needs a clone of github.com/spacedock-dev/spacedock at tag v0.27.2):
1. In `kc-dev-flow-2/`: `python3 scripts/test_sd_dispatch.py --sd-plugin-root <path to that clone>` prints six `PASS` lines (the fifth names the six fixes) then `Not run:`, exit 0.
2. In `kc-dev-flow-2/scripts/`: `python3 -m unittest test_number_guards` ends `Ran 20 tests` and `OK`.
3. In `kc-dev-flow-2/`: `python3 scripts/adr_lint.py ../docs/adr --require 2` prints `7 ADR file(s) checked, 0 legacy`, exit 0.
4. `git diff --stat origin/main` (origin/main at a12de311) lists five files: ADR 0002, workflow.md, number_guards.py and the two test files.
Does not cover: whether FO applies the prose (goal-change skip check, collision rule, field clearing) correctly in a live run, the adopter's secret wrapper, or the adopter's re-sync of #1248.

### Polish fix

FO-authorized Polish fix (validation finding "AC wording"): the ADR 0002 amendment line now cites 「准」 at the backlog gate for the environment freeze and the collision rule, and 「可以」 at the ideation gate for base-branch-counts-as-applied and first-to-merge-keeps-the-number; quoted words verbatim, nothing else on the line or in the commit changed. New candidate SHA b88732c289d8f7d77a3617f72a83c785e2a7bea8 (on 581991fa, one file, one line). `adr_lint.py ../docs/adr --require 2` printed `7 ADR file(s) checked, 0 legacy`, exit 0; `test_adr_doc_checks.py` exit 0. Not pushed.
