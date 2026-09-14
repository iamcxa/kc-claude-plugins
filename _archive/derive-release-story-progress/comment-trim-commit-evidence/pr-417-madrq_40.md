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
