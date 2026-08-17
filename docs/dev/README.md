---
commissioned-by: spacedock@0.25.0
entity-type: task
entity-label: task
entity-label-plural: tasks
id-style: sd-b32
state: .spacedock-state
trunk: main
stages:
  defaults:
    worktree: false
    concurrency: 2
  states:
    - name: backlog
      initial: true
      gate: true
    - name: ideation
      gate: true
    - name: implementation
      worktree: true
    - name: validation
      worktree: true
      fresh: true
      feedback-to: implementation
      gate: true
    - name: release
      gate: true
    - name: done
      terminal: true
---

# kc-claude-plugins Development Workflow

This workflow exposes one superset state graph. A committed work profile selects
the working route and the contracts an agent loads:

| Profile | Active route |
|---|---|
| POC | `backlog -> implementation -> validation -> done` |
| Pilot | `backlog -> ideation -> implementation -> validation -> done` |
| Production | `backlog -> ideation -> implementation -> validation -> release -> done` |

Backlog and done are state boundaries, not worker stages. Skipped stages do not
receive placeholder reviews or receipts.

## Local Profile

Read only this section before resolving the selected item. Do not read this full
README as a policy bundle.

| Role | Bound local authority |
|---|---|
| Project context | Root `PRODUCT.md`, `ARCHITECTURE.md`, and `CLAUDE.md` |
| Work items | Spacedock entities under `docs/dev/` |
| Iteration | Captain-owned product sprint headings in `docs/dev/ROADMAP.md` |
| Execution state | `docs/dev/.spacedock-state` on `spacedock-state/dev`, owned by Spacedock |
| Profile receipt | `## Work profile receipt` in the exact work item |
| Profile loader | `docs/dev/_mods/profile-contract-loader.py` |
| Contracts root | `docs/dev/_mods` |
| Delivery | GitHub PR to `main`; required checks; release-please owns versions and tags |
| Scope, profile, irreversibility, merge/release | Captain |
| Orchestration | First Officer |
| Normal delivery advice | `kc-dev-flow:chief-engineer`, only on its bounded triggers |
| Independent assurance | `kc-dev-flow:science-officer`, only on its bounded triggers |
| Optional observation | RoboRev at Production implementation exit only; local runbook below |

The loader, shared core, and profile contracts are vendored from `kc-dev-flow`.
`scripts/kc-dev-flow-contract-test.py` checks their package/adopter identity and
every supported profile-stage combination.

The Production-only observation is `review_convergence` in `observe` mode with
provider RoboRev. Repository config `.roborev.toml` binds agent, model, reasoning,
and severity; `panel: none` and one exact-tip request bound the run.
The run allows one changed-tip repair confirmation.
POC and Pilot do not load this runbook.

## State prerequisite

Before mutating or using state for an outward action, run:

```bash
scripts/dev-flow-state-prereq.sh
```

Exit 0 establishes the clean state holder at the fetched state tip. Other exits
do not authorize attaching to or mutating another holder. Load
[`runbooks/state-recovery.md`](./runbooks/state-recovery.md) only after exit 75,
76, or 77, or an interrupted state transaction.

Keep a setter and its durability action together:

```bash
spacedock status --workflow-dir docs/dev \
  --set "$SLUG" "${EXACT_FIELD_ASSIGNMENTS[@]}" &&
spacedock state commit --workflow-dir docs/dev "$SLUG"
```

Validate controlled work-item fields at capture and transition:

```bash
python3 scripts/dev-flow-work-context-check.py validate \
  --task "$TASK_FILE" \
  --marketplace .claude-plugin/marketplace.json \
  --roadmap docs/dev/ROADMAP.md
```

## Profile selection

Before the first working stage, re-read the exact work item's
`kc-dev-flow-work-profile/v2` receipt. If missing or stale, invoke
`kc-dev-flow:choose-work-profile`; the Captain chooses and the authorized actor
commits and re-reads it. An unchanged v1 receipt upgrades mechanically with the
same Captain selection; it is migration evidence until the v2 result is committed.

Use the host's structured Ask UI when available; plain chat is the fallback.
Selection precedes acceptance-criteria expansion and stage dispatch.

