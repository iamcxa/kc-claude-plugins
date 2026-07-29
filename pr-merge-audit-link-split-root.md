---
id: w1py17w13ga14nd3k6sbp358
title: pr-merge builds a dead audit link under split-root state
status: validation
source: found by the FO while assembling xn's PR draft, 2026-07-25
started: 2026-07-29T06:07:23Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-pr-merge-audit-link-split-root
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
D2 launched 2026-07-29T06:34:23Z | tokens: n/a (Codex runtime did not expose per-worker usage)
D3 launched 2026-07-29T06:56:49Z | tokens: pending

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

- Change only the marked executable audit-link recipe block and its three matching descriptions
  in `docs/dev/_mods/pr-merge.md`.
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

Resolver failure is fail-closed. A non-zero `status --resolve`, unparseable JSON, or a JSON object
whose `workflow` or `path` key is missing, non-string, or empty stops audit-link construction and
reports the exact resolver failure to the captain. None of those cases may fall back to the
code-worktree SHA/path or to the neighboring literal `main` fallback used by the older
worktree-`rev-parse` failure path. The PR body is not accepted until canonical entity resolution
has produced both required keys and the chosen SHA/path tuple passes its blob-existence check.

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
2. First install and commit a marked executable recipe block that encodes the current buggy
   code-worktree-short-SHA/code-repo-relative-path behavior byte-for-byte; this baseline commit
   changes representation only, not resolution semantics.
3. Write the direct shell contract test to extract and execute that committed baseline recipe,
   following the tested-recipe pattern already used by `review-shadow.test.sh`; it must not pass by
   grepping for new prose. Capture RED by running the extracted current recipe against the
   split-root fixture and observing
   `git cat-file -e "{code-short-sha}:{code-repo-relative-entity-path}"` exit non-zero. Mere absence
   of the new recipe, an extraction failure, or a syntax error does not count as RED; the harness
   must first prove that it executed the committed buggy baseline and produced the expected old
   tuple. The single-root baseline remains green.
4. Update the merge-hook input paragraph, template row, and extraction-rule row together. Resolve
   the entity once via `spacedock status --workflow-dir {dir} --resolve {entity ref} --json`.
   Keep the old worktree tuple for inline state; for a separate state root, compute full `HEAD`,
   state-relative path, and require `git cat-file -e` on that tuple.
5. Run GREEN against synthetic git fixtures:
   - split-root README plus a separate `.spacedock-state` git checkout containing a root entity;
   - inline README plus an entity tracked in the code repository.
   Assert the exact final Markdown link in each case, not only the intermediate SHA/path.
6. Run negative resolver fixtures through the same extracted recipe: command exits non-zero,
   malformed JSON, missing `workflow`, and missing `path`. Each must return non-zero, emit a
   specific diagnostic, and emit no SHA/path tuple or Markdown link. A mutation that substitutes
   the code tuple or literal `main` must turn these cases red.
7. Re-run `bash -n` and ShellCheck on the contract test. Run the split-root live probe against the
   pushed state SHA and a single-root probe against a reachable code SHA/path. Confirm the product
   diff contains only the marked recipe block, its three descriptions, and the direct test.

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
`git diff --check` and review of the final diff showing changes only in the marked executable
audit recipe block, its three matching descriptions, and its direct test. Falsified by any edit to
review convergence, lifecycle commands, templates outside the audit row, or unrelated tests/docs.

**AC-5 — Resolver failures stop link construction.**

Audit-link construction stops when `status --resolve` exits non-zero, emits malformed JSON, or
omits either required `workflow` or `path` key. Verified by: four negative fixtures executing the
same marked recipe and asserting non-zero exit, a case-specific diagnostic, and zero emitted
SHA/path tuples or Markdown links; a mutation that falls back to the code tuple or literal `main`
must make the corresponding fixture fail. Falsified by any PR body containing an audit link after
one of these resolver failures, or by a silent/ambiguous failure with no captain-facing reason.

### Risks and pre-mortem

- A split-root state commit that exists only locally still produces a structurally correct but
  remotely dead URL; the live GitHub API probe therefore uses the exact pushed SHA.
- Comparing filesystem locations or git-common-dir identities instead of canonical workflow roots
  can misclassify a single-root workflow with a separate code worktree.
- A test that reimplements the Markdown recipe can stay green while the agent-facing contract
  regresses; recipe extraction is mandatory.
- Resolver error handling that reuses the neighboring `main` fallback can turn a visible
  resolution failure back into a plausible-looking dead link; negative fixtures require no output
  tuple or link.

If this ships exactly per spec and still fails, the most likely cause is a hidden assumption:
`status --resolve` identifies the right entity checkout, but the state commit was not pushed to the
same remote before the PR body was published.

### Process residue note

At `tm` closeout, `redundant-rule-removal` was archived PASSED but no matching task row was present
in `docs/dev/ledger.csv`. This is process residue only. It is not repaired or counted as part of
this task.

### Summary

