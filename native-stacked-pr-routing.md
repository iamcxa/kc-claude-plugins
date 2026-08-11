---
id: c6wj65396r1s42330e19dweg
title: Align PR merge policy and route oversized changes to native stacks
status: ideation
source: captain directive 2026-08-11
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

The adopted PR merge mod is a custom artifact protocol that the released
Spacedock runtime does not consume. It also describes stacked delivery only
qualitatively and does not identify GitHub's native stack topology or CLI.

## Proposed approach

Replace the custom mod with the released Spacedock 0.26.0 `pr-merge` v0.12.2
contract plus one bounded local routing section. Preserve Draft PR delivery,
remove only artifact machinery with no released consumer, and use numeric change
shape only to require a topology decision.

## Design determination

Design is required because a single entity may need multiple dependent PRs and
because line-count policy can be gamed. The accepted topology is GitHub native:
the bottom PR targets trunk and every higher PR targets the branch below.

Ideation EM route: `narrow`. The narrowed design defines merge-base measurement,
keeps mechanical volume in the observed total, makes semantic seams override
numeric thresholds, and records the top PR as the entity's tracked `pr` after
the captain approves all Draft PR bodies.

## Acceptance criteria

**AC-1 — The adopted merge hook executes against Spacedock 0.26.x and contains
only a bounded local Draft/native-stack extension to released `pr-merge`
v0.12.2.**
Verified by: compare the retained upstream body byte-for-byte after removing the
marked local extension, then exercise `spacedock merge guard` over its released
fixtures. Falsified by: an unreleased `spacedock gate` command or unrelated local
artifact protocol remains.

**AC-2 — Native stacks have one unambiguous topology and command surface.**
Verified by: adversarial examples distinguish a native dependent stack, parallel
PRs, and an atomic single PR; `gh stack link --help` supports the named command.
Falsified by: `gh pr link`, a higher PR targeting trunk, or an independent PR
being called a stack.

**AC-3 — Delivery-shape thresholds trigger judgment without becoming quality or
minimality scores.**
Verified by: the contract measures merge-base additions plus deletions and
changed files at review request, routes `>1500` gross lines or `>20` files to a
stack decision, and requires a stack below the thresholds when two dependent,
independently green layers exist. Falsified by: counts authorize deletion,
compression, relabeling, weakened tests, or a fake layer.

**AC-4 — An inseparable change can remain one PR only through a visible,
reviewer-acknowledged exception.**
Verified by: the Draft PR body names why no layer can be independently reviewed
and verified and identifies mechanical/generated volume separately without
subtracting it from the trigger. Falsified by: an author silently bypasses the
decision or generated volume automatically exempts the PR.

**AC-5 — Removed artifact machinery has no remaining released-runtime or
repository consumer.**
Verified by: a repository-wide search has no `pr_artifact_v1`, terminal
transaction marker, or obsolete test reference; state recovery fails closed
without inventing an artifact. Falsified by: a shipped skill, workflow, script,
template, or runbook still consumes the removed field.
