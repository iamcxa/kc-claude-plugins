---
id: c6wj65396r1s42330e19dweg
title: Align PR merge policy and route oversized changes to native stacks
status: implementation
source: captain directive 2026-08-11
product: kc-dev-flow
sprint:
started: 2026-08-11T12:40:19Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-native-stacked-pr-policy
issue:
pr:
mod-block:
design: required
lane: main
---

## Problem

The adopted PR merge mod is a custom artifact protocol that the released
Spacedock runtime does not consume. It also describes stacked delivery only
qualitatively and does not identify GitHub's native stack topology or CLI.

## Proposed approach

Replace the custom mod with the released Spacedock 0.26.0 `pr-merge` v0.12.2
contract plus bounded local routing and runtime-hardening sections. Preserve
Draft PR delivery, remove only artifact machinery with no released consumer,
and use numeric change shape only to require a topology decision. Compare the
shipped `mods/pr-merge.md` from Spacedock `v0.27.0-pre3` at peeled commit
`ffaeaef696cad492c8d40ab84939178e242aff2e`: backport safety behavior that the
installed 0.26.x runtime can execute, and reject commands owned by 0.27.x. No
final `v0.27.0` tag or release exists at the comparison date.

## Design determination

Design is required because a single entity may need multiple dependent PRs and
because line-count policy can be gamed. The accepted topology is GitHub native:
the bottom PR targets trunk and every higher PR targets the branch below.

Ideation EM route: `narrow`. The narrowed design defines merge-base measurement,
keeps mechanical volume in the observed total, makes semantic seams override
numeric thresholds, and records the top PR as the entity's tracked `pr` after
the captain approves all Draft PR bodies.

## Acceptance criteria

**AC-1 — The adopted merge hook executes against Spacedock 0.26.x while
backporting only runtime-compatible behavior from the Spacedock
`v0.27.0-pre3` shipped `pr-merge` template around the released v0.12.2 body.**
Verified by: compare the retained upstream body byte-for-byte after removing the
marked local extension; exercise `spacedock merge guard` over its released
fixtures; and prove PR bodies use a mode-0600 file, the approved candidate SHA
does not change, pushes name that exact SHA, repository selection comes from the
entity worktree or qualified PR reference, and terminal discovery enters the
0.26 merge-guard sentinel path. Falsified by: an unreleased `spacedock gate` or
`merge guard --rework` command, shell-interpolated PR body, post-approval rebase,
ambient-repository lookup, branch-name push, direct terminalization, or unrelated
local artifact protocol remains.

**AC-2 — Native stacks have one unambiguous topology and command surface.**
Verified by: adversarial examples distinguish a native dependent stack, parallel
PRs, and an atomic single PR; `gh stack link --help` supports the named command.
Falsified by: `gh pr link`, a higher PR targeting trunk, or an independent PR
being called a stack.

**AC-3 — Delivery-shape thresholds trigger judgment without becoming quality or
minimality scores.**
Verified by: the contract measures merge-base additions plus deletions and
changed files at review request, routes `>1500` gross lines or `>20` files to a
stack decision, and requires a stack below the thresholds when two dependent,
independently green layers exist. Falsified by: counts authorize deletion,
compression, relabeling, weakened tests, or a fake layer.

**AC-4 — An inseparable change can remain one PR only through a visible,
reviewer-acknowledged exception.**
Verified by: the Draft PR body names why no layer can be independently reviewed
and verified and identifies mechanical/generated volume separately without
subtracting it from the trigger. Falsified by: an author silently bypasses the
decision or generated volume automatically exempts the PR.

**AC-5 — Removed artifact machinery has no remaining released-runtime or
repository consumer.**
Verified by: a repository-wide search has no `pr_artifact_v1`, terminal
transaction marker, or obsolete test reference; state recovery fails closed
without inventing an artifact. Falsified by: a shipped skill, workflow, script,
template, or runbook still consumes the removed field.

## Stage Report: implementation

- DONE: AC-1 — Commit `e66b39c95286c93b101d0b7e2ff6bb3d28456cfe`
  replaces the custom merge mod with released Spacedock `pr-merge` 0.12.2.
  Removing the marked extension and the single `--draft` token reproduces
  upstream SHA-256
  `a70a0ba4f9fb48a1c33e9f9e2c4ff3cb76b0a816d050a42bdbd6eced9fd15f64`.
  The installed 0.26.0 binary arms `merge:pr-merge` and blocks a bare open PR
  over the released fixture with this exact mod.
- DONE: AC-2 / AC-3 / AC-4 — The marked extension measures the merge-base diff
  at review request, selects semantic seams before numeric triggers, distinguishes
  dependent stacks from parallel trunk PRs, fixes the bottom-to-top GitHub
  topology, requires one approval over every exact Draft title/body and edge,
  links existing Draft PRs with `gh stack link`, and tracks the top PR. The
  installed `gh stack link --help` confirms bottom-to-top arguments and `--base`.
  Gross counts keep mechanical/generated/vendor/lock volume and cannot redefine
  scope, tests, accepted value, or quality. An inseparable oversized change needs
  the fixed `## Native stack exception` heading and explicit reviewer
  acknowledgment.
- DONE: AC-5 — Removed the digest-bound delivery field from the workflow README
  and task template, deleted the terminal-transaction and audit-link extraction
  tests whose only subject was the deleted custom mod, and changed recovery to
  preserve evidence and stop when a delivery mutation can no longer be
  authenticated. The tracked-file sweep finds zero removed field, extraction
  marker, terminal-transaction marker, or obsolete-test references.
- DONE: RED / GREEN — `python3 scripts/kc-dev-flow-contract-test.py` first exited
  1 with `pr-merge does not contain one trailing native-stack extension`. At the
  committed head it passes and enforces released-body integrity, Draft routing,
  stack/exception semantics, fail-closed recovery, and stale-reference absence.
