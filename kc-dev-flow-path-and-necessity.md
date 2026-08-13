---
title: "kc-dev-flow: correct mod adoption path and enforce mechanism necessity"
source: "Captain directive `修 bug + 183`, GitHub issue #183, 2026-08-10"
product: kc-dev-flow
sprint: S2
design: required
id: 9f63nm17bntn0ts7k9b1nm9c
status: implementation
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/fix-kc-dev-flow-path-necessity
---

## Problem

The canonical reverse-recovery mod tells adopters to copy it into
`docs/ship-flow/_mods/`, although kc-dev-flow binds mods under each adopted
workflow's own `_mods/` directory. Separately, kernel's mechanism-necessity rule
has no local rejection predicate, so a new control can pass ideation without
naming the AC it serves, the simpler alternative, or an escaped defect.

The captain authorized this bounded repair together with issue #183. The
published-tag smoke review remains a separate unscheduled follow-up.

## End value

An adopter is directed to the selected workflow's local `_mods/` directory,
and this repository's ideation gate refuses a proposed control mechanism until
its necessity is reviewable. Speculative controls also leave a dated removal
review in the existing work-item authority.

## Scope

Two policy surfaces:

1. Correct the reverse-recovery mod's portable adoption instruction in the
   canonical and self-adopted copies, with one semantic regression assertion.
2. Add one local ideation rejection predicate for gates, checks, harnesses,
   automations, and registries. Reuse backlog seeds for speculative review.

No new registry, script, CI job, required context, kernel clause, or change to
the separate published-tag smoke review is in scope.

## Reverse-recovery audit

Against `origin/main` at `bd81be0081911639e5930be896eea5bb3ba23bb5`:

| Layer | Classification | Need | Evidence |
|---|---|---|---|
| Portable mechanism-necessity rule | WORKING_UNIT_UNPROVEN | REQUIRED | `kc-dev-flow/references/kernel.md` requires criterion, alternative, and insufficiency, but local ideation has no refusal predicate. |
| Local ideation gate | EXISTS_BROKEN | REQUIRED | `docs/dev/README.md` already owns local judgment; issue #183 records #178 passing without a necessity record. |
| Existing absolutes registry/check | WORKING_UNIT_UNPROVEN | REQUIRED | `scripts/kc-dev-flow-contract-test.py` invokes `absolutes-check.py`; required CI invokes the contract test. Issue #183's unwired premise is stale. |
| Work-item authority | WORKING | REQUIRED | Spacedock backlog already holds `kc-dev-flow-published-tag-smoke-review.md` as a dated review seed pattern. |
| Mod distribution path | EXISTS_BROKEN | REQUIRED | `reverse-recovery-audit.md` hard-codes `docs/ship-flow/_mods/`; `continue-dev-flow` reads only the adopted workflow's named local `_mods/`. |

No greenfield layer is required. The cheapest compatible seam is the existing
ideation gate plus the existing work-item authority.

## Options and decision

- **Take:** add one ideation rejection predicate and require a referenced
  backlog review seed only for speculative controls.
- **Do not take:** issue #183's proposed second content-hash registry and CI
  wiring. The cited wiring gap has already been closed, and another registry
  would duplicate the gate and work-item authorities.
- **Do not take:** a text-presence assertion for the ideation wording. Kernel
  says a text match cannot close a behavioral gate; validation will exercise a
  missing and a complete necessity record through a fresh reviewer instead.

Fastest path and smallest cut are the same: one local gate clause, one portable
path correction, and one semantic regression assertion in the existing suite.

## Necessity records

**Ideation refusal predicate**

- `Criterion:` AC-2.
- `Alternative:` leave the kernel rule as guidance; insufficient because #178
  passed the workflow without any of its three required facts.
- `Escape:` #178 would have been returned unread because it named no criterion,
  simpler alternative, or past escape/speculative review.

**Adoption-path regression assertion**

