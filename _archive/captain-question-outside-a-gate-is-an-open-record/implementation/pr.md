feat(kc-dev-flow-2): keep Captain questions open until their answers are recorded

Questions asked outside gates now persist their owner, options, approval meaning, affected tasks and answer lifecycle in the existing asks.jsonl file. The timeline helper lists open questions and native gate attempts, preserves legacy interruption counts and per-round timing, and flags repeated questions that need a Review briefing.

The design check refuses a post-adoption amendment whose quoted question has no record, including records shared through tasks. Adoption starts from the author date of the first commit introducing the approved ask sentence in the workflow README; missing or shallow history skips this rule with a diagnostic. The format's reference and ADR 0086 record the approved boundary.

Captain amendment 1 adds the required owner to the startup command in its separate wording/budget commit: the sentence grows from 25 to 41 words, and the workflow budget changes by +16 (6097 to 6113 on this base). Recount that difference when integrating the delivery-record PR #869 before delivery.

Validation: all 29 configured commands ran locally in hosted order. Before the install boundary they used a missing SPACEDOCK_BIN; 28 commands passed, while release-acceptance reproduced the same 27 failures on both the rejected head and repair. As FO directed, that suite also ran with SPACEDOCK_BIN unset, matching hosted CI, and passed 122 cases with four optional skips. No CI definition changed. The full run covers 1,480 unittest cases, 13 optional skips and native dispatch checks.

The open list exposes question text in plain/JSON open lists, including mixed native gates; makes all five question-record checks independent of the not-yet-installed binary; and reconciles the unchanged fourteen-question cohort to complete public source records and recorded-answer commit times. The new source-backed fixture matches the validator's saved independent reader at 56 clocks with zero mismatches. Sixteen mutations were caught. Lint, ADR and number checks pass; comments are 0.4% against a 5% maximum.

The repair is local at 0b620345b538b67f4c6522d8b97028038f1ec17d. FO owns pushing PR #870, RoboRev, hosted CI and validation-2. The format revision, eight-path product boundary and approved +16 startup-word difference remain. CI cost per PR was not measured.
