---
title: Review the published-tag Science Officer runtime smoke
status: implementation
source: Captain-approved issue #183 follow-up, 2026-08-10
product: kc-dev-flow
sprint: S1
design: required
id: jj5jbzp2tpyc7a6x78wnfqky
lane: main
started: 2026-08-10T22:03:08Z
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/kc-dev-flow-release-batch
---

## Problem

The published-tag cross-harness smoke is intentionally speculative until the first kc-dev-flow release containing its packaged schema and prompt can exercise the clean-installed Claude and Codex surfaces. Without a durable review point, the harness could remain permanently after its claimed value fails to materialize.

## Review contract

After the first GitHub Release containing the smoke assets, run the authenticated exact-tag release smoke and preserve its receipt. Keep the harness only if it produces installed-runtime evidence unavailable from the existing post-install and marketplace helpers; otherwise remove it.

The captain scheduled this review in `kc-dev-flow/S1` as the first item in the
single-release batch.

## End value

Release closeout can prove that the exact published kc-dev-flow tag installs and
invokes through clean Claude and Codex plugin state, and that both hosts return
the complete EM compatibility record for that tag's commit.

## Smallest route and reverse-recovery audit

- `scripts/marketplace-verify.sh` is `WORKING` for current-checkout Claude
  marketplace resolution, but it does not bind an exact tag, invoke Codex, or
  validate the EM report.
- `kc-plugin-forge/scripts/post-release-sync.sh:38-68` is `WORKING` for copying a
  clean `main` checkout after release, but it neither checks a tag nor invokes a
  host.
- The v2.1.0 one-off exact-tag probe is `WORKING` evidence that clean-installed
  Claude and Codex can both invoke the skill, but it is not a reusable release
  check.

Keep one release-only wrapper around those real host CLIs. A per-PR matrix, new
CI job, new auth store, or reimplementation of plugin installation is outside
the route. The mechanism is required by AC-1; the cheaper existing helpers are
insufficient because none observes all four missing boundaries together.

## Design determination

`required` — this introduces a release-closeout command and a fail-closed report
contract. It runs only after a tag exists and before local install sync.

## Acceptance criteria

**AC-1 — The smoke is bound to one published artifact.**
Verified by: an exact-tag clone, exact revision lookup, and digest equality for
both installed plugin trees. Falsified by: a wrong revision or changed installed
tree makes the command fail.

**AC-2 — Both supported hosts exercise the installed skill.**
Verified by: isolated Claude and Codex plugin homes, operator authentication, and
one accepted EM report from each host. Falsified by: a missing, duplicate, or
implicit plugin load, or either host failing to return one report.

**AC-3 — The compatibility record is structural and exact.**
Verified by: direct negative fixtures for missing, extra, duplicated, misplaced,
invalid-enum, mismatched-wrapper, and wrong-revision data. Falsified by: any such
fixture being accepted.

**AC-4 — The check stays release-only and earns its maintenance cost.**
Verified by: the root release instructions place it after tag creation and before
local sync, with no per-PR workflow entry. Falsified by: wiring it into ordinary
PR CI, or the first released run producing no evidence beyond existing helpers.

## Test plan

Run the report fixtures without provider calls; run Claude plugin-isolation and
exact-tag install probes; run both hosts against one released tag; then run the
full kc-dev-flow contract, frontmatter, parity, marketplace, and link checks.

## Appetite and pre-mortem

One worker and one release-closeout command. Stop and re-cut if it needs a new
credential store, CI matrix, or provider abstraction. If this still fails after
release, the likely cause is that the wrapper validates its own files while one
host resolves a different installed plugin tree.

## Out of scope

Per-PR model calls, manual version edits, replacing marketplace verification or
post-release sync, and creating or merging a PR.

## Stage Report: ideation

- DONE: The captain scheduled the exact review obligation in `kc-dev-flow/S1`.
- DONE: Reverse recovery found two working but narrower helpers and one successful
  v2.1.0 experiment; one release-only dual-host wrapper is the smallest missing
  seam.
- DONE: AC-1..AC-4 name end value and concrete falsifiers; the route adds no CI,
  auth, registry, or installation authority.
- DONE: Fresh high-reasoning EM returned `narrow / high`: retain one
  release-closeout smoke, not a per-PR matrix. Multi-model review was not
  recommended.

### Summary

Proceed with one exact-tag, dual-host release-closeout smoke. Its first run from
a tag containing the command remains release evidence, not something local
validation can claim in advance.
