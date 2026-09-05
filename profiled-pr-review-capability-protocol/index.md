---
title: "Pilot a profiled PR review capability protocol"
status: ideation
source:
product: kc-pr-flow
planning-window:
planning-outcome:
sprint: kc-pr-review/profiled-capability-pilot
sprint-readiness: ready
started: 2026-09-04T18:58:31Z
completed:
verdict:
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/kc-pr-review-capability-pilot
issue:
pr:
mod-block:
id: t8cyxd55ve3dtcxb9r37z2a7
gates:
    version: 1
    records:
        - id: gate:t8cyxd55ve3dtcxb9r37z2a7:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:t8cyxd55ve3dtcxb9r37z2a7-backlog-1
              briefing:
                id: briefing:t8cyxd55ve3dtcxb9r37z2a7:backlog:attempt-1:revision-1
                digest: sha256:cc8f490db41b19620dc468c5eb42b6441fa863edc2ce700e273c7f4e21fe4b47
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:t8cyxd55ve3dtcxb9r37z2a7:backlog:1
                briefing: briefing:t8cyxd55ve3dtcxb9r37z2a7:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-04T18:55:49.333513Z"
                decision: approve
                reason: Captain approved the recommended Pilot route after the V1 protocol passed fresh Claude Opus 5 xhigh review; admission changes no posting, merge, release, or paid-run authority.
                conn:
                    quote: 批准
                    source: Captain chat, this conversation, 2026-09-05, approving kc-dev-flow Pilot progression
              application:
                target-stage: ideation
                state: consumed
        - id: gate:t8cyxd55ve3dtcxb9r37z2a7:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:t8cyxd55ve3dtcxb9r37z2a7-ideation-1
              briefing:
                id: briefing:t8cyxd55ve3dtcxb9r37z2a7:ideation:attempt-1:revision-1
                digest: sha256:6e214e25449a4c4cdaa14964bed82dd0972daeeec250c704d6801e3d172fa529
                room-ref: ./review/ideation/briefing-1
---

## The problem

The current `kc-pr-review` path pays for broad review work before it knows which review questions a pull request actually needs. The default-off delta fast path in Draft PRs #352-#355 has not established the accepted 33.3% real review-time reduction, and acquiring a full evidence catalog before routing can erase the intended saving. Review dimensions, evidence collection, synthesis, and posting authority are also coupled closely enough that adding or removing one review concern is difficult to measure independently.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: A default-off Lite path will serve bounded real PR reviews and create persistent protocol value without changing production defaults, posting authority, or release ownership.
  route: [shape, build, verify-deliver]
  obligations:
    architecture: [Freeze provider-neutral JSON Schema contracts; separate deterministic planning and evidence from capability execution and final synthesis; keep required coverage fail-closed]
    implementation: [Implement only the default-off Lite path and its fixtures; reuse existing exact-head confirmation and posting boundaries; keep Standard Full and Custom as documented protocol profiles]
    testing: [Validate every schema and state transition; mutate required coverage and identity inputs; run a sealed blind control-treatment evaluation before any promotion]
  scope_boundary: No production default, Custom UI, Nightwatch or Forge integration, real posting change, merge, release, or claim of speed improvement without accepted blind evidence.
  promote_when: [A later scope enables the path by default; adds real posting authority; implements Custom UI; creates long-term operational or compatibility commitments]
  decision:
    authority: captain:kent
    at: 2026-09-04T18:51:18Z
