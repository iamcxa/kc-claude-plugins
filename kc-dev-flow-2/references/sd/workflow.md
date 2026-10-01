---
commissioned-by: kc-dev-flow-2
entity-type: task
id-style: slug
entity-label: task
entity-label-plural: tasks
state: .spacedock-state
trunk: main
stages:
  defaults:
    worktree: false
    concurrency: 1
    model: sonnet
  states:
    - name: backlog
      initial: true
      gate: true
    - name: ideation
      gate: true
      context-sections:
        - Dispatch facts
    - name: implementation
      worktree: true
      context-sections:
        - Dispatch facts
        - Review-finding disposition
        - Decision records
        - Captain amendments
        - Affected documents
        - Number guards
        - Delivery authority
    - name: validation
      worktree: true
      fresh: true
      feedback-to: implementation
      gate: true
      context-sections:
        - Dispatch facts
        - Review-finding disposition
        - Decision records
        - Captain amendments
        - Affected documents
        - Number guards
        - Delivery authority
    - name: done
      terminal: true
---

# Development workflow

This is the adopted workflow's authority for SD stages and task schema. Resolve
its absolute directory and retain `--workflow-dir` on SD commands, including
worker reads and recovery. Skills guide work; SD owns dispatch, gates and state.

## File Naming

Each task is a flat `<slug>.md` file in the resolved state checkout. Keep existing
IDs and tasks in their recorded workflow; new work does not migrate old work.

## Schema

Record `id`, `title`, `status`, `variant: kc-dev-flow-2`, and the user's selected
`profile`. The five-stage route accepts `pilot` or `prod`; the POC adaptation
removes ideation from both frontmatter and Stages and accepts `poc` only.
Before admission and dispatch, FO checks that the selected profile matches this
workflow's actual ordered stages. Unknown/mismatched profiles require a hold,
not an invented transition or default. SD does not enforce this profile rule.
Preserve the approved outcome, scope, non-goals, budget and stop condition in the
body. Use bold **AC-N** declarations with individual evidence clauses.

## Stages

Stage workers run on the workflow's default model.
`kc-dev-flow-2:chief-engineer` and `kc-dev-flow-2:engineering-reviewer` run on the
model and reasoning their agent files declare; FO never dispatches them on a
cheaper model, because their value is a stronger second judgment.

`concurrency` limits only what `status --next` proposes (Spacedock 0.27.2 does not
slot-check a reflow dispatch; `<package>/scripts/test_sd_dispatch.py` builds one while another
entity holds the only `implementation` slot). A feedback-reflow repair and an FO fix
authorized under Review-finding disposition step 3 are dispatched at once in the
entity's own worktree, after the existing overlap check against running worktrees; they
do not wait for another entity's worker in the same stage. The validation recheck of
that repair or fix does not wait for another entity's worker either, but it is
dispatched only after the repair or fix has completed and committed its candidate, so
the validator reads the bytes that will be delivered. A repair that outgrows what its
assignment names returns to FO as a scope change.

FO resolves `<package>` in this workflow from the `Package root:` line of
`kc-dev-flow-2:dev`. Every worker dispatch FO builds carries that absolute path
as a `Package root: <absolute path>` line in its scope notes
(`--scope-notes-file`), which land in the dispatch file the worker reads first.
A checklist or scope-notes line that names a package script writes
`<package>/scripts/NAME.py` with the absolute root substituted, never the bare
script name. When `status --set` refuses to leave a stage, run
`status --workflow-dir <dir> --read <task> --stage <stage> --checklist`, return
any line it reports as neither DONE nor SKIPPED to the worker, and do not edit the
worker's report. The refusal itself does not say why; other causes are a missing
evidence line or Summary and an uncommitted report.

### `backlog`