- DONE: Fresh exact-head exit checks pass: kc-dev-flow contract; state-prerequisite
  refusal contract; released Spacedock status and CLI merge-guard fixture suites;
  installed-binary arm/block fixture; structural comparison; stale-reference
  sweep; `gh stack link` help probe; marketplace L0/L1/L2 including all seven
  installs; version parity; 40-skill frontmatter lint; and `git diff --check`.
  No CI workflow changed.

### Delivery-shape decision

Review-request merge base:
`1745b13563dd60ee41f51066ef15d0bff4929cb0`.
Implemented head: `e66b39c95286c93b101d0b7e2ff6bb3d28456cfe`.

```text
1   2     docs/dev/README.md
66  2017  docs/dev/_mods/pr-merge.md
0   585   docs/dev/artifacts/terminal-transaction-contract-test.sh
17  15    docs/dev/runbooks/state-recovery.md
0   291   kc-pr-flow/scripts/pr-merge-audit-link.test.sh
75  0     scripts/kc-dev-flow-contract-test.py
```

The merge-base diff is 159 additions plus 2,910 deletions = 3,069 gross lines
across six files. The structurally constrained upstream-mod replacement is
2,083/3,069 gross lines; generated/vendor/lock volume is 0. Nothing is
subtracted from the trigger total.

This requires a visible topology decision. It remains one Draft PR because the
mod replacement, consumer removal, and fail-closed recovery change form one
lifecycle-contract migration: splitting before consumer removal leaves active
recovery instructions for a field the selected mod does not produce, while
removing consumers before the mod lands leaves the custom protocol without its
contract. No ordering yields two dependent, independently reviewable and
verifiable green layers. The eventual PR must carry
`## Native stack exception` with this rationale and mechanical-volume share for
reviewer acknowledgment.

### Changed-file-to-AC mapping

| Changed path | AC |
|---|---|
| `docs/dev/_mods/pr-merge.md` | AC-1, AC-2, AC-3, AC-4 |
| `docs/dev/README.md` | AC-5 |
| `docs/dev/runbooks/state-recovery.md` | AC-5 |
| deleted terminal-transaction contract test | AC-5 |
| deleted audit-link extraction test | AC-5 |
| `scripts/kc-dev-flow-contract-test.py` | AC-1 through AC-5 |

Each retained extension paragraph maps to an accepted criterion: runtime and
Draft integrity to AC-1; measurement, semantic topology, and count boundaries to
AC-2/AC-3; the reviewer-acknowledged exception to AC-4; approval, linking,
top-PR tracking, and existing CI inheritance to AC-2. The recovery paragraph
maps to AC-5. No ROADMAP or CI paragraph was added.

**If the largest added responsibility is removed, which named AC fails?**
Removing native-stack routing fails AC-2, AC-3, and AC-4; the contract suite
fails on the missing marked extension and required routing phrases. Disposition:
`defense already established by AC mapping`. Number-management incident: none;
the 3,069-line trigger caused this topology decision and did not cause padding,
compression, relabeling, weakened tests, or deletion of accepted value.

### Summary

The committed implementation restores the executable released 0.12.2 merge
contract, keeps every PR Draft by default, adds one bounded native-stack routing
extension, and removes the unconsumed artifact protocol with fail-closed
recovery. The verified worker branch and worktree remain intact for First Officer
integration; no code-branch push, PR mutation, or cleanup was performed.

## Stage Report: implementation (cycle 2)

- DONE: The Material review finding reproduces. Released 0.12.2 builds its audit
  link from the code-worktree SHA, ambient repository, and code-relative entity
  path; that tuple cannot name this task in the split-root state commit.
- DONE: RED / GREEN — The existing kc-dev-flow contract first exited 1 with
  `pr-merge split-root audit link is missing: overrides the released audit-link
  inputs`. Commit `7b315696705840b0db4941d8205e53247ccafdd8` adds one
  clearly overriding subsection inside the existing local-extension markers and
  makes the same contract pass.
- DONE: The correction backports only the portable upstream v0.27 state
  resolution chain needed here: resolve the entity path through Spacedock,
  derive the state Git root, require the full state HEAD and tracked relative
  path to contain a blob, resolve the state remote repository explicitly, and
  format
  `/{state-owner}/{state-repo}/blob/{state-sha}/{state-relative-path}`. Any
  unresolved, untracked, missing-blob, empty, or failed input stops; there is no
  worktree/main fallback.
- DONE: No v0.27 gate, candidate-push, rework, sentinel, or mergeability behavior
  was copied. Released 0.12.2 still normalizes to SHA-256
  `a70a0ba4f9fb48a1c33e9f9e2c4ff3cb76b0a816d050a42bdbd6eced9fd15f64` after
  removing the marked extension and one Draft token. Native-stack routing and
  v0.26 `merge guard` behavior are unchanged; no delivery artifact returned.
- DONE: One-time live split-root exercise resolved this task through the real
  workflow and proved the referenced blob exists:
  `[c6](/iamcxa/kc-claude-plugins/blob/4a26fdb23a056c600be0bef09aa981822eb0b708/native-stacked-pr-routing.md)`.
- DONE: Every deletion was re-reviewed. The terminal-transaction test's only
  external consumer was the deleted custom transaction. The 291-line audit-link
  test's only executable target was the deleted extraction function; no function
  or marker remains to source. It stays deleted, while the existing Python
  contract now falsifies omission of every required split-root tuple step and
  the live exercise proves the tuple against real state.
