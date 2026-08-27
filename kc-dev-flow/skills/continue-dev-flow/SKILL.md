---
name: continue-dev-flow
description: Resume an adopted repository's approved work through its selected POC, Pilot, or Production route while loading only the shared core and selected profile-stage contract.
---

# Continue Dev Flow

Continue by the selected profile's smallest sufficient route.

## Resolve authority before policy

1. Read the workflow locator from the nearest repository instructions. Locate
   `## Local Profile` and the next same-level heading, then read that bounded
   section plus the frontmatter; do not open the full workflow README.
2. Recheck the worktree, branch, shared-state owner, and remote delivery state.
   When this item is delivered through a reviewable delivery artifact, list the
   open artifacts before creating or reusing a branch. An open unmerged artifact
   that carries work this item builds on is the default base: branch from its
   source branch and stack, rather than branching from the trunk or waiting for
   it to merge. `delivery-branch-base.md` owns the rule and its exceptions, and
   applies whoever owns the delivery ceremony.
3. Read the exact committed Spacedock work item only far enough to resolve its
   `source`, `planning-window`, `planning-outcome`, and `sprint`. Do not read
   current execution state yet, and do not treat the task body as a second
   planning authority.
4. Follow the exact work item's `source` to the accepted planning item and
   invoke the repository-local read-only planning reader. Read the item for the
   problem, decision, success condition, priority, and human-facing status, and
   obtain the union of the provider's current Ready set for the recorded
   planning window/outcome and every currently Ready snapshot source even when
   its current window or outcome moved. Refuse a truncated provider result. If
   `source` is not a resolvable planning link, report `planning
   source unavailable` and stop before reading execution state. If the reader or
   its inputs are unavailable, report `planning reconcile unavailable` and stop
   at the same boundary. Do not promote the admission snapshot into planning
   authority or invent, migrate, or rewrite its planning item.
5. Compare that current Ready set with the committed SD entity set for the same
   `sprint`. Compare source identity and membership, `planning-window`,
   `planning-outcome`, accepted goal, and non-goals; classify each difference as
   added, removed, changed, or moved. Normalize both sets into ephemeral JSON
   lists whose items contain `source`, `planning-window`,
   `planning-outcome`, `accepted-goal`, and string-list `non-goals`. Do
   not commit or reuse those files. Refuse the snapshot unless every item
   shares the exact window and outcome read from the engaged item.
6. Invoke the repository-local read-only engage comparator.

   ```bash
   python3 <planning-comparator> \
     --snapshot <ephemeral-snapshot-json> \
     --current <ephemeral-current-json> \
     --expected-source <exact-work-item-source> \
     --expected-window <exact-work-item-planning-window> \
     --expected-outcome <exact-work-item-planning-outcome>
   ```

   Exit `0` continues. Exit `1` reports the classified delta and stops
   before new dispatch or state mutation. Exit `2` reports
   `planning reconcile unavailable` and stops at the same boundary. If the
   comparison finds an added, removed, changed, or moved item, report the
   delta and stop before new dispatch or state mutation. The Captain must admit
   the delta before an authorized actor commits a replacement snapshot. No
   difference writes the provider or SD automatically. Do not cancel a running
   worker. The stop applies to new dispatch and later state changes.
7. Then read current execution state from its declared authority. Do not
   enumerate the state tree or use provider status to advance execution.
8. Re-read `## Work profile receipt`. New choices use v3; compatible v2 Pilot
   and Production receipts remain loadable, while an active v2 POC must finish
   on its pinned 3.x pair or be Captain re-recorded. If the receipt is missing
   or stale before the first working stage, invoke
   `kc-dev-flow:choose-work-profile`; let the locally authorized actor commit
   and re-read the Captain's choice. An unchanged v1 Pilot or Production choice
   upgrades mechanically. For a v1 POC, preserve the choice but use
   `kc-dev-flow:choose-work-profile` to complete the v3 POC fields with the
   Captain before dispatch.

If the repository changes planning provider, migrate only open planning items
that have not been admitted to SD. An already-admitted active SD task with a
resolvable planning link keeps its existing planning item and provider until
completion; the old provider must remain available for it. The legacy non-link
refusal above is not a migration and creates no planning item. New admissions
use the new provider. During this drain, each active item still has one
planning-item authority. Keep the active SD snapshot and its source, window,
outcome, and execution group unchanged. Reconcile each snapshot through the
reader for its own provider. Do not project SD state back to the provider,
import provider state into SD, poll either side, or rewrite an active snapshot
onto the replacement provider.

