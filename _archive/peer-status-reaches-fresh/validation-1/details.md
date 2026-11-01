# Independent validation of PR 756

Verdict: REJECTED at 1df246fa992ce0864348c2ffe67d93e80ad0a4b8, stacked base 422caef5a9b115a14f8391836499520d9fba6d91. The detached checkout was inside the assigned worktree. No product repair or remote mutation was performed. This is Pilot validation, not approval or adoption.

## Findings and evidence boundary

- F1 Material: Released user/normal workflow: Captain requests peer-derived status through dev. Observable harm: final response omits a dated observation time with timezone; a later reader cannot tell the status age from the response. Protected value: value-ac[AC-8] retains source/time for all merged cases; contract[kc-dev-flow-2/extensions/peers/EXTENSION.md#current-peer-facts] requires observation time with timezone. Trigger: all four MERGED outputs in cold-audit.json use “just now” or “剛”; f-notice gives the historical merge time, not current observation time. Source-query logs are timestamped separately; they do not put the observation time in the relayed status. Core stale-action prevention passed; the full retained criterion did not. Return evidence to FO without weakening the criterion or changing candidate bytes.
- F2 Needs decision: active Budget, Stop condition and Mermaid still say peers-only scope and require peers loading as a pass condition. AC-8 and Captain amendment 2 authorize the dev sentence, remove peers reading as a pass condition and retain direct-resume uncertainty. The engineering reviewer required active contract/diagram/count reconciliation; it was not applied. FO must route the authorized reconciliation and disposition; no new loader or broader authority is justified.
- F3 Deferred risk: the instruction replays below are warmed by the validator's assignment; they do not establish unhinted behavior of another FO or native delivery. This becomes Material on a normal-use authorization-to-release claim, forbidden send, hidden error or permission bypass. Do not report them as native proof.
- F4 Deferred risk: original cold fixture project configuration and gh wrapper bytes were not retained in this task folder. run.sh, all5.sh, init records, tool traces, complete source responses and outputs remain. This limits reconstruction of the initial environment; evidence of history/rule injection outside ordinary entry would invalidate the cold-entry claim.

## AC-8: independently recounted FO records, not new cold agents

All eight final logs delivered the exact candidate dev body (normalize package-root substitution and optional ARGUMENTS suffix). All eight queried gh pr view 186 --repo spacedock-dev/subspace-web before the final response. Four MERGED cases removed review/merge; OPEN retained the action without taking merge authority; three source-down cases retained an explicit FO check. f-down2 offers an optional self-check; f-down3 says the Captain may approve/merge if he independently knows readiness, alongside explicit FO ownership. Following the engineering reviewer's distinction, these do not transfer the source-check duty.

The final f-* README row is accurate for that core action matrix. It does not complete the observation-time requirement (F1). Prior r/s logs are earlier-head/scratch evidence only. The reviewer's second correction (workflow-sentence source-down 0/3) is retained; no 1/3 or 2/3 claim is reused. cold-audit.json retains hashes, source calls/results, word counts and full outputs.

| Final run | Source response words | Final status words | All tool-result words | Skill payload words |
| --- | ---: | ---: | ---: | ---: |
| f-absent1 | 17 | 198 | 115 | 781 |
| f-absent2 | 8 | 79 | 106 | 781 |
| f-delayed | 1 | 175 | 108 | 781 |
| f-notice | 1 | 177 | 108 | 781 |
| f-open | 6 | 189 | 9 | 781 |
| f-down1 | 4 | 54 | 105 | 781 |
| f-down2 | 4 | 219 | 75 | 781 |
| f-down3 | 7 | 166 | 56 | 788 |

Counts use Python len(text.split()): compact JSON can be one word; Chinese is not segmented. Skill counts include normal wrapper and f-down3 arguments, unlike source-file counts. All-tool-result words already include source results: do not add that column twice. Missing project-file/private context is not priced as zero or claimed as complete session totals. No native callback/runtime saving is claimed.

## AC-2 and AC-3: validator's exercises

record_replays.py, ac2/, replays.json and transport.jsonl retain declared inputs, source fixture bytes, observed time, decisions and intended calls. Three AC-2 files were read through the execution tool in this turn before composing statuses. Accessible question/answer clears only authorization, not rotation/release. Unavailable/unrelated originals produce unverified facts with FO-owned checking. These are explicitly synthetic, never authenticated 2026-10-28 history. Source/status words: accessible 38/30, unavailable 9/28, unrelated 22/26.

Twenty-one AC-3 cases cover merged/released/unblocked; involved A vs unrelated B; running/unknown recipients; confirmed Paseo with paseo unlisted; held go-live; same-question running reply; unavailable steering; five-minute expiry/one recheck/no independent work; uncertain receipt and attended reconciliation; duplicate/older/conflict/source-down; bound briefing; no-action finish; real error/permission hold; worker completion. Four calls were recorded; zero host sends occurred. Notices request steer/notify=true; requested reply steer/notify=false, per integrated binding and accepted ADR 0046. The criterion's older “quiet notice” phrase does not override that ruling. No permission-response, poll or automatic resend occurred.

This is a warm policy-consumer replay, with no product send interceptor. It proves requested behavior only. AC-3 conflict/source-down declare source outcomes rather than reading a real repository; native reconciliation/receiver state stay unverified. The sibling owns native ask/reply/notice/failure tests. AC-2/AC-3 are partial, never all behavioral acceptance green.

audit_evidence.py rejects output mutations: missing cold query, authorization upgraded to release, unrelated recipient, interrupt and stale quiet-notice flags. These challenge the evidence audit, not mechanical policy enforcement. The duplicate-word mutation checks the evidence count, not native behavior. AC-4's future natural-use falsifier is intentionally not run before delivery. checks.json records the real checker rejecting an empty criteria section (exit 1).

## AC-4, AC-5, AC-6 and implementation limits

AC-4 not run: no post-delivery natural adopted event exists here. FO retains original source, notice/held reason, receiver query, final status, actual entry path and response counts for the first natural authorized transition. It is not a pre-delivery hold.

Exact stacked-base/candidate counts: peers 1091/1353 (+262), paseo 389/389, dev 763/801 (+38 per source-file entry read), workflow 5781/5781; host 607. Unlisted 1698/1960; listed 2087/2349. Implementation's 1058/1320 and 2054/2316 refer to its older sibling base; current sibling adds 33 on both sides. Historical assembled recount is reproduced in recount.json (1412/1974 -> 1908/2297), not treated as final integrated counts.

Pinned common rows: 442/672/1021/371/1003; anchored heading correction gives 442/672/1021/371/776. Involved workflow/mods/scripts equal the stacked base, so base corpus is unchanged. Final listed rows: 2529->2791, 2759->3021, 3108->3370, 2458->2720, 2863->3125, before actual dev/output addends. AC-3 input/decision words: 189/211; each recorded prompt: 11. These are fixture corpora, not full-session reading, delivery or savings.

AC-6 ideation render/inspection receipt was read, not rerendered independently. Retained diagram is semantically stale (F2). Empty criteria mutation refuses. AC-8 has the marked replacement and direct-resume limit; AC-1/AC-7 are under their amendments. Product shared insertion, dev placement, restored workflow/budget, sibling binding, worker procedure and authority boundaries match amendment 2. No product script, version, startup hook or adopter was added.

Repository lint, 45 lint tests and dispatch tests passed. Negative controls cover signaling, stage/gate refusal and wording loss, not native workers. Dispatched checks: adr_lint (stacked base and origin/main) exit 0, 45 ADRs/0 legacy; doc_impact exit 0, 0 documents; comment_ratio exit 0, code/comments 0/0, maximum 5% not enforced below 20 lines; dispatch_records exit 0, 7 complete; design_surfaces exit 0/presentable (scope check not run at validation). Default number guard initially failed R4 on sibling ADR 0046; explicit assigned stacked base passes. No task ADR reservation or migration path exists. This is stacked-range handling, not a new unreserved ADR by this task.

RoboRev daemon-unavailable remains incomplete, never clean review. Hosted PR/CI read failed connecting to api.github.com (hosted-pr.stderr); no current hosted verdict is asserted. CI cost per PR not measured; no trigger changed.

## Captain's six-step acceptance

Run /bin/bash --noprofile --norc with the absolute acceptance.sh path in this directory. Its six numbered command groups are exact commands; acceptance-output.log retains observed output. It checks revision, lint, counterexamples, dispatch contracts, ADRs and the audit. No application screen changed. Expected exit 0 reproduces the audit, whose last line remains REJECTED. It does not prove native delivery, historical authority, long sessions, direct First Officer resumes, adoption or future natural use. No git config writes or remote mutations occur.
