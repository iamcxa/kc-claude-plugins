---
title: "kc-dev-flow: correct mod adoption path and enforce mechanism necessity"
source: "Captain directive `修 bug + 183`, GitHub issue #183, 2026-08-10"
product: kc-dev-flow
sprint: captain-directed
design: required
id: 9f63nm17bntn0ts7k9b1nm9c
status: implementation
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/fix-kc-dev-flow-path-necessity
---

## Problem

The canonical reverse-recovery mod tells adopters to copy it into
`docs/ship-flow/_mods/`, although kc-dev-flow binds mods under each adopted
workflow's own `_mods/` directory. Separately, kernel's mechanism-necessity rule
has no local rejection predicate, so a new control can pass ideation without
naming the AC it serves, the simpler alternative, or an escaped defect.

The captain authorized this bounded repair together with issue #183. The
published-tag smoke review remains a separate unscheduled follow-up.

## End value

An adopter is directed to the selected workflow's local `_mods/` directory,
and this repository's ideation gate refuses a proposed control mechanism until
its necessity is reviewable. Speculative controls also leave a dated removal
review in the existing work-item authority.

## Scope

Two policy surfaces:

1. Correct the reverse-recovery mod's portable adoption instruction in the
   canonical and self-adopted copies, with one semantic regression assertion.
2. Add one local ideation rejection predicate for gates, checks, harnesses,
   automations, and registries. Reuse backlog seeds for speculative review.

No new registry, script, CI job, required context, kernel clause, or change to
the separate published-tag smoke review is in scope.

## Reverse-recovery audit

Against `origin/main` at `bd81be0081911639e5930be896eea5bb3ba23bb5`:

| Layer | Classification | Need | Evidence |
|---|---|---|---|
| Portable mechanism-necessity rule | WORKING_UNIT_UNPROVEN | REQUIRED | `kc-dev-flow/references/kernel.md` requires criterion, alternative, and insufficiency, but local ideation has no refusal predicate. |
| Local ideation gate | EXISTS_BROKEN | REQUIRED | `docs/dev/README.md` already owns local judgment; issue #183 records #178 passing without a necessity record. |
| Existing absolutes registry/check | WORKING_UNIT_UNPROVEN | REQUIRED | `scripts/kc-dev-flow-contract-test.py` invokes `absolutes-check.py`; required CI invokes the contract test. Issue #183's unwired premise is stale. |
| Work-item authority | WORKING | REQUIRED | Spacedock backlog already holds `kc-dev-flow-published-tag-smoke-review.md` as a dated review seed pattern. |
| Mod distribution path | EXISTS_BROKEN | REQUIRED | `reverse-recovery-audit.md` hard-codes `docs/ship-flow/_mods/`; `continue-dev-flow` reads only the adopted workflow's named local `_mods/`. |

No greenfield layer is required. The cheapest compatible seam is the existing
ideation gate plus the existing work-item authority.

## Options and decision

- **Take:** add one ideation rejection predicate and require a referenced
  backlog review seed only for speculative controls.
- **Do not take:** issue #183's proposed second content-hash registry and CI
  wiring. The cited wiring gap has already been closed, and another registry
  would duplicate the gate and work-item authorities.
- **Do not take:** a text-presence assertion for the ideation wording. Kernel
  says a text match cannot close a behavioral gate; validation will exercise a
  missing and a complete necessity record through a fresh reviewer instead.

Fastest path and smallest cut are the same: one local gate clause, one portable
path correction, and one semantic regression assertion in the existing suite.

## Necessity records

**Ideation refusal predicate**

- `Criterion:` AC-2.
- `Alternative:` leave the kernel rule as guidance; insufficient because #178
  passed the workflow without any of its three required facts.
- `Escape:` #178 would have been returned unread because it named no criterion,
  simpler alternative, or past escape/speculative review.

**Adoption-path regression assertion**

- `Criterion:` AC-1.
- `Alternative:` change only the prose; insufficient because byte parity can
  keep two copies identically wrong, as the current defect demonstrates.
- `Escape:` mutate the corrected header back to `docs/ship-flow/_mods/`; the
  existing contract suite must fail before distribution.

## Design determination

`required` — this changes the local ideation gate contract. The accepted shape
is a necessity record with `Criterion`, `Alternative`, and `Escape`. `Escape`
names a past defect proved by mutation; when none exists it instead records
`speculative until YYYY-MM-DD; review <work-item ref>`, and removal is the
default at that review.

## Acceptance criteria

**AC-1 — Adoption path is workflow-local.**

