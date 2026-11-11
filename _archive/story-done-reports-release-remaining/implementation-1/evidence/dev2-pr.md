feat(kc-dev-flow-2): require story records in journey workflows

In workflows listing journey-map, backlog admission now requires an unfenced `Story: <id> ...` or `Story: none: <reason>` under FO alignment. The design check compares that record with journey-story; the existing idle look names backlog tasks missing the record. ADR 0076 records the Captain's ruling.

The journey-map extension tells FO to include the producer's progress report immediately after an archive. Captain amendment 1 authorizes updating only the consumer's stored progress sample for the additive members fields; its whole-document assertion and consumer contract registry remain unchanged. The extension is 713 words against a 726-word limit, and the workflow template is unchanged.

Validation: 222 design tests (4 existing conditional skips), 136 watch tests and 125 dispatch-record tests (1 existing conditional skip); 122 unchanged consumer tests pass against both candidate trees together. Pinned seed replays refuse 135 relay tasks, 163 qnow tasks and 0 tasks in the unlisted local workflow; idle look names 31/11 tasks. Reverse mutations confirm the story checks and unchanged consumer assertion reject their counterexamples. Skill lint, ADR lint, number guards and comment ratio pass.

Depends on the paired kc-journey-map producer landing first. No product branch push, PR creation, RoboRev or hosted CI was performed. Actual relay rollout and archive acceptance remain pending. CI cost was not measured; CI configuration is unchanged.
