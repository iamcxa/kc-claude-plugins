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
worktree: .worktrees/spacedock-ensign-native-stacked-pr-policy-v3
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
local artifact protocol remains. Because kc-dev-flow requires an authenticated
merged product PR for terminalization, an automatic local-merge fallback also
falsifies this criterion; delivery failures stop with pending authority intact.

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
- Cycle 3: REJECTED — fresh validation found non-Draft replacement argv,
  trunk-only hardening, insufficient whole-stack terminal proof, and three
  phrase-only safety cases; surface 10 layer-paths vs estimate 9 (11%); AC
  unchanged

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

## Stage Report: implementation (cycle 4)

### Outcome

Hardened the accepted bottom layer against the portable delivery seams present
in the formal Spacedock `v0.27.0-pre3` shipped template, then rebuilt the
accepted native-stack policy as one direct-child top commit. Both new layers
are committed, clean, independently green at their exact heads, and remain
local. No product branch was pushed, no PR was created, and no stack was linked.

The task `worktree` now points to
`.worktrees/spacedock-ensign-native-stacked-pr-policy-v2`.

### Source provenance

- No final Spacedock `v0.27.0` tag or GitHub release exists at this comparison
  date.
- The authoritative comparison seam is shipped `mods/pr-merge.md` from formal
  prerelease `v0.27.0-pre3`, annotated tag object
  `5a0b9a13282bd0abd6d1e3479475acd809b73b12`, peeled commit
  `ffaeaef696cad492c8d40ab84939178e242aff2e`, and full template SHA-256
  `0f2a4628a008e044b9d0faa67282597dfaa2ee56b6954f10028ca7d921b6e031`.
- Upstream commit `07ce3ddd30e644b289deda98d3a589ec18e57e41` is 102 commits
  after pre3, not a release. Its shipped template is byte-identical to pre3.
- Upstream `docs/dev/_mods/pr-merge.md` is a separate adopted workflow copy at
  v0.12.5. It retains branch-name push and inline `--body`, so it was not used
  as the comparison seam.
- The normalized released 0.26 v0.12.2 body remains byte-identical at SHA-256
  `a70a0ba4f9fb48a1c33e9f9e2c4ff3cb76b0a816d050a42bdbd6eced9fd15f64`.

### Bottom v2: portable runtime hardening

- Branch: `spacedock-ensign/pr-merge-runtime-alignment-v2`
- Worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-pr-merge-runtime-alignment-v2`
- Head: `264aabb017a36dcda0a740f28896086eab96bcc6`
- Parent and merge base:
  `0980e992c0f5f31a0e9c6d816d48f7bee3a8a5ae`
- Commit: `fix(kc-dev-flow): harden portable PR delivery`

Raw `git diff --numstat 0980e992...264aabb`:

```text
98	1	docs/dev/_mods/pr-merge.md
12	1	scripts/kc-dev-flow-contract-test.py
247	0	scripts/pr-merge-portable-delivery.test.py
```

The focused commit changes only the trailing local runtime extension and its
tests. It adds mode-0600 body-file transport, immutable approved-candidate
identity, merge-tree preflight without rebase, exact-SHA refspec push, explicit
entity-worktree branch/repository resolution, qualified PR lookup with explicit
`--repo`, and restart-safe merged-sentinel commit followed by the ordinary
installed 0.26 merge guard.

### Top v2: policy-only direct child

- Branch: `spacedock-ensign/native-stacked-pr-policy-v2`
- Worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-native-stacked-pr-policy-v2`
- Head: `e5b2e07fe45da7fe6104b15573f7a199ecf4da8f`
- Parent and merge base:
  `264aabb017a36dcda0a740f28896086eab96bcc6`
- Commit: `docs(kc-dev-flow): route dependent changes through native stacks`

Raw `git diff --numstat 264aabb...e5b2e07`:

```text
5	4	docs/dev/README.md
46	0	docs/dev/_mods/pr-merge.md
79	6	scripts/kc-dev-flow-contract-test.py
```

The top diff contains exactly the three accepted policy paths above. It does
not change `scripts/pr-merge-portable-delivery.test.py`; the authoritative
four-row topology table, README delegation, strict numeric trigger, exception,
approval, Draft/linking, CI, and top-PR tracking semantics remain the sole top
layer.

### TDD evidence

All five cases were added before changing the runtime extension and each failed
for its intended missing behavior:

