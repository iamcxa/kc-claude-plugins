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

## UNAPPROVED repair-sizing addendum

This is author sizing at the existing validation checkpoint, not an accepted route revision, implementation dispatch, gate decision, or permission to edit product files. Candidate remains `55b7cd28fbf73095bd3f6982e1ab3db00a0c9071`; the rejected validation report and stage pin remain unchanged. The approved stops are still 20 files / 5,600 total / 1,800 focused. No test, model call, product edit, branch change, or status change was performed for this estimate.

### Six-group estimate

These ranges estimate new source lines, including necessary negative-test lines, before replacement credit. Code includes closed schema/guard changes. They are not added again to the tests column.

| Confirmed repair group | Code / schema | Negative tests | Documentation | Added-line total | Replaced/deleted existing lines, estimate only |
|---|---:|---:|---:|---:|---:|
| 1. Preserve sampled routing and refuse contaminated control | 10–16 | 18–30 | 2–4 | 30–50 | 4–8 |
| 2. Malformed input, unsupported material and closed refusals | 48–80 | 55–85 | 4–6 | 107–171 | 15–30 |
| 3. Failed-run receipts and whole-experiment cost | 190–275 | 100–145 | 15–25 | 305–445 | 55–90 |
| 4. Inherited Git credential isolation | 20–35 | 30–45 | 2–5 | 52–85 | 3–8 |
| 5. Inline finding projection and arm-hidden input | 35–55 | 35–55 | 5–10 | 75–120 | 10–20 |
| 6. Generated views, authority tests and rendering | 25–45 | 45–70 | 8–15 | 78–130 | 5–10 |
| Total | 328–506 | 283–430 | 36–65 | 647–1,001 | 92–166 |

### Smallest concrete repair within existing owners

1. Reuse the skill invocation, `enabled()` and `cmd_pilot_run()`: remove forced `on` values and reject control runs leaving protocol artifacts. Execute the exact skill command under control-off flags with a local model stub; it must remain legacy with no capability invocation.
2. Reuse `main`, `terminal`, `prepare`, `collate` and `pilot_normalize`: validate dispatched/fallback object shape before access; bound the invalid-input echo per field; put unsupported encoding/size into the existing missing-evidence partition; close Token suffix acceptance and normalized finding failures. Invalid out-of-plan results must not consume the one-trigger `required_gap` reason. Reproduce overlong identity, missing prepared, null fallback, Latin-1, oversized material, newline Token and malformed finding as named non-passing outcomes without traceback-only exits.
3. Reuse `pilot_telemetry`, the existing experiment `.budget.lock`, manifests and receipt guard. Preserve every failed/retried call, known-cost subtotal and unknown-usage status; unknown usage must never be skipped, released as unused budget or scored. Route pre-freeze admission, arm, adjudication and designated-backup consumption through the same experiment reservation/finalization owner. The proposed mechanism is a closed unit-kind branch of existing `run --pilot`, not a new standalone CLI command, ledger, service or workflow; its new invocation branches and manifest/receipt fields are included above, not hidden by sharing a file. Test first failure then success, all failures, timeout, null usage, budget exhaustion and duplicate consumption without paid calls. A genuinely independent surface discovered while implementing this remains a route-back, not authorized by the estimate.
4. Reuse the existing child-environment construction: isolate global/system/injected Git configuration, credential helpers, askpass, SSH agent and GitHub credentials; restrict child Git transport while preserving required model authentication. Use only synthetic inherited helpers and local push targets to prove they are not invoked. This is not an OS-wide arbitrary-Bash/egress isolation guarantee and proposes no sandbox product or dependency.
5. Reuse `collate()` and `pilot_normalize()`: derive path/side/line from the already verified quote/blob/diff and produce the existing location-bound inline shape. Normalize both arms from the same structured findings instead of verbatim protocol summary prose; preserve all findings. Test left/right locations, quote mismatch, retained High blockers and treatment-only marker absence.
6. Generate the question table from the catalog and status matrix from the schema using the existing adapter/test owners, with checks reading and falsifying the retained table. Execute rehydrate projection mismatch and candidate-bearing non-succeeded-lane refusals, not enum-only fixtures. Render the Mermaid with an existing browser renderer, inspect it against the implementation, and retain the render evidence in task state. Read-only executable discovery found no `mmdc`; no dependency installation is proposed, and actual rendering remains owed.

### Counting and mapped relocation candidates

The final count remains additions plus deletions from delivery base `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`, not churn from the latest commit. Rewriting a newly added file does not count the removed intermediate lines twice. The ceiling proposal below takes zero replacement or document-relocation credit; actual final diff counting must still be recomputed after any separately authorized repair.

Seventy existing added lines have concrete replacement targets at candidate `55b7cd28`: adapter echo lines 1633–1643 (11); ablation telemetry 866–901 (36); reservation 1066–1071 (6); timeout 1166–1173 (8); terminal-cost 1239–1240 (2); skill forced flags line 114 (1); normalized summary line 1502 (1); adapter body 1200–1203 and empty inline line 1210 (5). Even deducting those mapped replacements from the low estimate yields `5,428 + 647 - 70 = 6,005`, above 5,600. Optimistically deducting all estimated replacements (166) and all gross relocation candidates below (106, before replacement links) still yields about 5,803; neither larger deduction is approved or guaranteed.

| Candidate record-only block at 55b7cd28 | Gross lines | Existing second home / preservation requirement |
|---|---:|---|
| Spec lines 5–8 and 32–35: task metadata and historical shape delta | 8 | Existing entity accepted-outcome and acceptance-history sections; preserve exact accepted zero-expansion boundary in the retained contract. |
| Spec lines 776–801: dated reverse-recovery audit and completeness labels | 26 | Existing entity ideation/audit history; copy the historical evidence without erasing the durable authority map. |
| Spec lines 814–825: pending project-context receipt | 12 | Existing entity implementation/validation context receipt; preserve original historical record and current validation result. |
| Spec lines 827–858: historical per-file implementation estimates | 32 | Existing entity shape-sizing history; preserve actual owner mapping in durable architecture/contract and update the inline-fixture disposition there. |
| Spec lines 870–885: superseded estimate and risk allowance narration | 16 | Existing entity accepted-limit revision/history; retain the actual approved stopping conditions and scope boundaries. |
| Spec lines 897–904 and runtime usage lines 371–374: historical tests and measured timing | 12 | Existing entity implementation/validation evidence; retain exact source revision, commands/results and attribution caveats. |
| Total gross candidate movement | 106 | No deletion permission or net line credit; any replacement links/durable wording consume lines. |

These are record-placement candidates, not unnecessary product surfaces or approval to delete accepted outcomes, limits, proof obligations or historical evidence. No relocation was performed. Protocol authority, profiles, question rules, schemas, evidence semantics, confirmation/posting boundaries and required falsifiers remain in the retained contract.

