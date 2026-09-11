---
title: "fix(kc-dev-flow): explain the next commitment during profile selection"
status: validation
product: kc-dev-flow
sprint: S7
sprint-readiness: ready
issue: iamcxa/kc-claude-plugins#393
provenance: https://github.com/iamcxa/kc-claude-plugins/issues/393
id: td0yhsww2jnwnrzh5c6wc6er
started: 2026-09-10T09:09:39Z
gates:
    version: 1
    records:
        - id: gate:td0yhsww2jnwnrzh5c6wc6er:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:td0yhsww2jnwnrzh5c6wc6er-backlog-1
              briefing:
                id: briefing:td0yhsww2jnwnrzh5c6wc6er:backlog:attempt-1:revision-1
                digest: sha256:68a25b098d6ffe011b12240fa4392e022eda7c5dbe98d22b3c51707a37c2872f
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:td0yhsww2jnwnrzh5c6wc6er:backlog:1
                briefing: briefing:td0yhsww2jnwnrzh5c6wc6er:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T09:12:02.999076Z"
                decision: approve
                reason: Captain Kent approved these issue repairs with "確認，就這樣交付" and selected Pilot for both with "Pilot可以". This initial admission records that existing scope/profile decision after publishing its administrative brief; it grants shape only and does not claim approval of a later implementation or future evidence.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:td0yhsww2jnwnrzh5c6wc6er:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:td0yhsww2jnwnrzh5c6wc6er-ideation-1
              briefing:
                id: briefing:td0yhsww2jnwnrzh5c6wc6er:ideation:attempt-1:revision-1
                digest: sha256:611a93f369240be4d07e9acec25eb12220a6b39a5ed16627aacf16c2e47b522f
                room-ref: ./review/ideation/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-09-10T09:23:51.845042Z"
                reason: Structured acceptance scan cannot locate AC-2, AC-3, or AC-4 in the report projection. The evidence exists below the Summary section but must be repaired by its report owner before a review can be presented; accepted scope is unchanged.
            - id: gate-attempt:td0yhsww2jnwnrzh5c6wc6er-ideation-2
              briefing:
                id: briefing:td0yhsww2jnwnrzh5c6wc6er:ideation:attempt-2:revision-1
                digest: sha256:59133c34c0735bc13868d806761ba1c6eab7267aa071df4bcee53dd34af2a55e
                room-ref: ./review/ideation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:td0yhsww2jnwnrzh5c6wc6er:ideation:2
                briefing: briefing:td0yhsww2jnwnrzh5c6wc6er:ideation:attempt-2:revision-1
                by: person:captain
                at: "2026-09-10T09:37:49.025289Z"
                decision: approve
                reason: Captain Kent replied "批准" to the presented two-item ideation review, including this task snapshot 59133c34. Accept the three-file design and enter implementation; new model spend remains separately reserved.
              application:
                target-stage: implementation
                state: consumed
        - id: gate:td0yhsww2jnwnrzh5c6wc6er:validation
          stage: validation
          attempts:
            - id: gate-attempt:td0yhsww2jnwnrzh5c6wc6er-validation-1
              briefing:
                id: briefing:td0yhsww2jnwnrzh5c6wc6er:validation:attempt-1:revision-1
                digest: sha256:00f3031ccf91ead6ed40ca3655e26c5141a386e7a3d5c832e290075d281b4643
                room-ref: ./review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:td0yhsww2jnwnrzh5c6wc6er:validation:1
                briefing: briefing:td0yhsww2jnwnrzh5c6wc6er:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-11T10:40:43.506561Z"
                decision: approve
                reason: 'Captain said 合併了 after reviewing the Ready delivery and personally merged PR #425 as iamcxa at 2026-09-11T10:36:31Z. Record this observed acceptance now for post-merge reconciliation; do not backdate approval. Exact reviewed head, required checks, and complete feedback observation match.'
              application:
                target-stage: done
                state: pending
worktree: .worktrees/spacedock-ensign-issue-393-profile-commitment-explanation
pr: pr-merge:425
---

