---
title: Review the published-tag Science Officer runtime smoke
status: validation
source: Captain-approved issue #183 follow-up, 2026-08-10
product: kc-dev-flow
sprint: S1
design: required
id: jj5jbzp2tpyc7a6x78wnfqky
lane: main
started: 2026-08-10T22:03:08Z
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/kc-dev-flow-release-batch
pr: "#199"
---

## Problem

The published-tag cross-harness smoke is intentionally speculative until the first kc-dev-flow release containing its packaged schema and prompt can exercise the clean-installed Claude and Codex surfaces. Without a durable review point, the harness could remain permanently after its claimed value fails to materialize.

## Review contract

After the first GitHub Release containing the smoke assets, run the authenticated exact-tag release smoke and preserve its receipt. Keep the harness only if it produces installed-runtime evidence unavailable from the existing post-install and marketplace helpers; otherwise remove it.

The captain scheduled this review in `kc-dev-flow/S1` as the first item in the
single-release batch.

## End value

Release closeout can prove that the exact published kc-dev-flow tag installs and
invokes through clean Claude and Codex plugin state, and that both hosts return
the complete EM compatibility record for that tag's commit.

## Smallest route and reverse-recovery audit

- `scripts/marketplace-verify.sh` is `WORKING` for current-checkout Claude
  marketplace resolution, but it does not bind an exact tag, invoke Codex, or
  validate the EM report.
- `kc-plugin-forge/scripts/post-release-sync.sh:38-68` is `WORKING` for copying a
  clean `main` checkout after release, but it neither checks a tag nor invokes a
  host.
- The v2.1.0 one-off exact-tag probe is `WORKING` evidence that clean-installed
  Claude and Codex can both invoke the skill, but it is not a reusable release
  check.

Keep one release-only wrapper around those real host CLIs. A per-PR matrix, new
CI job, new auth store, or reimplementation of plugin installation is outside
the route. The mechanism is required by AC-1; the cheaper existing helpers are
insufficient because none observes all four missing boundaries together.

## Design determination

`required` — this introduces a release-closeout command and a fail-closed report
contract. It runs only after a tag exists and before local install sync.

## Acceptance criteria

**AC-1 — The smoke is bound to one published artifact.**

Verified by: an exact-tag clone, exact revision lookup, and digest equality for
both installed plugin trees in
`scripts/kc-dev-flow-published-tag-smoke.py:305-451`. Falsified by: a wrong
revision or changed installed tree makes the command fail.

**AC-2 — Both supported hosts exercise the installed skill.**

Verified by: isolated Claude and Codex plugin homes, operator authentication, and
one accepted EM report from each host at
`scripts/kc-dev-flow-published-tag-smoke.py:234-451`. Falsified by: a missing,
duplicate, or implicit plugin load, or either host failing to return one report.

**AC-3 — The compatibility record is structural and exact.**

Verified by: direct negative fixtures for missing, extra, duplicated, misplaced,
invalid-enum, mismatched-wrapper, and wrong-revision data at
`scripts/kc-dev-flow-contract-test.py:64-159`. Falsified by: any such fixture
being accepted.

**AC-4 — The check stays release-only and earns its maintenance cost.**

Verified by: the root release instructions place it after tag creation and before
local sync at `CLAUDE.md:47-54`, with no per-PR workflow entry. Falsified by:
wiring it into ordinary PR CI, or the first released run producing no evidence
beyond existing helpers.

## Test plan

Run the report fixtures without provider calls; run Claude plugin-isolation and
exact-tag install probes; run both hosts against one released tag; then run the
full kc-dev-flow contract, frontmatter, parity, marketplace, and link checks.

## Appetite and pre-mortem

One worker and one release-closeout command. Stop and re-cut if it needs a new
credential store, CI matrix, or provider abstraction. If this still fails after
release, the likely cause is that the wrapper validates its own files while one
host resolves a different installed plugin tree.

## Out of scope

Per-PR model calls, manual version edits, replacing marketplace verification or
post-release sync, and creating or merging a PR.

## Stage Report: ideation

- DONE: The captain scheduled the exact review obligation in `kc-dev-flow/S1`.
- DONE: Reverse recovery found two working but narrower helpers and one successful
  v2.1.0 experiment; one release-only dual-host wrapper is the smallest missing
  seam.
