fix(kc-dev-flow-2): keep workers on unblocked steps after command denial

A refused command can leave a worker's remaining stage work undone. Add the approved single worker-facing sentence in Dispatch facts, its quoted +33-word workflow-budget step, and the Paseo instruction to send a Codex worker the denial reason with steer.

Local lint, 47 existing lint tests, native stage-context checks, budget-removal mutations, byte comparison of the Secrets bullet, ADR lint, number guards, design-surfaces, diff checking and comment ratio passed. Reading cost is +33 words at startup/resume and each dispatch; the Paseo permission callback adds 21 words. No version or CI trigger changes; CI cost per PR was not measured. ADRs added: none (the change extends ADR 0037 under ADR 0020's existing budget rule).

Delivery hold: AC-3 through AC-7 remain unproven. Six worker replay attempts were void because the target fetch returned 0 without an FO-addressable pending permission, including five explicit native escalation requests. The fresh FO Codex/Claude scenario passed, but it does not establish denied-worker behavior or same-turn steering. Do not infer acceptance from the local static checks. FO owns replay recovery, RoboRev, product push, Draft PR creation and hosted CI.
