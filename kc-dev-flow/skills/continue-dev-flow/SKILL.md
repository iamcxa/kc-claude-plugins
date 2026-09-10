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
2. Recheck the worktree, branch, shared-state owner, and remote delivery state.
   When this item is delivered through a reviewable delivery artifact, list the
   open artifacts before creating or reusing a branch. An open unmerged artifact
   that carries work this item builds on is the default base: branch from its
   source branch and stack, rather than branching from the trunk or waiting for
   it to merge. `delivery-branch-base.md` owns the rule and its exceptions, and
   applies whoever owns the delivery ceremony.
3. Read the exact committed work item and selected brief. A Pilot or
   Production new admission requires one Development Brief containing the
   problem, accepted outcome, complete non-goal list, route-back conditions, and
   one canonical `## Acceptance criteria` section with unique ascending `AC-N`
   bullets. A POC item uses its complete v3 decision, falsifier, budget, and
   stop condition as the Exploration Brief. Do not read current execution state
   or revalidate and rewrite an already-admitted item's historical headings.
4. Classify its optional Planning Receipt before provider access. The receipt is
   exactly `source`, `planning-window`, and `planning-outcome`:
   - when all Planning Receipt fields are absent, use the Captain-approved
     committed brief as planning authority and do not invoke a provider reader or
     comparator;
   - when all Planning Receipt fields are present, run provider reconcile only
     for the provider-backed branch below. For a new Pilot or Production
     admission, first invoke this activated skill's installed profile loader in explicit
     `--validate-admission` mode; default continuation never selects that mode;
     and
   - otherwise report `planning receipt incomplete` and stop before reading
     execution state or mutating it.
5. In the provider-backed branch, follow the exact work item's `source` to the
   accepted planning item. Use installed sibling `../../scripts/linear-admission.py`
   for Linear, or the bound local reader otherwise. Read the item for the problem,
   decision, success condition, priority,
   and human-facing status, and obtain the union of the provider's current Ready
   set for the recorded planning window/outcome and every currently Ready
   snapshot source even when its current window or outcome moved. Refuse a
   truncated provider result. If `source` is not a resolvable planning link,
   report `planning source unavailable` and stop before reading execution state.
   If the reader or its inputs are unavailable, report `planning reconcile
   unavailable` and stop at the same boundary. Do not promote the admission
   snapshot into planning authority or invent, migrate, or rewrite its planning
   item.
6. Still in that branch, compare the current Ready set with the committed
   execution snapshot selected through the adapter's local grouping. Compare
   source identity and membership, `planning-window`, `planning-outcome`,
   accepted goal, and non-goals; classify each difference as added, removed,
   changed, or moved. Normalize both sets into ephemeral JSON lists whose items
   contain `source`, `planning-window`, `planning-outcome`, `accepted-goal`, and
   string-list `non-goals`. Do not commit or reuse those files. Refuse the
   snapshot unless every item shares the exact window and outcome read from the
   engaged item.
7. Invoke the installed loader's sibling read-only engage comparator only in
   the provider-backed branch. The activated skill supplies both package paths
   for this invocation; do not store an installation path in the repository.

   ```bash
   python3 <planning-comparator> \
     --snapshot <ephemeral-snapshot-json> \
     --current <ephemeral-current-json> \
     --expected-source <exact-work-item-source> \
     --expected-window <exact-work-item-planning-window> \
     --expected-outcome <exact-work-item-planning-outcome>
   ```

   Exit `0` continues only when stdout parses as one JSON object with
   `status: clean` and empty `added`, `removed`, `changed`, and `moved` arrays.
   Any other exit-`0` output reports `planning reconcile unavailable` and stops
   before new dispatch or state mutation. Exit `1` reports the classified delta
   and stops at that boundary. Exit `2` reports
   `planning reconcile unavailable` and stops at the same boundary. If the
   comparison finds an added, removed, changed, or moved item, report the
   delta and stop before new dispatch or state mutation. The Captain must admit
   the delta before an authorized actor commits a replacement snapshot. No
   difference writes the provider or execution snapshot automatically. Do not
   cancel a running worker. The stop applies to new dispatch and later state
   changes.

   When `## Local Profile` binds one combined provider admission guard, use it
   for steps 4–7 instead of manual provider input or normalization. Continue
   only from one `kc-dev-flow-dispatch-envelope/v1` JSON object that binds the
   current work-item and state revisions, snapshot, live read, clean comparator,
   and loaded contracts. Empty stdout is the mechanical dispatch stop.

   The same successful provider read also returns one ephemeral `delivery`
   binding with `branch` and `close_line`; derive both from the same exact
   reconciled `source`, never from work-item prose. A Linear adapter returns its
   exact `branchName` and `Fixes TEAM-N`. A GitHub Issue adapter returns
   `branch: null` and `Closes owner/repo#N`; null preserves the current delivery
   branch. A non-empty branch is the exact forge head branch, even when the local
   worktree branch differs. Append the close line exactly once to the reviewed
   PR body. Missing, malformed, or source-mismatched bindings stop before branch
   push or PR creation. This binding writes neither provider nor execution
   state.
