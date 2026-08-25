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
3. Read iteration authority. If it contains no committed item, report that
   scheduling is needed; do not inspect or invent execution state.
4. Read the exact committed work item and current state from their declared
   authorities. Do not enumerate the state tree.
5. Re-read `## Work profile receipt`. If v2 is missing or stale before the first
   working stage, invoke `kc-dev-flow:choose-work-profile`; let the locally
   authorized actor commit and re-read the Captain's choice. An unchanged v1
   choice upgrades mechanically without another Captain question.

## Load one route

Invoke the repository-local profile loader declared in `## Local Profile` with
the exact committed work-item file. The loader derives and validates that item's
v2 receipt and current status, then binds their hash into the output. The output
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
trigger true and the second false. `implementation_exit_observation_declared` is
true only at a build stage whose emitted typed observation names a provider and
whose repository meets that provider's recorded precondition; it is the method
for that observation, not an extra review. RoboRev's precondition is a
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

A loader refusal means the item's current stage is outside its selected route,
its receipt is stale, or the adoption is incomplete. Resolve that exact
condition; do not substitute another item's profile or general workflow prose.

For a superset state graph, route as follows:

| Profile | Workflow states used |
|---|---|
| POC | `backlog -> implementation -> validation -> done` |
| Pilot | `backlog -> ideation -> implementation -> validation -> done` |
| Production | `backlog -> ideation -> implementation -> validation -> done` |

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

At implementation exit, inspect only the typed observation in the selected
`build` contract returned by the loader. When it declares `review_convergence`
in `observe` mode, that same `build` contract's
`implementation_exit_observation_declared` trigger is true, so read the provider
contract it names — `../../references/roborev-implementation-exit.md` — as the
method. Take the reviewer mapping, state holder, prerequisite, and durability
command from `## Local Profile`, select the reviewer complementary to the actual
implementation provider family, and pass the emitted profile controls explicitly.
An absent declaration leaves the trigger false and performs no RoboRev probe or
invocation. An unknown implementation family or unavailable provider produces an
honest non-gating `UNAVAILABLE` result; do not guess or use ambient defaults.

The provider contract is vendored and loaded like any other conditional
reference, so an adopter that vendors the profile tree gets this capability
rather than having to author a runbook for it. Only the repository-local
bindings stay local. Load improvement harvesting only on an explicit request; it
never interrupts the selected product route.
