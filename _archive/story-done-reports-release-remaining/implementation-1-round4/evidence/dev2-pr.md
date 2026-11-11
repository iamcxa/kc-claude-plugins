feat(kc-dev-flow-2): require story records in journey workflows

Stacked on [iamcxa/kc-claude-plugins#839](https://github.com/iamcxa/kc-claude-plugins/pull/839), with `spacedock-ensign/story-done-reports-release-remaining` as the PR base. That sibling carries the kc-journey-map producer and its additive progress contract; it must land first.

In workflows listing journey-map, backlog admission requires an unfenced `Story: <id> ...` or `Story: none: <reason>` under FO alignment. The design check compares the record with journey-story, and the existing idle look names missing records. The extension adds the archive progress report, and ADR 0076 records the Captain's ruling. The authorized sample update preserves the consumer's whole-document assertion and contract registry.

Merge commit `e079d0c555fde855527a82c7a497a4d07e6e4c04` combines the pushed producer with the original dev2 commit without rewriting either history. Its six-file diff against #839 is byte-identical to the original dev2 patch; no product file was edited by hand in this stacking round.

Validation: the unchanged 122-test release-acceptance suite passes on this merge head. The local replay ran all 28 hosted-workflow commands: 27 pass, while test_laws_check.py fails 9 of 84 cases because its isolated fixture copies design_surfaces.py without the newly imported workflow_extensions.py. The same narrow case passes at the producer base, and adding the existing helper only to the temporary fixture makes it pass. The candidate is blocked on authorizing and validating that test-fixture correction; no product file was edited to fix it in this round. Actual hosted CI, RoboRev and independent revalidation of the new head remain pending.

The first real adopter archive after release/rollout remains future acceptance. CI cost was not measured; workflow definitions are unchanged.
