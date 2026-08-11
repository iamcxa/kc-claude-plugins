---
title: Keep the release smoke fixture version-independent
status: validation
source: Release PR #202 required-check failure after #203 merged; captain authorized continuing through release
product: kc-dev-flow
sprint: S1
design: trivial-pass
lane: defect
started: 2026-08-11T07:39:56Z
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/release-pr-smoke-fixture-fix
pr: ""
id: 0bk09wbq8j7y6fec41ptg9kk
---

The published-mode contract fixture hard-codes `kc-dev-flow-v2.2.0`, so a correctly version-bumped Release PR fails before exercising its identity falsifiers. Derive fixture identity from the manifests under test while leaving the production smoke and its strict published-tag checks unchanged.

## Bounded known-defect route

- Root cause: `scripts/kc-dev-flow-contract-test.py:107,220,432-474` injects the `2.2.0` literal into an otherwise version-derived candidate receipt.
- Mechanical AC: the contract test fails in a parity-clean simulated `2.3.0` Release PR tree before the change and passes afterward.
- Seam: one deterministic fake-runtime fixture in one existing file; no production, schema, host, or release configuration change.
- Design: no choice remains after the failure is reproduced; the tested manifests are the single compatible source of fixture version identity.
- Appetite: one dispatch, 20 minutes with 10 minutes tolerance; stop on a second file or any production-smoke change.

## Stage Report: implementation

- DONE: Reproduce the release-version mismatch before changing the fixture
  RED: a parity-clean simulated `2.3.0` tree exited 1 with `published tag version differs from manifests: 2.2.0 != 2.3.0` before source and installed-tree falsifiers could run.
- DONE: Make the fixture version-independent at the bounded seam
  `scripts/kc-dev-flow-contract-test.py` maps to the Mechanical AC and one-file seam: commit `5e5c5f646a2ca401121b39eeac2628de685eb51f`, `+10/-9`, derives the tag from tested manifests, and preserves tag, version, source, Claude-tree, and Codex-tree falsifiers; production smoke is unchanged.
- DONE: Verify the exact implementation head and prepare fresh validation
  Current-tree and simulated-`2.3.0` contracts, marketplace L0/L1/L2, version parity, 40-file frontmatter lint, and diff check passed; the product worktree was clean at the exact head.

### Summary

The smallest sufficient change touched one existing fixture file and left production release identity enforcement intact. Without it, every future version-bumped Release PR would fail on the stale fixture tag before exercising the five intended falsifiers.
