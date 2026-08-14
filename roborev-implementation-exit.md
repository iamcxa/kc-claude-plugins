---
id: e9nrdgxgnp1rqwwbcxfzb1nj
title: "kc-dev-flow: adopt a proportional RoboRev implementation exit"
status: implementation
source: captain:conversation-2026-08-13
product: kc-dev-flow
sprint: S2
started: 2026-08-14T07:45:49Z
completed:
verdict:
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/roborev-implementation-exit-repair-recut
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

## Implementation repair cycle 1

### Summary

Repaired only the two validation-supported RoboRev findings. The recut
candidate now requires the Local Profile's registered holder, clean-holder
prerequisite, and `spacedock state commit` durability path before a claim can
win, and exact-input classification binds every declared provider, reviewer,
panel, and stable member-population field before lifecycle or verdict mapping.
No provider query, enqueue, retry, confirmation, PR, push, or stage transition
was performed.

### Exact candidate and recut

- Repaired source range:
  `f9895e5ee925b1cb20e82c1e7f494212ca0ff9d7..307f1b20647f88509ac69d31c092f81eae2d2fc9`.
- Final base: `c00de6c2140db268eb1fe693abfa347b13a9e0b4`.
- Final tip: `1e54cd4e25a3b9bd4c460d62b7a9d76ba1de9755` in
  `/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/roborev-implementation-exit-repair-recut`.
- `git range-diff` mapped both commits with `=`. The complete old and recut
  ranges share stable patch ID
  `53cc47a31daff0b02822072b14a7e2889cfc4b81`; there is no non-mechanical
  recut difference.

### RED and GREEN evidence

- F1 RED: the focused contract failed with `provider reference is missing:
  scripts/dev-flow-state-prereq.sh` before the runbook repair.
- F2 RED: with the new identity mutation present and the old classifier intact,
  `stale_provider_version` incorrectly mapped to `PASS(passed)` instead of
  `UNKNOWN(stale)`.
- Final focused suite:
  `python3 scripts/roborev-implementation-exit-contract.test.py` — `PASS` in
  8.13 seconds.
- Final full relevant suite: `python3 scripts/kc-dev-flow-contract-test.py` —
  `PASS` in 18.20 seconds.
- `git diff --check origin/main...HEAD`, fixture JSON parsing, and packaged /
  adopted runbook byte parity passed at the final tip. The final worktree is
  clean.

### Supported transaction and adversarial proof

- Installed Spacedock `0.26.0` exercised two independent registered holders
  concurrently through `scripts/dev-flow-state-prereq.sh` and
  `spacedock state commit`: exactly one claim reached `pending`, the same-entity
  loser returned `claim_lost`, and both clones' post-push re-read agreed on one
  remote identity and claimant.
- The shared-parent topology used the same supported path: the first claim was
  durable and clean after post-push re-read; the second same-identity claimant
  was refused before provider work.
- Missing Spacedock, non-holder, dirty, local-ahead, divergent, stale observed
  state, and bypassed-prerequisite cases all remained non-green and earned no
  claim winner. No alternate ledger, tracker, daemon, lock service, or raw-Git
  durability path was added.
- Independent mutations for repository, base, tip, configuration hash,
  RoboRev version, JSON contract, agent, model, reasoning, minimum severity,
  panel, stable member identity, missing member, and extra member all mapped to
  `UNKNOWN(reason: stale)` before lifecycle/verdict interpretation.

### Change map and proof-surface assessment

| Repair surface | Acceptance criteria |
|---|---|
| Packaged and adopted provider contract | AC2, AC3, AC4, AC5 |
| Canonical outcome fixture and classifier | AC2 |
| Registered-holder / supported-transaction topology and refusal fixtures | AC3, AC4 |
| Absolute-claim registry dispositions | AC2, AC3, AC5 |

The repair initially expanded the outcome fixture in generated-looking form;
it was compacted to 45 lines before commit. The remaining repair is 594
additions and 164 deletions across five existing files. Its largest surface is
the executable installed-Spacedock fixture that creates real registered holders,
races both required topologies, and falsifies each required invalid state; none
of those cases can be removed while retaining the explicit F1/F2 disproof
conditions. The complete candidate is one 13-file seam with 1,265 additions and
46 deletions. Splitting the contract from its only executable proof would not
create an independently acceptable slice.

