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

## Acceptance criteria

### AC-1 — Deltas preserve denominator meaning

Given a prior receipt-bearing snapshot, a stage-only change is delivery delta, membership change is scope delta, and goal/exit-criterion or qualified sprint identity change is definition delta. A ratio change caused by membership does not become work regression. Missing dates, estimates, or exit criteria produce `insufficient-evidence`, never inferred `ON_TRACK`.

### AC-2 — Draft facts are deterministic and LLM wording is mechanically bounded

The same manifest produces byte-stable baseline facts and Markdown apart from explicit observation metadata. An optional host LLM may omit or rephrase prose, but every number, date, identifier, and health claim in the candidate must exist unchanged in the manifest fact set. A fact invention or alteration refuses publication.

### AC-3 — Foreign history cannot become an implicit baseline

If the latest published Project Status Update lacks a parsable projector receipt, classification stops with `insufficient-evidence` until a human explicitly re-baselines. The tool never overwrites a foreign update or silently treats it as the prior snapshot.

### AC-4 — Publication remains human authority

`status publish` re-reads the live snapshot inputs, rejects a stale manifest, displays the exact mutation payload and diff from the latest receipt-bearing update, and requires explicit confirmation. Fake-adapter coverage proves zero create mutations before confirmation and exactly one receipt-bearing mutation after it.

### AC-5 — Candidate generation is useful but quiet

A weekly schedule plus sprint start, sprint close, and definition-change events may emit candidates. Content digest and cooldown suppress unchanged repeats. Projection-stale and projection-conflict events stay in reconcile health rather than becoming management status narratives. `COMPLETE` means the Project is complete, not that one sprint ended.

## Dependency and sizing

Blocked until `spacedock-github-project-projection` publishes and versions the deterministic snapshot contract. Re-estimate during ideation from that exact schema. This sibling may not broaden the projection task or delay its Issue + Project item + receipt + no-op value slice.