| Safety class | RED evidence | GREEN behavior |
| --- | --- | --- |
| Body file | `body-file contract missing: replaces the released shell-interpolated --body command` | A real mode-0600 file transported adversarial backticks, `$()`, `$HOME`, and embedded newlines byte-for-byte through a fake `gh --body-file`; no body content executed. |
| Candidate SHA | `candidate-SHA contract missing: CANDIDATE_SHA=...` | A real Git fixture recorded the candidate, moved `HEAD` after approval, preflighted the recorded SHA, pushed the exact refspec, and observed the remote branch at the approved candidate rather than moved `HEAD`. |
| Repository reference | `PR reference resolution table is not unique` | The test parses exact outcomes for `owner/repo#N`, `#N`, and `N`, and requires entity-worktree `CODE_REPO`, `BRANCH`, and explicit `--repo`. |
| Sentinel compatibility | `sentinel/guard sequence is incomplete` | The test requires ordered `pr=pr-merge:{N}` set, `spacedock state commit`, then ordinary 0.26 `merge guard`, and rejects direct terminal/archive writes. |
| Failure policy | `failure-policy contract missing: local kc-dev-flow compatibility override, not shipped pre3 parity` | The mod now preserves pending authority and state on push, mergeability, repository, or `gh` failure; it never treats local merge as authenticated terminal success. |

The integrated `kc-dev-flow` contract initially failed with all five RED rows,
then passed after only the local extension changed.

### Pre3 delta disposition

| Shipped pre3 behavior | Local disposition | Compatibility reason |
| --- | --- | --- |
| Mode-0600 temporary body plus `gh pr create --body-file` | Backported | Pure file/argv behavior; executable on 0.26 and protects Markdown bytes from shell interpolation. |
| Immutable `CANDIDATE_SHA`, merge-tree preflight, no post-approval rebase, exact-SHA refspec | Backported | Uses Git primitives available locally and preserves the exact approved commit. |
| Branch and code repository from entity worktree; qualified PR plus explicit `--repo` | Backported | Removes launch-directory ambiguity without requiring a newer Spacedock verb. |
| Durable `pr-merge:{N}` sentinel, state commit, then ordinary merge guard | Backported | Installed 0.26 provides both `state commit` and `merge guard`; this replaces unsafe direct terminalization. |
| Split-root immutable state audit tuple | Retained from accepted bottom | Already locally corrected and independently verified. |
| `spacedock gate consume` | Rejected | 0.27-only runtime surface; installed 0.26 does not provide it. |
| `merge guard --rework` | Rejected | 0.27-only flag; ordinary 0.26 guard remains the sole merge entry. |
| Push/mergeability/`gh` failure fallback to local merge | Rejected and locally overridden | kc-dev-flow `done` requires an authenticated merged product PR; failure must preserve authority/state and stop. |
| Role-generic PR-body extraction wording | Not backported | Outside the requested portable-delivery safety seam. |

### Acceptance and changed-path mapping

| Path/layer | Acceptance mapping | Exact evidence |
| --- | --- | --- |
| Bottom `docs/dev/_mods/pr-merge.md` | AC-1, AC-5 | Preserves released-body hash and installed-0.26 runtime while adding only portable safety overrides and fail-closed delivery. |
| Bottom `scripts/kc-dev-flow-contract-test.py` | AC-1, AC-5 | Runs the bounded portable behavior suite and keeps structural upstream/recovery/consumer guards. |
| Bottom `scripts/pr-merge-portable-delivery.test.py` | AC-1, AC-5 | Executes body-byte and candidate-SHA falsifiers; parses repository and sentinel semantics; enforces 0.26 exclusions and local failure policy. |
| Top `docs/dev/README.md` | AC-2, AC-3 | Delegates to the same authoritative topology predicates without a second readiness rule. |
| Top `docs/dev/_mods/pr-merge.md` | AC-2, AC-3, AC-4 | Adds only native-stack/parallel/single topology, strict trigger, exception, and approved Draft/link mechanics. |
| Top `scripts/kc-dev-flow-contract-test.py` | AC-2, AC-3, AC-4 | Parses the exact decision table and fails polarity/outcome drift while retaining all bottom checks. |

### Exact-head verification

At both exact heads, all of these exited zero:

