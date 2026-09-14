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
