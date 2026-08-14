---
id: e9nrdgxgnp1rqwwbcxfzb1nj
title: "kc-dev-flow: adopt a proportional RoboRev implementation exit"
status: ideation
source: captain:conversation-2026-08-13
product: kc-dev-flow
sprint: S2
started: 2026-08-14T07:45:49Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design: required
lane: main
---

## Problem

The workflow needs an implementation-exit review that catches material defects before Draft PR creation without repeating the author’s own heavyweight PR review after the Draft exists. A repository-configured RoboRev review can provide exact-tip evidence, but adopting it indiscriminately would make POCs pay for production-grade panels and would turn tool absence into a workflow blocker. The task must define a proportional, optional RoboRev path with an honest fallback while preserving fresh behavioral validation, external GitHub feedback reconciliation, and Captain delivery authority.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v1
  selected: production
  recommended: production
  basis: "A retained marketplace-published workflow contract for external repository adopters; evidence is exact-revision delivery input, hosts may lack RoboRev or local-machine access, and the change carries compatibility, release, rollback, and ownership obligations without granting delivery authority."
  obligations:
    architecture:
      - "Use one repository-configured exact-tip implementation-exit observation before initial Draft creation, reusing already-completed matching evidence without adding a daemon, second ledger, generalized evaluator, or automatic merge."
      - "Keep RoboRev evidence separate from fresh behavioral validation, GitHub-native feedback reconciliation, and Captain push, Ready, merge, and terminalization authority."
      - "Treat local, Conductor Cloud, and explicit local-command bridge capability as independently detected facts; an environment label alone proves neither support nor absence."
    implementation:
      - "Emit an explicit non-green no-run or fallback result when RoboRev, its daemon, a compatible agent, authentication, or persistent local state is unavailable; fresh validation remains sufficient to continue."
      - "Keep model, reasoning, minimum severity, and optional panel selection repository-owned and proportional; Production does not make a multi-reviewer panel the default."
      - "Bound spend structurally with one explicit exact-tip observation, matching-evidence reuse, duplicate-enqueue avoidance, and a repair-attempt cap; observe approximate provider cost/coverage when available without creating a second ledger or precise-dollar claim."
    testing:
      - "Prove exact-tip PASS and findings/non-pass behavior plus unavailable, unsupported, skipped, failed, timed-out, and stale classifications against current provider behavior."
      - "Prove the honest no-RoboRev fallback, matching-evidence reuse, configured single-reviewer and panel paths, and supported installed-host/release behavior."
      - "Keep each live or tool validation batch within 20 minutes and preserve exact-revision release evidence."
  invariant_sources:
    - "docs/dev/_mods/kernel.md — authority, exact-revision delivery, outcome, and evidence discipline"
    - "docs/dev/README.md — implementation, fresh validation, GitHub feedback, and Captain delivery boundaries"
    - "docs/dev/_mods/work-control-profile.md — closed evidence outcomes and resource/review controls"
    - "/Applications/Conductor.app/Contents/Resources/conductor-skill/skills/conductor/SKILL.md — local and Cloud environment boundary"
  scope_boundary: "No review-every-commit hook, micro-repair auto-review, unbounded refine loop, daemon, second ledger, generalized evaluator, automatic GitHub mutation, auto-Ready, or auto-merge."
  promote_when:
    - "Re-enter ideation if the seam gains unattended recurring execution, external mutation, retained provider state, or a hosted-service obligation beyond this repository-configured observation."
  decision:
    authority: captain:kent
    at: 2026-08-14T08:08:11Z
