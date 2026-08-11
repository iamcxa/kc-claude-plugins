---
title: Keep the release smoke fixture version-independent
status: implementation
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