- `Criterion:` AC-1.
- `Alternative:` change only the prose; insufficient because byte parity can
  keep two copies identically wrong, as the current defect demonstrates.
- `Escape:` mutate the corrected header back to `docs/ship-flow/_mods/`; the
  existing contract suite must fail before distribution.

## Design determination

`required` — this changes the local ideation gate contract. The accepted shape
is a necessity record with `Criterion`, `Alternative`, and `Escape`. `Escape`
names a past defect proved by mutation; when none exists it instead records
`speculative until YYYY-MM-DD; review <work-item ref>`, and removal is the
default at that review.

## Acceptance criteria

**AC-1 — Adoption path is workflow-local.**

The canonical and self-adopted reverse-recovery mods direct adopters to the
adopted workflow's `_mods/reverse-recovery-audit.md`, carry version `0.2.1`, and
remain byte-identical. Verified by: a RED-before-GREEN assertion in
`scripts/kc-dev-flow-contract-test.py`, the full contract test, and the
absolutes registry check it invokes.

**AC-2 — Necessity can stop ideation.**

A proposed control mechanism missing any required necessity fact is returned
unread; a complete past-escape record passes accounting; a speculative record
also requires a date and work-item reference. Verified by: a fresh-context
Claude Opus high exercise over three adversarial ideation packets, naming the
exact changed revision and the result that would fail the exercise.

**AC-3 — No parallel enforcement system is added.**

The diff adds no mechanism registry, new executable, workflow step, or required
context. Verified by: exact diff classification against `origin/main`, live
branch-protection read, and the existing version-parity/contract suites.

## Test plan

1. Add an assertion that the header contains the exact workflow-relative
   backticked destination `_mods/reverse-recovery-audit.md`; run the scoped
   contract test and expect RED on the current ship-flow-prefixed path.
2. Correct and version both copies without updating the absolutes registry;
   rerun and expect the existing registry check to RED on the changed block.
3. Update the existing absolutes registry and rerun the contract test: expected
   GREEN.
4. Exercise the ideation clause with #178's actual incomplete proposal, a
   past-escape record, and a speculative record through fresh Claude Opus high.
5. Run the full contract and version-parity suites once at stage exit.

E2E skip: this is a docs/policy-only task. Its behavioral proof is the
fresh-reviewer gate exercise; no product runtime or external consumer report
originated the accepted problem.

## Appetite and dispatch

One worker session, 45 minutes; stop and re-cut beyond 70 minutes or if the
change needs a new script, registry, CI step, or kernel edit. No spike needed:
the existing ideation gate, work-item authority, contract test, and required CI
path are live and were read directly.

## Pre-mortem

If this ships exactly per spec and still fails, the likely cause is criteria
that pass without delivering value: a reviewer may echo the required fields
without actually refusing an incomplete packet.

## Measurement

- Baseline: issue #183 records one control (#178) that passed without a
  necessity record.
- Target: 3/3 adversarial packets receive their specified disposition.

## Doc diff

- Reverse-recovery header: replace the ship-flow-specific destination with the
  adopted workflow's local `_mods/` destination.
- Ideation stage: add the necessity-record refusal predicate and speculative
  review-seed requirement.

## Out of scope

Changing kernel policy, adding a registry or CI step, reopening issue #178,
executing the published-tag smoke review, release version edits, and merge.

## Stage Report: ideation

- DONE: Reproduce both defects and bind their causes to `origin/main`
  `bd81be0081911639e5930be896eea5bb3ba23bb5`.
  The path came from the original ship-flow-specific copy; byte parity preserves
  the error. The mechanism rule exists in kernel, but local ideation has no
  refusal predicate.
- DONE: Recheck issue #183's enforcement premise.
  `scripts/kc-dev-flow-contract-test.py` invokes `absolutes-check.py`, required
  CI invokes that contract test, and live branch protection requires the job
  context. A second registry or CI step is therefore rejected.