- `python3 -m py_compile` for both Python contracts;
- `python3 scripts/pr-merge-portable-delivery.test.py` (5/5);
- `python3 scripts/kc-dev-flow-contract-test.py`;
- `bash scripts/dev-flow-state-prereq.test.sh`;
- `bash scripts/marketplace-verify.sh` (L0/L1 and all seven L2 installs);
- `bash scripts/version-parity-check.sh`;
- `bash scripts/skill-frontmatter-lint.test.sh` (12/12);
- `bash scripts/skill-frontmatter-lint.sh` (40/40); and
- `git diff --check`.

Spacedock 0.26.0 `internal/status` and `internal/cli` merge-guard fixtures passed.
The installed `spacedock 0.26.0 (contract 3)` exposes ordinary `state commit`
and `merge guard`; installed `gh stack link` still exposes the approved
bottom-to-top stack surface. The live holder prerequisite ran successfully
before this shared-state mutation.

The prior bottom, top, and combined evidence worktrees remain clean at
`0980e992c0f5f31a0e9c6d816d48f7bee3a8a5ae`,
`3ad8a4f8d35ac2efe1e839aa77291eb4521d9543`, and
`7b315696705840b0db4941d8205e53247ccafdd8`, respectively.

### Handoff and blockers

Track the top-v2 worktree and exact head above. There are no implementation
blockers. Any product push, Draft PR creation, native-stack link, readiness
change, merge, or terminalization remains captain/FO delivery work and was not
performed in this cycle.

## Stage Report: validation (cycle 3)

### Verdict

REJECTED at the exact stack bottom
`264aabb017a36dcda0a740f28896086eab96bcc6` and direct-child top
`e5b2e07fe45da7fe6104b15573f7a199ecf4da8f` against freshly fetched
`origin/main` `1745b13563dd60ee41f51066ef15d0bff4929cb0`.

Both exact heads are mechanically green and clean; released v0.12.2 identity,
formal pre3 provenance, removed-consumer cleanup, and 0.26 command availability
pass. Three Material contradictions plus one directly proven proof defect remain,
so no product
push, PR/link mutation, merge, terminalization, or stage advancement is allowed.

### Findings

- **[P1] Preserve Draft in the command that replaces PR creation —
  `docs/dev/_mods/pr-merge.md:188`.** The body-file replacement omits
  `--draft`; its test requires the same non-Draft argv. The earlier released
  command has `--draft` but is explicitly superseded, so bottom fails
  independently and combined single/exception routes can open ready PRs.
- **[P1] Bind hardening to each approved layer base —
  `docs/dev/_mods/pr-merge.md:188`.** Hardening resolves `$BASE` once from
  trunk and uses it for merge-tree and create, while the top policy requires
  each higher PR to target `{branch-below}`. No per-layer base reconciles the
  two recipes, so top can be preflighted and created against trunk.
- **[P1] Prove the whole stack landed before terminalizing from the tracked PR —
  `docs/dev/_mods/pr-merge.md:246`.** The mod stores only the top PR, queries
  only `state`, then writes a sentinel and runs guard. `gh stack link` is not the
  separate atomic `gh stack merge` operation; top can merge into the branch
  below before bottom lands on trunk. The query also omits approved head SHAs,
  required checks, and `mergedAt`, while installed guard writes its own current
  completion time. This conflicts with `docs/dev/README.md:327-329`.
- **[P2] Replace phrase-only safety cases with executable transcripts —
  `scripts/pr-merge-portable-delivery.test.py:159`.** A disposable exact-top
  mutant added ambient qualified lookup, continued after sentinel-commit
  failure, and automatic local-merge terminal success after failures. The three
  focused cases and integrated contract still passed. Body/candidate primitives
  and topology polarity are mutation-sensitive; repository, sentinel, and
  failure-policy cases are not.

### AC, path, diff, and deletion coverage

| AC | Verdict | Evidence |
| --- | --- | --- |
| AC-1 | FAIL | v0.12.2 equality, literal body bytes, immutable candidate/exact refspec, installed 0.26 verbs, and current fail-stop prose pass. Active create is non-Draft, terminal discovery misses authenticated head/check/mergedAt proof, and three safety cases accept contradictions. |
| AC-2 | FAIL | Decision rows, exact local graph, and `gh stack link` bottom-to-top help pass. Hardening still uses trunk for top, and top-only MERGED state is not atomic lower-layer proof. |
| AC-3 | PASS | Strict `>1,500 OR >20` semantics pass: 1,500/20 false; 1,501/20 and 1,500/21 true. Dependent green layers win at any size; all volume remains counted; polarity inversion fails. |
| AC-4 | FAIL | Exception heading/share/acknowledgment text passes, but its active replacement command can create the PR non-Draft. |
| AC-5 | PASS | No tracked live consumer remains for the artifact field, deleted transaction/audit functions or markers, or obsolete test names. Recovery stops without inventing authentication. |

