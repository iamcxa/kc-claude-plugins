---
title: Route review-runtime CI by the contract a change can affect
status: done
product: kc-pr-flow
sprint:
source: Captain direction after PR 249 CI review, 2026-08-18
design: required
started: 2026-08-18T03:28:12Z
worktree:
id: ntrtwg834txp70x6sqv27fke
pr: pr-merge:253
completed: 2026-08-18T07:34:54Z
verdict: passed
archived: 2026-08-18T08:10:12Z
---

The `typed review runtime contract` job takes about eleven minutes and currently
runs for root documentation and marketplace metadata changes that cannot change
the runtime. The full job also combines several distinct proof surfaces, making
an unrelated change pay for runtime, shadow, benchmark, and posting tests.

Preserve every check that can falsify a shipped behavior, but route it only from
the files that can change that behavior. Documentation-only and metadata-only
changes need a fast correspondence contract, not a replay of unchanged runtime
behavior. This task changes CI routing only; it does not retire or alter the
typed runtime.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v2
  selected: production
  recommended: production
  basis: >-
    This changes the repository's long-lived CI assurance boundary. A false
    negative could ship a broken review runtime, while a false positive imposes
    recurring cost on every matching PR. No production data or external runtime
    mutation is involved, but the validation and rollback obligation is durable.
  route: [shape, build, verify, release]
  obligations:
    architecture:
      - Map each current workflow step to the shipped behavior or document claim it can falsify.
      - Separate runtime behavior, adapter correspondence, documentation, and release metadata triggers.
    implementation:
      - Keep full behavioral suites reachable for every source that can change their production path.
      - Do not retain a test merely because it existed or remove one merely because it is slow.
    testing:
      - Prove representative runtime changes still select the behavioral suite.
      - Prove root documentation and metadata-only changes select only fast relevant contracts.
      - Validate workflow syntax and action pins.
  scope_boundary: >-
    No typed-runtime retirement, runtime rewrite, assertion deletion without a
    named redundant proof, or kc-pr-review behavior change.
  promote_when: []
  decision:
    authority: Captain Kent
    at: 2026-08-18T03:28:12Z
```

## Acceptance criteria

**AC-1 — Every retained CI step has a named assurance target.** Verified by: a
checked mapping from workflow step to shipped contract and changed-file owners;
steps with no distinct failure mode are removed or moved to their owning gate.
Falsified by: a step remains because it is historical, counts assertions, or
duplicates unchanged evidence without naming what it alone catches.

**AC-2 — Runtime-affecting changes still run the complete behavioral contract.**
Verified by: deterministic path-routing fixtures for runtime, safe-I/O, shadow,
benchmark, posting, adapter, and workflow changes. Falsified by: any production
source can change without selecting its owning behavioral suite.

**AC-3 — Documentation and release metadata no longer pay for unchanged runtime.**
Verified by: routing fixtures show root/product/architecture/plugin metadata
changes select only their fast correspondence or version gates, while the full
runtime suite is absent. Falsified by: a representative docs-only change still
selects the full job.

**AC-4 — The new routing is observable and bounded.** Verified by: local workflow
validation plus one PR run showing the fast path and no missing required check;
the PR records before/after selected jobs and wall time. Falsified by: a skipped
path leaves a required check pending or the fast path still executes the full
behavioral suite.

## Validation and release closeout

**Decision: passed with one Captain-accepted historical delivery residual.**

- PR #251 delivered the capability-owned runtime, shadow, posting, and
  evaluation routes. PR #253 delivered the repository-write owner, repo-wide
  workflow lint, and symmetric cross-model route at exact head
  `53c08eab4a42e3cc31731a86bbfcad691d93a54f`.
- PR #253 selected only its relevant contracts: cross-model and repository-write
  each passed in 5 seconds, review CI routing passed in 19 seconds, and version
  parity passed in 20 seconds. Typed review runtime and e2e-pipeline suites were
  absent, proving the unrelated fast path rather than inferring it from green.
- Local routing, actionlint, cross-model `68/68`, and repository-write `53/53`
  checks passed. GitHub reports no external review, thread, or PR-comment
  population on PR #251 or #253.
- GitHub merged PR #253 as
  `d5a68b34c24881daf7e6e93e4724c396aa813212` at
  `2026-08-18T07:34:54Z`; all required checks passed.
- Historical residual: PR #251 and PR #253 were created outside the adopted
  `pr-merge` delivery unit and their bodies contain no approved `Candidate:`
  SHA. Kent explicitly accepted this audit-only residual on 2026-08-18 so this
  already-merged task can close. The bodies remain unchanged because a
  retroactive edit cannot recreate pre-merge approval. Future delivery receives
  no waiver and must use the repository's current `pr-merge` contract.
- Kent authorized release closeout after reviewing that residual. Repository
  maintainers own the path-scoped Actions signals; a regression can be isolated
  by reverting #253's routing expansion or #251's capability split without
  altering the typed review runtime itself.
