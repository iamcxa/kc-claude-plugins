---
title: "The pr-merge extension has no adopter seam, so a fleet-wide title rule has nowhere to live"
status: ideation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: dev-flow-pr-merge-adopter-seam
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: 2f5a8kg1qwc5ba8jg3mcfjjw
gates:
    version: 1
    records:
        - id: gate:2f5a8kg1qwc5ba8jg3mcfjjw:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:2f5a8kg1qwc5ba8jg3mcfjjw-backlog-1
              briefing:
                id: briefing:2f5a8kg1qwc5ba8jg3mcfjjw:backlog:attempt-1:revision-1
                digest: sha256:e7c2a8e136175ae56326a860fa6d3f28da6973585f4e01dcdd041c0c4fcc081e
                room-ref: ./pr-merge-extension-has-no-adopter-seam/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:2f5a8kg1qwc5ba8jg3mcfjjw:backlog:1
                briefing: briefing:2f5a8kg1qwc5ba8jg3mcfjjw:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-12T09:58:36.464777Z"
                decision: approve
                reason: 'Captain approved in chat 2026-09-12: 「開」 to filing at Pilot after the AC-1..AC-4 presentation, then 「推」 to advance. Scope is the two asks presented: carry the title rule in the extension, and declare the post-:end adopter region and its precedence.'
              application:
                target-stage: ideation
                state: consumed
---

kc-dev-flow 4.4.0 pins the released pr-merge body's sha256 and ships the
extension as a canonical resource. The adopter `spacedock-dev/subspace-relay` ran the adopt-dev-flow sync on
2026-09-12 at `main` `3b8f233` and is the second adopter to do so, which is the residual #414
recorded for itself: *"Other adopters receive the block only after they run the
adopt-dev-flow sync."* The sync found one rule in that repository's
`docs/dev/_mods/pr-merge.md` with no upstream home — the pull request title must
be a Conventional Commits subject, refused by `scripts/check-pr-title.ts`. Both
of its call sites are inside `## Hook: merge`: once before the draft is presented,
and once chained as `check-pr-title.ts && gh pr create`. That section is inside
the sha-pinned released body, which may not be edited (Captain, 2026-09-11:
「不要去動那個上游」). The extension offers nowhere else to put it: the word
"adopter" appears once in its 424 lines, in the contract-test sentence, and
nothing declares whether adopter prose after the `:end` marker may override a
released section the way the extension's own `#### Local failure-policy override`
and `### Split-root audit-link correction` subsections do, or with what
precedence. The condition the rule guards is fleet-wide rather than that repository's:
`gh api repos/<r>` on 2026-09-12 reports `squash_merge_commit_title:
COMMIT_OR_PR_TITLE` with squash, merge and rebase all enabled for
`iamcxa/kc-claude-plugins`, `spacedock-dev/subspace-relay` and
`spacedock-dev/spacedock` alike, and this repository releases through
release-please. A pull request carrying two or more commits lands under the pull
request title; a title release-please cannot parse produces no release and
excludes that commit from every future changelog by type, permanently and
without a symptom.

## Accepted outcome

An adopter whose repository squash-merges under `COMMIT_OR_PR_TITLE` and
releases through release-please receives the title refusal from kc-dev-flow
itself, with no rule copied into its own mod and no edit to the pinned released
body. Separately, the extension and `adopt-dev-flow` both state whether an
adopter may add a rule of its own after the `:end` marker and what precedence
that region holds against the extension block, so the next adopter meets a
declared answer instead of silence.

## Non-goals

- Editing the released Spacedock pr-merge body or its pinned `pr_merge_released_body.sha256`.
- Changing Spacedock's shipped mod, its version stamp, or its merge-guard contract.
- The `spacedock-dev/subspace-relay` adoption of kc-dev-flow 4.4.0, which is gated separately on that repository's `slim-v0-terminal-review-pr58` stage boundary.
- Any Linear read or write.

## Acceptance criteria

- **AC-1** After a fresh `adopt-dev-flow` sync into a repository holding no local
  title prose, the title refusal is reachable from `## Hook: merge` in the
  resulting `_mods/pr-merge.md`, and that file's pre-marker body still hashes to
  `contract-manifest.json` `pr_merge_released_body.sha256`.
- **AC-2** A pull request title release-please cannot parse is refused before
  `gh pr create` would run, and a parseable title passes, both exercised against
  a fixture in this repository. Mutating the refusal's condition turns the
  refusing case green, proving the check and not its restatement.
- **AC-3** `references/pr-merge-extension.md` and `skills/adopt-dev-flow/SKILL.md`
  each state the post-`:end` adopter region and its precedence against the
  extension block. `scripts/kc-dev-flow-contract-test.py` still exits 0 for a
  conforming adopter and non-zero naming the drift when the marked block changes
  by one character.
- **AC-4** `spacedock-dev/subspace-relay`'s `docs/dev/_mods/pr-merge.md` at `main`
  `3b8f233`, rebuilt in a scratch worktree as
  pinned released body plus the verbatim extension, needs zero adopter-added
  prose for the title rule. Demonstrated by rebuilding the file and listing the
  behaviours the rebuild retains, not by asserting equivalence.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  route: [shape, build, verify-deliver]
  basis: >
    Captain approved in chat 2026-09-12 (「開」) after the Relay 4.4.0 adoption
    audit of `spacedock-dev/subspace-relay`. #414 selected POC because its falsifier
    was a single adopter and it recorded "the sync path is rewritten if other
    adopters need more"; that audit supplied the second adopter and answered the
    question, so this is a defined
    slice rather than a fresh exploration. Not Production: it moves no release
    identity, credential, or standing deployment path, and ships through the
    release-please lane #414 already used. The design question Pilot's shape stage
    owes is where the refusal mechanism lives — a kc-dev-flow-shipped checker, or
    a rule the extension states and each adopter binds in its Local Profile.
  obligations:
    architecture: [Released body and its pinned hash untouched; the refusal is reachable from the extension, not from adopter prose; the post-marker adopter region has one declared precedence]
    implementation: [references/pr-merge-extension.md; skills/adopt-dev-flow/SKILL.md; contract-manifest.json if a new resource is added; scripts/kc-dev-flow-contract-test.py]
    testing: [AC-1 to AC-4 at the candidate SHA; mutation proof on AC-2; drift mutation on AC-3]
  scope_boundary: >
    No Spacedock edit; no Linear; no change to `spacedock-dev/subspace-relay`; no edit to the
    released pr-merge body or its pinned hash.
  semantics_unchanged: false
```
