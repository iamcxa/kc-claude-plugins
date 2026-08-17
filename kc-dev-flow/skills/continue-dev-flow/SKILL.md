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
| Production | `backlog -> ideation -> implementation -> validation -> release -> done` |

`backlog` selects and queues; `done` terminalizes. They dispatch no working
contract. Skipped stages create no review or evidence obligation.

## Advance

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
in `observe` mode, resolve the repository-local
RoboRev runbook from `## Local Profile`, select the reviewer complementary to the
actual implementation provider family, and pass the emitted profile controls
explicitly. An absent declaration performs no RoboRev probe or invocation. An unknown
implementation family or unavailable provider produces an honest non-gating
`UNAVAILABLE` result; do not guess or use ambient defaults.

`../../references/roborev-implementation-exit.md` is an adoption source, not a
runtime fallback. Load improvement harvesting only on an explicit request; it
never interrupts the selected product route.