### Sole proposed Captain delta — NOT APPROVED

Raise only the total changed-line stop from **5,600 to 6,600**. Preserve 20 files, 1,800 focused lines, every confirmed repair obligation and accepted outcome, default-off Lite-only execution, zero executable expansion, current runtime/posting authority, no independent ledger/CLI/workflow/service/dependency, and all paid-budget/publication/merge restrictions.

The proposed 6,600 stop is `5,428 + 1,001 + 171`: current measured candidate, upper added-line estimate with no deletion credit, and 171 named integration allowance (cost/receipt integration 80, evidence/inline repairs 50, schema/proof repairs 41). Focused upper estimate is approximately 1,631 including conservatively counted corpus and proof risk, below unchanged 1,800. All proposed product edits reuse the existing 20 paths; state evidence/render artifacts do not create another product file.

This is a stopping line and risk allowance, not a guarantee of sufficiency. The 5,600 stop remains in force until the Captain explicitly approves the exact delta and its owning authority records it. Fresh validation remains rejected; no repair starts from this addendum, and the distinct paid blind budget remains unapproved.

## Accepted correction limit revision

Captain chat `同意` explicitly approves the preceding sole proposal: raise the total changed-line stop from 5,600 to 6,600 while preserving 20 files, 1,800 focused schema/catalog/fixture/test lines, the accepted outcome, all six confirmed repair obligations, default-off executable Lite, zero expansion reserve, and unchanged posting/merge/release authority. This authorizes the existing-owner correction batch and fresh Claude re-review, not acceptance of rejected candidate `55b7cd28fbf73095bd3f6982e1ab3db00a0c9071`.

No real paid admission/arm/adjudication, product branch push or publication, version/release change, Forge/Nightwatch integration, new dependency, independent ledger/CLI/workflow/service, or unrelated cleanup is approved. Unknown paid-attempt usage remains unknown and consumes its existing experiment reservation. Product scope remains the existing 20 paths and the cumulative base remains `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`.

The prior UNAPPROVED sizing addendum, both historical stage reports, rejected validation evidence and historical stage pin remain unchanged. The 6,600 stop is the recorded 5,428 candidate plus 1,001 upper added-line estimate and 171 named integration allowance; no deletion credit is assumed. The previous RoboRev UNKNOWN(stale), zero-request observation is retained without retry. Only the First Officer controls correction-round lifecycle and the retained independent validator's next review.

Historical shape estimates, pending context records and local timing records are preserved verbatim in [implementation-record-relocation.md](implementation-record-relocation.md) before their removal from retained product documentation. This is record placement only, not a status, pin, acceptance, scope or limit change.

## Stage Report: implementation (cycle 3)

- DONE: Record and re-read the Captain-approved total-limit revision before product edits, then repair all six confirmed findings groups through the existing owners without expanding executable scope or authority.
  Approval state `d60869b0`; all six existing-owner repairs committed as `9bb526170156a44cff90e2a2fab9eeab081e0eb1`; [per-group evidence and necessity mapping](correction-9bb52617.md).
- DONE: Prove each repair with the named falsifier and relevant regressions, including complete failed/unknown-cost records, isolated synthetic credential tests, correct inline projection and actual document rendering; preserve all known unresolved evidence.
  Exact sampled command, malformed CLI, all-failed/retry receipts, total reservation/unknown refusal, synthetic push refusal, real HIGH inline and rehydrate-mismatch cases exercised; generated table parity and [actual runtime-usage render](runtime-usage-render.svg) completed. Split 21 + 1 + 1 protocol coverage and 83-case ablation then affected Pilot RED→GREEN are reported without inventing one final full run.
- DONE: Commit one clean corrected exact-revision candidate within 6600 total changed lines, 20 files and 1800 focused lines; durably record the correction evidence and return to the retained independent validator without self-advancing or paid blind runs.
  Candidate `9bb52617`: 6,431 total / 20 files / 1,495 focused (1,502 including corpus), product worktree clean after commit. This state report is handed back through the First Officer; it is not a validation result or a status/pin update.

### Summary

Six rejected implementation boundaries were repaired through the accepted owners, with explicit failed-attempt cost retention and no new lifecycle surface. Historical records were preserved before relocation; the actual newly added runtime-usage diagram was rendered, withdrawing the earlier mistaken two-file source-disproof. Paid quality/speed and hosted CI cost remain unmeasured; prior UNKNOWN(stale) exit observation and rejected validation are preserved, and the First Officer owns the retained independent validation and neutral round-record boundary.

## Captain-approved one-round review-format deferral

Captain chat `同意` approves this exact question, as routed by the First Officer: `是否同意本輪明確延後格式轉換，以已提交的原始審查與逐項修復證據繼續 Claude 重審，不豁免任何缺陷或測試？`

For this corrected-candidate review round only, feedback-rejection-flow step 2 canonical two-file conversion (`briefing.json` plus `briefing.review.jsonl`) and the corresponding neutral recorder publication are **DEFERRED, NOT DONE**. Existing committed `validation-55b7cd28/findings.md`, `validation-55b7cd28/claude-result.json`, `validation-55b7cd28/local-checks.json`, `validation-55b7cd28/findings-repros.json`, and `correction-9bb52617.md` are the review evidence for a fresh Claude re-review of candidate `9bb526170156a44cff90e2a2fab9eeab081e0eb1` against base `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`.

This permits fresh re-review only after this approval is committed, synchronized, reread, and the First Officer confirms that readback. It waives no defect or test and authorizes no automatic gate approval, status/pin/review-round mutation, task closure, paid blind corpus admission/arms/adjudication, product branch push or PR publication, merge, or release. Do not fabricate the canonical two files, reuse an older gate room, add a ledger/CLI/workflow, or repair the missing converter under this exception.

All historical findings, reports, and approvals remain preserved. The accepted 6,600 total changed-line stop, 20 product-path stop, 1,800 focused-line stop, default-off executable Lite, zero expansion reserve, validation status, and historical validation-1 stage pin remain unchanged. The retained validator stops at this preparatory authority checkpoint until the First Officer confirms readback; no Claude call precedes that confirmation.

## Stage Report: validation (cycle 2)

- DONE: Record and reread the exact Captain-approved one-round review-format deferral in task state without altering product, status, historical pin, or previous findings, and return its durable commit to FO before any paid review.
  Approval commit `49cded7562b7175c9d951df1ad6ccf5fcb3da94a` synced/reread and FO-confirmed before the sole fresh request; canonical two-file conversion and neutral publication remain DEFERRED, NOT DONE, with no defect/test waiver.
- FAILED: After FO readback, independently assess corrected candidate 9bb526170156a44cff90e2a2fab9eeab081e0eb1 with fresh Claude Opus 5 xhigh, closing or retaining every prior finding on concrete evidence and checking the accepted journey at changed seams.
  Assessment completed but implementation REJECTED: Claude NEEDS_FIXES (1 High/7 Medium/6 Low); [every fresh and prior disposition, sources, falsifiers and owner](validation-9bb52617/reverification.md) separate confirmed defects from disproved/conditional claims.