- DONE: Select the smallest sufficient route.
  Reuse the ideation gate and work-item authority, correct the portable path,
  and add one assertion to the existing contract suite. No new authority or
  executable surface is introduced.
- DONE: Define falsifiable ACs and the control mechanisms' own necessity
  records.
  AC-1 has a mutation RED/GREEN; AC-2 has three fresh-reviewer packets; AC-3 has
  an exact diff and live required-context read.
- DONE: Complete ideation discipline.
  Captain-authored scope, design decision, reverse-recovery audit, appetite and
  tolerance, cheap path, rejected alternatives, doc diff, one-worker sizing,
  E2E skip reason, and pre-mortem are recorded.
- DONE: Obtain fresh-context EM judgment.
  Claude Opus high reviewed the exact `bd81be0` plan and returned `proceed`
  with confidence 0.82. It found the five-file diff minimal and required three
  zero-surface refinements: assert presence of the correct relative path,
  preserve the stale-registry intermediate RED, and use #178's actual proposal
  as the incomplete packet. All three are incorporated above.

### Summary

Proceed with the existing ideation gate as the enforcement point. A control
mechanism must name `Criterion`, `Alternative`, and `Escape`; speculative
controls also name a date and backlog review reference. Correct the mod's
workflow-local adoption path and protect that distribution contract in the
existing suite.

## Stage Report: implementation

- DONE: AC-1 RED — add the workflow-relative destination assertion before
  changing production policy.
  `scripts/kc-dev-flow-contract-test.py` exited 1 on `bd81be0` with
  `reverse-recovery adoption path is not workflow-relative`. The one new
  assertion is the behavior claim and appeared as the failure.
- DONE: AC-1 wiring RED — correct both mod copies and bump policy version while
  deliberately leaving the existing registry stale.
  The same suite exited 1 at `absolutes-check`: the new `d004c8dad2f2ac69`
  block was undispositioned and old `969c6d525879f6a9` matched no block. This
  proves the checker is executed through the contract suite rather than merely
  present in source.
- DONE: AC-1 GREEN — replace the one existing registry disposition and rerun.
  `scripts/kc-dev-flow-contract-test.py` exited 0 with
  `kc-dev-flow contract: PASS`; `cmp` confirms the canonical and self-adopted
  copies are byte-identical, both at policy version `0.2.1`.
- DONE: AC-2 implementation — add one rejection predicate to the existing
  ideation stage.
  It requires `Criterion`, `Alternative`, and mutation-proved `Escape`; a
  speculative escape additionally requires a date and resolvable backlog seed.
  No text-presence assertion was added for this behavioral gate.
- DONE: AC-3 scope and stage-exit checks.
  `git diff --check`, the full kc-dev-flow contract suite, and
  `scripts/version-parity-check.sh` pass. Exact diff: five declared files,
  +26/-7, all mapped to AC-1/2/3; zero manifest, marketplace, workflow, kernel,
  new executable, or new registry files. Plugin manifests remain 2.0.0 in
  parity; release-please owns the next package release.
- DONE: CI delta and old-arrangement audit.
  Required CI already runs the edited contract suite; the new assertion adds no
  subprocess and no material runtime. Before the fix, the stale path appeared
  only in the canonical and self-adopted copies; both now use the same
  workflow-relative destination.

### Summary

Two REDs proved the semantic path defect and the existing registry wiring;
GREEN restored both. The product diff remains the five-file shape accepted by
the ideation EM and is self-contained for fresh validation.

## Stage Report: validation

### TL;DR

Fresh Claude Opus high read diff artifact
`5adcec6cbb0eb3ee965b7627fec90550d7a45606acd44995324fc70010bd4b1f`
against `bd81be0` and returned `proceed`: AC-1..AC-3 PASS, all four adversarial
packet dispositions match, and there are zero Material findings. This is a
passed candidate-bytes review, not a delivery verdict; committing will create a
new revision and require re-binding before PR approval.

