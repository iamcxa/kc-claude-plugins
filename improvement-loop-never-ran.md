---
id: r9jtmpwnd1kd1ypscr41n635
title: "kc-dev-flow: the improvement loop's adopter half has never run — decide whether to wire it or retire it"
status: ideation
source: "README fact-check of kc-dev-flow, 2026-08-20. `references/improvement-harvesting.md` has been unreachable from any adopter since #249; archaeology showed #218 extracted it from `continue-dev-flow` and two later refactors deleted the two prose pointers that stood in for a declaration. This repo has 4 `_debriefs/` and no `_improvements/`, so the loop has produced nothing here either."
product: kc-dev-flow
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
---

## Problem

The improvement loop is specified across three files and wired in none.

**Producer half — `references/improvement-harvesting.md`.** On an explicit request only, read
`_debriefs/` newer than the `_improvements/state.yaml` cursor (at most three per run, older ones
retired as `skipped_superseded`), classify at most one candidate as repository-local or
reusable-kernel, and advance the cursor inside the same single-writer transaction that writes the
handoff — both or neither. A reusable candidate becomes a sanitized
`kc-dev-flow-improvement-handoff/v1` file sent to the source.

**Consumer half — `promote-dev-flow` + `scripts/improvement-intake.py`.** Requires those handoff
files, validates them, classifies placement, gates on the Captain. This half is covered:
`improvement-intake.test.py` runs inside `scripts/kc-dev-flow-contract-test.py`, a required check.

The producer half is unreachable, and it appears never to have run:

- No file names `references/improvement-harvesting.md` anywhere in the repository.
- No stage contract declares it as a `kc-dev-flow-conditional-references/v1` entry, so the loader's
  `check_conditional_references` never demands it and never emits it.
- `adopt-dev-flow` step 2 does not vendor it, and this repository's own self-adoption
  (`docs/dev/_mods/`) does not carry it — every other reference is there.
- `continue-dev-flow` says only "Load improvement harvesting only on an explicit request" — no
  filename, no path — while the same skill forbids reading an installed-package fallback.
- `promote-dev-flow` says the producer contract is `continue-dev-flow/SKILL.md`, which contains
  zero occurrences of `improvement-handoff`, `failure_shape`, or `source_policy_revision`.
- This repository holds four `_debriefs/` records and no `_improvements/` directory. No handoff
  artifact exists anywhere in the tree.

### How it broke

