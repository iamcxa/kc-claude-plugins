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
| Production | `backlog -> ideation -> implementation -> validation -> done`; eligible recovery skips the ideation dispatch |

Backlog and done are state boundaries, not worker stages. Skipped stages do not
receive placeholder reviews or receipts.

<!-- kc-dev-flow-static-local-profile:start -->
## Local Profile

Read only this section before resolving the selected item. Do not read this full
README as a policy bundle.

Linear is this repository's planning provider for new provider-backed
admissions, not an iteration authority. A Linear Project is the planning
outcome and release package, its Cycle is the planning window, and active
`unstarted` or `started` Issues select candidates. Spacedock tasks are execution
records, and `source` links the accepted Linear Issue. At every provider-backed
engage, compare the current Project/Cycle active set with the committed SD
snapshot. A difference requires Captain admission and never writes either side
automatically. Existing admitted work keeps its recorded provider and reader;
GitHub Project #4 remains historical and receives no new admissions. A
standalone Captain-approved brief leaves `source`, `planning-window`, and
`planning-outcome` empty and invokes no provider reader or comparator.

| Role | Bound local authority |
|---|---|
| Project context | Root `PRODUCT.md`, `ARCHITECTURE.md`, and `CLAUDE.md` |
| Planning items | Linear Issues in team `dev`; new provider-backed admissions only |
| Planning window | Linear Cycle |
| Planning outcome | Linear Project as one user-value release package |
| Planning reader and admission guard | Installed sibling `linear-admission.py`; organization `duckbase-co`; read `LINEAR_API_KEY` and `CONDUCTOR_WORKSPACE_ID` only from Conductor env, accept no credential argument or prompt, reconcile exact Project/Cycle active Issues, and emit the engaged Issue's exact `branchName` plus `Fixes DEV-N` |
| Planning comparator | Installed sibling `engage-reconcile.py` supplied by the activated `kc-dev-flow` skill; no stored installation path |
| Work items | Spacedock execution records under `docs/dev/` |
| Execution grouping | Shared SD `sprint` value; `docs/dev/ROADMAP.md` registers legacy or local group identifiers only |
| Execution state | `docs/dev/.spacedock-state` on `spacedock-state/dev`, owned by Spacedock |
| Profile receipt | `## Work profile receipt` in the exact work item |
| Profile loader | Installed `profile-contract-loader.py` supplied by the activated `kc-dev-flow` skill; default loading preserves admitted headings, while only the Linear admission guard selects `--validate-admission` for new Pilot or Production work |
| POC close guard | Installed sibling `poc-close-guard.py` supplied by the activated skill |
| Installed contract interface | `kc-dev-flow-local-profile/v1` |
| Local mods | `docs/dev/_mods/pr-merge.md` |
| Delivery | GitHub PR to `main`; required checks; release-please owns versions and tags |
| Scope, profile, irreversibility, merge/release | Captain |
| Orchestration | First Officer |
| Normal delivery advice | `kc-dev-flow:chief-engineer`, only on its bounded triggers |
| Independent assurance | `kc-dev-flow:science-officer`, only on its bounded triggers |
| Optional observation | Typed RoboRev observation at every profile's implementation exit where eligible: Pilot, full Production, retained/safety-bound POCs, and named-risk Production recovery; direct POCs and recovery `[none]` invoke nothing |
| RoboRev local bindings | Fixed reviewer Codex `gpt-5.6-terra`, reasoning `medium`, `panel: none`; implementation family is provenance only; `.roborev.toml` is the repository fallback; state holder `docs/dev/.spacedock-state`; prerequisite `scripts/dev-flow-state-prereq.sh`; durability `spacedock state commit` |
| Conditional references | Installed manifest resources `reverse-recovery-audit.md`, `journey-slicing.md`, `retained-document-policy.md`, `project-context-maintenance.md`, `delivery-branch-base.md`, `pr-delivery.md`, and `roborev-implementation-exit.md` |
| Delivery branch base | `delivery_artifact_review` is true: this repository delivers through GitHub PRs. **Local base policy: dependency-aware.** Independent units target trunk. Dependent green layers use the reviewed sibling branch immediately below and its exact candidate SHA; only the top provider-backed layer uses the provider delivery branch and close line. The local `pr-merge` mod preserves every reviewed branch/base pair. |
| Workflow scope | This repository's own plugin development is in scope, not exempt. The countable trigger is a **second pull request for the same piece of work**: one PR may be a small task, a second says it is not — stop there and take the work through the stages. Entering means reading this Local Profile section first, before the selected item; a session that runs the stages while skipping this table still misses the local base policy and the bound authorities below. Recorded 2026-08-22 after four plugin PRs merged with no entity, no stage report and no gate, and the largest defect among them survived to `main` because nothing had asked what would falsify it. |
| PR lifecycle | Spacedock `pr-merge`, only when a PR is the selected delivery artifact. It owns the ceremony, so `pr_delivery_selected` stays false and `pr-delivery.md` is not loaded here. |

