---
title: Plan a release from journey-board decisions into a development brief
status: implementation
product: kc-journey-map
source:
planning-window:
planning-outcome:
sprint: S2
sprint-readiness: ready
started: 2026-09-11T05:56:22Z
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
        - id: gate:r1fa7xv14afj9npcfe1wbx76:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:r1fa7xv14afj9npcfe1wbx76-ideation-1
              briefing:
                id: briefing:r1fa7xv14afj9npcfe1wbx76:ideation:attempt-1:revision-1
                digest: sha256:c10d134ec4085883bac62c867008a1581671e07f69fc1be597afdd0cccdadbdf
                room-ref: ./review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:r1fa7xv14afj9npcfe1wbx76:ideation:1
                briefing: briefing:r1fa7xv14afj9npcfe1wbx76:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-11T06:39:55.865713Z"
                decision: approve
                reason: Kent confirmed the presented two-file implementation plan and local commits after reviewing the integrated journey-map to dev-flow usage flow. Preserve the recorded thresholds and deferred delivery authority.
              application:
                target-stage: implementation
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


## Stage Report: ideation

### Implementation route proposed at ideation

One integrated Pilot slice: teach the existing journey entry to prepare one selected release and hand one Development Brief to existing dev-flow shaping. Product edits remain gated. `semantics_unchanged: false`: selected-release questioning and handoff guidance change; command grammar, source schema, progress calculation and admission authority do not.

#### Authority and delivery baseline

The Captain-approved Feedback Cycles take precedence over historical pending-selection/admission prose and the superseded prohibition on extending the predecessor stack. Pilot selection, two independent entrypoints, one Development Brief, the separate layer above PR #417, and S2 registration/use before merge are settled. Accepted outcome, non-goals, receipt and stage pin remain byte-preserved; this plan does not reinterpret their historical text.

Code root is `/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/worktrees/journey-release-planning`, branch `codex/journey-release-planning`, HEAD `36099fab28b9d19f73fc40e9d3e55614202e9b8a`. Delivery base is `36a969a6f890a63c541fad4bfa30071ac7115c64`; live GitHub read confirmed PR #417 OPEN at that exact head on `codex/journey-local-progress`, targeting `codex/journey-release-inspection`. The existing difference is only 13 added roadmap lines. No predecessor mutation, code push, PR creation or merge is part of ideation.

The installed 4.3.0 loader accepted state-owned attempt `ideation-1` with contract digest `cc4915cc2e4d5407d174a5eef77bb64ca078bc098f533e83db00f98785413558`. Only shared core, Pilot base/shape, reverse recovery, retained-document policy and project-context maintenance were loaded. Multi-slice is false: one integrated user journey is sufficient.

#### Journey and failure behavior

1. **DESIGNED — Codex or Claude running the journey entry:** on explicit planning/resume/release preparation, open the named repository journey YAML, take the selected release ID, persona, journey, release goal and recorded decisions as inputs. Inspect an existing relevant board proactively within that request; map-only requests keep their independent intent-only path.
2. **DESIGNED — The same host agent:** inspect selected-release gap/unverified stories and questions in every status, plus dependencies that can affect the selected outcome. Read accessible symbols, source-authored models and existing task observations before proposing value choices. A model authored through an agent may have no standalone handler; unavailable/incomplete Spacedock observation is separate from authored implementation uncertainty. Retain both as unknown unless their own evidence resolves them.
3. **DESIGNED — The host interaction surface:** ask one unresolved value/scope/acceptance decision, with recommendation and effect. Reuse answered, assigned and deferred decisions unless their premises changed. A later-release unknown stays visible without blocking an independent current release. No answer, abandonment or host interruption preserves the unresolved choice; dependent scope is not approved and a draft brief cannot be presented as ready. Resume from the source and recorded answer, not from a restarted interview.
4. **DESIGNED — The host agent edits the existing YAML:** preserve release/story IDs and record the decision beside existing story/release content, using its existing decision container where present or an existing note/rule with the relevant IDs. Add no required decision schema. Use `journey-read` only for supported readback; ambiguous/duplicated/unclaimed edits require disposition before applying. Re-read the source before writeback to avoid overwriting concurrent edits. Function-model edits remain source edits followed by redraw; no direct function-map writeback.
5. **DESIGNED — The host agent produces one Markdown Development Brief:** reuse the five sections owned by `kc-dev-flow/skills/adopt-dev-flow/SKILL.md:73-102`, with ascending AC identifiers. Put source path plus committed revision (or an explicit uncommitted content hash), release/story origins, observed facts, assumptions and technical unknowns inside those sections; create no duplicate template or sixth authority section. Generate the snapshot after decisions are reviewed. Keep the generated release contract as evidence, not as the Development Brief.
6. **OBSERVED, bounded — Python runs the existing consumer format seam:** `validate_admission_brief` accepts the prior actual and hypothetical briefs and refuses a missing Acceptance criteria section. The earlier independent consumer accepted both matched source/brief pairs and rejected a stale pairing. Those observations do not establish native admission or changed-entry behavior.
7. **DESIGNED — An agent running existing dev-flow ideation:** consume the reviewed brief and its evidence, perform technical gap/dependency/without-it work once, and propose the smallest necessary integrated work. Journey-map does not pre-split implementation tasks. Record multi-story/shared origins in task prose; the scalar `journey-story` progress mapping cannot represent shared work truthfully, so omit unsupported progress declarations and preserve unknown progress. Existing profile, admission and implementation gates remain in force; standalone dev takes a valid brief without a board.