- DONE: AC-1 binds the requested tag, resolved revision, and both installed trees.
- DONE: AC-2 requires one isolated installed-skill invocation from each host.
- DONE: AC-3 rejects every malformed or wrong-revision report class directly.
- DONE: AC-4 keeps the command after release and outside ordinary PR CI.
- DONE: Fresh high-reasoning EM returned `narrow / high`: retain one
  release-closeout smoke, not a per-PR matrix. Multi-model review was not
  recommended.

### Summary

Proceed with one exact-tag, dual-host release-closeout smoke. Its first run from
a tag containing the command remains release evidence, not something local
validation can claim in advance.

## Stage Report: implementation

- DONE: Commit `c48a9e97f1614d80d8220ac4c80b4df993db09fb` adds the one
  release-closeout script, its direct report-contract fixtures, and the bounded
  root release instruction.
- DONE: Claude runs with plugin autoload disabled and must report exactly one
  explicit kc-dev-flow plugin at the expected path/version; Codex uses a clean
  temporary home that reuses only operator authentication.
- DONE: Both installed plugin trees digest-match the canonical exact-tag clone;
  the nested EM revision must equal the tag commit and every duplicated wrapper
  value must match.
- DONE: Direct fixtures reject malformed, incomplete, misplaced, duplicate,
  invalid-enum, wrapper-mismatch, and wrong-revision records before provider
  execution.
- DONE: Fresh stage-exit checks pass: kc-dev-flow contract, 40 skill
  frontmatters, version parity at 2.1.0, marketplace L0/L1/L2, state-prerequisite
  contract, Python compilation, and `git diff --check`.

### Summary

The implementation is the accepted release-only shape and is self-contained for
fresh validation. The next exact tag invocation remains a release-closeout step.

## Stage Report: validation

### TL;DR

Fresh Claude Opus high session `d4daa8b0-ea12-4c8f-9ccc-a086ae9a8edd`
reviewed exact head `c48a9e97f1614d80d8220ac4c80b4df993db09fb` over
`a024b254e236f521d8438d567ade36d779a52d11` and returned
`proceed / high / multi_model:not_needed`, with zero Material findings. This is
candidate-code validation; the first tag containing the command and its local
sync are still release-closeout evidence, so the task stays in `validation`.

### Per-AC verdicts

- **AC-1 PASS** — the requested canonical tag resolves to one commit and both
  installed trees must digest-match that checkout; a wrong revision/tree is
  fail-closed.
- **AC-2 PASS** — post-correction Claude isolation reported one explicit
  kc-dev-flow plugin at the expected path/version; Codex reuses only operator
  auth in a temporary home.
- **AC-3 PASS** — direct fixtures reject missing, extra, duplicate, misplaced,
  invalid-enum, mismatched-wrapper, and wrong-revision reports.
- **AC-4 PASS** — `CLAUDE.md` places the command after tag publication and
  before local sync and explicitly excludes per-PR gating.

### Evidence block

`Lenses:` Runtime/platform, contract/schema, correctness, auth isolation, and
delivery fired; all PASS with zero Material findings against exact head above.
No concurrency or persistent-resource surface exists: temporary directories and
subprocess failures are bounded and fail-closed. Would fail on an extra Claude
plugin, unequal installed tree, malformed record, or revision mismatch.

`Diff coverage:` coverage.py reports 39% aggregate for the full new script under
the repeatable local contract suite (99/239 statements; 100 branches, 10 partial).
The uncounted authenticated orchestration is covered by the prior dual-host
v2.1.0 invocation plus post-correction isolation/install probes and remains a
release-only exact-tag check, not a unit-test substitute.

`Adversarial:` PASS — malformed/incomplete/misplaced/duplicate/invalid-enum/
wrapper-mismatch/wrong-revision fixtures all fail; plugin-count and tree-digest
mismatches are explicit refusal paths. Would fail if any bad fixture exited 0.

`Cross-model:` not_needed — the exact-head EM found no contested, irreversible,
low-confidence, or unresolved call. No optional second model was requested.

`E2E:` PASS, bounded — the v2.1.0 exact-tag one-off invoked both clean-installed
hosts; post-correction probes on this commit observed `plugins_count=1` for
Claude and equal Claude/Codex installed trees. The first execution from a tag
that contains this command is intentionally deferred to release closeout.

