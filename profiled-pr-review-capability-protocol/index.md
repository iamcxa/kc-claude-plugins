---
title: "Pilot a profiled PR review capability protocol"
status: validation
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

## Accepted implementation limit revision

Captain chat `核准` on 2026-09-05 approves the exact proposed total changed-line revision from 4,100 to 5,600. The 20-file and 1,800-focused-line stops, zero expansion reserve, default-off Lite-only execution, every accepted criterion, and all other scope, spend, confirmation, posting, release, and ownership boundaries remain unchanged. This authorizes resuming the preserved partial implementation, not paid blind admission/evaluation or PR publication/merge.

The revised estimate is 5,269 total changed lines plus 331 named risk allowance: runtime/fallback authority repairs 120, launcher/terminal correlation repairs 90, schema/mutation coverage repairs 80, and documentation/count repairs 41. The current stop is 5,600, measured from the unchanged delivery base; this is a risk allowance and stopping line, not a guarantee that the implementation fits. The prior stop report remains historical, and the existing implementation-1 stage pin is not rewritten for this same-stage authority update.

## Implementation-exit observation attempt

- State: not claimed; claimant: `spacedock-ensign-t8cyxd55ve-implementation`; result `UNKNOWN(reason: stale)`.
- Observed clean-holder revision: `bfc2a24da9367886860707ef0d68261eb8e11a2b`; prerequisite passed and the exact supported state transaction returned a clean no-op before claim preparation.
- Canonical identity SHA-256: `9abf78af9f46aba8f83a34824762929a1221c4dfee1758a1f6205480907383cb`.
- Repository: `iamcxa/kc-claude-plugins`; base: `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`; tip: `55b7cd28fbf73095bd3f6982e1ab3db00a0c9071`.
- Configuration object: `225a29d4fa1eef963a7effaab7e60afa5f488e8f`; configuration SHA-256: `ae3555f0b3fcf5b626c39c614e3b2058bd2e31fb5840ce864edfaeded34f07f1`.
- Provider: RoboRev `0.62.0`; required JSON contract: `list --json`, `show --job --json`; mode: observe; profile: Pilot; implementation family: codex.
- Fixed reviewer: agent codex, model `gpt-5.6-terra`, reasoning medium, minimum severity medium, panel none; one stable member `codex:gpt-5.6-terra:medium`, complete population count 1.
- Live timeout: 900 seconds; explicit-request cap 1; changed-tip confirmation cap 1; requests and confirmations before claim: 0.
- Capability evidence: required CLI help available; existing daemon healthy; Codex authenticated; exact candidate branch job query returned JSON null. An initial diagnostic identity used an unverified repository spelling and is discarded; the final identity derives the repository from live origin.
- Single-flight stop: after prerequisite observed `bfc2a24d`, holder HEAD and the fresh remote read were both `418b802b361a6a555c1bf30030e631cf2fb755d0` before durability. The claim was not committed or retried; no provider request or confirmation was made. This is an observation attempt record, not a live claim. Job identity/member states/cost coverage are unavailable because no job was enqueued.

## Stage Report: implementation (cycle 2)

- DONE: Finish the accepted default-off Lite end-to-end journey and existing ablation recovery, preserving every required coverage, identity, evidence, fallback, receipt, confirmation and posting boundary.
  Candidate `55b7cd28fbf73095bd3f6982e1ab3db00a0c9071` implements selected planning/evidence, bounded calls/retry, manual clean fallback, existing receipt/decision projection, read-only independent posting-run projection, and whole-tree blind harness recovery; actual posting owner is unchanged.
- DONE: Prove the complete positive/refusal/mutation/rollback obligations and run relevant regressions; keep blind promotion unclaimed until the separate paid budget and five-pair evidence exist.
  The 17 final protocol cases are covered by the split runs below; ablation is 83/0, projection 8/0, existing runtime 372/0 and shadow 213/0 remain applicable. AC-8/AC-9 real paid evidence is deliberately absent, not replaced by synthetic promotion fixtures.
- DONE: Commit the smallest mapped candidate within 20 changed files, 5600 total changed lines, and 1800 focused lines; complete project documentation and implementation-exit observation, then record exact candidate evidence for fresh independent validation.
  Commit `55b7cd28` is on the approved feature branch with a clean product worktree; total 5,428 lines / 20 files / focused 1,256 (1,263 conservatively including corpus). RoboRev observation is `UNKNOWN(stale)`, request_count 0, confirmation_count 0, not a validation verdict.

### Exercised evidence and falsifiers