Bottom `1745b135...264aabb` is 515 additions and 2,913 deletions over seven
paths. Top `264aabb...e5b2e07` is 130 additions and 10 deletions over exactly
three policy paths. Top remains policy-only.

| Path-layer | AC | Coverage |
| --- | --- | --- |
| bottom `docs/dev/README.md` | AC-1, AC-5 | Artifact deletion passes; terminal mergedAt/check rule exposes P1. |
| bottom `docs/dev/_mods/pr-merge.md` | AC-1, AC-5 | Full replacement/extension, pre3 delta, five hardening classes, failures, and split-root tuple reviewed. |
| deleted terminal transaction test | AC-5 | Its custom-artifact subject and all consumers are gone. |
| bottom recovery runbook | AC-5 | Refusal contract passes and preserves evidence. |
| deleted audit-link test | AC-5 | Its marked function is gone; tuple proof remains in contract/live state checks. |
| bottom integrated contract | AC-1, AC-5 | Hash/recovery/consumer checks pass; adversarial semantic blind spot reproduced. |
| bottom portable harness | AC-1, AC-5 | All 247 lines reviewed; two behavioral cases pass, three phrase-only cases fail validation. |
| top README/mod/contract | AC-2, AC-3, AC-4 | One table authority and polarity guard pass; Draft/base/terminal composition findings remain. |

Diff coverage: 100% path-layer coverage (10/10); all 645 sequential additions
classified or exercised; all 2,923 deletions covered by exact upstream-body
comparison and deleted-subject/consumer sweeps. The 99-line hardening plus
harness is not minimum: collapse the competing generic and stack-specific create
recipes into one Draft, body-file, exact-SHA, per-layer-base responsibility.

### Provenance, exact commands, and results

- Fresh `git fetch origin main --prune` left `origin/main` at the expected SHA.
  Bottom is two commits above it; top has bottom as its sole parent; both
  worktrees remained clean and range `git diff --check` passed.
- Fresh `git ls-remote` and GitHub API inventory resolved pre3 annotated tag
  object `5a0b9a13282bd0abd6d1e3479475acd809b73b12`, peeled commit
  `ffaeaef696cad492c8d40ab84939178e242aff2e`, prerelease publication
  `2026-08-09T17:05:53Z`, and no final `v0.27.0` tag/release.
- Shipped pre3 `mods/pr-merge.md` hashes to
  `0f2a4628a008e044b9d0faa67282597dfaa2ee56b6954f10028ca7d921b6e031`.
  The separate adopted pre3 `docs/dev/_mods/pr-merge.md` hashes to
  `44e7b345eee634b35780efe3106ad827b424661b45dd75aaeaec9fd90f38c4f2`;
  it was not used as the shipped comparison seam.
- Shipped v0.26.0 `mods/pr-merge.md` at peeled commit
  `ca136f83a579fd44c223321ae7f8fe7785c685f7` and normalized local baseline
  both hash to `a70a0ba4f9fb48a1c33e9f9e2c4ff3cb76b0a816d050a42bdbd6eced9fd15f64`.
- At each exact product head: Python compile, portable delivery 5/5, integrated
  contract, state-prereq refusal, version parity, frontmatter 12/12 and 40/40,
  marketplace L0/L1/all seven L2 installs, and diff checks exited 0.
- Clean v0.26 source: `go test -count=1 -v ./internal/status -run Merge` and
  `go test -count=1 -v ./internal/cli -run 'Merge|StateCommit'` exited 0.
- Installed 0.26: status/state commit/dispatch trunk/ordinary guard work;
  `spacedock gate consume` exits 2 `unknown command: gate`; guard `--rework`
  exits 1 `unknown argument: --rework`.
- Installed `gh 2.92.0`: link help confirms bottom-to-top, bottom `--base`, and
  `--open`; merge help identifies `gh stack merge` as the separate atomic
  all-or-nothing operation. The adopted mod never requires it.