The existing selection conversation explains this item's next commitment, unresolved assumption, observable result, and included operational duties before the Captain chooses. Its existing profile receipt preserves that accepted scope.

## Development Brief

### Problem

Profile selection can be understood as project scaffolding while the operator accepts hosted operations and recovery. The existing question about negative evidence is too abstract when the first real journey is unproved.

### Accepted outcome

The existing selection conversation explains this item's next commitment, unresolved assumption, observable result, and included operational duties before the Captain chooses. Its existing profile receipt preserves that accepted scope.

### Non-goals

- No new profile, receipt schema, workflow stage, approval gate, standing audit, or mandatory sequence of profiles.
- No operational deployment, credential use, data migration, rewrite of existing records, or retrospective relabeling of completed work.
- No self-improvement collector or new POC experiment; no change to the originating product.

### Route-back conditions

Return to the Captain if the correction requires new operational responsibility, a consumer migration, a new receipt/schema or gate, broader product work, or a behavioral proof method requiring unapproved external spend.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: "A bounded retained plugin-guidance repair for existing users, with no new operational duties or migration. Consumers can take the new version without rewriting their state."
  route: [shape, build, verify-deliver]
  obligations:
    architecture: ["Preserve the existing selection conversation and profile receipt as the authority; distinguish future product ambition from the accepted next commitment."]
    implementation: ["Revise the smallest necessary selection wording, examples, and existing receipt handoff; consumers upgrade by taking the new version without a migration."]
    testing: ["Exercise unproved integration, scaffolding, explicit operated release, and existing-consumer cases with falsifiable evidence; retain instruction and contract checks."]
  scope_boundary: "Only the accepted issue correction and its necessary evidence; no new operating commitment, workflow machinery, consumer migration, or new experiment."
  promote_when:
    - "A consumer must migrate, reconfigure, or rewrite records to upgrade."
    - "The scope accepts production data, destructive mutation, unattended operations, or new recovery/support responsibilities."
  decision:
    authority: "Captain Kent"
    at: "2026-09-10T09:06:26.340161Z"
