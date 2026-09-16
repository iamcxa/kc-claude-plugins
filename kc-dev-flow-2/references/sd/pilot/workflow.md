---
commissioned-by: kc-dev-flow-2@fixture
entity-type: task
entity-label: task
entity-label-plural: tasks
state: $inline
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
      context-sections:
        - Review-finding disposition
    - name: validation
      fresh: true
      feedback-to: implementation
      gate: true
      context-sections:
        - Review-finding disposition
    - name: done
      terminal: true
---

# Pilot dispatch fixture

The test copies this definition to README.md in a disposable standalone
repository, keeping the source template out of README-based workflow discovery.
Inline state and no per-stage worktree are deliberate fixture isolation choices,
not a replacement for a shipping project's ownership policy. Synthetic stage
snapshots test transport; they do not witness user approvals or worker execution.
No local delivery/merge hook is configured: hold any future live terminalization
until its delivery authority and merge guard path are concretely bound.

## File Naming

Each synthetic task is a flat `<slug>.md` file beside the copied workflow README.

## Schema

Each task records `id`, `title`, `status`, `variant: kc-dev-flow-2`,
`profile: pilot`, and `source: synthetic-cli-fixture`. Status is one of the five
declared stages. No approval or worker completion is fabricated. The AC scanner
test adds a labelled synthetic report header with no evidence, solely to exercise
its required report context; it does not represent historical stage work.
The work item body carries scope and acceptance criteria. A live run would first
need actual admission, host skill discovery and the existing SD gate procedure.

## Stages

### `backlog`

The user selects Pilot and approves the outcome, scope and budget. FO records
the choice; this boundary has no worker or placeholder report.

- **Gate content:** Show the selected variant/profile, proposed outcome, scope,
  exclusions and evidence needed before design starts.

### `ideation`

The default ensign invokes `kc-dev-flow-2:ideation` before useful work, using the
work item's recorded variant/profile and the skill's own profile routing table.
FO aligns direction and requests research when it can change a decision; the
worker authors the PRFAQ and optional preview. Missing skill or profile authority
requires a hold report rather than a baseline or default-profile substitution.

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
the exact artifact against the accepted Pilot outcome. It assesses the work;
it does not silently take over implementation. Rejection uses the supported
feedback path after the distinct FO disposition described below.

- **Outputs:** Independent verdict, primary evidence and unverified obligations
  recorded in the existing SD Stage Report.
- **Gate content:** Show actual checks and acceptance evidence, material findings
  and limits, and the user's pending delivery decision. Before recommending
  delivery, FO confirms both goal sufficiency and minimal necessity from the
  same candidate's existing route evidence. Passing checks or approval replace
  neither condition; approval is not merge.

### `done`

The terminal state remains behind SD's merge-finalize boundary. Consuming a
terminal gate approval is not completion; a live run requires the declared
delivery evidence and successful `merge guard` with an explicit verdict.
This fixture does not implement that delivery path or execute gate/merge actions.

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

## Workflow State

All state stays in the disposable fixture repository. Generated dispatch files
remain CLI transport artifacts; no emitted prompt is sent to a model by the test.
Use `${SPACEDOCK_BIN:-spacedock}` and forward its envelope unchanged in a future
authorized live run; no wrapper loader or unsupported `stage.skill` field exists.

## Task Template

```markdown
---
id: <unique-fixture-id>
title: Synthetic Pilot dispatch boundary
status: backlog
variant: kc-dev-flow-2
profile: pilot
source: synthetic-cli-fixture
---

This synthetic snapshot tests CLI transport, not prior approvals or completed work.

## Scope

Read the declared stage and produce a dispatch pointer; do not execute it.

## Acceptance criteria

**AC-1**: The pointer resolves to the selected variant's stage instruction.
Verified by: model-free CLI artifact and stage-definition inspection.
```
