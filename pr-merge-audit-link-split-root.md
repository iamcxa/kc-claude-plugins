---
id: w1py17w13ga14nd3k6sbp358
title: pr-merge builds a dead audit link under split-root state
status: ideation
source: found by the FO while assembling xn's PR draft, 2026-07-25
started: 2026-07-29T06:07:23Z
completed:
verdict:
worktree:
issue:
pr:
design: required
lane: main
---

## Problem

`_mods/pr-merge.md`'s audit-link extraction rule formats the link as
`[{short-id}](/{owner}/{repo}/blob/{short-sha}/{path-to-entity-file})`, where `short-sha` comes
from `git rev-parse --short HEAD` in the code worktree. That assumes the entity file lives in
the code repo at a path reachable from the code branch — true for single-root workflows, false
for this one.

This workflow is split-root (`state: .spacedock-state`). Verified on xn's branch:
`git ls-tree -r HEAD -- docs/dev` lists only `README.md`, `_mods/`, and `ledger.csv` — the
entity files are not on the code branch at all. They live at the ROOT of the `spacedock-state/dev`
branch. So the templated link 404s.

The FO worked around it by hand for xn (pointing at a `spacedock-state/dev` commit SHA plus the
branch-root filename), but every future PR from a split-root workflow will hit the same thing.
Whatever the fix is, note that using the branch NAME is ambiguous to GitHub because it contains
a slash (`spacedock-state/dev`); a commit SHA avoids that.

## Measurement

D1 launched 2026-07-29T06:07:23Z | tokens: n/a (Codex runtime did not expose per-worker usage)

## Ideation

### TL;DR

Keep the current single-root audit-link recipe and add one split-root branch driven by
Spacedock's canonical entity resolution. For inline state, the link continues to use the code
worktree commit and repo-relative entity path. For split-root state, it uses the full commit SHA
of the resolved state checkout and the entity's path relative to that checkout. A direct contract
test must execute the recipe against both layouts; a prose grep is not evidence.

Scope questions are skipped because the captain supplied a single-seam scope, the exact failure
and preferred commit-SHA direction, the required compatibility case, and explicit exclusions.
There is no unresolved scope choice to ask back.

### Scope and appetite

In scope:

- Change only audit-link input resolution and the three matching descriptions in
  `docs/dev/_mods/pr-merge.md`.
- Add one direct contract test beside the mod, or in the repository's existing shell-test
  surface, that executes the exact recipe against split-root and single-root fixtures.
- Preserve the audit label, PR-body placement, owner/repo resolution, short-id resolution, and
  all non-audit PR lifecycle behavior.

Out of scope:

- PR review convergence, the parked `skill-ablation-harness` (5b), `presentation-renderer` (fa),
  `reference-progressive-load` (sk), and the `n9 -> 11` or `vf -> x0` implementation sequences.
- Changing Spacedock's state schema, adding a new CLI command, or repairing state synchronization.
- Repairing the measurement ledger residue noted below.

Appetite: 45 minutes for implementation and scoped tests, with a 15-minute tolerance for one
bounded repair round. If canonical `status --resolve` cannot distinguish the two fixture layouts,
or the exact recipe cannot be exercised without adding a new runtime/helper surface, stop and
return for re-cut; do not widen into Spacedock runtime changes or weaken the proof.

### Options considered

1. **Branch on canonical entity resolution (chosen).** Run
   `spacedock status --workflow-dir {dir} --resolve {entity ref} --json` once. When its canonical
   state root is the workflow directory, keep the existing code-worktree SHA and repo-relative
   path. When the canonical state root is a separate checkout, use that checkout's full `HEAD` SHA
   and the resolved entity path relative to it.
2. **Always derive SHA and path from the entity file's owning checkout.** This is shorter, but it
   changes single-root behavior when the FO checkout and code worktree are different: the audit
   link could point at the FO branch rather than the PR head.
3. **Parse `state:` from README or use `spacedock-state/dev` in the URL.** Rejected. Hand-parsing
   workflow YAML duplicates Spacedock's resolver, while a slash-bearing branch ref is ambiguous
   in GitHub blob URLs and is mutable.

Fastest path: hard-code this workflow's `.spacedock-state` checkout, matching Spacedock's own
dogfood mod. Smallest safe cut: the chosen two-case contract, because it fixes this workflow
without regressing the reusable mod's inline behavior. Taking the cheap path: one conditional
audit-input seam and one two-layout contract test. The more thorough option not taken is a new
Spacedock CLI audit-link renderer; it is unnecessary for these acceptance criteria and outside
this repository's ownership.

### Design determination

`design: required`. This task changes the audit-link interface in the PR-body contract.

Before:

