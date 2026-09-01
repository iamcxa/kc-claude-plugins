---
title: Load kc-dev-flow contracts from the installed plugin
status: backlog
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: kc-dev-flow/plugin-owned-contracts
sprint-readiness: defer
design: required
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: d04wdm6eayba80ayawqg1qk7
gates:
    version: 1
    records:
        - id: gate:d04wdm6eayba80ayawqg1qk7:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:d04wdm6eayba80ayawqg1qk7-backlog-1
              briefing:
                id: briefing:d04wdm6eayba80ayawqg1qk7:backlog:attempt-1:revision-1
                digest: sha256:578780997ab5340c4f3313324434b99ae1956b471ac2d74fc70606b8c5928135
                request-digest: sha256:51967b548356b08de925116ec8acdbea0be579dfb3c4e2b8a56c7e3006d016fd
                room-ref: ./plugin-owned-dev-flow-contracts/review/backlog/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-09-01T15:03:22.471893Z"
                reason: Captain changed the planning source of truth from GitHub Project to Linear; rebind the planning provider before presenting the backlog gate.
---

## Problem

Repository adoption currently copies canonical kc-dev-flow kernels, profiles, references, loaders, and guards into each repository. Installation and upgrades therefore duplicate plugin-owned behavior, create merge and parity work, and can leave a repository on mixed contract bytes.

## Accepted outcome

An installed kc-dev-flow plugin is the canonical runtime source. An adopter repository keeps only its local workflow README, local mods, and Spacedock state. Adoption and upgrades inspect and refit those local files without copying canonical contracts.

A stage pins the plugin version and contract digest it starts with. A compatible plugin upgrade becomes effective at the next stage boundary; an active stage does not hot-swap its contract. An incompatible boundary stops before dispatch until the local README or mods are refit.

## Non-goals

- Do not change planning-provider choice or project-management semantics.
- Do not make plugin upgrade mutate active Spacedock state.
- Do not bind the design to Conductor, Claude Code, Codex, Hermes, GitHub Projects, or Linear.
- Do not retain vendored canonical files merely for offline parity.
- Do not build automatic plugin installation or marketplace release automation.

## Acceptance criteria

- **AC-1** A newly adopted repository can execute every supported profile and stage from installed plugin resources without repository copies of canonical kernel, profile, reference, loader, or guard files.
- **AC-2** An active stage remains bound to its starting plugin version and contract digest, while the next stage uses a compatible installed upgrade.
- **AC-3** An incompatible upgrade fails before next-stage dispatch and identifies the README or local mod refit required.
- **AC-4** Adoption and upgrade preserve repository-owned README policy, local mods, and Spacedock state, changing only accepted refits.
- **AC-5** The migration removes obsolete vendored files and parity machinery without weakening profile routing, close guards, or kernel authority.
- **AC-6** The runtime-resolution contract is host-neutral and demonstrably usable from Spacedock tracks in repository worktrees.
- **AC-7** Goal-sufficiency and without-it evidence show that every retained mechanism is necessary and that the result is smaller than the current adoption footprint.

## Ideation proof required

Compare the current vendored route with direct installed-plugin resolution at the exact stage boundary. Specify resource discovery, version/digest pinning, compatibility refusal, migration and rollback, the minimum retained repository surface, and falsifiers for AC-1 through AC-7 before implementation begins.
