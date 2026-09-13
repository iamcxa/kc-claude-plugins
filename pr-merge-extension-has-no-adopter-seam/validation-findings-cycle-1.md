# Validation findings, cycle 1 — candidate `019e4715`

All four acceptance criteria passed. These three defects are in bytes that ship to
adopters; none falsifies an acceptance criterion, and together they block Draft
creation because `spacedock-dev/subspace-relay` is the next repository to run the
sync.

1. **The extension quotes its own closing runtime-extension marker inline.**
   `skills/adopt-dev-flow/SKILL.md` step 7 tells an adopter to write the resource
   verbatim between the markers — prose, not a script. An agent obeying it with a
   bare text search stops at the first occurrence and writes 14 lines instead of
   477. The first officer's own tool already produced that shape: 715 characters
   read instead of 26184, silently.
2. **The shipped extension names no version-skew stop condition.** The checker's
   self-test proves agreement with its own committed fixture and never with the
   adopter's parser, so an adopter on a newer release-please gets a confident green
   from a stale oracle with no instruction telling them when to re-derive.
3. **Two shipped fixture files cite a section that does not ship.**
   `release-please-verdicts.tsv` and `capture-oracle.cjs` both point at "The title
   rule's oracle", which exists only in this entity's `## Shape`, inside the
   split-root state checkout that no adopter receives.

One validation item failed on host load rather than on the candidate: that the
contract-test battery reaches `check-pr-title.test.py` at runtime is unproven, and
it was routed with the three defects.
