---
title: Prove one agent-native skill evaluation boundary
source: comment-retention-discipline UNKNOWN receipts, 2026-08-15 and Captain continuation on 2026-08-16
product: kc-dev-flow
sprint:
status: implementation
design: required
lane: main
id: 2yrthe1tx7v4zmawgs1bqpkx
started: 2026-08-16T06:45:51Z
worktree: .worktrees/spacedock-ensign-agent-native-skill-eval-boundary
---

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v1
  selected: poc-exploration
  recommended: poc-exploration
  basis: >-
    Repository maintainers need one disposable experiment to prove the
    agent-native loader and provider-trace boundary. It creates no production
    state, external mutation, compatibility promise, or continuing operation.
  obligations:
    architecture:
      - Reuse the active harness and installed skill boundary; add no permanent evaluator surface.
    implementation:
      - Build only the disposable controller and opaque arm material needed for one real journey.
      - Keep hidden mapping and scoring outside every measured worker input.
    testing:
      - Prove one ordinary worker reads the exact installed skill and vendored kernel.
      - Bind its response to provider-native tool evidence and exact input digests.
      - Record cleanup and every claim the POC leaves unproved.
  invariant_sources:
    - docs/dev/_mods/kernel.md
    - docs/dev/_mods/work-control-profile.md
    - kc-safehouse
    - comment-retention-discipline UNKNOWN receipts
  scope_boundary: >-
    No reusable runner, generalized scoring framework, cross-host support,
    recurring model gate, product policy change, release, or sprint admission.
  promote_when:
    - A second skill or workflow needs the same retained evaluation path.
    - The controller or artifacts must persist beyond this experiment.
    - Cross-host, release, support, or compatibility obligations enter scope.
  decision:
    authority: Captain Kent
    at: 2026-08-16T06:47:39Z
