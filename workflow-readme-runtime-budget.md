---
title: Cut the local workflow README to 700 lines without losing authority
source: Captain runtime-reading budget, 2026-08-10
product: repo-platform
sprint: S1
id: hp4y9nwh8e75vk75j9ncwmb7
status: implementation
lane: main
started: 2026-08-10T22:03:08Z
design: required
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/kc-dev-flow-release-batch
pr: "#199"
---

## Problem

`docs/dev/README.md` is 1,362 lines, so every continuation and fresh gate pays to load local recovery mechanics, migration history, repeated portable policy, and stage examples before acting. Reduce the runtime authority to at most 700 lines without deleting a live safety or authority boundary and without merely moving the same mandatory reading cost to another always-loaded file.

## End value

Ordinary continuation reads a bounded authority map and current-stage policy;
recovery and validation recipes load only when their trigger fires. Cost
observations remain in the task records that produced them.

## Smallest route and reverse-recovery audit

The README already owns every local authority, stage boundary, and gate seat, so
it is `WORKING` but overgrown. Recovery procedure, validation recipes, and cost
history are separable content. Split only the two operational procedures, delete
the duplicated history and repeated rationale/examples, and add no index, loader,
registry, or new policy layer.

## Design determination

`required` — this changes the repository's runtime policy-loading boundary while
preserving the same authorities and lifecycle.

## Acceptance criteria

**AC-1 — The always-loaded README is at most 700 lines.**

Verified by: `wc -l docs/dev/README.md` and the ceiling at
`scripts/kc-dev-flow-contract-test.py:402-403`. Falsified by: line 701 or more.

**AC-2 — Authority and stage selection remain in the README.**

Verified by: `docs/dev/README.md:50-82`, `docs/dev/README.md:151-270`, and
`scripts/kc-dev-flow-contract-test.py:428-448,620-632`. Falsified by: removing a
Local Profile binding, lifecycle entry/exit, stage `Policy mods`, or Gate
Authority boundary without a replacement in the always-loaded file.

**AC-3 — Detail loads only at its real trigger.**

Verified by: the README's two trigger links and the bounded files under
`docs/dev/runbooks/`. Falsified by: ordinary backlog/implementation continuation
requiring recovery or validation procedure, or a separate observation log.

**AC-4 — The split reduces total mandatory reading rather than relocating it.**

Verified by: the README plus its two runbooks remaining below the 1,362-line
baseline. Falsified by: any stage's required path reaching that baseline or a
moved file becoming universally required.

## Test plan

Mutate the 700-line ceiling, Local Profile, Gate Authority, stage `Policy mods`,
and trigger links; then run the full contract, frontmatter, parity, marketplace,
link, and exact-diff checks and one fresh EM review.

## Appetite and pre-mortem

One worker; keep the README below 700 and the full three-file surface below the
old README. Stop if the split needs a loader or duplicates an authority. If this
ships and continuation is still slow, the remaining cost is the kernel or the
current stage mod, not hidden moved prose.

## Out of scope

Changing lifecycle authority, deleting safety predicates, a generated docs
system, product code, and creating or merging a PR.

## Captain scope revision — 2026-08-11

The captain approved deleting `docs/dev/history/workflow-cost-record.md` after
the exact-head audit found no runtime, gate, delivery, or self-improvement
consumer. `Observation` becomes `none`; task records remain the durable home for
their own measurements. This narrows AC-3 and AC-4 from three extracted detail
files to the two operational runbooks and supersedes only the history-retention
parts of the earlier stage reports.

## Stage Report: ideation

- DONE: The captain set a hard 700-line README ceiling and required every live
  authority and stage mod to remain correctly applied.
- DONE: Reverse recovery retained the existing README authority and identified
  exactly three trigger-owned categories; repeated examples/rationale are
  deletion candidates, not relocation candidates.
- DONE: AC-1 caps the always-loaded README at 700 lines with a fail-closed
  contract assertion.
- DONE: AC-2 keeps Local Profile, lifecycle, stage policy selection, and seat
  authority in the always-loaded README.
- DONE: AC-3 binds recovery, validation recipes, and observation history to
  explicit triggers instead of ordinary continuation.
- DONE: AC-4 requires every stage path and the combined four-file surface to
  remain smaller than the old 1,362-line README.
- DONE: Fresh high-reasoning EM returned `narrow / high`: delete repetition,
  retain authority in the README, and load recovery/validation/history only on
  their triggers. Multi-model review was not recommended.

### Summary

Proceed with one 700-line authority file plus three trigger-loaded documents;
add no loading framework or parallel policy source.

## Stage Report: implementation

- DONE: Commit `c48a9e97f1614d80d8220ac4c80b4df993db09fb` reduces
  `docs/dev/README.md` from 1,362 to 374 lines.
- DONE: Recovery procedure is 116 lines, validation procedure is 93, and
  observation history is 22; the four-file surface totals 605 lines and none of
  the moved files is universally loaded.
- DONE: Local Profile, state ownership, lifecycle entry/exit, every stage's
  `Policy mods`, validation predicate, and Captain/EM/FO boundaries remain in
  the README. Repeated rationale and examples were deleted, not relocated.
