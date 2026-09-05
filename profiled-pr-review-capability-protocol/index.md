---
title: "Pilot a profiled PR review capability protocol"
status: implementation
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
              resolution:
                type: Resolution
                id: resolution:spacedock:t8cyxd55ve3dtcxb9r37z2a7:ideation:1
                briefing: briefing:t8cyxd55ve3dtcxb9r37z2a7:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-05T02:07:00.346029Z"
                decision: approve
                reason: Captain chat 核准 on 2026-09-05 accepts the presented default-off Lite build, zero executable expansion reserve, and stop limits of 20 changed files / 4100 total changed lines / 1800 focused schema-catalog-fixture-test lines. Paid blind runs require a separately measured budget. Preserve pinned delivery base and existing Draft PRs 352-355.
              application:
                target-stage: implementation
                state: consumed
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

Define the complete V1 protocol for Lite, Standard, Full, and Custom selection, then implement one default-off Lite end-to-end path. A deterministic planner consumes exact-head PR shape and mechanically acquired evidence and selects typed review capabilities. Executable Lite has zero expansion reserve: every ExpansionRequest ends ABORTED_INCOMPLETE with reason unsupported_expansion; bounded add-only expansion is a documented forward contract only. Independent capability calls return closed schema results. A General Reviewer host consumes only the accepted evidence and capability results, resolves every required review question exactly once, and projects the existing user-facing review and confirmation shape without gaining posting, merge, or release authority.

