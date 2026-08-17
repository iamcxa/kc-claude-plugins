---
id: 16npdbnbe8707v7h5hcm4nbb
title: Turn projection snapshots into reviewable GitHub Project Status Updates
status: implementation
source: Captain-approved split from spacedock-github-project-projection after Claude Opus 5 ideation challenge on 2026-08-14
product: kc-dev-flow
sprint: S3
started: 2026-08-17
completed:
verdict:
worktree: .worktrees/spacedock-project-status-updates
issue:
pr:
mod-block:
design: required
lane: main
---

Consume versioned deterministic snapshots from `spacedock-github-project-projection` and turn delivery, scope, and definition changes into reviewable GitHub Project Status Update drafts without allowing an LLM or unattended workflow to calculate facts or publish.

## Boundary

This task begins at a validated projection snapshot. The projection sibling owns snapshot production, source receipts, and Project item reconciliation. This task owns delta classification, candidate cooldown/deduplication, deterministic Markdown, optional host-LLM wording, stale-manifest refusal, history, and human-confirmed publication.

V1 has no native GitHub draft object. Drafts remain derived local or Actions artifacts until `status publish` revalidates current inputs, shows the exact payload and diff, and receives explicit confirmation. Automatic publication and LLM-authored unattended payloads are out of scope.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v1
  selected: production
  recommended: production
  basis: "The feature serves a persistent production GitHub Project, retains publication history and compatibility receipts, may generate candidates on an unattended weekly schedule, and performs an external Project Status Update mutation after explicit human confirmation."
  obligations:
    architecture:
      - "Consume the versioned reconcile result without creating a second projection, lifecycle, or metric authority."
      - "Keep deterministic manifest facts separate from optional host-LLM prose and make receipt-bearing history the only automatic baseline."
      - "Preserve human publication authority while assigning retry, recovery, compatibility, and rollback ownership for the persistent Project surface."
    implementation:
      - "Generate and deduplicate unattended candidates without granting the workflow publication authority."
      - "Re-read live inputs, reject stale or foreign baselines, and display the exact Project mutation before confirmation."
      - "Persist versioned receipts and history with bounded retry and recovery for interrupted confirmed publication."
    testing:
      - "Prove byte-stable facts and Markdown for identical manifests and refuse every LLM-authored fact not present unchanged in the manifest."
      - "Exercise delivery, scope, definition, insufficient-evidence, cooldown, stale-input, foreign-history, retry, and recovery paths."
      - "Use a fake adapter to prove zero mutations before confirmation and exactly one receipt-bearing mutation after it, then require an authorized real Project seam before delivery."
  invariant_sources:
    - "docs/dev/README.md"
    - "docs/dev/_mods/kernel.md"
    - "docs/dev/ROADMAP.md#Sprint-S3-GitHub-projection-dogfood"
    - "kc-dev-flow/skills/setup-github-project-projection/SKILL.md"
    - "kc-dev-flow/skills/setup-github-project-projection/references/mapping-contract.md"
  scope_boundary: "No automatic publication, LLM-calculated facts, GitHub-to-SD writeback, Project schema ownership, multi-repository rollout, Relay or CarLove rollout, or workflow-global management authority."
  promote_when:
    - "Re-select the profile if automatic publication, another Project or repository, organization-wide compatibility, a different credential boundary, or an SLO/support promise enters scope."
  decision:
    authority: "Captain (Kent)"
    at: "2026-08-17T06:41:42Z"
