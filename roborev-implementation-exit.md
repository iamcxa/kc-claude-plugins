---
id: e9nrdgxgnp1rqwwbcxfzb1nj
title: "kc-dev-flow: adopt a proportional RoboRev implementation exit"
status: ideation
source: captain:conversation-2026-08-13
product: kc-dev-flow
sprint: S2
started: 2026-08-14T07:45:49Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design:
lane: main
---

## Problem

The workflow needs an implementation-exit review that catches material defects before Draft PR creation without repeating the author’s own heavyweight PR review after the Draft exists. A repository-configured RoboRev review can provide exact-tip evidence, but adopting it indiscriminately would make POCs pay for production-grade panels and would turn tool absence into a workflow blocker. The task must define a proportional, optional RoboRev path with an honest fallback while preserving fresh behavioral validation, external GitHub feedback reconciliation, and Captain delivery authority.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v1
  selected: production
  recommended: production
  basis: "A retained marketplace-published workflow contract for external repository adopters; evidence is exact-revision delivery input, hosts may lack RoboRev or local-machine access, and the change carries compatibility, release, rollback, and ownership obligations without granting delivery authority."
  obligations:
    architecture:
      - "Use one repository-configured exact-tip implementation-exit observation before initial Draft creation, reusing already-completed matching evidence without adding a daemon, second ledger, generalized evaluator, or automatic merge."
      - "Keep RoboRev evidence separate from fresh behavioral validation, GitHub-native feedback reconciliation, and Captain push, Ready, merge, and terminalization authority."
      - "Treat local, Conductor Cloud, and explicit local-command bridge capability as independently detected facts; an environment label alone proves neither support nor absence."
    implementation:
      - "Emit an explicit non-green no-run or fallback result when RoboRev, its daemon, a compatible agent, authentication, or persistent local state is unavailable; fresh validation remains sufficient to continue."
      - "Keep model, reasoning, minimum severity, and optional panel selection repository-owned and proportional; Production does not make a multi-reviewer panel the default."
      - "Bound spend structurally with one explicit exact-tip observation, matching-evidence reuse, duplicate-enqueue avoidance, and a repair-attempt cap; observe approximate provider cost/coverage when available without creating a second ledger or precise-dollar claim."
    testing:
      - "Prove exact-tip PASS and findings/non-pass behavior plus unavailable, unsupported, skipped, failed, timed-out, and stale classifications against current provider behavior."
      - "Prove the honest no-RoboRev fallback, matching-evidence reuse, configured single-reviewer and panel paths, and supported installed-host/release behavior."
      - "Keep each live or tool validation batch within 20 minutes and preserve exact-revision release evidence."
  invariant_sources:
    - "docs/dev/_mods/kernel.md — authority, exact-revision delivery, outcome, and evidence discipline"
    - "docs/dev/README.md — implementation, fresh validation, GitHub feedback, and Captain delivery boundaries"
    - "docs/dev/_mods/work-control-profile.md — closed evidence outcomes and resource/review controls"
    - "/Applications/Conductor.app/Contents/Resources/conductor-skill/skills/conductor/SKILL.md — local and Cloud environment boundary"
  scope_boundary: "No review-every-commit hook, micro-repair auto-review, unbounded refine loop, daemon, second ledger, generalized evaluator, automatic GitHub mutation, auto-Ready, or auto-merge."
  promote_when:
    - "Re-enter ideation if the seam gains unattended recurring execution, external mutation, retained provider state, or a hosted-service obligation beyond this repository-configured observation."
  decision:
    authority: captain:kent
    at: 2026-08-14T08:08:11Z
```

## Proposed approach

## Design determination

## Acceptance criteria

## Test plan

## Measurement

## Doc diff

## Out of scope