Load the selected working contract with:

```bash
python3 docs/dev/_mods/profile-contract-loader.py \
  --contracts-root docs/dev/_mods \
  --work-item "$EXACT_COMMITTED_WORK_ITEM"
```

The command validates and hash-binds that item's v2 receipt and current status,
then emits the shared core, one selected base, and one selected stage. Its
`next_workflow_stage` is the normal next state. Profiles are per item, so POC,
Pilot, and Production items may run concurrently in this repository without a
global profile switch. A refusal blocks only that item's dispatch until its
receipt, state, or vendored adoption is corrected.

## Stages

Each working stage uses the loader command above. The text below only binds
repository mechanics; it does not repeat the profile contract.

### `backlog` — queue and select

Capture `title`, `source`, `product`, and one problem paragraph. Only the Captain
or iteration owner schedules it. Obtain and commit the v2 profile receipt before
moving to the selected route's first working state.

### `ideation` — selected `shape`

Active only for Pilot and Production. Load the selected `shape` contract. Record
the accepted outcome and task-specific acceptance evidence in the work item.
POC moves directly from backlog to implementation.

### `implementation` — selected `build`

Load the selected `build` contract. Use an isolated worktree when the checkout is
contended. Run scoped checks while iterating and only the relevant exit checks
earned by the selected profile and diff.

For Production only, after tests and an exact candidate revision exist, the
declared optional RoboRev observation may load
[`runbooks/roborev-implementation-exit.md`](./runbooks/roborev-implementation-exit.md).
Its receipt is observation, not validation or delivery authority. POC and Pilot
do not load this runbook.

### `validation` — selected `prove`, `verify-deliver`, or `verify`

Load the stage selected by the profile loader. Read
[`runbooks/validation-evidence.md`](./runbooks/validation-evidence.md) only for
Production verification or when the accepted Pilot evidence explicitly names
it. POC does not load it.

When a GitHub PR exists, observe all current provider feedback at the exact head
and record a bounded disposition. A code repair returns to implementation and
gets one final re-verification. A new delivery completes its selected local
verification before Captain-authorized Draft creation.

POC and Pilot proceed to done after their selected delivery authority is met.
Production proceeds to release.

### `release` — Production only

The profile loader rejects this stage for POC and Pilot. Production loads the
selected release contract. Required checks, rollback or forward-recovery
readiness, operational ownership, and explicit Captain or release-owner
authorization must apply to the exact delivery revision.

### `done` — terminalize

Terminalize only after the selected route and declared delivery authority are
satisfied. Set `completed` from the provider's merged time, clear `mod-block`,
record the verdict, commit the entity, and run the path-scoped archive action.
Load state recovery only if that transaction fails.

When a PR is the selected delivery artifact, authenticated product PR
`mergedAt` supplies the completion time; local merge state does not substitute.

## Gate ownership

| Boundary | Owner |
|---|---|
| Stage routing and evidence presence | FO, applying the loader and declared checks |
| Decidable technical condition | Named deterministic check |
| Scope, profile, irreversible action, red residual | Captain |
| Production release | Captain or declared release owner |
| Delivery sequencing advice | Chief Engineer, advisory |
| Contested or high-risk technical assurance | Science Officer, advisory |

No agent is a general gatekeeper. A Science Officer `hold` recommends that the
named owner keep a boundary closed; it does not mutate state.

## Proof and delivery checks

- `python3 kc-dev-flow/scripts/profile-contract-loader.test.py`
- `python3 scripts/kc-dev-flow-contract-test.py`
- `scripts/version-parity-check.sh`
- `scripts/marketplace-verify.sh`
- `scripts/skill-frontmatter-lint.sh`
- exact-head GitHub required checks when a PR exists

Use the loader test for must-load/must-not-load claims. Model pressure is a
bounded behavioral comparison, not a substitute for loader evidence.

## Task template

```yaml
---
id:
title:
status: backlog
source:
product:
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

## Work profile receipt

## Accepted outcome and non-goals

## Acceptance evidence

## Measurement
```

Keep stage reports to decision, evidence that changes the decision, and next
action. Link raw artifacts instead of replaying the session narrative.
