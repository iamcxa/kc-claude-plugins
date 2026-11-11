# Implementation correction — default-send denial reasons

Candidate: d22a01d5e8d334f6f4e8a2c5853f8f6abeddc89a
Previous candidate: cdb99da0e52e8b5cad3a7be04658dc282432b644
Pinned base: e8664a72b0f904e5dda3c391d52ab3abaca876b4
Freshly fetched origin/main: 546a136386c94c58e430c91a6f3457b38bd73880
Branch: spacedock-ensign/denied-command-denies-only-that-command
Existing PR: iamcxa/kc-claude-plugins#842; this new commit is local only.

## Captain correction and resulting instruction

The validation gate's revise records the Captain asking about Claude and Gemini and choosing 「先改成預設都傳（建議）」. Amendment 2 copies those words and the bound follow-up question into the task. The product change replaces the existing one sentence in kc-dev-flow-2/extensions/paseo/EXTENSION.md, Worker permission requests; it adds no other product surface.

The default after a denial is now to send the worker the reason. The exception is a provider confirmed to deliver the denial message. Claude is the named exception, with its evidence explicitly identified as Paseo source, not a run. Codex's omission is attributed to the six FO-operated runs. Unconfirmed providers, including Gemini, explicitly receive the message.

send_agent_prompt (activeTurnBehavior steer) is byte-identical to the previous sentence's tool/flag form, so the tested same-turn mechanism is retained. Without this change, the old sentence names only Codex and has no general default or named delivery exception; its Codex-only condition is the missing instruction the Captain identified. This is a source-level comparison, not a fresh-reader behavioral test.

## Evidence and limits

The Claude exception uses the design's Facts checked item 3: Paseo 0.15.4's Claude resolveDeniedPermission returns behavior deny, response.message and interrupt. That is a source reading from the design, not a Claude runtime denial. It is not a new check of an installed provider or a general assurance about later versions.

The six original FO-operated Codex runs show the rejected native output omitting the reason. Their four candidate steers deliver the exact reason and lead to the specified local audit bytes and correct summary inside the original turn, without retrying the outside write. The fixed rule, original inputs and native extracts under ../fo-replay-scoring/ are unchanged. The earlier independent validation of cdb99da0 also remains historical evidence at that head, not independent validation of this new sentence.

Default sending for providers other than Codex rests on reading source and the Captain's operating policy, not on a run. Gemini remains unconfirmed; its forwarding, same-turn steering and reaction were not exercised. The changed sentence does not claim those behaviors have been demonstrated. The old fresh-FO scenario read the old sentence; its result is not presented as an interpretation test of this rewording.

No replay worker or fresh FO was started. Six earlier void worker attempts plus six valid FO-operated runs remain twelve counted attempts; the cap is spent. No denial or steer was sent this round and no raw rollout was copied. The earlier outside-write task was chosen to produce a refusal with FO as denying side; it was not a reproduction of the qnow build-parameter incident.

## Criteria and amendment preservation

AC-7 is moved verbatim under Amendment 2 and replaced by AC-11: the default, named source-confirmed exception, unconfirmed-provider treatment, explicit source/runtime boundary and retained Codex same-turn requirement. AC-9 is unchanged.

AC-10 is moved verbatim and restated as AC-12, changing only its id, amendment marker and same-turn reference from AC-7 to AC-11. Its directed-write, summary, no-retry and evidence requirements remain. amendment-proof.json records the moved-block hashes. No old report or prior scoring packet was rewritten, and the task frontmatter is unchanged.

criteria.json records implementation support for AC-11/AC-9/AC-12, with source-level policy review distinguished from existing Codex runtime proof. design-surfaces exits 0; the installed amendment added_words comparison has no finding. New runtime interpretation or other-provider acceptance is not inferred from a wording check.

## Scope, word cost and checks

scope-proof.json verifies that only the extension differs from the pinned base and that reverting this one sentence reproduces the previous candidate's file bytes. Workflow, lint budget and ADR 0052 remain byte-identical to the base; no merge, rebase or version edit was made. Product worktree is clean at d22a01d5e8d334f6f4e8a2c5853f8f6abeddc89a.

Whitespace-delimited counts in reading-cost.json: sentence 21→40 words; permission callback 291→310 (270 at base); extension 1133→1152 (1112 at base). This correction adds 19 words over the prior candidate, 40 over base. Startup workflow remains 5939 and Dispatch facts remains 297; no workflow budget raise is added.

All required local checks exit 0 at the new candidate: repository lint 5939/5939; installed ADR lint 67 records; design-surfaces; diff --check; comment ratio 0 added code/comment lines, 0%, 5% maximum with its 20-code-line floor not reached; doc_impact lists 0 affected documents; fresh-ref number guards at base 546a136386c9/head d22a01d5e8d3/merge-base e8664a72b0f9. role_triggers reads two events at the committed task head, both cleared. Saved commands and logs are in checks/. The unchanged lint implementation does not require its previously passed full suite again; no wording test is added.

ADRs added: none. ADR 0052 owns this operating procedure; default reason forwarding changes no permission authority or Captain hold. ADRs 0005/0016/0057 govern the moved and freshly numbered criteria, and ADR 0026's role check passed.

## Handoff

The new PR title/body is /tmp/impl-denied-command-denies-only-that-command-pr.md and prepared-pr.md. No product push, PR edit, comment, review request, new RoboRev, hosted CI, merge or gate advancement was performed. FO owns pushing this commit to PR #842, rerunning RoboRev and the independent validator re-review. No CI trigger changed and per-PR CI cost was not measured. State evidence and the complete superseding implementation report are committed and synced separately.
