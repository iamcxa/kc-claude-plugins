fix(kc-dev-flow-2): send denial reasons by default

After denying a worker request, FO now sends the reason with send_agent_prompt (activeTurnBehavior steer) unless that provider is confirmed to deliver denial messages. Claude is the named exception based on Paseo source reading, not a runtime run. Codex's missing denial reason is established by the six FO-operated runs. Unconfirmed providers, including Gemini, receive the default send.

This follows the Captain's validation-gate revision of the previous Codex-only sentence. Only that one sentence changes; permission authority and Captain holds stay governed by ADR 0052. The same tested send tool/flag is preserved. Changed criteria are restated under fresh ids AC-11 and AC-12 with the original text preserved in Amendment 2; AC-9 and the pre-run scoring rule remain unchanged.

Existing controlled Codex evidence shows four exact reason receipts and directed audit writes with correct summaries inside the original turn, without outside-write retry. The six runs used an outside-workspace text write to produce a denial with FO as the denying side, not the original qnow build parameter. Default sending beyond Codex is source-informed policy, not runtime proof; Claude and Gemini behavior was not replayed. No new worker was started because the twelve-attempt cap is spent, and the old fresh-FO scenario is not a new-reader test of this wording.

At local candidate d22a01d5e8d334f6f4e8a2c5853f8f6abeddc89a, lint passes at 5939/5939. ADR lint, design-surfaces, amendment comparison, fresh-ref number guards, diff checks, comment ratio and document impact pass. The sentence is now 40 words instead of 21: +19 over the previous candidate, +40 over base; the workflow budget is unchanged. ADRs added: none; no version or CI trigger change, per-PR CI cost not measured.

FO will push this commit to existing PR #842, rerun RoboRev and route independent validator re-review. The implementation worker has not pushed or updated the PR, rerun hosted CI or claimed independent validation of this head.
