# Three-unit Draft PR review — not published

Exactly three local commits were approved. Publishing these branches, creating Draft pull requests and linking the native stack require a separate explicit Captain decision. Every body below is the actual mode-0600 file to publish verbatim after approval; no body reconstruction or post-approval rebase.

Live main at preparation: `c1564b218799b3baf07fc5e6c346bb6dcc476a7e`; approved commit base remains `c9c5752fda853737d4a937ad7f59564c5651ca53`. Main moved, but all three exact-pair preflights pass. Bottom merge result: `3319ba6f63257f636ea848a56443cbe9b73bc1c0`. This is conflict preflight only, not validation of a merged runtime.

## Layer 1

Title: `feat(kc-journey-map): add editable native planning canvas`

Code repository: `iamcxa/kc-claude-plugins`

Worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/worktrees/journey-stack-recut/.context/local-stack/journey-planning`

Branch: `codex/journey-planning` → `main`

Base: `c1564b218799b3baf07fc5e6c346bb6dcc476a7e`

Candidate: `0d69be164ccdcd1b3509f3577d6bd03a468f8f36`

Body: `/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/journey-stack-recut/local-stack-commits/unit-1-1ssvamyc.md` (0600); SHA-256 `1db46a26f9a6b30ba8199d4564fc5ce770545975443df95dec2e0cc50b61d32a`

```markdown
Engineers can turn journey plans into editable native story maps and safely bring workshop edits back into the source.

## What changed

- Add native story maps with release bands.
- Persist room edits and preserve manual notes during redraw.
- Render journey YAML and read edits back by stable story ID.

## Evidence

- Producer model/readback checks: 17/17 passed.
- Producer live editing/persistence checks and retained independent negative/control evidence cover source safety.

[Exact 42-file manifest](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/schema-comment-correction-evidence/unit-1-files.json): +6994/-311; generated +5245/-0. [Retained independent evidence](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/three-unit-independent-validation/README.md). CI cost per PR is unmeasured.

---
Candidate: 0d69be164ccdcd1b3509f3577d6bd03a468f8f36
Task audit: [91](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/index.md)
```

## Layer 2

Title: `feat(kc-journey-map): add release evidence details and status borders`

Code repository: `iamcxa/kc-claude-plugins`

Worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/worktrees/journey-stack-recut/.context/local-stack/journey-release-inspection`

Branch: `codex/journey-release-inspection` → `codex/journey-planning`

Base: `0d69be164ccdcd1b3509f3577d6bd03a468f8f36`

Candidate: `818260a8c14b504dae8d3989ba9c710226255b74`

Body: `/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/journey-stack-recut/local-stack-commits/unit-2-yut57b0m.md` (0600); SHA-256 `e56e5b9f81ec5380c97b38e4431f639e0deaf639327f08f60c1ab2feb70ba7d2`

```markdown
Engineers can inspect release details and distinguish existing, unverified and missing story evidence across native boards.

## What changed

- Add release-detail and function-map projections.
- Check authored evidence and generate release contracts.
- Display standard status borders and a portable worked example.

## Evidence

- Producer model/example/evidence checks: 67/67 passed.
- Producer browser export/import/readback passed; retained independent proof covers borders, schema diagnostics and dependency reduction.

[Exact 35-file manifest](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/schema-comment-correction-evidence/unit-2-files.json): +2194/-160; generated +1/-0. [Retained independent evidence](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/three-unit-independent-validation/README.md). CI cost per PR is unmeasured.

---
Candidate: 818260a8c14b504dae8d3989ba9c710226255b74
Task audit: [91](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/index.md)
```

## Layer 3

Title: `feat(kc-journey-map): derive optional local task progress`

Code repository: `iamcxa/kc-claude-plugins`

Worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/worktrees/journey-stack-recut/.context/local-stack/journey-local-progress`

Branch: `codex/journey-local-progress` → `codex/journey-release-inspection`

Base: `818260a8c14b504dae8d3989ba9c710226255b74`

Candidate: `aabb8e7e8320b65fa852feae961df2e438d8f002`

Body: `/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/journey-stack-recut/local-stack-commits/unit-3-g9xoie6r.md` (0600); SHA-256 `92908b58884b7c22a684ef992de26ef2f2e70737e6f2f3da47946b8d197186c8`

```markdown
Engineers can explicitly refresh story progress from local development tasks while preserving independent planning and source files.

## What changed

- Add an explicit local-task progress refresh command.
- Match journey, release and story identities without automatic source writes.
- Show task provenance while keeping delivery acceptance pending.

## Evidence

- Producer affected progress/example checks: 9/9 passed.
- Retained independent proof and six producer mutations cover matching, refusal and source safety.

[Exact 10-file manifest](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/schema-comment-correction-evidence/unit-3-files.json): +427/-27; generated +0/-0. [Retained independent evidence](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/three-unit-independent-validation/README.md). CI cost per PR is unmeasured.

---
Candidate: aabb8e7e8320b65fa852feae961df2e438d8f002
Task audit: [91](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/index.md)
```

After explicit approval only, use each canonical exact-candidate push and gh pr create --draft --repo/--base/--head/--title/--body-file/--assignee binding. Link only the three resulting full PR URLs with installed native gh stack link --base main in bottom-to-top order; do not use --open. Existing Draft #394 stays untouched. No push, PR creation, linking, readiness, merge or release command has run.