The user selects the compatible profile and approves outcome, scope and budget.
FO records the choice; this boundary has no worker or placeholder report. FO
also records, under a `## FO alignment` heading in the task file, whether FO
direction alignment with the Captain is needed before the next declared stage
and why; a
stated reason is the whole record when not needed. On the five-stage route, FO
also records a `Surfaces:` line under the same heading: any of `ui`, `db`,
or `none`, read from the change surface rather than the diff, and next to it
a `Visible change:` line: one sentence on what a user sees or operates
differently, or `Visible change: none`.

- **Gate content:** Show the selected variant/profile, proposed outcome, scope,
  exclusions and evidence needed before the next declared stage starts, the
  `## FO alignment` need and reason, and the recorded `Surfaces:` and
  `Visible change:` lines on the five-stage route.
- **Seed check:** On the five-stage route, before `gate prepare`, FO runs
  `python3 <package>/scripts/design_surfaces.py check --seed <task>` and holds the
  gate until it exits 0. It reads the `## FO alignment` record only: a `ui` or `db`
  seed owes no artifact yet, the worker authors it, and the `Result:` line is not
  checked. An FO that skips this step still dispatches; the worker's own check is
  the backstop.
- **Release review:** Applies to a task that belongs to a release on a journey map
  (`journey`, `journey-release`, `journey-story`); a task with no release, such as a
  bug, infrastructure or workflow maintenance, is outside it. Four signals: (1) a task
  admitted into a release; (2) a Captain scope ruling that moves a story or task into
  or out of a release or changes the goal of the release, a story or a task; (3) a UAT
  failure that crosses two or more tasks; (4) a batch about to enter implementation. Signals 1 and 2 only mark the
  release changed: FO names the release and the signal in the task's `## FO alignment`
  reason. A task whose `journey-story` is already on the map in that release passes with
  that one check and marks nothing when, since its latest `Release review:` line, the
  journey file still holds the same story ids and the same release and story `goal`
  text and no Captain ruling has changed the goal of the release, a story or a task.
  A changed goal is signal 2 although no story id moved; FO marks the release
  changed in that task's `## FO alignment` reason. Signal 4 is the single checkpoint: at the first
  implementation dispatch for a release marked changed, FO dispatches a fresh worker
  with kc-journey-map's `review-release` mode, then splits tasks from its output; an
  unchanged release proceeds. One review covers every change since the last. Signal 3
  runs the review at once. FO writes no map and no candidate; the Captain accepts
  membership in conversation or at this gate. FO records under `## FO alignment` either
  `Release review: <journey>/<release-id> at <journey-file commit>` or
  `Release review: not needed: <reason>`; no script checks that line. When FO approves
  a task into a release story at this gate it sets the three fields with
  `spacedock status --workflow-dir <dir> --set <task> journey=<the map's journey: value> journey-release=<id> journey-story=<id>`;
  a worker never edits frontmatter. Where the adopter tracks completion with
  kc-journey-progress, FO also writes `journey-required-tasks` (full task ids) and
  `journey-mapping-complete: true` on one task per story at the review's split step.
  When signal 2 moves a task out of a release, FO clears its release fields with
  `spacedock status --workflow-dir <dir> --set <task> journey= journey-release= journey-story= journey-required-tasks= journey-mapping-complete=`
  (a field set to nothing is cleared) and, where kc-journey-progress is tracking,
  removes the task's full id from `journey-required-tasks` on the declaring task of
  its old story; when the cleared task was the declaring one, FO moves that list and
  `journey-mapping-complete: true` to another member of the story. A task moved to
  another story gets the new values from the set command above and its id is added to
  that story's list. kc-journey-progress reports a story unverified until its
  declaration matches its members.

### `ideation`

FO may dispatch ideation on a stronger model when the design is hard to reverse,
such as an event model, an architecture or a security boundary, and says so in
the dispatch. The default ensign invokes `kc-dev-flow-2:ideation` before useful work, using the
work item's recorded variant/profile and the skill's own profile routing table.
FO aligns direction and requests research when it can change a decision; the
worker authors the PRFAQ and the artifact each recorded surface owes. When
`## FO alignment` records alignment as needed, FO records the alignment result
as a `Result:` line before dispatching the worker. Missing skill or profile
authority requires a hold report rather than a baseline or default-profile
substitution.
Ideation writes no repository file, branch or commit: the design, the criteria and any
ADR draft live in the task file, and a draft carries no ADR number.