- Original finalization run: 15 protocol cases in 295.498 seconds, 13 passed / 2 errors. Preserve this result: one fixture used `repo` instead of `repository_path`; the other incorrectly appended posting events after a sealed review run. Neither error is relabeled a pass.
- Affected rerun: clean receipt/provider usage/posting outcome + corrected mechanical fixture + authority mutations + posting invalidation, 4/0 in 86.728 seconds. The clean case invokes six local provider stubs, projects/replays/rehydrates the actual runtime, and checks whole-child usage, model mismatch and raw-report tampering. Returning a fabricated cost or reusing the sealed review run breaks it.
- Final quick selection: all 14 non-long protocol cases, 14/0 in 16.338 seconds; later style-only combined-context change rechecked its authority case 1/0 in 1.206 seconds. These exercise closed fields/status pairs, catalog bijection/intent refusal, version/bundle/material/answer mutations, exact-on rollback routing, zero-attempt all-skipped termination, bounded retry/budget, and clean-only bound manual fallback.
- Final long-case coverage is three cases: High cross-capability merge and real failed/manual CLI fallback passed in the 15-case run; clean actual provider/receipt/posting passed in the 4-case rerun. No single final 17/0 execution is claimed. Later adapter edits only tightened independent posting-run projection; planner/evidence/dispatch/collation/finish owners used by High/fallback were unchanged.
- Latest posting refusal case: 1/0 in 6.318 seconds, proving absent outcome stays absent, independent run invalidation preserves its run ID, wrong review_key/head/config/base/repository and review-run reuse reject without changing the live event file. Latest confidence case: 1/0 in 1.629 seconds, checking 1–2 drop except quoted Critical, 3–4 advisory, 5+ finding, and unquoted Critical advisory.
- Actual posting mismatch RED→GREEN: current `review-post.sh` starts a fresh posting run; the original fixture failed replay with inconsistent event relationships. The corrected projection retains the actual posting run ID while binding the reviewed tuple, rather than weakening receipt replay or editing posting code.
- Ablation full regression: 83/0 in 49.88 seconds. Whole committed-tree drift, six-row/mode admission, designated backup substitution, sealed adjudication, missing High/extra false positive, both time thresholds, inherited credentials and stalled-host rejection fail their relevant assertions when weakened. Historical 82 cases remain pinned to their original committed text.
- Clone seam RED→GREEN: actual shared local clone fails the canonical repository helper because origin is a local path; the new runner validates the source identity then changes only its newly created clone origin, and the host stub confirms the canonical value. Source origin stays unchanged.
- Unchanged owner evidence: runtime Git blob `699535682a914a54faa22a29c42a12ad4c6fdb63` retains prior runtime 372/0, shadow 213/0 and explicit projection 8/0 results. Posting blob `70bbe96f5417369a1decf00a9bd9eea372180edc` and daemon blob `15542da657ccaa19a7518142f8f96dcdcd47a072` are exactly equal to the pinned delivery base. No remote posting or model experiment occurred.
- Static checks: Ruff check passes for adapter/tests and for existing ablation core with only its pre-existing UP031 style ignored; new adapter/test format check passes; shell syntax, git diff --check and skill frontmatter lint (44/44) pass. No hooks were bypassed; no dependency/version/release changes.

### Scope, cost and project context

- Count definition: additions plus deletions from `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8` to the exact candidate, including the 954-line retained design; 172 lines remain before the total stop. Five new protocol files and all existing-owner changes are counted, not only the last commit.
- Minimal mapping: schema/catalog own one closed contract and requiredness source; adapter owns planning/calls/collation; current runtime owns receipt and decision authority; existing ablation owner owns arms/admission/measurement; existing posting owns mutation. Removing the catalog/binding/projection/admission checks makes the corresponding exercised mutations pass incorrectly; no new daemon, service, provider, posting owner or executable expansion exists.
- File-map consolidation: the six originally planned JSONL fixture rows moved intact into the existing new Python test and still run as six subtests. The freed path was used by the existing evaluation workflow's narrow fetch of the exact historical Git object; no new workflow or skipped historical regression. New runtime job runs protocol/projection only, with no duplicated ablation invocation.
- CI cost per PR is unmeasured. Local finalization was 295.498 seconds including the failed fixtures; the repaired clean/four-case selection was 86.728 seconds and quick selection 16.338 seconds. These are test/runtime overhead, not paid review speed; the separate 8-minute profiled job preserves the original core job budget. Narrow historical fetch hosted incremental cost is also unmeasured.
- Mechanical observations from existing runs only: manual prepare 0.914 seconds, projection 75.956 seconds, rehydrate 6.908 seconds; repaired clean projection 73.541 seconds, rehydrate 5.396 seconds. Repeated append/replay validation is a source-backed overhead hypothesis, not a reason to weaken integrity.
- Read-only historical cost admission: 6 qualifying REVIEW-bearing records; max USD 4.9612; latest 2026-03-15T20:00:05Z; ledger SHA-256 `a6e8fc70c891f2840300cc132a2fa15fbe8c00080b9a95fe1fc1e90b20a7872c`. Old composite daemon attribution is not current-model assurance. No real corpus is admitted, no paid budget is approved, no blind model run or promotion result is claimed.
- Project context receipt: `impact: update`; authority root PRODUCT.md, ARCHITECTURE.md and CLAUDE.md via docs/dev/README.md; claim locators PRODUCT "Default-off profiled Lite Pilot" and ARCHITECTURE "Profiled Lite adapter"; surface default-off external Lite adapter with unchanged runtime/posting authority; approved_change selected evidence and question coverage before existing confirmation; landed_change those sections at `55b7cd28`; planned_check fresh protocol/runtime behavior against authority rows; validation_evidence pending fresh validation. Root CLAUDE rules remain unchanged; plugin README/CLAUDE and runtime usage were updated in the same slice.
- RoboRev exact-input identity/config and capability probes are recorded above. The supported clean no-op transaction passed, but another writer changed the holder revision before claim durability; the contract stopped with UNKNOWN(stale). No live claim, job, request, confirmation, or attributable review cost exists. Do not retry this observation as a substitute for fresh validation.