### Per-AC verdicts

- **AC-1 PASS** — both copies contain the workflow-relative destination and
  version `0.2.1`; contract RED caught the old path, the stale-registry
  intermediate RED proved absolutes wiring, final contract GREEN and `cmp`
  proved the accepted bytes.
  Verified by: `scripts/kc-dev-flow-contract-test.py:516-544`,
  `kc-dev-flow/references/reverse-recovery-audit.md:1-10`, and the two recorded
  RED exits plus final PASS.
- **AC-2 PASS** — fresh Opus dispositions: `P1 RETURN UNREAD` missing all three
  labeled lines; `P2 PASS accounting`; `P3 PASS accounting`; `P3-no-ref RETURN
  UNREAD` for the missing resolvable review reference.
  Verified by: fresh Opus session `e30e64f7-448f-4253-a4b2-53e0914c3f5e`
  against diff hash `5adcec6c` and `docs/dev/README.md:671-682`.
- **AC-3 PASS** — exact five-file +26/-7 diff adds no new file, executable,
  registry, workflow step, required context, manifest, or kernel edit.
  Verified by: `git diff --name-only origin/main`, live branch-protection
  receipt, `scripts/version-parity-check.sh`, and the exact diff hash above.

### Evidence block

`Lenses:` Exact diff hash above. Correctness PASS, 0 findings: Opus exercised
all necessity packet branches and adjudicated the path assertion against both
REDs. Manifest/back-compat PASS, 0 findings: policy version is `0.2.1`, existing
absolutes disposition is refreshed, and the standing contract at
`scripts/kc-dev-flow-contract-test.py:536-544` byte-compares canonical and
self-adopted references. Security, silent-failure, type-design, concurrency,
and resource-lifecycle did not fire: the diff touches one local policy clause,
one reference header in two distribution positions, one registry disposition,
and one synchronous assertion; no auth, error fallback, type, async/shared
state, process, handle, or growth surface. Would have failed on a wrong packet
disposition, a sixth path, or non-identical reference bytes.

`Diff coverage:` PASS — Python `trace` on the GREEN suite reported 267
executable lines, 99.6% file coverage, and positive counts for every added line
at `scripts/kc-dev-flow-contract-test.py:516-521`; changed executable-line
coverage is 100%. Would have failed on any added executable line with count 0.

`Adversarial:` PASS — the pre-fix path assertion RED and stale-registry RED
both spoke before GREEN. Fresh Opus then refused #178's actual unlabeled
proposal and the speculative packet without a review ref while accepting the
two complete records. Would have failed if either incomplete packet passed or
either complete packet was refused.

`Cross-model:` PASS — Claude Opus 5, high effort, safe/tool-less fresh session
`e30e64f7-448f-4253-a4b2-53e0914c3f5e` reviewed artifact hash above from the
Codex implementation lane and returned `proceed`, high confidence, zero
Material findings. Would have failed on any P1 or AC non-pass.

`E2E:` N/A — ideation declared a docs/policy-only task; no user-visible product
runtime changed. The applicable exercise is the fresh ideation-gate packet
drive recorded under Adversarial.

`Origin re-observation:` N/A — no accepted claim originated in a consumer or
external runtime; both accepted defects were reproduced from repository policy
and its contract suite.

### Reviewer adjudication

Opus recorded one non-Material dissent: it thought byte parity relied only on
the stage-exit `cmp`. Unsupported by primary source:
`scripts/kc-dev-flow-contract-test.py:536-544` reads both canonical and
self-adopted bytes for every named reference and fails on inequality. The
external `cmp` reproduced that standing gate; it is not the sole enforcement.
No citation error remains and no product edit follows from this adjudication.