- **Outputs:** Current design definition and acceptance criteria with reproducible
  evidence clauses; unresolved decisions identified for the user.
- **Gate content:** Present PRFAQ/Mermaid with matching actors, order, branches,
  approvals and stops, acceptance evidence/limits, and each recorded
  `Surfaces:` value's artifact. The gate is not presentable without the
  artifact each recorded surface owes. Before `spacedock gate prepare`, FO runs
  `python3 <package>/scripts/design_surfaces.py check <task>`; a non-zero exit,
  including a missing `## Acceptance criteria` section or one that declares no
  criterion, means the gate is not presentable, and FO includes the checker's output in
  the gate material. Required diagram defects or missing current-stage
  evidence block recommendation and gate preparation/presentation; honest
  unverified future checks do not.
  FO may correct design prose/Mermaid to reflect established decisions under an
  actual Captain grant covering that task's exact design section; reuse a matching
  standing grant. Template adoption grants no authority. Record the decision basis;
  preserve scope, acceptance criteria, risk acceptance, product code, worker
  evidence, prior reports, approvals and verdicts. Withdraw an affected open binding
  before editing, then reprepare through the applicable SD lifecycle. Other
  corrections require an authorized author; hold where no supported route applies,
  without inventing same-stage rework. Present a concise recommendation, including
  routine details; ask about unresolved material scope, interface, acceptance or
  authority choices. Corrections neither replace user approval nor advance stages.

### `implementation`

The default ensign invokes `kc-dev-flow-2:implementation` before useful work,
using the recorded profile and approved scope. Produce the bounded integrated
result and its evidence. Missing inputs require a hold; scope/profile changes
return to the affected user decision. Apply Review-finding disposition to repairs;
a repair is dispatched under the lane in Stages.

- **Outputs:** Exact delivered artifact, checks actually run, and material limits
  recorded in the existing SD Stage Report.

### `validation`

A fresh ensign invokes `kc-dev-flow-2:validation` before useful work and checks
the exact artifact against the accepted profile outcome. It assesses the work;
it does not silently take over implementation. Rejection uses the supported
feedback path after the distinct FO disposition described below. Its recheck of a
repair is dispatched under the lane in Stages.

- **Outputs:** Independent verdict, primary evidence, a minimal acceptance script
  and unverified obligations recorded in the existing SD Stage Report.
- **Gate content:** Show actual checks and acceptance evidence, material findings
  and limits, and the user's pending delivery decision. FO presents the stage's
  minimal acceptance script itself at the gate, not a pointer into the report.
  Before recommending delivery, FO confirms both goal sufficiency and minimal
  necessity from the same candidate's existing route evidence. Passing checks or
  approval replace neither condition; approval is not merge. When a POC report
  records `boundary-crossed:`, FO shows the marker and its evidence with the
  user's choice between profile selection and removing the crossing work with
  recorded cleanup through the feedback route, and does not recommend
  delivering that work as POC.

### `done`

The terminal state remains behind SD's merge-finalize boundary. Consuming a
terminal gate approval is not completion; a live run requires the declared
delivery evidence and successful `merge guard` with an explicit verdict.
Apply Delivery authority below; a pending PR or missing hook is not completion.

## Dispatch facts

Spacedock inlines this section into each stage whose `context-sections` lists it.

