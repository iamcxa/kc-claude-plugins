Engineers can explicitly refresh story progress from local development tasks while preserving independent planning and source files.

## What changed

- Add an explicit local-task progress refresh command.
- Match journey, release and story identities without automatic source writes.
- Show task provenance while keeping delivery acceptance pending.
- Install checksum-pinned Spacedock v0.27.2 for existing CI reader tests.

## Evidence

- Producer affected progress/example checks: 9/9 passed. Pinned-reader checks: 5/5 locally; Linux hosted verification pending.
- Retained independent proof and six producer mutations cover matching, refusal and source safety.

[Original exact 10-file manifest](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/schema-comment-correction-evidence/unit-3-files.json): +427/-27; generated +0/-0. [Retained independent evidence](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/three-unit-independent-validation/README.md). CI cost per PR is unmeasured.

[CI prerequisite patch](https://github.com/iamcxa/kc-claude-plugins/blob/285c84b18c9b373fc85ff301123b19666076bc2e/derive-release-story-progress/ci-reader-bootstrap-evidence/candidate.patch): +15/-0; total 11 files, +442/-27.

---
Candidate: a5c08cbdf812826125decb6b55a286c4bcd2f1be
Task audit: [91](https://github.com/iamcxa/kc-claude-plugins/blob/6c2d5af977ffa659bbd94ab862e56be7c225ff6e/derive-release-story-progress/index.md)
