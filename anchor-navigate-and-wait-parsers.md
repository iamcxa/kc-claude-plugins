---
id: f5kvze8ty8hraeyrzhj960e2
title: "e2e-pipeline: anchor `navigate` and `wait`, the two ACTION_PARSERS entries measured as genuinely at risk"
status: backlog
source: "Pre-mortem mitigation of issue189 (anchor the click grammar) — the anchoring audit that task's implementation stage was required to record; filed by the FO at the issue189 validation gate because the audit named the seed but no entity was ever created"
product: e2e-pipeline
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
pr_artifact_v1:
mod-block:
design:
lane:
---

## Problem

issue189 anchored `ACTION_PARSERS.click` so a click action string the grammar
cannot fully consume is a compile-time error. Its pre-mortem named the failure
mode that survives that fix: *"click is anchored, the tests are green, and the
identical prefix-match defect survives in the sibling parsers. The fix would be
locally correct and the class would live on."* The mitigation it required was an
anchoring audit of every `ACTION_PARSERS` entry plus a backlog seed for anything
measured as genuinely at risk. The audit ran and is recorded at
`docs/dev/.spacedock-state/issue189.md:251-262`; this entity is the seed it
called for, filed late.

Two entries were measured — by running the parser, not by reading the regex — as
**genuinely at risk**:

| Parser | Measured behaviour |
|---|---|
| `wait` | `"Wait 5 minutes"` → `seconds=5`. A **60x silent misread**. `"Please Wait 5 zzz"` → `seconds=5` |
| `navigate` | `"Please Navigate to /list"` → `target="/list"` (leading text silently dropped); `"Navigate to /list and then some junk"` → `target="/list and then some junk"`, which `resolveNavigate` accepts as a literal path |

`wait` is the sharper of the two: a flow author writing `Wait 5 minutes` gets a
five-second wait and no diagnostic. It is latent rather than live — issue189's
sweep found no corpus flow using that phrasing — which is why it was seeded
rather than hotfixed.

Four other entries (`snapshot`, `verify-external`, `execute-external`,
`capture-url-query`) were measured as *intentionally* unanchored: they are
detectors whose operands come from elsewhere, so there is nothing to discard.
They are not in scope here. `fill` was already anchored; `click` was anchored by
issue189.

## Proposed approach

Not decided — this is a seed, and it needs its own ideation. The open questions
a shaping round has to answer:

- Whether `navigate` and `wait` are one task or two. They share a defect class
  but not a blast radius: `navigate`'s `target` is consumed as a literal path,
  `wait`'s `seconds` is a number with a unit the grammar never reads.
- Whether `wait` should anchor, or should learn units (`minutes`/`seconds`), or
  should refuse a unit it does not understand. Anchoring alone turns
  `Wait 5 minutes` from a wrong answer into an error, which is the issue189
  precedent; teaching it units is a larger, separate behaviour change.
- The blast radius, measured the way issue189 measured it: sweep every
  `navigate` and `wait` action string in the repo through both the old and the
  new pattern before changing behaviour.

## Design determination

Not set — this is a `backlog` seed and has not been through ideation.

## Acceptance criteria

Not written — acceptance criteria are authored at ideation, against a decided
approach.

## Test plan

Not written — see above.

## Measurement

## Doc diff

To be decided at ideation. issue189's precedent is one row in
`e2e-pipeline/skills/e2e-compile/SKILL.md`.

## Out of scope

- Re-opening issue189's click anchoring, or the seven residuals accepted at its
  validation gate.
- The four `ACTION_PARSERS` entries measured as intentionally unanchored.