- **Signal:** send the completion message once, to the first officer by the name
  your session lists as addressable (`main` under Claude Code dispatch). The
  completion block's `team-lead` is Spacedock's default and is not registered
  there (spacedock-dev/spacedock #523, #608); do not try it first and do not
  describe a fallback in the report.
- **Package:** `<package>` in stage text is the `Package root:` line of the
  kc-dev-flow-2 skill you loaded; your dispatch's scope notes state the same path,
  and if they differ, use the skill's. Run package scripts only from it; never
  search the filesystem, `/tmp` or another install for them.
- **Secrets:** `<wrapper>` is the only route to a development secret: run a
  command that needs one as `<wrapper> <command>`. Never read or print a value.
  If a guard refuses a command that only mentions a secret-reading tool, rephrase
  it; do not split, encode or wrap the command to pass the guard.

## Review-finding disposition

Apply this checkpoint to findings from implementation, validation, detached audits,
consequential FO quick work and rejected gates.

1. Reviewers observe; workers' classifications and `actor:ensign` Resolutions are
   advisory. Preserve findings and assess the four evidence fields below, separating
   materiality, ownership and disposition. Missing required evidence or unresolved
   classification requires investigation or hold.
2. Within approved boundaries, FO may explicitly decline evidenced Deferred risk
   or Polish in the existing committed gate summary, naming the finding, reason
   and candidate revision. This FO-authored decision requires no live worker or
   reviewer rerun for acknowledgement; preserve worker reports and verdicts.
3. Repairs require worker investigation without candidate mutation, distinct FO
   `fix` authorization through the runtime's addressable-worker boundary, then
   independent validation. Without that authorization, hold.
4. Scope, value, threshold, tolerance, risk-acceptance and acceptance-criteria
   changes require the Captain. Material findings cannot use the record-only lane;
   hold/route-for-decision forbids repair and reviewer rerun.
5. A round is one verdict of an external reviewer of the delivery on the PR head
   (Codex on the PR, RoboRev or another); FO counts rounds and records the count in
   the committed gate summary. A finding assessed Material, or labelled P1 by the
   reviewer, blocks in every round: a reviewer P1 is fixed and revalidated, or waived by the
   Captain with the reason recorded (step 4). For an external reviewer that has no
   P1 label, its highest severity level counts as P1 (e.g. RoboRev). Rounds 1 and 2
   follow steps 1 to 4.
   From round 3 a finding that is neither does not start a repair cycle: FO declines
   it in the committed gate summary, naming the finding and its home, and adds a
   `Follow-up:` line to that task's Scope, the open task whose Scope edits the
   finding's file, else a new backlog task from `spacedock new`. The terminal gate
   lists each follow-up and its home.

Before repair authorization, product bytes and the recorded candidate revision stay
unchanged. Read-only inspection, non-mutating reproductions, existing tests and
throwaway-checkout probes are allowed. Report/gate commits may advance repository
HEAD without changing the candidate. Validators recommend `PASSED` or `REJECTED`;
new findings or changed evidence re-enter this checkpoint. Rejection routing carries
evidence, classifications, authorized dispositions and assignment without re-triage.

The four evidence fields are released user and normal workflow; observable harm;
affected value acceptance criterion or non-negotiable boundary; and trigger
evidence. Field 3 uses `value-ac[AC-N]`, `captain-ruling[YYYY-MM-DD]`, or
`contract[repo/relative/path#anchor]` plus a nonblank claim. `none:` with a rationale
does not establish Material.

- **Material:** all four fields establish supported-workflow harm to a protected
  boundary or value acceptance criterion.
- **Deferred risk:** hypothetical, unsupported, unobserved or unpromised trigger;
  record what would make it material.
- **Polish:** no current user-visible loss or protected boundary is at risk.
- **Needs decision:** the task cannot own the scope, product or compatibility call.

Materiality and ownership are independent. Owned Material is eligible for an
FO-authorized fix; out-of-scope Material holds as Needs decision. Deferred risk
or Polish may use the recorded FO decline above within existing risk acceptance.

## Decision records

A ruling settled at a gate, in a worker report, or mid-stage feedback — a rule
about the product, a constraint, or a direction later work must respect — is
landed as an ADR before the next gate is presented, at latest by the terminal
approval. A ruling that governs only this task's own work stays in the task.
Write one file per decision, `docs/adr/NNNN-short-title.md`, in the
ADR format of the kc-dev-flow-2 package's `references/adr-template.md`: Nygard's sections as adr-tools writes them, with
the decider's own words and the options considered inside Decision. Create
`docs/adr/` with this record if it is absent. A decision document that predates
this format may stay as one record marked `Status: Legacy`; new rulings get their
own files. This is not the gate `resolution.reason` or the SD stage report.
A design names an ADR by its ruling and the file's short title, with no number; FO
reserves the number when it dispatches implementation (Number guards) and the
implementation worker writes `docs/adr/<reserved number>-<short-title>.md`.
The implementation worker writes the record into the candidate and names the ADR
numbers it added or changed in its report; validation runs
`python3 <package>/scripts/adr_lint.py docs/adr --require <numbers>` and returns a
failure or a missing record through the existing feedback route; FO confirms it
before presenting the gate. A deferred user-facing capability belongs on the
product's journey map, not here.

## Captain amendments

A change the Captain makes to what he has accepted, whether at a gate approval,
during implementation or at a validation gate, is an amendment. A change he asks for
while the gate that would accept it is still open is not one: he calls `revise`; at a stage
with no `feedback-to` that dispatches a worker, that stage's worker reworks it; at a stage
whose gate has a `feedback-to`, the revision goes to that target and the stage's worker
re-reviews it; and at `backlog`, which dispatches no worker, FO revises the recorded outcome,
scope or budget, or asks the proposal's author to.

FO appends one entry per amendment to the task's `## Captain amendments` section and
changes nothing else in it. FO adds no words of its own and does not move or rewrite a criterion:

```
## Captain amendments

### Amendment 1 — <date>, <gate or chat>
Captain: 「<his words, verbatim>」 (where he said them)
Supersedes: <acceptance-criterion ids, or none>
Design: <optional: the design paragraph it overrides>
```

FO names the amendment in the next dispatch's checklist. That worker (implementation,
or the repair worker on a feedback route) moves each superseded criterion's block verbatim
from `## Acceptance criteria` into its entry under a `Superseded text:` line, writes any
replacement as a new `**AC-N**` under a fresh id that says "Amended by Captain, amendment N",
and never reuses an id. A superseded criterion and the design paragraph named by
`Design:` are withdrawn; evidence and the Captain's acceptance script follow
`## Acceptance criteria` plus the entries.

