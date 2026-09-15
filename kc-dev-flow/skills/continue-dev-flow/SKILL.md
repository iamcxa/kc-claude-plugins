---
name: continue-dev-flow
description: Resume an adopted repository's approved work through its selected POC, Pilot, or Production route while loading only the shared core and selected profile-stage contract.
---

# Continue Dev Flow

Continue by the selected profile's smallest sufficient route.

## Resolve authority before policy

1. Locate the workflow README via the nearest repository instructions. Require
   the unique ordered `kc-dev-flow-static-local-profile` start/end marker pair, with
   `## Local Profile` immediately after start. Read only its frontmatter and
   marked block; never infer boundaries from headings or open the full README.
2. Resolve repository root; recheck worktree, branch, shared-state owner and delivery state.
   For reviewable delivery, list open artifacts before branch creation/reuse.
   Stack on an unmerged dependency's source branch without waiting for merge.
   `delivery-branch-base.md` owns this default and exceptions across ceremonies.
3. Read the exact committed work item and selected brief. A Pilot or
   Production new admission requires one Development Brief containing the
   problem, accepted outcome, complete non-goal list, route-back conditions, and
   one canonical `## Acceptance criteria` section with unique ascending `AC-N`
   bullets. A POC item uses its complete v3 decision, falsifier, budget, and
   stop condition as the Exploration Brief. Do not read current execution state
   or revalidate and rewrite an already-admitted item's historical headings.
   A Pilot or Production item's new admission is the dispatch whose target
   `workflow_stage` is that profile's first route stage (`ideation`) with no
   prior stage pin recorded for this item; that dispatch's loader invocation
   (below) adds `--validate-admission` and stops on a non-zero exit, quoting
   the exact `profile contract: ...` stderr line to the Captain rather than
   dispatching. A subsequent stage's dispatch for the same already-admitted
   item omits the flag.
4. Before dispatch and whenever execution proposes a scope change, compare the
   accepted goal and complete non-goal list exactly with the admission snapshot.
   If either differs or must change, stop; do not replace the snapshot or
   candidate. Return a structured planning delta naming the changed premise,
   affected acceptance evidence, and recommended `change` or `stop`.
5. Then read current execution state from its declared authority. Do not
   enumerate the state tree or use provider status to advance execution.
6. Re-read `## Work profile receipt`. New choices use v3; compatible v2 Pilot
   and Production receipts remain loadable, while an active v2 POC must finish
   on its pinned 3.x pair or be Captain re-recorded. If the receipt is missing
   or stale before the first working stage, invoke
   `kc-dev-flow:choose-work-profile`; let the locally authorized actor commit
   and re-read the Captain's choice. An unchanged v1 Pilot or Production choice
   upgrades mechanically. For a v1 POC, preserve the choice but use
   `kc-dev-flow:choose-work-profile` to complete the v3 POC fields with the
   Captain before dispatch.

## Load one route

Resolve `../../scripts/profile-contract-loader.py` from this activated skill.
The manifest binds version, Local Profile interface and canonical bytes. Use the
exact item/marked README; never search hosts or store its path. It emits shared core, selected base, and selected stage only. Selection is per item; simultaneous items may load different routes.
For canonical admitted work with Acceptance criteria, the latest Stage Report
cites stable `AC-N` identifiers; Spacedock `--ac-scan` must report no unknown or
uncovered criterion before the next gate. POCs use `review` below.

Use loader `declared_receipts`; do not re-parse receipt names. Resolve each
`kc-dev-flow-conditional-references/v1` entry's `path` relative to the selected
stage. Read when its trigger is true; otherwise leave unread. Evaluate accepted
scope, recheck the exact diff before implementation exit or validation, and load
newly true references before the verdict.

- `retained_document_change`: accepted output or diff adds, removes, or changes
  a retained document.
- `project_context_claim_may_change`: a Pilot/Production map is missing, retained
  implementation needs its initial explanation, accepted behavior, architecture,
  or a public contract may change a bound claim, or the diff changes that context.
  A Markdown work record alone satisfies neither trigger.
- `delivery_artifact_review`: PR, merge request or equivalent delivery, regardless
  of ceremony owner; false for delivery without one.
- `pr_delivery_selected`: no local provider owns PR ceremony. With a local
  provider the first delivery trigger is true and this one false.
- Use loader `implementation_exit_observation_declared`: true loads the build
  observation; false performs no provider work. RoboRev requires a
  Spacedock-registered state holder; without it keep the trigger false and
  contract unread.

Record named receipts in the existing item; `receipt: null` creates no receipt.
A link is not activation. A reference adds no stage, scope, or new obligation.

Before dispatch, the First Officer writes and commits the state-owned stage-pin
sidecar, re-reads it, and dispatches only that envelope:

```bash
python3 <activated-skill-package>/scripts/profile-contract-loader.py \
  --work-item <exact-committed-work-item> \
  --local-profile <workflow-readme> \
  --stage-pin <state-owned-stage-pin> \
  --stage-attempt <runtime-owned-attempt> \
  --write-stage-pin
```

At a Pilot or Production item's new admission (per step 3 above), add
`--validate-admission` to that same invocation:

```bash
python3 <activated-skill-package>/scripts/profile-contract-loader.py \
  --work-item <exact-committed-work-item> \
  --local-profile <workflow-readme> \
  --stage-pin <state-owned-stage-pin> \
  --stage-attempt <runtime-owned-attempt> \
  --write-stage-pin \
  --validate-admission
```