### Summary

The accepted implementation is committed as a tested candidate within all three approved limits; the original stopping report and stage pin remain historical. Fresh independent validation is next, and the workflow status remains implementation until the First Officer advances it; paid blind admission/promotion and publication/merge remain outside this implementation authority.

## Stage Report: validation

- FAILED: Verify the exact committed default-off Lite journey and its authority/refusal boundaries through required real seams, using green implementation evidence where the relevant bytes are unchanged and performing the fresh checks the validation contract owns.
  REJECTED for six mapped repair groups; clean real receipt/rehydration/posting projection passes, but malformed artifacts lack closed terminals and route, projection, blind-harness, cost and document obligations remain.
- DONE: Obtain a fresh read-only Claude Opus 5 xhigh implementation assessment, faithfully record every finding and its evidence, and separate fixable implementation defects from the explicitly budget-gated real blind evaluation.
  Fresh main-model Opus 5 report says NEEDS_FIXES (8 Medium/6 Low); every item is dispositioned in [findings](validation-55b7cd28/findings.md), with unchanged [full result](validation-55b7cd28/claude-result.json). No second request or resumed session.
- DONE: Record exact-revision acceptance coverage, independent retained-document and project-context checks, minimal-necessity evidence, measured local cost/timing limits, and a concrete next decision without claiming speed improvement, Pilot completion, or publication authority.
  Candidate `55b7cd28fbf73095bd3f6982e1ab3db00a0c9071`, base `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`, clean approved feature branch; 20 files / 5,428 total / 1,256 focused (1,263 with corpus), leaving 172 total lines.

### Fresh evidence and disposition