`python3 <package>/scripts/design_surfaces.py check <task>` exits 1 when an entry has no
`Captain:` line or a superseded id is still declared in `## Acceptance criteria`;
implementation and validation run it, and exit 1 is a repair finding returned through feedback.
Between FO's record and the worker's move the task shows both, and the check says so.
It cannot see a skipped record, only the state after a skipped move; a moved block is
not scanned by `spacedock status --read --ac-scan`, which is why relocation, not
annotation in place, is the route.

## Affected documents

Implementation runs `python3 <package>/scripts/doc_impact.py <base> <candidate>`
and records, for each listed document, `updated` or `unaffected: <reason>` in its
stage report; validation reruns it at the candidate and checks every listed
document carries one. The list finds candidates by the paths and declared names
the change touched; it does not decide relevance. Make the update itself by the
retained-document practices in the package's `references/retained-documents.md`.

## Number guards

Applies when the task's `Surfaces:` includes `db`, or its design lands an ADR.
`<package>/scripts/number_guards.py` takes its values from this workflow's README
frontmatter (`--workflow-dir <workflow-dir>`): `trunk:`, the optional
`migrations-path:` (the adopter's migration directory) and `adr-path:` (default
`docs/adr`); a flag of the same name overrides. It reads a task's numbers and
applied deploys from the `## Number guards` section of the task file.

