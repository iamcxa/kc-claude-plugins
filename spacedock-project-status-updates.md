---
id: 16npdbnbe8707v7h5hcm4nbb
title: Turn projection snapshots into reviewable GitHub Project Status Updates
status: ideation
source: Captain-approved split from spacedock-github-project-projection after Claude Opus 5 ideation challenge on 2026-08-14
product: kc-dev-flow
sprint: S3
started: 2026-08-17
completed:
verdict:
worktree:
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

Use the shipped `spacedock-project-reconcile-result/v1` plus current state bytes as the input boundary. Extend the existing projection workflow to emit review-only candidate artifacts after a successful reconcile; do not add a `workflow_run` workflow or any unattended publication command. A local skill re-runs the input capture, displays the exact payload and diff, and requires the user to confirm that digest before the runtime may call GitHub's `createProjectV2StatusUpdate` mutation.

The first slice is `snapshot -> manifest -> deterministic Markdown candidate`, with no Project mutation. Its live demo uses Project #4's empty status history to return `insufficient-evidence` plus an explicit initial-baseline candidate, then proves an identical input produces the same fact and content digests. The second slice is `candidate -> fresh revalidation -> exact confirmation -> create/readback`, including recovery from an ambiguous create response by finding the deterministic receipt before any retry.

Candidate cooldown is derived observation, not authority: the workflow may use receipt-bearing published history plus digest-named Actions artifacts inside the bounded cooldown window. Expired candidate artifacts may cause another review artifact, never a publish. Sprint start, sprint close, and definition changes are delta classifications observed by the existing reconcile cadence; the weekly schedule and manual dispatch are emission triggers. Projection conflicts remain reconcile health and suppress status candidates.

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
Verified by: paired `spacedock-project-reconcile-result/v1` plus state fixtures classify stage-only movement as delivery, selected membership change as scope, and goal/exit-criterion or qualified sprint change as definition; missing dates, estimates, or exit criteria produce `insufficient-evidence` with no GitHub health enum. Falsified by: membership alone changes the delivery verdict, a bare sprint identity compares across products, or absent evidence yields `ON_TRACK`.

**AC-2 — Candidate facts and Markdown are deterministic and provenance-bound.**
Verified by: identical source bytes produce byte-equal fact sets and content digests apart from an explicit observation envelope; every number, date, identifier, percentage, and health token in Markdown is copied from the manifest allowlist, and a mutation that invents one refuses the candidate. Falsified by: a host model is required, observation time changes the content digest, or unmanifested factual text reaches a publish plan.

**AC-3 — Baseline history never guesses authority.**
Verified by: complete paginated Project status history accepts only the newest agreeing versioned receipt, returns `insufficient-evidence` for Project #4's empty history until explicit re-baseline, and refuses foreign, malformed, duplicate, or disagreeing receipts. Falsified by: foreign prose becomes the baseline, an incomplete page is treated as complete, or an initial baseline is published without exact confirmation.

**AC-4 — Publication remains an exact human-confirmed mutation.**
Verified by: `status plan` re-reads live inputs and status history and renders the exact GraphQL payload/diff; `status publish` accepts only the current plan digest after explicit confirmation. A fake adapter observes zero create calls before confirmation, zero on stale/different confirmation, and one receipt-bearing create plus readback after the matching confirmation. Falsified by: a workflow can publish, blanket approval counts, a stale manifest mutates, or the displayed payload differs from the sent payload.

**AC-5 — Confirmed publication is idempotent and recoverable.**
Verified by: a deterministic publication key is embedded in the receipt; a timeout after remote create followed by retry re-reads complete history, returns the existing update, and performs no second create. Conflicting key/body bytes fail closed and no update/delete mutation is available. Falsified by: an ambiguous response can duplicate an update, retry trusts local success state, or recovery rewrites foreign history.

**AC-6 — Candidate generation is useful, quiet, and non-authoritative.**
Verified by: the existing projection workflow emits only candidate artifacts after a successful conflict-free reconcile; weekly/manual triggers plus delivery/scope/definition classification generate reviewable output, while content digest and bounded artifact cooldown suppress unchanged repeats. Projection failure/conflict emits health evidence only, and `COMPLETE` is absent unless the whole configured Project is complete. Falsified by: cron publishes, a 15-minute no-change reconcile emits repeated candidates inside cooldown, a projection conflict becomes management prose, or sprint completion becomes Project completion.

## Sizing and proof

One worker owns two slices because they form one observable journey and share one manifest/receipt authority. Split only if the publish adapter becomes independently blockable from the deterministic candidate after the first live demo. E2E applies: slice one must produce a real Project #4 baseline candidate without mutation; slice two must use an explicitly authorized real create/readback and an identical no-duplicate retry. Proposed code surfaces are one new skill with one canonical runtime asset and tests, bounded changes to the existing installer/config/workflow assets, and the owning mapping/README documentation. No new dependency, service, database, issue, Project field, or GHA workflow is proposed.

The original dependency is satisfied by the merged projection result and Draft identity contracts at `f187ddbdf3442b883512dc1d37c05442edf28e08`. A changed projection schema, missing complete Project history, or inability to keep GHA candidate generation non-publishing returns this item to ideation.

## Stage Report: ideation — cycle 1

**Decision: accept the same-workflow, two-slice Production route and send the exact contract to one fresh EM; implementation remains closed until that verdict is recorded.**

- `Profile:` committed Production receipt `b34ec97c752b536709f179d6ec9df0e969d2a563` binds persistent history, unattended candidate generation, external mutation, recovery, compatibility, and rollback proof.
- `Journey:` slice one demos an exact no-write Project #4 re-baseline candidate; slice two demos exact confirmed create/readback plus ambiguous-response recovery without duplication.
- `Subtraction:` reuse the versioned projection result and existing workflow; omit another workflow, another authoritative ledger, optional LLM wording, update/delete mutations, automatic publish, and multi-Project abstraction.
- `Trigger decision:` existing reconcile cadence observes changes; weekly and manual dispatch emit candidates, with digest/artifact cooldown suppressing unchanged repeats. No privileged `workflow_run` chain is added.
- `External proof:` GitHub's current GraphQL schema exposes `ProjectV2.statusUpdates` and `createProjectV2StatusUpdate`; live Project #4 returns `totalCount=0` with complete pagination, making explicit re-baseline the first production journey.
- `Control receipt:` bound-field validation passes for the committed `kc-dev-flow/S3` identity. AC headings now carry concrete verification and falsifiers; `spacedock status --ac-scan` must be re-run after this report is durable.
- `AC scan:` all six headings are found, but the adapter again reports `unevidenced=true citations=0` despite each adjacent `Verified by:` and `Falsified by:` clause. This is the already-recorded scanner defect; primary evidence and the fresh EM remain the gate inputs.
- `Captain ruling:` Kent selected Production and accepted the same-workflow candidate-artifact plus local confirmed-publish topology. Automatic publication and scope expansion remain closed.
- `EM disproof target:` return if the existing result cannot be a sufficient deterministic input, candidate dedupe needs authoritative new state, confirmation cannot bind the displayed/sent payload, ambiguous create cannot reconcile exactly once, or AC-6 actually contains a third independently blockable value surface.
