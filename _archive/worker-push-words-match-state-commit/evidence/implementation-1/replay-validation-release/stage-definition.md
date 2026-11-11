### `validation`

A fresh ensign invokes `kc-dev-flow-2:validation` before useful work and checks
the exact artifact against the accepted profile outcome. It assesses the work;
it does not silently take over implementation. Rejection uses the supported
feedback path after the distinct FO disposition described below. Its recheck of a
repair is dispatched under the lane in Stages.

- **Outputs:** Independent verdict, primary evidence, a minimal acceptance script, the
  `python3 <package>/scripts/adr_lint.py docs/adr --since <base>` command run with its exit
  code, and unverified obligations recorded in the existing SD Stage Report.
- **Gate content:** Show actual checks and acceptance evidence, material findings
  and limits, and the user's pending delivery decision. For a `ui` task FO runs
  `python3 <package>/scripts/design_surfaces.py check <task>` and includes its
  output. Before the gate, FO runs the stage's minimal acceptance script under
  Captain steps, names its record on the summary's `Captain steps:` line, and
  returns an output that differs from the script through feedback.
  Before recommending delivery, FO confirms both goal sufficiency and minimal
  necessity from the same candidate's existing route evidence. Passing checks or
  approval replace neither condition; approval is not merge. When a POC report
  records `boundary-crossed:`, FO shows the marker and its evidence with the
  user's choice between profile selection and removing the crossing work with
  recorded cleanup through the feedback route, and does not recommend
  delivering that work as POC.

## Dispatch facts

- **Team:** You are one worker in a team completing the project goal; your stage
  and handoff serve that goal. Before substantial work or retrying a failure,
  check this task's prior reports, linked sibling tasks and PRs, and relevant
  workflow state: did someone already do this, hit this, or own it now? If your
  environment cannot run a required checklist check, tell FO before building
  work that depends on it. Ask FO early about overlapping ownership, repeated
  failures, missing authority or evidence, or infeasible targets. Give checked
  sources, findings, attempts and the specific question. With a mid-run FO
  channel, pause dependent work and continue safe independent work; without
  one, end your turn with that handback instead of waiting. Never answer your
  own or your reviewers' permission requests; route them to FO. FO coordinates
  peers and decisions; do not message peers or change others' work.
- **Signal:** send the completion message once, to the first officer by the name
  your session lists as addressable (`main` under Claude Code dispatch). The
  completion block's `team-lead` is Spacedock's default and is not registered
  there (spacedock-dev/spacedock #523, #608); do not try it first and do not
  describe a fallback in the report.
- **Package:** `<package>` in stage text is the `Package root:` line of the
  kc-dev-flow-2 skill you loaded; your dispatch's scope notes state the same path,
  and if they differ, use the skill's. Run package scripts only from it; never
  search the filesystem, `/tmp` or another install for them.
- **Secrets:** `scripts/with-dev-secrets.sh` is the only route to a development secret: run a
  command that needs one as `scripts/with-dev-secrets.sh <command>`. Never read or print a value.
  If a guard refuses a command that only mentions a secret-reading tool, rephrase
  it; do not split, encode or wrap the command to pass the guard.

## Review-finding disposition

Before repair authorization, product bytes and the recorded candidate revision stay
unchanged. Read-only inspection, non-mutating reproductions, existing tests and
throwaway-checkout probes are allowed. Report/gate commits may advance repository
HEAD without changing the candidate. Validators recommend `PASSED` or `REJECTED`;
new findings or changed evidence re-enter this checkpoint.

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

A `Follow-up:` line in Scope is not accepted scope by itself: the first stage of the
receiving task to meet it assesses it against its stated reason and earlier rulings. It builds the line only when the change alters no behaviour that an
accepted criterion, a Captain ruling or a journey contract relies on; otherwise it
returns the line to FO as a Needs decision. It records which, and why.
A finding FO declined in a committed gate summary or under `### FO declines` is settled:
a later validator does not report it again unless the candidate changes the lines or the
evidence the decline names, or new evidence would make it Material.

## Decision records

The implementation worker writes one ADR file per decision by its stage principles.
Validation runs `python3 <package>/scripts/adr_lint.py docs/adr --since <base>`, which
requires every record the candidate added or changed, plus `--require <numbers>` for
each `ADR:` number the task's `## Number guards` reserves and any number the
implementation report names; exit 1 or a missing record returns through the existing
feedback route, and exit 2 is a configuration error that returns to FO.

## Captain amendments

A change the Captain makes to what he has accepted, whether at a gate approval,
between gates or at a validation gate, is an amendment. A change he asks for
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
Asked: <the question or proposal he answered, verbatim, or the commit holding it>
Supersedes: <acceptance-criterion ids, or none> <optional: "(no replacement: <why>)">
Design: <optional: the design paragraph it overrides>
```

`Asked:` is required when his words do not name what they settle, such as 「同意第三點」. FO
names the amendment in the next dispatch's checklist. That worker (implementation, the
repair worker on a feedback route, or the worker of the stage a task is sent back to)
moves each superseded criterion's block verbatim from `## Acceptance criteria` into its
entry under a `Superseded text:` line, writes any replacement as a new `**AC-N**` under
a fresh id that says "Amended by Captain, amendment N", and never reuses an id. A
superseded criterion and the design paragraph named by `Design:` are withdrawn; evidence
and the Captain's acceptance script follow `## Acceptance criteria` plus the entries.

Sending an approved task back to an earlier stage, such as a design redo a release
review asks for, is the Captain's decision and is recorded as an amendment whose
`Design:` names what is redone; FO then runs `spacedock status --workflow-dir <dir>
--set <slug> status=<stage>`, and that stage's gate is approved again before the task
moves on.

`python3 <package>/scripts/design_surfaces.py check <task>`, run by implementation and
validation, prints each defect and exits 1; repair findings return through feedback. It cannot see a skipped record or
move, or FO's words in `Design:`.

## Affected documents

Implementation runs `python3 <package>/scripts/doc_impact.py <base> <candidate>`
and records, for each listed document, `updated` or `unaffected: <reason>` in its
stage report; validation reruns it at the candidate and checks every listed
document carries one. Make the update itself by the retained-document practices in
the package's `references/retained-documents.md`.

## Number guards

Applies when the task's `Surfaces:` includes `db`, or the task lands an ADR, including one first required by a ruling in a worker report or mid-stage feedback, whose number FO reserves before the next dispatch; the POC bullet below applies to every `poc` task.
`python3 <package>/scripts/number_guards.py --help` lists the flags and rules;
`trunk:`, `migrations-path:` and `adr-path:` (default `docs/adr`) come from this README's frontmatter.

- **Applied.** `check` freezes a migration in a commit recorded `Applied at:` (R2).
  `Applied: none as of <sha>` records that
  nothing was pushed up to that commit; a validator that finds none of `Applied at:`,
  `Not applied:` or `Applied: none` reports the missing record to FO instead of
  re-checking deploys. A task with no `Migration:` line owes none of these.
- **Check.** `python3 <package>/scripts/number_guards.py check --workflow-dir <workflow-dir> --task <task file>`
  runs at implementation exit, at validation and, after `git -C <repo> fetch`, on the PR
  head before FO asks for merge. Exit 2 is a configuration error, which returns to FO
  as a hold.
- **POC.** A task whose recorded `profile` is `poc` adds, edits and deletes no migration
  file and reserves no number. A `FAIL R6` crosses the POC boundary
  (a schema change persists across sessions): the worker records
  `boundary-crossed: persistent-state` naming the path, and the task is not repaired in
  place.
