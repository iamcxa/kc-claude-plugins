# Exact three-layer publication review — not published

Both comment drafts are committed and propagated locally. All three exact-pair merge preflights pass. Native stack #418 remains ordered #415 → #416 → #417 and all remote PRs remain Draft. New-head hosted checks are pending; prior CI evidence is historical. No remote write has run.

## PR415

Title: `feat(kc-journey-map): add editable native planning canvas`

Worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/worktrees/journey-stack-recut/.context/local-stack/journey-planning`

Repository: `iamcxa/kc-claude-plugins`

Branch/base: `codex/journey-planning` → `main`

Proposed base SHA: `c1564b218799b3baf07fc5e6c346bb6dcc476a7e`

Observed remote head: `0d69be164ccdcd1b3509f3577d6bd03a468f8f36`

Candidate: `c035e3ee792effb2708f646c2761d70ac17d9dbb`

Required explicit lease: `refs/heads/codex/journey-planning:0d69be164ccdcd1b3509f3577d6bd03a468f8f36`

Body: `/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/journey-stack-recut/comment-trim-commits/pr-415-h2p7hbpr.md` (0600), SHA-256 `1212dcc1637b809c6d841528b435cca37e608ab3ed41b52579dc267cb9a77a22`

```markdown
Engineers can turn journey plans into editable native story maps and safely bring workshop edits back into the source.

## What changed

- Add native story maps with release bands.
- Persist room edits and preserve manual notes during redraw.
- Render journey YAML and read edits back by stable story ID.
- Trim redundant comments while preserving library, data-safety and licence facts.

## Evidence

- Historical producer model/readback checks: 17/17 passed.
- Historical producer live editing/persistence checks and retained independent negative/control evidence cover source safety.

[Historical manifest](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/schema-comment-correction-evidence/unit-1-files.json). Current adjacent diff: 42 files, +6847/-311; generated +5245/-0. [Retained independent evidence](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/three-unit-independent-validation/README.md). CI cost per PR is unmeasured.

Comment-only executable equivalence passed. Hosted checks at this new head are pending; prior CI results are historical.

---
Candidate: c035e3ee792effb2708f646c2761d70ac17d9dbb
Task audit: [91](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/index.md)
```

## PR416

Title: `feat(kc-journey-map): add release evidence details and status borders`

Worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/worktrees/journey-stack-recut/.context/local-stack/journey-release-inspection`

Repository: `iamcxa/kc-claude-plugins`

Branch/base: `codex/journey-release-inspection` → `codex/journey-planning`

Proposed base SHA: `c035e3ee792effb2708f646c2761d70ac17d9dbb`

Observed remote head: `818260a8c14b504dae8d3989ba9c710226255b74`

Candidate: `d339355faf2c2833df91cf9dde42a5ee12098341`

Required explicit lease: `refs/heads/codex/journey-release-inspection:818260a8c14b504dae8d3989ba9c710226255b74`

Body: `/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/journey-stack-recut/comment-trim-commits/pr-416-hgwbztgh.md` (0600), SHA-256 `3426f4506cc54acf5f90364ba6e61bbe80982f329440dafe021d7e3df97ac968`

```markdown
Engineers can inspect release details and distinguish existing, unverified and missing story evidence across native boards.

## What changed

- Add release-detail and function-map projections.
- Check authored evidence and generate release contracts.
- Display standard status borders and a portable worked example.
- Trim redundant comments while preserving library, data-safety and licence facts.

## Evidence

- Historical producer model/example/evidence checks: 67/67 passed.
- Historical producer browser export/import/readback passed; retained independent proof covers borders, schema diagnostics and dependency reduction.

[Historical manifest](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/schema-comment-correction-evidence/unit-2-files.json). Current adjacent diff: 34 files, +2061/-150; generated +1/-0. [Retained independent evidence](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/three-unit-independent-validation/README.md). CI cost per PR is unmeasured.

Comment-only executable equivalence passed. Hosted checks at this new head are pending; prior CI results are historical.

---
Candidate: d339355faf2c2833df91cf9dde42a5ee12098341
Task audit: [91](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/index.md)
```

## PR417

Title: `feat(kc-journey-map): derive optional local task progress`

Worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/worktrees/journey-stack-recut/.context/local-stack/journey-local-progress`

Repository: `iamcxa/kc-claude-plugins`

Branch/base: `codex/journey-local-progress` → `codex/journey-release-inspection`

Proposed base SHA: `d339355faf2c2833df91cf9dde42a5ee12098341`

Observed remote head: `a5c08cbdf812826125decb6b55a286c4bcd2f1be`

Candidate: `36a969a6f890a63c541fad4bfa30071ac7115c64`

Required explicit lease: `refs/heads/codex/journey-local-progress:a5c08cbdf812826125decb6b55a286c4bcd2f1be`

Body: `/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/journey-stack-recut/comment-trim-commits/pr-417-madrq_40.md` (0600), SHA-256 `140a77116170cfe55a0b2c9e598c34de0402e27014575bc9e397ac00a7b1b954`

```markdown
Engineers can explicitly refresh story progress from local development tasks while preserving independent planning and source files.

## What changed

- Add an explicit local-task progress refresh command.
- Match journey, release and story identities without automatic source writes.
- Show task provenance while keeping delivery acceptance pending.
- Install checksum-pinned Spacedock v0.27.2 for existing CI reader tests.

## Evidence

- Historical producer affected progress/example checks: 9/9 passed. Pinned-reader checks: 5/5 locally; Linux hosted verification pending.
- Retained independent proof and six producer mutations cover matching, refusal and source safety.

[Historical manifest](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/schema-comment-correction-evidence/unit-3-files.json). Current adjacent diff: 11 files, +442/-25; generated +0/-0. [Retained independent evidence](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/three-unit-independent-validation/README.md). CI cost per PR is unmeasured.

[CI prerequisite patch](https://github.com/iamcxa/kc-claude-plugins/blob/285c84b18c9b373fc85ff301123b19666076bc2e/derive-release-story-progress/ci-reader-bootstrap-evidence/candidate.patch): +15/-0; included in the current totals above.

Comment-only executable equivalence passed. Hosted checks at this new head are pending; prior CI results are historical.

---
Candidate: 36a969a6f890a63c541fad4bfa30071ac7115c64
Task audit: [91](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/index.md)
```

After separate Captain approval only, publish bottom-to-top with each exact refspec and explicit `--force-with-lease=refs/heads/BRANCH:OBSERVED_OLD_HEAD`, then update the corresponding existing PR with the reviewed body file. Stop on any lease/binding mismatch; never substitute unconditional force. Bottom is a fast-forward, while middle/top are rewritten histories. No branch rename, new stack/link, Ready or merge is included.
