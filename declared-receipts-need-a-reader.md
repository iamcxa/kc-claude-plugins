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
gates:
    version: 1
    records:
        - id: gate:k69wjs5ttme3z11hph3sy45d:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:k69wjs5ttme3z11hph3sy45d-backlog-1
              briefing:
                id: briefing:k69wjs5ttme3z11hph3sy45d:backlog:attempt-1:revision-1
                digest: sha256:3a819626edd78e0af363c7505c85917b0a412b12425b73720ccfa7903d155150
                request-digest: sha256:442ee4660c5f499688d44ea995dcbaeb5e470769933ce0787495eebc7d514fac
                room-ref: ./declared-receipts-need-a-reader/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:k69wjs5ttme3z11hph3sy45d:backlog:1
                briefing: briefing:k69wjs5ttme3z11hph3sy45d:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-21T07:23:24.930534Z"
                decision: approve
                reason: 'Captain approved scheduling with the Pilot work profile. The task ships the first reader for declared_receipts so the emitted field does not repeat the defect #256 reported one layer up. Pilot rather than Production because this changes what a skill tells an agent, not an output contract adopters read at a pinned tag, so it carries no release or rollback obligation. Delivery base stays stacked on PR #262''s branch per delivery-branch-base.md: #262 is an open artifact sharing this candidate''s lineage through declared_receipts.'
              application:
                target-stage: ideation
                state: pending
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