```yaml
science_officer_em_upward_report:
  em_judgment: "AC-1 through AC-3 pass on diff 5adcec6c; zero Material findings."
  evidence_synthesis: "Two observed REDs, contract/parity GREEN, 100% changed-line execution, and four correct adversarial packet dispositions."
  risk_tradeoff_call: "Reuse the existing ideation and contract gates; avoid a second registry or CI surface."
  recommendation: "Keep the five-file candidate unchanged and re-bind validation after commit."
  route: proceed
  confidence: high
  fo_boundary: "No commit, merge, stage-terminalization, or delivery authority."
  engineering_judgment:
    question: "Does the exact candidate satisfy AC-1..AC-3 with the smallest sufficient shape?"
    revision: "base bd81be0081911639e5930be896eea5bb3ba23bb5; diff sha256 5adcec6cbb0eb3ee965b7627fec90550d7a45606acd44995324fc70010bd4b1f"
    evidence_synthesis: "Path and wiring REDs preceded GREEN; packet P1/P3-no-ref refused and P2/P3 accepted; five declared files only."
    adjudications:
      - finding: "AC-1 adoption path"
        disposition: supported
        basis: "workflow-relative header, version 0.2.1, RED/GREEN, and standing byte-parity contract"
      - finding: "AC-2 necessity refusal"
        disposition: supported
        basis: "fresh four-variant packet exercise"
      - finding: "AC-3 no parallel system"
        disposition: supported
        basis: "exact five-path diff and live required-context evidence"
      - finding: "byte parity depends only on external cmp"
        disposition: unsupported
        basis: "contract test lines 536-544 fail on canonical/self-adoption byte drift"
    risk_tradeoff: "One existing-suite assertion buys deterministic path protection; behavioral necessity stays at the judgment gate where a text check cannot substitute."
    recommendation: "Keep candidate unchanged; after captain-approved commit, re-bind exact-head evidence."
    route: proceed
    confidence: high
    dissent: "AC-2 remains judgment-enforced; a text check is intentionally not credited as behavioral proof."
    disproof_condition: "Any incomplete packet passes, a complete packet is refused, the path mutation stays green, or the five-file diff grows a parallel enforcement surface."
    authority_boundary: "Captain retains scope and commit choice; delivery owns PR/CI/merge; EM record is advisory."
```

### Summary

Candidate validation passed without product edits. The task remains in
`validation` because the captain's commit confirmation and an exact committed
revision do not yet exist.

### Exact-head rebind after captain-confirmed commits

The captain confirmed the two logical commits. While they were being created,
`origin/main` advanced from `bd81be0` to `334764d` in two non-overlapping
`e2e-pipeline/compiler/test` paths. The branch rebased cleanly and retained the
same product diff hash.

- Base: `334764d6779aaafcb2621e63036fadc56f3146c2`
- Path fix: `cd2aa442e8897816dfc5f8538b17801b93d66c4a`
- Necessity gate: `fd45025f1ea9878f1eb6f10f4edad35007b021ce`
- Final diff SHA-256:
  `5adcec6cbb0eb3ee965b7627fec90550d7a45606acd44995324fc70010bd4b1f`

Fresh Claude Opus high session `68c7cabe-cb58-4dfd-b62c-6a805513e913`
re-bound the complete diff and receipts to that exact commit chain: AC-1..AC-3
PASS, route `proceed`, zero Material findings. Fresh contract, version-parity,
byte-identity, no-stale-path, diff-check, commit-boundary, and clean-worktree
checks all passed after rebase.

The rebind recorded two non-Material dissents, both unsupported by primary
authority omitted from its embedded packet:

1. A one-sided path mutation is caught by the standing byte-parity loop at
   `scripts/kc-dev-flow-contract-test.py:536-544`.
2. The ideation refusal predicate's own necessity record is present in this
   authoritative item at lines 71-79: `Criterion: AC-2`, the kernel-only
   alternative and its insufficiency, and #178 as the escaped defect.