`Origin re-observation:` PASS — Reported scenario: an exact published kc-dev-flow
tag installs and invokes through Claude and Codex | Originating runtime kind:
authenticated installed host CLIs | Re-observation artifact/revision: v2.1.0 tag
`a024b254e236f521d8438d567ade36d779a52d11` plus corrected wrapper commit
`c48a9e97f1614d80d8220ac4c80b4df993db09fb` | Equivalent-runtime rationale:
same host CLIs, canonical repository, tag resolver, plugin layouts, and operator
authentication; the correction probes isolate plugin state and bind tree bytes |
Falsifier kind: mutation | Result: both host invocations passed, one Claude plugin
was observed, and both installed trees matched the tag checkout.

### Engineering judgment

- `question:` Does the retained release-closeout smoke prove the accepted exact
  tag, dual-host, isolation, and report boundaries without excess mechanism?
- `revision:` `c48a9e97f1614d80d8220ac4c80b4df993db09fb` over
  `a024b254e236f521d8438d567ade36d779a52d11`.
- `adjudications:` the prior isolation, structural-parser, revision/tree-binding,
  and recovery-version findings are closed; no whole changed file or smoke
  mechanism is removable without losing an AC or falsifier.
- `risk_tradeoff:` retain one substantial authenticated release-only check to
  cover boundaries the cheaper marketplace and sync helpers do not observe;
  avoid the higher recurring cost of a per-PR model matrix.
- `recommendation/route/confidence:` proceed / proceed / high.
- `dissent:` empty. `multi_model:` not_needed.
- `disproof_condition:` change route on an extra Claude plugin, unequal installed
  tree, accepted malformed/wrong-revision report, or unmapped changed file.
- `authority_boundary:` advisory only; Captain, Spacedock, GitHub checks, and
  release-please retain scope, state, PR, merge, tag, release, and sync authority.

### Exact-head PR rebind

Fresh PR-level Claude Opus high session
`53ca4a4a-e114-4a4b-9412-ae0fbb0c0e0a` rebound AC-1, AC-2, AC-3, and AC-4 to
`454507f7ba56ce79ca0414f1964af4e59126eea5`. The intervening delta changes no
smoke script, parser fixture, `CLAUDE.md` release placement, workflow file, or
host invocation surface; the new kernel rule preserves the pending smoke and
leaves its keep-or-remove decision captain-owned. Hosted CI is green at that
exact head. Verdict remains `proceed / high`, with zero Material findings; the
first containing-tag invocation remains release-closeout evidence.

## Exact-head candidate validation — `76614da671eaf29e9bed2147aae4e4f9f390af84`

Fresh Claude Opus high session `317c8a98-df85-4baa-8a48-c780d51e55b9`
returned `proceed / high`, AC 4/4 at candidate scope, zero Material findings,
and `multi_model: not_needed`. The same session corrected its output envelope
without changing evidence or verdict.

- `Lenses:` release placement, installed-tree binding, host isolation, report
  schema, and delivery sequencing pass.
- `Diff coverage:` all smoke paths map to AC-1 through AC-4; the subtractive
  correction changes no host invocation or release placement.
- `Adversarial:` malformed, duplicate, mismatched, and wrong-revision records
  fail; installed-tree and plugin-count mismatches remain refusal paths.
- `Cross-model:` not_needed — no contested, irreversible, low-confidence, or
  unresolved call remains.
- `E2E:` bounded PASS — prior v2.1.0 same-kind Claude/Codex host probes plus
  current exact-head contract, tree-digest, and isolation instruments.
- `Origin re-observation:` bounded PASS — Reported scenario: exact published
  kc-dev-flow tag installs and invokes through Claude and Codex | Originating
  runtime kind: authenticated installed host CLIs | Re-observation
  artifact/revision: v2.1.0 host probes plus candidate
  `76614da671eaf29e9bed2147aae4e4f9f390af84` | Equivalent-runtime rationale:
  same host CLIs, tag resolver, plugin layouts, operator authentication, and
  report contract | Falsifier kind: mutation | Result: prior host probes and
  current refusal instruments pass; the first containing-tag run remains open.

The sequencing boundary is intentional: release-please must create the first tag
that contains this command before its closeout smoke can run. Do not terminalize
this task until that tag records a keep-or-remove disposition.