- DONE: Fresh exact-head exits pass: kc-dev-flow contract; state-prerequisite
  refusal contract; released Spacedock status and CLI merge-guard fixtures;
  installed 0.26.0 arm/block fixture; structural comparison; removed and
  unreleased-command sweep; `gh stack link` help; live state tuple/blob; all
  marketplace L0/L1/L2 installs; version parity; 40-skill frontmatter lint; and
  `git diff --check`.

### Updated delivery-shape evidence

Review-request merge base remains
`1745b13563dd60ee41f51066ef15d0bff4929cb0`; implemented head is now
`7b315696705840b0db4941d8205e53247ccafdd8`.

```text
1    2     docs/dev/README.md
103  2017  docs/dev/_mods/pr-merge.md
0    585   docs/dev/artifacts/terminal-transaction-contract-test.sh
17   15    docs/dev/runbooks/state-recovery.md
0    291   kc-pr-flow/scripts/pr-merge-audit-link.test.sh
88   0     scripts/kc-dev-flow-contract-test.py
```

The cumulative merge-base diff is 209 additions plus 2,910 deletions = 3,119
gross lines across the same six files. The structurally constrained upstream-mod
replacement remains 2,083/3,119 gross lines; generated/vendor/lock volume remains
0. Cycle 2 adds 51 net contract/audit-correction lines and changes no topology:
the mod, its removed consumers, fail-closed recovery, and the split-root tuple
guard still cannot form two independently reviewable and verifiable green
layers. The single-Draft `## Native stack exception` remains required.

### Summary

Cycle 2 corrects the one split-root regression without widening runtime or
delivery scope: PR bodies now use immutable task-state audit links and stop when
state cannot be proven, while released 0.12.2 behavior, Draft/native-stack
routing, artifact removal, and the two test deletions remain intact.

## Stage Report: validation

### Verdict

REJECTED at exact product head
`7b315696705840b0db4941d8205e53247ccafdd8` against merge base
`1745b13563dd60ee41f51066ef15d0bff4929cb0`. Released-runtime preservation,
split-root link construction, and removal of the unconsumed artifact protocol
pass. The delivery cannot advance because the governing stack predicates
conflict, this oversized change has a demonstrated independently green lower
layer, and the new routing contract accepts semantically inverted policy.

### Findings

- **[P1] Align the governing stack predicate with the new mandatory route —
  `docs/dev/_mods/pr-merge.md:157`.** The extension requires a native stack
  whenever two dependent, independently reviewable and verifiable green layers
  exist. The unchanged governing implementation rule in `docs/dev/README.md:276`
  allows a stack only when waiting for the lower PR to merge blocks useful work.
  The same change can therefore receive opposite topology decisions. Make the
  README rule and the extension express one predicate before this can govern
  delivery.
- **[P1] Route this oversized migration through the demonstrated green
  two-layer stack — `docs/dev/_mods/pr-merge.md:161`.** The exact diff is 3,119
  gross lines. In a disposable checkout, removing only the new native-routing
  policy paragraphs and their phrase assertions left a lower layer containing
  the released-runtime/artifact migration and split-root correction; both
  `python3 scripts/kc-dev-flow-contract-test.py` and
  `bash scripts/dev-flow-state-prereq.test.sh` passed. That falsifies the entity's
  claim that no ordering yields two independently reviewable and verifiable
  green layers. Deliver that lower layer first and the corrected routing policy
  above it, or identify a named independent acceptance check that the lower
  layer actually fails.
- **[P2] Make the routing guard fail on semantic inversion —
  `scripts/kc-dev-flow-contract-test.py:830`.** A disposable mutant changed the
  normative rule to say that two green dependent layers "never requires a
  native stack at any size." The current phrase loop still passed because it
  checks vocabulary, not polarity or classification. Replace the loose phrase
  assertions with exact normative assertions and data-driven adversarial cases
  that fail when stack, parallel, atomic, and exception outcomes are inverted.

### Acceptance-criteria coverage

| Criterion | Verdict | Evidence |
| --- | --- | --- |
| AC1 | PASS | Removing the trailing extension and the one `--draft` token reproduces released `pr-merge` v0.12.2 SHA-256 `a70a0ba4f9fb48a1c33e9f9e2c4ff3cb76b0a816d050a42bdbd6eced9fd15f64`. Spacedock v0.26.0 merge tests passed 49/49, and the installed 0.26.0 binary armed then refused terminal advancement until its merge hook ran. No v0.27 gate/rework/candidate behavior or unrelated artifact protocol remains. |
| AC2 | FAIL | The extension states the required bottom-to-trunk and higher-to-branch-below topology and uses `gh stack link`, but its mandatory stack predicate conflicts with the governing README predicate. |
| AC3 | FAIL | Gross lines and file count are measured from the merge base, all volume stays in the totals, and semantic examples classify correctly in isolation. The current one-PR topology nevertheless ignores a demonstrated green seam, while the README conflict makes the semantic override ambiguous. |
| AC4 | FAIL | The fixed `## Native stack exception`, non-subtracted mechanical share, and reviewer acknowledgment are specified. This change's exception is not justified because a lower green layer passes independently. |
| AC5 | PASS | `pr_artifact_v1`, the two recipe marker pairs, obsolete executable subjects, and obsolete tests have no tracked consumer at HEAD. Recovery now preserves evidence and stops instead of inventing a replacement credential. |

### Changed-path and diff coverage

