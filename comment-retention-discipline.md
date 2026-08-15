---
title: "Teach agents to retain only comments with maintenance value"
status: ideation
source: "Captain-approved independent kc-dev-flow/S3 slice, 2026-08-15; does not alter the existing projection sequence"
product: kc-dev-flow
sprint: S3
started: 2026-08-15T12:03:26Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design:
lane: main
id: hpxks7c1kndqqhhr38kzna6q
---

## Problem

Agents have repeatedly produced code diffs where comments restate more code than they clarify. The portable kernel constrains absolute claims but does not require comments to preserve non-obvious maintenance value, so adopters lack a proportional rule that removes narration while retaining invariants, external constraints, hazards, and rejected alternatives.

This independent S3 slice must prove a behavior change through the installed loader within a 20-minute model-pressure cap, add no new skill, mod, linter, or standing model gate, and leave the existing projection sequence unchanged.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v1
  selected: production
  recommended: production
  basis: "A portable marketplace-released kernel changes long-lived authoring behavior for external adopters; it carries compatibility, release, rollback, and ownership obligations, while this slice changes no executable product behavior or external production state."
  obligations:
    architecture:
      - "Reuse the existing kernel authoring and minimality seam; add no skill, mod, linter, recurring gate, daemon, evaluator, or duplicate policy surface."
      - "Preserve the absolute-claim rule and keep the new comment-retention principle portable across languages and hosts."
    implementation:
      - "Keep canonical and vendored kernel copies byte-identical and record only the minimal independent S3 ROADMAP wording without changing projection sequence."
      - "Keep net always-loaded policy growth at or below roughly 50 words and aim near zero by rewriting existing minimality prose."
    testing:
      - "Run six paired installed-loader responses across three cases, repeating at most one ambiguous pair, within a 20-minute live-model cap."
      - "Require baseline redundant-comment retention at least once and candidate improvement without necessary-comment loss; otherwise report UNKNOWN or no-change."
      - "Run existing contract and release checks and verify no executable-behavior or test regression at the exact candidate revision."
  invariant_sources:
    - "docs/dev/_mods/kernel.md — authority, outcome, minimality, and verification discipline"
    - "docs/dev/README.md — Local Profile, Gate Authority, and state transaction"
    - "docs/dev/_mods/engineering-judgment.md — independent ideation recommendation and retained authority"
  scope_boundary: "No capability-scoped work-control-profile loading, repository-wide comment cleanup, language-specific style rules, RoboRev or PR-review policy change, new skill or mod, linter, recurring gate, daemon, generalized evaluator, or standing model run."
  promote_when:
    - "Re-enter ideation if the change gains executable enforcement, unattended model execution, language-specific policy, or external review-policy ownership."
  decision:
    authority: captain:kent
    at: 2026-08-15T12:03:26Z
```
