feat(kc-dev-flow-2): keep Captain questions open until their answers are recorded

Questions asked outside gates now persist their owner, options, approval meaning, affected tasks and answer lifecycle in the existing asks.jsonl file. The timeline helper lists open questions and native gate attempts, preserves legacy interruption counts and per-round timing, and flags repeated questions that need a Review briefing.

The design check refuses a post-adoption amendment whose quoted question has no record, including records shared through tasks. Adoption starts from the author date of the first commit introducing the approved ask sentence in the workflow README; missing or shallow history skips this rule with a diagnostic. The format's reference and ADR 0086 record the approved boundary.

Captain amendment 1 adds the required owner to the startup command. This is the separate final commit: the sentence grows from 25 to 41 words, and the workflow budget changes by +16 (6097 to 6113 on this base). Recount that difference when integrating the delivery-record PR #869 before delivery.

Validation: the complete 29-command kc-dev-flow-2 CI list, final affected suites, thirteen caught mutations, the unchanged h3 regression fixture, and thirty-four native gate attempts are recorded in the task's implementation report and evidence. Pytest is unavailable locally; the same unittest file was run as CI does, as directed by FO. No product branch push, hosted CI, independent blind read or RoboRev was performed. CI cost per PR was not measured.