```

## Problem

The comment-retention dogfood could not produce countable evidence. Stage-only
capture omitted the changed kernel; the first ordinary-worker fixtures leaked
their hidden class and rubric; and the isolated correction caused nested Codex
to reject every filesystem read before a kernel digest could be retained.

Prove one real agent-native evaluation journey that lets an ordinary worker load
the exact installed skill and vendored kernel, keeps arm mapping and scoring
outside the model-readable surface, and exports provider-native tool evidence
that binds the response to exact input bytes. Do not build a generalized eval
platform before this boundary works.

No provider calls, permanent harness, comment-policy change, or sprint admission
is authorized by this seed. At ideation, select the proportional work profile
through the active harness Ask UI when available; plain chat is fallback only.

## Ideation design

### Bound decision and live surfaces

Design one disposable local POC at `origin/main`
`54594f1871a1a693528f8bdbbe132010ea4fb6db`. The active host is Conductor
0.81.0 on local macOS, Spacedock 0.26.0 contract 3, Codex CLI 0.147.0, and
Safehouse 0.9.0. The installed `continue-dev-flow` 2.5.0 skill is 4,370 bytes
with SHA-256 `28c358633fd7a0d076c4175e783e1a872607627f814192b06bc51eb9877b959f`;
the 21,918-byte adopted kernel and canonical source both have SHA-256
`300149e43cf2bc3c548fbdae750a90d305869280af5517436932741047210473`.

The two prior `UNKNOWN` receipts remain controlling negative evidence. The
first stopped after three baseline responses because fixture paths and the
live entity leaked the hidden classes, candidate, and rubric, while its outer
event capture lacked matching per-response kernel-digest evidence. The
Captain-approved correction isolated six opaque shadows, but nested Codex
read-only sandbox setup failed before every filesystem command with
`sandbox_apply: Operation not permitted`; all six responses were `BLOCKED`,
with no kernel read in the retained traces. Those nine calls authorize neither
a retry nor a behavioral conclusion.

### Reverse recovery and subtractive result

- Conductor's native child-agent surface is `WORKING` for orchestration but has
  no exposed raw child tool-event export in this harness. Completion messages
  and its concise transcript API are summaries, not provider-native read
  evidence; the API is also unavailable here without a user API token.
- `review-ablation.sh` is `WORKING_UNIT_UNPROVEN` for its own Claude PR-review
  experiment. It invokes a Claude plugin tree and accepts an agent-written
  findings receipt; its own comments say this is not filesystem isolation. It
  cannot prove a Codex-installed `continue-dev-flow` kernel read without
  becoming a second evaluator.
- Codex CLI 0.147.0 already supplies the missing observation seam:
  `codex exec --json` emits JSONL events, and retained Codex session JSONL on
  this host contains provider tool-call and tool-output items. This is the only
  recovered surface proposed for the POC.

Subtractive result: add no runner, schema, registry, evaluator, or product
file. Use disposable shell orchestration and retain the provider JSONL only
long enough to validate and hash it. If that existing export cannot bind both
complete reads, the answer is no-go rather than another surface.

### Fastest path and one journey

1. Outside the measured worker's readable boundary, create one opaque temporary
   controller directory and one standalone opaque shadow workflow. Copy the
   exact pinned workflow bytes into the shadow; keep arm identity, expected
   digests, validation predicates, and any fixture classification only in the
   controller directory.
2. Before spending, generate and hash an outer Safehouse policy. From the
   shadow, prove direct and symlink reads of the controller, live product,
   state checkout, and any alternate arm are denied. Grant only the shadow and
   the exact installed kc-dev-flow cache needed for skill discovery.
3. Launch exactly one ordinary worker through `codex exec --json` inside that
   outer Safehouse. Disable Codex's inner approvals/sandbox because Safehouse is
   the containing sandbox; this is the documented externally-sandboxed use of
   the bypass and removes the already-observed nested-sandbox failure. Give the
   worker only a normal request to invoke `kc-dev-flow:continue-dev-flow` and
   identify the next authorized action without mutation.
4. The outer controller, not the worker, parses the retained JSONL. Count the
   journey only if provider tool-call/output events reconstruct the complete
   installed skill bytes and complete vendored kernel bytes and match the
   pinned hashes. A final answer, claimed digest, child summary, command string
   without matching output, truncated output, or session-id assertion does not
   count.
5. Hash the provider JSONL and a minimal external manifest, record the result,
   then remove shadow, controller, trace, and any Codex session created for the
   POC. Do not run a baseline/treatment comparison or edit comment policy.

## Acceptance criteria

**AC-1 — One real agent-native loader journey is trace-bound.** `Verified by:`
one retained `codex exec --json` event stream whose provider tool-call/output
items reconstruct and hash-match the complete installed skill and complete
shadow-vendored kernel. `Falsifier:` either file is absent, incomplete,
truncated, read only through a self-authored claim, or hashes differently.

**AC-2 — Hidden authority stays outside worker-readable input.** `Verified by:`
pre-call Safehouse direct and symlink denial probes plus an external manifest
showing that the worker received only the opaque shadow and normal continuation
request. `Falsifier:` the worker can read the controller, mapping, validation
predicates, live task/state, product tree, or alternate arm by any tested path.

**AC-3 — The POC stops at the smallest useful claim.** `Verified by:` one
provider response at most, no retry, no A/B behavioral verdict, no product or
workflow edit, no retained runner/schema, and cleanup of every disposable
artifact after hashing. `Falsifier:` a second response is requested, a comment
behavior conclusion is recorded, or a reusable surface/product diff remains.

**AC-4 — Failure is an explicit no-go.** `Verified by:` missing exact trace
binding, sandbox denial, timeout, schema ambiguity, output truncation, or
cleanup failure returns `UNKNOWN/no-go` without substituting prose evidence.
`Falsifier:` any such condition is presented as a pass or used to authorize a
new comment-policy experiment.

### Compute, cleanup, and residuals

Future compute is capped at one `gpt-5.6-terra` high-reasoning response and five
minutes of model wall clock, with no retry. Preflight and cleanup are local and
must complete outside that clock; if the call has not produced terminal JSONL
by the cap, terminate it and record `UNKNOWN/no-go`.

This POC will not prove comment-retention benefit, A/B causality, deterministic
model compliance, another provider or skill loader, Conductor cloud behavior,
cross-host support, production reliability, or that all provider events are
retained under every failure. Promotion is required before any reusable runner,
second journey, second provider response, or product-policy experiment.

### Pre-mortem

The likeliest failure is that `--json` retains a command event but truncates or
normalizes the 21,918-byte kernel output, so an apparently successful worker
still cannot bind exact bytes. That is a useful no-go: it names trace retention,
not instruction prose, as the smallest missing capability.

## Fresh EM verdict

```yaml
science_officer_em_upward_report:
  em_judgment: >-
    Proceed with the single disposable POC. It is one reversible value surface,
    uses recovered agent-native and provider-trace seams, directly targets the
    two prior UNKNOWN causes, and fails closed without creating a reusable
    evaluator or authorizing a behavioral experiment.
  evidence_synthesis: >-
    At state commit b42a99a772164fe26e6db33803409faf42d26705 and governing
    product revision 54594f1871a1a693528f8bdbbe132010ea4fb6db, the installed
    continue-dev-flow 2.5.0 skill is 4,370 bytes with SHA-256
    28c358633fd7a0d076c4175e783e1a872607627f814192b06bc51eb9877b959f,
    while the canonical and vendored kernels are 21,918 bytes with SHA-256
    300149e43cf2bc3c548fbdae750a90d305869280af5517436932741047210473.
    Codex 0.147.0 exposes JSONL execution events and reserves sandbox bypass for
    externally sandboxed environments; Safehouse 0.9.0 exposes exact grants.
    Whether provider events retain complete bytes remains the POC's unresolved
    claim; no behavioral or cross-provider conclusion follows.
  risk_tradeoff_call: >-
    The benefit is one countable answer about whether the existing loader and
    trace support later evaluation. The sole response may still produce an
    unreadable, truncated, ambiguous, or blocked trace; preflight probes, exact
    hashes, a five-minute cap, no retry, UNKNOWN/no-go, and cleanup contain that
    risk. No durable surface remains. Stopping now avoids the small spend but
    leaves the decisive observation boundary untested.
  recommendation: >-
    Accept the design. If Captain Kent separately schedules it and authorizes
    spend, execute exactly one gpt-5.6-terra high journey under outer Safehouse;
    count it only when provider-native evidence reconstructs both pinned files.
  route: proceed
  confidence: high
  multi_model: not_needed
  fo_boundary: ""
  engineering_judgment:
    question: >-
      Should the pinned ideation advance as one disposable agent-native
      loader/trace POC after nine invalid or blocked prior calls?
    revision: >-
      state b42a99a772164fe26e6db33803409faf42d26705; product
      54594f1871a1a693528f8bdbbe132010ea4fb6db
    evidence_synthesis: >-
      At state commit b42a99a772164fe26e6db33803409faf42d26705 and governing
      product revision 54594f1871a1a693528f8bdbbe132010ea4fb6db, the installed
      continue-dev-flow 2.5.0 skill is 4,370 bytes with SHA-256
      28c358633fd7a0d076c4175e783e1a872607627f814192b06bc51eb9877b959f,
      while the canonical and vendored kernels are 21,918 bytes with SHA-256
      300149e43cf2bc3c548fbdae750a90d305869280af5517436932741047210473.
      Codex 0.147.0 exposes JSONL execution events and reserves sandbox bypass for
      externally sandboxed environments; Safehouse 0.9.0 exposes exact grants.
      Whether provider events retain complete bytes remains the POC's unresolved
      claim; no behavioral or cross-provider conclusion follows.
    adjudications:
      - finding: prior-receipts-establish-worker-behavior
        disposition: unsupported
        basis: >-
          The first three calls leaked hidden authority and lacked matching
          provenance; the next six executed no reads. They prove failure shapes only.
      - finding: exact-skill-and-kernel-inputs-are-bindable
        disposition: supported
        basis: >-
          Direct inspection confirmed byte counts and hashes; AC-1 rejects
          claims, truncation, incomplete output, and mismatches.
      - finding: outer-safehouse-removes-the-known-nested-sandbox-conflict
        disposition: supported
        basis: >-
          Codex documents bypass for external containment and Safehouse supplies
          that exact-grant boundary plus pre-spend denial probes.
      - finding: provider-trace-retains-complete-file-output
        disposition: unresolved
        basis: >-
          Structured execution evidence exists, but complete untruncated kernel
          retention is unproved and is precisely the bounded POC claim.
      - finding: proposed-scope-fits-one-poc-iteration
        disposition: supported
        basis: >-
          This is one value surface, one journey, one capped response, no retry,
          and no surviving evaluator responsibility.
    risk_tradeoff: >-
      The benefit is one countable answer about whether the existing loader and
      trace support later evaluation. The sole response may still produce an
      unreadable, truncated, ambiguous, or blocked trace; preflight probes, exact
      hashes, a five-minute cap, no retry, UNKNOWN/no-go, and cleanup contain that
      risk. No durable surface remains. Stopping now avoids the small spend but
      leaves the decisive observation boundary untested.
    recommendation: >-
      Accept the design. If Captain Kent separately schedules it and authorizes
      spend, execute exactly one gpt-5.6-terra high journey under outer Safehouse;
      count it only when provider-native evidence reconstructs both pinned files.
    route: proceed
    confidence: high
    dissent: ""
    disproof_condition: >-
      Return or block if preflight cannot prove the required denials, pinned
      hashes drift, the one journey cannot launch inside the envelope, or its
      provider events cannot reconstruct both complete file outputs.
    authority_boundary: >-
      Captain Kent retains scope, scheduling, sprint admission, and spend;
      Gate Authority retains transition and verdict; work-item authority retains
      acceptance mutation. This report authorizes no provider call, retry,
      product edit, stage advancement, merge, archive, or closeout.