```

## Accepted Production route

Use the shipped `spacedock-project-reconcile-result/v1` plus current state bytes as the input boundary. Projected title, body, status, identity, and product facts come only from the result; state contributes only sprint, dates, goal/exit criteria, and other definition facts absent from the result, and every result receipt must pin the exact loaded state commit. Extend the existing projection workflow to emit review-only candidate artifacts after a successful reconcile; do not add a `workflow_run` workflow or any unattended publication command. A local skill captures the result through an explicit projector dry-run override that performs no external write even when the installed config is apply-enabled, displays the exact payload and diff, and requires the user to confirm that digest before the runtime may call GitHub's `createProjectV2StatusUpdate` mutation.

The first slice is `snapshot -> manifest -> deterministic Markdown candidate`, with no Project mutation. Its live demo uses Project #4's empty status history to return `insufficient-evidence` plus an explicit initial-baseline candidate, then proves an identical input produces the same fact and content digests. The second slice is `candidate -> fresh revalidation -> exact confirmation -> create/readback`, including recovery from an ambiguous create response by finding the deterministic receipt before any retry.

Candidate history is derived observation, not authority. The existing workflow gains one explicit low-frequency weekly cron in addition to its 15-minute projection cron; only the weekly schedule and manual dispatch run candidate emission. The newest agreeing published receipt suppresses an unchanged content digest. Candidate artifacts are outputs only and are never listed across runs, so no `actions: read`, artifact-retention dependency, or cooldown ledger exists. Sprint start, sprint close, and definition changes remain delta classifications included in the next low-frequency/manual candidate. Projection conflicts remain reconcile health and suppress status candidates.

Optional LLM wording, a second history ledger, a second workflow, reverse GitHub-to-SD sync, automatic publication, multi-Project rollout, and dedicated analytics infrastructure are absent from the accepted implementation. Facts, metrics, dates, identifiers, and health remain deterministic; Project #4 currently has no prior Status Update, so the first real publication is an explicitly confirmed re-baseline.

## Reverse-recovery audit

| Surface | Completeness / need | Evidence and disposition |
| --- | --- | --- |
| Projection result | `WORKING / REQUIRED` | Exact merged-main live reconcile emits versioned `spacedock-project-reconcile-result/v1` with ten selected entities and zero operations. Reuse it; a schema mismatch or failed result suppresses the candidate. |
| Projection workflow | `WORKING / REQUIRED` | The installed default-branch workflow already owns cadence, state checkout, reconcile, and artifact upload. Add a candidate step there rather than creating another trigger/secret lifecycle. |
| GitHub Status Update API | `WORKING / REQUIRED` externally, `MISSING` in repo | Official GraphQL exposes read/create/update/delete and live Project #4 readback returns a complete empty history. Add only create plus paginated readback; update/delete stay absent. |
| Deterministic status compiler | `MISSING / REQUIRED` | Searches by product terms and GraphQL symbols found no GitHub status compiler. The Linear-only `kc-project-pulse` is prose/LLM-led and owns a different provider and fact authority, so it is a reference, not a reusable runtime. |
| Separate status workflow or ledger | `MISSING / NO_OBSERVED_CONSUMER` | Repository workflows, plugin runtime, Project #4, external rollout, and current operations were checked; no consumer requires another workflow or authoritative ledger. Re-observe if a second Project, automatic publish, or independent SLO enters scope. |

The protected value is an accurate, low-noise management update that a human can review and publish without recalculating facts. Appetite is one Production PR with at most two demoable slices. If time forces a cut, keep deterministic draft plus confirmed exactly-once publication; drop only the immediate delta fast path and optional wording, preserving weekly/manual candidate emission. The pre-mortem is a scope change appearing as delivery regression or a timed-out create producing a duplicate update.

## Acceptance criteria

**AC-1 — Deltas preserve denominator meaning.**
Verified by: paired `spacedock-project-reconcile-result/v1` plus exact-pinned state fixtures classify stage-only movement as delivery, selected membership change as scope, and goal/exit-criterion or qualified sprint change as definition; projected fields are consumed from the result rather than re-derived, and missing dates, estimates, or exit criteria produce `insufficient-evidence` with no GitHub health enum. Falsified by: state/result commit pins disagree, a projector stage/identity mutation does not break the consumer, membership alone changes the delivery verdict, a bare sprint identity compares across products, or absent evidence yields `ON_TRACK`.

**AC-2 — Candidate facts and Markdown are deterministic and provenance-bound.**
Verified by: identical source bytes produce byte-equal fact sets and content digests apart from an explicit observation envelope; every number, date, identifier, percentage, and health token in Markdown is copied from the manifest allowlist, and a mutation that invents one refuses the candidate. Falsified by: a host model is required, observation time changes the content digest, or unmanifested factual text reaches a publish plan.

**AC-3 — Baseline history never guesses authority.**
Verified by: complete paginated Project status history accepts only the newest agreeing versioned receipt, returns `insufficient-evidence` for Project #4's empty history until explicit re-baseline, and refuses foreign, malformed, duplicate, or disagreeing receipts. Falsified by: foreign prose becomes the baseline, an incomplete page is treated as complete, or an initial baseline is published without exact confirmation.

**AC-4 — Publication remains an exact human-confirmed mutation.**
Verified by: `status plan` uses an explicit apply-disabled projector path and a fake adapter counts zero external writes of every kind while it re-reads inputs/history and renders the exact GraphQL payload/diff; an apply-enabled effective capture is refused. `status publish` requires a controlling terminal, accepts only the current plan digest typed after explicit confirmation, and then performs one receipt-bearing create plus readback. Falsified by: plan reaches any Project mutation, a non-interactive workflow reaches create, blanket approval counts, a stale/different digest mutates, or the displayed payload differs from the sent payload.

**AC-5 — Confirmed publication is idempotent and recoverable.**
Verified by: a deterministic publication key is embedded in the receipt; a timeout after remote create followed by retry re-reads complete history, returns the existing update, and performs no second create. Conflicting key/body bytes fail closed and no update/delete mutation is available. Falsified by: an ambiguous response can duplicate an update, retry trusts local success state, or recovery rewrites foreign history.

**AC-6 — Candidate generation is useful, quiet, and non-authoritative.**
Verified by: the existing projection workflow adds one explicit low-frequency weekly cron and emits only candidate artifacts on that event or manual dispatch after a successful conflict-free reconcile; the 15-minute projection cron never emits a status candidate, and the newest agreeing published receipt suppresses an unchanged content digest without cross-run artifact listing. Projection failure/conflict emits health evidence only, and `COMPLETE` is absent unless the whole configured Project is complete. Falsified by: either cron publishes, the 15-minute cron emits a candidate, an unchanged weekly input already represented by the latest receipt emits again, a projection conflict becomes management prose, or sprint completion becomes Project completion.

## Sizing and proof

One worker owns two slices because they form one observable journey and share one manifest/receipt authority. Split only if the publish adapter becomes independently blockable from the deterministic candidate after the first live demo. E2E applies: slice one must produce a real Project #4 baseline candidate without mutation; slice two must use an explicitly authorized real create/readback and an identical no-duplicate retry. Proposed code surfaces are one new skill with one canonical runtime asset and tests, bounded changes to the existing installer/config/workflow assets, and the owning mapping/README documentation. No new dependency, service, database, issue, Project field, or GHA workflow is proposed.

The original dependency is satisfied by the merged projection result and Draft identity contracts at `f187ddbdf3442b883512dc1d37c05442edf28e08`. A changed projection schema, missing complete Project history, or inability to keep GHA candidate generation non-publishing returns this item to ideation.

## Stage Report: ideation — cycle 1

**Decision: accept the same-workflow, two-slice Production route and send the exact contract to one fresh EM; implementation remains closed until that verdict is recorded.**

- `Profile:` committed Production receipt `b34ec97c752b536709f179d6ec9df0e969d2a563` binds persistent history, unattended candidate generation, external mutation, recovery, compatibility, and rollback proof.
- `Journey:` slice one demos an exact no-write Project #4 re-baseline candidate; slice two demos exact confirmed create/readback plus ambiguous-response recovery without duplication.
- `Subtraction:` reuse the versioned projection result and existing workflow; omit another workflow, another authoritative ledger, optional LLM wording, update/delete mutations, automatic publish, and multi-Project abstraction.
- `Trigger decision:` add one low-frequency weekly cron to the same workflow and keep manual dispatch; the existing 15-minute cron never emits a status candidate. Published-receipt digest comparison suppresses unchanged output without artifact listing, new permissions, or a privileged `workflow_run` chain.
- `External proof:` GitHub's current GraphQL schema exposes `ProjectV2.statusUpdates` and `createProjectV2StatusUpdate`; live Project #4 returns `totalCount=0` with complete pagination, making explicit re-baseline the first production journey.
- `Control receipt:` bound-field validation passes for the committed `kc-dev-flow/S3` identity. AC headings now carry concrete verification and falsifiers; `spacedock status --ac-scan` must be re-run after this report is durable.
- `AC scan:` all six headings are found, but the adapter again reports `unevidenced=true citations=0` despite each adjacent `Verified by:` and `Falsified by:` clause. This is the already-recorded scanner defect; primary evidence and the fresh EM remain the gate inputs.
- `Captain ruling:` Kent selected Production and accepted the same-workflow candidate-artifact plus local confirmed-publish topology. Automatic publication and scope expansion remain closed.
- `EM disproof target:` return if the existing result cannot be a sufficient deterministic input, candidate dedupe needs authoritative new state, confirmation cannot bind the displayed/sent payload, ambiguous create cannot reconcile exactly once, or AC-6 actually contains a third independently blockable value surface.

## Stage Report: ideation — cycle 2

**Decision: NARROW the contract by three bounded corrections, preserve the accepted topology and value, and advance to implementation after this exact state is durable.**

- `Fresh EM:` tool-assisted read-only Claude Opus 5 High session `8c6db708-7550-4dd6-bfac-24d6270f0108` returned `narrow / high`, `multi_model: not_needed`. It accepted the two-slice topology, result-plus-state boundary, external receipt history, exactly-once recovery shape, Production obligations, and every omitted surface.
- `Input correction:` `status plan` must force the projector's effective mode to dry-run and count every external adapter write, because dogfood config is intentionally apply-enabled. Projected facts come from the result; state adds only absent definition facts under agreeing `state_commit` pins.
- `Trigger correction:` the installed 15-minute cron is projection liveness, not weekly status emission. Add one explicit low-frequency weekly cron to the same workflow and select it by event schedule; manual dispatch remains the explicit fast path.
- `Subtraction correction:` remove cross-run Actions artifact listing and bounded artifact cooldown. It had no necessity record and would add `actions: read` plus retention lifecycle. Unchanged-output suppression uses the newest agreeing published receipt; ephemeral candidate artifacts remain outputs only.
- `Confirmation correction:` plan digest binds displayed/sent payload, while a controlling-terminal refusal is the scheduled-workflow enforcement point. The workflow contains no publish step; its no-TTY invocation must fail before create.
- `Required RED:` apply-enabled capture attempts any write; projector stage/identity mutation leaves facts unchanged; mixed state/result commits pass; non-TTY or stale digest reaches create; timeout recovery creates twice; observation time changes content digest; 15-minute cron emits a candidate; unchanged published digest emits again.
- `Gate boundary:` no Captain scope or architecture delta remains. Implementation may create the accepted isolated worktree and run RED/GREEN; live Project publication still requires a separately shown exact payload and fresh explicit confirmation before mutation.

```yaml
science_officer_em_upward_report:
  em_judgment: "The accepted topology is the smallest sufficient Production route, but ideation must correct the apply-enabled input hazard, name the real low-frequency emission trigger, and remove the unearned artifact-cooldown mechanism before implementation."
  evidence_synthesis: "At product f187ddbdf3442b883512dc1d37c05442edf28e08 and state 4f061515e362ab3cc6c3e8dc07ea60faa056c28d, the versioned reconcile plan is deterministic and pins state/trunk/entity/projector identity, but dogfood config enables external apply; the installed workflow has only a 15-minute cron plus dispatch; and cross-run artifact listing would require a new actions:read permission and retention lifecycle. The result plus exact-pinned state is sufficient when projected fields are consumed from the result and state contributes only absent definition facts."
  risk_tradeoff_call: "The benefit is a deterministic reviewable update with human-confirmed publication on one shipped projection authority. The material risk is a plan command mutating Project data or relying on a trigger that does not exist. The smaller alternative is an explicit dry-run capture, one same-workflow low-frequency cron, and published-receipt digest suppression without artifact history."
  recommendation: "Record the three bounded corrections, then implement one skill with one canonical runtime and tests, bounded same-workflow/installer/config changes, and owning docs. RED must cover all-write refusal, producer-consumer mutation, state-pin refusal, non-TTY/stale confirmation refusal, ambiguous-create no-duplicate recovery, time-free content digest, correct cron routing, and published-digest suppression."
  route: narrow
  confidence: high
  multi_model: not_needed
  fo_boundary: "FO may record and sync these corrections, re-read them, advance to implementation, and dispatch the accepted worktree. FO may not alter scope, add a permission/workflow/ledger, authorize live publication, or treat scanner defects as gate evidence."
  engineering_judgment:
    question: "Does the exact ideation contract deserve proceed as the smallest sufficient Production route?"
    revision: "Task state 4f061515e362ab3cc6c3e8dc07ea60faa056c28d; product f187ddbdf3442b883512dc1d37c05442edf28e08."
    evidence_synthesis: "At product f187ddbdf3442b883512dc1d37c05442edf28e08 and state 4f061515e362ab3cc6c3e8dc07ea60faa056c28d, the versioned reconcile plan is deterministic and pins state/trunk/entity/projector identity, but dogfood config enables external apply; the installed workflow has only a 15-minute cron plus dispatch; and cross-run artifact listing would require a new actions:read permission and retention lifecycle. The result plus exact-pinned state is sufficient when projected fields are consumed from the result and state contributes only absent definition facts."
    adjudications:
      - finding: "F-1: The reconcile result plus exact-pinned state is a sufficient non-duplicative input."
        disposition: supported
        basis: "The result owns projected fields and receipts; state supplies only sprint/date/goal definition facts absent from the result, with a mutation test and matching state_commit pin enforcing the allocation."
      - finding: "F-2: status plan is no-write under the apply-enabled dogfood config."
        disposition: unsupported
        basis: "The current projector applies whenever external_apply_enabled is true; the status capture must force an effective dry-run and test every adapter write count."
      - finding: "F-3: Cross-run artifact cooldown is necessary for AC-6."
        disposition: unsupported
        basis: "Low-frequency/manual emission plus latest published-receipt digest suppression meets the quiet-candidate value without actions:read, artifact listing, or retention lifecycle."
      - finding: "F-4: Candidate compile and confirmed publish are two slices of one journey."
        disposition: supported
        basis: "The emission seam owns no independent persistent lifecycle state and cannot deliver value separately from candidate review or confirmed publication."
      - finding: "F-5: Receipt-key history readback can recover an ambiguous create without a local ledger."
        disposition: supported
        basis: "Complete paginated remote history is the durable observation; a matching deterministic receipt returns the existing update, while no match fails closed rather than auto-creating again."
      - finding: "F-6: The omitted LLM, workflow, ledger, update/delete, service, dependency, and multi-Project surfaces are required."
        disposition: unsupported
        basis: "No retained AC fails without them; several would add authority or lifecycle responsibilities contrary to the accepted minimal route."
    risk_tradeoff: "The benefit is a deterministic reviewable update with human-confirmed publication on one shipped projection authority. The material risk is a plan command mutating Project data or relying on a trigger that does not exist. The smaller alternative is an explicit dry-run capture, one same-workflow low-frequency cron, and published-receipt digest suppression without artifact history."
    recommendation: "Record the three bounded corrections, then implement one skill with one canonical runtime and tests, bounded same-workflow/installer/config changes, and owning docs. RED must cover all-write refusal, producer-consumer mutation, state-pin refusal, non-TTY/stale confirmation refusal, ambiguous-create no-duplicate recovery, time-free content digest, correct cron routing, and published-digest suppression."
    route: narrow
    confidence: high
    dissent: "A proceed-with-conditions reading is defensible because the topology is unchanged, but AC-6 named the unearned cooldown and the plan-write falsifier was absent, so both corrections belong to ideation authority."
    disproof_condition: "Return if dry-run capture cannot avoid the apply-enabled projector, complete status history or state pinning is unavailable, candidate generation needs a new permission/workflow, the projection schema changes, or the authorized live create cannot run before its credential envelope expires."
    authority_boundary: "Captain retains scope, schema, credentials, live external mutation, red residuals, merge, and closeout; work-item authority owns these bytes; Spacedock owns stage/worktree/durability; EM is advisory; validation remains fresh at the final revision."
```