The activated `kc-dev-flow` skill supplies its self-locating installed loader.
`contract-manifest.json` binds the package version, contract digest, Local
Profile interface, and canonical runtime resources. This repository retains
only README policy, local mods, provider adapters, and Spacedock state;
`scripts/kc-dev-flow-contract-test.py` checks every supported profile-stage
combination and rejects canonical repository copies.

The selected stage resolves documentation triggers from accepted scope and
rechecks them against the exact diff before implementation exit or validation.
An accepted or observed retained-document change loads
`retained-document-policy.md` without creating a receipt. A possible changed
claim in the bound `PRODUCT.md`, `ARCHITECTURE.md`, or `CLAUDE.md` context loads
`project-context-maintenance.md` and records its existing `project_context`
receipt. Work-item records and unrelated Markdown changes activate neither.

The selected profile's `build.md` supplies one typed `review_convergence`
observation in `observe` mode, which appears only in the implementation-stage
loader result. The runbook fixes agent `codex`, model `gpt-5.6-terra`, reasoning
`medium`, and `panel: none`; the actual host and implementation family is
provenance only. Pass every value explicitly; `.roborev.toml` is only the
committed repository fallback and installs no hook or panel.
For Production recovery, a named `review_risks` entry is also required to
activate it; the Production label and `[none]` are insufficient.

| Profile | Reasoning | Minimum severity | Timeout | Request / confirmation cap |
|---|---|---|---:|---:|
| POC | `medium` | `high` | 10 minutes | `1 / 0` |
| Pilot | `medium` | `medium` | 15 minutes | `1 / 1` |
| Production | `medium` | `medium` | 20 minutes | `1 / 1` |

All use `panel: none`. The result is observation, not validation or delivery
authority. Missing CLI, daemon/local mode, mapped agent, authentication, or host
bridge is an honest `UNAVAILABLE`; normal fresh validation remains reachable.

<!-- kc-dev-flow-static-local-profile:end -->

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
`kc-dev-flow-work-profile/v3` receipt for new choices. If missing or stale, invoke
`kc-dev-flow:choose-work-profile`; the Captain chooses and the authorized actor
commits and re-reads it. An unchanged v1 Pilot or Production choice upgrades
mechanically. A v1 POC keeps its choice but needs the Captain to complete the v3
POC fields before dispatch.

Use the host's structured Ask UI when available; plain chat is the fallback.
Selection precedes acceptance-criteria expansion and stage dispatch.

The activated skill supplies its exact installed loader path as
`$KC_DEV_FLOW_LOADER` for the current invocation; do not persist that path. The
First Officer also supplies the state-owned pin path and runtime-owned attempt:

```bash
python3 "$KC_DEV_FLOW_LOADER" \
  --work-item "$EXACT_COMMITTED_WORK_ITEM" \
  --local-profile docs/dev/README.md \
  --stage-pin "$EXACT_STAGE_PIN" \
  --stage-attempt "$EXACT_STAGE_ATTEMPT" \
  --write-stage-pin
```

Write and commit the pin before dispatch, then rerun without
`--write-stage-pin` and require exact readback. Same-stage re-entry restores the
pinned plugin when version or digest differs. A compatible upgrade takes effect
only when the next stage writes its pin; `LOCAL_PROFILE_REFIT_REQUIRED` stops
before pin write or dispatch and names this README plus `Local mods` for Captain
review; after the accepted refit, rerun with `--accept-local-profile-refit`.
Plugin upgrades do not rewrite README policy, local mods, provider
adapters, or unrelated Spacedock state.

The command validates and hash-binds that item's supported receipt and current status,
then emits the shared core, one selected base, and one selected stage. At a
route's first working stage it also requires one non-empty `sprint` and
`sprint-readiness: ready` as local Spacedock execution mechanics. They do not
prove a Planning Receipt. Its
`next_workflow_stage` is the normal next state. An eligible Production recovery
instead emits `skip_to_workflow_stage: implementation` with no loaded ideation
contract. Profiles are per item, so POC, Pilot, and Production items may run
concurrently in this repository without a global profile switch. A refusal
blocks only that item's dispatch until its receipt, state, scheduling fields, or
installed binding is corrected.

## Stages

Each working stage uses the loader command above. The text below only binds
repository mechanics; it does not repeat the profile contract.

### `backlog` — queue and select

Capture `title`, `product`, and the required Development Brief or Exploration
Brief. Only the Captain admits it. Provider-backed work records the complete
`source`, `planning-window`, and `planning-outcome` tuple; standalone work records
none of it. A partial tuple stops. This Spacedock adoption separately requires a
shared `sprint` execution-group value and `sprint-readiness: ready`. Queued items
carry `sprint-readiness: defer` until then, so the admitted execution set is
`spacedock status --workflow-dir docs/dev --where sprint=<group> --where
sprint-readiness=ready`. Obtain and commit the supported profile receipt before
moving to the selected route's first working state.

### Engage reconcile

For a new Linear-backed Pilot or Production admission, pin the full state commit
and run the combined guard. Resolve installed `../../scripts/linear-admission.py`
from the active skill as `$KC_DEV_FLOW_LINEAR_ADMISSION` for this invocation;
never persist it. No manual MCP read, copied provider JSON, or hand-written
normalization is accepted:

```bash
python3 "$KC_DEV_FLOW_LINEAR_ADMISSION" \
  --workflow-dir docs/dev \
  --work-item "$EXACT_COMMITTED_WORK_ITEM" \
  --profile-loader "$KC_DEV_FLOW_LOADER" \
  --local-profile docs/dev/README.md \
  --linear-workspace duckbase-co \
  --state-revision "$EXACT_40_HEX_STATE_REVISION" \
  --timeout 30
```

Success stdout is one `kc-dev-flow-dispatch-envelope/v1` object. Every
authentication, canonical-brief, pagination, snapshot, comparator, race, or
timeout refusal has empty stdout, so the First Officer has no dispatch input.
Its ephemeral `delivery` binding supplies the exact forge head branch and PR
close line. The command is read-only and never creates a task or workspace.

For a complete Planning Receipt, before reading execution state or dispatching
new work, run the read-only planning reader for the union of the snapshot's
`planning-window`/`planning-outcome` Ready set and every currently Ready snapshot
source outside those bounds. Refuse a truncated result. Compare that union with
every non-terminal committed SD entity sharing its `sprint` (a `done` or archived
item has left the active set and is not a removed planning item): source membership, window,
outcome, accepted outcome, and non-goals. Normalize both sets into ephemeral JSON
lists and refuse the snapshot unless every item shares the engaged item's exact
window and outcome. Run the bound planning comparator with `--expected-source`,
`--expected-window`, and `--expected-outcome` set to the exact engaged work item
values. Exit `0` continues only when stdout parses as one JSON object with
`status: clean` and empty delta arrays. Any other output stops before new
dispatch or state mutation: exit `1` reports added, removed, changed, and moved
items; exit `2` or an invalid exit-`0` payload reports unavailable input. The
Captain admits every delta before an authorized actor commits the replacement
snapshot. Do not cancel a running worker. This is reconcile, not projection or
sync: neither side is written automatically. A standalone item skips this whole
provider branch and uses its Captain-approved committed brief.