```

## Accepted outcome

Define the complete V1 protocol for Lite, Standard, Full, and Custom selection, then implement one default-off Lite end-to-end path. A deterministic planner consumes exact-head PR shape and mechanically acquired evidence, selects typed review capabilities, and may make one bounded add-only expansion. Independent capability calls return closed schema results. A General Reviewer host consumes only the accepted evidence and capability results, resolves every required review question exactly once, and projects the existing user-facing review and confirmation shape without gaining posting, merge, or release authority.

The Pilot is successful only if a sealed blind comparison against the current full review preserves the accepted quality floor and reduces median review-to-confirmation-ready wall time by at least 33.3%, including evidence acquisition, planning, capability execution, and synthesis. Human waiting and actual GitHub posting are excluded from both arms.

## Non-goals

- Do not enable the new path by default or merge, close, rewrite, or promote Draft PRs #352-#355.
- Do not implement Standard, Full, or Custom UI execution in this slice; define their V1 contracts only.
- Do not change the existing human confirmation, GitHub posting, merge, release, or versioning authorities.
- Do not integrate Nightwatch or `kc-plugin-forge` in this slice.
- Do not perform live browser or runtime probing, performance or resource-exhaustion review, or cross-run duplicate suppression in V1.
- Do not acquire evidence for unselected capabilities unless the bounded expansion reserve explicitly activates them.
- Do not claim a general quality or speed improvement from synthetic fixtures, structural timings, or fewer than five valid real PR pairs.
- Do not launch paid model runs until a measured per-run pilot cost and an explicit experiment budget are recorded.

## Acceptance criteria

- **AC-1** One versioned protocol document names the Planner, Evidence Builder, capability plugins, General Reviewer host, confirmation projection, and posting adapter; it assigns exactly one authority owner to every lifecycle decision and records Lite, Standard, Full, and Custom selection semantics.
- **AC-2** Versioned JSON Schemas are the source of truth for plugin metadata, planner input and output, evidence bundles, capability requests and results, review decisions, confirmation projections, and posting outcomes; closed fixtures prove valid examples and reject unknown fields, missing identity, malformed evidence, and unsupported versions.
- **AC-3** The Lite planner is deterministic for the same exact-head input, freezes a question bank and requiredness before dispatch, activates only profile-required or signal-required capabilities, and permits at most one add-only expansion whose requested questions and evidence are explicitly budgeted.
- **AC-4** Mechanical checks and repository facts are acquired once by the Evidence Builder and content-bound to the exact base and head. A capability cannot fetch undeclared evidence or treat missing evidence as a clean result.
- **AC-5** Each capability is invokable through a provider-neutral typed contract, sees only its declared input, and returns one terminal result for each assigned question. A missing, invalid, stale, timed-out, or contradictory required result remains visible and prevents approval.
- **AC-6** The General Reviewer host resolves each required question exactly once from accepted typed inputs, preserves blockers and unresolved coverage, cannot silently suppress a known problem, and cannot turn model silence into positive evidence.
- **AC-7** The Lite path projects the current review summary, finding, recommendation, confirmation, and event vocabulary without changing actual GitHub posting. Default-off and rollback fixtures reproduce the existing route.
- **AC-8** A sealed blind evaluation uses at least five real ordinary PR control-treatment pairs with the same model family, reasoning level, harness conditions, and exact PR inputs. Independent adjudication freezes accepted findings and severities before timing is opened.
- **AC-9** Promotion evidence requires zero treatment misses among accepted Critical or High findings found by the control, aggregate treatment false positives no greater than control, complete required coverage, median review-to-confirmation-ready time at least 33.3% lower than control, and at least three of five pairs individually clearing 33.3%.
- **AC-10** Every invalid identity, required-coverage gap, exhausted expansion, schema failure, stale head, or incomplete run has a closed terminal state and cannot post, approve, or be counted as a passing timing sample.

## Route-back conditions

Stop and return a structured planning delta before implementation if correctness requires full-catalog evidence acquisition before planning, more than one expansion, a new GitHub posting owner, a new CI workflow, a compatibility action by existing adopters, persistent cross-run state, live runtime or browser probing, or implementation of Standard, Full, or Custom UI. Stop before paid evaluation if its measured cost or frozen corpus differs from the separately approved budget and experiment record.

## Measurement

Primary measure: exact-head review-to-confirmation-ready wall time, with evidence acquisition charged to the arm that uses it. Quality is frozen before timing. Record per pair: PR identity and shape, selected questions and capabilities, evidence bytes, capability terminals, accepted findings by severity, false positives, model and harness identity, tokens, retries, wall time, and human intervention. Structural fixtures validate the protocol but cannot promote it.

## Stage Report: ideation

- DONE: Freeze one implementation-ready protocol shape at the pinned delivery base.
  Design: `docs/superpowers/specs/2026-09-05-kc-pr-review-capability-protocol-v1.md`.
  Feature commit: `41186709` on `feature/kc-pr-review-capability-protocol-pilot`.
  Delivery base remains `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`.
- DONE: Define Lite, Standard, Full, and Custom contracts while keeping execution Lite-only.
  The executable path is default-off and requires exact typed/profiled `on` switches.
  Standard, Full, and Custom remain documented contracts and route-back conditions.
- DONE: Separate Planner, Evidence Builder, typed capabilities, and General Reviewer authority.
  JSON Schema owns object shape; one catalog owns requiredness, signals, and manifests.
  `InteractiveCollationDecision/v1` remains the sole approval authority.
  Existing confirmation and `review-post.sh` posting ownership remain unchanged.
- DONE: Close required coverage, evidence, identity, receipt, and terminal behavior.
  Missing required evidence is fail-closed and cannot become a clean answer.
  Zero-attempt skips emit no runtime lane, preserving the existing attempt/lane bijection.
  All-skipped zero-lane review ends `ABORTED_INCOMPLETE: receipt_incomplete`.
- DONE: Recover the existing `review-ablation` harness instead of creating a second runner.
  The design adds only whole-tree Pilot arms and a bounded Pilot comparator.
  Five effective primary slots, quality-first blind adjudication, and exact-head provenance are fixed.
  Control is the current legacy route; treatment is the combined typed plus profiled route.
- DONE: Complete independent architecture review through fresh Claude Opus 5 xhigh passes.
  Thirty fresh review rounds were run; every blocking and optional issue was resolved or disproved by base evidence.
  Final round verdict: PASS with no optional refinements.
- VERIFIED: Pinned-base mechanical checks remain green.
  `review-runtime.test.sh`: 372 passed, 0 failed.
  `review-post.test.sh`: 156 passed, 0 failed.
  `review-ablation.test.sh`: 82 passed, 0 failed with the repository venv active.
- DELTA FOR CAPTAIN: Executable Lite expansion reserve is exactly zero.
  Any `ExpansionRequest/v1` ends `ABORTED_INCOMPLETE: unsupported_expansion`.
  The add-only expansion contract remains documented for a later accepted route only.
  This narrows the Brief's executable bounded-expansion wording and requires ideation-gate acceptance.
- PROJECT CONTEXT RECEIPT: PRODUCT and ARCHITECTURE headings are exact and overlap-checked.
  The shape retains runtime event-envelope and approval authority claims while adding the external Planner.
  No new posting owner, CI workflow, persistent service, Nightwatch, or Forge integration is introduced.
- LIMITATION: No protocol implementation or blind treatment run exists yet.
  Hosted CI cost per PR is unmeasured, so no CI cost or 33.3% speed claim is authorized.
  Paid admission and experiment calls remain behind a separate measured budget approval.

### Ideation summary

The smallest integrated route is ready for a Captain gate: 18 estimated changed files, about 4,010
changed lines against a 4,100 stop, and 1,700 focused schema/catalog/fixture/test lines against a
1,800 stop. Build must stop on threshold breach or any need for executable expansion, broader
profiles, new CI/posting ownership, or pre-plan full-catalog evidence.
