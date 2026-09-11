---
title: Plan a release from journey-board decisions into a development brief
status: ideation
product: kc-journey-map
source:
planning-window:
planning-outcome:
sprint: S2
sprint-readiness: ready
started:
completed:
verdict:
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/worktrees/journey-release-planning
issue:
pr:
mod-block:
id: r1fa7xv14afj9npcfe1wbx76
gates:
    version: 1
    records:
        - id: gate:r1fa7xv14afj9npcfe1wbx76:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:r1fa7xv14afj9npcfe1wbx76-backlog-1
              briefing:
                id: briefing:r1fa7xv14afj9npcfe1wbx76:backlog:attempt-1:revision-1
                digest: sha256:2efc26b48657bc9d6f797d1af2109ce21a61f6ea776ebd70ed9d91b803362527
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:r1fa7xv14afj9npcfe1wbx76:backlog:1
                briefing: briefing:r1fa7xv14afj9npcfe1wbx76:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-11T05:55:37.104718Z"
                decision: approve
                reason: Kent explicitly selected Pilot, approved the separate layer above PR 417, and replied 可以 to S2 registration and using it before merge to start this task. Enter ideation only; implementation remains gated.
              application:
                target-stage: ideation
                state: consumed
---

## The problem

The journey tool can express release slices and show development observations, but does not yet turn an existing board into focused value questions and a development-ready handoff. Repeating plan-value's questionnaire ignores prior decisions; treating every unverified story as missing implementation invents work. Running plan-detail and dev-flow ideation separately repeats technical planning.

## Accepted outcome

A planner selects one release slice, receives only the unresolved questions that affect its user value, and obtains one reviewed Development Brief that dev-flow can consume. Journey-map owns value planning; dev-flow owns technical shaping, implementation and verification. One release delivery scope serves one explicit journey value. The board remains a view of planning intent and recorded development facts, not an acceptance authority.

Kent confirmed the two-entry architecture, proactive board awareness, facts-before-choices questioning and this scope-preparation step in the current conversation. This seed captures that approved direction; profile selection and formal admission remain pending.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: >-
    Kent selected Pilot for retained, limited real use of adaptive release
    planning in the existing journey skill and a Development Brief handoff to
    existing dev-flow shaping. Existing consumers need no migration.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Keep journey-map value planning and dev-flow technical shaping independently usable.
      - Reuse the existing brief format and source identities without a second planning authority.
      - Pin the smallest change surfaces and resolve the open-stack dependency before implementation.
    implementation:
      - Integrate only necessary selected-release questioning and handoff guidance in existing skills.
      - Preserve map-only use, unknown evidence, deferred choices, and current admission authority.
    testing:
      - Exercise the changed entry with known answers, unknown evidence, and one actual development consumer.
      - Use a changed-source and stale-brief contrast to falsify an inconsistent handoff.
      - Run only existing checks relevant to the exact changed surfaces; add no standing harness or CI lane.
  scope_boundary: >-
    The accepted outcome and complete non-goal list in this task remain unchanged.
    Excludes provider retirement, global sprint renaming, canvas writeback,
    command retirement, automatic task admission, and consumer migration.
  semantics_unchanged: false
  promote_when:
    - A required consumer migration, destructive external mutation, or long-term operational commitment enters scope.
  decision:
    authority: 'Captain Kent; explicit "Pilot" in this session'
    at: '2026-09-11T05:44:44Z'