```text
[{short-id}](/{owner}/{repo}/blob/{code-short-sha}/{code-repo-relative-entity-path})
```

After:

```text
inline:     [{short-id}](/{owner}/{repo}/blob/{code-short-sha}/{code-repo-relative-entity-path})
split-root: [{short-id}](/{owner}/{repo}/blob/{full-state-sha}/{state-root-relative-entity-path})
```

The discriminant and path source are the JSON returned by
`spacedock status --workflow-dir {dir} --resolve {entity ref} --json`, not an inferred branch
name. The split-root tuple must pass
`git -C {resolved-state-root} cat-file -e "{full-state-sha}:{state-relative-path}"` before the
body is accepted. No branch ref appears in the split-root URL, so archival or later branch movement
cannot invalidate the original target.

### Reverse-recovery audit

Audited against freshly fetched `origin/main @
85959dce110834f67d6d0e5193991a7c4b315696`.

| Layer | Evidence | Classification |
|---|---|---|
| PR merge entry | `docs/dev/_mods/pr-merge.md:31-39` | WORKING for PR-body assembly |
| Entity resolver | `spacedock status --workflow-dir docs/dev --resolve w1 --json` returned canonical split-root `workflow` and absolute `path` | WORKING |
| Inline audit tuple | `docs/dev/_mods/pr-merge.md:37,71,83` | WORKING contract to preserve |
| Split-root audit tuple | Same lines bind code SHA plus code-relative path although the entity is absent from the code tree | EXISTS_BROKEN |
| Proven split-root pattern | `spacedock-v1:docs/dev/_mods/pr-merge.md:43-97` uses full state SHA plus state-relative path | WORKING precedent, workflow-specific |
| Direct contract harness | No test in this repo executes this mod's audit recipe; searches covered tracked test scripts and all `pr-merge.md` references | MISSING |

Disproof hooks: a `status --resolve` result that does not expose distinct canonical roots would
invalidate the chosen discriminant; a `git cat-file -e` success for the current code-SHA/code-path
tuple would invalidate the defect classification. Neither occurred. The live baseline probe against
`origin/main` returned GitHub 404 for
`docs/dev/pr-merge-audit-link-split-root.md`, while state commit
`82192534e89f1503b5be11931b1e0281b295c6f5` resolved
`pr-merge-audit-link-split-root.md` through the GitHub contents API.

No spike is needed. The risky mechanisms are already proven: Spacedock returns the canonical
entity path/root, `git ls-files --full-name` returns the correct relative path for both checked
layouts, and `git cat-file -e` verifies that each SHA/path tuple names a blob.

### Implementation and test plan

One worker session is sufficient: one instruction surface, one conditional behavior, and one
two-case test file.

1. Freeze the implementation head and re-run the resolver for this entity with
   `--workflow-dir docs/dev`; confirm the target mod has not drifted from the three audit-link
   descriptions at ideation lines 37, 71, and 83.
2. Write the direct shell contract test first. It must extract and execute the audit-resolution
   recipe from a fenced/marked block in `pr-merge.md`, following the tested-recipe pattern already
   used by `review-shadow.test.sh`; it must not pass by grepping for new prose.
3. Capture RED: the split-root fixture must produce the wrong code SHA/path (or lack the new
   executable recipe) before the edit, while the single-root baseline remains green.
4. Update the merge-hook input paragraph, template row, and extraction-rule row together. Resolve
   the entity once via `spacedock status --workflow-dir {dir} --resolve {entity ref} --json`.
   Keep the old worktree tuple for inline state; for a separate state root, compute full `HEAD`,
   state-relative path, and require `git cat-file -e` on that tuple.
5. Run GREEN against synthetic git fixtures:
   - split-root README plus a separate `.spacedock-state` git checkout containing a root entity;
   - inline README plus an entity tracked in the code repository.
   Assert the exact final Markdown link in each case, not only the intermediate SHA/path.
6. Re-run `bash -n` and ShellCheck on the contract test. Run the split-root live probe against the
   pushed state SHA and a single-root probe against a reachable code SHA/path. Confirm the product
   diff contains only the mod and its direct test.

E2E browser/full-stack testing is skipped: this is an agent-instruction/PR-body contract, not a
browser, service, or user-flow wiring change. The live GitHub API probe is the end-to-end check for
the value surface that does change: whether the emitted blob target exists remotely.

No `PRODUCT.md` or `ARCHITECTURE.md` diff is proposed. The published behavior is defined by
`docs/dev/_mods/pr-merge.md` itself; the before/after contract above is the concrete doc diff.

## Acceptance criteria

**AC-1 — Split-root links resolve.**

