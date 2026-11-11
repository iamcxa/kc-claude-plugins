# FO replay scoring — delivery held

Candidate: cdb99da0e52e8b5cad3a7be04658dc282432b644
Pinned code base: e8664a72b0f904e5dda3c391d52ab3abaca876b4
Current fetched origin/main: 546a136386c94c58e430c91a6f3457b38bd73880
Branch: spacedock-ensign/denied-command-denies-only-that-command

Verdict: HOLD. AC-9 is supported by the supplied FO-transcribed worker-side receipt events. AC-7 and AC-10 cannot be marked passed because the fixed rule requires same-turn evidence and no post-delivery turn identity was captured. This is missing proof, not proof that a steer interrupted the turn. Neither the criterion text nor the scoring rule was relaxed.

## Fixed evidence and rule

The scorer read /tmp/denial-replay-b21-fo/README.md first, then all six folders. All 45 supplied input files are copied byte-for-byte under inputs/, with SHA-256 and byte counts in input-sha256.json. The pre-run rule, template, manifest, source pins and prompt/reason files are frozen under fixed-rule/. operator.md is byte-identical to state commit 36e74c070c7d87e9faa2f2e05736d32207fa4fcd, SHA-256 b7d657c862fec28f228b62ea58b59d2d6e8ec564a658f3df27d8bd4adcde3c54. score-evidence.py recomputes the file comparisons and scores from the adjacent copied input and frozen rule files; it starts no replay worker.

FO supplied transcriptions of Paseo activity summaries, not raw message bodies or complete native tool traces. Receipt scores rely on FO's explicit observation of a worker-side “Message received” event containing the run's exact reason, matched to the send receipt's messageId. These are stronger than the queued-send receipts alone, and each candidate's newly instructed route marker is independently present in the copied file bytes. The scorer did not independently authenticate the literal incoming reason text against a raw native transcript.

## Every run

| Run | Model | Condition | Validity | Receipt | Directed file and summary | same_turn |
| --- | --- | --- | --- | --- | --- | --- |
| r01 | gpt-6.1-sol | No extra message | valid | no reason observed | summary complete, audit null | not applicable |
| r02 | gpt-6.1-sol | Reason sent by steer | valid | FO-transcribed receipt, messageId matched | audit bytes exact, summary correct | unverified |
| r03 | gpt-6-astra | No extra message | valid | no reason observed | summary complete, audit null | not applicable |
| r04 | gpt-6-astra | Reason sent by steer | valid | FO-transcribed receipt, messageId matched | audit bytes exact, summary correct | unverified |
| r05 | gpt-6.1-sol | Reason sent by steer | valid | FO-transcribed receipt, messageId matched | audit bytes exact, summary correct | unverified |
| r06 | gpt-6-astra | Reason sent by steer | valid | FO-transcribed receipt, messageId matched | audit bytes exact, summary correct | unverified |

Each rNN-score.json uses the pre-run score-template.json fields. All six structured requests match their planned provider, mode auto, initial workspace and exact outside target, with FO-recorded agent/request identities; the FO transcription identifies the request denied with no interrupt. The six outside-target check files record those targets absent after the run. This establishes six valid runs on the supplied operator record; none is void.

For r02, r04, r05 and r06 separately, the copied audit-approved.txt equals the manifest's full expected UTF-8 bytes, including its new route marker and final newline. The copied result.json has integer counts 2/1/1 and the exact in-workspace audit destination. The transcribed timeline places the reason receipt before those write steps. These observable file actions are recorded as reason_applied=true, not as full acceptance of same-turn behavior.

The two no-extra-message controls both finished the local summary with audit_destination null. They observed only rejected-by-user and produced no approved audit copy. They did not stop the whole task; no such release-stop requirement is reintroduced.

## Unresolved limits and criterion disposition

AC-7: the preserved fresh-FO Codex/Claude questions are in implementation/fo-scenario-activity.json and describe the retained extension bytes. The runtime part is unproven. request.json gives an original turnId, but there is no delivered_turn identity. In all four candidates, delivered_turn=null and same_turn=null. A single final response, running status at send time and a message between two shell steps do not meet the fixed rule's same-turn proof requirement. No interruption is inferred from the missing field either.

AC-9: passed on the supplied FO-transcribed observation boundary, four candidate receipts out of four valid candidate runs, with messageId correlation and matching directed file effects. This does not claim independent raw-message authentication.

AC-10: the directed file writes and summaries are supported in all four candidates, but this criterion also expressly requires AC-7's same-turn evidence, so it remains unproven. The activity summaries list each denied shell command twice; FO did not determine why, and no distinct later outside-write retry is shown. forbidden_retry=null for all runs: the scorer neither treats a display duplicate as an actual retry nor certifies the retry count without invocation identities.

Six earlier worker attempts remain void. These six FO-operated runs consume the six remaining authorized replay attempts; the operator's two method probes remain labeled as probes and are not promoted to replay evidence. No new replay, follow-up, criterion edit or code repair was attempted by the scorer. This round stops with AC-7 and AC-10 held, as the follow-up assignment requires.

## Candidate and checks

The narrowed product candidate remains cdb99da0e52e8b5cad3a7be04658dc282432b644, already committed locally, with only kc-dev-flow-2/extensions/paseo/EXTENSION.md differing from the pinned base. No new product commit was needed and no empty commit was made. The worker continuation sentence and +33 budget step remain removed. The current main ref advanced to 546a136386c94c58e430c91a6f3457b38bd73880; no merge/rebase was performed during this scoring round.

Current checks in checks/: repository lint 5939/5939, ADR lint (67 records), design-surfaces, diff --check, doc_impact.py (0 affected documents), comment ratio (0 added code/comment lines, 0%, maximum 5%, 20-line floor not reached), and fresh-ref number guards all exit 0. Number guards records current base 546a136386c9, candidate cdb99da0e52e, merge-base e8664a72b0f9. These static passes cannot replace the missing runtime proof. ADRs added: none; the D2 procedure leaves ADR 0052 authority unchanged.

PR text is updated at /tmp/impl-denied-command-denies-only-that-command-pr.md and prepared-pr.md. Product push, Draft PR, RoboRev, hosted CI, independent validation and gate advancement remain FO-owned and unperformed by the worker. No CI trigger changed; per-PR cost was not measured. The implementation report is a hold, not approval to advance or deliver.
