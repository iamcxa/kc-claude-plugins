---
id: k69wjs5ttme3z11hph3sy45d
title: continue-dev-flow states the stage's declared receipts to the working agent
status: backlog
source: residual named at every gate of declared-receipt-has-no-reader (#256) and ruled on by the Captain, 2026-08-20 — ship the reader before the emitted field repeats the defect it was added to answer
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

`declared-receipt-has-no-reader` (#256, PR #262) makes the profile loader emit
`declared_receipts` — the receipt names the selected stage contract declares.
Nothing reads it. That is the same shape as the defect #256 reported, moved one
layer up: a field that names an obligation, emitted in machine-readable output,
consumed by nobody.

`continue-dev-flow` is the natural reader. It already invokes the loader and
already tells the working agent to "Record a named receipt in the existing work
item" (`skills/continue-dev-flow/SKILL.md:62`), but the agent learns *which*
receipt only by parsing the contract's `kc-dev-flow-conditional-references/v1`
JSON block itself (`SKILL.md:40-41`). The loader has already parsed, validated
and hash-bound that block; handing the list up front replaces a re-parse with a
read.

What this buys is visibility at the moment of action, not a guarantee. `trigger`
stays prose the agent evaluates, so the strongest true statement the skill can
make is "this stage declares these receipts, each behind a trigger you must
evaluate" — never "this stage owes X".

## Verification boundary (decided before the work starts)

Two layers, and only one is verifiable here:

- **Verifiable:** `declared_receipts` reaches the skill's documented invocation
  and the skill's instruction reads it. A check can fail on this.
- **Not verifiable in this repository today:** whether agents that read the
  instruction record receipts more often. That is a behavioural A/B comparison,
  and the entity that would build the instrument — `skill-ablation-harness`
  (`5b5gp68f2aq0bdrcf3q28jgg`, "Cutting prose from a skill has no failure signal
  — build one before cutting") — records its review driver as MISSING and its
  materiality verdict as EXISTS_BROKEN. It is a larger entity than this one.

Do not attempt the behavioural measurement here, and do not claim the
instruction is effective. Claim only what the first layer proves.

## Closing #256

When this lands, `#256` closes with a bounded note: the ambiguity is gone (the
loader emits the declared names, `continue-dev-flow` reads them, and the
docstring records the exact boundary), and the obligation is still unverified by
design — no evaluable `trigger`, no stage-exit check. Option 2 gets no
speculative issue; the first observed case of a receipt that should have been
produced and was not is what opens it.

## Work profile receipt

## Accepted outcome and non-goals

## Acceptance evidence

## Measurement