- DONE: Commit faithful exact-candidate validation evidence, AC coverage, raw Claude result and complete usage, distinguishing implementation acceptance from still-unapproved paid blind quality/speed runs, and return to FO without self-advancing.
  [Full unchanged Claude JSON](validation-9bb52617/claude-result.json), [repair checks](validation-9bb52617/local-checks.json), [document checks](validation-9bb52617/document-checks.json), [adapter reproductions](validation-9bb52617/new-findings-probes.json) and [runner reproductions](validation-9bb52617/runner-findings-probes.json); no product/status/pin/gate/PR mutation.

### Evidence that changes the decision

- Existing six-group repairs: eight separate targeted protocol tests passed, including real inline/blocker journey (122.751 s) and actual runtime-output mismatch (104.572 s); selected Pilot 1/0 and runtime receipt 9/0. These are stubbed/local mechanics, not one full-suite run or speed evidence. Removing quoted inline output, accepting changed runtime output, unknown cost or failed-lane candidates falsifies them.
- New adapter failures: actual post-mint malformed fallback loses run_id/config_hash/review_key; null/NaN provider output escapes per-attempt classification; absolute monotonic values over 2^53−1 fail the audit. Same-quote second occurrence is incorrectly rendered at line 1. Correct failures must stay identity-bound, visible and non-approving.
- New runner failures: actual INVALIDATED/identity_change becomes generic attempt_failed; changing only runner-local catalog rejects unchanged arm traces; schema-valid preplanted receipt survives failed owner finalization and is accepted by the real ten-record join with forged wallclock_ms=1. Recommendation prose also survives blind normalization. Missing input/repeated phase retain traceback-only diagnostics.
- No unauthorized outer retry: Claude F5's latest-success replacement conflicts with the accepted fixed effective sample set and is not assigned. F13 remains conditional hardening; F14 separates local wall-time evidence from hosted dollar cost, with pre-trigger-widening sequence not established. No new paid compatibility probe or whole-candidate review.
- AC-1/AC-2/AC-5/AC-7/AC-10 remain incomplete on confirmed boundaries; AC-3/AC-4/AC-6 have bounded exercised evidence, not a whole-outcome pass. AC-8 has fixable harness defects plus unrun paid evidence; AC-9 quality/speed evidence remains NOT RUN and separately Captain-budget-gated.
- Count: 6,431 total changed lines / 20 product paths; narrow four-path focused count 1,502, but schema/catalog/corpus/protocol plus runtime/ablation focused changes total 1,939 (139 over 1,800). Even excluding 14 shell enablement/maintenance lines gives 1,925. Original narrow arithmetic and broad wording conflict; Captain owns the denominator/stop decision, so no unconditional within-limit PASS or cap revision is asserted.
- Project context: approved `impact: update` at PRODUCT "Default-off profiled Lite Pilot" / ARCHITECTURE "Profiled Lite adapter" matches fresh route/receipt ownership evidence, subject to the open boundary defects. All eight historical blocks are preserved exactly; actual runtime-usage Mermaid source matches existing rendered input. Temporary wrong table produces RED, original text GREEN; no extra render or unrelated document repair.
- Necessity/reuse: runtime `699535682a914a54faa22a29c42a12ad4c6fdb63` unchanged; posting/daemon equal base. Prior actual projector-removal without-it remains valid exact-owner evidence, not a newly rerun claim. No new service, dependency, runtime event, posting owner or expansion exists; every retained surface maps to the accepted journey/proof.
- Provenance: one fresh Opus 5 CLI request with xhigh explicitly requested, safe mode, empty tools/MCP, no persistence/resume; provider session `b96ca5d8-ce91-4571-a605-69ce87107132`, completed/exit 0, 920572 ms, zero subagents/web calls. USD 6.11592275 includes Opus 3.44122975 + Haiku 0.099723 + Fable advisor 2.57497; full usage retained, no separately reported effective-effort field invented.
- Product remains clean at exact `9bb52617`; historical validation-1 pin SHA-256 remains `8dbc54e264711a9d9da98a160726a3a9b4f846bed2d4e4b23196581fb5c67ea8`. Prior RoboRev UNKNOWN(stale), zero requests retained. Hosted incremental CI cost/PR and real blind quality/speed are unmeasured; reservation/refusal is not a guaranteed provider hard-dollar ceiling.

### Summary

REJECTED: concrete adapter and measurement-authority defects remain despite green targeted repair checks. FO receives the deduplicated repair batch plus Captain-owned focused-count/CI-precondition questions; no repair, new limit, paid blind run, gate approval, publication or terminalization is authorized by this report.

## Accepted complete counting and reduction decision

Captain replied `同意` to: `Claude 重審未通過；已重現假耗時紀錄被接受、失敗身分遺失等問題。納入新增 shell 測試後，相關行數是 1,939，不是先前窄口徑的 1,502。建議採完整口徑，維持原上限與驗收要求，先縮減並修復，再送 Claude；是否同意？`

The complete focused denominator is 375 schema + 96 catalog + 1,024 protocol tests/inline fixtures + 7 corpus + 47 runtime integration/refusal tests + 390 ablation Pilot tests/enabling edits = **1,939**. Historical 1,502 remains a narrow prior report, not current acceptance. The unchanged stops are **6,600 total changed lines / 20 product paths / 1,800 complete focused lines**, counting additions plus deletions against `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`; test content counts by role wherever placed. Current excess is authorized for equivalent reduction, not general growth, hidden relocation, weakened falsifiers or another cap increase.

This authorizes one retained owner to reduce actual duplicate test/setup structure and repair the five existing-owner groups in the latest dispatch: adapter terminal/provider/audit closure; terminal telemetry/pinned-arm evaluation; runner-owned measurement integrity; blind/inline projection; existing unit-kind and duplicate-phase diagnostics. Outcome, non-goals, default-off executable Lite, zero expansion reserve and existing posting authority remain unchanged. A sufficient repair needing a new surface, authority or lifecycle returns to the First Officer before implementation. F5 outer retry is not assigned; F13 remains conditional; F14 requires honest historical sequence evidence or an explicitly unmet precondition.

Rejected candidate `9bb526170156a44cff90e2a2fab9eeab081e0eb1`, latest rejection state `f7f34d39c5caf1ad0a0ba4456295627721d51863`, earlier reports, validation status and stage pin are preserved. No paid blind work, self-review, publication, branch push, workflow tooling, gate/status/pin change or new observation is authorized. The prior one-round review-format deferral is historical and is not expanded by this decision. This decision is committed/synced and reread before product edits.

## Stage Report: implementation (cycle 4)

