---
title: Cut the local workflow README to 700 lines without losing authority
source: Captain runtime-reading budget, 2026-08-10
product: repo-platform
sprint: S1
id: hp4y9nwh8e75vk75j9ncwmb7
status: validation
lane: main
started: 2026-08-10T22:03:08Z
design: required
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/kc-dev-flow-release-batch
---

## Problem

`docs/dev/README.md` is 1,362 lines, so every continuation and fresh gate pays to load local recovery mechanics, migration history, repeated portable policy, and stage examples before acting. Reduce the runtime authority to at most 700 lines without deleting a live safety or authority boundary and without merely moving the same mandatory reading cost to another always-loaded file.

## End value

Ordinary continuation reads a bounded authority map and current-stage policy;
recovery, validation recipes, and history load only when their trigger fires.

## Smallest route and reverse-recovery audit

The README already owns every local authority, stage boundary, and gate seat, so
it is `WORKING` but overgrown. Recovery procedure, validation recipes, and cost
history are independently triggered content. Split only those three categories,
delete repeated rationale/examples, and add no index, loader, registry, or new
policy layer.

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

Verified by: `docs/dev/README.md:105-108,229-231,325-329` and the three bounded
files under `docs/dev/runbooks/` and `docs/dev/history/`. Falsified by: ordinary
backlog/implementation continuation requiring recovery, validation recipes, or
history.

**AC-4 — The split reduces total mandatory reading rather than relocating it.**

Verified by: 374 README lines and a 605-line four-file total, compared with the
1,362-line baseline. Falsified by: any stage's required path exceeding its old
1,362-line path or a moved file becoming universally required.

## Test plan

Mutate the 700-line ceiling, Local Profile, Gate Authority, stage `Policy mods`,
and trigger links; then run the full contract, frontmatter, parity, marketplace,
link, and exact-diff checks and one fresh EM review.

## Appetite and pre-mortem

One worker; keep the README below 700 and the full four-file surface below the
old README. Stop if the split needs a loader or duplicates an authority. If this
ships and continuation is still slow, the remaining cost is the kernel or the
current stage mod, not hidden moved prose.

## Out of scope

Changing lifecycle authority, deleting safety predicates, a generated docs
system, product code, and creating or merging a PR.

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