8. Before dispatch and whenever execution proposes a scope change, compare the
   accepted goal and complete non-goal list exactly with the admission snapshot.
   If either differs or must change, stop; do not replace the snapshot or
   candidate. Return a structured planning delta naming the changed premise,
   affected acceptance evidence, and recommended `change` or `stop`.
9. Then read current execution state from its declared authority. Do not
   enumerate the state tree or use provider status to advance execution.
10. Re-read `## Work profile receipt`. New choices use v3; compatible v2 Pilot
   and Production receipts remain loadable, while an active v2 POC must finish
   on its pinned 3.x pair or be Captain re-recorded. If the receipt is missing
   or stale before the first working stage, invoke
   `kc-dev-flow:choose-work-profile`; let the locally authorized actor commit
   and re-read the Captain's choice. An unchanged v1 Pilot or Production choice
   upgrades mechanically. For a v1 POC, preserve the choice but use
   `kc-dev-flow:choose-work-profile` to complete the v3 POC fields with the
   Captain before dispatch.

On a planning-provider change, migrate only unadmitted items. Active items keep
their provider, reader, snapshot, source, window, outcome, and execution group
through completion; new admissions use the replacement. Do not project, import,
poll, or rewrite either authority.

## Load one route

Resolve `../../scripts/profile-contract-loader.py` from this activated skill.
Its manifest binds version, Local Profile interface, and canonical
byte. Invoke it with the exact item and marked README; do not search hosts or
store its path. It emits shared core, selected base, and selected stage only.
Profile selection is per item, never a
project-global mode; simultaneous items may load different routes.
For canonical admitted work with Acceptance criteria, the latest Stage Report
cites stable `AC-N` identifiers; Spacedock `--ac-scan` must report no unknown or
uncovered criterion before the next gate. POCs use `review` below.

A selected stage may emit a `kc-dev-flow-conditional-references/v1` block;
the loader's output already parses that block into `declared_receipts` — the
receipt names this stage declares, each behind a trigger you evaluate. Read
`declared_receipts` for those names instead of re-parsing the block for
`receipt`. For each entry, still resolve `path` relative to the selected
stage contract and read it only when its named `trigger` is true; otherwise
leave it unread. Resolve the
trigger first from accepted scope, then recheck it against the exact changed
files before implementation exit or validation. `retained_document_change` is
true only when the accepted output or exact diff adds, removes, or changes a
retained document. `project_context_claim_may_change` is true only when accepted
behavior, architecture, or a public contract may change a claim in the bound
project context, or the exact diff changes that bound context. A Markdown work
record alone satisfies neither trigger. `delivery_artifact_review` is true when
this item is delivered through a reviewable delivery artifact — pull request,
merge request, or forge equivalent — no matter who owns the ceremony; it is false
only for a route that delivers without one. `pr_delivery_selected` is narrower:
true only when no local delivery provider owns the PR ceremony, so the portable
one applies. A repository whose provider mod owns the ceremony has the first
trigger true and the second false. Read
`implementation_exit_observation_declared` from the loader output; true loads
the declared build observation and false performs no provider work. RoboRev's
repository precondition is a
Spacedock-registered state holder, so a repository without one leaves the trigger
false and never loads the contract. A newly true trigger loads its reference
before the stage verdict. Record a named receipt in the existing work item;
`receipt: null` creates no receipt. A link is not activation. A reference cannot
add stages, broaden scope, or become a standing policy bundle.

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
