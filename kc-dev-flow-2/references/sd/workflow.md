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
  states:
    - name: backlog
      initial: true
      gate: true
    - name: ideation
      gate: true
    - name: implementation
      worktree: true
      context-sections:
        - Review-finding disposition
        - Decision records
        - Affected documents
        - Delivery authority
    - name: validation
      worktree: true
      fresh: true
      feedback-to: implementation
      gate: true
      context-sections:
        - Review-finding disposition
        - Decision records
        - Affected documents
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

### `backlog`

The user selects the compatible profile and approves outcome, scope and budget.
FO records the choice; this boundary has no worker or placeholder report. FO
also records, under a `## FO alignment` heading in the task file, whether FO
direction alignment with the Captain is needed before the next declared stage
and why; a
stated reason is the whole record when not needed.

- **Gate content:** Show the selected variant/profile, proposed outcome, scope,
  exclusions and evidence needed before the next declared stage starts, and the
  `## FO alignment` need and reason.

### `ideation`

The default ensign invokes `kc-dev-flow-2:ideation` before useful work, using the
work item's recorded variant/profile and the skill's own profile routing table.
FO aligns direction and requests research when it can change a decision; the
worker authors the PRFAQ and optional preview. When `## FO alignment` records
alignment as needed, FO records the alignment result as a `Result:` line
before dispatching the worker. Missing skill or profile authority requires a
hold report rather than a baseline or default-profile substitution.

- **Outputs:** Current design definition and acceptance criteria with reproducible
  evidence clauses; unresolved decisions identified for the user.
- **Gate content:** Present PRFAQ/Mermaid with matching actors, order, branches,
  approvals and stops, acceptance evidence/limits, and a preview when relevant.
  Required diagram defects or missing current-stage evidence block recommendation
  and gate preparation/presentation; honest unverified future checks do not.
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
return to the affected user decision. Apply Review-finding disposition to repairs.

- **Outputs:** Exact delivered artifact, checks actually run, and material limits
  recorded in the existing SD Stage Report.

### `validation`

A fresh ensign invokes `kc-dev-flow-2:validation` before useful work and checks
the exact artifact against the accepted profile outcome. It assesses the work;
it does not silently take over implementation. Rejection uses the supported
feedback path after the distinct FO disposition described below.

- **Outputs:** Independent verdict, primary evidence, a minimal acceptance script
  and unverified obligations recorded in the existing SD Stage Report.
- **Gate content:** Show actual checks and acceptance evidence, material findings
  and limits, and the user's pending delivery decision. FO presents the stage's
  minimal acceptance script itself at the gate, not a pointer into the report.
  Before recommending delivery, FO confirms both goal sufficiency and minimal
  necessity from the same candidate's existing route evidence. Passing checks or
  approval replace neither condition; approval is not merge.

### `done`

The terminal state remains behind SD's merge-finalize boundary. Consuming a
terminal gate approval is not completion; a live run requires the declared
delivery evidence and successful `merge guard` with an explicit verdict.
Apply Delivery authority below; a pending PR or missing hook is not completion.

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
The implementation worker writes the record into the candidate and names the ADR
numbers it added or changed in its report; validation runs
`python3 <package>/scripts/adr_lint.py docs/adr --require <numbers>` and returns a
failure or a missing record through the existing feedback route; FO confirms it
before presenting the gate. A deferred user-facing capability belongs on the
product's journey map, not here.

## Affected documents

Implementation runs `python3 <package>/scripts/doc_impact.py <base> <candidate>`
and records, for each listed document, `updated` or `unaffected: <reason>` in its
stage report; validation reruns it at the candidate and checks every listed
document carries one. The list finds candidates by the paths and declared names
the change touched; it does not decide relevance. Make the update itself by the
retained-document practices in the package's `references/retained-documents.md`.

## Delivery authority

The adopted `_mods/pr-merge.md` is the unmodified mod from the activated SD
package. Before delivery, confirm the file still matches the reviewed source
(or an explicitly approved project customization) and its merge hook is
registered. Missing/changed delivery configuration requires a hold: `merge: pr`
alone does not block SD's no-hook local-finalize route.

Project and Captain authority constrain hook instructions: present the exact
candidate and PR body before authorized push/create; create a Draft PR where
required, and request ready only after the required CI is green. Approval of a
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