- FAILED: Record and reread the Captain-approved complete focused-test counting scope, then reduce duplication without weakening any accepted behavior or falsifier until the existing 6600 total / 20 files / 1800 complete focused-line stops are met.
  Approval was committed/synced and reread at `73b108d5fe17cd4c3e5471491f0e9aee98e49d10` before any product edit. Reduction remains NOT DONE: complete focused count is still 1,939, 139 over 1,800; total remains 6,431 / 20 files. No deletion credit or green count is claimed.
- FAILED: Repair the five confirmed existing-owner defect groups using structural fixes and RED-to-Green falsifiers, with special proof that child-written measurement records cannot be accepted and post-identity failures preserve identity and terminal meaning.
  Measurement-integrity diagnostic reproduced a missing protection premise; the First Officer explicitly stopped product work before a partial remedy. All five repair groups remain unimplemented; exact blocker and observed evidence follow.
- FAILED: Commit one clean exact-revision candidate with complete scope counts, required regressions, retained-document/context evidence, and every unresolved or conditional finding preserved; return to FO without self-review, paid blind work, publication, or gate changes.
  No corrected candidate exists. Product is unchanged and clean at rejected `9bb526170156a44cff90e2a2fab9eeab081e0eb1`; this is a state-only stop report. Prior render, raw reviews, conditional/disproved findings, status and stage pin remain untouched.

### Exact missing premise and new reproduction

The accepted outcome requires trustworthy runner-owned measurement, but the existing process and filesystem permissions do not isolate the model's Bash child from existing experiment authority files. `pilot_join` in `review-ablation-core.py` reads manifests/receipts from that same writable tree and checks closed schemas and recomputable hashes; there is no independently trusted authentication root. The existing Git credential isolation does not protect local measurement files.

One new synthetic local diagnostic was actually run with activated Python 3.13.2 against unchanged candidate bytes (process exit 0, 0.499 s; no network or provider). It reused only the existing valid ten-record fixture setup from `review-ablation.test.sh`, created a temporary experiment, set `1-control/receipt.json` to mode 0400, and launched a separate Bash child from `2-treatment`. That child invoked Python to change the earlier receipt back to mode 0600 and set its `wallclock_ms` to 1; the parent then called the real `pilot_join`. Observed output:

```json
{"child_cwd_unit":"2-treatment","modified_prior_unit":"1-control","initial_mode":"0400","child_exit":0,"real_join_count":10,"accepted_wallclock_ms":1,"network":false}
```

The child operation was `p.chmod(0o600); v=json.loads(p.read_text()); v["wallclock_ms"]=1; p.write_text(json.dumps(v))`, with the exact temporary prior-receipt path passed as an argument. The fixture and child were disposable, and product/state authority files were never child targets. This supplements the preserved independent F6 reproduction where actual finalization raises FileExistsError on a preplant and real join accepts it; it does not replace or rewrite that evidence.

### Cheaper remedies and boundaries

- Moving current child output to a subdirectory or making receipts read-only is insufficient: the new diagnostic crosses unit directories and reverses mode 0400 under the same UID. Neither pathname placement nor same-owner chmod establishes a write boundary.
- Replacing only the current unit's receipt after the child exits would not protect an earlier unit: the observed mutation targets `1-control` while the child runs in `2-treatment`. Catching FileExistsError alone would fix a diagnostic while leaving forged data eligible for join.
- Extra unkeyed hashes or a seal in the same child-writable tree supply consistency, not an independent producer identity; the verifier and all inputs remain reconstructible by the child. No such partial repair was implemented.
- A parent-memory snapshot, full-lifetime advisory lock and parent-only final write were considered, not implemented or certified. They would require limiting the child threat to the runner's controlled lifetime. Existing `killpg` is not evidence that arbitrary Bash cannot leave a writer outside that process group; no detached-process exploit was run and no stronger guarantee is claimed. The First Officer explicitly rejected silently narrowing that premise.

A sufficient solution needs a protection premise not currently present: an enforced write boundary for owner measurements, or an independent trusted verification root that the child cannot rewrite. Introducing that premise may change the accepted authority/surface allocation and is outside this correction's explicit no-sandbox/service/ledger expansion boundary. The First Officer is taking a bounded route revision to the Captain; no implementation, new key store, sandbox, service, workflow or ledger was started.

### Remaining work and summary

Paused, not complete: equivalent focused-test reduction; adapter terminal/provider/audit closure (F1/F2/F3/F9); treatment terminal telemetry and pinned-arm evaluation (F4/F7); measurement integrity (F6); blind/inline projection (F8/F12); missing-input/re-entry diagnostics (F10/F11); and their actual regressions. Existing CI sequence issue F14 remains unresolved; no timing history or Captain-owned precondition was rewritten. F5 outer retry remains unassigned/disproved, F13 remains conditional, and all other unverified questions retain their original disposition.

Only the counting approval and this evidence report were changed in task state. No product edits, new tests in product, paid review/model, browser probing, new render, RoboRev retry, publication, gate/status/pin or branch changes occurred. The prior stage's passing tests are historical evidence, not proof of these still-open repairs. Product work stops pending the Captain-owned route decision; the retained worker remains addressable.

## Accepted bounded isolation feasibility validation

Captain replied `確認` to: `目前尚未縮減或修復：已實測受測程序能修改前一筆耗時，彙整器仍接受；搬目錄或設唯讀都擋不住。依 kc-dev-flow:chief-engineer（交付建議）的範圍界線，建議先驗證最小隔離方案，讓受測程序無法寫入正式量測紀錄。是否同意這項限定路線調整？行數上限不變，不新增常駐服務，也不啟動付費盲測。`

This permits one bounded local synthetic feasibility proof of an enforced owner/child write boundary using an already-installed local OS/sandbox primitive. It does not authorize product integration, package installation/update, a new user, sudo, global configuration, image pull, daemon/service, independent ledger/telemetry owner, remote/cloud/model call or a weakened child threat. Experiments use one owned disposable directory and synthetic paths only, retaining Bash workspace work and testing current/prior records, alternate paths, descendants, parent finalization and an unisolated negative control. Residual IPC/proxy/process-memory/daemon and real-auth compatibility risks must be explicit.

Product HEAD remains `9bb526170156a44cff90e2a2fab9eeab081e0eb1` on `feature/kc-pr-review-capability-protocol-pilot`; no product edit/commit/rebase/push is permitted in this feasibility step. Stops remain 6,600 total / 20 paths / 1,800 complete focused lines, and the current 1,939 focused count is still unpassed. All five repair groups, reduction, F14 sequence evidence, fresh independent review and budget-gated AC8/9 remain pending. Existing rejected reports, status, pin and review round remain unchanged; the historical canonical-format deferral is not extended. This approval is committed/synced and reread before experimentation; findings return to the First Officer as a minimal integration shape or an exact feasibility blocker, not shipped code.

## Stage Report: implementation (cycle 5)