```yaml
work_control_repair:
  provider: roborev
  prior_job: 170
  request_count_this_cycle: 0
  confirmation_count: 0
  outcome: FAIL
  reason: review_findings_repaired_pending_fresh_validation
  authority: evidence-only
  continuation: fresh-validation
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

### Fresh Claude Opus 5 High EM gate: PROCEED

- **Reviewed state revision:**
  `826f3f64ce6ec18971c55bdb5836d4909b015ca1`.
- **Reviewer:** canonical Claude Opus 5 (`claude-opus-5`), high effort, using
  claude.ai OAuth with API-key/auth-token environment variables removed,
  read-only Read/Grep/Glob tools, Bash/Edit/Write disabled, empty MCP, safe mode,
  and no session persistence. Duration was approximately 203 seconds; the Claude
  CLI reported approximate cost USD 1.4197335.
- **Verdict:** `PROCEED`, confidence `high`. The repaired Production-profile
  proposal is gate-ready; remaining risk belongs to normal implementation proof,
  not another ideation repair loop.
- **Implementation proof obligation 1:** the two-concurrent-continuation test
  must exercise the real existing state transaction in both required topologies:
  two independent state clones where non-fast-forward rejection can fire, and a
  shared-parent variant that refuses a second claim when the parent already
  records the same identity. Both variants must perform a post-push re-read. A
  mocked lock is not sufficient.
- **Implementation proof obligation 2:** define deterministic precedence for an
  incomplete or ambiguous member state versus stale completed findings:
  `member_incomplete` versus `stale`.
- **Implementation proof obligation 3:** a claim loser conservatively returning
  `UNKNOWN` with no provider re-query, no enqueue, and no retry is accepted
  behavior.
- **Disproof condition:** return the task from implementation if either
  concurrency topology produces two winners, any loser re-queries or enqueues at
  the provider, or the existing state transaction cannot express same-identity
  refusal without adding a second ledger, tracker, daemon, or generalized lock
  service.
- **Authority boundary:** unchanged. This EM recommendation does not approve the
  Captain gate, implementation dispatch, external spend, PR readiness, or merge;
  existing Spacedock, validation, GitHub-observation, and Captain authorities
  remain in force.

## Stage Report: implementation

### Checklist

- `DONE` — Implemented and recut the approved conditional RoboRev
  implementation-exit slice at candidate
  `b2b2e229738cef5caec84b1a87e69f5f23a50717`, with a
  reachable RED failure for the absent provider contract and GREEN package,
  adopted, loader, configuration, outcome, authority, and spend-cap coverage.
- `DONE` — Proved the closed outcome matrix, omitted-control zero-call path,
  repository-owned single reviewer and named-panel refusal, reuse-before-enqueue,
  one-request/one-confirmation caps, incomplete cost coverage, package/adopted
  byte parity, and unchanged validation/GitHub/Captain authority.
- `DONE` — Exercised the real Git-backed Spacedock state transaction in two
  independent clones and one shared-parent checkout. Both topologies produced
  one winner, performed a post-push remote re-read, and kept the loser from
  provider re-query, enqueue, or retry.
- `DONE` — Used the Captain-authorized single-flight claim and exactly one live
  `gpt-5.6-terra` review request for the exact recut candidate. Provider-native
  job `170` completed with a findings verdict; no retry, confirmation, repair,
  or delivery mutation was performed.

### Summary

The candidate adds one repository-declared RoboRev sensor at implementation
exit. It records an exact-input four-state observation or honest fallback,
loads no provider contract for undeclared adopters, defaults this repository to
one `gpt-5.6-terra` thorough reviewer at medium severity with `panel: none`, and
continues into fresh validation without giving RoboRev delivery authority. No
daemon, second ledger, generalized evaluator, hook, or lock service was added.

### Evidence

- Exact recut base and merge base:
  `f9895e5ee925b1cb20e82c1e7f494212ca0ff9d7`.
- Candidate commit: `b2b2e229738cef5caec84b1a87e69f5f23a50717`.
- Superseded deterministic candidate:
  `78ae901808445f11bbf143dda51be741f245fb17` on approved base
  `6f0e274e6e02ff7e0e5b158859783df037c45c4d`.
- RED: `python3 scripts/roborev-implementation-exit-contract.test.py` failed
  with `missing packaged provider reference` before the implementation.
- GREEN at the candidate tree:
  `python3 scripts/roborev-implementation-exit-contract.test.py` and
  `python3 scripts/kc-dev-flow-contract-test.py` both reported `PASS`;
  `git diff --check origin/main...HEAD` passed and the product worktree was
  clean.
- Local read-only capability/config probe: RoboRev `v0.62.0`, healthy local
  daemon/database/workers, max workers `4`; `roborev config list --local
  --show-origin` resolved repository-local `review_agent=codex`,
  `review_model=gpt-5.6-terra`, `review_reasoning=thorough`, and
  `review_min_severity=medium`.
- Configuration object SHA-256:
  `63b6d59a39c07c8a28db161da4d79af412d4b01d46b5bdcf1c7cc4eec58e64dd`.
- Recut proof: `git range-diff
  6f0e274e6e02ff7e0e5b158859783df037c45c4d..78ae901808445f11bbf143dda51be741f245fb17
  f9895e5ee925b1cb20e82c1e7f494212ca0ff9d7..b2b2e229738cef5caec84b1a87e69f5f23a50717`
  reported `=`. Both patches have stable patch ID
  `8b4e1372577bf5a18286cf9262e5092a65cba2d1`; the two overlapping PR #227
  paths auto-merged without changing either patch, so there is no
  non-mechanical difference to explain.

### Work Control evidence

```yaml
capability: review_convergence
mode: observe
provider: roborev
boundary: implementation-exit
repository: kc-claude-plugins
base: f9895e5ee925b1cb20e82c1e7f494212ca0ff9d7
tip: b2b2e229738cef5caec84b1a87e69f5f23a50717
configuration_sha256: 63b6d59a39c07c8a28db161da4d79af412d4b01d46b5bdcf1c7cc4eec58e64dd
outcome: FAIL
reason: review_findings
detail: "Exact-input RoboRev job 170 completed normally with verdict F and two retained medium findings. No execution failure, skip, incomplete member, retry, confirmation, repair, or delivery mutation occurred."
request_count: 1
confirmation_count: 0
cost:
  approximate_total_usd_before: 0
  approximate_total_usd_after: 0
  jobs_with_cost_before: 0
  jobs_with_cost_after: 0
  jobs_total_before: 0
  jobs_total_after: 1
  complete: false
  interpretation: "Provider cost coverage is incomplete, so the zero reported total is not a zero-cost claim."