Persistence uses the consumer repository's existing journey YAML and one reviewed Markdown snapshot. Git review provides recovery for source edits; retry re-reads identities, the selected revision and the decision disposition rather than duplicating work. Canvas failure returns source plus Markdown and reports unavailable rendering. A planning change after admission produces a new planning delta, never automatic rewrites of running tasks; source provenance stays in body text, not a partial provider Planning Receipt.

#### Where it touches and without-it justification

Paths below are relative to the code root. Counts are measured at `36099fab`; resulting counts are estimates, not pass criteria.

| Path | Lines now | Estimated after | Why retained / what absence would break |
|---|---:|---:|---|
| `kc-journey-map/skills/kc-journey-map/SKILL.md` | 148 | 160–175 | Route explicit selected-release planning to the existing conversation reference, scope evidence checks to that route, and use the available host question surface. Without the entry change, the current map/draw/check routing does not expose selected-release preparation or its handoff. AC-1, AC-2, AC-6. |
| `kc-journey-map/skills/kc-journey-map/references/map-from-conversation.md` | 72 | 125–150 | Retain the four-pass new-map path; add existing-board decision reuse, facts-before-choice, persistence and brief handoff in one explanatory home. Without it, the current reference explicitly forbids code inspection and stops at rendering/readback, with no development-ready release handoff. AC-1–AC-6. |
| `docs/dev/ROADMAP.md` | 478 | 478 | Already committed S2 registration (`36099fab`), +13 versus delivery base; no further edit planned. Without the existing registration, the authorized execution group cannot be used for this task. |

Unchanged dependencies were inspected and are deliberately not changes: `canvas.md` (258 lines), `cell-contract.md`, `lib/read.mjs`, `lib/progress.mjs`, dev-flow `continue-dev-flow/SKILL.md` (266), `adopt-dev-flow/SKILL.md` (268), `profile-contract-loader.py` (1119), and Pilot `shape.md` (89). The four inspected dev-flow intake/shape files are byte-identical to installed 4.3.0; the warning about older source does not describe these measured files. Reuse their five-section admission, profile routing, reverse-recovery and technical-shape contracts. No newer runtime contract import, consumer migration or consumer edit is justified by the observed format seam.

Source inspection is the shape-tier without-it observation, not a changed-entry behavioral ablation. During build, exercise the accepted goal against the unchanged entry/reference as the control and the changed pair as the candidate; name the actual missing behavior. If a retained edit has no distinguishable contribution to the accepted goal or a named boundary, remove it. Do not equate a searched phrase with behavior proof.

Stop and report before continuing if the diff against `36a969a6f890a63c541fad4bfa30071ac7115c64` exceeds **3 changed code-tree files**, **220 added plus deleted lines**, or **160 added plus deleted lines in `map-from-conversation.md`**. These include the existing 13 roadmap additions. Any dev-flow consumer/code/schema/renderer/progress edit is an unplanned surface and returns to shape even below those counts. State report and disposable exercise output are outside the product diff; no retained harness is authorized.

Release compatibility is additive guidance: existing source files, commands, independent map use and valid standalone briefs remain supported. Put that no-migration instruction in the existing reference; use a journey-map-scoped feature commit and the existing release-please component for the eventual version/changelog. Do not hand-bump predecessor versions or add a parallel migration template. Existing release metadata checks remain applicable; publication remains separately authorized.

#### Acceptance checks and decisive falsifiers

All changed-entry checks below are **planned**, not passed. Use the real prior Release 3 source and settled decisions as the bounded starting scenario, then one controlled deferral of `hand-the-order-to-planning`; label the variant hypothetical.