- DONE: Record and reread the Captain-approved bounded isolation-route validation in the existing task before any experiment, preserving the accepted outcome, complete counting denominator, limits and historical state.
  Approval `087047c577d4f58003f6833478c345c50f7b377e` was supported-committed/synced/reread before the first local sandbox execution; no product or status/pin changes.
- DONE: Use an existing local enforcement primitive to prove, with synthetic fixtures and a failing unisolated control, that the measured Bash child and its descendants cannot alter authoritative current or previous measurement records while normal workspace work and runner-owned recording still succeed.
  [Bounded filesystem evidence](isolation-feasibility/report.md): unisolated control fails; sandbox-only hard-link bypass retained as a failure; guarded alias/normal/nonzero/timeout instrument passes four cases through actual runner finalization/join. Direct/traversal/symlink/new-link/rename/unlink and detached-descendant writes receive EPERM; normal Bash/work/output/temp and parent writing succeed. Existing aliases are refused before launch, not silently repaired.
- DONE: Commit a concise evidence-backed minimal integration proposal or exact blocker, with lifecycle/surface mapping, platform and compatibility limits, and estimated counts; leave product unchanged and return to FO without paid work or self-advancement.
  Proposal reuses the existing launch/measurement owner but is NOT integrated; macOS-deprecated primitive, real host/auth, IPC/proxy/process-memory and portability premises remain unproven. Current 6,431 / 20 / 1,939 is unchanged. Mapped reduction 85–121 versus 80–120 new focused tests does not establish an 1,800-line fit, even before other repairs.

### Summary

The specifically measured filesystem boundary is feasible locally with native enforced policy plus a prelaunch alias check; it is not yet a sufficient full review-host isolation result or a repaired F6. All five product repairs, reduction, F14 sequence evidence, fresh review and paid outcome evidence remain pending, and the First Officer receives the exact residuals and count gap before any product-integration decision. No dependency, global configuration, user, daemon, service, ledger, paid model, browser, product commit, publication or stage/gate mutation occurred.

## Stage Report: implementation (cycle 6)

- DONE: Record and reread the Captain-approved bounded isolation-route validation in the existing task before any experiment, preserving the accepted outcome, complete counting denominator, limits and historical state.
  Reused and reread exact approval `087047c577d4f58003f6833478c345c50f7b377e` under the First Officer's one-existing-tool alternative assignment; no new approval, status, pin or route inferred. Native report `c7673f29` is preserved.
- FAILED: Use an existing local enforcement primitive to prove, with synthetic fixtures and a failing unisolated control, that the measured Bash child and its descendants cannot alter authoritative current or previous measurement records while normal workspace work and runner-owned recording still succeed.
  [Safehouse alternative evidence](safehouse-alternative/report.md): exact owner deny blocks direct/alias/new-link/internal rename/unlink and detached descendant writes, but a parent-directory rename/write/restore bypass succeeds and real join accepts the forged earlier 1-ms record. Strict instrument exits 1; no further patch or auth probe followed this concrete stop condition.
- DONE: Commit a concise evidence-backed minimal integration proposal or exact blocker, with lifecycle/surface mapping, platform and compatibility limits, and estimated counts; leave product unchanged and return to FO without paid work or self-advancement.
  Report includes effective generated policy, failed startup-binding trial explicitly excluded from pass evidence, actual attack result, existing-owner-only necessary condition and provisional 70–120 code / 90–140 test estimate. Mapped reduction is insufficient to promise 1,800; Claude startup/auth/provider compatibility remain NOT RUN, not failed or passed.

### Summary

The single existing-tool alternative is insufficient as configured: broad temporary-directory writes defeat an exact owner-tree path deny through ancestor rename. Product remains clean and unchanged at `9bb52617`, counts remain 6,431 / 20 / 1,939, and all original repairs/count/CI-sequence/paid-outcome obligations remain pending. No installation, settings mutation, credential disclosure, real host/model call, new standing component, product integration or self-advancement occurred.

## Stage Report: implementation (cycle 7)

- DONE: Record and reread the Captain-approved bounded isolation-route validation in the existing task before any experiment, preserving the accepted outcome, complete counting denominator, limits and historical state.
  Reused and reread approval `087047c577d4f58003f6833478c345c50f7b377e` under the First Officer's final existing-container assignment; no new Captain approval inferred. Earlier native and Safehouse results are preserved.
- DONE: Use an existing local enforcement primitive to prove, with synthetic fixtures and a failing unisolated control, that the measured Bash child and its descendants cannot alter authoritative current or previous measurement records while normal workspace work and runner-owned recording still succeed.
  [Container proof](container-feasibility/report.md): corrected five-case instrument exits 0 in 7.011 seconds; prior unisolated failure retained. Existing hardlink/symlink inputs refuse before launch; nine owner-write routes plus an independently grouped live descendant are denied, normal work succeeds, actual parent finalization/join accepts unchanged prior measurements. Exit 7 and timeout record incomplete failures and join refuses. Exact CID/label cleanup proves no owned container remains, including the timeout container observed running after CLI kill. Initial error-message parser failure is retained, not green.
- DONE: Commit a concise evidence-backed minimal integration proposal or exact blocker, with lifecycle/surface mapping, platform and compatibility limits, and estimated counts; leave product unchanged and return to FO without paid work or self-advancement.
  State-only report/inputs/raw results record immutable image, mount topology, cleanup identity, synthetic-only costs, new Docker/image/container lifecycle obligations and unproven real-model compatibility. Low focused estimate after maximum mapped savings is 1,928, still 128 over 1,800 before other repairs; no fit or product-integration approval claimed.

### Summary

The bounded local filesystem/process and container-cleanup proof passed; it does not complete the Pilot implementation or establish an approved/cap-compliant real-model runtime. Product remains clean at `9bb526170156a44cff90e2a2fab9eeab081e0eb1`, counts 6,431 / 20 / 1,939 with unchanged 6,600 / 20 / 1,800 stops; all five repairs, reduction, F14, fresh review and AC8/9 remain pending. No product edit, model/auth request, image change, new standing service, gate/status/pin/PR action or additional alternative was performed; the First Officer receives the next route decision.

## Accepted bounded cloud-workspace feasibility preflight

Captain asked why Docker rather than a cloud workspace. The First Officer clarified that Docker was only the already-authorized local synthetic proof, not a required product dependency, and proposed validating an existing Conductor cloud configuration with the measured agent inside its own workspace and all authoritative measurement outside it: external timing/records, no RunLocalCommand/local-command privilege or credentials capable of modifying controller records, and real completion/timeout/cleanup verification. Captain explicitly replied: `確認，就這樣驗證`.

This accepts bounded cloud-workspace feasibility validation instead of Docker product integration, not a product dependency/route adoption. It permits owned disposable cloud execution with synthetic inputs, not a paid real-PR blind batch, new standing service, global/org/settings changes, image/tool installation, product push/PR/merge or review-speed claim. No measured-dollar model budget is inferred; existing paid-model limits remain in force. Prefer a supported no-model terminal path; if any model call is necessary, return the exact minimum and cost/authorization gap before launch.

