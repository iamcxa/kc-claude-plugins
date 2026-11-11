# Independent validation, cycle 2

Verdict: PASSED for PR #842 at d22a01d5e8d334f6f4e8a2c5853f8f6abeddc89a under Captain amendments 1 and 2. AC-11/AC-9/AC-12 pass within their recorded evidence boundary. F1 is open Polish; no Material, Deferred risk or Needs decision finding. This grants no delivery authority.

## Identity and policy

Live pr.json matches the head, OPEN and non-draft. Pinned origin/main is 546a136386c94c58e430c91a6f3457b38bd73880; merge-base is e8664a72b0f904e5dda3c391d52ab3abaca876b4. candidate.diff changes only the permission paragraph; correction.diff changes one sentence versus cdb99da0. current-base.diff also includes later main-only work and is not the PR change set. Execution used an archive plus disposable bare metadata, with no worktree creation or shared git-config writes.

The candidate matches the bound question: send by default, confirmed delivery as the exception, Claude explicitly source-only, unconfirmed Gemini included. The exact send_agent_prompt (activeTurnBehavior steer) is unchanged. Removing the correction restores the old Codex-only sentence, which fails the new default: a direct source counterexample, not a wording test or fresh-reader proof. ADR 0052 permission authority remains unchanged.

## Primary evidence and falsifiers

AC-11: claude-source.json independently reads installed Paseo 0.15.4. resolveDeniedPermission returns response.message and respondToPermission resolves denied pending requests through it. This confirms the source claim, not a runtime pass. Four prior Codex reason/action sequences remain in their original turns; the new-turn corruption is rejected.

AC-9: re-opened all six pinned original native logs, checked hashes and every allowlisted tool call, and read the extracted sequences. All six rejection outputs omit the reason; four candidate incoming bodies equal frozen reason text and receipt message IDs. The two controls have no reason message. native/ and summary.json preserve the historical cdb99da0 identity intentionally. Changed-reason and queued-without-receipt corruptions are rejected.

AC-12: four native rejection→reason→audit write→success→completion sequences stay in one turn. live-readback.json independently compares all six current result bytes, checks four audit files against exact frozen bytes and destinations, and observes all six outside targets absent. Wrong-audit-bytes and post-denial-retry corruptions fail. The two controls finish summaries with audit destination null: they did not stop the whole task.

falsifiers.json maps old scorer AC-7/AC-10 labels to current AC-11/AC-12. Five mutations prove rejection of corrupt evidence, not new runtime behavior. Only the copied scorer's optional UI mirror is redirected into its own scratch directory; assertions and frozen inputs remain unchanged.

## Amendment and F1

Captain/Asked match the validation-gate resolution. AC-7/AC-10 moved verbatim, ignoring boundary blank lines; AC-9 stayed unchanged; AC-11/AC-12 have fresh ids and markers (amendment-review.json). The entry is not limited to quotation plus an overridden-design pointer: Design contains extra agent explanation. F1 is Polish because its substantive clauses trace to the bound question, unchanged send or existing dispatch cap, without adding a permission or accepted behavior. ADR 0016 allows prose pointers and explicitly leaves semantic judgment outside its script. No amendment or product repair was made.

## Checks and limits

checks/checks.json records package lint at 5939/5939, 67 ADR records, design-surfaces, comment ratio, doc impact, number guards and whitespace checks. Initial number guards exited 2 because disposable bare metadata has no origin/main; using its identical pinned SHA exits 0. Both attempts are preserved. The separately requested installed Claude-package ADR command exits 0. dispatch-records and role-triggers exit 0; step-back.md answers the nonblocking reminder. No ADR or migration added; no affected document listed; no code comments added. reading-cost.json confirms wc-w counts: callback 291→310, extension 1133→1152, +19 this revision and +40 over base; normalized counts are separately labeled.

Four-step acceptance.sh ran unchanged in fresh Bash, exit 0 (acceptance-result.json, checks/captain-acceptance.log). Named machine-local native logs are required; raw logs and host instructions were not copied to state.

The six valid plus six earlier void attempts remain the spent cap. No worker, denial, steer or fresh FO scenario was started. Old reader/runtime evidence belongs to cdb99da0; only its unchanged Codex mechanism transfers. Claude has source evidence only; Gemini/other providers have no runtime evidence here. Their default send is policy, not proven provider reliability. The deliberately denied outside-workspace write is not the original qnow build flag. No general reliability, whole-task-stop, new hosted CI/RoboRev, merge, release or adoption claim is made. CI triggers did not change; per-PR cost was not measured. FO retains review, gate and delivery ownership.

## Cleanup

cleanup.json records exact owned scratch paths and final removal results. Existing /tmp/denial-replay-b21-fo, original native logs and other workers' scratch remain outside this run's ownership.