| Criterion | Existing surface and planned check | Falsifier |
|---|---|---|
| AC-1 | Actual host interaction starts from the existing source's persona, journey, r3 goal and format decision, then asks the one remaining material choice with recommendation/effect. | Re-asking a settled answer or issuing a fixed interview fails; a changed premise permits only its affected question. |
| AC-2 | Feed source-authored unverified model stories, an accessible model symbol, an unavailable/partial task observation, a question on an exists story, and assigned/deferred work. Inspect facts before deciding. | Inferring a missing handler/task from either unknown, skipping the exists-story question, or reopening unchanged deferred scope fails. |
| AC-3 | Preserve all existing IDs and nonselected releases; apply one approved source decision, and exercise the existing conflicting-readback refusal. Include a later-release unknown and a current-scope unanswered choice. | Silent ID replacement, ambiguous writeback, blocking only on independent later work, or accepting unanswered current scope fails. |
| AC-4 | Run the existing format consumer on the generated brief; compare bound source revision/release membership and facts. Change the source's handoff membership while retaining the old brief as a negative. | Missing canonical section/AC, conflated assumption, missing provenance, stale scope accepted, or automatic task rewrite fails. Format validation alone does not detect stale source. |
| AC-5 | A real separately observed agent consumes the brief through the existing selected ideation contract and proposes necessary shared/model/handoff work with origins; repeat the controlled deferral. | Repeating value interviews, preselected framework/handler tasks without evidence, duplicated shared work, false scalar story mapping, or changed authority fails. Record exactly which native boundary ran; do not call contract-guided assessment full native admission. |
| AC-6 | Run the existing map-only entry on intent with no code/Spacedock; run dev-flow on a valid standalone brief with no board; exercise a host without a question tool via plain text. | Any mandatory board/provider/evidence demand, absent text fallback, or new standing test framework fails. No tool answer is not scope approval. |

Implementation owns the actual changed-entry session and recorded artifacts; validation owns a fresh brief consumer and final recheck, dispatched through the existing workflow by the First Officer. No child agent, self-roleplayed independent proof or new native work item is authorized by this shape report. A required consumer change discovered by that exercise returns here with its concrete failure instead of silently expanding this two-file route.

Existing checks to reuse are `scripts/skill-frontmatter-lint.sh`, `scripts/version-parity-check.sh`, and the journey `read.test.mjs`, `release-contract.test.mjs`, `progress.test.mjs` checks relevant to the claimed unchanged seams. Use the declared `npm ci` prerequisites when those suites/CLI need dependencies; do not report core tests as CLI or rendered proof. No CI change or trigger is proposed; cost per PR is unmeasured. No speed comparison was performed.

#### Bounded audit receipts

```yaml
reverse_recovery:
  trigger: selected-release planning and brief handoff in an existing skill
  boundary: journey entry/conversation/canvas/cell contract and dev-flow intake/shape/loader; existing libs; external or historical planning packages excluded
  layers:
    - {surface: entry and conversation handoff, location: 'kc-journey-map/skills/kc-journey-map/{SKILL.md,references/map-from-conversation.md}', completeness: EXISTS_BROKEN, need: REQUIRED, evidence: 'current map route forbids factual inspection and ends at board readback; AC-1 through AC-6 need selected-release preparation', disproof_hook: 'unchanged-entry exercise produces the faithful brief without extra task-specific coaching'}
    - {surface: selected-release evidence contract, location: kc-journey-map/lib/release-contract.mjs, completeness: WORKING_UNIT_UNPROVEN, need: REQUIRED, evidence: '4 existing tests passed including unknown-release refusal and three statuses; no CLI/render claim', disproof_hook: 'another release leaks into rows or unknown becomes gap'}
    - {surface: canvas persistence and task observation, location: 'kc-journey-map/lib/{read,progress}.mjs', completeness: WORKING_UNIT_UNPROVEN, need: REQUIRED, evidence: 'prior bounded core proof and existing refusal tests; complete changed-entry wiring unproven', disproof_hook: 'fresh readback/conflicting-ID and partial-observation tests fail'}
    - {surface: brief intake and technical shaping, location: 'kc-dev-flow/{skills/continue-dev-flow/SKILL.md,scripts/profile-contract-loader.py,references/profiles/pilot-product-slice/shape.md}', completeness: WORKING_UNIT_UNPROVEN, need: REQUIRED, evidence: 'live format positive/negative probe; earlier independent paired consumer; native changed-entry ideation unproven', disproof_hook: 'actual consumer needs repeated value decisions or incompatible format'}
  decision: recover the two existing journey guidance surfaces; reuse consumer and persistence
project_context:
  impact: none
  authority: 'Local Profile root PRODUCT.md, ARCHITECTURE.md and CLAUDE.md'
  claim_locator: 'PRODUCT.md Repository plugin catalog / kc-dev-flow; ARCHITECTURE.md kc-dev-flow profile-native loading'
  surface: independent plugin boundaries and five-section standalone admission
  stale_claim: none
  approved_change: none
  landed_change: none
  planned_check: compare delivered entry behavior with independent map/dev use and unchanged authority/loading claims; return newly affected claims to shape
  validation_evidence: pending
```