- Real-seam test `PlannerTests.test_selected_evidence_binds_the_runtime_identity_and_rehydrates`: 1/0 in 79.344 s; six local provider stubs, exact identity, whole-child usage, replay/rehydration and independent posting run. Removing identity/usage binding or accepting altered raw reports breaks it; this is not paid-model proof.
- Document-claim checks: closed fixtures/deterministic plan/terminal matrix 3/0 in 0.008 s; selected CI entry `review-runtime.test.sh --case profiled-receipt` 8/0. Invalid identity, uncertain input, and reused sealed start fail; no full green regression replay or synthetic speed conclusion.
- Actual without-it: an ephemeral copy removes the new projector function and CLI entry; the same prepared clean journey returns runtime exit 2 and ABORTED_INCOMPLETE/receipt_incomplete instead of an approval-ready decision. Product code is untouched; [observation](validation-55b7cd28/local-checks.json).
- Reuse is byte-bound: runtime blob `699535682a914a54faa22a29c42a12ad4c6fdb63` matches the implementation report; unchanged posting `70bbe96f5417369a1decf00a9bd9eea372180edc` and daemon `15542da657ccaa19a7518142f8f96dcdcd47a072` equal base. Prior runtime 372/0 and shadow 213/0 remain author evidence for unchanged owners, not a fresh full-suite claim.
- Repair groups: sampled route/control refusal; malformed input/evidence/terminal closure; failed-run receipts and complete cost accounting; inherited credential isolation; inline finding projection and blind prose neutrality; promised parity/authority tests plus retained-document/render proof. Each has an exact owner and falsifier in findings.md; repairs return to the original implementation worker through FO.
- Fresh [reproductions](validation-55b7cd28/findings-repros.json): overlong identity, missing prepared and non-object fallback exit 1 with no terminal; newline Token accepted; unknown capability emits the wrong required_gap trigger; Latin-1 text becomes schema_failure; HIGH/confidence-9 yields no inline comments/location; protocol prose survives blind normalization; malformed normalized finding raises KeyError.
- Claude dispositions: M1–M6 confirmed in the bounded forms recorded; M7 is a gated performance hypothesis only; M8 partly confirmed, with historical file-map and existing confirmed-blocker/pending tests corrected. L1/L2/L5 reproduced; L3 disproved by existing pipefail; L4 is conditional exposure, not a proven sibling-file leak; L6 has no current runtime mismatch. Seven explicitly unverified questions are not promoted into defects.
- Retained-document check independently compared every new spec section with product/architecture, plugin README/CLAUDE, runtime usage/reference and triage. The table/catalog drift claim has no reader/check; record-only shaped/pending/count/timing prose remains in retained docs. Author confirmed the new Mermaid diagram was not rendered. Existing shape rows are estimates, not proof a missing fixture file must be added.
- Project context: impact update; authority root PRODUCT.md, ARCHITECTURE.md, CLAUDE.md; landed locators “Default-off profiled Lite Pilot” / “Profiled Lite adapter” at the candidate. Fresh CLI default-off/Custom refusal and real receipt behavior validate unchanged authority ownership; projection/document defects above prevent declaring the full delivered context clean. No new unmapped service, dependency, posting owner or executable expansion found.
- AC-1 authority owners mapped, retained documentation needs repair; AC-2 closed schemas partly pass but malformed-input/parity gaps remain; AC-3 deterministic Lite and zero expansion exercised; AC-4 selected evidence passes with unsupported-material/host isolation gaps; AC-5 clean results and usage pass, failed-run accounting remains; AC-6 blocker/coverage ownership passes with missing mismatch probes; AC-7 default-off and inline projection need repair; AC-10 traceback-only and failed-run records need repair. AC-8 and AC-9 real quality/speed evidence are NOT RUN, separately budget-gated.
- Claude provenance: CLI 2.1.261; AUTH_OK claude.ai; fresh full-prompt stdin, safe-mode, disabled slash commands, strict empty MCP, tools empty, no persistence. Main model readback claude-opus-5; xhigh is the explicit CLI request, with no separate effective-effort field. Internal Haiku/Fable advisor usage is disclosed, not an invented pure-provider requirement; spawned subagents 0, server web calls 0.
- Reported review cost USD 8.4982805 includes Opus 5.9702385 + Haiku 0.086922 + Fable 2.44112; duration 1,781,095 ms (API 1,782,901 ms). Full JSON SHA-256 `0dc306b2e84b25f6a454bb2497100f4095f592fae718e0fa975f5b5cce234f5c`; session `d259cfcf-8e27-4939-a933-04e1023e5d66`. This ordinary assessment is not a blind-run cost or timing sample.
- Local environment: activated existing Python 3.13.2 venv, Bash 5.3.3, jq 1.7.1; no dependencies installed. Fresh mechanical projection 70.066604541 s / rehydrate 5.742714292 s; hosted incremental CI cost per PR remains unmeasured. Existing narrow path triggers and pinned-base fetch inspected; no CI edit by validation.
- Read-only historical helper: 6 REVIEW-bearing records, max USD 4.9612, latest 2026-03-15; ledger SHA-256 `a6e8fc70c891f2840300cc132a2fa15fbe8c00080b9a95fe1fc1e90b20a7872c`. Proposed USD 115 planning allocation covers 6 admission + 10 arm + 5 adjudication + 2 backup units (23 × 4.9612 = 114.1076); it is NOT a current-price assurance or hard whole-experiment guard because admission/adjudication accounting is missing.
- SKIPPED: Real PR admission, paid blind runs/adjudication, speed or Pilot-completion claims, provider posting/publication, PR/branch push, merge/release/version changes, and duplicate RoboRev observation.
  Explicit authority boundaries remain closed. Candidate PR query returned none; product tree stayed clean; validation writes only this task's state-owned evidence and does not self-advance or prepare a gate.

### Summary

Validation rejects the exact candidate for the mapped repair batch while preserving passing real-seam and actual-removal evidence; missing blind authorization is not mislabeled a product defect. Next is a read-only repair plan from the original author under the remaining 172-line allowance; no fit is promised and no document-deletion credit assumed, so any needed scope/limit delta goes to the Captain before product edits.
