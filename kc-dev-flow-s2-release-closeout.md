---
id: tgta74m7bxs4jypvs2mvwwnt
title: "Close kc-dev-flow S2 through Release PR #221"
status: validation
source: "Captain-approved S2 release closeout after all four implementation tasks exited, 2026-08-14"
product: kc-dev-flow
sprint: S2
started: 2026-08-14T14:59:28Z
completed:
verdict:
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.context/worktrees/kc-dev-flow-s2-release-221-aad7
issue:
pr: pr-merge:221
mod-block:
design: required
lane: main
---

## Problem

All four Captain-approved kc-dev-flow/S2 implementation tasks have exact-revision validation and merged delivery evidence, so the Roadmap release hold is clear. Release PR #221 now owns the generated version, changelog, manifest, and marketplace bytes, but no active task binds its exact candidate, pre-publication compatibility receipt, Captain merge authority, published tag identity, or final S2 closeout. Releasing without that task would make the irreversible tag boundary depend on session memory.

## Proposed approach

Treat the existing release-please PR as one validation-and-delivery artifact. Bind its exact head and intended kc-dev-flow version, run the existing candidate smoke once through isolated installed Claude and Codex hosts, reconcile complete GitHub-native feedback and required checks, obtain Captain merge authority, then reuse the closed candidate receipt in published mode without another model call. Terminalize only after the tag, version, package tree, installed trees, and Roadmap S2 exit all agree.

## Design determination

Validation-only release closeout. Release-please owns version and tag generation; this task introduces no product design, implementation branch, second release PR, retry loop, provider matrix, or alternate publication mechanism.

## Acceptance criteria

**AC-1 — The release candidate is one closed exact-revision artifact.**
Verified by: PR #221 has one exact head, one intended kc-dev-flow version, manifest/marketplace/plugin parity, an attributable diff, and a candidate receipt whose revision and package tree match that checkout.
Falsified by: head drift, mixed versions, extra release scope, malformed receipt, or receipt identity that differs from the checkout.

**AC-2 — Publication is not the first host-compatibility observation.**
Verified by: one bounded candidate smoke installs and invokes the exact checkout through isolated Claude and Codex state and both closed reports pass.
Falsified by: either host is skipped, uses ambient installed state, returns an invalid report, or requires an unapproved retry.

**AC-3 — Merge remains Captain-owned and externally reviewable.**
Verified by: exact-head required checks and complete GitHub-native feedback are green, every retained item has an evidenced disposition, and Captain explicitly authorizes merge.
Falsified by: silence, provider evidence, stale feedback, pending or failed required checks, or a changed head being treated as authority.

**AC-4 — The published artifact is the validated candidate.**
Verified by: the containing kc-dev-flow tag, declared version, source package tree, Claude installed tree, and Codex installed tree all match the preserved candidate receipt; published mode makes no model call.
Falsified by: any tag/version/tree mismatch, missing publication, or published-mode provider invocation.

**AC-5 — S2 closes only after authenticated release evidence.**
Verified by: the release PR is merged, the published receipt passes, the task terminalizes through Spacedock, and Roadmap S2 has no remaining implementation or release-closeout work.
Falsified by: closing on PR creation, candidate smoke alone, a tag without published smoke, or an active S2 task remaining.

## Test plan

- Re-run repository version parity, relevant contract checks, diff validation, and complete GitHub feedback observation at the exact Release PR head.
- Run exactly one candidate-mode dual-host smoke, bounded to 20 minutes with no automatic retry.
- After Captain-authorized merge and tag publication, run published mode against the preserved receipt without invoking a model.
- Re-read GitHub, tag, installed trees, state branch, and Roadmap before terminalization.

## Measurement

Record exact PR head, target version, candidate and published receipt identities, host verdicts, package-tree hashes, CI duration, feedback fingerprint, merge commit, tag, and elapsed live-smoke time. Provider cost remains unknown unless the provider reports it; zero reported cost is not a zero-cost claim.

## Doc diff

No product doc edit is planned. The already-merged Roadmap declares the S2 release hold and exit; this task supplies the missing release evidence and state closeout.