The audit used file enumeration plus scoped content/entry-path tracing; it claims a broken integration boundary, not universal absence of a capability. Root catalog counts and unrelated reviewer prose were already stale in the base and are not caused or repaired by this slice. Retained-document policy applies to the two existing skill documents under repair-in-place: entry routing points to one detailed reference, the brief section schema remains owned by dev-flow, and the source/board boundary stays owned by canvas/cell contracts. No retained document is added or removed.


- DONE: Define one faithful selected-release planning-to-development journey, preserve settled decisions and unknown evidence, and assign every AC a falsifier.
  AC-1, AC-2, AC-3, AC-4, AC-5, AC-6: the journey and falsifier table above bind one release, existing identities, facts-before-choice, deferred scope, stale snapshots and independent entrypoints; changed-entry proof remains planned.
- DONE: Justify the smallest file-level change against PR #417 with measured current lines, estimated resulting lines, without-it reasoning, and explicit stop thresholds.
  Two guidance edits (148 and 72 current lines), plus the already committed 13-line roadmap registration; stop above 3 files / 220 changed lines / 160 conversation-reference changed lines against exact base `36a969a6`.
- DONE: Identify and exercise the existing brief consumer seam as far as shaping requires, reuse prior bounded evidence honestly, and return one reviewable implementation route without product edits.
  AC-4, AC-5, AC-6: candidate `validate_admission_brief` refused a removed Acceptance criteria heading, then accepted both prior briefs with digests `2184f8e1` and `371833cc`; measured intake/adopt/loader/shape bytes equal installed 4.3.0, so no consumer edit is justified.
- DONE: Preserve the accepted planning delta and the pinned authority.
  The Feedback Cycles supersede historical pending prose and the no-stack restriction; Pilot/S2/pre-merge use are approved, while the accepted brief, receipt and `ideation-1` pin remain unchanged.
- DONE: Exercise the unchanged selected-release evidence core at the shaping boundary.
  AC-2, AC-3, AC-4: `node --test kc-journey-map/lib/release-contract.test.mjs` passed 4 tests; unknown release is refused, other-release stories excluded, and gap/unverified remain distinct. Leaking membership or collapsing statuses would fail these checks.
- SKIPPED: Product implementation, changed-entry interaction, native admission/ideation, rendered canvas and comparative speed proof.
  These are outside ideation or belong to later authorized exercises; prior `consumer-result.md` is bounded independent assessment and prior CLI lint failed for missing `yaml`, neither is relabeled as native or visual proof.

### Summary

Recommend one two-file journey guidance change above PR #417, reusing the existing Development Brief consumer with no dev-flow code or contract change. The plan records the approved delta, all six falsifiers, measured stop numbers, recovery boundaries and the remaining real interaction/consumer proof; implementation awaits the ideation gate.


## Stage Report: implementation

- DONE: Implement only the two approved existing journey guidance edits; preserve independent map/dev use and all six accepted criteria within the recorded stop thresholds.
  AC-1–AC-6: local commit `74fe23086e4e34c5e288c46a43c6d559bd89ebf2` adds selected-release routing and one conversation-reference procedure; no consumer/schema/renderer/progress changes. Against `36a969a6f890a63c541fad4bfa30071ac7115c64`: 3 files / 114 added+deleted lines, including prior ROADMAP +13; conversation reference 87 changed lines. Product branch remains `codex/journey-release-planning`.