- **Reserve.** Before an implementation dispatch, FO runs `git -C <repo> fetch`, then
  `python3 <package>/scripts/number_guards.py reserve --kind migration|adr --workflow-dir <workflow-dir> --repo <repo> --task <task file>`
  once per kind the task needs, when the implementation dispatch is built and not
  earlier. FO records each printed `Migration: NNNN` /
  `ADR: NNNN` line under `## Number guards` in the task and repeats the lines as
  dispatch scope notes. One number per kind per task; a task needing more returns
  to FO.
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
- **Check.** `python3 <package>/scripts/number_guards.py check --workflow-dir <workflow-dir> --task <task file>`
  runs at implementation exit, at validation and, after `git -C <repo> fetch`, on the PR
  head before FO asks for merge. Exit 1 lists `FAIL R1..R5` lines; exit 2 is a
  configuration error, which returns to FO as a hold. A migration on the base
  branch must not change, comment-only edits included; `check` exit 1 (R1, R2) is
  the enforcement, and the fix is reverting the edit and writing a new migration.
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
  `check` accepts the renumber. A branch reset is one Netlify Open API call, `netlify api resetSiteDatabaseBranch --data '{"site_id":"<site>","branch_id":"<branch>"}' > /dev/null`
  (`netlify api --list` shows the method). The response carries connection
  strings, so redirect it to `/dev/null` and read the result from the next
  deploy. This step is documented, not wrapped in a tool.

## Delivery authority

The adopted `_mods/pr-merge.md` is the unmodified mod from the activated SD
package. Before delivery, confirm the file still matches the reviewed source
(or an explicitly approved project customization) and its merge hook is
registered. Missing/changed delivery configuration requires a hold: `merge: pr`
alone does not block SD's no-hook local-finalize route.

Project and Captain authority constrain hook instructions: present the exact
candidate and PR body before authorized push/create; create a Draft PR where
required, and request ready only after the required CI is green. Required CI is green
only when its test jobs have finished on the PR head. Where CI skips drafts, FO
marks the PR ready under the Captain's authority and waits for those jobs to
finish before asking for merge. Approval of a
validation gate is not permission to push, create or merge a PR. Preserve manual
merge authority. Do not invoke local fallback, push the trunk, merge, or clean up
an owned worktree unless the specific action is authorized. An upstream hook's
default fallback is not that grant. A failure holds delivery pending an explicit
choice. These are orchestration instructions, not added mechanical guardrails.

Use SD's pending terminal approval and existing merge hook; do not invent another
PR stage. Observe the actual repository-qualified PR merge before recording its
landed sentinel and running SD merge guard to finalize/archive. CI green, PR
creation, gate approval and a locally manufactured sentinel do not prove merge.

A PR delivers only the commit on its head. Before asking for merge, FO confirms the
PR head equals the candidate the latest passing validation report names; a repair
validated after the PR was opened reaches the PR only when that exact commit is
pushed to its branch.

## Workflow State

The README and `_mods` stay in the code repository; mutable task state lives in
`.spacedock-state`, an ignored linked checkout of this workflow's distinct orphan
state branch. Commission/refit owns setup; a fresh clone uses SD state init.
Implementation and validation share the task's registered code worktree; validation
uses a fresh worker. POC uses independent validation in this variant; direct POC
eligibility and special Production recovery routes are not implemented.

## Task Template

```markdown
---
id: <task-id>
title: <bounded outcome>
status: backlog
variant: kc-dev-flow-2
profile: <selected-profile>
merge: pr
worktree:
pr:
---

<Why this outcome matters.>

## Scope

<Approved scope, non-goals, budget and stop condition.>

## Acceptance criteria

**AC-1**: <Observable outcome.>
Verified by: <Reproducible evidence and its limits.>
```

Optional frontmatter, absent until used: `journey`, `journey-release` and
`journey-story`, set by FO with `status --set` when the task belongs to a release
story (see `backlog`, Release review). `journey` holds the map's own `journey:` value,
not its file name. A placeholder comment would sit beside the real values once
`status --set` filled them, so the template carries none.
