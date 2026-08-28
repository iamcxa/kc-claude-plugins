# KC Dev Flow Planning and Development Boundary Design

**Status:** Approved by the Captain on 2026-08-28

## Problem

KC Dev Flow currently assumes that every admitted item comes from an external
planning provider with a planning window and outcome. PR #306 also adds portable
rules for one planning item, one Spacedock task, and one isolated execution
context. Those rules mix three separate concerns:

- planning decides what outcome is worth pursuing and when;
- KC Dev Flow turns an accepted target into proportionate implementation proof;
- a runtime adapter decides whether Hermes, Conductor, Spacedock, a worktree, or
  manual steering executes the work.

The coupling makes small standalone patches unnecessarily expensive and makes a
future GitHub Project-to-Linear migration look like a development-flow change.
It also lets exploratory work drift into delivery before planning has accepted
what the evidence means.

## Decision

Keep one KC Dev Flow product and one profile engine. Split its inputs into two
required brief shapes and one optional planning receipt:

| Input | Required for | Purpose |
|---|---|---|
| Development Brief | Pilot and Production delivery work | Fix the problem, accepted outcome, non-goals, acceptance evidence, and route-back conditions. |
| Exploration Brief | POC or Spike work | Fix one decision, falsifier, budget, and stop condition. |
| Planning Receipt | Work scheduled by GitHub Project, Linear, or another provider | Bind the provider source, Cycle, and Release/Milestone; current Ready membership is re-read. |

The existing `kc-dev-flow-work-profile/v3` POC fields are the Exploration Brief;
no new profile or stored schema is needed. The Development Brief is the readable
work-item content. The Planning Receipt is optional, complete-or-absent metadata;
it is not a second copy of the brief.

## Authority and revision binding

For provider-backed work, the planning item remains the accepted-goal authority.
The committed execution item carries its Development or Exploration Brief as an
admission snapshot, plus the complete Planning Receipt. Engage re-reads the
provider and uses the existing read-only comparator before new dispatch or state
mutation.

For standalone work, the Captain-approved committed work item is the planning
authority. Its exact committed content and loader SHA bind the revision. It has
no Planning Receipt, does not call a provider reader or comparator, and does not
invent a Cycle or Release/Milestone.

A Planning Receipt is exactly the `source`, `planning-window`, and
`planning-outcome` tuple. Current Ready membership is provider state, not copied
receipt data. A partial tuple is invalid: if any field is present, all three and
the provider route must be resolvable and reconciled. Local `sprint` and
`sprint-readiness` fields remain runtime mechanics and never prove this receipt.

## Shared route for features and bugs

Feature and bug labels do not select a workflow. Uncertainty, risk, urgency, and
the next commitment select the brief and profile:

| Work shape | Input | Typical profile | Planning behavior |
|---|---|---|---|
| Scheduled new feature | Development Brief plus Planning Receipt | Pilot or Production | Cycle and Release/Milestone are reconciled. |
| Scheduled or complex bug | Development Brief plus Planning Receipt | Pilot or Production | Same route; the brief emphasizes observed versus expected behavior and regression evidence. |
| Clear urgent bug | Standalone Development Brief | Proportional Pilot or eligible Production recovery | Captain admission replaces scheduling; verification still applies. |
| Unknown cause or risky premise | Exploration Brief, optionally with a Planning Receipt | POC | Evidence returns to planning before delivery work exists. |

No `feature-flow`, `bug-flow`, `spike-flow`, or work-type discriminator is added.

## Exploration route-back

POC and Spike are both uses of `poc-exploration`:

- a Spike reduces uncertainty about the problem, constraint, or decision;
- a POC proves or falsifies a concrete technical route.

Both end by recording `poc_outcome` with direction, exact evidence, strongest
limit, reversal fact, and cleanup. KC Dev Flow then returns that outcome to the
planning authority and terminalizes the exploration item after Captain approval.
It does not create, preselect, or schedule downstream delivery work. Planning may
stop, request another exploration, or create a new Development Brief.

An exploration may carry a Planning Receipt when it is intentionally time-boxed
inside a Cycle. Its output is decision evidence, not a user-value release.

## Ownership boundary

Planning owns:

- problem discussion and accepted user value;
- Cycle, Release/Milestone, priority, and Ready state when a provider is used;
- accepting an exploration result and deciding whether another work item exists.

KC Dev Flow owns:

- brief admission and profile selection;
- shape, build, and proportional proof;
- refusal when accepted outcome or non-goals must change;
- goal sufficiency, minimum sufficient stack, and without-it evidence.

Runtime adapters own:

- Hermes, Conductor, Spacedock, or manual execution;
- task-to-worktree cardinality, retry, resume, and worker recovery;
- pull-request, merge, release, and publication ceremony.

The portable kernel must not require one Issue, one task, one workspace, a fresh
executor, or any particular downstream engine.

## Smallest PR #306 reshape

Keep:

- the readable Issue body beginning directly with the problem;
- accepted outcome, non-goals, acceptance evidence, and route-back conditions;
- exact scope comparison and structured route-back on a changed premise;
- existing read-only provider reconciliation;
- deterministic contract and minimal-stack mutation coverage.

Remove or narrow:

- one planning item to one Spacedock task;
- one task to one isolated execution context;
- fresh-executor input and worker retry rules;
- universal source, Cycle, and Release/Milestone requirements;
- POC downstream-item creation inside KC Dev Flow.

Add no new plugin, workflow stage, profile, persistent manifest, synchronization
loop, or CI job. Reuse the existing profile receipt, committed work item, engage
comparator, and POC outcome.

## Acceptance criteria

1. Pilot and Production cannot begin without a complete Development Brief.
2. POC cannot begin without its existing four Exploration Brief fields.
3. A complete Planning Receipt invokes read-only reconcile; no receipt invokes no
   provider dependency; a partial receipt stops.
4. Feature and bug work share the same brief-to-profile engine.
5. POC and Spike terminalize with evidence and return to planning without
   creating downstream delivery work.
6. The portable kernel contains no task, workspace, executor, or provider
   cardinality rule.
7. Completion still requires goal sufficiency and minimal necessity for the same
   exact candidate.
8. Mutation tests fail when the required brief, optional standalone path,
   route-back boundary, or runtime-topology deletion is removed.