This narrowing is accepted by consumed ideation resolution `resolution:spacedock:t8cyxd55ve3dtcxb9r37z2a7:ideation:1` (Captain's 核准, 2026-09-05). It changes executable expansion only; historical ideation reports remain unchanged.

The Pilot is successful only if a sealed blind comparison against the current full review preserves the accepted quality floor and reduces median review-to-confirmation-ready wall time by at least 33.3%, including evidence acquisition, planning, capability execution, and synthesis. Human waiting and actual GitHub posting are excluded from both arms.

## Non-goals

- Do not enable the new path by default or merge, close, rewrite, or promote Draft PRs #352-#355.
- Do not implement Standard, Full, or Custom UI execution in this slice; define their V1 contracts only.
- Do not change the existing human confirmation, GitHub posting, merge, release, or versioning authorities.
- Do not integrate Nightwatch or `kc-plugin-forge` in this slice.
- Do not perform live browser or runtime probing, performance or resource-exhaustion review, or cross-run duplicate suppression in V1.
- Do not acquire evidence for unselected capabilities or execute any expansion.
- Do not claim a general quality or speed improvement from synthetic fixtures, structural timings, or fewer than five valid real PR pairs.
- Do not launch paid model runs until a measured per-run pilot cost and an explicit experiment budget are recorded.

## Acceptance criteria

- **AC-1** One versioned protocol document names the Planner, Evidence Builder, capability plugins, General Reviewer host, confirmation projection, and posting adapter; it assigns exactly one authority owner to every lifecycle decision and records Lite, Standard, Full, and Custom selection semantics.
- **AC-2** Versioned JSON Schemas are the source of truth for plugin metadata, planner input and output, evidence bundles, capability requests and results, review decisions, confirmation projections, and posting outcomes; closed fixtures prove valid examples and reject unknown fields, missing identity, malformed evidence, and unsupported versions.
- **AC-3** The Lite planner is deterministic for the same exact-head input, freezes a question bank and requiredness before dispatch, activates only profile-required or signal-required capabilities, and fixes executable expansion reserve at zero. Every ExpansionRequest ends ABORTED_INCOMPLETE with reason unsupported_expansion; the bounded add-only expansion contract is documented only.
- **AC-4** Mechanical checks and repository facts are acquired once by the Evidence Builder and content-bound to the exact base and head. A capability cannot fetch undeclared evidence or treat missing evidence as a clean result.
- **AC-5** Each capability is invokable through a provider-neutral typed contract, sees only its declared input, and returns one terminal result for each assigned question. A missing, invalid, stale, timed-out, or contradictory required result remains visible and prevents approval.
- **AC-6** The General Reviewer host resolves each required question exactly once from accepted typed inputs, preserves blockers and unresolved coverage, cannot silently suppress a known problem, and cannot turn model silence into positive evidence.
- **AC-7** The Lite path projects the current review summary, finding, recommendation, confirmation, and event vocabulary without changing actual GitHub posting. Default-off and rollback fixtures reproduce the existing route.
- **AC-8** A sealed blind evaluation uses at least five real ordinary PR control-treatment pairs with the same model family, reasoning level, harness conditions, and exact PR inputs. Independent adjudication freezes accepted findings and severities before timing is opened.
- **AC-9** Promotion evidence requires zero treatment misses among accepted Critical or High findings found by the control, aggregate treatment false positives no greater than control, complete required coverage, median review-to-confirmation-ready time at least 33.3% lower than control, and at least three of five pairs individually clearing 33.3%.
- **AC-10** Every invalid identity, required-coverage gap, exhausted expansion, schema failure, stale head, or incomplete run has a closed terminal state and cannot post, approve, or be counted as a passing timing sample.

## Route-back conditions

Stop and return a structured planning delta before implementation if correctness requires full-catalog evidence acquisition before planning, any executable expansion, a new GitHub posting owner, a new CI workflow, a compatibility action by existing adopters, persistent cross-run state, live runtime or browser probing, or implementation of Standard, Full, or Custom UI. Stop before paid evaluation if its measured cost or frozen corpus differs from the separately approved budget and experiment record.

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

## Stage Report: implementation

- FAILED: Implement the approved default-off Lite journey through existing runtime and posting seams, with closed schemas, deterministic selected evidence, required coverage, and zero executable expansion.
  Partial working diff exercises clean selected evidence through existing start/project/replay/rehydrate; the integrated feature is incomplete and not a delivery candidate.
- FAILED: Demonstrate meaningful positive, refusal, mutation, rollback and integration tests; map AC-1 through AC-10 honestly and leave paid blind outcomes unclaimed.
  Clean-path proof exists; required negative, retry/fallback, blocker, posting-projection, rollback, and blind-harness proof remains incomplete. No paid calls or promotion claim.
- FAILED: Commit the smallest mapped implementation within 20 files / 4100 total changed lines / 1800 focused lines; complete documentation and implementation-exit observation, and record evidence in the state-owned stage report.
  Product work paused on measured row growth; FO explicitly directed preserving the product diff uncommitted. Approved limits and status remain unchanged; no implementation-exit candidate or observation exists.
- DONE: Record the Captain-approved zero-expansion narrowing before product work.
  State commit `588a7a82` records the consumed ideation resolution in outcome, AC-3, non-goal, and route-back wording; prior reports and stage pin are preserved.
- DONE: Exercise the current receipt seam and the clean exact-head journey.
  Public project-receipt test went from 3 failures/1 pass to 4/0: removing the new entry loses minted-run reuse and complete replay. Python integration is 2/0 (118.109 s): dropping rev2 identity/parent binding or complete rehydration breaks its assertions. This is not the full required without-it experiment.
- DONE: Check existing affected regressions and formatting.
  Existing runtime 372/0 and shadow 213/0 passed; their malformed-input fixtures retain their expected diagnostics. Ruff check and git diff --check pass. Changing shadow fail-open behavior or existing replay/confirmation semantics is covered by these suites; new authority refusal mutations remain owed.
- AC mapping: AC-1 is shaped, not fully documented as delivered; AC-2 through AC-7 are partial; AC-8/AC-9 are not run and remain budget-gated; AC-10 has partial code but not the required complete terminal/mutation proof.
- Current count: 7 changed files, 2,404 total changed lines, 462 focused lines. Definition: additions plus deletions from delivery base `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`, including the 950-line retained spec and complete untracked-file line counts; focused is schema + catalog + protocol test + fixture paths.
- Exact product HEAD remains `4118670919840fec859b139f580fdd47e4f912f8` on `feature/kc-pr-review-capability-protocol-pilot`. The partial diff is dirty, uncommitted, and unfit for validation: High finding-id composition differs from the current runtime helper, and retry/fallback, CLI activation, terminal schemas, sidecar metrics, and ablation recovery are not complete.

### Remaining ledger and proposed stop revision

All ranges below are additional formatted changed lines, including their negative tests where stated; they are planning estimates, not passing proof or new authorization. No product/document deletion or dependency change was made for this estimate.

| Remaining obligation | Existing owner / reuse and new seam | Required negative proof | Low-high lines |
|---|---|---|---:|
| Complete adapter | review-capability.py: retain planner/evidence/rehydration; add retry, manual fallback, CLI sampling, audit metrics, semantic closure | Wrong hash/ref, second contributor, missing required class, bad fallback, stale identity, false blocker, unsupported expansion | 290-480 |
| Complete closed objects | Existing new schema/catalog files: add terminals, decisions, confirmation, posting and audit definitions | Every status/reason mismatch, unknown field/version, invalid-intake echo misuse | 220-340 |
| Protocol proof corpus | Existing new protocol test file plus planned JSONL fixture file | Real rehydrate High merge, partial skip/no-lane, all-skipped abort, required-gap COMMENT, confidence boundaries, rollback and without-it | 580-780 |
| Runtime refusals | review-runtime.sh/test.sh: reuse append/replay and new existing-start entry | Wrong start identity, failed lane candidate, uncertain candidate, interrupted append, seal mismatch | 55-95 |
| Entry/docs/CI | Existing skill, PRODUCT, ARCHITECTURE, runtime docs, plugin README/CLAUDE and existing workflow | Exact-on switches sampled once, default-off parity, changed claim matches behavior; measure added local wall time | 160-240 |
| Whole-tree arms | ablation-core.py cmd_arm/arm_manifest: reuse manifest hashing; add committed tracked-tree/mode/commit pins | Uncommitted input, changed non-skill blob or executable mode, stale manifest | 90-130 |
| Corpus/admission/backup | ablation-core.py cmd_corpus: retain exact PR tuple; add five primary plus designated backup and dual six-mode admission | Missing/duplicate slot, non-Lite mode, changed corpus hash, second/one-sided substitution | 70-105 |
| Launcher policy/provenance | ablation.sh run: reuse pristine checkout and runtime-model readback; add explicit effort/host/tool/timeout/switch pins | Inherited token, wrong activation pair, mismatched effort/host/tools/timeout, mutation, resumed/human-input run | 105-150 |
| Driver/v4 receipt | Existing identical driver and runner wrapper: move stop to confirmation request, add symmetric config and closed treatment outcome | Missing/mismatched config, non-Lite treatment, decision plus terminal, unexplained missing receipt, early stop | 85-130 |
| Sidecar telemetry | Existing runner receipt wrap plus protocol sidecar: derive evidence bytes, lane critical path and treatment retries | Missing/malformed/non-monotonic telemetry, forged model counters, retry-source mismatch | 75-110 |
| Joined blind provenance | ablation.sh join/guard: reuse nonce/PR/prompt/model binding; add sealed normalized envelopes/adjudication binding | Swapped/stale adjudication, duplicate receipt, revealed labels, mutated joined provenance | 60-80 |
| Pilot comparator | ablation-core.py: keep old comparator unchanged; add five-slot quality-first wall-time rule | Lost control High/Critical, extra treatment FP, incomplete slot, either 33.3% rule failing | 80-110 |
| Cost admission | Existing daemon ledger read-only plus ablation runner launch guard | Fewer than five numeric completed REVIEW records, malformed selected entry, absent/mismatched approved budget | 40-65 |
| Ablation plumbing | Existing CLI/test fixture builders and planned corpus path; no second runner | Old arm/run/compare regressions, unsupported new options and missing pins | 35-50 |

- Ablation subtotal is 640-930; complete remaining estimate is 1,945-2,865, giving 4,349-5,269 total. Actual real corpus rows/admission calls remain deferred to the separately approved paid budget; synthetic fixtures do not impersonate admitted PRs.
- Proposed Captain decision: raise only total changed-line stop from 4,100 to 5,600; retain 20 files and 1,800 focused. The 5,269 upper estimate leaves 331 explicit risk allowance: runtime/fallback repairs 120, launcher/terminal correlation 90, schema/mutation repairs 80, documentation/count repairs 41. It is a stopping line, not a guarantee of sufficiency.
- File map remains the original 18 changed paths plus plugin README/CLAUDE (20 maximum); focused upper estimate is 1,582 plus 80 schema/test repair allowance = 1,662, leaving 138 before its unchanged stop. Exceeding any limit or adding a new surface returns to shape.
- Read-only reuse findings: the schema evaluator is 97 formatted lines; no declared generic JSON Schema dependency exists in kc-pr-flow. Marketplace L1 invokes the Claude marketplace installer; sibling Bun-lock Ajv entries are not this plugin's runtime seam. Host CLI help supports effort/MCP/tool-list flags; a stubbed launcher must prove their environment/argument isolation without model calls. This is not an OS-wide network-isolation claim.
- Documentation findings: about 60 retained-spec lines are clear metadata/history/maintenance-state candidates; another 66 ledger/stop lines own accepted scope. None was deleted or moved, and no hundreds-line equivalent was found. Such relocation alone does not establish a compliant 4,100-line route.
- Project context receipt remains `impact: update`, authority PRODUCT.md and ARCHITECTURE.md at their named kc-pr-flow headings; approved change is the external default-off Planner with unchanged runtime approval/posting owners. `landed_change: pending`; planned_check remains exact-head protocol tests plus authority-row comparison; `validation_evidence: pending`. No delivered-context update or RoboRev observation is claimed.

### Summary

Implementation is paused with a verified clean receipt journey and an incomplete, preserved product diff. The proposed 5,600 total-line stop changes neither outcome nor executable surface scope, but requires Captain approval before further product work; status remains implementation and the approved 4,100 stop is still in force.
