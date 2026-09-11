---
title: "fix(kc-dev-flow): make retained architecture explanations discoverable"
status: validation
product: kc-dev-flow
sprint: S7
sprint-readiness: ready
issue: iamcxa/kc-claude-plugins#396
provenance: https://github.com/iamcxa/kc-claude-plugins/issues/396
id: m0e43swm7wrs71xy98ea43gp
started: 2026-09-10T09:09:43Z
gates:
    version: 1
    records:
        - id: gate:m0e43swm7wrs71xy98ea43gp:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:m0e43swm7wrs71xy98ea43gp-backlog-1
              briefing:
                id: briefing:m0e43swm7wrs71xy98ea43gp:backlog:attempt-1:revision-1
                digest: sha256:31e8caf4368d8f332b6fadbdecd3dbdac9c63b80def6e5cf14105656a540336b
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:m0e43swm7wrs71xy98ea43gp:backlog:1
                briefing: briefing:m0e43swm7wrs71xy98ea43gp:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T09:13:27.58782Z"
                decision: approve
                reason: Captain Kent approved these issue repairs with "確認，就這樣交付" and selected Pilot for both with "Pilot可以". This initial admission records that existing scope/profile decision after publishing its administrative brief; it grants shape only and does not claim approval of a later implementation or future evidence.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:m0e43swm7wrs71xy98ea43gp:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:m0e43swm7wrs71xy98ea43gp-ideation-1
              briefing:
                id: briefing:m0e43swm7wrs71xy98ea43gp:ideation:attempt-1:revision-1
                digest: sha256:e1c30c753d41c2b4d9723cf6c14879d4fc7ac999958b16c4d27ceb0b8380d959
                room-ref: ./review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:m0e43swm7wrs71xy98ea43gp:ideation:1
                briefing: briefing:m0e43swm7wrs71xy98ea43gp:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T09:38:30.021828Z"
                decision: approve
                reason: Captain Kent replied "批准" to the presented two-item ideation review, including this task snapshot e1c30c75. Accept the bounded architecture-entrypoint design and enter implementation; new model spend remains separately reserved.
              application:
                target-stage: implementation
                state: consumed
        - id: gate:m0e43swm7wrs71xy98ea43gp:validation
          stage: validation
          attempts:
            - id: gate-attempt:m0e43swm7wrs71xy98ea43gp-validation-1
              briefing:
                id: briefing:m0e43swm7wrs71xy98ea43gp:validation:attempt-1:revision-1
                digest: sha256:db828450a509750b8df4ef5e510076b829712a5af98b6e122dacfe483f7dfe35
                room-ref: ./review/validation/briefing-1
worktree: .worktrees/spacedock-ensign-issue-396-architecture-entrypoint
pr: pr-merge:426
---

The selected route identifies one discoverable home for the architecture explanation before implementation, and retained documentation describes implemented behavior at the existing exit boundary.

## Development Brief

### Problem

A retained implementation can pass reviews while its architecture is discoverable only by reading code and a long work history. Current context-maintenance guidance does not clearly cover the initial, proportional architecture explanation.

### Accepted outcome

The selected route identifies one discoverable home for the architecture explanation before implementation, and retained documentation describes implemented behavior at the existing exit boundary.

### Non-goals

- No new stage, gate, architecture reviewer, documentation generator, mandatory diagram tool, second context authority, roadmap, or status file.
- No mandatory completed architecture before an experiment answers its question; no speculative designs or mutable progress in retained architecture documentation.
- No reopening completed work, forced ARCHITECTURE.md when an existing authoritative section suffices, or boilerplate edits to unchanged accurate documentation.
- No implementation changes in the originating product, new operating guarantees, consumer migration, or self-improvement experiment.

### Route-back conditions

Return to the Captain if the correction requires a new authority, gate, mandatory tool, schema, consumer migration, retrospective work, or a broader operating commitment; ask separately before unapproved external proof spend.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: "A bounded retained plugin-guidance repair for existing users, with no new operational duties or migration. Consumers can take the new version without rewriting their state."
  route: [shape, build, verify-deliver]
  obligations:
    architecture: ["Use the existing bound project-context authority and its linked architecture home; reuse project-context maintenance and retained-document policy."]
    implementation: ["Update the smallest necessary adoption, brief, and selected-stage guidance; allow existing accurate linked explanations without duplicate files or retrospective work."]
    testing: ["Exercise disposable and retained POCs, existing linked architecture, changed persistence/API boundaries, and unchanged documentation, with code or command evidence appropriate to the claim."]
  scope_boundary: "Only the accepted issue correction and its necessary evidence; no new operating commitment, workflow machinery, consumer migration, or new experiment."
  promote_when:
    - "A consumer must migrate, reconfigure, or rewrite records to upgrade."
    - "The scope accepts production data, destructive mutation, unattended operations, or new recovery/support responsibilities."
  decision:
    authority: "Captain Kent"
    at: "2026-09-10T09:06:31.121677Z"
