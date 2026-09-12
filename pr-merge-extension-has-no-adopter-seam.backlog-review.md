# Backlog admission: pr-merge-extension-has-no-adopter-seam

## What is being admitted

kc-dev-flow 4.4.0 pins the released pr-merge body's sha256 and ships the extension
as a canonical resource. `spacedock-dev/subspace-relay` ran the adopt-dev-flow sync
at `main` `3b8f233` on 2026-09-12 — the second adopter, which is the residual PR
#414 recorded for itself. The sync found one rule with no upstream home: the pull
request title must be a Conventional Commits subject, refused by
`scripts/check-pr-title.ts` at two call sites inside `## Hook: merge`. That section
sits inside the sha-pinned released body, which may not be edited (Captain,
2026-09-11: 「不要去動那個上游」), and the extension declares no adopter region.

The condition is fleet-wide, not one adopter's. Measured `gh api repos/<r>` on
2026-09-12: `iamcxa/kc-claude-plugins`, `spacedock-dev/subspace-relay` and
`spacedock-dev/spacedock` all report `squash_merge_commit_title:
COMMIT_OR_PR_TITLE` with squash, merge and rebase enabled. This repository
releases through release-please, so a pull request with two or more commits lands
under the pull request title, and an unparseable title yields no release and
excludes that commit from every future changelog, silently.

## Acceptance criteria

- **AC-1** After a fresh sync into a repository holding no local title prose, the
  title refusal is reachable from `## Hook: merge`, and the pre-marker body still
  hashes to `pr_merge_released_body.sha256`.
- **AC-2** An unparseable title is refused before `gh pr create` would run and a
  parseable one passes, both on a fixture here; mutating the refusal's condition
  turns the refusing case green.
- **AC-3** `references/pr-merge-extension.md` and `skills/adopt-dev-flow/SKILL.md`
  each state the post-`:end` adopter region and its precedence;
  `scripts/kc-dev-flow-contract-test.py` stays 0 for a conforming adopter and
  non-zero naming the drift on a one-character change inside the block.
- **AC-4** `spacedock-dev/subspace-relay`'s `_mods/pr-merge.md` at `main`
  `3b8f233`, rebuilt as pinned body plus verbatim extension, needs zero
  adopter-added prose for the title rule — shown by rebuilding and listing
  retained behaviours, not by asserting equivalence.

## Non-goals

- Editing the released Spacedock pr-merge body or its pinned hash.
- Changing Spacedock's shipped mod, version stamp, or merge-guard contract.
- The `spacedock-dev/subspace-relay` adoption of 4.4.0, gated separately on that
  repository's `slim-v0-terminal-review-pr58` stage boundary.
- Any Linear read or write.

## Profile

`pilot-product-slice`, route `[shape, build, verify-deliver]`. #414 chose POC
because its falsifier was a single adopter and it recorded "the sync path is
rewritten if other adopters need more"; the second adopter has now reported, so
this is a defined slice. Not Production: no release identity, credential, or
standing deployment path moves, and it ships through the release-please lane #414
already used. Verified: `profile-contract-loader.py` at 4.4.0 resolves all three
Pilot stages from this work item with no unselected-profile or unselected-stage
bytes loaded.

## The one open design question, owed to shape

Where the refusal mechanism lives — a checker shipped by kc-dev-flow as a manifest
resource, or a rule the extension states while each adopter binds its own checker
in its Local Profile. Left open on purpose; deciding it is shape's work.