```

The decision timestamp is capture time. In this Kathmandu session the Captain approved the maintenance delivery sequence with "確認，就這樣交付", then explicitly selected Pilot for both issue #393 and issue #396 with "Pilot可以". This records those scope and profile decisions, not review of a later implementation. The GitHub issue is provenance; this standalone brief has no Planning Receipt or provider scheduling claim.

## Acceptance criteria

- **AC-1**: The recommendation states the next commitment, unresolved assumption, observable result, and concrete included work; it distinguishes scaffolding, a disposable integrated experiment, limited real use, and an operated release.
- **AC-2**: When the first user journey is unproved and Production is recommended, the explanation offers the smallest lower-commitment alternative and identifies the evidence or explicit operational duty that makes it insufficient.
- **AC-3**: Existing valued state and consumers are distinguished from state an experiment might create; a new repository neither forces POC nor justifies Production by itself.
- **AC-4**: The Captain's accepted scope carries into the existing profile receipt, and a misunderstood or unanswered scope stays unresolved instead of becoming an automatic selection or retrospective success claim.
- **AC-5**: Representative scenario evidence tests both lower-commitment and valid Production cases; affected existing contract and instruction-budget checks pass, with no additional standing process or consumer migration.

## Stage Report: ideation

- DONE: Define one bounded accepted journey and its real program/file seams, non-goals, state boundaries and applicable context-policy receipts. Shape evidence: AC-1 specifies commitment, assumption, observable result and included work (Journey step 2); AC-2 specifies the lower alternative and the evidence or operational duty it cannot cover (step 3); AC-3 distinguishes existing valued state/consumers from disposable experiment output and rejects repository-age routing (steps 1 and 3). These are designed behaviors, not observed acceptance.
  The journey and policy dispositions below repair the named selection seam using existing programs, receipt fields, and authorities; no new standing process is proposed.
- DONE: Trace AC-1 through AC-5 to concrete falsifiable implementation and verification steps, with no new standing process or unsupported behavior claim. Shape evidence: AC-4 maps accepted scope into existing receipt fields and keeps misunderstanding, no answer and interruption unresolved (Journey steps 4-5). The Falsifiable acceptance and proof proposal section maps AC-1, AC-2, AC-3, AC-4 and AC-5 to six concrete cases, including unchanged-receipt readback and both lower-commitment and valid Production responses; implementation and behavioral proof remain pending.
  The six cases and fixed baseline/candidate exercise below are design obligations; no implementation acceptance or operator-behavior pass is claimed.
- DONE: Measure the proposed file surface and instruction-budget pressure, set stop numbers, and durably report one sufficient implementation route after the FO grants the state-write slot. Shape evidence: AC-5 uses the three measured proposed files in Where it touches and stop numbers, retains existing contract checks and the 40,000-byte limit (observed source maximum 39,991), and proposes the bounded baseline/candidate exercise in Falsifiable acceptance and proof proposal. This proves measured shape feasibility, not implementation acceptance; no new standing process or consumer migration is proposed.
  Source base c2c62bf9dff5c3af1e27eb643a15eadf9023485f was clean main; source gate measurement returned maximum 39,991 / 40,000 bytes. This report is recorded after the FO's serialized write grant.

### Summary

One sufficient route replaces the abstract opening of the existing chooser with a concrete explanation of the next accepted commitment, then carries the answer through the existing receipt. Retain the existing production boundaries, stale-receipt handling, admission rules, and transaction readback; reuse the scenario file and contract test, with no new runtime, profile, receipt field, tool, reviewer, or gate. Implementation and behavioral evidence remain pending.
### Journey, semantics, and state

1. **DESIGNED:** The existing Claude or Codex host executing `kc-dev-flow/skills/choose-work-profile/SKILL.md` reads the exact work item and `Work profile receipt`; it reuses a supported unchanged choice, and treats changed scope or an unconfirmed interpretation as unresolved. Repository age is context, not a selection rule.
2. **DESIGNED:** Before the existing Ask UI or plain-chat question, that host states this item's next commitment, unresolved assumption, observable result, and included work in task terms. It distinguishes repository scaffolding (files exist; integration unproved), a disposable integrated experiment (one real journey decides an uncertainty), limited real use (accepted valuable state and iteration), and an operated release (named data, recovery, support, release/rollback or other accepted operational duties). Scaffolding is neither a fourth profile nor proof of the first journey; future product ambition is not the current commitment.
3. **DESIGNED:** If the first user journey is unproved and the host recommends Production, its same explanation offers the smallest sufficient lower-commitment alternative and names the evidence or explicit operational duty it cannot cover. A disposable integration may be sufficient and change the recommendation; accepted production-data, migration, or operational duty can keep Production valid. No mandatory POC-to-Pilot-to-Production sequence is introduced, and an experiment's newly created disposable state is distinguished from existing valuable state and consumers.
4. **DESIGNED:** The Captain answers the existing choice. The host carries the accepted commitment/assumption/result into existing `basis`, included work into `obligations`, exclusions into `scope_boundary`, and escalation conditions into `promote_when`; it adds no receipt key. Misunderstanding, abandonment, no answer, cancellation, or a timeout leaves the scope unresolved and creates no selected receipt or retrospective success; a noninteractive host returns the existing `NEEDS_PROFILE_DECISION` result with the missing fact.
5. **DESIGNED:** The locally authorized work-item actor uses the existing state transaction to commit the accepted receipt and re-read it before continuation invokes `profile-contract-loader.py`. Death before commit grants no working-stage authority; after commit, restart re-reads the exact receipt and pin. A mismatched or unavailable readback follows the existing refusal/recovery path rather than reconstructing acceptance. **OBSERVED:** this shape's installed 4.1.1 loader accepted the committed task and ideation-1 pin at state commit 88627fc42682fedef63a63b2c3b7538599d46d62; digest e6f51ce2b017a3252be4a9541252309fd9ccb480f30d7979b9b6a980aa4b7f80. That is route-loading evidence, not an observed selection conversation.
- Permitted observable change: recommendation content/order, clarity of the existing question, and faithfully populated existing receipt values. `semantics_unchanged: false` describes this design for the later source-native stage receipt; this report preserves the already admitted receipt and installed pin. Command grammar, receipt schema, routes, authority, external mutation, and persistence layout remain unchanged. No credentials, deployment, migration, original POC reopening, historical rewrite, package installation, or external planning write is included.
### Where it touches and stop numbers

| File at the delivery base | Lines now | Estimated final | Journey seam / disposition |
|---|---:|---:|---|
| `kc-dev-flow/skills/choose-work-profile/SKILL.md` | 136 | 155 | Steps 1-5: replace the opening and consolidate the existing question/receipt handoff; preserve actual production and authority boundaries. |
| `kc-dev-flow/skill-scenarios/choose-work-profile.scenarios.yaml` | 22 | 130 | Steps 2-5: retain and tighten the existing migration case; add five bounded counterexamples using the same scenario schema. |
| `scripts/kc-dev-flow-contract-test.py` | 2405 | 2415 | Steps 1-5: align the existing chooser assertion if its abstract opening is replaced; keep route, schema, admission, and byte-account checks. Clause checks are structural regression evidence. |
| `kc-dev-flow/README.md` | 236 | 236 | Existing selection/promotion overview remains accurate; keep the detailed explanation in the chooser. |
| `kc-dev-flow/skills/continue-dev-flow/SKILL.md` | 269 | 269 | Step 5 read-only consumer; use existing committed-receipt readback and route resolution. |
| `kc-dev-flow/scripts/profile-contract-loader.py` | 1119 | 1119 | Step 5 read-only parser/loading seam; no new field or fallback. |
| `docs/dev/README.md` | 459 | 459 | Step 5 read-only local authority and transaction binding. |
| `kc-plugin-forge/reference/skill-runner.py` | 364 | 364 | Existing optional behavior-exercise transport and scorer; no runner change. |
| `PRODUCT.md` | 109 | 109 | Read-only context authority. |
| `ARCHITECTURE.md` | 270 | 270 | Read-only context authority. |
| `CLAUDE.md` | 117 | 117 | Read-only context authority and delivery rules. |
- All counts were measured from opened source at c2c62bf9dff5c3af1e27eb643a15eadf9023485f, not inherited. Halt and report if the proposed product diff exceeds **3 changed files**, **340 changed lines (additions + deletions)**, or **150 changed lines in the chooser**, measured against that exact delivery base; also halt if any source-native static stage exceeds 40,000 bytes. A changed delivery base must be recorded and all counts remeasured before build. These are stopping conditions, not targets; any threshold replacement remains Captain-owned.
- Measurement used the existing gate's `load_loader()` and `assert_proportional_load(loader, ROOT / "kc-dev-flow/references")`, without the live route driver: eight source-stage loads passed; maximum is Pilot ideation 39,991, with continuation 16,016 and Local Profile/frontmatter 7,631 bytes. The chooser, scenarios, and test are outside this defined mandatory account, so this route leaves it at 39,991; it does not claim total conversation tokens are capped. Keep the chooser replacement within 8,500 bytes (currently 7,562), avoid repeating explanations in shared references, and do not raise the 40,000-byte limit. No CI change is proposed and cost per PR was not measured.
### Falsifiable acceptance and proof proposal

- **AC-1 / AC-2:** Add a new-repository scaffolding-only case with an unresolved first integration (clarify the missing commitment, do not treat scaffolding as proof), plus a disposable real-integration case with throwaway generated state (recommend POC when that evidence decides the next commitment). Require task-specific commitment, uncertainty, observable result, included work, and exclusions in the actual response. Fail if it jumps from scaffolding or future hosting ambition to operated release, invents a proved journey, or omits a lower alternative when recommending Production for an unproved journey.
- **AC-1 / AC-2 / AC-3:** Add an operated-release case with an unproved first journey but explicitly accepted production data and recovery ownership: retain Production, offer the disposable alternative, and explain which accepted duty it fails to cover. Fail if the new-repository label forces POC or the alternative silently drops that duty. Add a valued existing-consumer case whose users upgrade by taking the version with no migration: Pilot remains available; existing value must not be described as hypothetical disposable output.
- **AC-3 / AC-4:** Retain scenario T4 (the twelve-line rename requiring every adopter to edit configuration): Production remains the recommendation despite small size. Add an unanswered/misunderstood-scope case against a fixture containing an existing receipt; require the missing fact to remain unresolved, `NEEDS_PROFILE_DECISION` in a noninteractive invocation, and byte-identical original receipt after the attempt. The other answered fixtures require readback values matching the Captain's exact accepted scope; fail on recommendation-as-selection, invented acceptance, changed existing scope, or an added receipt field.
- **AC-5 / without-it proposal:** Use the existing scenario schema/runner and the repository's pinned model in one implementation-owned exercise, not a new standing check. First run one discriminating case against the actual delivery-base chooser (the runner's `red` merely omits the preamble and is not this baseline); then the same case against the candidate, plus the other five candidate cases: at most **7 model invocations, 35 minutes total, no automatic retry**. Use isolated fixture copies and capture the exact source revision/hash, raw conversation, returned receipt, before/after file bytes, and scorer result. First feed a deliberately wrong saved response to the existing scorer and observe refusal/failure so passing regexes are not assumed credible. If the delivery-base response does not expose the claimed absence, record that result and revise the falsifier rather than claiming improvement.
- Structural checks cannot establish operator understanding or faithful scope transfer; the existing implementation/validation owner must read each captured recommendation and receipt against the task facts, especially the lower alternative and named duty. The existing runner is single-turn and does not prove the real Ask UI's rendering, interactive cancellation, all hosts, or future conversations; fixture readback and a bounded native-host observation cover only the paths exercised. No model/provider exercise ran during shape. New external spend requires a Captain-approved provider/time/spend bound before those calls; without it, behavioral acceptance remains pending. Reuse the affected contract, loader, instruction-budget and required repository checks after implementation, not as substitutes for these cases.

### Applicable policy receipts and delivery boundary

- Conditional dispositions: `retained_document_change=true` for the chooser; retained-document policy Rules 1-3 and 6-8 apply to its in-place repair, with no retained-document addition/deletion and no policy receipt required. Its concrete chooser explanation is the single home; the README overview and shared boundaries remain accurate. `project_context_claim_may_change=true` was checked against the bound authorities below. `brownfield_capability_change=false`: this is direct repair of the already named explanation seam, an explicit reverse-recovery exclusion; no new/missing abstraction or removal claim needs an audit. `multi_slice_required=false`: one integrated selection-to-receipt slice is sufficient; journey-slicing was not loaded.
- `project_context: {impact: none, authority: "docs/dev/README.md Local Profile: PRODUCT.md + ARCHITECTURE.md + CLAUDE.md", claim_locator: "PRODUCT.md kc-dev-flow entry; ARCHITECTURE.md profile-native loading; CLAUDE.md Commit / PR Conventions", surface: "per-item profile routes, committed-receipt authority, loader boundaries, and delivery ownership", stale_claim: none, approved_change: none, landed_change: none, planned_check: "At candidate validation compare the captured recommendation and receipt-to-loader readback with these claims, and inspect the exact diff for changed routes, schema, loading or authority; any changed or contradicted claim falsifies none", validation_evidence: pending}`
- Separate delivery prerequisite supplied by the FO, not independently rerun here: release PR #369 head 2db51cdd / run 34458008467 fails the installed-digest-disabled ablation because the expected later diagnostic is now caught earlier by `feedback accepted changed package bytes`; expected-diagnostic alignment precedes shared release validation. It is outside this issue's three-file acceptance surface, must be separately owned/approved, and proves nothing about later ablations. No product commit, PR, delivery gate, install, or external issue mutation was performed in shape.

## Stage Report: implementation

- DONE: Commit only the reviewed issue correction and integrate current main without losing sibling or main behavior.
  Correction `23ecab00ae5bd7b88474b749e2d3f277cca5df1f` and normal merge `7623ff78dbd6d1331050c4552db21672f4235fd8` are on `spacedock-ensign/issue-393-profile-commitment-explanation`. The exact delivery base is `790278b7165682bfae8b0e61e091b40989328a16`. The merge was conflict-free. Against that base only the chooser, its existing scenarios, and the existing contract test differ: 293 changed lines, including 130 chooser lines and 8,489 chooser bytes. Main's POC-close, role-guidance and Go-test surface-map changes remain inherited; issue #396 and the frozen combined candidate were not modified.
- DONE: Run affected actual-head checks and budgets; retain truthful behavioral/observation limits.
  The full `python3 -B scripts/kc-dev-flow-contract-test.py` passed on `7623ff78` in 60.901 seconds with an isolated process session; this includes the loader and affected main regression checks. Earlier SIGTERM executions are retained as interruptions, not assertion failures. Existing scenario validation passed all six cases; six receipt-byte controls and eight block/flow-selection controls passed, and the timestamp template parsed with its capture annotation outside the value. Existing static accounting passed all eight stage loads, maximum 39,979/40,000 bytes. No extra broad ablation was run after the First Officer accepted the actual-head checks. RoboRev is non-gating `UNAVAILABLE(reason: unsupported)`: its v0.62.0 JSON lacks the pinned configuration/version/caps/timeout correlation envelope. Daemon and Codex authentication were available, but no claim, review request, confirmation, model exercise or provider setup was performed.
- DONE: Prepare exact candidate and implementation report for independent validation and authorized Draft delivery.
  The full candidate patch and source hashes, actual-head check results, controls, observation and preserved original patch are in the evidence directory below. The task frontmatter, accepted brief, receipt, pins and old report are preserved. This implementation report does not mark validation, behavioral acceptance, PR readiness, merge or release complete; parent owns fresh validation and delivery.

### Summary

The existing chooser now routes unchanged recorded choices, supplied acceptance and unaccepted recommendations before the shared explanation. It names the next commitment, unresolved assumption, observable result and included work; compares an unproved journey with a concrete disposable alternative even after Production acceptance; and carries only accepted scope/history into the existing receipt. The timestamp placeholder puts capture annotation in a YAML comment. The existing scenario checker preserves required final-newline bytes and permits inline historical quotations while rejecting new standard block/flow selections. Mechanical signatures remain subordinate to existing semantic review; no semantic grader, new schema, gate, consumer migration or CI trigger was added.

### Acceptance evidence

- **AC-1 — implemented; bounded behavior observed.** The frozen scaffolding/unanswered-choice case explicitly states all four explanation parts as proposed scope, keeps the journey unproved and creates no selected receipt. Its unsupported aside about individual steps and imprecise final file-count wording remain recorded in the manual review; they are not evidence of task facts. Structural checks alone do not prove explanation quality on every invocation.
- **AC-2 — implemented; earlier comparison PASS, current complete-case acceptance pending.** The accepted-Production observation on chooser SHA-256 `18cbec22bad38faf3c84fedc0654bfea41c463645e1a9440de54037be0e7f2c0` names a disposable upload/parse/view alternative and why accepted recovery/rollback duties make it insufficient, while retaining the legitimate full Production route. That run is overall PARTIAL because `(capture)` was inside its timestamp scalar. Current chooser SHA-256 `deed5f7abcc89119d0b6284a49997867b94640e0d9afe5c0ce3b84c047f0e812` has local parser/contract evidence for the comment correction, not a fresh accepted-Production model run. No successful-general-benchmark claim follows.
- **AC-3 — implemented; source/fixture coverage retained.** Existing valuable state and consumers are distinct from disposable generated state, repository age selects no profile, and consumer migration retains the Production boundary. The existing six scenarios cover disposable integration, accepted operation, existing reports and required adopter migration. Earlier model outputs remain bound to their original source; this integrated head has no new model proof.
- **AC-4 — implemented; unresolved/reuse preservation observed.** Frozen changed-scope and unchanged-receipt cases preserved the exact 596-byte receipt including its final newline (SHA-256 `f9d4bd4534edd0820cd25c6bf2b3247493608b3227a9120a0942a5ec895a472e`). The old checker incorrectly rejected that required newline and a quoted historical selection. Those original scores are preserved; current controls/rescoring repair the checker interpretation without turning old outputs into new model runs. Standard block/flow no-selection signatures are not a universal YAML or semantic validator. Unknown candidate facts do not grant committed-stage readiness.
- **AC-5 — local checks PASS; full behavioral acceptance remains for fresh validation.** The existing full contract, six-case schema, named controls and 40,000-byte accounting pass at the integrated head. Lower/unresolved/reuse and valid-Production evidence is retained with the limitations above. No new model calls occurred in this delivery continuation. No CI change was made; cost per PR was not measured. Marketplace/install/frontmatter and independent semantic review are assigned to fresh validation by the First Officer.

### Exact evidence and review boundary

Evidence directory: `/Users/kent/conductor/workspaces/kc-claude-plugins/kathmandu/.context/poc-coordinator/.context/pilot-maintenance/ready-delivery/profile`.

- `candidate.patch`: SHA-256 `9da3da533c003f171cf380a1a8a32774b3fb5eff95857a86878efce8058f906e`; `candidate.json` binds head/base/branch and all three source hashes.
- `full-contract-result.json`, `full-contract.log`, `static-budget.json`, `scoped-controls.json`, `roborev-observation.json` bind this local result. `original-uncommitted.patch`, `original-complete.patch` and `reviewed-standalone.patch` preserve the reviewed correction before integration.
- Prior behavior remains immutable in `../../handoff-repair/six-case-cloud-proof/report.md` and `../../handoff-repair/single-comparison-cloud-proof/`; old mechanical scores, failed cases and timestamp failure remain evidence. Local checker calibration remains in `../../local-correction-after-opus/issue-393/`.
- Project-context disposition remains `impact: none`: no routes, schema, authority, loading contract or repository product claims changed. Detailed explanation remains in the existing chooser; retained-document policy adds no new document or receipt. The changed contract test is structural evidence, and the checker controls establish only the stated serialization behavior. Independent validation owns sufficiency and necessity judgment at this exact candidate.

## Stage Report: validation

- DONE: Independently review the exact candidate against accepted behavior and retained authority boundaries.
  AC-1/AC-2/AC-3/AC-4: reviewed clean `7623ff78dbd6d1331050c4552db21672f4235fd8` against `790278b7165682bfae8b0e61e091b40989328a16`; three files/293 changed lines, 8,489 chooser bytes. No material contradiction in four-part commitment explanation, concrete disposable alternative, accepted Production route, valuable state, consumer migration, or unresolved/unchanged receipt handling.
- DONE: Complete missing required checks and verify actual evidence without relabeling historic model results.
  AC-5: validator marketplace parity/schema/9 installs passed, frontmatter passed 65/65, and existing-rule sanitizer had zero BLOCK/REJECT and no changed public-plugin findings; manifest drift, unresolvable install, malformed frontmatter or known leaks would fail these checks. Owner exact-head full contract passed exit 0 in 60.901 s; six schema cases, six receipt-byte controls, eight selection-signature controls and eight stage budgets passed, maximum 39,979/40,000 bytes; altered receipt bytes or standard unresolved selections falsify the controls, not arbitrary semantic mistakes.
- DONE: Prepare a truthful validation report, actionable defect dispositions and PR-readiness recommendation.
  AC-1/AC-2/AC-3/AC-4/AC-5 map and exact argv/log/hash evidence are in `validation-evidence/report.md` under the evidence directory below; counts DONE 3 / SKIPPED 0 / FAILED 0. Recommend authorized PR delivery for the bounded guidance repair; no whole-issue/model reliability, merge or release acceptance is claimed.

### Summary

Local verification is complete: independent review found no material product defect at the exact candidate, and the missing local repository checks passed. PR creation, hosted CI and exact-head provider feedback remain pending; the validation assignment stays active for that boundary. The earlier Production comparison stays overall PARTIAL because its old timestamp scalar was invalid; current comment/parser evidence and later checker rescoring are not new model runs. Prior scaffolding/unanswered/reuse observations support only their recorded boundaries; no new model exercise, standing checker, gate, source mutation or runtime replacement occurred.

### Evidence and disposition

- Evidence directory: `/Users/kent/conductor/workspaces/kc-claude-plugins/kathmandu/.context/poc-coordinator/.context/pilot-maintenance/ready-delivery/profile/validation-evidence`.
- Source identity: chooser SHA-256 `deed5f7abcc89119d0b6284a49997867b94640e0d9afe5c0ce3b84c047f0e812`; full-index patch `9da3da533c003f171cf380a1a8a32774b3fb5eff95857a86878efce8058f906e`. `identity-verification.json` verifies all three files; `final-readback.json` records clean owner status and no existing PR on this branch.
- `marketplace-result.json` / `.log`: `bash scripts/marketplace-verify.sh`, exit 0, 131.103 s, no smoke. `frontmatter-result.json` / `.log`: `bash scripts/skill-frontmatter-lint.sh`, exit 0. `sanitize-result.json` records exact one-off existing-rule argv, exit 0; 27 nonblocking extra test-file warnings are unchanged fixture/policy lines, with dispositions in `sanitize-disposition.json`.
- `project_context`: impact remains `none`; fresh source and bound PRODUCT/ARCHITECTURE/CLAUDE claims agree on existing schema/routes, committed-receipt loading and Captain authority. Validation evidence is the report's AC-4/source review plus owner exact-head loader contract. No retained-document addition/deletion or changed diagram applies.
- Remaining bounded uncertainty: no complete current-head accepted-Production model run, broad host/interactive cancellation proof or universal YAML-selection checker. Historic receipt cases preserve the exact 596 bytes including newline; original failure scores remain immutable. These limits were part of Captain-authorized local PR continuation, not silently relaxed proof claims.
- Required hosted CI and exact-head feedback remain for the delivery owner after PR creation. No CI change was made; cost per PR was not measured. Captain retains merge/release authority.

### PR feedback before Ready

PR feedback: {"dispositions":[],"fingerprint":"sha256:cb19ca27801e9b85fa2b7e51c5aedeba8821cdf3af6e67ce7f48587aff1105b0","head":"7623ff78dbd6d1331050c4552db21672f4235fd8","layer":"single","pr_number":425,"repository":"iamcxa/kc-claude-plugins","scheme":"github-pr-feedback/v1"}

- Complete native observation at 2026-09-11T10:19:52.546810+00:00: one complete GraphQL thread page and one complete REST review page, zero reviews and zero retained external items; before/after repository, PR author and head are stable. Evidence: `validation-evidence/feedback-before-ready/` in the directory above. No external comment or review was posted.
- First Officer CI evidence `../github-checks.json` records 3/3 checks passing: GitGuardian Security Checks, multi-profile route gate, and version parity. `../github-pr.json` binds OPEN/Draft, MERGEABLE/CLEAN to candidate `7623ff78dbd6d1331050c4552db21672f4235fd8`. These factual reads permit the delivery owner to perform its final identity/check read before Ready; Ready and merge are not claimed here.

### Ready delivery readback

At 2026-09-11T10:21:45Z, PR #425 is OPEN and Ready (`isDraft=false`), MERGEABLE/CLEAN, with `mergedAt=null` and exact candidate `7623ff78dbd6d1331050c4552db21672f4235fd8`. Validator after-Ready native observation completed both paginated surfaces and found zero retained external feedback; fingerprint remains `sha256:cb19ca27801e9b85fa2b7e51c5aedeba8821cdf3af6e67ce7f48587aff1105b0`, matching the current report receipt. Evidence: `validation-evidence/feedback-after-ready/` and `validation-evidence/after-ready-checks.json`. Both required checks pass (2/2); the route gate also reran successfully on Ready as run `34588801398`. This completes the authorized local-validation and Ready-feedback work; Captain merge and post-merge reconciliation remain pending, with no terminalization or release claim.
