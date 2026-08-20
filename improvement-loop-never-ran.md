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

## Accepted outcome and non-goals

The first decision is whether the loop is wanted, not how to repair it. Four pointers can be fixed
in an afternoon; that is worth doing only if an adopter is actually expected to produce handoffs.
Zero handoffs in the plugin's own repository — the most motivated adopter there is — is the
evidence that should be weighed first.

Open design questions:

1. **Keep or retire.** If retired, `improvement-harvesting.md` and the `reusable-kernel` transport
   label go, and `promote-dev-flow` narrows to whatever real intake path replaces it. If kept, the
   remaining questions apply.
2. **Enforcement point.** Request-triggered references have none today. Either bring harvesting
   inside the declaration system despite not being stage-triggered, or give request-triggered
   references their own fail-closed mechanism, or accept prose and add a contract-test assertion
   that pins the chain. Accepting prose without an assertion reproduces this exact failure.
3. **Precondition.** Harvesting reads `_debriefs/`, which is a Spacedock concept. RoboRev already
   has a shape for this: declare the precondition, and record out-of-scope once for a repository
   that does not meet it. Whether harvesting should follow that shape is open.
4. **Contract ownership.** The handoff shape currently lives in the reference; `promote-dev-flow`
   credits the skill. Whichever file owns it, the other two must point at it, and the pointer needs
   a check.

Non-goals: changing `improvement-intake.py`'s validation, changing the handoff schema, and altering
`promote-dev-flow`'s placement classification or Captain gate. All of those work.

## Acceptance evidence

If kept: one handoff produced end-to-end from a real `_debriefs/` record in a repository that
vendored the files through `adopt-dev-flow`, ingested by `improvement-intake.py`, plus a check that
fails when any link in the chain is broken — proven by mutation, not by inspection.

If retired: the removed surface named, the surviving intake path for `promote-dev-flow` named, and
no dangling reference to `reusable-kernel` or the handoff schema left behind.

## Measurement

Handoffs produced per adopter per month, against the current baseline of zero. A repair that leaves
that number at zero has restored a pointer, not a capability.