### Development Brief

A Linear Issue used for admission has this body shape without a
`## Human-readable release brief` wrapper:

```markdown
## The problem

## Goal

## Non-goals

## Acceptance criteria

- **AC-1** <observable condition>

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning
delta that names the changed premise, affected acceptance evidence, and
recommended change or stop.
```

`python3 scripts/kc-dev-flow-contract-test.py` checks this shape; the minimal-stack
ablation test mutates each boundary and requires rejection for the named reason.
At gate time, Spacedock `--ac-scan` must find every stable `AC-N` identifier in
the latest Stage Report with no unknown or uncovered criterion.

### `ideation` — selected `shape`

Active only for Pilot and full-route Production. An eligible recovery creates no
worker, briefing, report, or gate here; re-read its hash-bound receipt, apply the
implementation skip, and load `build`. Otherwise load the selected `shape`
contract. For a complete Planning Receipt, copy the planning item's accepted
outcome and non-goals into the work item as an admission snapshot; it is not a
second accepted-goal authority. For standalone work, the Captain-approved
committed Development Brief already holds that authority. Record task-specific
acceptance evidence as execution evidence.
Its conditional references load only when their predicates fire: reverse
recovery for a proposed addition, replacement, removal, or missing claim in
existing code; the multi-slice guard when one integrated slice is insufficient.
POC moves directly from backlog to implementation.

### `implementation` — selected `build`

Load the selected `build` contract. Use an isolated worktree when the checkout is
contended. Run scoped checks while iterating and only the relevant exit checks
earned by the selected profile and diff.

POC build performs its conditional reverse-recovery check here because POC has
no shape stage. Pilot and Production do not repeat a completed shape audit; an
unplanned new surface returns to the stage that owns scope.

After tests and an exact candidate revision exist, a true loader
`implementation_exit_observation_declared` loads the installed
`roborev-implementation-exit.md` resource as the build observation. Direct
no-code/disposable POCs emit false and perform
no provider work; retained or safety-bound POCs stay fresh. Its receipt is
observation, not validation or delivery authority. POC ends after one request;
Pilot and full-route Production allow one changed-tip confirmation.
Recovery allows that observation only for a named accepted risk. Recheck its
falsifier, exact diff, rollback, and risks before exit and validation; uncertainty
returns `RECOVERY_FULL_ROUTE_REQUIRED` to the Captain-owned full-route decision.

### `validation` — selected `prove`, `verify-deliver`, or `verify`

Load the stage selected by the profile loader. Read
[`runbooks/validation-evidence.md`](./runbooks/validation-evidence.md) only for
Production verification or when the accepted Pilot evidence explicitly names
it. POC does not load it.

When a GitHub PR exists, observe all current provider feedback at the exact head
and record a bounded disposition. A code repair returns to implementation and
gets one final re-verification. A new delivery completes its selected local
verification before Captain-authorized Draft creation.

`pr-merge` owns PR creation, provider polling, and landed-state reconciliation.
It is a delivery event mod, not a profile contract, and remains unread until PR
delivery is selected or a tracked PR needs reconciliation.

