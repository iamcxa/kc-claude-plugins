---
commissioned-by: spacedock@0.26.0
entry-point: ship-flow:ship-shape
entity-type: feature
entity-label: feature
entity-label-plural: features
id-style: slug
state: .spacedock-state
stages:
  defaults:
    worktree: true
    concurrency: 2
  states:
    - name: draft
      initial: true
      worktree: false
    - name: shape
      worktree: false
      gate: true
      manual: true
      parallelism: probes
      skill: ship-flow:ship-shape
      model: opus
    - name: design
      worktree: true
      gate: true
      manual: conditional
      parallelism: lanes
      skill: ship-flow:ship-design
      model: opus
    - name: plan
      parallelism: draft-lanes
      skill: ship-flow:ship-plan
      model: sonnet
    - name: execute
      parallelism: dag
      skill: ship-flow:ship-execute
      model: sonnet
    - name: verify
      gate: true
      worktree: false
      parallelism: checks
      skill: ship-flow:ship-verify
      model: sonnet
      dispatch: debate-driven
      feedback-to: execute
    - name: ship
      worktree: false
      skill: ship-flow:ship-review
      model: sonnet
    - name: done
      terminal: true
      worktree: false
  transitions:
---

# Ship-Flow Pipeline

Ship-focused delivery pipeline for `kc-claude-plugins`. The captain shapes and
accepts the problem boundary once; agents then design, plan, execute, verify,
and prepare the change for review through durable stage artifacts.