The current dispatched step stops at preflight: record/sync/reread this approval and prepare only synthetic inputs, with no cloud creation, messaging, execution or model session. A terminal filesystem proof cannot certify agent-specific RunLocalCommand/MCP restrictions; missing tool-inventory evidence remains unverified. All cloud-returned bytes are untrusted; authoritative elapsed time and canary bytes stay with the local controller outside synced workspaces. Session cancel or archive status alone cannot prove descendant termination.

Product remains unchanged at rejected `9bb526170156a44cff90e2a2fab9eeab081e0eb1` on `feature/kc-pr-review-capability-protocol-pilot`, cumulative base `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`; actual counts 6,431 / 20 / 1,939 and limits 6,600 / 20 / 1,800 remain unchanged. Preserve stage/status/pin/review round and native, Safehouse and container reports including failures. All five original repair groups, focused reduction, F14 sequence and real quality/speed evidence remain pending. The supported state prerequisite must pass, then this approval is committed/synced and reread before synthetic preparation.

## Stage Report: implementation (cycle 8)

- DONE: Record and reread the exact Captain-approved cloud-workspace feasibility scope, preserving product, limits, rejected stage, historical pin and earlier evidence.
  Supported prerequisite exited 0; approval `87940eae3dae61a041949208a7d6e3360fd4f6f1` was committed/synced/reread before preparing synthetic inputs. No product/status/pin change.
- DONE: Resolve the real cloud execution, permission and external-measurement surfaces without starting a model or changing settings; return one bounded executable probe plan or a concrete preflight blocker.
  [Preflight report](cloud-preflight/report.md) records FO's native-UI startup failure and no terminal executor in public API/MCP; supported no-model execution, effective agent permissions and terminal/workspace termination evidence are unavailable/unverified. This is a concrete execution preflight blocker, not CLOUD_ISOLATION_FAILED. The minimum model-session alternative has no demonstrated dollar cap and was not launched.
- DONE: Prepare only owned synthetic proof inputs and report the ready-to-run commands, exact targets, lifecycle cleanup and cost/authorization limits to FO before any cloud creation or execution.
  One Bash/Python payload syntax-checks without execution; exact local canary hash and absent-current target are recorded outside sync. Normal/exit-7/5-second external-timeout commands are conditional on a verified terminal and exact owned workspace; no unsupported API, cloud write or model was used. External timing/canary authority and unresolved descendant/agent-tool evidence are explicit.

### Summary

Cloud preflight and synthetic input preparation are complete, but no cloud isolation run or model request occurred. Product remains clean at `9bb52617`, counts and limits unchanged; no cloud-execution-ready claim, full implementation completion or workflow advancement is made. FO receives the supported-execution and billing/permission gaps before any launch.

## Accepted one-off cloud agent synthetic attempt

Captain replied `確認` to the exact question: `是否批准一次 Claude Opus 5、中等推理、最多 5 分鐘、無重試的合成測試？費用尚未量測，不含正式 PR 盲測。` The preceding explanation explicitly stated that the Conductor API has no hard-dollar cap. This is one bounded feasibility/model-usage exception, not a real-PR blind budget, known per-PR cost, zero-charge promise or new dollar ceiling.

Execute at most one new workspace, its initial session and one initial user message in approved project `8f58f9d4-cb71-443a-b64d-c2a225248c7b`, specifying `claude` / `opus-5-1m` / `medium`, no fast mode. No follow-up prompt, retry, fallback provider, remote subagent or real repository review. Setup is separately bounded at 180 seconds; message submission begins a 300-second externally monitored model-attempt window, including queue/tools, with cancellation control-call margin. Requested stop and actual observed stop remain distinct; local deadlines cannot guarantee a remote hard stop.

Local controller/canary/monitor/raw timing remain outside all synced workspaces. Only exact synthetic attack targets and fixture bytes may enter the prompt. Stop on a concrete local-command bridge or measurement-write falsifier; absent trusted agent-tool/credential inventory remains unverified. Preserve raw evidence, cancel if needed and recoverably archive only the exact owned workspace after identity readback on every exit; archive state is not independent descendant termination proof. No secrets/settings/install/product/branch/PR/stage/status/pin/gate/review-round change is permitted.

Product stays clean at rejected `9bb526170156a44cff90e2a2fab9eeab081e0eb1` on `feature/kc-pr-review-capability-protocol-pilot`; cumulative base `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`, actual 6,431 / 20 / 1,939 and limits 6,600 / 20 / 1,800 are unchanged. Earlier proofs/failures and all five repair groups, reduction, F14 and real quality/speed evidence remain pending. This approval is supported-committed/synced/reread before cloud creation or any model message.

## Stage Report: implementation (cycle 9)

- DONE: Record, sync and reread the exact Captain approval for one Claude Opus 5 medium cloud synthetic test, maximum five minutes and no retry, without inventing a dollar ceiling.
  Approval `f268b348fd4acb408a832f72bb5f9a3ef0bd2e9f` was durable/reread before the one workspace/session/message; exact Opus/medium/off request and external deadline recorded, no dollar cap inferred.
- DONE: Execute that one bounded cloud attempt with external authoritative timing/canaries and actual tool, exit, failure, timeout evidence where available; stop on a concrete isolation falsifier and do not change settings or product.
  [Attempt report](cloud-once/report.md): three Bash cases and unchanged actual external canaries; normal and tool timeout positive, nonzero outer exit masked, complete bridge/credential exclusion unverified. Provider turn completed, not whole-proof PASS. SDK list-based cost $0.483311 includes extra provider-reported Haiku, not worker fallback or invoiced spend; no retry.
- DONE: Preserve raw evidence, cancel/archive only the owned cloud workspace on every path, read back its terminal lifecycle and record precise pass/fail/unverified findings and remaining integration limits in the existing task.
  Sanitized raw events and failed monitor preserved. Transcript JSON parse failure also interrupted monitor cleanup; independent exact-identity archive recovery timed out locally but subsequent workspace get/status confirm archived and session idle. Terminal tail recovered read-only; monitor PID absent. Descendant termination and general external-deadline/all-error-path robustness remain unverified.

### Summary

The one authorized attempt is over and its exact workspace is recoverably archived; no new inference, product work or workflow advancement followed it. Product remains clean at `9bb52617`, count/limit unchanged; partial filesystem evidence does not resolve the remaining permission, nonzero, controller-lifecycle or product obligations. The First Officer receives the failures and limits, not an integration or speed/fit recommendation.

## Accepted local monitor and exit-code repair only

Captain replied `批准` to the exact recommendation/question: `建議保留雲端方向。是否批准先修正本地監控腳本與退出碼檢查，不啟動下一次雲端測試、不修改產品？` This permits only a small state-owned diagnostic revision and bounded local synthetic tests; it does not authorize another cloud run, real PR batch, product isolation integration or the original five repairs.