POC and Pilot proceed to done after their selected delivery authority is met.
For a direct POC, build durably records `poc_outcome`; `poc-close-guard.py`
checks the admission-to-outcome time, separate close measurement, and proof path,
then moves the item to `validation` only for the existing terminal gate without
dispatching a validation worker. Fresh POCs record the outcome in validation.
The guard prepares and consumes the approval gate and terminalizes the experiment. KC Dev Flow then
returns the outcome to planning; it creates no downstream item and preselects no
profile. Planning alone may admit a new, independent Development Brief.
Production's validation gate approval targets the terminal `done` stage, so
`gate consume` leaves it pending (`route=approved-awaiting-merge`) instead of
landing anywhere: `spacedock merge guard <slug> --verdict passed|rejected` is
the sole terminal consumer of that approval, and it refuses to finalize
without one pending. This keeps two separately timestamped rulings on record
without a dedicated `release` state — the validation gate's
`resolution.decision: approve` ("the code is verified") and the merge-guard
verdict ("this may be released") — and it is refused, not silently skipped,
when the pending approval or the merge-guard verdict is absent. Required
checks, rollback or forward-recovery readiness, operational ownership, and
explicit Captain-or-release-owner authorization apply to the exact delivery
revision per `production/verify.md`'s Required output.

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
| Production release (validation's terminal-target approval + `merge guard --verdict`) | Captain or declared release owner |
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

## Placing a finding

Kept from the retired `promote-dev-flow` skill, which was deleted with the adopter-to-source
transport it gated. The transport is gone; this judgment is not, because findings still
arrive — from a review, an adopter's own audit, or a session debrief. Run the reverse-recovery
audit first, then pick one:

| Disposition | Meaning | Destination |
|---|---|---|
| `rule-gap` | A portable semantic obligation is absent. | Kernel proposal. |
| `enforcement-gap` | The rule exists but repeated violations lack a control. | Named enforcement point; no duplicate clause. |
| `local-instance` | The rule is portable but the topology or mechanism is not. | Return to the adopter's authority. |
| `duplicate/no-change` | Existing work covers it, or the rule worked as designed. | Merge observations or retain evidence only. |

Record the observations, recurrence, expected value, cost, disproof hook, duplicate search,
disposition, target, and the result that would reverse the classification. Most "missing rule"
findings are `enforcement-gap`: grep for the rule before proposing it, and check that the
precedent being copied actually runs.

## Task template

```yaml
---
id:
title:
status: backlog
source:
product:
planning-window:
planning-outcome:
sprint:
sprint-readiness: defer
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
---

## The problem

## Work profile receipt

## Accepted outcome

## Non-goals

## Acceptance evidence

## Route-back conditions

## Measurement
```

Keep stage reports to decision, evidence that changes the decision, and next
action. Link raw artifacts instead of replaying the session narrative.

## Ship-flow runtime

This section applies only to a First Officer that dispatches build workers into
Conductor cloud workspaces and reads them back through the `conductor` CLI. It
is this repository's own runtime record, not a kc-dev-flow contract: an adopter
running workers locally, on a Hermes runner, or on another host is not covered
by it and must not treat these sentences as requirements.

A dispatch message to a cloud build worker carries no bootstrap or download
line: the Conductor WAF blocks a dispatch message containing a `curl | tar`
bootstrap line, and the worker's image already preinstalls `kc-dev-flow` and
`spacedock`, so no dispatch message needs to fetch and unpack them. A task
body longer than the first message does not fit in that message either; it
travels on a committed carrier — a file such as `DISPATCH.md` committed to a
branch the worker fetches and reads with `git show <branch>:<path>` — rather
than being pasted inline.

CLI e2e evidence is a timestamped stdout log written by
`scripts/ship-flow/e2e-cli.sh <sha> <flow.yaml>`. It runs each of the flow's
`Execute external` steps (e2e-pipeline's `execute.cli` step shape, consumed
read-only) at the pinned `<sha>` and exits non-zero on the first step whose
command's exit code does not match its declared `expect`. `asciinema` and
`script(1)` both hang without a pty, which cloud build workers do not have, so
this stdout log — not a terminal recording — is the CLI e2e evidence of
record for that context.