- Installed guard fixture ran sentinel set -> state commit -> ordinary guard and
  archived with `completed: 2026-08-11T14:45:04Z`, proving guard does not source
  GitHub `mergedAt`.
- Mutant repository/sentinel/failure focused cases and integrated contract
  exited 0. Changing the dependent row to `One Draft PR` then exited 1 with
  `delivery-topology row polarity or required outcome drifted`.
- Immediately before this write,
  `scripts/dev-flow-state-prereq.sh /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/docs/dev`
  exited 0 at holder/remote `2fa66d0ae2c2c7a4ddbe81ad67f865a683c060bf`;
  bound-field validation returned PASS.

Lenses: behavior FAIL; contract/schema PASS for baseline and removals; state/concurrency FAIL for top-only sentinel; security/privacy PASS for body bytes/explicit repo with proof residual; runtime/platform PASS for 0.26 commands; docs/policy FAIL for terminal rule and competing bases; delivery FAIL; test-quality FAIL (4 findings: 3 P1, 1 P2; falsifiers: Draft replacement argv, one per-layer base, full-stack exact-head/check/mergedAt proof, and contradictory mutants fail).
Adversarial: FAIL — body bytes, moved HEAD, exact refspec, strict thresholds, and polarity pass; Draft argv, per-layer base, top-only tracking, and three semantic mutants fail.
Cross-model: not_needed — exact text, tagged primary source, installed CLI behavior, graph evidence, and deterministic mutants settle the findings at high confidence; no optional pass launched.
E2E: N/A — workflow policy/CLI orchestration has no app/browser journey; exact source/installed CLI fixtures, Git/state worktrees, help surfaces, and mutations cover the runtime boundary. Real PR creation/linking is withheld delivery authority.
Origin re-observation: FAIL — Reported scenario: 0.26 executes the adopted merge ceremony, pre3 safety remains portable/fail-closed, and native Draft layers land bottom-to-top before terminalization | Originating runtime kind: installed Spacedock/GitHub CLIs plus Git/state worktrees | Re-observation artifact/revision: origin/main `1745b13563dd60ee41f51066ef15d0bff4929cb0`, bottom `264aabb017a36dcda0a740f28896086eab96bcc6`, top `e5b2e07fe45da7fe6104b15573f7a199ecf4da8f`, pre3 `ffaeaef696cad492c8d40ab84939178e242aff2e`, v0.26.0 `ca136f83a579fd44c223321ae7f8fe7785c685f7`, installed spacedock 0.26.0, gh 2.92.0, state `2fa66d0ae2c2c7a4ddbe81ad67f865a683c060bf` blob `67858078652a000d1c4bfa500533e784b7677d6f` | Equivalent-runtime rationale: exact tags, actual layer graph, installed commands, real Git primitives, installed guard mutation, and live split-root state; outward PR mutation stayed with delivery owner | Falsifier kind: refusal and mutation | Result: baseline/runtime checks pass, but active create is non-Draft/trunk-based, top-only state is insufficient terminal proof, and contradictory safety mutants remain green.

### Engineering-manager judgment

