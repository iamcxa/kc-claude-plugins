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

## Work profile decision request

**NEEDS_PROFILE_DECISION — recommend `Production` (`production`).**

Basis: at `origin/main@6f0e274e6e02ff7e0e5b158859783df037c45c4d`,
this task changes the retained implementation-exit contract of a marketplace-
published plugin for external repository adopters. The evidence is bound to an
exact implementation revision and influences whether delivery may proceed to a
Draft PR. Provider absence and failure therefore need durable truthful behavior,
and the changed contract carries compatibility, release, rollback, and ownership
obligations. It still grants RoboRev no validation, feedback-reconciliation,
push, Ready, merge, or terminalization authority.

The Captain must choose one of these exact profiles before acceptance criteria
or the approach below are expanded:

| Choice | Architecture and implementation delta for this task | Testing, scope, and proof delta |
|---|---|---|
| `POC / Exploration` (`poc-exploration`) | Restrict the work to one disposable local-repository experiment using the shortest safe manual RoboRev seam and an explicit no-run result; publish no adopter compatibility or release contract and name cleanup. | Prove owned result handling, the riskiest current RoboRev capability/failure assumption, and one real exact-tip journey. Record host, release, upgrade, and broader compatibility as unproved. This requires a Captain-owned cut of the current published-adoption outcome. |
| `Pilot / Product slice` (`pilot-product-slice`) | Ship an opt-in repository-native seam for limited known adopters, with diagnostics and recovery for expected unavailable, skipped, failed, and stale-result paths; keep shortcuts and supported environments explicit. | Exercise the real integration seam, one installed-host end-to-end journey, tool-absent and provider-failure fallback, and retry/recovery behavior. Broad host/version compatibility and release/rollback support remain outside the accepted commitment. |
| `Production` (`production`) — recommended | Keep one released repository-configured evidence seam with explicit lifecycle, compatibility, failure, ownership, upgrade, and rollback boundaries. Reuse the existing stage report/work item; add no daemon, second ledger, generalized evaluator, or automatic merge. | Prove exact-revision PASS/non-pass honesty, tool absence, provider failure/skips, stale evidence rejection, supported installed-host behavior, and exact-release/rollback behavior, while separately preserving fresh validation and GitHub-native feedback reconciliation. |

Shared invariants for every choice: a run that did not happen is never green;
RoboRev is a review sensor rather than workflow authority; fresh behavioral
validation, optional repair tooling, complete GitHub-native feedback observation,
and Captain delivery authority remain separate. No receipt is recorded until the
Captain selects a profile and the authorized actor commits, syncs, and re-reads it.

## Proposed approach

## Design determination

## Acceptance criteria

## Test plan

## Measurement

## Doc diff

## Out of scope
