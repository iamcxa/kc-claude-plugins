---
id: e9nrdgxgnp1rqwwbcxfzb1nj
title: "kc-dev-flow: adopt a proportional RoboRev implementation exit"
status: backlog
source: captain:conversation-2026-08-13
product: kc-dev-flow
sprint: S2
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design:
lane:
---

## Problem

The workflow needs an implementation-exit review that catches material defects before Draft PR creation without repeating the author’s own heavyweight PR review after the Draft exists. A repository-configured RoboRev review can provide exact-tip evidence, but adopting it indiscriminately would make POCs pay for production-grade panels and would turn tool absence into a workflow blocker. The task must define a proportional, optional RoboRev path with an honest fallback while preserving fresh behavioral validation, external GitHub feedback reconciliation, and Captain delivery authority.

## Proposed approach

## Design determination

## Acceptance criteria

## Test plan

## Measurement

## Doc diff

## Out of scope