```yaml
science_officer_em_upward_report:
  em_judgment: "Reject the exact stack: baseline and runtime compatibility pass, but Draft, per-layer base, authenticated stack terminalization, and behavioral proof remain unsatisfied."
  evidence_synthesis: "Fresh origin/main and the requested bottom/direct-child-top graph are exact and clean; primary tags and hashes prove shipped pre3 versus adopted-copy provenance and exact v0.12.2 normalization. Active argv/data flow, installed CLI behavior, and deterministic mutants establish three Material contradictions and one proof defect despite green mechanical suites."
  risk_tradeoff_call: "Returning costs one bounded recipe consolidation, terminal-evidence correction, and executable safety matrix, but avoids ready PRs, trunk-based top PRs, premature terminalization, and phrase-only false confidence; accepting wording leaves those observable failures intact."
  recommendation: "Return: use one Draft body-file exact-SHA recipe parameterized by layer base; require full-stack exact-head, checks, and mergedAt evidence; make repository, sentinel, and failure mutants fail."
  route: return
  confidence: high
  multi_model: not_needed
  fo_boundary: "FO may route this rejection to implementation, but may not waive findings, push, create/link/merge PRs, or terminalize."
  engineering_judgment:
    question: "Do bottom 264aabb017a36dcda0a740f28896086eab96bcc6 and top e5b2e07fe45da7fe6104b15573f7a199ecf4da8f satisfy all ACs after pre3 hardening?"
    revision: "1745b13563dd60ee41f51066ef15d0bff4929cb0 -> 264aabb017a36dcda0a740f28896086eab96bcc6 -> e5b2e07fe45da7fe6104b15573f7a199ecf4da8f"
    evidence_synthesis: "Fresh origin/main and the requested bottom/direct-child-top graph are exact and clean; primary tags and hashes prove shipped pre3 versus adopted-copy provenance and exact v0.12.2 normalization. Active argv/data flow, installed CLI behavior, and deterministic mutants establish three Material contradictions and one proof defect despite green mechanical suites."
    adjudications:
      - finding: "Replacement body-file command preserves Draft."
        disposition: unsupported
        basis: "The active argv omits --draft and the harness requires that argv."
      - finding: "Hardening composes with each native-stack base."
        disposition: unsupported
        basis: "Hardening uses trunk BASE while top policy requires branch-below; no per-layer seam exists."
      - finding: "Tracked top MERGED proves authenticated whole-stack delivery."
        disposition: unsupported
        basis: "Link is not atomic merge; state-only lookup omits all heads, checks, and mergedAt, and guard supplies current completion time."
      - finding: "Every hardening class has behaviorally falsifiable proof."
        disposition: unsupported
        basis: "Ambient lookup, skipped sentinel commit, and local-terminal-success contradictions pass focused and integrated contracts."
    risk_tradeoff: "Returning costs one bounded recipe consolidation, terminal-evidence correction, and executable safety matrix, but avoids ready PRs, trunk-based top PRs, premature terminalization, and phrase-only false confidence; accepting wording leaves those observable failures intact."
    recommendation: "Return: use one Draft body-file exact-SHA recipe parameterized by layer base; require full-stack exact-head, checks, and mergedAt evidence; make repository, sentinel, and failure mutants fail."
    route: return
    confidence: high
    dissent: "Implementation reports independent green and Draft-safe behavior; mechanical suites are green, but active argv/base flow, installed terminal behavior, and passing contradictory mutants disprove those outcome claims."
    disproof_condition: "Change route only when replacement argv is Draft/per-layer-base-bound, terminalization proves all approved layer heads/checks and product mergedAt, and all named safety mutants fail."
    authority_boundary: "Captain retains scope/topology/Draft-body/irreversible delivery; validation owns this rejection; work-item/FO may route back; delivery owner alone may push, create, link, merge, ready, or close."
```

### Summary

Return to implementation without terminalizing. Preserve the exact baseline,
provenance, consumer removal, literal body transport, candidate-SHA protection,
strict topology table, and fail-closed recovery; repair the four findings and
re-enter validation fresh. This cycle changed only this authorized state report.

## Stage Report: implementation (cycle 5)

### Outcome

Repaired the four cycle-3 findings as a fresh two-layer local stack. The bottom
now defines one canonical Draft delivery unit and an authenticated single-PR
completion decision. The top composes that exact unit per layer and requires
native atomic-stack landing evidence before the stored top PR can drive the
ordinary 0.26 sentinel/guard transcript. No product branch was pushed and no
PR, ready transition, stack link, merge, or terminalization was performed.

The tracked worktree is now
`.worktrees/spacedock-ensign-native-stacked-pr-policy-v3`.

### Exact layers

Bottom:

- Branch: `spacedock-ensign/pr-merge-runtime-alignment-v3`
- Worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-pr-merge-runtime-alignment-v3`
- Head: `647d4c87805f0dde8b71d1153d2c226edb129d87`
- Parent/merge base: `264aabb017a36dcda0a740f28896086eab96bcc6`
- Commit: `fix(kc-dev-flow): bind portable PR delivery evidence`

```text
75	55	docs/dev/_mods/pr-merge.md
111	223	scripts/pr-merge-portable-delivery.test.py
```

Top:

- Branch: `spacedock-ensign/native-stacked-pr-policy-v3`
- Worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-native-stacked-pr-policy-v3`
- Head: `a87326b901bebd88858beea85a463b1fbd1a26cf`
- Parent/merge base: `647d4c87805f0dde8b71d1153d2c226edb129d87`
- Commit: `docs(kc-dev-flow): route dependent changes through native stacks`

```text
5	4	docs/dev/README.md
99	0	docs/dev/_mods/pr-merge.md
182	6	scripts/kc-dev-flow-contract-test.py
```