authority: evidence-only
continuation: fresh-validation
```

### Live observation evidence

- Captain authorization bounded the run to one initial request, zero automatic
  retry, zero confirmation, and at most 20 minutes from the first provider
  query. The first provider query was `2026-08-14T09:55:25Z`; terminal evidence
  was read at `2026-08-14T09:58:44Z`, for 199 seconds total.
- The claim identity was
  `338ce58947be74701d68f3ee6335ea924647cc874d3304e45285df3180ae5d1b`.
  Claim commit `c1fb6adac1721a8fbb5b9f6f7a4769151c172b59` was pushed by
  `codex-worker:/root/roborev_implementation` and verified by a post-push remote
  re-read before enqueue.
- The exact request bound repository `github.com/iamcxa/kc-claude-plugins`, base
  `f9895e5ee925b1cb20e82c1e7f494212ca0ff9d7`, tip
  `b2b2e229738cef5caec84b1a87e69f5f23a50717`, agent `codex`, model
  `gpt-5.6-terra`, reasoning `thorough`, minimum severity `medium`, and
  `panel: none`. The provider represents that panel selection as
  `panel_name: null`; the complete population was the single parent reviewer.
- A post-claim winner re-query found no matching job. One request created the
  sole new matching parent job: job ID `170`, job UUID
  `cb3847db-560b-4053-9235-2e378d5b6f87`, review record ID `165`, review UUID
  `440fd7e8-b097-4ec6-a72c-d758161035c1`, session
  `019fffb3-6a27-77a2-b8f2-7258377ba3ed`. Its provider range, branch, agent,
  model, reasoning, and severity all matched; retry count was zero.
- Job `170` ran from `2026-08-14T09:56:14Z` to
  `2026-08-14T09:58:30Z`, reached `status: done`, `verdict: F`, and had no
  execution error. It reported two medium findings: the runbook claim path does
  not require the registered state-holder/supported state transaction, and the
  identity contract test omits reviewer-configuration and panel-population
  mismatch cases. Under the closed mapping this is `FAIL`, not `UNKNOWN`.
- `roborev cost --json` moved from zero observed jobs to one, but both snapshots
  reported `jobs_with_cost: 0` and `complete: false`. No precise cost conclusion
  is possible.

### Changed-file to acceptance-criteria map

| Surface | AC |
|---|---|
| `.roborev.toml` | AC3 |
| `PRODUCT.md`, `ARCHITECTURE.md` | AC1, AC3, AC4 |
| `kc-dev-flow/README.md`, `kc-dev-flow/skills/continue-dev-flow/SKILL.md` | AC1, AC4, AC5 |
| Packaged and adopted RoboRev contract | AC1, AC2, AC3, AC4, AC5 |
| `docs/dev/README.md`, `docs/dev/ROADMAP.md` | AC1, AC3, AC4, AC5 |
| Absolute registry, focused fixture/test, and aggregate contract test | AC1, AC2, AC3, AC4, AC5 |

### Delivery topology

This is one dependent product slice, not multiple dependent layers or
independent sibling slices. The merge-base diff is 13 files and 881 gross
additions/deletions, below both numeric triggers. The authoritative topology is
one Draft PR with no Native stack exception. The implementation worker has no
push or PR-creation authority.

### RoboRev observation claim

- identity: `338ce58947be74701d68f3ee6335ea924647cc874d3304e45285df3180ae5d1b`
- claimant: `codex-worker:/root/roborev_implementation`
- observed-state-revision: `625c60eb4937db31587a235f498da6f8778df11c`
- repository: `github.com/iamcxa/kc-claude-plugins`
- base: `f9895e5ee925b1cb20e82c1e7f494212ca0ff9d7`
- tip: `b2b2e229738cef5caec84b1a87e69f5f23a50717`
- configuration-sha256: `63b6d59a39c07c8a28db161da4d79af412d4b01d46b5bdcf1c7cc4eec58e64dd`
- state: `claimed`

## Stage Report: validation

### Checklist

- `DONE` — Bound fresh validation to merge target
  `f9895e5ee925b1cb20e82c1e7f494212ca0ff9d7`, candidate
  `b2b2e229738cef5caec84b1a87e69f5f23a50717`, validation-entry state
  `33bed021`, the authoritative AC1-AC5 revision, and all 13 changed files.
  The product worktree was clean; both the focused and full relevant suites
  passed, and `git diff --check` passed.
- `DONE` — Adjudicated both medium findings from RoboRev job `170` against
  exact code, the Local Profile, kernel, Work Control Profile, and direct
  falsifiers. Both are supported; the concrete repair asks below remain inside
  AC2/AC3 and do not add a daemon, ledger, tracker, evaluator, or reviewer
  round.
- `DONE` — Obtained exactly one fresh-context GPT-5.6 High engineering
  judgment at the exact candidate. It returned `route: return`, confidence
  `high`, with `multi_model: not_needed`.
- `DONE` — Recorded the initial-delivery no-PR condition, one-PR topology,
  complete AC/file mapping, provider-origin re-observation, and the exact
  return-to-implementation route without editing implementation or exercising
  push, PR, provider, Ready, merge, release, or terminalization authority.

### Summary

`REJECTED`. RoboRev job `170` raised two medium claims and fresh validation
supports both. The current contract can claim single-flight without requiring
the repository's registered Spacedock state boundary, and its executable
identity matcher accepts reviewer-configuration and panel/member-population
mismatches as `PASS`. Return the same bounded slice to implementation, repair
AC2/AC3, recut against the then-current target, and re-enter fresh validation.

### Validation evidence

- Exact inputs: base `f9895e5ee925b1cb20e82c1e7f494212ca0ff9d7`;
  candidate `b2b2e229738cef5caec84b1a87e69f5f23a50717`; state
  `33bed021`; candidate worktree clean; merge base equal to the declared base.
- Fresh suites: `python3 scripts/roborev-implementation-exit-contract.test.py`
  reported `PASS`; `python3 scripts/kc-dev-flow-contract-test.py` reported
  `PASS`; `git diff --check` reported no error.
- Fresh origin-target observation at `2026-08-14T10:09:44Z` found
  `origin/main` at `c00de6c2140db268eb1fe693abfa347b13a9e0b4`. Its three
  GitHub-projection files are disjoint from this 13-file candidate and a
  merge-tree showed no conflict. This does not alter either adjudication, but
  the repaired candidate must bind the latest merge target.

```text
Lenses: FAIL — behavior, contract/schema, state/concurrency, runtime/platform, docs/policy, and delivery fired; 2 supported findings from exact base/tip, AC1-AC5, the Local Profile/state prerequisite, provider runbook, focused fixture, job 170 JSON, and direct mismatch/binary-absence falsifiers. Security/privacy found no new credential, disclosure, destructive, or GitHub-mutation path; delivery authority remained intact.
Diff coverage: 100% measured statement execution (231/231 focused contract statements and 1386/1386 aggregate contract statements; 1617/1617 total) and 13/13 changed files mapped to ACs. This is not behavioral closure: six declared identity mutations remained incorrectly green outside the modeled denominator.
Adversarial: FAIL — agent, model, reasoning, minimum-severity, panel-name, and member-identity/population mismatches each returned PASS; the focused concurrency fixture also passed with Spacedock absent from PATH, proving it exercises bare Git rather than the registered workflow-state boundary.
Cross-model: not_needed — the one fresh GPT-5.6 High EM adjudicated both findings supported, returned route `return` with high confidence, and found no contested, irreversible, low-confidence, or unresolved residue.
E2E: FAIL — provider-native local RoboRev v0.62 job 170 evaluated the exact range with the repository-owned single reviewer and retained two supported medium findings; validation re-read it without enqueue, retry, confirmation, repair, or external mutation.
Origin re-observation: FAIL — Reported scenario: one exact-tip implementation-exit observation must bind the supported state transaction and full reviewer/panel identity before fresh validation | Originating runtime kind: local RoboRev v0.62 daemon, single Codex reviewer, exact Git range | Re-observation artifact/revision: job 170 / cb3847db-560b-4053-9235-2e378d5b6f87 at candidate b2b2e229738cef5caec84b1a87e69f5f23a50717 | Equivalent-runtime rationale: same provider-native job, actor, exact range, repository configuration, daemon path, and medium-severity policy were re-read through `show --json`; direct mutations exercised the claim-relevant matcher | Falsifier kind: mutation | Result: both provider claims reproduced as supported contract failures; cost remains 0 observed USD across 0/1 covered jobs with `complete: false`, so zero is not a cost claim.
```

### Finding adjudications and repair route

1. **F1 — supported (`AC3`, with AC4/AC5 parity implications).** The Local
   Profile at `docs/dev/README.md:79-103` requires the registered
   `spacedock-state/dev` holder, `scripts/dev-flow-state-prereq.sh`, and the
   supported Spacedock mutation/durability transaction. The candidate provider
   runbook at lines 68-91 instead prescribes direct append, commit, and push
   without requiring that boundary. The focused proof at lines 133-235 creates
   temporary bare-Git clones and still passes when `spacedock` is absent from
   `PATH`; it therefore cannot prove the accepted Spacedock lifecycle claim.
   **Repair ask:** make the provider contract resolve and obey the Local
   Profile's registered state holder/prerequisite and repository-supported
   claim transaction, return non-green when that boundary is unavailable, and
   exercise both concurrency topologies through that real boundary. Prove a
   missing, stale, ahead, divergent, or bypassed state holder cannot earn a
   winner. Do not add a second state system.
2. **F2 — supported (`AC2`).** The runbook at lines 49-66 binds RoboRev
   version/JSON contract, agent, model, reasoning, minimum severity, panel, and
   complete declared member population, but `classify` at test lines 32-64 and
   fixture identity lines 2-7 compare only repository, base, tip, and
   configuration. Independent mutations of every omitted reviewer/panel field
   still returned `PASS`. **Repair ask:** extend the canonical fixture and
   matcher to correlate every declared identity field and stable member
   identities/population before lifecycle/verdict interpretation; add one
   mutation per field and require `UNKNOWN(reason: stale)` or the other exact
   declared non-pass.

After the bounded repair, keep package/adopted contracts byte-identical, rerun
the focused and aggregate suites plus the adversarial mutations, recut against
the then-current `origin/main`, and dispatch a new fresh validation worker. Do
not request another RoboRev job unless separately authorized under the existing
confirmation cap.

### Feedback and delivery topology

- `PR feedback: N/A — initial delivery has no product PR or stack layer; the
  authoritative task's pr field is blank, and the workflow creates its first
  Draft only after local validation and Captain push approval. No PR was
  queried or created merely to satisfy observation.`
- Delivery topology remains one dependent product slice and one future Draft
  PR; no stack exception is earned.
- Changed-file coverage remains complete: `.roborev.toml` maps to AC3;
  `PRODUCT.md` and `ARCHITECTURE.md` to AC1/AC3/AC4; package README and
  continuation skill to AC1/AC4/AC5; packaged/adopted provider contracts to
  AC1-AC5; workflow README/Roadmap to AC1/AC3/AC4/AC5; and the registry,
  outcome fixture, focused test, and aggregate test to AC1-AC5. F1/F2 prevent
  acceptance despite this complete map.

### Engineering judgment

```yaml
science_officer_em_upward_report:
  em_judgment: >-
    The validation gate is not ready. F1 and F2 are supported by the governing contracts and adversarial behavior, so the exact candidate b2b2e229738cef5caec84b1a87e69f5f23a50717 should return to implementation for a bounded AC2/AC3 repair.
  evidence_synthesis: >-
    The clean candidate is bound to base f9895e5ee925b1cb20e82c1e7f494212ca0ff9d7, candidate b2b2e229738cef5caec84b1a87e69f5f23a50717, and validation-entry state 33bed021. The focused and aggregate contract tests pass, and the focused script executes 231/231 measured statements, but those receipts do not close the behavioral contract. For F1, docs/dev/README.md:79-103 requires the registered spacedock-state/dev holder, the clean-holder prerequisite, and the supported Spacedock mutation/durability transaction; docs/dev/runbooks/roborev-implementation-exit.md:68-91 instead prescribes direct task append, Git commit, and push, while scripts/roborev-implementation-exit-contract.test.py:133-235 proves only temporary bare-Git clones and still passes with Spacedock absent from PATH. For F2, the runbook's exact-input record at lines 49-66 includes RoboRev version/JSON contract, agent, model, reasoning, minimum severity, panel, and complete member population, but classify at test lines 32-64 and the fixture identity correlate only repository, base, tip, and configuration; direct mutations of agent, model, reasoning, severity, panel, member identity, and member population still return PASS. RoboRev job 170 is exact-range findings evidence with two medium claims and incomplete cost coverage, not authority. No PR exists at this brand-new delivery point, so GitHub feedback observation is not yet required. origin/main later advanced to c00de6c2140db268eb1fe693abfa347b13a9e0b4 through three disjoint projection files; that does not change either adjudication, but a repaired candidate must bind the latest target.
  risk_tradeoff_call: >-
    The sensor buys useful early exact-tip defect evidence, but the current contract can claim single-flight without exercising the repository's authoritative state path and can reuse a job whose declared reviewer identity does not match. That risks duplicate provider work, incorrect evidence attribution, and false confidence at implementation exit. The lowest-cost alternative is a bounded repair to the existing runbook and fixture, not a new ledger, daemon, tracker, or evaluator.
  recommendation: >-
    Return to implementation. For AC3, require the Local Profile's registered state holder, clean-holder prerequisite, and supported Spacedock mutation/durability transaction, then replace the bare-Git-only proof with both required concurrency topologies through that real boundary and prove missing Spacedock cannot pass. For AC2, extend the canonical fixture and matcher to validate RoboRev version/JSON contract, agent, model, reasoning, minimum severity, panel identity, member identities, and complete member population before lifecycle/verdict interpretation; make every independent mismatch produce stale or another declared non-pass. Keep packaged and adopted contracts byte-identical, rerun the focused and full relevant suites plus all adversarial mutations, recut against latest origin/main, and re-enter fresh validation at the new exact head.
  route: return
  confidence: high
  multi_model: not_needed
  fo_boundary: >-
    FO may account for evidence and route this advisory to Gate Authority; it may not adjudicate the findings, mutate state, invoke RoboRev, create or push a PR, or advance the stage.
  engineering_judgment:
    question: >-
      Do RoboRev findings F1 and F2 identify material AC2/AC3 gaps at candidate b2b2e229738cef5caec84b1a87e69f5f23a50717, or do the green focused/full tests and implementation report justify proceeding from validation?
    revision: >-
      base f9895e5ee925b1cb20e82c1e7f494212ca0ff9d7; candidate b2b2e229738cef5caec84b1a87e69f5f23a50717; validation-entry state 33bed021
    evidence_synthesis: >-
      The clean candidate is bound to base f9895e5ee925b1cb20e82c1e7f494212ca0ff9d7, candidate b2b2e229738cef5caec84b1a87e69f5f23a50717, and validation-entry state 33bed021. The focused and aggregate contract tests pass, and the focused script executes 231/231 measured statements, but those receipts do not close the behavioral contract. For F1, docs/dev/README.md:79-103 requires the registered spacedock-state/dev holder, the clean-holder prerequisite, and the supported Spacedock mutation/durability transaction; docs/dev/runbooks/roborev-implementation-exit.md:68-91 instead prescribes direct task append, Git commit, and push, while scripts/roborev-implementation-exit-contract.test.py:133-235 proves only temporary bare-Git clones and still passes with Spacedock absent from PATH. For F2, the runbook's exact-input record at lines 49-66 includes RoboRev version/JSON contract, agent, model, reasoning, minimum severity, panel, and complete member population, but classify at test lines 32-64 and the fixture identity correlate only repository, base, tip, and configuration; direct mutations of agent, model, reasoning, severity, panel, member identity, and member population still return PASS. RoboRev job 170 is exact-range findings evidence with two medium claims and incomplete cost coverage, not authority. No PR exists at this brand-new delivery point, so GitHub feedback observation is not yet required. origin/main later advanced to c00de6c2140db268eb1fe693abfa347b13a9e0b4 through three disjoint projection files; that does not change either adjudication, but a repaired candidate must bind the latest target.
    adjudications:
      - finding: F1-state-holder-and-supported-transaction
        disposition: supported
        basis: >-
          AC3 requires the claim to use existing Spacedock execution state. The Local Profile at docs/dev/README.md:79-103 makes the registered spacedock-state/dev holder, scripts/dev-flow-state-prereq.sh, and the supported Spacedock setter/durability transaction authoritative. The candidate runbook at lines 68-91 directly specifies append, commit, and push without requiring that boundary, and the focused test at lines 133-235 substitutes temporary bare-Git clones; its PASS with Spacedock absent from PATH demonstrates that the declared lifecycle obligation is not exercised.
      - finding: F2-incomplete-exact-input-identity
        disposition: supported
        basis: >-
          AC2 and the candidate runbook at lines 49-66 require correlation across repository, range/tip, configuration, RoboRev version/JSON contract, agent, model, reasoning, minimum severity, panel, and complete member identity/population. The classifier at scripts/roborev-implementation-exit-contract.test.py:32-64 and fixture identity at outcomes.json:2-7 check only repository, base, tip, and configuration. Independent reviewer and panel identity/population mutations remaining PASS directly falsify the declared exact-input matching claim.
    risk_tradeoff: >-
      The sensor buys useful early exact-tip defect evidence, but the current contract can claim single-flight without exercising the repository's authoritative state path and can reuse a job whose declared reviewer identity does not match. That risks duplicate provider work, incorrect evidence attribution, and false confidence at implementation exit. The lowest-cost alternative is a bounded repair to the existing runbook and fixture, not a new ledger, daemon, tracker, or evaluator.
    recommendation: >-
      Return to implementation. For AC3, require the Local Profile's registered state holder, clean-holder prerequisite, and supported Spacedock mutation/durability transaction, then replace the bare-Git-only proof with both required concurrency topologies through that real boundary and prove missing Spacedock cannot pass. For AC2, extend the canonical fixture and matcher to validate RoboRev version/JSON contract, agent, model, reasoning, minimum severity, panel identity, member identities, and complete member population before lifecycle/verdict interpretation; make every independent mismatch produce stale or another declared non-pass. Keep packaged and adopted contracts byte-identical, rerun the focused and full relevant suites plus all adversarial mutations, recut against latest origin/main, and re-enter fresh validation at the new exact head.
    route: return
    confidence: high
    dissent: >-
      The implementation report says AC2 and AC3 are proved, and both declared suites are green. That conclusion is rejected because the executable fixture omits the authoritative Spacedock boundary and accepts six declared identity mismatches; there is no unresolved dissent after primary-source adjudication.
    disproof_condition: >-
      Change to proceed on a new exact candidate if both concurrency topologies exercise the registered Local Profile state holder and supported Spacedock transaction, absence or bypass of that boundary cannot pass, every declared reviewer/panel/member identity mutation produces the specified non-pass, all relevant tests pass at that exact head, and the candidate is rebound to the then-current merge target.
    authority_boundary: >-
      Captain retains scope, Roadmap, irreversibility, accepted-red, push, initial Draft, Ready, merge, and terminalization authority; Gate Authority owns stage advancement; the implementation owner performs any repair; Spacedock and its registered state holder retain work-item and execution-state mutation authority; fresh validation and later GitHub observation retain their existing roles; RoboRev remains an evidence-only sensor with no provider-posting or workflow authority.