For a workflow whose canonical entity root is a separate state checkout, the PR body's audit link
contains the entity short ID, a full state commit SHA, and the entity's state-root-relative path.
Verified by: the direct split-root fixture asserting the exact Markdown link,
`git cat-file -e "{state-sha}:{state-path}"`, and a GitHub contents API request for the same pushed
SHA/path returning success. Falsified by a code-worktree SHA, a `docs/dev/` path prefix, a branch
ref, or remote 404.

**AC-2 — Single-root links retain their target.**

For an inline workflow, the audit link retains the existing code-worktree commit/path semantics
and points at the inline entity on the PR head. Verified by: the direct inline fixture asserting
the exact Markdown link and `git cat-file -e "{code-sha}:{code-relative-path}"`; the fixture must
use distinct FO and code worktrees so an entity-checkout-only implementation fails. Falsified by
a state-only/FO SHA, a path relative to the workflow directory instead of the code repository, or
a missing blob.

**AC-3 — The executable contract owns both cases.**

One marked recipe in `pr-merge.md` produces both tuples, and the direct test executes that recipe
rather than duplicating it. Verified by: the test's extraction-and-source step, RED-before-GREEN
capture, and a mutation check in which forcing either branch makes its corresponding fixture fail.
Falsified by a prose grep, copied resolver logic in the test, or either fixture passing after its
branch is neutralized.

**AC-4 — Neighboring PR behavior is unchanged.**

Only audit-link input resolution changes; owner/repo and short-id lookup, PR body ordering,
approval, push/create, and merge tracking remain unchanged. Verified by: a path-scoped
`git diff --check` and review of the final diff showing changes only in the audit recipe's three
descriptions plus its direct test. Falsified by any edit to review convergence, lifecycle commands,
templates outside the audit row, or unrelated tests/docs.

### Risks and pre-mortem

- A split-root state commit that exists only locally still produces a structurally correct but
  remotely dead URL; the live GitHub API probe therefore uses the exact pushed SHA.
- Comparing filesystem locations or git-common-dir identities instead of canonical workflow roots
  can misclassify a single-root workflow with a separate code worktree.
- A test that reimplements the Markdown recipe can stay green while the agent-facing contract
  regresses; recipe extraction is mandatory.

If this ships exactly per spec and still fails, the most likely cause is a hidden assumption:
`status --resolve` identifies the right entity checkout, but the state commit was not pushed to the
same remote before the PR body was published.

### Process residue note

At `tm` closeout, `redundant-rule-removal` was archived PASSED but no matching task row was present
in `docs/dev/ledger.csv`. This is process residue only. It is not repaired or counted as part of
this task.

### Summary

Specified a two-case audit-link contract that preserves inline behavior and binds split-root links
to an immutable state commit, with executable RED/GREEN fixtures and live remote-resolution proof.

## Stage Report: ideation

TL;DR: Design and proof are ready for gate review: one conditional audit-input seam, one direct
two-layout contract test, and no product edits during ideation.

- DONE: Defined the smallest split-root-aware audit-link contract while preserving the existing
  single-root code-worktree target.
- DONE: Chose canonical `status --resolve` output over branch-name parsing, filesystem guesses, or
  a new Spacedock runtime surface.
- DONE: Recorded `design: required` with the exact before/after PR-body link shapes.
- DONE: Completed the reverse-recovery trace against fetched `origin/main @ 85959dc`; classified
  the existing link assembler and resolver as present, with one EXISTS_BROKEN tuple seam.
- DONE: Proved the baseline remotely: the code-SHA/code-path URL returns 404 while the full state
  SHA plus state-root filename resolves through GitHub.
- DONE: AC-1 — specified the exact split-root Markdown link, local blob-existence check, and live
  GitHub API success proof; a code SHA/path, branch ref, or 404 falsifies it.
- DONE: AC-2 — specified a distinct-FO/code-worktree inline fixture that preserves the old PR-head
  target and fails if the implementation substitutes the entity checkout's SHA/path.
- DONE: AC-3 — required the test to extract and execute the mod's marked recipe, capture
  RED-before-GREEN, and neutralize each branch so a copied/prose-grep test cannot pass.
- DONE: AC-4 — bounded the diff to the three audit-link descriptions and their direct contract
  test, with path-scoped diff review as the falsifier for neighboring PR behavior.
- DONE: Recorded a 45-minute appetite, 15-minute tolerance, one-worker sizing, stop/re-cut
  condition, risks, pre-mortem, exclusions, and RED-before-GREEN implementation plan.
- SKIPPED: Browser/full-stack E2E because the changed value surface is a PR-body blob target; the
  direct recipe test and live GitHub API probe cover that surface end to end.
- SKIPPED: Measurement-ledger repair. The `tm` residue is noted only, per dispatch.
