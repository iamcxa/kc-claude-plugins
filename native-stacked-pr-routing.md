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
worktree: .worktrees/spacedock-ensign-native-stacked-pr-routing
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
contract plus one bounded local routing section. Preserve Draft PR delivery,
remove only artifact machinery with no released consumer, and use numeric change
shape only to require a topology decision.

## Design determination

Design is required because a single entity may need multiple dependent PRs and
because line-count policy can be gamed. The accepted topology is GitHub native:
the bottom PR targets trunk and every higher PR targets the branch below.

Ideation EM route: `narrow`. The narrowed design defines merge-base measurement,
keeps mechanical volume in the observed total, makes semantic seams override
numeric thresholds, and records the top PR as the entity's tracked `pr` after
the captain approves all Draft PR bodies.

## Acceptance criteria

**AC-1 — The adopted merge hook executes against Spacedock 0.26.x and contains
only a bounded local Draft/native-stack extension to released `pr-merge`
v0.12.2.**
Verified by: compare the retained upstream body byte-for-byte after removing the
marked local extension, then exercise `spacedock merge guard` over its released
fixtures. Falsified by: an unreleased `spacedock gate` command or unrelated local
artifact protocol remains.

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