| When | Commit | Effect |
|---|---|---|
| 2026-08-09 | `97e3d259` | `promote-dev-flow` created. Its "producer contract is `continue-dev-flow/SKILL.md`" pointer was correct: that skill then carried the handoff shape in four places. |
| 2026-08-13 | `3e28d4a7` (#218) | Extraction. 214 lines left `continue-dev-flow`; `improvement-harvesting.md` was created with 159. The commit never touched `promote-dev-flow`, so its pointer went stale the moment it landed, and the new file was never added to the adopt vendor list. Two paths survived: a `## Self-improvement` section in `kernel.md` that did not name the file, and one line in the package README that did. |
| 2026-08-14+ | `cbeec9d4` (#249) | Profile-native rewrite. `kernel.md` went 327 → 76 lines and lost `## Self-improvement`; the README was rewritten without the named pointer. The last path disappeared. |

Nothing caught it because harvesting is request-triggered, not stage-triggered. The loader fails
closed only on references a stage contract declares, so #218 was right not to declare it — and that
same correctness put it outside the only mechanism that would have failed. The contract test pins
prose in the README and skills but asserts nothing about harvesting or the producer pointer. The
consumer half stayed green throughout, so from the source side the loop looked healthy.

### Adopter sweep, 2026-08-20

Three repositories carry kc-dev-flow. No single one holds both the wiring and the input.

| Repository | Vendored | `_debriefs/` input | Handoffs produced |
|---|---|---|---|
| `kc-claude-plugins` (source) | no | 4 records | none |
| `carlove-v1/krakow-v1` | **yes**, 8.9K, linked three times from its workflow README | none | none |
| `subspace-relay` | no — vendor set predates 3.0 — but its workflow README names the file | — | none |

No `_improvements/` directory exists on this machine. The chain is intact in exactly one
repository, and that repository has nothing to feed it.

`carlove-v1/krakow-v1`'s own 3.0.0 upgrade audit reached this finding independently:
"`improvement-harvesting.md` — declared by nothing; outside the loader-enforced set. It is where
the deleted kernel Self-improvement section went." An adopter saw the defect, recorded it locally,
and had no route to send it upstream — because the route is this loop.

The sweep changes the retire branch's cost: one adopter holds a vendored copy, so retirement
removes published surface a real repository depends on rather than deleting an unused file.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v2
  selected: pilot-product-slice
  recommended: production
  basis: >-
    Audience is three known repositories, all Kent's own. Lifespan is ongoing — whatever is
    decided becomes published plugin contract. Persistent state is the vendored reference plus
    one adopter's copy. The mutation boundary is documentation and skill contracts only; no
    production data, credentials, destructive external mutation, or irreversible migration.
    Recommendation was production because a vendored adopter copy puts public compatibility in
    scope; the Captain selected pilot on the judgment that the adopter surface is self-owned and
    the compatibility risk is absorbable without a release-stage rollout proof.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Decide keep or retire before any repair; the four broken pointers all presuppose keep.
      - If keep, name the enforcement point for a request-triggered reference — the class the
        loader's declaration mechanism does not cover.
      - Name which file owns the handoff shape, and make the other two point at it.
    implementation:
      - Change only the producer half and its pointers. Leave improvement-intake.py validation,
        the handoff schema, and promote-dev-flow's classification and Captain gate untouched.
      - Carry the decision to the one adopter holding a vendored copy.
    testing:
      - Any check added must be proven by mutation, not inspection — break each link and show
        the check fails with its own message.
      - A green check that would still pass with the chain broken is the defect being repeated.
  scope_boundary: >-
    Excludes a release-stage rollout, rollback, and ownership proof; excludes changing the
    handoff schema or the consumer half; excludes repairing adopters other than recording what
    they must do.
  promote_when:
    - A repository outside Kent's own set is found with the reference vendored.
    - Retire is chosen and an adopter is found to depend on the removed surface at runtime.
    - The decision requires changing improvement-intake.py or the handoff schema after all.
  decision:
    authority: Kent (Captain)
    at: 2026-08-20T08:18:16Z
```

## Shape — reverse recovery

`brownfield_capability_change` is true: this work proposes to repair or remove an existing
capability. Audit per `_mods/reverse-recovery-audit.md`.

```yaml
reverse_recovery:
  trigger: repair or removal of the adopter-side improvement producer
  boundary: >-
    Journey — an adopter turns an unseen debrief into a handoff the source ingests. Searched
    kc-claude-plugins, and every kc-dev-flow adopter reachable on this machine
    (~/conductor/repos, ~/conductor/workspaces, ~/Project). Not searched: any clone outside
    this machine.
  layers:
    - surface: producer procedure
      location: kc-dev-flow/references/improvement-harvesting.md
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: >-
        Procedure is complete prose and is the only definition of the handoff shape, but no
        adopter can resolve it — undeclared, unvendored by the source repo, unnamed by
        continue-dev-flow, and package fallback is forbidden.
      disproof_hook: a second authoritative definition of kc-dev-flow-improvement-handoff/v1
    - surface: reachability binding
      location: MISSING
      completeness: MISSING
      need: REQUIRED
      evidence: >-
        Two strategies — filename grep across the repo, and a scan of every
        kc-dev-flow-conditional-references/v1 block plus kernel.md — both empty.
      disproof_hook: the loader emitting the file for any profile-stage combination
    - surface: producer-contract pointer
      location: kc-dev-flow/skills/promote-dev-flow/SKILL.md:16
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: credits continue-dev-flow/SKILL.md, which has zero occurrences of the shape
      disproof_hook: grep the three field names in that skill and get a non-zero count
    - surface: consumer half
      location: kc-dev-flow/scripts/improvement-intake.py
      completeness: WORKING_UNIT_UNPROVEN
      need: REQUIRED
      evidence: its test runs in a required check, but it has never processed a real handoff
      disproof_hook: any kc-dev-flow-improvement-handoff artifact on disk
    - surface: cursor state
      location: MISSING
      completeness: MISSING
      need: NO_OBSERVED_CONSUMER
      evidence: no _improvements/ directory in any adopter; nothing reads a cursor that never existed
      disproof_hook: find -type d -name _improvements returning a hit
  decision: recover
```

The circularity is worth naming: `promote-dev-flow` needs handoffs, handoffs exist only to feed
`promote-dev-flow`, and neither side has ever fired. That makes both halves unproven together, not
a working consumer with a broken producer.

### Why the original move lost reachability

`_archive/product-first-continuation.md` (#218) accepted: "Improvement harvesting remains available
only through an explicit trigger." It moved the procedure "byte-for-byte" — a move that preserves
content and not reachability — and explicitly ruled out the obvious mechanism: "Do not create a
second skill." So the reachability mechanism was rejected without a replacement being named. The
defect is that omission, not the extraction.

## Accepted outcome and non-goals

**Accepted journey.** This repository harvests one of its four real `_debriefs/` records and
produces the first `kc-dev-flow-improvement-handoff/v1` artifact that has ever existed, which
`improvement-intake.py` then accepts. Limited user: this repository. End-to-end value: the loop
that carries adopter findings upstream runs once for real.

The slice is chosen because the two halves of the evidence sit in different repositories —
`kc-claude-plugins` has the input and no vendored copy, `carlove-v1/krakow-v1` has the vendored copy
and no input. Vendoring here is the only place both exist.

**Persistent state.** `_improvements/state.yaml` in the state checkout, holding
`newest_processed_debrief`. It is created by this slice. The cursor and the handoff are one write
unit under the existing Spacedock single-writer transaction: if both cannot be written safely,
neither is.

**Recovery and data safety.** The four debriefs are immutable inputs and are never modified. A
failed or aborted run leaves no cursor and no handoff, so a rerun is a first run. A handoff is a
file the Captain hands over; nothing uploads, posts, or fetches an adopter repository.

**Non-goals.** No change to `improvement-intake.py`'s validation, the handoff schema, or
`promote-dev-flow`'s classification and Captain gate. No second skill (#218 ruled that out and
nothing since changes that). No release-stage rollout proof. No repair of the other two adopters
beyond recording what they must do. Not a general redesign of request-triggered references — this
slice needs one reachability mechanism that works, and a broader rule can be lifted from it later
if a second case appears.

## Acceptance evidence

1. One handoff produced from a real debrief in this repository and accepted by
   `improvement-intake.py`. Baseline is zero artifacts in existence.
2. `_improvements/state.yaml` exists afterward with `newest_processed_debrief` set to the consumed
   record, and a second run consumes nothing.
3. The reachability mechanism fails closed: with the binding removed, the harvest request stops with
   a named error instead of silently doing nothing. Proven by mutation.
4. The producer-contract pointer in `promote-dev-flow` resolves to the file that actually defines
   the shape, and a check fails when it does not. Proven by mutation.

Each of 3 and 4 must fail with its own message. A check that still passes with the chain broken is
this defect repeated.

## Measurement

Handoffs produced per adopter per month, against the current baseline of zero. A repair that leaves
that number at zero has restored a pointer, not a capability.