## Load one route

Invoke the repository-local profile loader declared in `## Local Profile` with
the exact committed work-item file. The loader derives and validates that item's
supported receipt and current status, then binds their hash into the output. The output
is the active contract: shared core, selected profile base, and selected stage.
Do not separately read the full kernel, another profile, another stage, or an
installed-package fallback. Profile selection is per work item, never a
project-global mode; simultaneous items may load different routes.

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

The canonical vendored loader invocation is:

```bash
python3 <profile-loader> \
  --contracts-root <contracts-root> \
  --work-item <exact-committed-work-item>
```

Use `--format json` only when a machine consumer needs the structured envelope.

At Production `ideation`, `skip_to_workflow_stage: implementation` loads no
contract and authorizes only that existing state transition: re-read the same
hash-bound item, create no ideation worker, briefing, report, or gate, then load
`build` normally. Before the skip, implementation exit, and validation, recheck
the recovery falsifier, exact diff against `scope_boundary`, rollback, and risk
list. False or uncertain evidence returns `RECOVERY_FULL_ROUTE_REQUIRED`; only
the Captain or an explicit `recovery_rollback` may re-record the full route.

A loader refusal means the item's current stage is outside its selected route,
its receipt is stale, or the adoption is incomplete. Resolve that exact
condition; do not substitute another item's profile or general workflow prose.

For a superset state graph, route as follows:

| Profile | Workflow states used |
|---|---|
| POC | `backlog -> implementation -> validation -> done` |
| Pilot | `backlog -> ideation -> implementation -> validation -> done` |
| Production | `backlog -> ideation -> implementation -> validation -> done`; eligible recovery skips the ideation dispatch |

`backlog` selects and queues; `done` terminalizes. They dispatch no working
contract. Skipped stages create no review or evidence obligation.

## Advance

At POC validation, use the repository-local `poc-close-guard.py`. Record one
`poc_outcome`, prepare the gate through the guard, and record approval without
`--consume`. Then record one Captain-owned `poc_handoff`: stop/change use
`not_applicable`; proceed uses created, deferred, or declined. A created item
must resolve uniquely by `source: poc:<exact-source-id>` before guarded consume.
Raw Spacedock remains bypassable; this is a fail-closed KC Dev Flow path, not an
engine tamper-resistance claim.

- Perform the selected stage mission and required output. Move to the loader's
  `next_workflow_stage` when its stated stop condition is met.
- Invoke `kc-dev-flow:chief-engineer` only for an unclear next step, a material
  blocker, route drift, or a selected transition that needs delivery sequencing.
- Invoke `kc-dev-flow:science-officer` only for a contested, high-risk,
  hard-to-reverse, or low-confidence technical claim, or on Captain request.
  Do not load the legacy `science-officer-em` adapter unless a consumer requests
  its legacy report envelope.
- Repair material findings with one owner and one final re-verification. Do not
  create an open-ended implementation-review loop.
- Use required deterministic gates at their declared boundaries. FO applies
  them; provider labels and agent advice do not replace them.
- Ask the Captain only for scope/profile change, irreversibility, new spend or
  permission, accepted red residuals, and merge or release authority.

After the exact selected route and repository delivery authority are satisfied,
terminalize through the existing state owner. Keep reports to decision, evidence
that changes the decision, and next action.

## Optional observations

At implementation exit, inspect the loader's
`implementation_exit_observation_declared` field. When the loader output is true,
read the selected build contract's `review_convergence` observation and provider
contract it names — `../../references/roborev-implementation-exit.md` — as the
method. Use fixed reviewer Codex `gpt-5.6-terra`, reasoning `medium`, and
`panel: none`; the actual host and implementation family is provenance only.
Pass the selected profile's minimum severity and caps explicitly. A full route
or named recovery risk emits true; recovery `[none]` emits false. A false or
absent declaration performs no RoboRev probe or invocation. An unavailable
fixed reviewer produces an honest non-gating `UNAVAILABLE` result.

The provider contract is vendored and loaded like any other conditional
reference, so an adopter that vendors the profile tree gets this capability
rather than having to author a runbook for it. Only the repository-local
bindings stay local. Load improvement harvesting only on an explicit request; it
never interrupts the selected product route.
