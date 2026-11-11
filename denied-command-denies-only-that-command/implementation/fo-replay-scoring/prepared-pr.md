fix(kc-dev-flow-2): send Codex workers the denial reason through Paseo

Paseo's permission denial does not deliver FO's reason to a Codex worker. The worker-permission procedure now tells FO to send the reason separately with send_agent_prompt and activeTurnBehavior steer. Captain amendment 1 limits the product change to this Paseo instruction; the worker continuation sentence and +33 workflow-budget step are removed.

FO-operated replay: all six runs are valid. The four reason-send runs have FO-transcribed worker-side incoming reason events, exact instructed audit-file bytes and correct summaries. Both no-extra-message controls also finish their summaries, with no approved audit copy; no whole-task-stop claim is made. Full supplied inputs and per-run scores are preserved in the task's state branch.

Delivery hold: AC-7 and AC-10 remain unproven. No post-delivery turn identity was recorded, so same_turn is unverified in all four candidate runs under the unchanged pre-run rule. The single final response and message ordering do not establish that no fallback interruption occurred. Duplicate denied-command entries also leave invocation/retry identity unresolved; no actual retry is inferred. AC-9 is supported on the supplied FO-transcription boundary, not independently authenticated raw-message text.

Local lint passes at 5939/5939. ADR lint, fresh-ref number guards, design-surfaces, diff checking, scope checks and comment ratio pass; doc_impact lists no affected documents. The callback adds 21 words. ADRs added: none; authority under ADR 0052 is unchanged. No version or CI trigger changes; CI cost per PR was not measured. No worker product push or PR; FO owns RoboRev, hosted CI, validation and any further delivery decision.