```

The decision timestamp is capture time. In this Kathmandu session the Captain approved the maintenance delivery sequence with "確認，就這樣交付", then explicitly selected Pilot for both issue #393 and issue #396 with "Pilot可以". This records those scope and profile decisions, not review of a later implementation. The GitHub issue is provenance; this standalone brief has no Planning Receipt or provider scheduling claim.

## Acceptance criteria

- **AC-1**: A disposable POC can use a small Exploration Brief outline covering components, data flow, external boundaries, and tentative assumptions, without a permanent documentation set.
- **AC-2**: A retained POC has a repository entry point linked from its bound context or README, explaining retained components and responsibilities, inputs/outputs, persistence/source-of-truth boundaries, important package roles, and relevant code or commands.
- **AC-3**: Pilot and Production extend that explanation only for applicable authorization, deployment, failure, recovery, and compatibility boundaries; an existing accurate linked section satisfies the requirement without a duplicate file.
- **AC-4**: The explanation's home is identified before implementation, in build for a POC without shape, and changed implemented claims are aligned before the existing implementation/validation boundary using the existing maintenance policies.
- **AC-5**: Scenario evidence covers the issue's five acceptance examples, traces retained claims to implementation, and proves unchanged accurate documentation needs no extra edit or review loop; affected existing contract and instruction-budget checks pass.

## Stage Report: ideation

- DONE: Define one bounded accepted journey and its real program/file seams, non-goals, state boundaries and applicable context-policy receipts. Design coverage: AC-1 uses the disposable brief outline (journey step 2); AC-2 traces the retained linked home to code/commands (steps 2-3); AC-3 reuses an accurate home and applicable deeper boundaries (steps 3-4); AC-4 identifies the home before build and aligns claims before the existing exit (steps 2-4). These are design obligations, not passed implementation acceptance.
  Installed 4.1.1 pin readback passed for committed task/pin at state commit `88627fc42682fedef63a63b2c3b7538599d46d62`; source and `origin/main` are clean at `c2c62bf9dff5c3af1e27eb643a15eadf9023485f`. Journey, policy receipts, and exact seams follow.
- DONE: Trace AC-1 through AC-5 to concrete falsifiable implementation and verification steps, with no new standing process or unsupported behavior claim. AC-5 maps all five issue examples to the scenario file below, including byte-identical unchanged documentation with no extra review dispatch; the existing loader/contract baseline passes, while operator scenarios and candidate acceptance remain pending.
  The five issue examples map below to fixture actions and explicit failure observations; all implementation acceptance remains pending. Source `profile-contract-loader.test.py` and `scripts/kc-dev-flow-contract-test.py` passed; they prove existing loader/structural mechanics, not operator compliance.
- DONE: Measure the proposed file surface and instruction-budget pressure, set stop numbers, and durably report one sufficient implementation route after the FO grants the state-write slot.
  Thirteen existing files are proposed below; the actual baseline maximum is 39,991/40,000 bytes. The 39,792-byte result is hypothetical replacement arithmetic, not an implemented candidate or passed behavioral exercise.

### Summary

Use the existing `project-context-maintenance.md` as the explanation's policy home: identify one architecture home before implementation, accept an accurate linked section, and align implemented claims at the existing exit/validation boundary. Extend the existing trigger to initial retained implementation, qualify the POC exemption, and reuse existing stage outputs, receipts, document policy, regression tests and scenarios. No new stage, gate, reviewer, tool, runtime schema, duplicate authority, speculative retained design, archived-task retrofit, installed-package change, provider mutation, originating-product implementation, or paid experiment is part of shape.

1. OBSERVED — this Codex worker ran installed `profile-contract-loader.py` with the committed state task, README, pin and `ideation-1`; stdout selected kernel + Pilot base + shape. Source `scripts/kc-dev-flow-multi-profile-gate.py::assert_proportional_load` exercised source `load_contracts` for eight existing profile/stage combinations and measured static input bytes.
2. DESIGNED — a contributor's Codex/Claude process follows `adopt-dev-flow/SKILL.md` and the package README to bind existing context. Its continuation process loads the selected source contracts; Pilot/Production shape or POC build identifies the home in its current work-item output. Disposable POC uses a tentative Exploration Brief outline; retained work chooses a README/context-linked existing section, or defaults to `ARCHITECTURE.md` in a new repository.
3. DESIGNED — the implementation process follows `project-context-maintenance.md`: a retained explanation traces input -> components/package responsibilities -> persistence/source of truth -> query/output using real code/commands; Pilot/Production add applicable authorization, deployment, failure, recovery and compatibility boundaries. Proposed assumptions remain in the work item until implemented. An already accurate linked section satisfies the obligation without a new file or edit.
4. DESIGNED — the existing validation process runs each changed claim's cited command and follows README/context links; a stale persistence/API description, broken link, or false command result returns through the current stage-return mechanism. Missing bound authority returns to existing binding/authority resolution, not automatic document creation. An unchanged explanation adds no documentation edit or extra review loop.
5. DESIGNED — if the experiment is abandoned, record its existing outcome/cleanup and tentative outline; no permanent documentation set is required for disposable work. If a worker dies or times out, retain the current work-item evidence, do not claim alignment, and resume under the existing pin/attempt rules; no watcher, retry engine or recovery state is added. Permitted semantic change: initial architecture coverage/discoverability and its timing in existing guidance. Command grammar, receipt schemas, provider authorization, pin compatibility and stage graph are unchanged. Persistence is existing Git documents/work-item state; fixtures use disposable local files only, with no production data, credential access, migrations or external mutation.

Paths are relative to the pinned coordinator; counts are measured current lines -> estimated final lines. `Text` is instruction/document behavior; `Proof` is an existing test/scenario surface.
| Exact file | Lines now -> estimated after | Indispensable role in the journey |
|---|---:|---|
| `kc-dev-flow/references/project-context-maintenance.md` | 118 -> 138 | Text: one coverage/timing home; reuse `none`/`update` receipt, include initial explanation, keep current verification/authority boundaries. |
| `kc-dev-flow/references/profiles/poc-exploration/base.md` | 33 -> 34 | Text: replace broad architecture-document exemption with disposable/retained proportionality; otherwise retained example conflicts with its selected base. |
| `kc-dev-flow/references/profiles/poc-exploration/build.md` | 89 -> 92 | Text: small outline/home output before the first edit on the route without shape; no completed design prerequisite. |
| `kc-dev-flow/references/profiles/pilot-product-slice/shape.md` | 89 -> 91 | Text: identify the linked home in the existing pre-build output; leave build/verify descriptors unchanged. |
| `kc-dev-flow/references/profiles/production/shape.md` | 91 -> 93 | Text: same pre-build home with applicable deeper boundaries, using existing policy rather than duplicate coverage prose. |
| `kc-dev-flow/skills/continue-dev-flow/SKILL.md` | 269 -> 263 | Text: initial-retained trigger and consolidation of the existing conditional-reference explanation; preserve all loader, receipt, delivery and observation boundaries. |
| `kc-dev-flow/skills/adopt-dev-flow/SKILL.md` | 268 -> 272 | Text: bind the explanation through existing authority and adopt the initial-retained trigger; future adopters otherwise retain the old condition. |
| `docs/dev/README.md` | 459 -> 459 | Text: replace this adopter's old changed-claim trigger in place; keep marked Local Profile and authority bindings intact. |
| `kc-dev-flow/README.md` | 236 -> 244 | Text: public brief/conditional-reference entry exposes disposable outline and routed retained home; readers otherwise see old trigger guidance. |
| `kc-dev-flow/MIGRATION.md` | 492 -> 499 | Text: ordinary Pilot delivery note states no consumer migration or archived retrofit; same-stage pins remain pinned and compatible next-stage loading adopts the correction. No manual version bump. |
| `scripts/kc-dev-flow-contract-test.py` | 2405 -> 2440 | Proof: extend existing structural contract checks for the corrected exemption, trigger, timing and policy links; not an operator-behavior claim. |
| `scripts/kc-dev-flow-minimal-stack-ablation.test.py` | 932 -> 958 | Proof: remove each corrected contract seam in existing fixture copies and require the named contract rejection; retain the 40,000-byte falsifier. |
| `kc-dev-flow/skill-scenarios/continue-dev-flow.scenarios.yaml` | 62 -> 262 | Proof: five bounded action scenarios using the existing Forge scenario format and runner; actual file/command observations rather than policy substring claims. |
Each text seam serves entry, selected-stage timing, canonical explanation or compatibility communication; omitting one leaves the relevant accepted case unavailable or contradictory through that entry. The three proof seams separate wiring regression, witnessed test failure and operator action. Loader code, other build/verify contracts, manifest resources, retained-document policy, and root PRODUCT/ARCHITECTURE/CLAUDE documents are read-only dependencies already carrying the required mechanics; changing them would add no accepted behavior.

- AC-1 (disposable outline): scenario supplies a disposable local experiment and pressure to add permanent docs; the process records components/data flow/external boundaries/tentative assumptions in the brief, executes its question/outcome, and leaves permanent architecture files absent. Fail on required permanent docs, omitted outline, or postponed outcome; inspect actual files and commands, not only an action label.
- AC-2 (retained entry): scenario supplies a runnable local input/store/query fixture whose explanation exists only in a long log. The process creates one linked entry containing responsibilities, package roles and code/commands; a fresh reader follows README to it and runs the input-to-output path. Remove the link or point persistence at the wrong store to make that observation fail; log-only guidance cannot pass.
- AC-3 (existing home/proportional depth): scenario starts with an accurate linked README architecture section and a bounded Pilot/Production boundary; reuse it without creating `ARCHITECTURE.md`, and explain only relevant authorization/deploy/failure/recovery/compatibility. Fail on duplicate home, invented operating promise or missing exposed boundary. No mandatory diagram; if one is added, apply the existing render-and-check rule.
- AC-4 (timing/changed boundary): scenario changes a local persistence or API seam. Observe the home recorded before the first implementation edit, the approved claim updated in the same slice, and a cited command reading the new output/store before exit; a deliberately stale claim must fail the fresh check. POC performs initial classification in build; no new gate, record field or validation worker is introduced.
- AC-5 (five examples/no churn): the fifth scenario supplies an accurate linked explanation and unrelated one-line implementation correction; compare document bytes before/after and the process transcript, requiring no doc edit or extra review dispatch. Reuse `profile-contract-loader.test.py`, `kc-dev-flow-contract-test.py` and `kc-dev-flow-minimal-stack-ablation.test.py` on the candidate; a removed trigger/pointer must redden structural checks. The five scenarios cover issue examples retained, disposable, existing-linked, changed-boundary and unchanged; fixture artifact readback plus the fresh validator's code/command trace carries behavior evidence, not clause presence. Proposed behavioral exercise: five scenario IDs, at most one baseline and one candidate run each, using `kc-plugin-forge/reference/skill-runner.py` with isolated `{SCRATCH}`, same runner/model/settings and no judge-model calls. Baseline must explicitly load the real baseline skill/resources from the pinned delivery base and record their paths/hashes; runner `red` merely omits `green_preamble` and is not baseline-skill evidence. Run identical explicit skill-loading prompts against separate baseline and candidate checkouts (using the existing runner mode that loads that checkout), with no contamination from installed candidate content. Proposed elapsed stop: 60 minutes total, at most 10 calls; use the existing bare runner's 300-second per-call timeout and start no call with less than 300 seconds left. At either bound stop without added retries and mark unfinished cases inconclusive. Before spending, pin the exact available model/runtime and obtain Captain approval for new external spend; cost is unmeasured and no calls are approved or performed here. Record passed/failed/error by case with real file diffs and command transcripts; a missing negative failure is inconclusive, and this small sample proves neither general compliance nor cross-model reliability. A task-owned removal of the correction followed by the same accepted-goal observation supplies minimal-necessity evidence; no generic new harness or standing check is proposed.

`brownfield_capability_change=true` (initial coverage gap); `retained_document_change=true` (existing retained guidance changes); `project_context_claim_may_change=true` was evaluated against bound context. `multi_slice_required=false`: one integrated guidance repair, so journey-slicing was not loaded. Installed reverse-recovery, retained-document and project-context policies were loaded; source counterparts were inspected for archaeology. Retained-document Rules 1-3 and 6-8 govern in-place changes; there is no retained-document addition/deletion, so Rules 4/5 add no formal add/delete duty. Section overlap was nevertheless checked by scoped content search and file/history traversal: coverage belongs in project-context maintenance, callers keep short pointers, retained-document policy remains unchanged, and no diagram is proposed.
```yaml
reverse_recovery: {trigger: initial retained architecture coverage gap, boundary: "kc-dev-flow adoption/continuation -> selected shape or POC build -> context/doc policy -> existing proof surfaces; excludes originating product and archived work", layers: [{surface: loader, location: "kc-dev-flow/scripts/profile-contract-loader.py::load_contracts", completeness: WORKING_UNIT_UNPROVEN, need: REQUIRED, evidence: "source route tests and eight-stage byte accounting passed; operator journey unexercised", disproof_hook: "alter selected route/resource and rerun profile-contract-loader.test.py"}, {surface: architecture guidance, location: "references/profiles/poc-exploration/base.md:26; references/project-context-maintenance.md:24; skills/continue-dev-flow/SKILL.md:150", completeness: EXISTS_BROKEN, need: REQUIRED, evidence: "accepted initial retained case meets broad exemption/change-only trigger; content search plus path/history traversal found existing upkeep, not initial coverage", disproof_hook: "baseline retained-log-only action scenario unexpectedly produces a discoverable accurate home"}, {surface: existing proof entry, location: "scripts/kc-dev-flow-contract-test.py; skill-scenarios/continue-dev-flow.scenarios.yaml", completeness: WORKING_UNIT_UNPROVEN, need: REQUIRED, evidence: "existing deterministic loader checks pass; architecture operator scenarios are not present", disproof_hook: "remove corrected seam and require the existing structural check to fail; exercise actual files/commands in five scenarios"}], decision: recover}
project_context: {impact: none, authority: "docs/dev/README.md Local Profile: root PRODUCT.md, ARCHITECTURE.md and CLAUDE.md", claim_locator: none, surface: "PRODUCT.md kc-dev-flow catalog; ARCHITECTURE.md profile-native loading; CLAUDE.md release and authority conventions", stale_claim: none, approved_change: none, landed_change: none, planned_check: "fresh candidate loader routes/pins plus five action scenarios must retain one context authority, stage graph, disposable proportionality and release ownership; compare exact diff against these root claims beyond named surfaces", validation_evidence: pending}
```

Delivery base is `origin/main=c2c62bf9dff5c3af1e27eb643a15eadf9023485f`; independent repair targets trunk. Stop implementation when its diff against that base exceeds 15 changed files, 650 added+deleted lines, or 260 added+deleted lines in `kc-dev-flow/skill-scenarios/continue-dev-flow.scenarios.yaml`; report the observed crossing without continuing until the existing Captain-owned choice. Counts exclude ignored scratch and state reports, but include every product/proof change. Re-pin and remeasure against any newly selected delivery base rather than inherit these baseline counts. The existing gate measured 16,016 continuation bytes + 7,631 marked README bytes + emitted selected contracts, with maximum 39,991 (Pilot ideation). A shape-only 2,034 -> 1,572-byte consolidation of continuation's conditional explanation saves 462 bytes; allowing 80 local-profile bytes, 220 POC base/build bytes or 180 shape bytes yields a hypothetical maximum 39,792. Keep 40,000 enforced and verify the combined #393/#396 delivery; preserve trigger timing, relative resolution, named/null receipt handling, provider ownership, observation eligibility and false-trigger no-provider behavior. Conditional policy content is outside this measured mandatory prefix and must remain conditional, not hidden mandatory load. No CI trigger changes or measured CI cost are proposed. Implementation, action scenarios, exact-candidate checks and delivery remain future work.

## Captain scope amendment — mandatory architecture map and authorized delivery

Captain authorization: "就這樣發 PR 到可以讓我合併". The current dispatch records the accepted requirements as: "non-POC needs useful docs/architecture.md, read before exploration/implementation every continuation/worker, missing-map bootstrap by implementation owner including recovery, stale maps updated same slice, validation returns missing product docs."

These instructions supersede the original optional-file/alternative-home and no-consumer-action wording for this issue. Pilot and Production require a useful repository-root-relative `docs/architecture.md` even when another accurate architecture explanation exists; keep useful overview content there and link named deeper pages without duplicating them. Each continuation and worker reads it after authority/profile/pin checks and before exploration or implementation. An authorized implementation owner bootstraps a missing map, including recovery routes; independent validation returns missing/stale product documentation to that owner. POC creation remains exempt and an available map is read. A retained POC still keeps proportional linked explanation.

Keep the approved human writing rules: useful overview core, complexity-driven Mermaid diagrams and named linked subpages; each page has at most 1000 units, using the stated Chinese-character/English-word working convention and excluding only Mermaid diagram blocks. Headings, lists, table text and captions count. No general multilingual counting tool or renderer installation was added.

Consumer action means an ordinary authorized implementation worker creates or aligns missing documentation during a subsequent non-POC continuation after a compatible upgrade. There is no required pre-upgrade manual schema/configuration/record migration, pin rewrite, data conversion or operational duty; the existing Pilot choice remains unchanged. The stronger documentation requirement is real and is described in MIGRATION, not concealed as a no-op. Active pinned 4.1.1 bytes and historical brief/ideation remain immutable until the usual authorized upgrade/refit. This amendment changes the consumer policy under test; it does not retrofit the current pinned repository's root docs or replace its actual PRODUCT/ARCHITECTURE/CLAUDE authority bindings.

Delivery now includes product commits, normal main integration, and parent-owned PR delivery/review to readiness. Merge and release remain Captain-owned. No version bump, installed-cache rewrite, CI change, new cloud experiment or shared-state mutation is included in this implementation candidate.

## Stage Report: implementation

- DONE: Commit only the reviewed issue correction and integrate current main without losing sibling or main behavior.
  Standalone correction 03a055f4c9d10304c99310f72c93d422c45773fd is recoverable; normal merge retains exact main 790278b7165682bfae8b0e61e091b40989328a16. Final candidate 3ce12bdced8e3cf56ff6cb1a62949821fc346221 is clean on spacedock-ensign/issue-396-architecture-entrypoint; main POC closing semantics remain intact.
- DONE: Run affected actual-head checks and budgets; retain truthful behavioral/observation limits.
  Full integrated contract passed at cd34625b33ed4588609c110858b574d28597e9f1; the final two-file clarification passes --ablation-check and seven removal ablations (each rejects the named missing obligation). Eight schemas and sixteen handcrafted controls pass on unchanged scenario/runner bytes. Size 13 files/508 changed lines/scenario191; static39979/40000 excludes separately accounted map and conditional-policy text.
- DONE: Prepare exact candidate and implementation report for independent validation and authorized Draft delivery.
  Exact patch SHA256 f8c9c20319857f468a9937f2506a1035d3c830cc16e671d7ee147172c2fa9d3d, candidate hashes, commands/logs, scope amendment, acceptance limits and RoboRev UNAVAILABLE(unsupported; zero requests) are in the linked evidence directory; independent validation and parent-owned PR delivery remain next.

### Summary

Pilot/Production now requires a useful docs/architecture.md and reads it after authority/profile/pin checks before exploration/implementation; missing maps are bootstrapped by implementation, including recovery, and validation returns missing/stale documentation to that owner. POC creation remains exempt, accurate maps need no churn, and human overview/1000-unit/Mermaid/subpage guidance is preserved. Compatible upgrades require no schema/config/record migration; the required documentation action occurs during ordinary authorized implementation.

### Acceptance evidence and limits

- **AC-1:** Disposable POC brief outline and creation exemption remain; A2 handcrafted positive passes and forced-map negative fails. No current-model rerun is claimed.
- **AC-2:** Current map/link/content contract and fixture controls pass. Historical Sonnet5 A1 on policy 6c3fe20410561e343db03f5ee01bf2d099b909cfdd2871c53e1a11fc9d6cc696 created docs/architecture.md + README link and ran one inspector yielding HELLO (5/5 predicates); it proves old default-home behavior only. Omitted json module naming and history-trace relocation remain observations.
- **AC-3:** The scope amendment supersedes alternative-home sufficiency: a useful mandatory overview links accurate deeper details. A3/A6 controls preserve existing guide and reject alternate-only, overwritten detail and missing recovery map. Exhaustive content/model compliance is not established; no diagram artifact was added.
- **AC-4:** Source/manual inspection and removal ablations cover read-after-pin/before-exploration ordering and recovery ownership. A4 fixture changes store.json to saved.json and rejects a stale map; read chronology remains a future transcript requirement, not automated chronology or a new model run.
- **AC-5:** Eight schemas, six positive/ten negative handcrafted controls, full integrated contract and final scoped checks pass; unchanged-map bytes are preserved and churn is rejected. These prove deterministic contracts/endpoints, not exhaustive behavioral acceptance or cross-model reliability. Fresh validation, marketplace/parity/frontmatter and combined issue393+396 checks remain parent-owned.

### Context and observation

Actual root PRODUCT.md/ARCHITECTURE.md/CLAUDE.md authority bindings, historical brief/receipt/pins and installed 4.1.1 resources are preserved; this consumer-policy change performs no live root-map retrofit. Fresh validation must check the previously named context surfaces against the scope amendment; unchanged bytes alone are not evidence. No CI changes or CI-cost measurement occurred.

Pinned Pilot RoboRev eligibility is declared; CLI/JSON help, daemon and Codex-login probes passed. Same-host v0.62.0 actual JSON lacks required configuration hash, provider/JSON identity, caps and timeout envelope, so the observation is non-gating UNAVAILABLE(reason: unsupported), with zero requests/confirmations and no current-job verdict; unrelated job data was only a schema capability sample.

Evidence directory: [/Users/kent/conductor/workspaces/kc-claude-plugins/kathmandu/.context/poc-coordinator/.context/pilot-maintenance/ready-delivery/architecture](/Users/kent/conductor/workspaces/kc-claude-plugins/kathmandu/.context/poc-coordinator/.context/pilot-maintenance/ready-delivery/architecture). Read implementation-stage-report.md for full scope/evidence detail; candidate.json, integrated.patch, validation-commands.md, contract-result.json, final-contract-ablation-check-result.json, architecture-ablation-result.json, fixture-results.json, fixture-provenance.json, instruction-budget.json, map-input-accounting.json and roborev-observation.json bind the exact claims. The old SIGTERM/literal-check failures remain recorded, not relabeled as passes.

## Stage Report: validation

- DONE: Independently review the exact candidate against accepted behavior and retained authority boundaries.
  Candidate 3ce12bdced8e3cf56ff6cb1a62949821fc346221 vs base 790278b7165682bfae8b0e61e091b40989328a16 is clean; all source hashes match. Mandatory useful map, pin-before-read ordering, recovery bootstrap ownership and compatible-upgrade wording align with the Captain amendment.
- DONE: Complete missing required checks and verify actual evidence without relabeling historic model results.
  Exact candidate marketplace/parity/schema/eight installs pass. Frontmatter covers all 46 tracked candidate skills; 136 aggregate includes 90 ignored copies. Sanitizer 0 BLOCK/REJECT, 9 inherited WARN; clean peer merge passes scoped contract and static 39979/40000. Full final contract remains required Draft CI.
- DONE: Prepare a truthful validation report, actionable defect dispositions and PR-readiness recommendation.
  No material defect; local verification supports authorized Draft creation. Ready remains pending exact-head required CI and provider feedback. Report and exact argv/log/hash records: /Users/kent/conductor/workspaces/kc-claude-plugins/kathmandu/.context/poc-coordinator/.context/pilot-maintenance/ready-delivery/architecture/validation-evidence/report.md.

### Summary

Local independent validation is complete; Draft creation, full exact-head CI and native provider-feedback disposition are still pending. The accepted overview/read-order policy is coherent across continuation, adoption and profile guidance; implementation owns bootstrap/alignment and validators return defects. Source/manual review and synthetic/removal controls do not prove universal model obedience or whole-issue closure.

### Acceptance and context evidence

- AC-1: POC creation exemption and disposable outline remain; forced-map negative control rejects permanent-doc churn.
- AC-2: Retained linked components/IO/storage/package/check obligations remain; missing, wrong-root, empty and link-only controls reject absent useful maps.
- AC-3: Amendment requires useful docs/architecture.md despite existing detailed docs; controls preserve deeper guide and reject alternate-only/missing recovery map.
- AC-4: Read follows authority/profile/pin checks and precedes exploration; same-slice map/guide updates and recovery/validation ownership are explicit. Chronology is source/manual/removal proof only.
- AC-5: Eight schemas and sixteen handcrafted controls hash-match candidate; unchanged-map churn rejects. Owner final scoped checks and seven missing-clause rejections pass; full actual-head CI remains pending.
- Integration: architecture candidate plus peer 7623ff78dbd6d1331050c4552db21672f4235fd8 merges cleanly without owner-branch changes; tree 97dcaef3bf9cdda94bbccdc56d390199997a5782 passes existing --ablation-check and assert_proportional_load. Removing shared assertions or exceeding static budget fails these checks.
- Project-context `none` revalidated against root PRODUCT.md catalog, ARCHITECTURE.md profile/pin topology and CLAUDE.md release conventions; no contradiction or new authority found. Main Advance/POC closing text is byte-identical. Amendment exempts retrofitting this pinned adopter.
- Full-index patch SHA256 f8c9c20319857f468a9937f2506a1035d3c830cc16e671d7ee147172c2fa9d3d independently matches. Static budget excludes map/conditional-policy input; no universal byte cap or current-model reliability claim. No CI change; cost per PR unmeasured.
- Skips: parent assigns full exact-head contract to Draft CI, so unchanged mechanism suites are not rerun locally; no new model/provider/cloud smoke. No diagram or architecture-map artifact changed, so rendering/page-count checks are inapplicable. Older A1 proves only its older default-home policy.
- Frontmatter scope: existing script excludes only .git/node_modules, so its 136 successful files include 45 each under ignored .context/issue-396-combined and .context/issue-396-model-baseline; frontmatter-scope.json records all paths. This is not 136 distinct tracked skills.

Counts: DONE 3 / SKIPPED 0 / FAILED 0 for the dispatched completion checklist. Deliberate execution skips and pending delivery obligations are explicit above; they are not final CI passes.

## Stage Report: validation (cycle 2)

- DONE: Independently review the exact candidate against accepted behavior and retained authority boundaries.
  PR iamcxa/kc-claude-plugins#426 remains exact head 3ce12bdced8e3cf56ff6cb1a62949821fc346221, OPEN/Draft/MERGEABLE/CLEAN. Prior independent source review and combined-peer result remain valid; no product change or new defect occurred.
- DONE: Complete missing required checks and verify actual evidence without relabeling historic model results.
  All 3 observed checks pass, including both required checks; job 103230011063 logs actual ./scripts/kc-dev-flow-contract-test.py with PASS. Complete native feedback observation at 2026-09-11T10:30:19Z has no retained items or missing dispositions.
- DONE: Prepare a truthful validation report, actionable defect dispositions and PR-readiness recommendation.
  Recommend parent mark this exact revision Ready. Detailed evidence remains in ready-delivery/architecture/validation-evidence/report.md; parent retains Ready orchestration and Kent retains merge/release authority.

### Summary

Local validation, full exact-head CI and complete pre-Ready native feedback are green; no material defect remains for PR readiness. This completes the previously pending full-contract obligation without a duplicate local run. General model obedience, read-order transcripts and whole-issue reliability remain outside the proof.

### Exact-head delivery evidence

- Required check: version parity (plugin.json / marketplace.json / codex / README), run 34589094057/job 103230011063, SUCCESS; pr426-full-contract-ci.log records the actual full contract command and PASS, alongside marketplace/frontmatter checks.
- Required check: multi-profile route gate (live Spacedock), run 34589094090/job 103230011273, SUCCESS. GitGuardian Security Checks is also SUCCESS; pr426-ci.log binds all three to head 3ce12bdced8e3cf56ff6cb1a62949821fc346221.
- Native observation: explicit repository/PR views before and after reads match; one complete GraphQL thread page and one complete REST review page, zero threads/reviews/retained items, empty dispositions. pr426-before-ready-final/observation.json and normalized.json bind the fingerprint below; conversation-tab issue comments are outside this defined review slice.
- Factual correction to prior local report: marketplace.log passed nine plugin installs, not eight. Frontmatter correctly covered 46 tracked candidate skills; 136 aggregate additionally includes 90 ignored-copy files. No check rerun or source change was needed.
- AC-1/AC-2/AC-3/AC-4: prior source/manual and fixture evidence remains unchanged, including POC exemption, required overview, retained detail, recovery bootstrap ownership and same-slice alignment. AC-5 now additionally has full final CI PASS; prior clean peer merge and static 39979/40000 remain valid.
- Known boundaries: older A1 is old default-home model proof; schema 8/8 is scenario schema validation, not eight model runs. No new cloud/model proof, standing checker, CI trigger change or measured cost-per-PR claim.

PR feedback: {"dispositions":[],"fingerprint":"sha256:c7e7f6215a739d64cbfbd5f8f9c373e557cd9d1b2512c934e09e52fd84e764d5","head":"3ce12bdced8e3cf56ff6cb1a62949821fc346221","layer":"single","pr_number":426,"repository":"iamcxa/kc-claude-plugins","scheme":"github-pr-feedback/v1"}

## Stage Report: validation (cycle 3)

- DONE: Independently review the exact candidate against accepted behavior and retained authority boundaries.
  Ready PR iamcxa/kc-claude-plugins#426 is still head 3ce12bdced8e3cf56ff6cb1a62949821fc346221, OPEN/MERGEABLE/CLEAN with mergedAt=null. Registered owner source is clean; prior semantic review and approved scope remain unchanged.
- DONE: Complete missing required checks and verify actual evidence without relabeling historic model results.
  After-Ready native observation at 2026-09-11T10:31:58Z is complete and empty with unchanged fingerprint. Required checks 2/2 and all 3 distinct check names pass; Ready-triggered route-gate run 34589647234/job 103231740714 also passed.
- DONE: Prepare a truthful validation report, actionable defect dispositions and PR-readiness recommendation.
  Authorized delivery-to-Ready is verified with no material blocker. Final evidence is ready-delivery/architecture/validation-evidence/report.md, pr426-after-ready/observation.json and pr426-after-ready-checks.json; Captain merge/release remains pending.

### Summary

The exact reviewed revision is Ready, all required CI passes, and the one complete requested after-Ready native observation finds no retained feedback. No source change, extra model/provider experiment or local test rerun occurred. This validation completes authorized PR readiness, not merge, release or universal architecture/model correctness.

### Final acceptance and delivery evidence

- AC-1: Disposable POC outline and map-creation exemption retain source/manual and fixture evidence; no new model obedience claim.
- AC-2: Useful retained overview, linked responsibilities/IO/storage/packages/checks retain positive/negative control evidence; older A1 remains old default-home proof.
- AC-3: Required non-POC overview, applicable boundaries and named deeper links remain consistent with the Captain amendment; recovery/bootstrap ownership is preserved.
- AC-4: Pin-before-map-read ordering, implementation-owned bootstrap and same-slice alignment retain source/manual/removal proof; actual model chronology remains unproven.
- AC-5: Eight scenario schemas and sixteen handcrafted controls are hash-linked; final full contract actually passed CI, and clean peer integration plus static 39979/40000 passed. The static check excludes map/conditional policy bytes.
- Local verification correction remains nine plugin installs and 46 tracked candidate skill frontmatters; 136 successful physical files included 90 ignored copies. Sanitizer has 0 BLOCK/REJECT and 9 inherited WARN. No CI change; cost per PR not measured.
- Native feedback: repository-explicit identity stable before/after all reads, one complete thread page and one complete REST review page, zero threads/reviews/retained items and empty dispositions. Four successful check-run entries represent three distinct check names because Ready reran the required route gate.
- Counts for dispatched checklist: DONE 3 / SKIPPED 0 / FAILED 0. Earlier justified execution skips and local-only behavioral limits remain as recorded. Parent owns subsequent delivery state; any merge must reobserve native feedback under the existing merge boundary.

PR feedback: {"dispositions":[],"fingerprint":"sha256:c7e7f6215a739d64cbfbd5f8f9c373e557cd9d1b2512c934e09e52fd84e764d5","head":"3ce12bdced8e3cf56ff6cb1a62949821fc346221","layer":"single","pr_number":426,"repository":"iamcxa/kc-claude-plugins","scheme":"github-pr-feedback/v1"}
