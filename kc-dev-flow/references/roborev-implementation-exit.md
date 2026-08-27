# RoboRev Implementation Exit

Use this provider contract when the selected build contract in the profile
loader result declares `review_convergence` in `observe` mode with `provider: roborev` at
`implementation exit`. The observation gives fresh validation exact-tip defect
evidence. It does not replace validation and it does not make RoboRev a gate.

## Precondition

This contract's single-flight claim runs through a Spacedock-registered state
holder and its supported state transaction. That dependency is deliberate and is
not being made portable: the observation is in scope for a repository running
Spacedock together with kc-dev-flow, and out of scope for one that is not.

A repository with no Spacedock state authority records that once and leaves the
observation unloaded. That is a declared boundary, not a missing binding, not an
adoption defect, and not an `UNAVAILABLE` result to re-derive at every
implementation exit. Ordinary fresh validation is unchanged either way.

## Activation and repository ownership

The typed observation and repository Local Profile together name:

- the repository-local contract path and selected build-contract configuration;
- the selected profile and fixed reviewer: agent `codex`, model
  `gpt-5.6-terra`, reasoning `medium`, and `panel: none`;
- the actual host and implementation family as provenance only;
- `agent`, `model`, `reasoning`, `minimum severity`, and `panel: none`;
- the exact implementation-exit boundary and `observe` mode;
- the live-batch timeout, explicit-request cap, and repair-confirmation cap;
- any authorized local-command bridge.

An absent typed declaration performs no RoboRev detection, configuration read,
provider query, or invocation. An absent fixed reviewer or missing field is
`UNAVAILABLE(reason: unavailable)`; ambient global defaults do not fill it.
File presence alone does not activate this contract. The actual host and
implementation family is provenance only and never selects the reviewer.

RoboRev reads repository configuration from its precedence chain, and exact
commit/range reviews may read the default branch's copy. Resolve the typed
observation and mapped reviewer from the candidate Git object, record that
object's configuration hash, and pass the values explicitly to the candidate
review command. This keeps a new candidate configuration repository-owned
before it reaches the default branch. A default-branch configuration may be used
after its bytes match the recorded candidate hash. Every profile forces
single-reviewer execution with `--panel none`.

## Capability matrix

Probe the actual execution host without installing, updating, starting, or
supervising RoboRev or an agent.

| Capability | Green evidence | Non-green result |
|---|---|---|
| CLI contract | Version plus `review`, `list --json`, and `show --json` help | Missing binary/command is `UNAVAILABLE`; missing JSON correlation is `UNAVAILABLE(reason: unsupported)` |
| Execution state | Reachable daemon/state for queued work, or a declared compatible local mode | Missing daemon/state is `UNAVAILABLE`; a named panel without daemon support is `UNAVAILABLE(reason: unsupported)` |
| Agent and authentication | Configured agent is available and authenticated on this host | Missing agent/auth is `UNAVAILABLE(reason: unavailable)` |
| Local-command bridge | Declaration authorizes it and the remote and local checkout prove the same repository, base, and tip | Missing bridge or a SHA mismatch is `UNAVAILABLE`; do not cross the host boundary |

`CONDUCTOR_IS_LOCAL` describes an environment, not provider capability. Apply
the same probes in Conductor Cloud. Tool absence is an honest fallback and
fresh validation remains reachable.

## Exact-input identity

Canonicalize and hash these fields before the first provider query:

```text
repository identity
base SHA
tip SHA
RoboRev version and required JSON command/response contract
configuration object SHA
selected profile and implementation provider family
agent, model, reasoning, minimum severity
live-batch timeout, request cap, and repair-confirmation cap
panel identity, sorted stable member identities, and complete member count
```

The claim identity is the SHA-256 of that canonical record. Provider evidence
matches only when its repository, exact range or tip, configuration, selected
profile, implementation family, RoboRev version/JSON contract, agent, model,
reasoning, minimum severity, caps, timeout, panel
identity, stable member identities, and complete population match the record.
Every evidence field must be present; missing or null fields and malformed,
duplicate, extra, or incomplete member populations are `UNKNOWN(reason:
stale)`, never values copied from the expected record. Human-formatted output
is diagnostic; it cannot establish `PASS`.

## Existing-state single-flight transaction

First query queued, running, and completed jobs for reusable exact-input
evidence. If none matches, claim the identity in the current work item's
implementation evidence through the Local Profile's registered state holder,
clean-holder prerequisite, and supported Spacedock state transaction. For this
repository the prerequisite is `scripts/dev-flow-state-prereq.sh` and the
durability command is `spacedock state commit`; adopters resolve their declared
equivalents rather than copying those paths blindly.

1. Resolve the declared holder, prerequisite, and Spacedock executable before
   mutating state. An absent executable is `UNAVAILABLE(reason: unavailable)`.
   A missing or non-holder checkout, dirty holder, local-ahead holder, divergent
   holder, or failed prerequisite is `UNKNOWN(reason: state_unknown)` and earns
   no claim preparation.
2. Run the clean-holder prerequisite. Exit zero establishes the registered
   holder at the freshly observed remote state revision; a behind checkout may
   proceed only after the prerequisite fast-forwards it and proves equality.
   Record that exact revision and re-read the bound task. A shared parent that
   already records the identity returns `UNKNOWN(reason: claim_lost)`.
3. Append one claim containing identity, claimant, observed state revision, and
   `state: claimed` to the bound task. Before durability, prove that the holder
   HEAD is still the recorded revision and the bound task is the sole dirty
   path. A missing, bypassed, or additionally dirty boundary is
   `UNKNOWN(reason: state_unknown)`.
