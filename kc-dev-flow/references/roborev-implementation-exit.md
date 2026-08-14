# RoboRev Implementation Exit

Use this provider contract when the repository's Local Profile declares
`review_convergence` in `observe` mode with `provider: roborev` at
`implementation exit`. The observation gives fresh validation exact-tip defect
evidence. It does not replace validation and it does not make RoboRev a gate.

## Activation and repository ownership

The declaration names:

- the repository-local contract path and committed RoboRev configuration path;
- `agent`, `model`, `reasoning`, `minimum severity`, and either `panel: none` or
  one named panel;
- the exact implementation-exit boundary and `observe` mode;
- the live-batch timeout, explicit-request cap, and repair-confirmation cap;
- any authorized local-command bridge.

An omitted declaration performs no RoboRev detection, configuration read,
provider query, or invocation. A present declaration with an absent field is
`UNAVAILABLE(reason: unavailable)`; ambient global defaults do not fill it.
File presence alone does not activate this contract.

RoboRev reads repository configuration from its precedence chain, and exact
commit/range reviews may read the default branch's copy. Resolve the declared
values from the candidate Git object, record that object's configuration hash,
and pass the values explicitly to the candidate review command. This keeps a
new candidate configuration repository-owned before it reaches the default
branch. A default-branch configuration may be used after its bytes match the
recorded candidate hash. Force single-reviewer execution with `--panel none`;
Production does not select a panel by itself.

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
RoboRev version and JSON contract
configuration object SHA
agent, model, reasoning, minimum severity
panel name and declared member population
```

The claim identity is the SHA-256 of that canonical record. Provider evidence
matches when its repository, exact range or tip, configuration, and complete
panel membership match the record. Human-formatted output is diagnostic; it
cannot establish `PASS`.

## Existing-state single-flight transaction

First query queued, running, and completed jobs for reusable exact-input
evidence. If none matches, claim the identity in the current work item's
implementation evidence through the repository's existing Spacedock
execution-state transaction:

1. Re-read the authoritative remote state revision and the bound task. A
   shared parent that already records the same identity refuses the new claim
   and records `UNKNOWN(reason: claim_lost)`.
2. If absent, append one claim containing identity, claimant, state revision,
   and `state: claimed`; commit only the bound task path.
3. Push the state branch as a fast-forward compare-and-swap. Do not pull,
   rebase, or retry a rejected claim push. A non-fast-forward rejection is
   `UNKNOWN(reason: claim_lost)`; an indeterminate write is
   `UNKNOWN(reason: state_unknown)`.
4. After success or rejection, fetch and perform a post-push re-read of the
   authoritative task. The claimant proceeds only when the remote record names
   its identity and claimant. Any other state is a loss or indeterminate state.

The push rejection is the independent-clone enforcement point; the existing
claim check is the shared-parent enforcement point. A claim loser performs no
provider re-query, enqueue, or retry. Do not add another ledger, tracker,
daemon, or generalized lock service.

## Winner observation protocol

The claim winner re-queries provider jobs. It reuses a matching queued,
running, or completed parent job. If none exists, it snapshots current job IDs
and makes one explicit request with the exact base/tip and the declared
agent/model/reasoning/severity/panel flags.

The supported `review` command has no stable JSON launch receipt. Correlate the
request by comparing the post-request `list --json` population with the
snapshot. Accept the launch identity when one new parent job matches the full
exact-input record. Zero, multiple, stale, or ambiguous candidates produce
`UNKNOWN(reason: state_unknown)` and do not earn another request.

Wait within the declared live-batch timeout and re-read the selected job with
`show --job <id> --json`. Record job ID and UUID, exact input, status, verdict,
configuration, and the complete configured member population. At the deadline,
record `UNKNOWN(reason: timed_out)` without duplicate enqueue.

## Correlation precedence and closed mapping

Apply correlation before lifecycle and verdict interpretation. A repository,
range/tip, configuration, panel, or member-population mismatch is `stale`; when
that same evidence also has an incomplete member, `stale` wins over
`member_incomplete`. For an exact-input job, execution failure wins over skip or
findings, then member skip wins over incomplete state, and an incomplete or
ambiguous member wins over a completed parent verdict.

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
| Repository, range/tip, configuration, panel, or population mismatch | `UNKNOWN(reason: stale)` |
| Claim lost | `UNKNOWN(reason: claim_lost)` |
| Claim, launch identity, JSON evidence, or state is indeterminate | `UNKNOWN(reason: state_unknown)` |

Store the result in the ordinary implementation report's Work Control evidence
envelope. Bind it to the candidate revision and include capability, mode,
provider, outcome, reason, identity hash, config hash, job identity when known,
member states, request count, confirmation count, and cost coverage. This is not
a separate receipt database.

## Repair and spend boundary

A matching queued/running/completed job is reused before a claim. One identity
has one explicit-request allowance. After an ordinary implementation repair,
the repository may authorize one repair confirmation for the changed tip. A
second non-pass, timeout, ambiguity, or setup failure is carried into fresh
validation. Do not invoke `refine`, install hooks, review intermediate repair
commits, or silently fall back from a named panel to a single reviewer.

When `cost --json` is supported, record its approximate total with
`jobs_with_cost`, `jobs_total`, and `complete`. Incomplete coverage stays
visible and is not an exact-dollar ceiling. The enforceable controls are the
request cap, confirmation cap, selected reviewer/panel, model, reasoning, and
live-batch timeout.

## Authority boundary

RoboRev is observation, not authority. `PASS`, `FAIL`, `UNKNOWN`, and
`UNAVAILABLE` all flow to one fresh-context validation decision. Provider
evidence cannot push, create a Draft, post to GitHub, mark Ready, merge, accept a
known-red residual, advance or close a stage, or terminalize work. GitHub-native
feedback reconciliation and required checks keep their existing roles; the
Captain keeps delivery, scope, irreversibility, and accepted-red authority.