Specified a fail-closed two-case audit-link contract that preserves inline behavior and binds
split-root links to an immutable state commit, with an executed buggy-baseline RED, resolver
negative fixtures, GREEN layout fixtures, and live remote-resolution proof.

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

## Stage Report: ideation (cycle 2 — EM narrow repair)

TL;DR: Tightened only the three reviewed seams: RED now requires executing a committed buggy
baseline, resolver failures stop without fallback, and the declared diff scope includes the marked
recipe block.

- DONE: AC-1 — preserved the split-root full-state-SHA/state-relative-path contract and its local
  plus live-remote resolution evidence.
- DONE: AC-2 — preserved the distinct-FO/code-worktree inline fixture and unchanged PR-head target.
- DONE: AC-3 — removed the missing-recipe escape hatch: implementation first commits the current
  buggy recipe, then the extracted recipe must produce the old tuple and `git cat-file -e` must
  fail against the split-root fixture before GREEN work begins.
- DONE: AC-4 — reconciled scope everywhere to include the marked executable recipe block, its
  three matching descriptions, and the direct contract test.
- DONE: AC-5 — specified fail-closed handling and falsifiable negative fixtures for non-zero
  resolver exit, malformed JSON, missing `workflow`, and missing `path`; none may emit a tuple/link
  or fall back to the code tuple or literal `main`.
- DONE: Preserved the existing design choice, 45-minute appetite, 15-minute tolerance, one-worker
  sizing, exclusions, and process-residue boundary.
- SKIPPED: Product edits and measurement-ledger repair; this correction touched the ideation state
  artifact only.

## Stage Report: implementation — 2026-07-29

### Summary

Implemented the marked audit-link recipe so inline workflows keep the code-worktree tuple while
split-root workflows link the resolved state checkout's full commit SHA and root-relative entity
path. Resolver and blob failures now stop link construction with case-specific diagnostics.

**Code commits:** `55031ae` (`fix(kc-pr-flow): mark current audit link recipe`) records the
representation-only buggy baseline; `38fa874` (`fix(kc-pr-flow): resolve split-root audit links`)
contains the repair and direct contract test.

- DONE: Added one extractable `pr-merge-audit-link-recipe` block and updated only the merge-hook
  input description, PR-body template audit row, and audit extraction row.
- DONE: Preserved inline owner/repo, short-id, code-short-SHA, and code-repository-relative-path
  behavior with distinct FO and code worktrees in the fixture.
- DONE: Split-root resolution now uses one canonical `status --resolve --json` call, a full state
  SHA, a state-root-relative path, and `git cat-file -e` before emitting the Markdown link.
- DONE: Nonzero resolution, malformed JSON, missing keys, empty strings, non-string values, and a
  tracked-but-uncommitted missing blob all return nonzero, emit a case-specific diagnostic, and
  emit no tuple or link.
- DONE: Final code diff is limited to `docs/dev/_mods/pr-merge.md` and
  `kc-pr-flow/scripts/pr-merge-audit-link.test.sh`; review convergence, parked lanes, and ledger
  residue were not touched.

### RED → GREEN evidence

- Committed buggy baseline `55031ae`: the extracted recipe executed successfully for inline state
  but emitted `[split](/acme/widgets/blob/<code-short-sha>/docs/dev-split/split.md)` for split-root
  state. The arrangement check confirmed `git cat-file -e` failed for that exact old tuple.
  Initial RED was **7 passed / 25 failed**: the split-root exact-link assertion failed for the
  expected old tuple, and every resolver-error fixture still emitted a link.
- First GREEN was **32 passed / 0 failed** after canonical resolution and fail-closed validation.
- Blob-existence guard received its own loop: with the guard removed, a staged-only state entity
  produced RED **32 passed / 3 failed** by emitting a full-SHA link to a blob absent from `HEAD`;
  restoring the minimal `cat-file -e` guard produced final GREEN **35 passed / 0 failed**.

### Verification evidence

- `bash -n kc-pr-flow/scripts/pr-merge-audit-link.test.sh` — exit 0.
- `bash kc-pr-flow/scripts/pr-merge-audit-link.test.sh` — **35 passed / 0 failed** on committed
  head `38fa874`.
- CI-pinned ShellCheck v0.9.0 Docker run over the direct test and extracted recipe — clean.
- `bash kc-pr-flow/scripts/review-shadow.test.sh` — **213 passed / 0 failed**.
- Forced-inline, forced-split, and literal-`main` fallback mutations each turned the direct
  contract red.
- Live recipe output:
  `[w1](/iamcxa/kc-claude-plugins/blob/976612379bfa2b47a3e753fdfcac6274b7f6d198/pr-merge-audit-link-split-root.md)`.
  Local and GitHub API state blob hashes both resolved to
  `a21663ad70792200804deab5ee9e1f84bc255ca6`; the `origin/main` code-path probe matched remotely at
  blob `9f46314864ec71948a159fc718c5b225a8a38714`.