| Changed path | AC mapping | Validation |
| --- | --- | --- |
| `docs/dev/README.md` | AC2-AC3 | Compared its implementation-stage predicate with the extension and found the blocking contradiction. |
| `docs/dev/_mods/pr-merge.md` | AC1-AC4 | Proved exact released-body equality, exercised released merge behavior, inspected all extension rules, ran topology attacks, and demonstrated the lower green layer. |
| `docs/dev/artifacts/terminal-transaction-contract-test.sh` | AC5 | Inspected the deleted test and swept HEAD for its extracted function, recipe markers, and remaining consumers; none exists. |
| `docs/dev/runbooks/state-recovery.md` | AC5 | Ran the refusal contract and inspected the new fail-closed recovery language for invented credentials or unsafe fallback. |
| `kc-pr-flow/scripts/pr-merge-audit-link.test.sh` | AC5 | Inspected the deleted executable subject and swept HEAD for its function and markers; none exists. The live state tuple replaces its surviving boundary claim. |
| `scripts/kc-dev-flow-contract-test.py` | AC1-AC5 | Ran at exact head, inspected every addition, exercised a split-root tuple, and used a polarity mutant to expose the inadequate routing assertions. |

`git diff --numstat` reports 209 additions and 2,910 deletions across six paths.
All 209 additions were classified: the 191 mod/contract lines were exercised by
structural comparison, exact-head suites, live CLI/state checks, and direct
mutants; the 18 README/recovery lines were exercised by policy comparison and
the refusal path. Deletions were covered by exact released-body comparison plus
deleted-subject and consumer sweeps.

Diff coverage: 100% path coverage (6/6); 209/209 additions classified and exercised by a suite, live boundary check, structural equality check, or direct falsifier; 2,910 deletions covered by exact upstream comparison and deleted-subject/consumer sweeps.

### Adversarial classification and falsifiers

- 200 gross lines with two dependent, independently green layers: native stack.
- 2,000 atomic lines: the numeric decision fires; if no green seam exists, one
  Draft PR needs the fixed exception, the separately named zero/nonzero
  mechanical share, and explicit reviewer acknowledgment.
- 2,000 generated lines: all 2,000 count; generated share is named but never
  subtracted or auto-exempted.
- 25 independent files: the file trigger fires; independent slices become
  parallel Draft PRs from trunk, not a stack.
- Two independent parallel slices: parallel Draft PRs from trunk.
- A proposed layer that cannot verify alone: not a green seam; reject the fake
  layer, then use atomic or exception routing according to the full diff.

Concrete falsifier: a mutant that preserves the current keywords while changing
"requires a native stack" to "never requires a native stack" must fail the
contract. Separately, the one-PR exception remains disproved unless the
runtime/artifact lower-layer carveout fails a named independent acceptance
check.

### Exact evidence

- Product worktree was clean and exact HEAD remained
  `7b315696705840b0db4941d8205e53247ccafdd8`; `git diff --check` passed.
- `python3 scripts/kc-dev-flow-contract-test.py`,
  `bash scripts/dev-flow-state-prereq.test.sh`,
  `bash scripts/version-parity-check.sh`,
  `bash scripts/skill-frontmatter-lint.sh`, and
  `bash scripts/marketplace-verify.sh` all passed at exact HEAD.
- Extracted tag `spacedock/v0.26.0` at
  `3819610affd5bfc01f9a9a31893462c02b578589`: 42 `internal/status` merge tests
  and 7 `internal/cli` merge tests passed. The installed `spacedock 0.26.0`
  fixture armed `merge:local-merge` and then refused terminal advancement before
  the hook ran.
- The released section contains one Draft adjustment; after removing it, its
  bytes equal the tagged v0.12.2 mod and hash to
  `a70a0ba4f9fb48a1c33e9f9e2c4ff3cb76b0a816d050a42bdbd6eced9fd15f64`.
- Installed `gh 2.92.0` reports that `gh stack link` arguments are bottom to top,
  `--base` selects the bottom base, and `--open` opts out of Draft creation.
  Official source confirms the default Draft flag and official documentation
  confirms bottom-to-trunk/higher-to-branch-below topology and stack-base CI:
  `https://github.com/github/gh-stack/blob/main/cmd/link.go`,
  `https://github.github.com/gh-stack/introduction/overview/`, and
  `https://github.github.com/gh-stack/faq/`.
- Live split-root resolution produced state HEAD
  `e355fb298762eceec5c769f30177159bcab77032`, relative path
  `native-stacked-pr-routing.md`, and blob
  `0459a92843ce6f6401ccc5aea77c3d379a4f91d1`. Both plausible product/code-tree
  tuples failed blob existence as required.
- HEAD contains no tracked `pr_artifact_v1`, deleted recipe marker, deleted test
  name, or deleted executable subject.

Lenses: behavior PASS; contract/schema FAIL; state/recovery PASS; runtime/platform PASS; docs/policy FAIL; delivery/topology FAIL; security/privacy PASS; concurrency/split-root PASS (3 findings: 2 P1, 1 P2).
Adversarial: six topology cases classified; live arm/block and split-root fail paths passed; disposable lower-layer carveout and polarity mutant both falsified acceptance.
Cross-model: not_needed — direct source, exact-runtime, live-state, and mutant evidence is high confidence; no optional pass was launched under the no-agent contract.
E2E: N/A — this ideation-approved change is workflow policy and CLI orchestration with no app/browser journey; exact installed CLI, released-source fixtures, and the live split-root tuple exercised the equivalent boundaries.
Origin re-observation: PASS — Reported scenario: released Spacedock 0.26 must arm/block the merge guard, the custom artifact protocol must have no consumer, and split-root audit links must name committed task state | Originating runtime kind: installed native CLI plus GitHub-hosted stack/gh CLI | Re-observation artifact/revision: product `7b315696705840b0db4941d8205e53247ccafdd8`, Spacedock v0.26.0 tag `3819610affd5bfc01f9a9a31893462c02b578589`, installed spacedock 0.26.0, gh 2.92.0, state `e355fb298762eceec5c769f30177159bcab77032` blob `0459a92843ce6f6401ccc5aea77c3d379a4f91d1` | Equivalent-runtime rationale: exact released tag/installed binary, actual task-state checkout, installed gh help, and official GitHub stack source/docs | Falsifier kind: refusal plus existence disproof | Result: installed fixture armed then refused without its hook; the state tuple blob exists; both product/code-tree tuples fail.

