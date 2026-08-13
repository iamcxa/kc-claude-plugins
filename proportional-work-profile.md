---
id: 4wkne0vvpgsy2japzr08xqtx
title: "kc-dev-flow: choose a proportional work profile before AC expansion"
status: backlog
source: captain:conversation-2026-08-13
product: kc-dev-flow
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design: required
lane: main
---

## Problem

The current ideation contract can expand acceptance criteria, architecture, and tests as if exploratory work were a production commitment. This makes POCs slower and can replace an adequate shell or off-the-shelf solution with structure unrelated to the experiment's value.

## Proposed approach

Add a conditional `kc-dev-flow:choose-work-profile` skill before acceptance-criteria expansion. It reads project context, recommends one of three profiles, and asks the Captain through the host's best structured question UI, with one concise plain-chat fallback only when no structured surface exists:

- `POC / Exploration`: prove a real journey quickly; prefer disposable, off-the-shelf, shell, or CLI mechanisms; test owned logic, critical risks, and one real end-to-end path.
- `Pilot / Product slice`: support limited real use and likely iteration; require diagnostics, retryability, data safety, and tests for real seams without solving hypothetical scale.
- `Production`: accept long-term operational commitment; require relevant lifecycle, compatibility, recovery, observability, integrity, and release evidence.

Store a compact work-profile receipt in the existing task body and let normal ideation derive scope, ACs, and tests from it. Do not add a lifecycle stage, parallel tracker, or profile-specific framework mandate. Secrets, permissions, spend, destructive actions, production data, external mutations, evidence honesty, cleanup, and irreversibility remain hard invariants at every profile.

## Design determination

Pending ideation. The Captain approved the three-profile model; ideation must refine activation, receipt shape, promotion triggers, and falsifiable evaluation without reopening the number of levels.

## Acceptance criteria

Pending ideation.

## Test plan

Use frozen paired scenarios across all three profiles, including an adversarial task labeled POC that touches production secrets or external mutation. Verify that scope and proof obligations change proportionally while hard invariants do not.

## Measurement

Measure unnecessary AC count, prescribed implementation surface, required test surface, safety-invariant retention, profile-selection accuracy, and end-to-end task success under the installed loader. Keep model sampling bounded and treat non-deterministic pass rates statistically rather than requiring 100% identical outputs.

## Doc diff

Expected to update the kc-dev-flow skill/reference contract and the adopted docs/dev copies required by repository parity.

## Out of scope

A new lifecycle stage, language-specific mandates, relaxing authority or safety boundaries, and a general-purpose eval platform.