- DONE: Demonstrate changed-entry behavior and meaningful without-it evidence through actual bounded agent execution plus existing mechanical checks; preserve unknowns, provenance, and authority.
  AC-1, AC-2, AC-4: separate FO-dispatched Codex control/candidate actors used the same real r3 input. Both reused settled answers; control drafted a brief but read no implementation and failed installed admission formatting. Candidate inspected model/render facts, retained six story IDs plus source SHA-256, separated historical/current refs and both unknown classes, and passed `validate_admission_brief` at digest `db8ca25350ffff2fab4f9ce69ca07e82b109b64ec5e247b40f98ed1298e13c59`. This proves bounded instructed behavior, not installed discovery or native admission.
  AC-3, AC-6: same frozen actor found a new hypothetical acceptance-audience question on an exists story, asked one recommended plain-text choice, and kept dependent acceptance/brief draft with no answer. An independent coffee-shop intent input produced a source draft across three activities with online preorder deferred and no implementation status/evidence. Supplementary source hash `c4be5510b7146ff93dc1a3bb6ed1702f261ef7f3d57666b8cc35c8209d17ad20`; no fixture answer grants live scope.
  AC-2, AC-3, AC-4: 38 existing read/release-contract/progress tests pass; conflicting/stale/duplicated readback refuses writes, unknown releases refuse output, and incomplete task observations cannot complete. Collapsing unknowns or leaking identities/membership would fail those tests. Declared `npm ci --ignore-scripts` restored missing yaml; no dependency file changed.
  AC-4: existing CLI journey lint now refuses removed evidence (`exists-without-evidence`) then accepts unchanged r3 source. This is new CLI evidence, not a relabeling of the prior missing-yaml failure; no rendered canvas was inspected.
- DONE: Commit only approved files locally, run the required proportional exit observation and comment/minimality pass, and record exact-candidate evidence with honest limits for fresh validation.
  Frontmatter and version parity pass; the frontmatter checker first rejected a missing description. Empty surface mapping rejected all 3 files, then `surface-map-check.py` accepted the evidence mapping. Removing ROADMAP registration produced `sprint_unregistered`; the candidate registration passed. `git diff --check` is clean. No CI change; CI cost per PR remains unmeasured.
  Comment/minimality pass cut the draft rendering-selection change because existing rendering behavior is independent and question fallback belongs in the conversation reference. Retained discovery, facts-before-choice, decision persistence, brief provenance and authority paragraphs map to AC-1–AC-6; canonical schema and canvas rules retain their existing owners. No retained tests, dependency, abstraction or duplicate template was added.
  Typed RoboRev observation is `UNKNOWN(reason: stale)`: job 488 / UUID `5fb5ce1a-764f-4c7f-a402-37ccd2b9f1ac` completed with `SEVERITY_THRESHOLD_MET`, but JSON omits required config/profile/version/cap/panel-population binding. Fixed codex / gpt-5.6-terra / medium / minimum medium / panel none; 900-second cap, 1 request, 0 confirmations. Config SHA-256 `ae3555f0b3fcf5b626c39c614e3b2058bd2e31fb5840ce864edfaeded34f07f1`; approximate cost $0.0379616, coverage 1/1 complete. No provider verdict substitutes for validation.
- SKIPPED: Fresh brief-to-ideation consumer, standalone dev behavior confirmation, native admission, rendered/installed interaction UI, and delivery acceptance.
  AC-5 and final AC-6 consumer proof belong to the separately dispatched validation worker in the approved plan. Actual host was Codex; plain-text fallback was exercised. Prior hypothetical-deferral consumer evidence remains historical, not exact-candidate proof. No push/PR/merge or speed claim is authorized by these observations.

### Summary

Implemented one two-file release-preparation route and committed it locally at `74fe2308`, with passing proportional checks and a concrete unchanged/candidate admission contrast. Forward this exact candidate and actor artifacts to fresh validation for the actual ideation consumer and remaining acceptance checks; scope and delivery authorization remain unchanged.

#### Evidence locations and context

Product-local mechanical logs, the three-file SURFACE mapping, observation input/result and comment pass: `.context/implementation-proof/` under the assigned code worktree. FO actor artifacts: `/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/journey-release-planning-dispatch/{control-result,candidate-result}/`; the source and brief fingerprints bind the exact frozen candidate. These are task-owned disposable artifacts, not a standing harness.
Project-context impact remains `none`: PRODUCT.md's dev-flow catalog and ARCHITECTURE.md's profile-native admission/loading retain their existing standalone brief and authority claims; fresh validation still owes its receipt confirmation. The accepted body, receipt, implementation-1 pin, gates and reviewed Briefings were preserved; installed 4.3.0 loader readback accepted the report-only state change.

#### Exit observation claim

```yaml
review_convergence_claim:
  identity: 08da679c6737e704bcd967ca24161e4979a77f74359a11adb2c3974e0e380f36
  claimant: codex-implementation-1-74fe2308
  observed_state_revision: bfd2653e37377b268c06bda485d7de795df58851
  state: claimed
```