The top remains one direct-child policy commit across exactly the prior three
policy paths. The strict four-row topology table and its thresholds/polarity are
unchanged.

### RED/GREEN and mutants

Bottom RED reported missing canonical delivery/completion tables, Draft create,
per-unit base/candidate preflight, exact refspec, Candidate metadata, explicit
repository proof/checks, and failed-state-commit stop. GREEN now parses the
exact tables and rejects all three proven mutants:

- ambient `gh pr view` without `--repo` — REJECTED;
- continuing to guard after failed `spacedock state commit` — REJECTED;
- automatic local-merge terminal success — REJECTED.

The reduced 135-line portable contract removes the fake-gh and scratch-Git
halves. It checks the mod's active argv/data contract directly: one canonical
`gh pr create` contains `--draft`, explicit repo, unit base/head/title, and
mode-0600 body file; the reviewed body contains exactly one full
`Candidate: {full approved SHA}` audit line.

Top RED reported missing per-layer unit/base binding, URL-only link, atomic
stack completion table, explicit API/PR/check queries, atomic merge, non-stack
refusal, and captain-authorized ready gate. GREEN parses both exact tables and
rejects these scoped mutants:

- binding a higher layer to trunk SHA instead of the approved candidate below;
- linking branch names instead of already-created full PR URLs;
- replacing native atomic `gh stack merge` with individual `gh pr merge`.

Draft remains the creation default. Each layer may run
`gh pr ready "$LAYER_PR_URL"` only after its required checks and review are green
and the captain explicitly authorizes readiness; atomic stack merge is forbidden
while any layer remains Draft.

### Completion and source contract

For a single PR, startup/idle now requires an explicit repository, exactly one
full Candidate SHA from the approved body, matching GitHub `headRefOid`,
non-empty `mergedAt`, and successful explicit-repository required checks. Only
then may it set `pr-merge:{N}`, commit state, and invoke ordinary 0.26 guard;
every missing, ambiguous, or failed proof stops.

For a native stack, already-created full PR URLs are linked bottom-to-top. The
bottom unit targets trunk; every higher unit targets the branch below and uses
the approved candidate SHA below as its exact preflight base SHA. Landing uses
GitHub native atomic stack merge, never an individual PR merge.

The public-preview source contract is queried explicitly as
`GET repos/{repo}/stacks?pull_request={top}`. The response contract used here is
one stack `number`, `base.ref`, and ordered `pull_requests[]` entries containing
`number`, `merged_at`, `head.ref`, and `head.sha`. Completion requires exactly
one matching stack, correct trunk base, stored top in final position, every
ordered entry merged, each entry/PR head equal to its approved body Candidate,
and required checks green. The stored top PR's `mergedAt` supplies completion
time; a non-stack top merge stops without sentinel or guard.

### AC and path mapping

| Layer/path | AC mapping | Evidence |
| --- | --- | --- |
| Bottom `docs/dev/_mods/pr-merge.md` | AC-1, AC-5 | One parameterized Draft unit plus fail-closed authenticated single-PR completion; normalized released v0.12.2 body remains invariant. |
| Bottom `scripts/pr-merge-portable-delivery.test.py` | AC-1, AC-5 | Exact unit/completion parsers and three named contradiction mutants. |
| Top `docs/dev/README.md` | AC-2, AC-3 | Still delegates to unchanged authoritative topology predicates. |
| Top `docs/dev/_mods/pr-merge.md` | AC-2, AC-3, AC-4, AC-5 | Per-layer canonical units, URL linking, captain-authorized ready gate, atomic merge, full-stack completion proof, unchanged threshold/exception policy. |
| Top `scripts/kc-dev-flow-contract-test.py` | AC-2, AC-3, AC-4, AC-5 | Exact topology/composition/completion tables and three scoped stack mutants. |

### Verification and handoff

- Exact bottom passed the focused portable mutant suite, independent integrated
  contract, and diff check.
- Exact top passed the portable/integrated contracts, marketplace L0/L1 plus
  all seven L2 installs, version parity, frontmatter tests 12/12, frontmatter
  lint 40/40, and diff check.
- Installed `gh stack link` and `gh stack merge` command surfaces are present.
- The live state prerequisite passed before this shared-state update.
- v2 and all older evidence branches/worktrees remain untouched.

There are no implementation blockers. Delivery authority remains with the
captain/FO; this cycle performed no outward product mutation.