### Engineering-manager judgment

```yaml
science_officer_em_upward_report:
  em_judgment: "Exact head preserves released runtime behavior and artifact removal, but cannot pass validation because its routing policy is internally contradictory, its own oversized diff has a demonstrable green stack seam, and its phrase guard accepts inverted semantics."
  evidence_synthesis: "At 7b315696705840b0db4941d8205e53247ccafdd8 the v0.12.2 normalized body matches SHA-256 a70a0ba4f9fb48a1c33e9f9e2c4ff3cb76b0a816d050a42bdbd6eced9fd15f64, Spacedock v0.26.0 merge suites pass 49/49 and the installed arm/block fixture reproduces, while disposable bottom-layer and semantic-mutant experiments respectively pass the affected contracts and expose the invalid one-PR exception and tautological routing assertion."
  risk_tradeoff_call: "Returning costs one bounded policy/test correction and stacked delivery, but avoids shipping contradictory routing and a reviewer exception already disproved by an independently green layer; the alternative is to retain a one-PR exception that violates the change's own rule."
  recommendation: "Return to implementation: align the README and mod predicates, replace loose phrase checks with semantic adversarial fixtures, and deliver the runtime/artifact migration below the native-stack policy layer."
  route: return
  confidence: high
  multi_model: not_needed
  fo_boundary: "The First Officer may route the rejected gate but has no authority to waive findings, approve the exception, or mutate PR delivery."
  engineering_judgment:
    question: "Does exact head 7b315696705840b0db4941d8205e53247ccafdd8 satisfy native-stacked-pr-routing acceptance and justify one oversized Draft PR?"
    revision: "7b315696705840b0db4941d8205e53247ccafdd8"
    evidence_synthesis: "At 7b315696705840b0db4941d8205e53247ccafdd8 the v0.12.2 normalized body matches SHA-256 a70a0ba4f9fb48a1c33e9f9e2c4ff3cb76b0a816d050a42bdbd6eced9fd15f64, Spacedock v0.26.0 merge suites pass 49/49 and the installed arm/block fixture reproduces, while disposable bottom-layer and semantic-mutant experiments respectively pass the affected contracts and expose the invalid one-PR exception and tautological routing assertion."
    adjudications:
      - finding: "The governing README and extension give different stack predicates."
        disposition: supported
        basis: "README line 276 conditions stacking on blocked useful work; mod line 157 makes every dependent green seam mandatory at any size."
      - finding: "The current oversized diff has no independently green stack seam."
        disposition: unsupported
        basis: "A disposable lower layer retaining released runtime, artifact removal, recovery, and split-root correction passed both affected contracts."
      - finding: "The phrase loop protects native-routing semantics."
        disposition: unsupported
        basis: "A polarity-inverted rule retained every searched phrase and the contract still passed."
    risk_tradeoff: "Returning costs one bounded policy/test correction and stacked delivery, but avoids shipping contradictory routing and a reviewer exception already disproved by an independently green layer; the alternative is to retain a one-PR exception that violates the change's own rule."
    recommendation: "Return to implementation: align the README and mod predicates, replace loose phrase checks with semantic adversarial fixtures, and deliver the runtime/artifact migration below the native-stack policy layer."
    route: return
    confidence: high
    dissent: "The implementation report asserts no green split exists; the disposable bottom-layer PASS directly contradicts that assertion."
    disproof_condition: "A corrected exact head would change this route if the bottom carveout fails a named independent acceptance check, the two governing predicates are identical, and a polarity inversion makes the routing contract fail."
    authority_boundary: "The captain owns scope, exception, and stack-body approval; the validation gate owns this verdict; work-item and First Officer owners may transition or route the entity; this judgment grants no merge or delivery-mutation authority."
```

### Summary

Return to implementation. Preserve the confirmed released-runtime, split-root,
and fail-closed artifact-removal work; align the governing topology predicate,
make semantic inversion fail the contract, and deliver the demonstrated lower
green migration layer before the corrected native-stack policy layer.

### Feedback Cycles

- Cycle 1: REJECTED — fresh validation; surface 6 files vs estimate 6 (0%); AC unchanged
- Cycle 2: RETURN — exact Spacedock `v0.27.0-pre3` shipped-template comparison
  found runtime-compatible body-file, candidate-SHA, repository-selection,
  exact-push, and sentinel hardening absent from the accepted bottom layer;
  sequential surface 9 layer-paths vs estimate 9 (0%); AC-1 widened by captain
  directive, AC-2 through AC-5 unchanged

## Stage Report: implementation (cycle 3)

### Outcome

Split the rejected combined delivery into the demonstrated two-layer native
stack. Both layers are committed, clean, independently green at their exact
heads, and remain local: no code branch was pushed and no PR was opened.

### Bottom layer: released-runtime alignment

- Branch: `spacedock-ensign/pr-merge-runtime-alignment`
- Worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-pr-merge-runtime-alignment`
- Head: `0980e992c0f5f31a0e9c6d816d48f7bee3a8a5ae`
- Merge base against `origin/main`:
  `1745b13563dd60ee41f51066ef15d0bff4929cb0`
- Commit: `refactor(kc-dev-flow): align PR merge with released runtime`

This layer restores the released Spacedock 0.26.0 `pr-merge` v0.12.2 body,
changes only its one create command to Draft, retains the bounded split-root
immutable audit-link correction, removes the unconsumed `pr_artifact_v1`
protocol and obsolete extraction/terminal tests, and makes unsupported delivery
recovery fail closed. It introduces no native-stack routing policy.

Raw `git diff --numstat origin/main...HEAD`:

```text
1	2	docs/dev/README.md
58	2017	docs/dev/_mods/pr-merge.md
0	585	docs/dev/artifacts/terminal-transaction-contract-test.sh
17	15	docs/dev/runbooks/state-recovery.md
0	291	kc-pr-flow/scripts/pr-merge-audit-link.test.sh
81	0	scripts/kc-dev-flow-contract-test.py
```

### Top layer: native-stack policy

- Branch: `spacedock-ensign/native-stacked-pr-policy`
- Worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-native-stacked-pr-policy`
- Head: `3ad8a4f8d35ac2efe1e839aa77291eb4521d9543`
- Merge base against the bottom head:
  `0980e992c0f5f31a0e9c6d816d48f7bee3a8a5ae`
