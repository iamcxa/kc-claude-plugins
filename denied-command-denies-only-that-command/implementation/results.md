# Implementation evidence (delivery held)

Candidate: 4de97af6885d6e8aad3ed867fd56de50e14d6c05
Base: e8664a72b0f904e5dda3c391d52ab3abaca876b4
Branch: spacedock-ensign/denied-command-denies-only-that-command

Only the approved three product files changed. The initial root/path/branch verification matched the dispatch before edits. Product branch has not been pushed and no PR has been opened. FO owns publication, RoboRev, CI and the independent validation gate. The candidate is not accepted for delivery: the refusal boundary could not be exercised.

## Native replay result

Seven fresh agents were started: six worker attempts, all void, and one FO scenario agent answering both conditional scenarios. This stays within the Captain's hard stop of twelve. Four later worker arms were built but not started. No refusal answer was ever issued; no worker was steered after a refusal. C/S/Q/X/W classifications require a real refused command and are not assigned to these void runs.

The initial release-sol attempt used state 58deb9c699822a8092b5b9a450b641123ed2e344: fetch returned 0 without a permission and the task also lacked its existing direction-alignment Result. The next five runs used f3210a9de759b66294459f29ba7597fc408b7b0a, the historical ideation revision already containing that Result. Release and candidate used the same state and pinned code e8664a72b0f904e5dda3c391d52ab3abaca876b4. The only harness correction was asking Codex to use native sandbox_permissions=require_escalated for the same git fetch origin, in a standalone call, so a staged refusal could be answered. All five native calls requested that option and returned 0 in about one second, with no FO-addressable pending permission observed or notification received. See *-native-fetch.json, *-boundary-status.json and void-batch-*-activity.json. The native traces establish execution, not merely an agent's report.

| Run | Result | Reason |
| --- | --- | --- |
| Initial release sol | void | fetch succeeded; historical alignment absent |
| Release sol | void | native fetch returned 0; no refusal |
| Candidate sol 1 | void | native fetch returned 0; no refusal |
| Candidate sol 2 | void | native fetch returned 0; no refusal |
| Release astra | void | native fetch returned 0; no refusal |
| Candidate astra 1 | void | native fetch returned 0; no refusal |
| Candidate astra 2 | not run | refusal boundary unavailable |
| Candidate control sol | not run | refusal boundary unavailable |
| Candidate Claude | not run | refusal boundary unavailable |
| Candidate steer sol | not run | refusal boundary unavailable |
| Fresh FO scenario | passed | Codex sends reason by steer; Claude sends no extra message |

Four still-running void workers were canceled and all task-owned child agents archived; the release astra worker had already finished. All nine explicitly named replay fixtures were preserved under replays/ and removed with replay_dispatch.py cleanup after manifest ownership checks. The first wildcard cleanup proposal was automatically rejected for unproven ownership; the replacement enumerated and checked each directory and succeeded. No permission bypass was attempted. No synthetic denial or alternative command was substituted. A runtime method that actually produces the approved request is needed before replay can establish AC-3 through AC-7.

## Static acceptance and falsifiers

static-proof.py ran with python3 -B on fresh temporary package copies, excluding __pycache__ and *.pyc. ideation, implementation and validation show-stage-def outputs each carry the 33-word sentence once. The saved Codex and Claude dispatch artifacts each carry the same show-stage-def fetch command once. Removing ideation's context-sections drops the sentence from its output. Removing the sentence causes lint exit 1, 33 words below budget; removing its raise causes exit 1, 33 words above budget. The sentence has one package home. The Secrets bullet is byte-identical, SHA-256 fd6bab1765eb69ab501b763d9b539950076da9c2be21b5b9a62283829bcfab04. No behavioral mutation/falsifier is claimed without a valid denied-command run.

Word counts (wc -w equivalent): startup/resume 5939 -> 5972; Dispatch facts 297 -> 330; Paseo permission callback 270 -> 291. Other lifecycle passages are unchanged. The +33 budget step quotes the complete ideation gate's bound question and Captain answer, and names the loaded moment. It replaces no existing sentence: the Team bullet's existing independent-work language is limited to asking FO and did not address a command refusal; the approved design found no equivalent enforceable instruction to cut. No script enforces worker behavior; replay remains owed.

## Document impact and boundaries

ADRs added: none. This extends ADR 0037's Team instruction and records the word raise under ADR 0020; it does not replace either ruling. doc_impact.py returned seven retained documents: ADR 0020 unaffected (same quote/budget mechanism); ADR 0037 unaffected (same single Team home); ADR 0049 unaffected (model table unchanged); ADR 0052 unaffected (authority unchanged; the provider-specific reason step extends its procedure); package README unaffected (same authority, install and routing claims); maintain-flow skill unaffected (same replay method); learning.md unaffected (no learning adoption).

Local lint exits 0 at 5972/5972; 47 existing lint tests pass; ADR lint exits 0 (67 records); fresh-ref number guards exits 0 at candidate; design-surfaces exits 0; diff --check exits 0; comment ratio 0/3 code lines, 0%, package maximum 5% (floor 20 code lines, therefore the numeric cap is not enforced for this three-line addition). No CI trigger changed; per-PR CI cost was not measured. Package lint is the repository copy used by CI; other required package scripts are from the exact installed 0.38.1 root named in the dispatch.