```

## Stage Report: ideation

- DONE: Pin the live origin/main, active Conductor/Spacedock/Codex harness
  surfaces, and the two comment-retention UNKNOWN receipts; identify the exact
  nested-sandbox and provenance failure without running provider experiments.
  Bound product `54594f18`, tool versions/hashes, leakage/provenance failure,
  and six `sandbox_apply: Operation not permitted` read failures.
- DONE: Determine whether an existing agent-native invocation can expose
  retained provider-native tool evidence for a worker that reads the exact
  installed continue-dev-flow skill and vendored kernel while hidden arm
  mapping and scoring remain unreadable.
  Recovered `codex exec --json`; Conductor summaries and agent-written receipts
  do not qualify, and exact full-byte retention remains AC-1's falsifiable claim.
- DONE: Recover the smallest disposable one-journey design; prove why existing
  surfaces cannot be reused before proposing any new code, runner, schema, or
  framework.
  Outer Safehouse plus inner Codex bypass reuses existing seams and leaves no
  new surface; any missing exact trace binding is no-go.
- DONE: Define value-level ACs, falsifiers, cleanup, explicit unproved claims,
  a bounded future compute envelope, and a no-go route when exact trace binding
  is unavailable.
  AC-1 through AC-4 cap work at one response/five minutes/no retry and exclude
  behavioral, cross-host, generalized, and production claims.
- DONE: Append and sync a concise ideation report. Obtain one fresh EM judgment
  under the local gate; do not run the POC, edit product files, schedule a
  sprint, or create another tracker.
  Fresh EM at state `b42a99a7` returned `proceed/high`, multi-model not needed;
  this stage made only state-file edits and no provider experiment.

### Summary

Ideation recovered one viable existing boundary and deliberately stopped before
spend: outer Safehouse contains one `codex exec --json` worker while external
validation requires exact full-file provider events. EM recommends proceeding;
Captain and Gate Authority retain scheduling, spend, and transition decisions.

## Stage Report: implementation — UNKNOWN/no-go, no product change

- DONE: Re-pinned the exact inputs before setup. Product HEAD and fresh
  `origin/main` were both `54594f1871a1a693528f8bdbbe132010ea4fb6db`;
  Codex CLI was 0.147.0, Safehouse was 0.9.0, and Spacedock was 0.26.0
  contract 3. The 4,370-byte installed skill and both 21,918-byte kernels
  retained the accepted SHA-256 values.
- DONE: Prepared one disposable opaque shadow and external controller without a
  product edit. The generated outer Safehouse policy had SHA-256
  `4ec70de2d8dc8f49042ac0c3707b48674fec8548db381e8ee01a93ef4bc4a4f7`,
  reported no common-Git or linked-worktree grants, and passed 12/12 pre-spend
  probes: the shadow README/kernel and exact installed skill were readable,
  while direct and symlink reads of controller, live product, shared state, and
  alternate input plus a non-required product sibling were denied. All probe
  symlinks were removed before launch.
- FAILED: The one authorized launch attempt did not reach the provider.
  Safehouse regenerated the byte-identical policy, then its sanitized execution
  environment returned `env: codex: No such file or directory` with exit 127.
  It ran from `2026-08-16T07:09:37Z` to `2026-08-16T07:09:39Z`; the provider
  JSONL was empty. The no-retry slot is exhausted, so no second launch was made.
- FAILED: External trace validation found zero provider tool-call/output events.
  It therefore cannot reconstruct either complete file or satisfy AC-1; under
  AC-4 the result is `UNKNOWN/no-go`, not a loader, trace, or comment-behavior
  pass.
- DONE: Hashed a 926-byte minimal receipt as
  `8e4133e11bb462e1c30637809e0bbee05658a314652e34fb57d6b19f97b8b960`.
  The empty JSONL hash was
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`;
  stderr hash was
  `b8a5a0e719eb890cab5eb5620a3a3656afcca098087746fe92607a0612bf5cae`.
  Removed every controller, shadow, alternate-input, policy, trace, prompt,
  receipt, and path-marker artifact. The product worktree remains clean at the
  exact origin/main revision with no runner, schema, commit, or PR.