```

## Proposed approach

### Accepted outcome and appetite

Protect one value: before a candidate implementation leaves implementation, the
workflow records what the repository-configured RoboRev reviewer observed at the
exact candidate tip, or records an honest non-green reason why no observation
exists. This is early defect evidence for fresh validation; it is not a second
validation gate and it never gains push, Draft, Ready, merge, or closeout
authority.

- **Appetite:** one independently deliverable S2 closeout slice, one
  implementation worker, and one fresh validation worker. Keep the product diff
  to the existing continuation seam, one conditional provider reference,
  repository-owned provider configuration, parity docs, and proportional
  contract fixtures. Re-enter ideation if implementation cannot stay within
  roughly 90 worker minutes excluding the separately bounded live checks.
- **Tolerance:** at most one explicit review request for one exact tip and at
  most one confirmation after an ordinary repair. Tool, daemon, agent,
  authentication, state, bridge, or protocol absence may not block entry to the
  existing fresh-validation path, but it may never be called `PASS`.
- **Keep if cut:** exact-revision binding, the closed four-state receipt,
  no-tool continuation, matching-evidence reuse, and the existing authority
  separation.
- **Non-goals:** review-every-commit hooks, automatic micro-repair review,
  `roborev refine`, a managed daemon, a second receipt or cost ledger, a generic
  review evaluator, a mandatory panel, automated GitHub mutation, auto-Ready,
  auto-merge, or replacing fresh validation.
- **Assumption most likely to be wrong:** an agent can uniquely correlate one
  explicit `roborev review` request with provider-native JSON even though the
  current and documented `review` command has no stable JSON launch receipt.
- **Pre-mortem:** the workflow ships and says it reviewed the right code, but a
  concurrent job or ambient global configuration caused it to read a different
  review or spend twice. The prevention is an atomic claim in existing Spacedock
  execution state, winner-only re-query/enqueue, exact repo/ref/config matching,
  and `UNKNOWN` whenever claim or job identity is not unique.

### Fastest path and smallest cut

Reuse the adopted Work Control Profile's `review_convergence` capability in
`observe` mode at one named boundary, `implementation exit`. The repository's
Local Profile declares the provider binding and Captain authority. Omission is
valid and performs no RoboRev detection, configuration read, or invocation.

When declared, `continue-dev-flow` conditionally loads one provider-specific
reference, `references/roborev-implementation-exit.md`. That reference defines
the bounded observation protocol and receipt mapping. It does not add a daemon,
workflow state store, or evaluator. The ordinary stage report carries the
existing Work Control evidence envelope.

The adopting repository owns all review choices. Its committed RoboRev config
or committed Local Profile binding must name the agent, model, reasoning,
minimum severity, and either one reviewer (`panel: none`) or an explicit named
panel. Ambient global defaults do not satisfy that ownership claim. Production
permits but does not imply a panel; the lowest-cost declared single reviewer is
conformant. This repository dogfoods a committed single-reviewer configuration;
a named-panel fixture and an already-observed `branch_final` run prove the opt-in
path without making it the default.

The observation runs after scoped and full relevant tests, the exact candidate
revision, and the changed-file-to-AC map exist, and before fresh validation. A
changed code tip invalidates the receipt. Fresh behavioral validation then
adjudicates the evidence independently. GitHub-native feedback is still loaded
at validation entry when a PR exists, and the Captain retains push, initial
Draft, Ready, merge, and terminalization decisions.

### Exact-tip observation protocol

1. **Activation and ownership.** Read only the Local Profile declaration. If
   `review_convergence` is omitted, stop with no provider work. If declared,
   resolve the exact repository identity, base and tip SHAs, provider version,
   and the origin of every agent/model/reasoning/severity/panel choice. An
   unowned choice is `UNAVAILABLE`, not an invitation to use an ambient default.
2. **Capability detection.** Probe the actual host for compatible `roborev`
   commands, daemon/state access, the configured agent and authentication, and
   `list --json` plus `show --json`. `CONDUCTOR_IS_LOCAL` only identifies the
   Conductor environment. Cloud support is established by the same probes. An
   explicit local-command bridge is usable only when the binding authorizes it
   and the bridge proves the Mac checkout is the same exact tip; otherwise the
   result is non-green.
3. **Reuse probe.** Query queued, running, and completed provider jobs. Reuse or
   wait for a provider-native job only when its repository, exact range/tip,
   agent, model, reasoning, minimum severity, panel name and complete membership,
   and configuration revision all match. Stale or ambiguous jobs do not match.
4. **Atomic single-flight claim.** If the first probe finds no match, claim the
   identity `{repository, base, tip, configuration}` through the current work
   item's existing Spacedock execution-state transaction. The mutation and
   fast-forward state push are the compare-and-swap enforcement point; this is a
   receipt in the authoritative work item, not a provider ledger or second
   tracker. Exactly one winner may continue. Claim loss, a non-fast-forward race,
   ambiguous ownership, or indeterminate state produces `UNKNOWN` without
   enqueue, rebase-and-enqueue, or automatic retry.
5. **Winner re-query and one explicit request.** Only the claim winner re-queries
   provider jobs after claiming, closing the gap between the first probe and
   enqueue. It reuses a newly matching job if present. Otherwise it snapshots the
   job IDs and enqueues exactly one explicit exact-ref review. Because `review`
   exposes no stable JSON launch receipt, accept a job only when exactly one new
   parent job matches all bound inputs. Zero or multiple candidates are
   `UNKNOWN`; do not enqueue again in the same attempt.
6. **Terminal evidence.** Wait no longer than the repository's declared live
   batch limit, then re-read the selected job through `show --job <id> --json`.
   Record the job ID/UUID, exact range/tip, status, verdict, configuration, and
   panel/member terminal states when applicable. Every configured member must
   complete without execution failure or skip before either `PASS` or a
   review-findings `FAIL` is possible. Human-formatted CLI prose alone cannot
   establish `PASS`.
7. **Bounded repair.** A material finding returns to the ordinary implementation
   worker. If the resource envelope permits it, one changed exact tip may receive
   one confirmation using the same protocol. A second non-pass, timeout,
   ambiguity, or setup failure is carried into fresh validation. Never invoke
   `refine`, install a post-commit hook, or auto-review intermediate repairs.
8. **Cost observation.** When supported, record `cost --json` totals together
   with `jobs_with_cost`, `jobs_total`, and `complete`. The numbers are
   approximate observation only. Invocation count, confirmation cap, panel
   membership, model, and reasoning are the enforceable spend controls.

### Closed outcome mapping

| Provider observation | Work Control outcome | Required evidence and continuation |
|---|---|---|
| Terminal exact-input review completes without parent/member execution failure or skip and its verdict passes | `PASS` | Matching `show --json` job, configuration, and complete member population; continue to fresh validation. |
| Terminal exact-input review completes without parent/member execution failure or skip and reports retained review findings | `FAIL` | Matching job, findings verdict, stable finding identities, and complete member population; repair once if authorized or carry to fresh validation. |
| Binary, daemon/state, configured agent/authentication, authorized bridge, or declared repository configuration is absent | `UNAVAILABLE` (`reason: unavailable`) | Probe/config evidence; run no review and continue to fresh validation. |
| Installed version lacks the required command or JSON contract, or a named panel cannot run without the daemon | `UNAVAILABLE` (`reason: unsupported`) | Version/help evidence; never silently downgrade a named panel to local single-reviewer mode. |
| Provider gives an explicit supported no-run/eligibility result before evaluating the input | `UNAVAILABLE` (`reason: skipped`) | Provider-native skip/no-run evidence; continue to fresh validation without retry. |
| Invocation, parent, or any configured member has an execution failure; any member is skipped/incomplete; or a mixed panel contains an execution failure | `UNKNOWN` (`reason: failed`, `member_skipped`, or `member_incomplete`) | Matching job and complete observed member population. Execution failure is neither clean feedback nor review-findings `FAIL`; a completed reviewer findings verdict remains distinct. |
| No terminal exact-input result exists at the live-batch deadline | `UNKNOWN` (`reason: timed_out`) | Job/timeout evidence; do not enqueue a duplicate. |
| A result binds another tip, range, repository, configuration, or incomplete/ambiguous panel | `UNKNOWN` (`reason: stale`) | Mismatch evidence; never reuse it or relabel it `PASS`. |
| The Spacedock single-flight claim is lost, ambiguous, or indeterminate | `UNKNOWN` (`reason: claim_lost` or `state_unknown`) | Authoritative execution-state evidence; the loser performs no provider re-query, enqueue, rebase-and-enqueue, or automatic retry. |

`observe` means these non-passes do not themselves close the implementation
boundary. They remain explicit validation input. A validator may decide the
product is otherwise acceptable, but it cannot rewrite the RoboRev receipt.

### Primary and local proof

- Current source is `origin/main` at
  `6f0e274e6e02ff7e0e5b158859783df037c45c4d`. Its implementation/validation
  split and authority boundary are at `docs/dev/README.md:244-302`; its Work
  Control declaration and closed envelope are at
  `docs/dev/_mods/work-control-profile.md:14-67`.
- The official [RoboRev command reference](https://www.roborev.io/commands/)
  exposes exact-ref review controls, `list/show/cost --json`, and approximate
  cost coverage, but no `review --json` contract. The official
  [post-commit documentation](https://www.roborev.io/automation/post-commit-reviews/)
  says explicit reviews start fresh jobs, so reuse must precede enqueue. The
  [configuration reference](https://www.roborev.io/configuration/) makes CLI
  and repository config higher priority than global defaults. The
  [panel reference](https://www.roborev.io/advanced/subagent-review-panels/)
  shows that panels multiply jobs and require the daemon.
- Local RoboRev `v0.62.0` is healthy with four workers. Its `review` command
  accepts exact refs, agent/model/reasoning/minimum severity, `--panel none`,
  and local execution; `list` and `show` expose JSON, while `review` and `run`
  do not expose JSON launch receipts in this version.
- Local provider-native evidence includes a completed two-member `branch_final`
  findings verdict at job `164` (one reviewer pass and one reviewer findings
  fail) and a passing two-member synthesis at job `169`. Job `167` records the
  exact tip and repository-owned
  Codex model/reasoning/severity/member configuration. This proves the panel and
  member-failure distinctions; it does not prove a shipped Spacedock runtime
  integration.
- Local seven-day cost output is approximately `$12.389502` across 22 jobs with
  cost on only 4 (`complete: false`). That proves why a precise dollar ceiling
  would be false confidence.
- Spacedock `v0.27.0-pre4` supplies repository configuration and a commander
  directive for `roborev review --branch --panel branch_final`. The inspected
  Praia checkout has no shipped RoboRev integration on its current tracked
  runtime surfaces, so this is adoption evidence, not a runtime adapter to copy.
- The Conductor environment contract states that Cloud is a Linux sandbox with
  one checkout and no Mac access unless an explicit local-command bridge exists.
  Therefore `CONDUCTOR_IS_LOCAL=0` is neither a support nor an absence receipt.

### Reverse-recovery audit at exact `origin/main`

| Surface | Completeness | Need | Evidence and disproof hook |
|---|---|---|---|
| Implementation exit followed by separate fresh validation | `WORKING_UNIT_UNPROVEN` | `REQUIRED` | `docs/dev/README.md:244-302` and `kc-dev-flow/skills/continue-dev-flow/SKILL.md:50-60` define the seam and authority, but no current exact-tip runtime walk proves RoboRev there. **Disproof:** an installed-host walk that cannot reach fresh validation after implementation. |
| Work Control four-state receipt and `review_convergence` abstraction | `STUB` for this provider | `REQUIRED` | `docs/dev/_mods/work-control-profile.md:14-67,147-175` defines the reusable contract but has no RoboRev binding. **Disproof:** a repository adapter already emitting a matching RoboRev envelope. |
| Repository-bound RoboRev implementation-exit observation | `MISSING` | `REQUIRED` | Exact-source searches for both provider nouns (`RoboRev`, `roborev`) and indirect seams (`review_convergence`, `Observation`, implementation review) covered package skills/references, adopted docs/mods, scripts, configuration, and the read-only Praia checkout. They found the generic control and external adoption evidence, but no kc-dev-flow provider binding or runtime adapter. External dynamic consumers are unknown and do not supply this repository seam. **Disproof:** an exact-main tracked path or installed-runtime trace showing the same binding and receipt. |
| Fresh validation, GitHub feedback reconciliation, and Captain delivery authority | `WORKING_UNIT_UNPROVEN` | `REQUIRED` | `docs/dev/README.md:278-302` and kernel authority rules retain the downstream boundaries; their current behavior is not reimplemented here. **Disproof:** validation evidence showing the new sensor can advance, post, Ready, merge, or close work. |
| RoboRev provider exact-job and panel evidence | `WORKING` | `REQUIRED` | Live `status`, `list --json`, and `show --json` walks on jobs `164`, `167`, and `169`. **Disproof:** the declared installed-version matrix cannot reproduce exact input/config/member fields. |

Search boundaries were the exact `origin/main` tree, the package/adopted workflow
surfaces, repository scripts/config, current local RoboRev CLI/daemon state, and
the specified read-only Spacedock checkout. Hosted/dynamic external adopters were
not enumerable and remain `UNKNOWN`; that limits absence claims to this product
tree.

### Subtractive result and necessity records

| Candidate surface | Result | Necessity or return instrument |
|---|---|---|
| Reuse `review_convergence` in `observe` | Keep | **Criterion:** AC1-AC4. **Alternative:** a new review capability duplicates the closed envelope and authority model. **Escape:** local job `164` proves completed reviewer findings can coexist with a passing reviewer, while the required mixed execution-failure mutant must remain `UNKNOWN`, not clean or review-findings `FAIL`. Mutation: collapse those two classes and AC2 fails. |
| One conditional RoboRev provider reference | Keep | **Criterion:** AC1-AC3. **Alternative:** inline provider mechanics in `continue-dev-flow` makes every adopter load RoboRev details and obscures the no-provider path. **Escape:** current `review` lacks JSON launch identity and local named-panel execution can silently become one reviewer. Mutation: accept prose or silent downgrade and AC2/AC3 fails. |
| Repository-native `.roborev.toml` for this repository's dogfood selection | Keep | **Criterion:** AC3. **Alternative:** ambient global defaults are not repository-owned; duplicating provider settings in a second registry creates drift. **Escape:** origin-aware config mutation to global/default makes AC3 fail. |
| New daemon, hook, generalized evaluator, receipt database, or cost ledger | Return | Remove each from the proposed tree. AC1-AC4 remain testable through explicit CLI observation, the existing stage report envelope, and provider JSON/cost coverage. Any future claim that one is necessary must provide its own failed without-it instrument and Captain scope decision. |
| Mandatory panel or Production-to-panel inference | Return | Set the dogfood default to one reviewer and `panel: none`. Named-panel fixtures still prove opt-in behavior; all value ACs remain satisfiable. |
| Repeated review/refine loop | Return | Cap the ordinary repair confirmation at one. Fresh validation owns residual adjudication; no value AC requires convergence by repeated provider spend. |

### Slice and implementation shape

One slice is independently deliverable: an adopter either omits the control and
keeps today's route, or declares it and receives one exact-tip receipt/non-pass
before fresh validation. It has observable behavior and no separately blockable
sibling. One worker owns the conditional loading rule, provider reference,
repository dogfood config, parity docs, contract fixtures, and Roadmap wording.
The first demo runs the same candidate tip once with the declared single reviewer
and then reruns continuation against the matching completed job to show reuse
with zero additional enqueue. A deterministic two-continuation demo proves one
atomic Spacedock claim winner and zero loser enqueues for the same identity.

## Design determination

`required` — this changes a portable workflow boundary and introduces external
provider evidence with host, identity, configuration, cost, and authority failure
modes. The concrete decision is one optional, repository-declared
`review_convergence` observation at implementation exit, using a conditional
RoboRev reference and the existing four-state envelope. It remains `observe`
until a future separately authorized promotion proves fail-closed behavior for
every non-pass; this item does not perform that promotion.

## Acceptance criteria

**AC1: Declared exact-tip observation or honest no-tool continuation**

At implementation exit, a repository that declares the RoboRev control records
one four-state receipt for the exact base/tip and then reaches the existing fresh
validation route; an omitted control performs zero RoboRev work, and an
unavailable/unsupported/skipped host records a non-green reason without blocking
fresh validation. **Verified by:** deterministic activation fixtures plus one
installed-host candidate walk; assert exact SHA fields, provider evidence, zero
calls when omitted, and validation reachability for every no-run case.
**Falsifier:** any omitted declaration invokes RoboRev, any no-run receipt says
`PASS`, or missing RoboRev prevents ordinary fresh validation.

**AC2: Provider evidence cannot pass on findings, failure, timeout, ambiguity, or staleness**

Only one terminal `show --json` result matching repository, exact range/tip,
agent/model/reasoning/severity/panel configuration, and complete member state can
produce `PASS`; only a completed review-findings verdict with no parent/member
execution failure or skip maps to `FAIL`. Any parent/member execution failure,
skipped or incomplete member, mixed panel containing an execution failure,
timeout, ambiguity, or staleness maps to `UNKNOWN`. **Verified by:**
fixture/mutation cases for all eight required classes plus member-failed,
member-skipped, member-incomplete, and mixed-panel variants; live job `169` must
map `PASS`, completed mixed-reviewer findings job `164` must map `FAIL`, and the
mixed execution-failure fixture must map `UNKNOWN(reason: failed)`. Mutate exact
tip, config, member terminal state, job count, and deadline independently.
**Falsifier:** any mutation still yields `PASS`, an execution failure maps to
review-findings `FAIL`, a member failure/skip/incompleteness is synthesized
clean, or human prose alone closes the receipt.

**AC3: Review spend is repository-owned and structurally bounded**

The workflow reuses a matching queued/running/completed job before enqueue,
then atomically claims `{repository, base, tip, configuration}` through existing
Spacedock execution state. Only the claim winner may re-query and enqueue;
claim loss or indeterminate state returns `UNKNOWN` with no enqueue/retry. The
workflow enqueues at most once for one identity, permits at most one post-repair
confirmation, defaults this repository to one declared reviewer with `panel:
none`, and runs a named panel only when committed repository configuration opts
in. It reports provider cost coverage as approximate and incomplete when so
marked.
**Verified by:** a fake provider call log and origin-aware config fixtures for
single, named-panel, global-default, reuse, repair, and cost-coverage cases, plus
a two-concurrent-continuation test in which both first probes miss, exactly one
atomic claim wins, and the loser performs zero provider re-query/enqueue.
**Falsifier:** two claim winners or any loser enqueue for the same identity,
duplicate enqueue for a matching tip, a third review round,
Production alone selects a panel, ambient global settings pass ownership, a
named panel silently becomes local single review, or incomplete cost is reported
as a precise ceiling.

**AC4: RoboRev remains evidence, not validation or delivery authority**

Every RoboRev receipt, including `PASS`, flows into exactly one fresh-context
validation decision; existing GitHub-native feedback reconciliation still runs
for the exact PR head, and only the Captain can authorize push/initial Draft,
Ready, merge, known-red acceptance, or terminalization. **Verified by:** contract
mutants that attempt to skip fresh validation after RoboRev PASS, treat RoboRev
FAIL as a stage gate, bypass GitHub observation, post provider output, or grant a
delivery transition, followed by the normal exact-head delivery smoke.
**Falsifier:** any provider verdict advances/blocks the stage by itself, replaces
fresh validation/GitHub feedback, mutates GitHub, or gains Captain authority.

**AC5: Published and installed behavior preserves the proportional contract**

The package, adopted docs, and release artifact agree on conditional loading,
closed outcome mapping, exact-tip reuse, repair cap, configuration ownership,
and authority; the S2 Roadmap closes only with exact-revision validation and
delivery evidence for this item and its existing S2 dependencies. **Verified
by:** package/adopted parity checks, candidate and published-tag smoke on
supported installed hosts, exact-head CI, and Roadmap text comparison.
**Falsifier:** the installed skill omits the provider reference, loads it for an
undeclared adopter, changes an outcome/authority rule, or Roadmap claims S2 exit
without this item's exact-revision evidence.

## Test plan

All live/tool batches fail at their declared timeout and remain at or below 20
minutes; a timeout records `UNKNOWN` and never triggers an automatic retry.

| Batch | Maximum | Evidence |
|---|---:|---|
| Static contract and parity mutants | 10 min | Conditional locator, omitted declaration, package/adopted wording, four-state mapping, authority, no hook/refine/ledger, and Roadmap closeout. |
| Fake-provider deterministic matrix | 15 min | PASS, completed review findings, unavailable, unsupported, top-level skipped, parent/member failed, member skipped/incomplete, mixed-panel failure, timed out, stale, reuse, ambiguity, single/panel, repair cap, and incomplete cost coverage. |
| Two-concurrent-continuation single-flight | 10 min | Both initial probes miss; the existing Spacedock execution-state transaction yields exactly one claim winner, while claim loss/indeterminate state yields `UNKNOWN` and zero loser re-query/enqueue/retry. |
| Current local capability probe | 5 min | Version/help, daemon/state, configured agent/auth check, JSON command support, and config origin; no review enqueue. |
| Exact-tip single-reviewer/reuse demo | 20 min | One explicit review at the candidate tip, provider-native terminal receipt, then a second continuation observation with zero new job IDs. |
| Named-panel compatibility | 20 min | Run only when committed repository config opts in and the resource envelope permits; otherwise use the proven provider fixture plus `UNAVAILABLE`, never silent single-reviewer fallback. |
| No-tool/Cloud/bridge simulations | 10 min each | CLI absent, daemon absent, agent/auth absent, no state, unsupported version, Cloud without bridge, bridge with mismatched SHA, and authorized matching bridge. |
| Full repository and candidate-package suite | 20 min per command | Full relevant tests, contract test, candidate smoke for Claude/Codex, and exact candidate revision receipt. |
| Published-tag installed-host smoke | 20 min per host | Supported local/Cloud host paths, exact tag/tree receipt, release-please and exact-head CI evidence. |

E2E applies because this is a host/tool integration even though no UI changes.
The exact-tip single-reviewer/reuse demo is the walking runtime evidence; fixtures
cover destructive or unavailable branches without spending or mutating external
state.

## Measurement

- **Primary value measure:** the validation packet for one candidate exact tip
  contains either one provider-native RoboRev observation that catches a seeded
  medium-or-higher defect (or truthfully passes the clean mutation) or one honest
  non-green no-run receipt, and fresh validation remains reachable in both cases.
- **Correctness counters:** 8/8 required outcome classes classified; 0 stale,
  ambiguous, failed/skipped/incomplete-member, mixed-execution-failure, or
  prose-only cases accepted as `PASS`; 0 execution failures classified as
  review-findings `FAIL`; 100% receipts bind repository and exact tip.
- **Spend counters:** explicit enqueue count `<= 1` per tip, repair confirmation
  `<= 1`, atomic claim winners `<= 1` per repository/base/tip/config identity,
  claim-loser re-query/enqueue/retry `= 0`, omitted-control calls `= 0`,
  undeclared panel members `= 0`, and reuse demo additional enqueue `= 0`.
- **Cost observation:** report the provider total and coverage fields together.
  `complete: false` or missing usage stays visible and makes no exact-dollar
  claim.
- **Authority counter:** zero provider-triggered GitHub or workflow transitions;
  one fresh EM at ideation and one later at validation remain distinct from the
  RoboRev receipt.

## Doc diff

- `PRODUCT.md`: say kc-dev-flow can carry an optional repository-owned
  implementation-exit review observation without making a provider a gate.
- `ARCHITECTURE.md`: add the conditional implementation-exit sensor between
  implementation evidence and fresh validation, with the four-state/no-tool and
  authority boundaries.
- `kc-dev-flow/README.md`: document the optional RoboRev provider binding,
  proportional configuration, and conditional distribution behavior.
- `kc-dev-flow/skills/continue-dev-flow/SKILL.md`: replace the absolute “no
  reviewer loop” wording with “no unbounded/adjudicating loop” and conditionally
  load the provider reference only when the Local Profile declares it.
- `kc-dev-flow/references/roborev-implementation-exit.md`: add the narrow
  provider protocol, capability matrix, existing-state atomic single-flight
  claim, exact-job correlation, outcome mapping, bounded repair, approximate
  cost observation, and authority limits.
- `docs/dev/README.md`: adopt the behavior locally, declare the
  `review_convergence` observation at implementation exit, and retain the
  existing validation/GitHub/Captain contract.
- `.roborev.toml`: commit this repository's lowest-cost valid single-reviewer
  model/reasoning/severity choice with no automatic hook and no default panel.
- `scripts/kc-dev-flow-contract-test.py` and focused fixtures: prove conditional
  loading, exact mappings, configuration origin, two-concurrent-continuation
  single-flight, structural caps, package/adopted parity, and reject authority
  mutations without creating a generic evaluator.
- `docs/dev/ROADMAP.md`: add `roborev-implementation-exit` after
  `proportional-work-profile` and replace the S2 exit with:

  > Exit: external PR feedback is reconciled before completion; every proposed
  > control names the criterion and failed simpler route that earn it; normal
  > ideation records one Captain-selected POC, Pilot, or Production receipt
  > before acceptance criteria expand; and a declared RoboRev implementation
  > exit records one exact-revision observation or an honest non-green fallback
  > without becoming validation or delivery authority. All four items have
  > exact-revision validation and delivery evidence, and the product diff retains
  > no generalized evaluation platform. Hold the S2 Release PR until all four
  > items exit.

## Out of scope

- Installing, starting, updating, or supervising RoboRev or any coding agent.
- Post-commit hooks, review-every-commit, automatic review on intermediate
  repairs, and unbounded `refine`/fix loops.
- Making RoboRev required, blocking implementation exit on its absence, or
  accepting a non-pass as clean.
- A default panel by work profile, automatic fallback between reviewers, or
  workflow-owned model/provider policy.
- A new daemon, generalized evaluator, job mirror, finding tracker, receipt
  store, cost ledger, generalized lock service, exact-dollar budget, or
  cross-repository scheduler.
- Replacing fresh validation, the GitHub-native feedback contract, required
  checks, release evidence, or Captain delivery authority.
- Posting review output or mutating a PR from this sensor.
- Supporting an undeclared provider version/schema or an unproven local-command
  bridge; those attempts remain explicitly non-green.

## Stage Report: ideation

### Checklist

- `DONE` — Ran the work-profile chooser, recorded the Captain's Production
  decision at `2026-08-14T08:08:11Z`, committed and synced it at
  `eb6f664f88097bc52a540c1d3f10cc46537175d9`, and re-read the unchanged receipt
  before expanding this design.
- `DONE` — Designed one conditional implementation-exit seam that reuses
  `review_convergence`, preserves fresh validation/GitHub/Captain authority, and
  gives every no-RoboRev route an honest non-green outcome.
- `DONE` — Proved the riskiest provider/version/panel/cost assumptions against
  current official docs, local `v0.62.0` jobs, exact `origin/main`, and the
  specified read-only Spacedock evidence; defined falsifiable ACs, one smallest
  slice, S2 closeout wording, and live batches capped at 20 minutes.

### Summary

The accepted Production design adds one optional repository-owned RoboRev
observation at implementation exit. It reuses matching exact-tip evidence,
enqueues at most once, allows one bounded repair confirmation, records all
failure/no-run classes without blocking fresh validation, and leaves provider,
GitHub, validation, and Captain authority separate.

### Engineering judgment

```yaml
science_officer_em_upward_report:
  em_judgment: "The proposal is the smallest credible production seam and preserves authority correctly, but it is not gate-ready: its mixed-panel failure mapping is inconsistent, and reuse-before-enqueue detects rather than prevents concurrent duplicate enqueue."
  evidence_synthesis: >-
    Bound to origin/main at 6f0e274e6e02ff7e0e5b158859783df037c45c4d and the current roborev-implementation-exit state proposal. Reusing review_convergence in observe mode, one conditional provider reference, repository-owned configuration, honest no-tool outcomes, and retained fresh validation/GitHub/Captain authority form one independently deliverable surface. Local RoboRev v0.62 evidence establishes the missing launch receipt, JSON list/show evidence, fresh explicit jobs, mixed-member panel failure at job 164, passing job 169, silent local panel reduction risk, and incomplete cost coverage. Exact-input matching plus UNKNOWN on zero, multiple, stale, or ambiguous candidates makes observation correlation falsifiable, but does not prove launch causality. The closed mapping conflicts over a mixed panel whose parent fails with one passing and one failed member. The protocol also has no atomic single-flight control, so two continuations can both observe no match and enqueue before either detects the resulting ambiguity.
  risk_tradeoff_call: >-
    The design buys early exact-tip defect evidence with low durable surface cost and preserves an honest fallback. Shipping it as written risks spending twice under concurrency and assigning inconsistent receipts to incomplete panel evidence; post-enqueue ambiguity does not undo that spend. The minimum alternative is not another daemon or ledger, but one atomic claim through existing execution-state authority plus one unambiguous failure rule.
  recommendation: >-
    Return for one bounded contract repair, then repeat the ideation gate: reserve FAIL for completed review findings; classify any parent or member execution failure, including mixed pass/fail job 164, as UNKNOWN with reason failed. Before enqueue, atomically claim the repository/base/tip/config observation through existing execution-state authority; only the winner may re-query and enqueue, while claim loss or indeterminate state produces UNKNOWN without enqueue or retry. Add a two-concurrent-continuation test and align AC2, AC3, measurement, and the mapping table. Make no other scope change.
  route: return
  confidence: high
  multi_model: not_needed
  fo_boundary: "FO may verify evidence presence, state mechanics, and delivery mechanics; it may not adjudicate these findings or advance the gate without the corrected fresh EM record."
  engineering_judgment:
    question: "Is the current proportional RoboRev implementation-exit proposal the smallest production-grade seam, with honest outcome mapping and job correlation and sufficient acceptance, test, measurement, and Roadmap closeout?"
    revision: "origin/main@6f0e274e6e02ff7e0e5b158859783df037c45c4d; docs/dev/.spacedock-state/roborev-implementation-exit.md as currently written"
    evidence_synthesis: >-
      Bound to origin/main at 6f0e274e6e02ff7e0e5b158859783df037c45c4d and the current roborev-implementation-exit state proposal. Reusing review_convergence in observe mode, one conditional provider reference, repository-owned configuration, honest no-tool outcomes, and retained fresh validation/GitHub/Captain authority form one independently deliverable surface. Local RoboRev v0.62 evidence establishes the missing launch receipt, JSON list/show evidence, fresh explicit jobs, mixed-member panel failure at job 164, passing job 169, silent local panel reduction risk, and incomplete cost coverage. Exact-input matching plus UNKNOWN on zero, multiple, stale, incomplete, or ambiguous candidates makes observation correlation falsifiable, but does not prove launch causality. The closed mapping conflicts over a mixed panel whose parent fails with one passing and one failed member. The protocol also has no atomic single-flight control, so two continuations can both observe no match and enqueue before either detects the resulting ambiguity.
    adjudications:
      - finding: "F1-smallest-production-seam"
        disposition: supported
        basis: "Kernel Outcome and Route discipline favor the fewest lifecycle responsibilities; the proposal reuses review_convergence, adds one conditional provider binding, rejects daemon/ledger/evaluator surfaces, and retains one independently deliverable value surface."
      - finding: "F2-exact-job-correlation-is-honest-and-falsifiable"
        disposition: supported
        basis: "The protocol binds repository, base/tip, configuration, membership, and terminal JSON, and returns UNKNOWN for zero, multiple, stale, incomplete, or ambiguous candidates. This is honest observation correlation despite the documented absence of a JSON launch receipt."
      - finding: "F3-mixed-panel-failure-mapping-is-consistent"
        disposition: unsupported
        basis: "AC2 broadly maps failed evidence to UNKNOWN and job 164 demonstrates one passing plus one failed member, while the mapping table permits a terminal verdict that fails to become FAIL and reserves UNKNOWN explicitly for all-member failure or execution error. The same provider state can therefore receive two outcomes."
      - finding: "F4-no-duplicate-enqueue-is-enforced"
        disposition: unsupported
        basis: "Kernel absolute-claim discipline requires an enforcement point. Reuse-before-enqueue followed by a job-set comparison only detects a race after two callers have already enqueued; the fake-provider ambiguity case cannot prevent the duplicate spend required by AC3's falsifier."
      - finding: "F5-acceptance-test-measurement-and-roadmap-closeout"
        disposition: supported
        basis: "AC1-AC5 name falsifiers, the test plan covers installed-host behavior and bounded failure branches, measurement keeps incomplete cost coverage visible, and Roadmap closeout requires exact-revision validation and delivery for all S2 dependencies. Their structure is sufficient once F3 and F4 are corrected consistently."
    risk_tradeoff: >-
      The design buys early exact-tip defect evidence with low durable surface cost and preserves an honest fallback. Shipping it as written risks spending twice under concurrency and assigning inconsistent receipts to incomplete panel evidence; post-enqueue ambiguity does not undo that spend. The minimum alternative is not another daemon or ledger, but one atomic claim through existing execution-state authority plus one unambiguous failure rule.
    recommendation: >-
      Return for one bounded contract repair, then repeat the ideation gate: reserve FAIL for completed review findings; classify any parent or member execution failure, including mixed pass/fail job 164, as UNKNOWN with reason failed. Before enqueue, atomically claim the repository/base/tip/config observation through existing execution-state authority; only the winner may re-query and enqueue, while claim loss or indeterminate state produces UNKNOWN without enqueue or retry. Add a two-concurrent-continuation test and align AC2, AC3, measurement, and the mapping table. Make no other scope change.
    route: return
    confidence: high
    dissent: ""
    disproof_condition: "Change to proceed if the revised proposal provides one unambiguous UNKNOWN rule for every incomplete or failed panel member and a tested atomic single-flight enforcement point that prevents two concurrent continuations from enqueueing the same repository/base/tip/config observation without adding a second ledger."
    authority_boundary: "Captain retains scope, Roadmap, irreversibility, red-residual, push, Draft, Ready, merge, and terminalization authority; Gate Authority owns advancement; Spacedock remains work-item and execution-state authority; fresh validation and GitHub observation retain their existing decisions; RoboRev remains a sensor with no posting or transition authority."