- Commit: `docs(kc-dev-flow): route dependent changes through native stacks`

The top diff contains only `docs/dev/README.md`,
`docs/dev/_mods/pr-merge.md`, and
`scripts/kc-dev-flow-contract-test.py`. One authoritative parsed decision table
now maps the four exact cases: dependent green layers to a native stack at any
size; independent green slices to parallel Draft PRs; an atomic change above
the strict `> 1,500` gross-lines or `> 20` files trigger to one Draft with
`## Native stack exception`; and a smaller atomic change to one Draft. README
points to those same predicates and no longer adds the lower-merge waiting
condition.

Raw `git diff --numstat 0980e992c0f5f31a0e9c6d816d48f7bee3a8a5ae...HEAD`:

```text
5	4	docs/dev/README.md
46	0	docs/dev/_mods/pr-merge.md
79	7	scripts/kc-dev-flow-contract-test.py
```

### Exact-head evidence

- At each exact head, `python3 scripts/kc-dev-flow-contract-test.py`,
  `bash scripts/dev-flow-state-prereq.test.sh`,
  `bash scripts/marketplace-verify.sh`,
  `bash scripts/skill-frontmatter-lint.test.sh`,
  `bash scripts/skill-frontmatter-lint.sh`, and `git diff --check` passed.
- Spacedock 0.26.0 `internal/status` and `internal/cli` merge-guard fixtures
  passed against the retained runtime contract.
- A temporary outcome inversion in the first table row failed with
  `delivery-topology row polarity or required outcome drifted`; restoring the
  exact row returned the contract to green.
- Installed `gh stack link --help` passed and documents bottom-to-top arguments,
  `--base`, and the `--open` opt-out that the policy forbids.
- The preserved combined-evidence worktree remains clean at
  `7b315696705840b0db4941d8205e53247ccafdd8` on
  `spacedock-ensign/native-stacked-pr-routing`.

### Handoff

Track the top worktree listed above. When captain approval authorizes delivery,
push and open the bottom Draft PR first, then the top Draft PR based on the
bottom branch, and link them bottom to top. This implementation cycle performed
none of those outward mutations.

## Stage Report: validation (cycle 2)

### Verdict

ACCEPTED for the exact two-layer revision:

- bottom `0980e992c0f5f31a0e9c6d816d48f7bee3a8a5ae` against remote and local
  `origin/main` `1745b13563dd60ee41f51066ef15d0bff4929cb0`;
- top `3ad8a4f8d35ac2efe1e839aa77291eb4521d9543` against that exact bottom head.

No blocking findings remain. Product worktrees were read-only and clean; no
branch push, PR creation, stack link, merge, or product edit was performed.

### Cycle-1 finding disposition

- **Resolved — governing predicate alignment.** The README now delegates to the
  one authoritative Delivery topology decision table and expressly adds no
  second readiness condition. The old lower-merge waiting predicate is absent.
  The exact-head contract enforces both facts.
- **Resolved — actual stacked delivery shape.** Remote `main` and local
  `origin/main` both equal `1745b13563dd60ee41f51066ef15d0bff4929cb0`.
  The bottom commit's sole parent is that revision, and the top commit's sole
  parent is the exact bottom head. The bottom passes independently without any
  native-stack policy; the top is one policy-only commit above it.
- **Resolved — outcome/polarity mutation failure.** In a disposable archive of
  the top head, changing the dependent-green row's required topology from
  `Native stack at any size` to `One Draft PR` made
  `python3 scripts/kc-dev-flow-contract-test.py` exit 1 with
  `delivery-topology row polarity or required outcome drifted`. The unmodified
  top head passes.

### Acceptance-criteria coverage

| Criterion | Verdict | Exact evidence |
| --- | --- | --- |
| AC-1 | PASS | At both layer heads, removing the one Draft token from the released section reproduces tagged `pr-merge` v0.12.2 byte-for-byte at SHA-256 `a70a0ba4f9fb48a1c33e9f9e2c4ff3cb76b0a816d050a42bdbd6eced9fd15f64`. Spacedock v0.26.0 merge tests passed 42 status plus 7 CLI cases, and the installed 0.26.0 binary reproduced arm then refusal. No unreleased gate/rework/candidate surface exists. |
| AC-2 | PASS | The exact decision table separates dependent stack, parallel slices, and atomic single-PR outcomes. The local commit graph is bottom-to-trunk and top-to-bottom. Installed `gh 2.92.0` documents bottom-to-top `gh stack link`, correct base chaining, bottom `--base`, and the `--open` opt-out. |
| AC-3 | PASS | The authoritative table uses the strict `gross additions + deletions > 1,500 OR changed files > 20` trigger, keeps all mechanical/generated/vendor/lock volume in the totals, and makes dependent green layers win at any size. Exact row equality and the polarity mutant protect the outcomes. |
| AC-4 | PASS | The atomic-trigger row requires one Draft PR with the fixed `## Native stack exception`; policy requires why no green layer exists, separately names non-subtracted mechanical/generated/vendor/lock share, and requires explicit reviewer acknowledgment. |
| AC-5 | PASS | Both exact heads have zero tracked removed artifact fields, recipe markers, obsolete test names, or deleted executable subjects. Bottom recovery fails closed, and top changes no recovery or artifact-removal file. |