The exact-head validation result therefore remains `proceed` with no product
correction round. Delivery, PR creation, CI, merge, and terminal state remain
outside this receipt.

### PR-ready revalidation on current main

The branch rebased without conflict onto current `origin/main`
`a024b254e236f521d8438d567ade36d779a52d11`. The two logical commits are now
`d937ae9a1c86b12043f4d22a13508f34fffbaa96` and
`fc7e5abdbd1ef658940750e46832c4f2788627e2`; the exact five-file `+26/-7` diff
has SHA-256
`8c5f89386742bcdb6c0eeeebbce19ad57f4ea799589c5b559e63558a2dda78e4`.

Fresh exact-head mechanical receipts pass: the kc-dev-flow contract suite,
version parity, skill frontmatter lint, marketplace schema and clean-HOME
installation of all seven plugins, diff/check and five-path scope assertions,
canonical/self-adopted byte identity, stale-path absence, and the changed-file
sanitize scan with zero REJECT, BLOCK, or WARN matches.

Fresh Claude Opus 5 high session `821be97e-5137-4500-8d44-dcc329a83433`
returned `proceed`: AC-1 through AC-3 PASS, all four adversarial packet
dispositions match, and there are zero Material findings. It recorded two
non-blocking dissents — the path assertion remains a bounded prose substring
guard, and the mechanism's necessity record lives in this authoritative item
rather than the five-file product diff — but found neither changes an AC,
minimality, or route verdict.

The candidate is ready for the delivery boundary. Per captain instruction, no
PR was created. The item remains in `validation`; `done` still requires a Draft
PR, exact-head hosted CI, authorized merge to `main`, and durable archive state.

### Feedback Cycles

- Cycle 1: REJECTED — delivery merge preflight; surface 5 files/33 LOC vs estimate 5 files (100% file count); AC unchanged

## Stage Report: implementation

- DONE: Reconcile the accepted two-commit change with current `origin/main`
  `951618fbc81f9dae46a22014d109904a54eda6b2`.
  The path assertion was placed after main's retained subtraction checks, and
  the necessity predicate was recut into main's current concise ideation stage.
  Main's `github-pr-feedback/v1` validation and done-stage contract, including
  its contract-test mutation exercise, remains present and green.
- DONE: Preserve the accepted five-file AC scope.
  Both reverse-recovery copies still carry version `0.2.1`, direct adopters to
  `_mods/reverse-recovery-audit.md`, and remain byte-identical. The existing
  absolutes disposition and workflow-relative regression assertion remain in
  place. Ideation still returns gates, checks, harnesses, automations, and
  registries unread without `Criterion`, `Alternative`, and `Escape`; a
  speculative escape still requires a dated, resolvable backlog review seed
  with removal as the default recommendation.
- DONE: Re-run proportionate implementation checks on the corrected head.
  `scripts/kc-dev-flow-contract-test.py` passes, including the merged GitHub
  feedback contract; `scripts/version-parity-check.sh` passes; `git diff
  --check`, canonical/self-adopted `cmp`, and the stale ship-flow-path negative
  search pass. The worktree is clean.
- DONE: Bind the implementation handoff to the exact candidate.
  Base is `951618fbc81f9dae46a22014d109904a54eda6b2`; path commit is
  `d339e1e835ebcde03f2536b2044b4072a162c15f`; necessity commit is
  `f20157bc64af5725122bdccf9d9e1de5671e856e`; final diff SHA-256 is
  `39fef2aec22027a99e82d3539d252aa633c7c289467c37843789a8a52a132730`.
  The diff remains exactly five declared files, `+24/-7`, with no new file,
  executable, registry, workflow step, required context, manifest, or kernel
  edit. Fresh validation remains required; no PR, product push, or delivery
  action was taken.

### Summary

The latest-main conflicts are reconciled without weakening either accepted
contract. The clean five-file candidate is ready for a fresh exact-head
validation pass.