4. Fetch the authoritative state ref once more. If it no longer equals the
   recorded revision, return `UNKNOWN(reason: stale)` without committing,
   rebasing, or retrying the claim.
5. Invoke `spacedock state commit --workflow-dir "$WORKFLOW_DIR" "$SLUG"`.
   This is the supported Spacedock state transaction: it commits the bound task,
   integrates peer state only through Spacedock's durability rules, and pushes
   the registered state branch. Do not substitute raw `git commit`/`git push`,
   manually pull or rebase, or retry a rejected claim transaction. A
   same-entity conflict or remote claimant is `UNKNOWN(reason: claim_lost)`; an
   indeterminate write is `UNKNOWN(reason: state_unknown)`.
6. After success or rejection, fetch and perform a post-push re-read of the
   authoritative task. The claimant proceeds only when the supported command
   succeeded and the remote record names exactly its identity and claimant. Any
   other state is a loss or indeterminate state.

The supported transaction's same-entity conflict is the independent-clone
enforcement point; the existing claim check is the shared-parent enforcement
point. A claim loser performs no provider re-query, enqueue, or retry. Do not
add another ledger, tracker, daemon, or generalized lock service.

## Winner observation protocol

The claim winner re-queries provider jobs. It reuses a matching queued,
running, or completed parent job. If none exists, it snapshots current job IDs
and makes one explicit request with the exact base/tip and the declared
agent/model/reasoning/severity/panel flags.

The supported `review` command has no stable JSON launch receipt. Correlate the
request by comparing the post-request `list --json` population with the
snapshot. Accept the launch identity when one new parent job matches the full
exact-input record, including provider version/JSON contract, reviewer
configuration, panel identity, and the complete stable member population. Zero,
multiple, stale, or ambiguous candidates produce
`UNKNOWN(reason: state_unknown)` and do not earn another request.

Wait within the declared live-batch timeout and re-read the selected job with
`show --job <id> --json`. Record job ID and UUID, exact input, status, verdict,
configuration, and the complete configured member population. At the deadline,
record `UNKNOWN(reason: timed_out)` without duplicate enqueue.

## Correlation precedence and closed mapping

Apply correlation before lifecycle and verdict interpretation. A repository,
range/tip, configuration, provider version/JSON contract, agent, model,
reasoning, minimum severity, panel identity, stable member identity, or complete
population mismatch is `stale`; when that same evidence also has an incomplete
member, `stale` wins over `member_incomplete`. For an exact-input job, execution
failure wins over deadline, skip, or findings, then member skip wins over
incomplete state, and an incomplete or ambiguous member wins over a completed
parent verdict.

| Observation | Work Control receipt |
|---|---|
| Exact-input terminal JSON; parent and members complete without execution failure or skip; passing verdict | `PASS(reason: passed)` |
| Exact-input terminal JSON; parent and members complete without execution failure or skip; retained review findings | `FAIL(reason: findings)` |
| Missing binary, daemon/state, configured agent/auth, declared configuration, or authorized bridge | `UNAVAILABLE(reason: unavailable)` |
| Installed version lacks required commands/JSON, or named panel cannot run as declared | `UNAVAILABLE(reason: unsupported)` |
| Provider-native no-run before input evaluation | `UNAVAILABLE(reason: skipped)` |
| Parent/member execution failure, including mixed execution-failure panel | `UNKNOWN(reason: failed)` |
| Exact-input member skipped | `UNKNOWN(reason: member_skipped)` |
| Exact-input member incomplete or ambiguous | `UNKNOWN(reason: member_incomplete)` |
| No terminal exact-input evidence at deadline | `UNKNOWN(reason: timed_out)` |
| Any canonical provider/input/reviewer/panel/member identity mismatch, or a stale observed state revision | `UNKNOWN(reason: stale)` |
| Claim lost | `UNKNOWN(reason: claim_lost)` |
| Claim, launch identity, JSON evidence, registered state boundary, or state is indeterminate | `UNKNOWN(reason: state_unknown)` |

Store the result in the repository's ordinary implementation evidence. Bind it
to the candidate revision and include capability, mode, selected profile,
provider, outcome, reason, identity hash, config hash, job identity when known,
member states, request count, confirmation count, and cost coverage. This is not
a separate receipt database.

## Repair and spend boundary

A matching queued/running/completed job is reused before a claim. The selected
profile's request and repair-confirmation caps are absolute. POC authorizes one
request and no RoboRev confirmation; Pilot and Production authorize one request
and at most one changed-tip confirmation. A further non-pass, timeout,
ambiguity, or setup failure is carried into fresh validation. Do not invoke
`refine`, install hooks, review intermediate repair commits, or add a panel.

When `cost --json` is supported, record its approximate total with
`jobs_with_cost`, `jobs_total`, and `complete`. Incomplete coverage stays
visible and is not an exact-dollar ceiling. The enforceable controls are the
request cap, confirmation cap, selected reviewer/panel, model, reasoning, and
live-batch timeout. Minimum severity reduces finding and repair noise; it is not
an inference-cost ceiling.

## Authority boundary

RoboRev is observation, not authority. `PASS`, `FAIL`, `UNKNOWN`, and
`UNAVAILABLE` all flow to one fresh-context validation decision. Provider
evidence cannot push, create a Draft, post to GitHub, mark Ready, merge, accept a
known-red residual, advance or close a stage, or terminalize work. GitHub-native
feedback reconciliation and required checks keep their existing roles; the
Captain keeps delivery, scope, irreversibility, and accepted-red authority.