Route: `return to Captain; the one-response POC ended UNKNOWN/no-go`.

### Summary

Containment was proven before launch, but the existing Safehouse-to-Codex
execution seam failed before provider spend because sanitized PATH resolution
could not find `codex`. No countable loader evidence exists, no retry or product
claim was substituted, and cleanup left no durable experiment surface.

## Stage Report: implementation (bounded launch correction) — UNKNOWN/no-go

- DONE: Recreated the same disposable opaque shadow/controller at exact product
  and `origin/main` revision
  `54594f1871a1a693528f8bdbbe132010ea4fb6db`. The only launch-resolution
  change was a read-only grant for the fixed native Codex vendor directory and
  direct invocation of its binary; the binary SHA-256 was
  `19c4f144c5226a9f17c58e6f0fa854843b0f77a6eb420f40e2745a12f10f5d37`.
- DONE: The corrected policy SHA-256 was
  `2439e477385dcf93fed8ee5884da57bdaba66843385c6f049247be24e6afe138`.
  It retained no common-Git or linked-worktree grants and passed 14/14 local
  probes: prior direct/symlink denials remained, required shadow/skill/binary
  reads succeeded, and the exact native binary returned `codex-cli 0.147.0`
  inside that policy. The launch-regenerated policy was byte-identical.