Preserve the original cloud-once monitor, prompt, reports and failures byte-identically. The new revision uses structurally fake-only injected transport/clock and owned local scratch; no real Conductor/API/model command, cloud create/start/unarchive/message/cancel/archive, settings, networked experiment, installation or reviewer. Local checks must reproduce malformed JSON and cleanup coupling, retain precise failure/unknown outcomes and exact structured identity checks, preserve child exit codes and return a nonzero controller result for failed/incomplete observations. Idle alone is not terminal proof. Cloud tool/credential exclusion, live deadline/descendant termination and whole-cloud proof remain unverified.

Product remains clean at rejected `9bb526170156a44cff90e2a2fab9eeab081e0eb1` on `feature/kc-pr-review-capability-protocol-pilot`, base `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`; counts 6,431 / 20 / 1,939 and limits 6,600 / 20 / 1,800 are unchanged. Existing stage/status/pin/gate/review round and historical evidence remain unchanged, with all original repairs, focused reduction, F14 and real speed/quality pending. Preserve unrelated holder files and peer state. This approval is supported-committed/synced/reread before implementation; no new cloud/model cost is authorized.

## Stage Report: implementation (cycle 10)

- DONE: Record, sync and reread the exact Captain approval for local monitor/exit-code repairs only, preserving all historical evidence and product/workflow boundaries.
  Approval `dec0f52dff489381da1dc5c6f6b71677931ff7cd` was durable/reread before edits. Original cloud-once tree is byte-identical to `bcc53147`; no product/frontmatter/pin change.
- DONE: Reproduce and repair malformed transcript handling, cleanup independence, and actual nonzero propagation using only bounded local synthetic tests that cannot invoke a real cloud or model command.
  [Local repair evidence](cloud-local-repair/report.md): old behavior RED 4 tests (3 failures/1 error), nested null/list RED four errors, frozen-start RED three failures; final GREEN 19 tests in 0.333 s (wall 0.47 s). Same revised command/core path uses injected fakes with real subprocess blocked; dormant live construction/default entrypoint refuses. Exact identity, independent cleanup, frozen caller timing/canary, classified malformed/timeout outcomes, terminal requirement and actual shell/controller exit status are exercised.
- DONE: Commit the state-only revision and complete test evidence; distinguish local fixes from unproven live isolation/deadline/descendant guarantees and return with product and historical pin unchanged.
  State-only revision/logs/report preserve failures and local proof; no Conductor/API/model command, retest, cloud mutation, product integration or reviewer. Existing cloud archive is historical, not freshly observed. Product remains clean `9bb52617`, counts 6,431 / 20 / 1,939 and original obligations unchanged.

### Summary

Local monitor and exit-code repairs are complete for FO inspection, not a full cloud/product PASS. FO clarified that tests must use fake execution against the same dormant production adapter/core rather than maintain a separate simulation; this revision follows that boundary without a live creation/submission entrypoint. Real permissions, external remote deadline, descendant termination and all original product/quality/speed work remain pending; no self-advancement or cloud retest follows.

## Accepted single cloud follow-up

Captain replied `批准` to this exact proposal: `建議只補一輪雲端測試，驗證真實退出碼、外部停止與歸檔：一個工作區、一次 Claude Opus 5 中等推理，準備最多 3 分鐘、執行最多 5 分鐘、無重試、不跑 PR。上次用量回報約 US$0.48，僅供參考，沒有美元硬上限；無法觀測的權限與子程序證據仍不能算通過。是否批准這一輪限定補測？`

This authorizes exactly one additional synthetic cloud workspace, its initial session and one initial message, explicitly `claude` / `opus-5-1m` / `medium`, fast mode off; no retry/fallback/subagent, real PR review, ongoing budget or dollar ceiling. All local deterministic preparation precedes creation. Setup from create to observed ready/model binding is bounded at 180 seconds; the model window is frozen before submission at submission monotonic + 300 seconds, including queue/transport/tools. Use the unchanged repaired monitor SHA-256 `54d55e640c85b7957173cc3b66a23751fe3be2d515389265669447a82c8f890b` with caller-frozen canary hash/times and only bounded one-run outside-sync glue. Arm independent failure cleanup before the sole message. Stop on a concrete bridge/canary falsifier; no permission grants or credential injection.

Normal and intended exit-7 evidence must retain actual outer shell status. A lightweight finite waiting workload may be deliberately interrupted while active to exercise the existing external cancellation/archive path; canceled/incomplete monitor status is not relabeled as a review success. Exact-owned cancellation/archive/readbacks remain bounded with unknown responses preserved and no blind mutation retries. Provider lifecycle does not prove descendant death; missing authority evidence remains unverified. Preserve old cloud workspace/session and all historical cloud-once/cloud-local-repair bytes; no unarchive, second message or additional experiment.

The retained author remains sole execution/report owner (FO corrected only the generated fresh-owner premise). Product stays clean at rejected `9bb526170156a44cff90e2a2fab9eeab081e0eb1` on `feature/kc-pr-review-capability-protocol-pilot`, base `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`; actual 6,431 / 20 / 1,939 and limits 6,600 / 20 / 1,800 unchanged. Status remains held validation; no product/branch/PR/settings/install/CI/gate/status/pin/review-round or original-repair changes. This approval is supported-committed/synced/reread before cloud creation or model work. FO owns the next decision after the single attempt and durable cleanup report.

## Stage Report: implementation (cycle 11)

- DONE: Record, sync and reread the exact Captain approval and freeze one owned cloud attempt, model, setup/execution bounds and external evidence before launch.
  Approval `1e32bb69a198002f25853d66e56f528e4c8a746c` durable/reread before one exact workspace/session/message; Opus 5 medium, 9.311-second setup, caller-frozen 300-second deadline/canary and independent cleanup armed before submission.
- DONE: Run one synthetic cloud request using the repaired monitor and real raw exits; exercise external stop while work is observed active, with no retry or product change.
  [Follow-up report](cloud-followup/report.md): raw normal success and genuine exit-7 error, pending third Bash plus working status before cancel, then exact idle/archived before deadline. Immutable core returns `deadline_incomplete`/1; no successful model-turn or whole-isolation claim.
- DONE: Preserve evidence and cost, read back exact owned cleanup, separate pass/fail/unverified conclusions, commit the state-only report and stop.
  Sanitized raw/manifest retain archive timeout as unknown followed by archived readback; local canary unchanged/current absent, both controller PIDs gone. No SDK result/cost receipt or direct descendant proof, so neither is invented; prior evidence/product/status/pin preserved.

### Summary

The single authorized follow-up completed its bounded execution/reporting checklist (3 DONE / 0 SKIPPED / 0 FAILED), not a full cloud/product proof. Actual error propagation and external active-to-idle/archive lifecycle are now observed; archive call uncertainty, missing descendant/authority/cost evidence and all original product obligations remain explicit. Product stays clean at `9bb52617`, counts 6,431 / 20 / 1,939 unchanged; no retry, additional inference or self-advancement follows.