A non-zero exit is a refusal, not a contract to fix by hand: stop before
writing the stage pin or dispatching, and surface the exact `profile
contract: ...` stderr line to the Captain. POC and any subsequent-stage
dispatch for an already-admitted item omit `--validate-admission`; the loader
itself is the enforcement point (`validate_admission_brief` returns
immediately for a profile other than `pilot-product-slice`/`production`), so
including the flag on a POC or later-stage dispatch is inert, not incorrect.

`ACTIVE_STAGE_PIN_MISMATCH` requires restoring the changed pinned input.
An unchanged `local_profile_interface` permits a next-boundary upgrade.
`LOCAL_PROFILE_REFIT_REQUIRED` emits no envelope/pin: obtain Captain acceptance
of its named README/mod refit, then add `--accept-local-profile-refit`.
`--format json` selects machine output.

For report resume or authorized feedback, read only
`../../MIGRATION.md#stage-pin-continuation`. Never replace a pin to clear a refusal.

At Production `ideation`, `skip_to_workflow_stage: implementation` loads no
contract and authorizes only that existing state transition: re-read the same
hash-bound item, create no ideation worker, briefing, report, or gate, then load
`build` normally. Before the skip, implementation exit, and validation, recheck
the recovery falsifier, exact diff against `scope_boundary`, rollback, and risk
list. False or uncertain evidence returns `RECOVERY_FULL_ROUTE_REQUIRED`; only
the Captain or an explicit `recovery_rollback` may re-record the full route.

A loader refusal means an off-route stage, stale receipt, or incomplete adoption.
Resolve that condition; do not substitute another item's profile or general
workflow prose.

Each working continuation/worker, after authority/profile/pin
checks, read repository-root `docs/architecture.md` before exploration or implementation.
Read task-relevant code/docs; code overrides stale claims. If absent, POC continues;
otherwise FO assigns implementation useful context/code bootstrap before feature
work; validation returns missing/stale maps to that owner. Follow `project-context-maintenance.md`; include these instructions in every dispatch,
including Production recovery that skips shape. No empty or link-only map.

For a superset state graph, route as follows:

| Profile | Workflow states used |
|---|---|
| POC | `backlog -> implementation -> validation -> done` |
| Pilot | `backlog -> ideation -> implementation -> validation -> done` |
| Production | `backlog -> ideation -> implementation -> validation -> done`; eligible recovery skips the ideation dispatch |

`backlog` selects and queues; `done` terminalizes. They dispatch no working
contract. Skipped stages create no review or evidence obligation.

## Advance

Resolve `../../scripts/poc-close-guard.py` from this skill. Record
`poc_outcome` and `poc_close_measurement`; future wait/cleanup durations
and cleanup status stay `pending`, never fabricated zero.

```bash
python3 <guard> --workflow-dir <workflow-dir> --work-item <task-path> review
```

`review` selects Spacedock's latest implementation report for direct proof,
validation for fresh proof. Declared criteria and checklist items need evidence;
absent criteria are allowed. Direct build records the outcome; `prepare` commits
implementation to validation before binding. Stop on durability failure; do not dispatch a validation worker. Fresh proof records its outcome in validation.

Prepare through the guard, record human approval without `--consume`, then
consume through the guard. Native merge guard terminalizes and archives; consume
alone leaves approval pending. Preserve frozen Briefing bytes and frontmatter.
The First Officer performs separately authorized cleanup, records actual wait
and cleanup in the archived body, commits that path through the existing state
owner, then runs native `state commit` to publish. Resume from the archive without reusing approval. Run guard
`check-final` on that path: it requires `done`, numeric durations and cleanup
`complete`/`not-applicable`; pending/failed cleanup remains incomplete.
Then return the POC outcome to planning. KC Dev Flow does not create downstream delivery work
or preselect its profile; planning decides whether a new Development Brief exists.

- Complete the selected mission/output; advance to `next_workflow_stage` at its
  stop condition.
- Use `kc-dev-flow:chief-engineer` for unclear sequencing, blockers or route drift;
  `kc-dev-flow:science-officer` for contested, high-risk, hard-to-reverse or
  low-confidence claims, or Captain request. Load `science-officer-em` only for
  consumers requesting its legacy envelope.
- Assign findings one owner and one final recheck, without open-ended review.
- FO applies deterministic gates at declared boundaries; advice is not a gate.
- Ask the Captain for scope/profile changes, irreversibility, spend/permissions,
  accepted red residuals, or merge/release authority.

After the selected route and delivery authority are satisfied, terminalize
through the existing state owner. Report decision, material evidence and next action.

## Optional observations

At implementation exit, when the `implementation_exit_observation_declared`
loader output is true, load the selected `review_convergence` observation and installed
`../../references/roborev-implementation-exit.md` conditional reference.
Direct POCs and recovery `[none]` emit false; full routes and named recovery risks
emit true. A false/absent declaration performs no RoboRev probe or invocation. Use Codex
`gpt-5.6-terra`, reasoning `medium`, `panel: none`, and explicit profile severity
and caps; host/implementation family is provenance. Unavailable reviewer yields
non-gating `UNAVAILABLE`.

README policy, local mods, provider adapters and Spacedock state stay
repository-owned. Load improvement harvesting only on explicit request;
it cannot interrupt the selected route.
