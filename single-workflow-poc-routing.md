---
title: "kc-dev-flow: make POC a bounded decision route in one workflow"
status: backlog
source: "Captain-approved design 6a68cab0 after Claude PASS, 2026-08-25"
product: kc-dev-flow
sprint: S4
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: ahd8hehpz3g9r7vqmrz82z4x
---

## Problem

KC Dev Flow currently describes POC as an experiment that passes when one real
journey and critical assumption are observed, but actual use also asks POC to
decide whether the next commitment should proceed, stop, or change. Without an
explicit decision, falsifier, budget, stop condition, and terminal handoff
boundary, exploratory work can grow into delivery without a new risk decision.

Implement the Captain-approved single-workflow design at commit `6a68cab0`.
Keep the existing Spacedock graph and POC/Pilot/Production route slugs. Add the
smallest deterministic entry and close guards that make the declared kc-dev-flow
path fail closed while preserving Captain task-creation, scheduling, profile,
merge, and release authority.

## Work profile receipt

## Accepted outcome and non-goals

Accepted outcome: one adopted workflow routes bounded exploration and technical
proof through POC; a supported POC conclusion closes as `proceed`, `stop`, or
`change`; any downstream delivery is separately created, scheduled, and
profiled.

Non-goals: no Explore workflow or stage, no Spacedock engine change, no
cross-entity transaction, no model call or new CI job in the contract slice, no
automatic downstream profile selection, and no reuse of the 14,568-line
behavioral-gate branch.

## Acceptance evidence

- Exact loader fixtures reject each missing or deterministic placeholder POC
  entry field while leaving Pilot and Production free of POC placeholders.
- A pinned Spacedock local test exercises `stop`, `change`, `created`,
  `deferred`, and `declined` close paths, including succeeded-create / failed-
  handoff-write retry without a duplicate item.
- Package and adopted contract copies remain byte-identical where required.
- Migration proves the declared v2/v3 cutover behavior and names the consumer
  action before release.
- Existing multi-profile routing remains green on the exact supported runtime.

## Measurement

No model call or new CI job belongs to this contract slice. Measure any added
runtime in existing CI jobs before release; do not claim an unmeasured cost.