- `git diff --check origin/main` and the two-path scope assertion — exit 0.

CI path filters were not widened: this task's approved scope excludes workflow edits, so fresh
validation must run the direct contract command above explicitly. The existing shadow regression
job sees no changed runtime file and was run locally as ripple evidence.

Known limitation: owner/repo continues to resolve from the code repository; this cut does not
guarantee a split-root state checkout hosted in a different GitHub repository.

## Stage Report: validation — 2026-07-29

- DONE: Re-anchor the clean exact implementation head against freshly fetched origin/main and independently verify the two-file authorized scope plus both commits' TDD meaning.
  Fresh fetch kept `origin/main@85959dce`; clean head `38fa87489a19decce7d89b414187a66c7aadffd2` changes only the mod and direct test, while baseline `55031ae8985578cbb60294f61b23679baa5c4e5e` executes the old tuple and goes RED 7/35.
- DONE: Freshly execute the direct contract, shadow regression, pinned ShellCheck v0.9.0, fail-closed negative cases, branch mutations, and local/remote blob probes without trusting implementation claims.
  Final runs returned direct 35/35, shadow 213/213, `bash -n` clean, and both the documented CI Docker command and pinned checks of the added test/extracted recipe clean.
- DONE: Map exact evidence to AC-1 through AC-5, disposition EM residuals, and return PASSED or concrete Material findings without modifying product files.
  PASSED at exact head `38fa87489a19decce7d89b414187a66c7aadffd2`; no Material finding and no product-file edit occurred during validation.
- DONE: AC-1 — Split-root links resolve.
  The extracted recipe asserted the full state SHA/root-relative link; live `[w1]` used `23f0eef473ceffad73a8c88aae0f875ec2251aee:pr-merge-audit-link-split-root.md`, whose local and GitHub blobs both equal `102a9d2efaa0ccca19f358154cbde472879fcc6f`.
- DONE: AC-2 — Single-root links retain their target.
  The distinct-FO/code-head fixture asserted the code short-SHA/repo-relative link and `cat-file`; the reachable `origin/main` tuple's local and GitHub blobs both equal `9f46314864ec71948a159fc718c5b225a8a38714`.
- DONE: AC-3 — The executable contract owns both cases.
  The test extracted/sourced the marked recipe; committed baseline emitted the old code tuple before failing 28 assertions, while forced-inline, forced-split, and literal-main mutations failed 4, 1, and 2 assertions respectively.
- DONE: AC-4 — Neighboring PR behavior is unchanged.
  `git diff --check origin/main...HEAD` exited 0 and the diff names only `docs/dev/_mods/pr-merge.md` plus `kc-pr-flow/scripts/pr-merge-audit-link.test.sh`; mod hunks are the marked recipe and its three audit descriptions.
- DONE: AC-5 — Resolver failures stop link construction.
  Nonzero, malformed, missing, empty, and non-string workflow/path plus missing-blob cases each returned nonzero, emitted the case diagnostic, and emitted no tuple/link across 27 negative assertions.

### Evidence block

Lenses: executable Bash recipe embedded in a Markdown hook plus one Bash test; correctness PASS (0 findings), security PASS (0), and silent-failure PASS (0); type-design, concurrency, resource-lifecycle, and manifest/back-compat did not fire because no such surface changed.
Diff coverage: 86.7% (117/135) of traceable command-start lines in the added `scripts/*.test.sh`; heredoc payload/structural lines were excluded, while the Markdown recipe used exercise-based proof.
Adversarial: forced-inline was 31/35, forced-split 34/35, and literal-main fallback 33/35, so every claim-breaking scratch mutation turned the direct contract red.
Cross-model: Codex attempted Gemini via `agy 1.1.8` (~180 seconds, no output, interrupted rc 130), then Claude Code `2.1.220` (~150 seconds, no output, interrupted rc 130); observed unavailability, no second-opinion findings produced.
E2E: the live recipe emitted the immutable split-root link and GitHub returned the same state blob as local Git; the reachable code tuple also matched local/remote blobs.

### EM residuals

- DONE: False RED by recipe absence is closed: baseline extraction succeeded and emitted the actual old code-SHA/code-path tuple before RED.
- DONE: Resolver fail-closed behavior is closed by nine negative modes and the literal-main fallback mutation.
- DONE: AC scope is closed by the exact two-file diff including the marked recipe, its three descriptions, and direct test.
- SKIPPED: Cross-repository state owner/repo support remains outside this cut; both spec and mod explicitly retain code-repository-derived owner/repo.
- SKIPPED: Browser/full-stack E2E remains inapplicable by ideation; the changed PR-body value surface was exercised through the live recipe and GitHub API.

### Summary

Validation independently reproduced RED-to-GREEN provenance, all five ACs, the relevant correctness/security/silent-failure lenses, mutation sensitivity, coverage, and local/remote blob reachability at the exact clean repair head. Verdict: **PASSED**, with only the explicitly accepted cross-repository owner/repo boundary and observed cross-model tool unavailability.