```

## Stage Report: validation cycle 2

### Checklist

- `DONE` — Bound the fresh cycle to merge target
  `c00de6c2140db268eb1fe693abfa347b13a9e0b4`, candidate
  `1e54cd4e25a3b9bd4c460d62b7a9d76ba1de9755`, validation-entry task revision
  `ce9e7632`, all five acceptance criteria, and all 13 changed files. The
  product worktree was clean, the declared base was the merge base and current
  `origin/main`, both relevant suites passed, and `git diff --check` passed.
- `DONE` — Revalidated F1 through installed Spacedock `0.26.0`, the registered
  Local Profile holder shape, `scripts/dev-flow-state-prereq.sh`, and
  `spacedock state commit` in both concurrency topologies. Adjudicated F2 with
  direct wrong-value, missing-field, malformed-population, and precedence
  falsifiers without editing product files or invoking RoboRev.
- `DONE` — Obtained exactly one new fresh-context GPT-5.6 High engineering
  judgment against this exact candidate. It returned `route: return`,
  confidence `high`, and `multi_model: not_needed`.
- `DONE` — Recorded all six validation-evidence lines, measured focused-test
  execution, package/adopted parity, the initial-delivery no-PR condition,
  one-PR topology, proof-surface judgment, and one structural bounded route for
  the second rejected cycle without exercising implementation or delivery
  authority.

### Summary

`REJECTED`. F1/AC3 is closed: the repaired fixture now exercises the actual
registered-holder prerequisite and supported Spacedock durability transaction,
and its large setup is not replaceable by the existing refusal-only test. AC1
and AC2 remain open. Missing canonical identity evidence can still become
`PASS`, malformed member evidence escapes the closed outcome mapping, terminal
failure can be mislabeled as timeout, and historical job `170` is not an
exact-current-tip receipt for the repaired candidate. Return once for a
structural, bounded classifier/receipt correction; do not invoke RoboRev again.

### Validation evidence

- Exact inputs: base and merge base
  `c00de6c2140db268eb1fe693abfa347b13a9e0b4`; candidate
  `1e54cd4e25a3b9bd4c460d62b7a9d76ba1de9755`; task revision `ce9e7632`;
  clean product worktree; 13 files, 1,265 additions, and 46 deletions.
- Fresh suites: `python3 scripts/roborev-implementation-exit-contract.test.py`
  passed in 8.57 seconds; `python3 scripts/kc-dev-flow-contract-test.py` passed
  in 19.28 seconds; `git diff --check` passed. Python trace observed 441/441
  executable statement lines in the focused test; this is statement execution,
  not proof of unmodeled inputs or prose behavior.
- Fresh origin observation at `2026-08-14T10:42:26Z` found `origin/main` still
  at the declared base. Package and adopted provider contracts were byte
  identical, the fixture parsed as JSON, and no product PR exists for branch
  `iamcxa/roborev-implementation-exit-repair-recut`.

```text
Lenses: FAIL — behavior, contract/schema, state/concurrency, runtime/platform, docs/policy, and delivery fired against AC1-AC5, the Local Profile, kernel, Work Control Profile, provider runbook, exact 13-file diff, installed Spacedock transaction, fixture classifier, and historical job 170; F1 and present-but-wrong identity mutations passed, while 4 material AC1/AC2 gaps remained. Security/privacy found no new credential, disclosure, destructive, or GitHub-mutation path; authority remained intact.
Diff coverage: focused executable statement execution was 100% (441/441 lines) and 13/13 changed files were mapped to AC1-AC5; prose-only surfaces were adversarially reviewed rather than assigned a numeric execution percentage. Full execution does not cover absent identity fields, malformed population shapes, failed-plus-deadline precedence, or a changed-tip receipt.
Adversarial: FAIL — all 11 present-but-wrong scalar identity fields plus wrong/missing/extra stable members returned UNKNOWN(stale), but the canonical PASS fixture supplied none of those scalar fields and still passed; deleting each required scalar independently still passed, malformed member populations raised SystemExit or AttributeError instead of UNKNOWN, and terminal failed plus deadline_reached returned timed_out. F1's installed transaction produced one winner in both topologies, refused invalid holder states, and the suite failed when SPACEDOCK_BIN was replaced by /usr/bin/false.
Cross-model: not_needed — the one fresh GPT-5.6 High EM adjudicated F1 closed, F2A/F2B/F2C and the current-tip receipt gap supported, returned route return with high confidence, and recommended one structural bounded correction for the second rejected cycle rather than a second model.
E2E: FAIL — installed Spacedock 0.26.0 exercised registered holders, the clean-holder prerequisite, supported state commit, independent-clone race, shared-parent refusal, and post-push re-read at this exact candidate, but no exact-current-tip RoboRev observation or closed non-green fallback exists after the repair; historical job 170 was not queried, retried, or confirmed.
Origin re-observation: FAIL — Reported scenario: one proportional implementation-exit observation must bind the full exact-input identity and the supported Spacedock transaction before fresh validation | Originating runtime kind: local RoboRev v0.62 historical job plus installed Spacedock 0.26.0 state transaction | Re-observation artifact/revision: job 170 retained as historical evidence; state fixture and classifier at candidate 1e54cd4e25a3b9bd4c460d62b7a9d76ba1de9755 | Equivalent-runtime rationale: the repaired concurrency path used the declared holder/prerequisite/durability commands and the classifier exercised the same canonical provider fields and member population named by the runbook | Falsifier kind: mutation and refusal | Result: F1 passed through the actual supported transaction, but missing identity and malformed/precedence mutations defeated AC2 and the changed candidate has no closed exact-tip receipt, so the origin claim remains non-green.
```

### Finding adjudications and bounded route

1. **F1 — closed (`AC3`).** The focused test uses installed Spacedock `0.26.0`,
   the real `scripts/dev-flow-state-prereq.sh`, registered
   `spacedock-state/dev` holders, and `spacedock state commit`. Independent
   clones produced one `pending` winner and one `claim_lost`; the shared parent
   refused the second identity; post-push reads agreed. Missing tool,
   non-holder, dirty, ahead, divergent, stale, and bypassed-preparation cases
   earned no winner. Replacing `SPACEDOCK_BIN` with `/usr/bin/false` made the
   suite fail. The existing 47-line prerequisite test covers only refusal and
   cannot substitute for this concurrency/durability proof; the retained
   installed-Spacedock fixture is bounded necessary evidence, not removable
   ceremony in this slice.
2. **F2A — supported (`AC2`).** `classify` at lines 45-59 uses
   `case.get(field, identity[field])`. The PASS fixture contains none of the 11
   scalar identity fields, and removal of any one field from an otherwise
   explicit exact case still returned `PASS(passed)`. Missing provider evidence
   therefore masquerades as an exact match. Require each canonical field to be
   present and equal before lifecycle/verdict mapping; add sparse and
   field-deletion falsifiers.
3. **F2B — supported (`AC2`).** `members=None` or a mapping exits through
   `SystemExit`, and a null member raises `AttributeError`. The closed contract
   requires malformed, incomplete, or ambiguous population evidence to return
   a typed non-pass. Add one fail-closed normalization boundary and make every
   malformed shape return the declared `UNKNOWN` reason without exception.
4. **F2C — supported (`AC2`).** A terminal parent `status: failed` combined
   with `deadline_reached: true` returned `UNKNOWN(timed_out)` because deadline
   interpretation precedes failure. Apply terminal parent/member execution
   failure before deadline interpretation and add the overlap mutant.
5. **Current-tip receipt — supported (`AC1`).** Job `170` belongs to the
   superseded tip. The repair-cycle block preserves useful historical
   provenance but carries `FAIL` with a reason outside the closed mapping. For
   the repaired exact tip, record a closed honest non-pass such as
   `UNKNOWN(reason: stale)` referencing job `170`; do not request confirmation
   without separate authority.

This is the second rejected validation cycle at the same gate. The fresh EM
recommends one structural bounded correction because the architecture, real
state transaction, proportional spend boundary, authority separation, package
parity, and one-PR topology are otherwise valid. An ideation reset, scope cut,
or stop would discard working proof without addressing the localized
normalization/receipt defects.

### Feedback and delivery topology

- `PR feedback: N/A — initial delivery has no product PR or stack layer; the
  exact branch query returned an empty population. The first Draft remains
  Captain-push-authorized only after a passed local validation.`
- Delivery remains one dependent slice and one future Draft PR. No stack
  exception, provider posting, push, Draft creation, Ready, merge, release, or
  terminalization was performed.
- Changed-file coverage remains 13/13: configuration maps to AC3; product and
  architecture docs to AC1/AC3/AC4; package/adopted loader and runbook surfaces
  to AC1-AC5; Roadmap to AC1/AC3/AC4/AC5; and registry, fixture, focused test,
  and aggregate test to AC1-AC5.

### Engineering judgment

```yaml
science_officer_em_upward_report:
  em_judgment: >-
    The exact candidate 1e54cd4e25a3b9bd4c460d62b7a9d76ba1de9755 should not proceed. F1 is credibly closed and the retained proof surface is justified, but AC1 and AC2 remain materially open: the current-tip Work Control record reuses a historical FAIL outside the closed mapping, missing identity evidence can still produce PASS, malformed member evidence aborts instead of returning UNKNOWN, and terminal failure can be mislabeled timed_out. Because this is the second rejected validation cycle, recommend one structural bounded correction rather than ideation reset, scope narrowing, or stop.
  evidence_synthesis: >-
    The clean worktree, HEAD, origin/main, and merge base bind the review to base c00de6c2140db268eb1fe693abfa347b13a9e0b4 and candidate 1e54cd4e25a3b9bd4c460d62b7a9d76ba1de9755. Fresh focused and aggregate contract reruns pass, git diff --check is clean, package and adopted runbooks are byte-identical, and the candidate changes 13 files with 1265 additions and 46 deletions. F1 is closed by actual Spacedock 0.26.0 execution through scripts/dev-flow-state-prereq.sh and spacedock state commit: independent clones produce one winner and one claim_lost, the shared parent refuses duplication, both paths re-read authoritative state, invalid holder states stay non-green, and substituting /usr/bin/false for SPACEDOCK_BIN makes the focused suite fail. The 710-line focused file is therefore substantial executable setup and proof for concurrency and state-boundary behavior that the existing 47-line refusal-only test cannot establish. However, classify at lines 45-59 compares each required scalar with case.get(field, identity[field]); the canonical PASS case contains none of those eleven fields, a sparse case returns PASS, and deleting any one field from an explicit exact case still returns PASS, contrary to AC2 and runbook lines 49-66 and 121-157. members=None or a mapping raises SystemExit and members=[None] raises AttributeError rather than producing a declared UNKNOWN. A failed terminal parent with deadline_reached=true returns UNKNOWN(timed_out) because the deadline branch precedes failure, although failed is terminal evidence and the runbook assigns execution failure UNKNOWN(failed). The repair-cycle Work Control block also carries historical job 170 as FAIL with a new non-canonical reason at the changed tip; the old job is useful provenance but cannot be the exact-current-tip receipt required by AC1. AC3's state and spend controls, AC4's authority boundary, and AC5's candidate-stage package parity are otherwise supported; published-tag and exact-head delivery evidence remain later delivery obligations.
  risk_tradeoff_call: >-
    The accepted sensor provides useful exact-tip defect evidence, and F1 now proves its most expensive concurrency boundary through the supported runtime. Proceeding would still permit absent provider identity evidence to be treated as an exact match, turn malformed provider data into an uncontrolled abort, misstate execution failure as timeout, and present a stale historical FAIL as the changed tip's receipt. The durable cost of correction is small and localized: replace permissive defaulting with one fail-closed normalization/schema boundary, define total member-shape handling and terminal precedence, and record a closed current-tip non-pass without another provider request. Reset, narrowing, or stopping would discard a valid architecture without reducing this localized risk.
  recommendation: >-
    Return for one Captain-approved bounded correction. Structurally eliminate the repeated identity-matching failure shape: require every canonical scalar field to be present and equal before PASS or FAIL, normalize and validate the complete member population without exceptions, and apply terminal parent/member execution failure before deadline interpretation. Add adversarial cases for sparse identity, deletion of every required field, malformed member shapes, and failed-plus-deadline precedence; do not merely add more permissive defaults. Replace the repair-cycle Work Control entry with a closed exact-current-tip non-pass such as UNKNOWN(stale) referencing historical job 170, unless separate authority later permits confirmation; do not invoke RoboRev for this correction. Retain the proven Spacedock harness, package/adopted parity, authority limits, and one-PR topology, then rerun the focused and aggregate suites and dispatch fresh validation at the new exact head.
  route: return
  confidence: high
  multi_model: not_needed
  fo_boundary: >-
    FO may preserve evidence, present this second-cycle recommendation to the Captain, and route an authorized bounded correction; FO may not accept the residuals, invoke RoboRev, mutate implementation or state, create or push the Draft PR, or advance the validation gate.
  engineering_judgment:
    question: >-
      After the prior validation rejection and bounded repair, do F1 closure and the green exact-candidate receipts justify proceeding, or do F2A, F2B, F2C and the current-tip receipt require another bounded correction at the second validation cycle?
    revision: >-
      base c00de6c2140db268eb1fe693abfa347b13a9e0b4; candidate 1e54cd4e25a3b9bd4c460d62b7a9d76ba1de9755; authoritative task roborev-implementation-exit at validation
    evidence_synthesis: >-
      The clean worktree, HEAD, origin/main, and merge base bind the review to base c00de6c2140db268eb1fe693abfa347b13a9e0b4 and candidate 1e54cd4e25a3b9bd4c460d62b7a9d76ba1de9755. Fresh focused and aggregate contract reruns pass, git diff --check is clean, package and adopted runbooks are byte-identical, and the candidate changes 13 files with 1265 additions and 46 deletions. F1 is closed by actual Spacedock 0.26.0 execution through scripts/dev-flow-state-prereq.sh and spacedock state commit: independent clones produce one winner and one claim_lost, the shared parent refuses duplication, both paths re-read authoritative state, invalid holder states stay non-green, and substituting /usr/bin/false for SPACEDOCK_BIN makes the focused suite fail. The 710-line focused file is therefore substantial executable setup and proof for concurrency and state-boundary behavior that the existing 47-line refusal-only test cannot establish. However, classify at lines 45-59 compares each required scalar with case.get(field, identity[field]); the canonical PASS case contains none of those eleven fields, a sparse case returns PASS, and deleting any one field from an explicit exact case still returns PASS, contrary to AC2 and runbook lines 49-66 and 121-157. members=None or a mapping raises SystemExit and members=[None] raises AttributeError rather than producing a declared UNKNOWN. A failed terminal parent with deadline_reached=true returns UNKNOWN(timed_out) because the deadline branch precedes failure, although failed is terminal evidence and the runbook assigns execution failure UNKNOWN(failed). The repair-cycle Work Control block also carries historical job 170 as FAIL with a new non-canonical reason at the changed tip; the old job is useful provenance but cannot be the exact-current-tip receipt required by AC1. AC3's state and spend controls, AC4's authority boundary, and AC5's candidate-stage package parity are otherwise supported; published-tag and exact-head delivery evidence remain later delivery obligations.
    adjudications:
      - finding: F1-registered-state-transaction-closure
        disposition: supported
        basis: >-
          AC3, the Local Profile state boundary, and runbook lines 69-112 require the registered holder, clean-holder prerequisite, supported Spacedock durability command, one winner, loser refusal, and post-push re-read. The focused test exercises those paths with installed Spacedock 0.26.0, rejects missing, dirty, ahead, divergent, stale, non-holder, and bypassed states, and fails when SPACEDOCK_BIN is replaced with /usr/bin/false.
      - finding: F2-explicit-mismatch-repair
        disposition: supported
        basis: >-
          Independent present-but-wrong mutations of repository, base, tip, configuration, provider version, JSON contract, agent, model, reasoning, severity, panel, member identities, and member count all return UNKNOWN(stale). This closes the previously reported explicit-value mismatch cases, but not missing or malformed evidence.
      - finding: F2A-missing-identity-evidence-can-pass
        disposition: supported
        basis: >-
          AC2 and runbook lines 49-66 require provider evidence to match every canonical input. The classifier's case.get(field, identity[field]) substitutes the expected value when evidence omits a field. The canonical PASS fixture omits all eleven scalar fields, sparse PASS returns PASS, and deleting each field independently also returns PASS.
      - finding: F2B-malformed-member-population-is-not-total
        disposition: supported
        basis: >-
          AC2 and runbook lines 136-157 require incomplete or ambiguous member evidence to become a typed UNKNOWN. The executable classifier instead raises SystemExit for None or mapping populations and AttributeError for a null member, so it supplies neither the closed outcome nor a stable reason.
      - finding: F2C-terminal-failure-precedence
        disposition: supported
        basis: >-
          Runbook lines 140-154 assign terminal parent or member execution failure UNKNOWN(failed), while timed_out applies only when no terminal exact-input evidence exists. The classifier checks deadline_reached before status failed, causing a terminal failed parent at the deadline to return UNKNOWN(timed_out).
      - finding: AC1-current-tip-observation-or-fallback
        disposition: unsupported
        basis: >-
          Kernel exact-revision discipline and runbook lines 159-163 invalidate job 170 as a receipt for the changed candidate tip. The repair block preserves its historical FAIL under reason review_findings_repaired_pending_fresh_validation, which is outside the closed mapping. No further provider request is needed, but the current tip still needs an honest closed non-pass record.
      - finding: AC2-closed-exact-input-classification
        disposition: unsupported
        basis: >-
          F2A permits false PASS, F2B escapes the four-state mapping, and F2C violates declared reason precedence. Green modeled cases and full statement execution cannot close unmodeled required-field and malformed-shape behavior.
      - finding: AC3-bounded-spend-and-single-flight
        disposition: supported
        basis: >-
          The real supported state transaction produces at most one winner across both required topologies, claim losers do not reach provider re-query or enqueue, request and confirmation caps remain explicit, and no new ledger, daemon, tracker, or lock service was introduced.
      - finding: AC4-evidence-only-authority
        disposition: supported
        basis: >-
          The package, adopted runbook, Local Profile, architecture, and executable authority mutants retain fresh validation, GitHub observation, and Captain delivery authority and grant RoboRev no stage or delivery mutation.
      - finding: AC5-candidate-parity-and-proof-surface
        disposition: supported
        basis: >-
          Package and adopted runbooks are byte-identical, fixture JSON parses, the relevant aggregate contract passes, and every changed file remains mapped to AC1-AC5. The 710-line focused harness is one inseparable executable proof surface for real concurrency and refusal behavior; the shorter existing prerequisite test cannot replace it. Published-tag and exact-head delivery proof remain future release-boundary obligations.
    risk_tradeoff: >-
      The accepted sensor provides useful exact-tip defect evidence, and F1 now proves its most expensive concurrency boundary through the supported runtime. Proceeding would still permit absent provider identity evidence to be treated as an exact match, turn malformed provider data into an uncontrolled abort, misstate execution failure as timeout, and present a stale historical FAIL as the changed tip's receipt. The durable cost of correction is small and localized: replace permissive defaulting with one fail-closed normalization/schema boundary, define total member-shape handling and terminal precedence, and record a closed current-tip non-pass without another provider request. Reset, narrowing, or stopping would discard a valid architecture without reducing this localized risk.
    recommendation: >-
      Return for one Captain-approved bounded correction. Structurally eliminate the repeated identity-matching failure shape: require every canonical scalar field to be present and equal before PASS or FAIL, normalize and validate the complete member population without exceptions, and apply terminal parent/member execution failure before deadline interpretation. Add adversarial cases for sparse identity, deletion of every required field, malformed member shapes, and failed-plus-deadline precedence; do not merely add more permissive defaults. Replace the repair-cycle Work Control entry with a closed exact-current-tip non-pass such as UNKNOWN(stale) referencing historical job 170, unless separate authority later permits confirmation; do not invoke RoboRev for this correction. Retain the proven Spacedock harness, package/adopted parity, authority limits, and one-PR topology, then rerun the focused and aggregate suites and dispatch fresh validation at the new exact head.
    route: return
    confidence: high
    dissent: >-
      The implementation report and green suites claim F1 and F2 closure, with every modeled line executed. F1 and the explicit mismatch subset are accepted, but the broader proceed claim is rejected because direct adversarial inputs reproduce a false PASS, two uncontrolled abort classes, incorrect failure precedence, and a non-canonical current-tip receipt. No material disagreement remains unresolved.
    disproof_condition: >-
      Change to proceed on a new exact candidate when one fail-closed schema boundary requires every canonical identity field, malformed or ambiguous member populations always produce a declared UNKNOWN without exception, terminal execution failure wins over deadline interpretation, the current-tip Work Control entry uses the closed mapping without another unauthorized provider request, the retained Spacedock transaction tests still prove one winner and loser refusal, and all focused and aggregate checks pass at a clean head bound to the current merge target.
    authority_boundary: >-
      Because this is the second consecutive rejection at the same validation gate, the Captain retains the continuation choice among the recommended bounded correction, reset, narrowing, or stop. Gate Authority keeps validation closed; the implementation owner may correct only after that route is accepted. Spacedock and its registered holder retain task and execution-state mutation authority. RoboRev remains evidence-only, and no actor gains provider invocation, push, Draft creation, Ready, merge, accepted-red, stage advancement, or terminalization authority from this report.
```