This workflow runs [split-root state](https://spacedock.md/docs/advanced/split-root-state/):
the README and stage declarations live on the code branch, while mutable entity
state (entities, `_archive/`, `_debriefs/`) lives in a `.spacedock-state`
checkout — an orphan `spacedock-state/ship-flow` branch, gitignored on the code
branch. Routine stage transitions never churn the code branch. On a fresh clone
the checkout is absent; run `spacedock state init` to restore it.

> **Bad news early, no surprises.** Surface violated assumptions, ambiguous
> contracts, scope growth, state races, and incomplete evidence when discovered.

## Lifecycle

```text
draft -> shape -> design -> plan -> execute -> verify -> ship -> done
                                 ^              |
                                 +--------------+
```

- `shape` is the captain-facing product boundary gate.
- `design` always runs. Purely mechanical changes use its trivial-pass path;
  UI, domain, schema, API, architecture, and contract work receive explicit
  design treatment.
- `verify` is an agent gate. A failed verdict routes findings back to
  `execute`; it is not an implicit captain-approval prompt.
- `ship` prepares the PR and canonical documentation. The `pr-merge` mod owns
  the repository-specific review and merge lifecycle.

## Entity Layout

New entities use a folder so decisions and evidence survive context resets.
Under split-root state the entity root is the `.spacedock-state` checkout, not
the definition dir:

```text
docs/ship-flow/.spacedock-state/<slug>/
  index.md      # entity metadata and artifact links
  shape.md      # problem, appetite, constraints, DAG, and assumptions
  design.md     # design intent and design-dispatch-manifest
  plan.md       # tasks, TDD contract, reviewer questions, and plan-parallelization-manifest
  execute.md    # commits, RED/GREEN evidence, UAT, and execute-dispatch-manifest
  verify.md     # independent checks, reviewer panel, UAT, and verify-check-manifest
  review.md     # PR draft and canonical-document impact
  ship.md       # final PR and delivery receipt
```

Legacy flat entities and legacy `spec.md` shape artifacts remain readable, but
new work must use the folder layout and `shape.md`.

### Parallelism Contract

Ship-Flow uses stage-internal parallelism only. The stage chain remains serial
because each stage defines the next stage's input contract. Every parallel
stage has a single integrator responsible for reconciling lane output and
writing the durable stage artifact.

The plan-to-verify reviewer panel lane is explicit: plan turns domain and
framework `skills_needed` into task-level `reviewer_questions` and a hand-off
`domain_acceptance_checklist`; verify consumes those rows when building the
reviewer panel. Missing or failed required lanes must remain visible as
coverage gaps rather than being silently treated as success.

## Stage Contracts

### `draft`

- **Input:** A problem, request, issue, or observed failure.
- **Output:** Enough source context to begin shaping.
- **Good:** One coherent outcome with concrete evidence or motivation.
- **Bad:** Several unrelated changes hidden in one entity.

### `shape`

- **Input:** Draft context plus repository product and roadmap evidence.
- **Output:** `shape.md` with scope, appetite, done criteria, assumptions, and
  decomposition when the work is too large for one vertical slice.
- **Good:** The smallest independently valuable outcome with observable done
  criteria.
- **Bad:** Treating an implementation idea as the problem statement.

### `design`

- **Input:** Confirmed shape and relevant UI/domain/contract context.
- **Output:** `design.md` with a `design-dispatch-manifest` and an explicit
  proceed or route-back verdict.
- **Good:** Decisions and interface boundaries are resolved before planning.
- **Bad:** Skipping design because the work has no visual UI.

### `plan`

- **Input:** Confirmed shape and design artifacts.
- **Output:** `plan.md` with bounded tasks, dependencies, TDD expectations,
  runnable verification, `reviewer_questions`,
  `domain_acceptance_checklist`, and `plan-parallelization-manifest`.
- **Good:** Every task identifies files, evidence, and its downstream reviewer.
- **Bad:** Tasks described only as broad implementation intentions.

### `execute`

- **Input:** Accepted plan and dispatch manifests.
- **Output:** Tested implementation plus `execute.md` and an
  `execute-dispatch-manifest` recording lane ownership and integration.
- **Good:** RED-before-GREEN evidence, explicit commits, and bounded recovery.
- **Bad:** Silent scope expansion or unverifiable completion claims.

### `verify`

- **Input:** Execute diff, done criteria, reviewer questions, and evidence.
- **Output:** Independent quality checks, reviewer findings, UAT, a
  `verify-check-manifest`, and a machine-readable verdict in `verify.md`.
- **Good:** Required lane failures remain visible and prevent an approval
  verdict while optional failures are recorded as evidence.
- **Bad:** Converting missing coverage into an implicit pass.

### `ship`

- **Input:** A passing verify verdict and complete delivery evidence.
- **Output:** Review-ready PR draft, documentation impact, and durable shipping
  receipt.
- **Good:** Exact-head evidence and an idempotent PR hand-off.
- **Bad:** Posting or merging before the configured review gates complete.

### `done`

Terminal lifecycle state reached only after merge reconciliation and archival.

## Hierarchy and Dependencies

Large directives become an epic with vertical child entities. `parent` groups
children; `depends-on` controls execution order. Create the full dependency
graph during shaping, but dispatch only children whose dependencies are done.

```yaml
entity_type: entity
parent: agent-native-pr-toolkit
depends-on:
  - runtime-shadow-harness
```

## Entity Schema

```yaml
---
id:
title:
status: draft
source:
started:
completed:
verdict:
priority:
score:
worktree:
parent:
depends-on: []
tracker:
issue:
external_id:
pr:
token_budget:
token_actual:
entity_type: entity
children: []
mod-block:
review_resolve_pending:
---
```

- `status` is one of `draft`, `shape`, `design`, `plan`, `execute`, `verify`,
  `ship`, or `done`; epics use `status: epic`.
- `priority` is captain urgency (`P0` through `P3`); `score` is the shaping
  quality score and is not a substitute for priority.
- `parent` creates hierarchy; `depends-on` creates DAG edges.
- `mod-block` records a mod-owned lifecycle block and must be cleared before
  terminalization.

## Repository Operating Rules

- Follow the root `CLAUDE.md` and the nearest plugin-local `CLAUDE.md`.
- Feature work never hand-bumps plugin versions; release-please owns release
  versions and changelogs.
- Stage and commit only explicitly named paths.
- New entity work runs in an isolated worktree.
- Public PR bodies, comments, and reviews must not contain local absolute paths
  or personal information.
- A merged PR is not equivalent to a reconciled `done` entity; the merge hook
  must clear blocks, terminalize, and archive successfully.

## Status Commands

```bash
spacedock status --workflow-dir docs/ship-flow
spacedock status --workflow-dir docs/ship-flow --archived
spacedock status --workflow-dir docs/ship-flow --next
spacedock status --workflow-dir docs/ship-flow --validate
```

## Commit Discipline

Use pathspec locks at both stage and commit time:

```bash
git add -- <path1> <path2>
git commit -m "<type>(<scope>): <description>" -- <path1> <path2>
```

Never use `git add .`, `git add -A`, or `git commit -a` in workflow-managed
worktrees.

## Ship-flow runtime

This section applies only to a First Officer that dispatches build workers into
Conductor cloud workspaces and reads them back through the `conductor` CLI. It
is this repository's own runtime record, not a kc-dev-flow contract: an adopter
running workers locally, on a Hermes runner, or on another host is not covered
by it and must not treat these sentences as requirements.

Dispatch a higher layer only after the lower layer is fully verified. (DEV-67)

A dispatch message to a cloud build worker carries no bootstrap or download
line: the Conductor WAF blocks a dispatch message containing a `curl | tar`
bootstrap line, and the worker's image already preinstalls `kc-dev-flow` and
`spacedock`, so no dispatch message needs to fetch and unpack them. A task
body longer than the first message does not fit in that message either; it
travels on a committed carrier — a file such as `DISPATCH.md` committed to a
branch the worker fetches and reads with `git show <branch>:<path>` — rather
than being pasted inline.

A worker's without-it command runs in an isolated environment (temporary HOME, no agent, no network). (DEV-67)

CLI e2e evidence is a timestamped stdout log written by
`scripts/ship-flow/e2e-cli.sh <sha> <flow.yaml>`. It runs each of the flow's
`Execute external` steps (e2e-pipeline's `execute.cli` step shape, consumed
read-only) at the pinned `<sha>` and exits non-zero on the first step whose
command's exit code does not match its declared `expect`. `asciinema` and
`script(1)` both hang without a pty, which cloud build workers do not have, so
this stdout log — not a terminal recording — is the CLI e2e evidence of
record for that context.

The worker's Evidence block defines `CANDIDATE_SHA`, `BRANCH`, `BASE_SHA`,
`WITHOUT_IT_COMMAND`, and `WITHOUT_IT_REMOVED_VARIANT`. `WITHOUT_IT_COMMAND` is
one self-contained shell line: it references no file outside the candidate
tree, it exits 0 on the candidate and non-zero once `WITHOUT_IT_REMOVED_VARIANT`
is applied, and the First Officer runs it verbatim, unchanged, in a worktree
with no secrets. `scripts/ship-flow/without-it.sh <sha> <command>
<removed-variant>` runs `<command>` retained, applies `<removed-variant>`, runs
`<command>` again, and exits 0 only when the retained run passes and the
removed run fails.

Security, data-loss, and compatibility findings outside the Brief block the candidate while general improvements are scoped out. (DEV-67)

Ship-flow's workspace-create guarantee is that the production entry issues at
most one `conductor workspace create` call after a committed intent:
`conductor workspace create` is not idempotent and a holder can sleep between
the call and its receipt, so every external action follows one order —
`scripts/ship-flow/intent.sh commit` writes the claim, dispatch token,
project, base branch, and message sha256 to the state branch and pushes it;
`holder.sh check` confirms the writer; the create is called once with the
token in the workspace name; the token, name, and project are read back;
`holder.sh check` runs again; only then `intent.sh adopt` persists the
workspace id. It is not exactly-once and it covers workspace creation only: a
holder that takes over runs `intent.sh reconcile` first, adopting the one live
workspace whose name carries the intent's token and whose project matches,
blocking with `unresolved intent` on zero matches and `ambiguous intent` on
two or more, and in no case does the new holder create a workspace for an
intent it did not commit. `intent.sh commit` and `intent.sh adopt` hold an
flock on `<state-dir>/.ship-lock` around their whole sync-write-commit-push
sequence so two concurrent calls on the same checkout serialize instead of
racing the shared working tree, and the intent binds the dispatched project,
base branch, and message sha256 so reconcile and every adopt refuse a
candidate workspace with `project mismatch` when its project id does not
match the one committed.

The First Officer reads a worker's transcript through `conductor sql` against
`session_transcripts_view`, not `conductor session message --after`: that CLI
truncates its JSON response at 64 KB, which cuts off a long Evidence block, and
its `--after` cursor rejects a sent message's id, which breaks polling from the
FO's own last message. `scripts/ship-flow/worker-transcript.sh <session-id>`
prints the session's last fenced `## Evidence` block, or exits 1 with `no
evidence block` when the transcript has none. One read per invocation; no
polling loop, retry, or daemon.