The canonical and self-adopted reverse-recovery mods direct adopters to the
adopted workflow's `_mods/reverse-recovery-audit.md`, carry version `0.2.1`, and
remain byte-identical. Verified by: a RED-before-GREEN assertion in
`scripts/kc-dev-flow-contract-test.py`, the full contract test, and the
absolutes registry check it invokes.

**AC-2 — Necessity can stop ideation.**

A proposed control mechanism missing any required necessity fact is returned
unread; a complete past-escape record passes accounting; a speculative record
also requires a date and work-item reference. Verified by: a fresh-context
Claude Opus high exercise over three adversarial ideation packets, naming the
exact changed revision and the result that would fail the exercise.

**AC-3 — No parallel enforcement system is added.**

The diff adds no mechanism registry, new executable, workflow step, or required
context. Verified by: exact diff classification against `origin/main`, live
branch-protection read, and the existing version-parity/contract suites.

## Test plan

1. Add an assertion that the header contains the exact workflow-relative
   backticked destination `_mods/reverse-recovery-audit.md`; run the scoped
   contract test and expect RED on the current ship-flow-prefixed path.
2. Correct and version both copies without updating the absolutes registry;
   rerun and expect the existing registry check to RED on the changed block.
3. Update the existing absolutes registry and rerun the contract test: expected
   GREEN.
4. Exercise the ideation clause with #178's actual incomplete proposal, a
   past-escape record, and a speculative record through fresh Claude Opus high.
5. Run the full contract and version-parity suites once at stage exit.

E2E skip: this is a docs/policy-only task. Its behavioral proof is the
fresh-reviewer gate exercise; no product runtime or external consumer report
originated the accepted problem.

## Appetite and dispatch

One worker session, 45 minutes; stop and re-cut beyond 70 minutes or if the
change needs a new script, registry, CI step, or kernel edit. No spike needed:
the existing ideation gate, work-item authority, contract test, and required CI
path are live and were read directly.

## Pre-mortem

If this ships exactly per spec and still fails, the likely cause is criteria
that pass without delivering value: a reviewer may echo the required fields
without actually refusing an incomplete packet.

## Measurement

- Baseline: issue #183 records one control (#178) that passed without a
  necessity record.
- Target: 3/3 adversarial packets receive their specified disposition.

## Doc diff

- Reverse-recovery header: replace the ship-flow-specific destination with the
  adopted workflow's local `_mods/` destination.
- Ideation stage: add the necessity-record refusal predicate and speculative
  review-seed requirement.

## Out of scope

Changing kernel policy, adding a registry or CI step, reopening issue #178,
executing the published-tag smoke review, release version edits, and merge.

## Stage Report: ideation

- DONE: Reproduce both defects and bind their causes to `origin/main`
  `bd81be0081911639e5930be896eea5bb3ba23bb5`.
  The path came from the original ship-flow-specific copy; byte parity preserves
  the error. The mechanism rule exists in kernel, but local ideation has no
  refusal predicate.
- DONE: Recheck issue #183's enforcement premise.
  `scripts/kc-dev-flow-contract-test.py` invokes `absolutes-check.py`, required
  CI invokes that contract test, and live branch protection requires the job
  context. A second registry or CI step is therefore rejected.
- DONE: Select the smallest sufficient route.
  Reuse the ideation gate and work-item authority, correct the portable path,
  and add one assertion to the existing contract suite. No new authority or
  executable surface is introduced.
- DONE: Define falsifiable ACs and the control mechanisms' own necessity
  records.
  AC-1 has a mutation RED/GREEN; AC-2 has three fresh-reviewer packets; AC-3 has
  an exact diff and live required-context read.
- DONE: Complete ideation discipline.
  Captain-authored scope, design decision, reverse-recovery audit, appetite and
  tolerance, cheap path, rejected alternatives, doc diff, one-worker sizing,
  E2E skip reason, and pre-mortem are recorded.
- DONE: Obtain fresh-context EM judgment.
  Claude Opus high reviewed the exact `bd81be0` plan and returned `proceed`
  with confidence 0.82. It found the five-file diff minimal and required three
  zero-surface refinements: assert presence of the correct relative path,
  preserve the stale-registry intermediate RED, and use #178's actual proposal
  as the incomplete packet. All three are incorporated above.

### Summary

Proceed with the existing ideation gate as the enforcement point. A control
mechanism must name `Criterion`, `Alternative`, and `Escape`; speculative
controls also name a date and backlog review reference. Correct the mod's
workflow-local adoption path and protect that distribution contract in the
existing suite.