### Layer and changed-file coverage

Bottom `origin/main...0980e992` is 157 additions and 2,910 deletions across six
paths (3,067 gross lines):

| Bottom changed path | AC mapping | Validation |
| --- | --- | --- |
| `docs/dev/README.md` | AC-5 | Removed the artifact field; tracked consumer sweep passed. |
| `docs/dev/_mods/pr-merge.md` | AC-1, AC-5 | Released-body equality, Draft adjustment, split-root extension, released merge suites, and installed arm/refusal passed; native-stack policy is absent. |
| `docs/dev/artifacts/terminal-transaction-contract-test.sh` | AC-5 | Deleted subject and all marker/name consumers are absent. |
| `docs/dev/runbooks/state-recovery.md` | AC-5 | Refusal contract passes and recovery stops without an invented credential. |
| `kc-pr-flow/scripts/pr-merge-audit-link.test.sh` | AC-5 | Deleted extraction subject and all marker/name consumers are absent. |
| `scripts/kc-dev-flow-contract-test.py` | AC-1, AC-5 | Exact released hash, split-root tuple, policy absence, recovery refusal, and consumer removal pass independently. |

Top `0980e992...3ad8a4f8` is 130 additions and 11 deletions across exactly three
paths (141 gross lines):

| Top changed path | AC mapping | Validation |
| --- | --- | --- |
| `docs/dev/README.md` | AC-2, AC-3 | Points to the table's exact predicates; old conflicting waiting predicate is absent and contract-guarded. |
| `docs/dev/_mods/pr-merge.md` | AC-2, AC-3, AC-4 | Adds only the decision table, exception, Draft stack mechanics, approval, linking, CI, and top-PR tracking policy. |
| `scripts/kc-dev-flow-contract-test.py` | AC-2, AC-3, AC-4 | Parses one table, requires its exact header/four rows and strict threshold, guards README authority, and fails on outcome inversion. |

Diff coverage: 100% path-layer coverage (9/9: six bottom plus three top); 287/287 sequential additions classified and exercised by an exact-head suite, structural comparison, live boundary, adversarial document case, or direct mutant; 2,921 sequential deletions covered by released-body equality, top-only scope inspection, and deleted-subject/consumer sweeps.

### Exact-head evidence

- Both product worktrees matched their declared heads and were clean before and
  after the checks; `git diff --check` passed for each declared layer range.
- At **each** exact head, these exited zero:
  `python3 scripts/kc-dev-flow-contract-test.py`,
  `bash scripts/dev-flow-state-prereq.test.sh`,
  `bash scripts/version-parity-check.sh`,
  `bash scripts/skill-frontmatter-lint.test.sh` (12/12),
  `bash scripts/skill-frontmatter-lint.sh` (40/40), and
  `bash scripts/marketplace-verify.sh` (L0, L1, and all seven L2 installs).
- A clean extraction of Spacedock tag `v0.26.0` at
  `3819610affd5bfc01f9a9a31893462c02b578589` passed 42
  `internal/status` and 7 `internal/cli` merge tests with zero failures.
- Installed `spacedock 0.26.0 (contract 3)` armed
  `merge:local-merge`, then a second guard call exited 1 because the hook had not
  run. The guard neither inferred success nor advanced terminal state.
- Structural comparison at each layer produced the same released-body SHA-256
  `a70a0ba4f9fb48a1c33e9f9e2c4ff3cb76b0a816d050a42bdbd6eced9fd15f64`.
  The bottom extension reports `policy=false`; the top reports `policy=true`.
- The top diff contains only `docs/dev/README.md`,
  `docs/dev/_mods/pr-merge.md`, and
  `scripts/kc-dev-flow-contract-test.py`; its parent is the bottom head. The
  bottom contract's explicit policy-absence guard passes before the top lands.
- Live state resolution found state head
  `e1ab5e82cf2e689bfd9f814e80a2f262812d9c67`, task path
  `native-stacked-pr-routing.md`, blob
  `d24dc94af802b0b61965702dd9801c72d36f2e31`, repository
  `iamcxa/kc-claude-plugins`, and short ID `c6`.

Lenses: behavior PASS; contract/schema PASS; state/recovery PASS; runtime/platform PASS; docs/policy PASS; delivery/topology PASS; security/privacy PASS; concurrency/split-root PASS (0 findings; inputs: exact bottom/top commits, task ACs, selected mods, installed CLIs, released tag; falsifiers: parent mismatch, policy leak into bottom, predicate conflict, semantic outcome inversion, missing consumer, or unsafe recovery).
Adversarial: PASS — classified dependent, parallel, triggered atomic, and smaller atomic rows; proved bottom green with policy absent; an inverted dependent-row outcome failed with the exact polarity error; released guard and split-root refusal/existence paths remained fail closed.
Cross-model: not_needed — all three disputed findings have direct exact-graph, exact-text, exact-suite, live-runtime, and mutation evidence at high confidence; the no-agent validation contract was preserved.
E2E: N/A — the accepted change is workflow policy and CLI orchestration with no app/browser user journey; exact local stack graph, installed CLI, released-source fixtures, marketplace installs, and live split-root resolution exercise the relevant boundaries. External PR creation/linking remains captain-gated delivery, not validation-owned E2E.
Origin re-observation: PASS — Reported scenario: released Spacedock 0.26 must arm/block its merge ceremony, removed artifact machinery must have no consumer, split-root audit links must name committed task state, and native GitHub stacks must use bottom-to-top/base chaining | Originating runtime kind: released and installed native CLIs plus repository task state | Re-observation artifact/revision: bottom `0980e992c0f5f31a0e9c6d816d48f7bee3a8a5ae`, top `3ad8a4f8d35ac2efe1e839aa77291eb4521d9543`, Spacedock tag `3819610affd5bfc01f9a9a31893462c02b578589`, installed spacedock 0.26.0, gh 2.92.0, state `e1ab5e82cf2e689bfd9f814e80a2f262812d9c67` blob `d24dc94af802b0b61965702dd9801c72d36f2e31` | Equivalent-runtime rationale: exact released source and installed binary, actual parent-linked layer revisions, actual split-root state checkout, and installed gh command surface | Falsifier kind: refusal, mutation, and existence-disproof | Result: 49 released merge tests passed, installed guard armed then refused without its hook, both tracked-consumer sweeps were empty, the committed state tuple exists, the local stack parent chain is exact, and the polarity mutant failed.

