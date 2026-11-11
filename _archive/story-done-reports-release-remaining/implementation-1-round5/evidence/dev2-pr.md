feat(kc-dev-flow-2): require story records in journey workflows

Stacked on [iamcxa/kc-claude-plugins#839](https://github.com/iamcxa/kc-claude-plugins/pull/839), with `spacedock-ensign/story-done-reports-release-remaining` as the PR base. That sibling carries the kc-journey-map producer and its additive progress contract; it must land first.

In workflows listing journey-map, backlog admission requires an unfenced `Story: <id> ...` or `Story: none: <reason>` under FO alignment. The design check compares the record with journey-story, and the existing idle look names missing records. The extension adds the archive progress report, and ADR 0076 records the Captain's ruling. The authorized sample update preserves the consumer's whole-document assertion and contract registry.

The Story check loads workflow_extensions only when called, preserving callers that import unrelated design_surfaces helpers without that module. The unchanged laws suite protects this boundary. Commit `01d23393ebe5bfd63d8bcafc01859c3b146021d2` repairs that dependency on top of merge `e079d0c555fde855527a82c7a497a4d07e6e4c04`, which preserves both original parents. This repair changes only design_surfaces.py; no test or fixture changes.

Validation at this head: all 28 Python command steps from the hosted workflow pass in a local macOS/Python 3.15 replay, including the 84-test laws suite (one existing conditional skip), 222 design tests (four existing conditional skips), and the unchanged 122-test release-acceptance suite. The narrow laws regression fails before the repair and passes afterward; both seed and default Story checks pass. ADR lint requiring 0076, fresh-ref number guards against the stacked base, skill lint and comment ratio pass. Actual hosted CI, RoboRev and independent revalidation of this head remain pending.

The first real adopter archive after release/rollout remains future acceptance. CI cost was not measured; workflow definitions are unchanged.
