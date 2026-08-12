---
title: "kc-dev-flow: route product work before improvement harvesting"
status: ideation
source: "captain:conversation-2026-08-12-third-slice"
product: kc-dev-flow
sprint:
started: 2026-08-12T08:28:54Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design: required
lane: main
id: gpvz6779wyexg9k9xtn19zbb
---

## Problem

The ordinary continue-dev-flow path loads 1,143 of its 1,643 words before product routing to scan debriefs, maintain improvement cursors, and prepare handoffs. The authoritative state currently contains four debriefs and no _improvements files, so every continuation pays a large coordination cost without a demonstrated ordinary-path consumer.

## End value

An adopted repository with an active product item reaches product routing without reading or writing _debriefs or _improvements. Improvement harvesting remains available only through an explicit trigger and preserves the existing bounded evidence, validator, handoff, and captain-authority guarantees.

## Observed baseline

- continue-dev-flow/SKILL.md: 208 lines / 1,643 words.
- Pre-product improvement block: 150 lines / 1,143 words.
- Product-routing portion without that block: 58 lines / 500 words.
- State holder: four debriefs and zero improvement files.
- PR #216 supplies exact-ref evaluation support; this slice must use it to judge a real subtraction rather than expand a general harness.

## Scope boundary

Preserve improvement-intake.py, the handoff schema, promote-dev-flow, debrief evidence, source-side placement judgment, and every prohibition on automatic task creation, scheduling, posting, merge, or product pause. Compare exact baseline and candidate behavior with fresh-context pressure at the real skill/runtime boundary.

## Proposed approach

To be shaped during ideation.

## Design determination

Required: this changes activation and ownership of an adopter-side skill path.

## Acceptance criteria

To be authored during ideation as value or hard-invariant criteria with external falsifiers.

## Test plan

To be shaped during ideation. It must cover ordinary product routing, unseen debriefs, unavailable compare-and-swap, reusable-source proposals, and no committed work.

## Measurement

Safety and authority are lexicographically first. Then compare time to first product action, policy input, tool calls, state writes, captain interruptions, and wall time.

## Doc diff

To be determined from the smallest accepted route.

## Out of scope

A general model runner, all-stage runtime shadow, v0 workflow rewrite, active-history compaction, new improvement schema, provider-specific policy, and changes to Spacedock itself.
