---
title: Load kc-dev-flow contracts from the installed plugin
status: ideation
source: https://linear.app/duckbase-co/issue/DEV-45/load-kc-dev-flow-contracts-from-the-installed-plugin
product: kc-dev-flow
planning-window: Linear Cycle b788c52d-8370-475f-be4f-8fcd88dd03d6 2026-08-27T16:00:00.000Z/2026-09-10T16:00:00.000Z
planning-outcome: Linear Project e780d04f-cf7d-4ebb-bf9a-90fec8466923 Plugin-owned kc-dev-flow contracts sha256:4106b2e493e8bd75052c1fb3b775eaf434ef8b087a7717611d5d81f2a3a81990
sprint: S7
sprint-readiness: ready
design: required
started: 2026-09-01T16:31:49Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: 3fkmdwdvsfha8ektb2s5jz7d
gates:
    version: 1
    records:
        - id: gate:3fkmdwdvsfha8ektb2s5jz7d:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:3fkmdwdvsfha8ektb2s5jz7d-backlog-1
              briefing:
                id: briefing:3fkmdwdvsfha8ektb2s5jz7d:backlog:attempt-1:revision-1
                digest: sha256:ae267311c31a0901273945546368887a7d6c2cd9bfe84748a06a52dc5dbdf822
                request-digest: sha256:a18c3d220d0cbce5f1048e194bf5745aeecdc945a63c166cc1766b7bc5ddda4b
                room-ref: ./dev-45-load-kc-dev-flow-contracts/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:3fkmdwdvsfha8ektb2s5jz7d:backlog:1
                briefing: briefing:3fkmdwdvsfha8ektb2s5jz7d:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-01T16:29:53.994804Z"
                decision: approve
                reason: Captain approved the bound Production ideation direction.
              application:
                target-stage: ideation
                state: consumed
---

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: production
  recommended: production
  basis: Existing and new adopters keep persistent repository policy and state; removing vendored runtime contracts changes migration, compatibility, and rollback commitments.
  route: [shape, build, verify]
  obligations:
    architecture: [Define host-neutral installed-resource discovery, bind one plugin version and contract digest per stage, distinguish compatible from incompatible stage-boundary upgrades, preserve provider-neutral GitHub and Linear adapters]
    implementation: [Keep README, local mods, and Spacedock state repository-owned, resolve canonical runtime contracts from the installed plugin, remove obsolete vendored files and parity machinery only after replacement behavior is proven]
    testing: [Exercise fresh adoption across supported hosts and profiles, prove active-stage pinning and next-stage upgrade, prove incompatible upgrades stop before dispatch, measure the smaller retained surface, reject every required-mechanism removal]
  scope_boundary: No automatic plugin installation, marketplace release automation, provider writes, executor scheduling, or Hermes and Nightwatch portfolio work.
  decision:
    authority: person:captain
    at: 2026-09-01T16:13:19Z
```

## The problem

Repository adoption currently copies canonical kc-dev-flow kernels, profiles, references, loaders, and guards into each repository. Installation and upgrades therefore duplicate plugin-owned behavior, create merge and parity work, and can leave a repository on mixed contract bytes.

## Accepted outcome

An installed kc-dev-flow plugin is the canonical runtime source. An adopter repository keeps only its local workflow README, local mods, and Spacedock state. Adoption and upgrades inspect and refit those local files without copying canonical contracts. A stage pins the plugin version and contract digest it starts with; a compatible upgrade becomes effective at the next stage boundary, while an incompatible boundary stops before dispatch until local policy is refit.

## Non-goals

- Do not change planning semantics beyond the approved forward-only Linear cutover for new docs/dev admissions.
- Do not mutate active Spacedock state during plugin upgrades.
- Do not bind the design to Conductor, Claude Code, Codex, Hermes, GitHub Projects, or Linear internals.
- Do not retain vendored canonical files merely for offline parity.
- Do not build automatic plugin installation, marketplace release automation, executor scheduling, or the proposed Hermes/Nightwatch portfolio direction.

## Acceptance criteria

- **AC-1** A fresh adopter executes every supported profile and stage from installed plugin resources without repository copies of canonical kernel, profile, reference, loader, or guard files.
- **AC-2** An active stage stays bound to its starting plugin version and contract digest; the next stage uses a compatible installed upgrade.
- **AC-3** An incompatible upgrade fails before next-stage dispatch and identifies the README or local mod refit required.
- **AC-4** Adoption and upgrade preserve repository-owned README policy, local mods, and Spacedock state.
- **AC-5** Migration removes obsolete vendored files and parity machinery without weakening profile routing, close guards, or kernel authority.
- **AC-6** Runtime resolution remains host-neutral and works from Spacedock tracks in repository worktrees.
- **AC-7** Goal-sufficiency and without-it evidence prove every retained mechanism is necessary and the adoption surface is smaller.

## Route-back conditions

The accepted outcome, non-goals, Linear Project, or Cycle changes; runtime discovery cannot bind a plugin version and digest at a stage boundary; or the minimum retained repository surface cannot preserve local policy without weakening kernel authority.