```

### Ideation repair report: REPAIRED_FOR_CLAUDE_OPUS_EM

- **Reviewed state revision:**
  `8c2e2b193516f21358c3c7b2680f8a8d09c71dbf`, preserving its OpenAI
  `gpt-5.6-sol` `route: return` report as historical evidence.
- **Panel correction:** only completed review findings with no parent/member
  execution failure, skip, or incompleteness can be `FAIL`; any such execution
  defect, including a mixed execution-failure panel, is unambiguously `UNKNOWN`
  with a typed reason. Completed mixed-reviewer findings job `164` remains the
  distinct `FAIL` example. The mapping, AC2, tests, measurements, and examples
  now agree.
- **Single-flight correction:** the existing Spacedock execution-state
  transaction atomically claims repository/base/tip/config before enqueue. Only
  the winner may re-query/enqueue; claim loss, ambiguity, or indeterminate state
  is `UNKNOWN` with no enqueue, rebase-and-enqueue, or automatic retry. AC3 now
  includes a two-concurrent-continuation falsifier and matching counters.
- **Unchanged boundaries:** Production profile, optional no-tool/Cloud path,
  one-review-per-tip and one-confirmation caps, provider cost caveat, no new
  daemon/ledger/lock service, and fresh validation/GitHub/Captain authority.
- **Status:** `REPAIRED_FOR_CLAUDE_OPUS_EM`. This records a bounded correction,
  not a gate pass; the First Officer owns the Captain-selected fresh Claude Opus
  5 High review.