```

Selection is recorded; formal admission is still pending. The successful
Release 3 source-to-brief exercise informs shaping but grants neither delivery
acceptance nor authority to extend the predecessor stack.

## Non-goals

- Do not add a planning Spacedock workflow, another tracker, progress cache, polling daemon or background board monitor.
- Do not reinterpret task completion as verified journey usability, change the three-color calculator, or give the renderer E2E classification rules.
- Do not mechanically turn every story or non-green card into a task, reopen settled choices without changed premises, or require evidence for pure intent mapping.
- Do not import PR392 wholesale, retire its commands, or require migration of existing journey files and consumers.
- Do not perform the separate repository-wide sprint-to-release migration or provider retirement. This route uses existing local standalone admission without requiring Linear.
- Do not build a generic task projector, auto-admission path, new approval system, standing review harness or CI lane.
- Do not extend the predecessor three-PR stack; re-read its delivery/base state before starting this independent change.

## Acceptance criteria

- **AC-1** Given an existing board with an agreed persona, journey, release goal and prior decisions, the agent reuses those answers and asks only a missing value/scope/acceptance decision, one at a time, with a recommendation and its effect. It does not run a fixed six-question interview again.
- **AC-2** On an explicit planning/resume or selected-release preparation request, the agent examines relevant unverified/gap stories and unresolved questions in any status. It distinguishes authored evidence uncertainty from unavailable or incomplete SD observation, investigates accessible facts first, preserves unknowns, and does not invent development work from missing evidence. Already assigned or deliberately deferred work does not trigger the same question again unless its premise changes.
- **AC-3** User decisions retain stable story/release identity and reuse existing journey content and supported safe canvas readback. Ambiguous canvas edits are surfaced rather than silently applied. Later-release uncertainty does not block an independent current release; unresolved decisions that change the current accepted outcome, scope or acceptance cannot be silently treated as approved.
- **AC-4** The selected release produces one Development Brief using the existing admission sections: problem, accepted outcome, non-goals, acceptance criteria and route-back conditions. It cites the journey source revision and release/story identities, separates observations from assumptions and names unresolved technical questions. The brief is an admission snapshot, not another live planning database; a later planning change does not rewrite running tasks automatically.
- **AC-5** The existing dev-flow ideation consumes that brief and prior factual evidence, performs plan-detail's technical gap/dependency/without-it work once, and proposes only necessary tasks with traceable release/story origins. Shared or integration work is not duplicated or forced into a false one-story mapping for progress counts. Existing profile/admission/implementation authority still applies; no task execution or gate approval follows merely from drawing a card.
- **AC-6** Existing map-only use remains independently usable without SD or code evidence, and standalone dev-flow accepts a valid brief without requiring a board. Questioning uses the host's available interaction surface with a clear text fallback. The focused evidence demonstrates known-answer reuse, gap-versus-unknown handling and an actual brief-to-ideation handoff; no new standing test framework is introduced.

## Proposed change surfaces

- kc-journey-map entry and conversation-planning reference: integrate selected-release awareness and adaptive plan-value questions into the existing interaction.
- One canonical handoff description or existing template location, chosen during shaping: reuse the current Development Brief format and identify its actual dev-flow consumer before adding fields.
- kc-dev-flow's existing intake/shape references: consume the handoff and retain one technical-planning owner instead of an independent plan-detail flow.
- Existing focused validation/examples and normal release metadata only as required by actual changes. Pin the exact file list and stop thresholds during shaping; this is not approval for a schema or framework expansion.

## Acceptance evidence

Use one real selected-release planning session to exercise the closed loop: reuse an answered value question; investigate an unverified observation; ask one remaining scope choice; retain that decision; prepare the brief; and let existing ideation consume it without repeating the questionnaire or manufacturing tasks. Existing mechanisms or bounded contrasting inputs must distinguish the failure cases. Keep prior rendering/progress proof only where unchanged behavior supports reuse. CI cost per PR is unmeasured; no new CI trigger is proposed.

## Route-back conditions

Stop and return the changed premise, affected acceptance evidence and recommended change or stop if the accepted outcome or non-goals change. Also return for an unavoidable consumer migration, a new authoritative planning store, automatic status/task writes, or a technical fact that changes the selected release value. Current task mapping cannot be assumed to support shared/integration tasks; shaping must state the bounded handling without broadening the progress feature silently.

### Feedback Cycles

#### Captain-approved planning delta — 2026-09-11

- Changed premise: predecessor PRs #415, #416, and #417 are still open. This
  work depends on their journey-map source, so a trunk-based independent
  implementation would repeat their unmerged work.
- Captain decision: Kent replied "可以" to allowing a separate new layer based
  on #417. This explicitly supersedes only the non-goal forbidding extension of
  the predecessor stack. The existing three PRs remain unchanged.
- Accepted replacement boundary: prepare the new work on a separate branch
  based on `codex/journey-local-progress` at
  `36a969a6f890a63c541fad4bfa30071ac7115c64`; any later PR targets that dependency
  branch while it remains open. Push, PR creation, and merge keep their existing
  authorization boundaries. All other accepted outcomes and non-goals remain.
- Affected evidence: shape and without-it measurements must use this exact
  delivery base, excluding predecessor changes. The minimum file table must
  justify any development-consumer change before including it.
- Remaining admission prerequisite: the active definition checkout has no
  `kc-journey-map` execution-group registration. The dependency branch registers
  only S1, for inspecting release evidence, with pre-merge authority scoped to
  the older board task. This new release needs its own local registration; do
  not borrow S1 or claim its existing grant covers this task.

#### Captain-approved release registration and start — 2026-09-11

Kent replied "可以" to direct FO registration of `kc-journey-map/S2` in the
new branch's `docs/dev/ROADMAP.md` and use of that registration before merge to
start this task. Registration commit: `36099fab`, branch
`codex/journey-release-planning`. The bound context validator passed with no
findings against that branch's marketplace and roadmap. S2 names the new
release value, not a time cycle. This resolves the admission prerequisite above.

The earlier pending-selection prose is historical: Pilot is selected and the
Captain has authorized this task's start. The accepted stack delta above is
part of the admission scope; the shape worker must consolidate these explicitly
approved decisions in the task before presenting the implementation plan.