- DONE: Contract tests enforce the ceiling, required authority sections,
  trigger links, EM selection/fallback, and every stage's policy declaration.
- DONE: Fresh stage-exit checks pass: kc-dev-flow contract, 40 skill
  frontmatters, version parity at 2.1.0, marketplace L0/L1/L2,
  state-prerequisite contract, Python compilation, and `git diff --check`.

### Summary

The implementation keeps one bounded authority entrypoint and three documents
that load only for recovery, validation, or historical observation.

## Stage Report: validation

### TL;DR

Fresh Claude Opus high session `d4daa8b0-ea12-4c8f-9ccc-a086ae9a8edd`
reviewed exact head `c48a9e97f1614d80d8220ac4c80b4df993db09fb` over
`a024b254e236f521d8438d567ade36d779a52d11` and returned
`proceed / high / multi_model:not_needed`, with AC-1..AC-4 PASS and zero
Material findings. The README is 374 lines and all four documents total 605.

### Per-AC verdicts

- **AC-1 PASS** — exact-head count is 374 lines; the contract ceiling leaves a
  326-line margin.
- **AC-2 PASS** — Local Profile, lifecycle, every stage's `Policy mods`, the
  validation predicate, and Captain/EM/FO authority remain always loaded and
  contract-enforced.
- **AC-3 PASS** — recovery is 116 lines and failure-triggered; validation is 93
  lines and stage-triggered; 22 lines of history are non-authoritative and absent
  from ordinary continuation.
- **AC-4 PASS** — 605 total lines remain below the 1,362-line baseline, and no
  moved file is universally required; repeated rationale/examples were deleted.

### Evidence block

`Lenses:` Docs/policy, authority, state recovery, validation procedure,
back-compat, and delivery fired; all PASS with zero Material findings. The
script change is comment-only. Would fail on a missing authority binding, stage
mod, trigger link, recovery runtime, or universally loaded moved file.

`Diff coverage:` N/A — the task's production change is Markdown plus a comment
path update; there is no changed executable behavior line. The contract suite
and state-prerequisite test both ran and passed as validation instruments.

`Adversarial:` PASS — the old 1,362-line README reddened the new ceiling, and
the contract rejects missing Local Profile/Gate Authority clauses, stage policy
selections, EM fallback, and trigger paths. Thirteen changed-document local links
resolve; would fail if one target were removed or a required clause disappeared.

`Cross-model:` not_needed — the exact-head EM found no contested, irreversible,
low-confidence, or unresolved call. No optional second model was requested.

`E2E:` N/A — ideation declared a local docs/workflow-loading change; it has no
user-visible or full-stack product runtime. Contract, path, and recovery
prerequisite exercises are the applicable evidence.

`Origin re-observation:` N/A — no accepted claim originated in a consumer or
external runtime; the baseline and result are repository document counts and
locally bound workflow authority.

### Engineering judgment

- `question:` Does the 374-line README preserve all always-loaded authority and
  reduce every mandatory reading path without relocating universal cost?
- `revision:` `c48a9e97f1614d80d8220ac4c80b4df993db09fb` over
  `a024b254e236f521d8438d567ade36d779a52d11`.
- `adjudications:` AC-1..AC-4 supported; the prior ambiguous recovery-version
  finding is closed by explicit `spacedock 0.26.0 (contract 3)` wording. No
  task-level non-pass, Material finding, or removable complete document remains.
- `risk_tradeoff:` pay three small trigger-owned files to cut ordinary reading by
  988 lines while preserving authority; avoid a loader, index, or duplicate
  policy source.
- `recommendation/route/confidence:` proceed / proceed / high.
- `dissent:` empty. `multi_model:` not_needed.
- `disproof_condition:` change route if README exceeds 700, any moved file becomes
  universal, a stage path reaches the old 1,362-line baseline, a trigger/authority
  is lost, or the installed Spacedock version differs from the named contract.
- `authority_boundary:` advisory only; Captain retains workflow scope, Spacedock
  retains state, and GitHub/release-please retain delivery and release.

### Exact-head PR rebind

Fresh PR-level Claude Opus high session
`53ca4a4a-e114-4a4b-9412-ae0fbb0c0e0a` rebound AC-1, AC-2, AC-3, and AC-4 to
`454507f7ba56ce79ca0414f1964af4e59126eea5`. The always-loaded README is now
389 lines and the four-file surface is 620, still below both the 700-line ceiling
and 1,362-line baseline. Recovery remains failure-triggered at README line 94,
validation procedure stage-triggered at line 240, and history non-authoritative
at line 54. No moved file changed or became universally required; the 15 added
README lines allocate the new pilot to existing stages. Hosted CI is green at
the exact head. Verdict remains `proceed / high`, with zero Material findings.

The prior 374/605 values remain the measurement at `c48a9e9`; 389/620 is the
current delivery snapshot. The growth direction is a pilot observation, not an
AC failure: the README retains 311 lines of ceiling headroom.