## Accepted one-batch local correction and pin exception

Captain's exact instruction: `1. 先開一張票。然後按照建議採一次性的、明確記錄的流程例外`. The upstream defect was filed first and independently reread OPEN: [issue 382 — stage pins block report updates and authorized feedback re-entry](https://github.com/iamcxa/kc-claude-plugins/issues/382). No duplicate ticket or upstream implementation belongs to this batch.

The accepted exception waives only the pre-dispatch stage-pin rebinding check for ONE retained-author local correction batch. Historical `stage-pin.json` remains byte-identical, SHA-256 `8dbc54e264711a9d9da98a160726a3a9b4f846bed2d4e4b23196581fb5c67ea8`, attempt `validation-1`, installed kc-dev-flow 4.1.1 digest `e6f51ce2b017a3252be4a9541252309fd9ccb480f30d7979b9b6a980aa4b7f80`. No replacement pin, loader patch, process upgrade, forged validation, status/gate/review-round change or reinterpretation of rejected evidence is authorized. Normal state/product ownership rules remain effective.

Earlier Captain `批准範圍修復` authorizes equivalent complete-focused-test reduction and the four independent existing-owner groups recorded in `validation-9bb52617/reverification.md`: adapter terminal/provider/audit closure (F1/F2/F3/F9); terminal telemetry and frozen-arm evaluation (F4/F7); blind-label and ambiguous inline projection (F8/F12); existing CLI input/re-entry diagnostics (F10/F11). Preserve minted identity and exact dispositions, raw attempts and available/unknown incurred cost, pre-spend arm binding, closed blind vocabulary, unambiguous provenance, named refusals and sealed bytes. Each distinct failing shape requires actual failing-then-passing behavior, not schema-only claims.

Measurement integrity (F6) remains a genuine BLOCKER: same-authority arbitrary Bash rewrote runner measurement and join accepted a planted 1 ms record. It is not waived, passed, accepted red or deferred to success. No isolation integration, new authority store, sandbox, ledger, cloud attempt or credential redesign is authorized. Outer retry (F5) is not a required repair; conditional environment hardening (F13), historical CI sequence (F14), unmeasured hosted incremental cost and real paid quality/speed evidence remain as previously classified. Earlier five-group proposals and rejected reports are not rewritten as satisfied. The historical canonical review-format deferral is not a blanket waiver.

Product starts clean at `9bb526170156a44cff90e2a2fab9eeab081e0eb1` on `feature/kc-pr-review-capability-protocol-pilot`, worktree `/Users/kent/conductor/workspaces/kc-claude-plugins/kc-pr-review-capability-pilot`; cumulative base `3b37000a16ca2eadad0cb5dfd8e43a5f1d06f0f8`. Starting counts 6,431 total / 20 files / 1,939 complete focused; unchanged limits 6,600 / 20 / 1,800 include shell-hosted tests and new regressions. The approved reduction must eliminate the actual 139 focused excess plus added tests without moving tests outside the denominator, weakening falsifiers, minifying, raising limits or changing scope. Preserve default-off executable Lite, zero executable expansion, documented-only other profiles, planner-before-selected-evidence, confirmation/posting ownership and all unmet accepted obligations. No new surface, dependency, CI lane/trigger widening, standing service or product rebase/retarget.

This standalone admitted brief has no Planning Receipt; do not reconcile Linear, migrate authority or replace historical headings. Preserve held validation, peer state and unrelated holder files. Load installed shared kernel/Pilot base/build; apply triggered documentation and bound project-context obligations only. The explicit bounded assignment does NOT perform implementation-exit reviewer observation: record NOT PERFORMED, never passed. No review submission/model request, paid evaluation, cloud activity, product push, PR, merge, release or gate consumption is authorized.

This approval must be supported-committed, synced and reread with the unchanged historical pin; the retained author sends the checkpoint to FO and waits for FO confirmation before product edits. After confirmation, complete only the local correction/count/test/report batch. The exception expires on return of that local report, including an incomplete/blocker report; wider Pilot sufficiency and the five-pair real quality/33.3-percent-speed criteria remain unproven.

## Stage Report: implementation (cycle 12)

- DONE: Record the Captain-approved one-batch pin exception and existing four-group repair/reduction approval in the original task; commit, sync and reread it, preserve the historical pin and rejected evidence, then send FO the durable commit and wait for FO readback confirmation before product edits.
  Approval `dab22663d8500df0b8c11ab48087ab27c3679771` was synced/reread and independently confirmed by FO before product edits; historical pin and rejected evidence remain unchanged.
- FAILED: After FO confirmation, equivalently reduce the complete focused footprint and repair only the four assigned existing-owner groups with actual failing-then-passing regressions, within 6600 total changed lines, 20 product files and 1800 complete focused lines including all new regression tests.
  Four local repair groups have RED/GREEN evidence, but final **6,443 / 20 / 1,903** remains **103 focused lines over**; [exact counts and patch](local-correction/counts.json), [finding evidence](local-correction/red-green.md). No fit or completed-candidate claim.
- DONE: Return one exact-head local repair report with checklist accounting, actual verification and complete count evidence, addressed/unresolved findings and explicit exception expiry; preserve held validation and remaining blockers, with no review, paid/cloud call, push, PR, merge, release, stage/gate/pin change or unrelated edits.
  [Local report](local-correction/report.md) binds unchanged HEAD `9bb526170156a44cff90e2a2fab9eeab081e0eb1` plus uncommitted six-path patch SHA-256 `fa9108f8bb0646139be7a8e222daeaa1a990d732706af6702d835931c779ee1e`; state-only report is committed/synced, product remains dirty and unpushed. Exception expires on this report's return.

### Summary

Checklist: **2 DONE / 0 SKIPPED / 1 FAILED**. Final local protocol suite **25 OK / 434.47 s wall**, full ablation **83 passed / 0 failed / 57.73 s wall**; five removal mutations reproduce missing-input and sealed re-entry failures, with full raw suite/mutation output preserved. The protocol regressions fail on lost minted identity, unrecorded malformed attempts, wrong configuration terminal, success-only terminal telemetry, sibling-arm loading or guessed duplicate quote; shell regressions fail on leaked blind labels, unnamed input/re-entry errors or overwritten sealed bytes.

Equivalent in-file reduction retained assertions but did not meet the unchanged cap; no further redesign or product commit is claimed. F6 measurement integrity remains BLOCKING, F14 and hosted incremental cost remain unresolved/unmeasured, and real five-pair quality/speed remains unproven; implementation-exit observation was NOT PERFORMED. Held validation and historical pin remain unchanged, bound project-context impact is none with fresh validation pending, and this one-time exception is exhausted by the incomplete report.