### Engineering-manager judgment

```yaml
science_officer_em_upward_report:
  em_judgment: "The corrected two-layer exact revision satisfies all five acceptance criteria and resolves every cycle-1 finding: authoritative predicate alignment, real parent-linked stack shape, and mutation-sensitive semantic enforcement."
  evidence_synthesis: "Bottom 0980e992c0f5f31a0e9c6d816d48f7bee3a8a5ae is the sole child of current origin/main and passes independently with native-stack policy forbidden; top 3ad8a4f8d35ac2efe1e839aa77291eb4521d9543 is its sole-child policy commit across only three mapped paths. Both exact heads pass the full repository gates, the released body matches SHA-256 a70a0ba4f9fb48a1c33e9f9e2c4ff3cb76b0a816d050a42bdbd6eced9fd15f64, released merge tests pass 49/49, and an inverted topology outcome fails the semantic contract."
  risk_tradeoff_call: "Proceeding retains two-PR review and landing overhead and still requires captain-approved Draft bodies and linking, but buys truthful independent review boundaries and one authoritative routing rule; returning to the combined branch would reintroduce the already proven topology violation."
  recommendation: "Proceed from validation with 0980e992c0f5f31a0e9c6d816d48f7bee3a8a5ae as the bottom Draft targeting main and 3ad8a4f8d35ac2efe1e839aa77291eb4521d9543 as the top Draft targeting the bottom branch; preserve the approval, link, and no-open guards."
  route: proceed
  confidence: high
  multi_model: not_needed
  fo_boundary: "The First Officer may route the accepted gate and seek captain approval, but may not push, create, link, ready, or merge either PR without the declared authority."
  engineering_judgment:
    question: "Do exact heads 0980e992c0f5f31a0e9c6d816d48f7bee3a8a5ae and 3ad8a4f8d35ac2efe1e839aa77291eb4521d9543 resolve the three cycle-1 findings and satisfy native-stacked-pr-routing acceptance?"
    revision: "0980e992c0f5f31a0e9c6d816d48f7bee3a8a5ae -> 3ad8a4f8d35ac2efe1e839aa77291eb4521d9543"
    evidence_synthesis: "Bottom 0980e992c0f5f31a0e9c6d816d48f7bee3a8a5ae is the sole child of current origin/main and passes independently with native-stack policy forbidden; top 3ad8a4f8d35ac2efe1e839aa77291eb4521d9543 is its sole-child policy commit across only three mapped paths. Both exact heads pass the full repository gates, the released body matches SHA-256 a70a0ba4f9fb48a1c33e9f9e2c4ff3cb76b0a816d050a42bdbd6eced9fd15f64, released merge tests pass 49/49, and an inverted topology outcome fails the semantic contract."
    adjudications:
      - finding: "Cycle-1 governing predicate conflict persists."
        disposition: unsupported
        basis: "The top README delegates to one decision table, removes the lower-merge waiting predicate, and the exact-head contract guards both properties."
      - finding: "Cycle-1 independently green seam remains delivered as one combined revision."
        disposition: unsupported
        basis: "The bottom commit is a clean, independently green child of origin/main and the top policy commit is its direct child; their declared diffs are separately bounded and mapped."
      - finding: "Cycle-1 phrase guard still accepts a polarity inversion."
        disposition: unsupported
        basis: "The contract parses and compares all four exact rows; replacing the dependent outcome with One Draft PR exits 1 with the polarity-drift error."
    risk_tradeoff: "Proceeding retains two-PR review and landing overhead and still requires captain-approved Draft bodies and linking, but buys truthful independent review boundaries and one authoritative routing rule; returning to the combined branch would reintroduce the already proven topology violation."
    recommendation: "Proceed from validation with 0980e992c0f5f31a0e9c6d816d48f7bee3a8a5ae as the bottom Draft targeting main and 3ad8a4f8d35ac2efe1e839aa77291eb4521d9543 as the top Draft targeting the bottom branch; preserve the approval, link, and no-open guards."
    route: proceed
    confidence: high
    dissent: ""
    disproof_condition: "Change this route if remote main no longer equals the bottom parent, the bottom fails independently with stack policy absent, the top gains an unmapped non-policy path, a topology outcome inversion passes, the released hash drifts, or a removed artifact consumer reappears."
    authority_boundary: "The captain retains Draft-body, topology, scope, and irreversible delivery approval; the validation gate owns this verdict; work-item and First Officer owners may route the entity; delivery owners alone may push, create, link, ready, merge, or close."
```

### Summary

Proceed. The bottom runtime/artifact migration is independently green without
native-stack policy, the top is a policy-only direct child, one authoritative
predicate now governs routing, and semantic outcome inversion is caught. The
next authorized action is captain review of both exact Draft PR bodies and the
bottom-to-top branch/base bundle.