- DONE: Ran the one Captain-authorized `gpt-5.6-terra` high response with no
  retry. It terminated exit 0 in 112 seconds, from
  `2026-08-16T08:14:39Z` through `2026-08-16T08:16:31Z`, producing 29 JSONL
  events and 11 completed command events.
- FAILED: Exact external reconstruction found the full 21,918-byte vendored
  kernel but not the full 4,370-byte installed skill. The worker's first command
  requested the skill before later denied paths, but its retained aggregated
  output contained only the later denial messages. A command string or inferred
  read does not satisfy AC-1, so the trace is not countable.
- FAILED: The provider trace also showed a successful read from global
  `~/.codex/memories/MEMORY.md` through Safehouse's automatically selected
  Codex profile. Controller, live product, shared state, and alternate inputs
  remained denied, but the literal AC-2 claim that only the opaque shadow and
  exact skill bytes were readable is false for this policy.
- DONE: Hashed the 1,274-byte minimal receipt as
  `dfa013980868f0372b11497e4e168bc59fadb6dc5edf216810a7d98a9a4016a9`;
  provider JSONL SHA-256 was
  `8135ebf11a81cf293145ba3d3a6756f7c737214c6be91fed298267f971705471`
  and stderr SHA-256 was
  `a09e6fb512b21beca1698f57610a5f0e7dcb000f93a875b2527fcec0ff03bfb2`.
  The ephemeral nested thread retained no session file. Removed every shadow,
  controller, alternate-input, policy, prompt, trace, receipt, and path marker;
  the product worktree remains clean and exact with no runner, schema, commit,
  PR, or behavioral claim.

Route: `return to Captain; corrected launch exhausted, UNKNOWN/no-go`.

### Summary

The fixed native binary solved launch resolution and proved that JSONL can
retain one complete kernel read, but it did not retain the complete installed
skill read and the selected Codex profile exposed unrelated global memory.
Therefore the existing boundary still cannot produce the promised isolated,
countable loader provenance; the correction is exhausted without product work.
