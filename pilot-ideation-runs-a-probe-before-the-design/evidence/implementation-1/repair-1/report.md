# F2 wording repair

Candidate: 45d5ebb9d24665c0904aca5412123a7224d056cc; base: 88f86f2749dadb6f4ef0cf9aa089c1827096865b; branch: spacedock-ensign/pilot-ideation-runs-a-probe-before-the-design. Local commits only, no product push. Start: 2026-11-13 16:18:17 Asia/Taipei, clock.curr_time UTC +08:00. Final completion reply records the end from the same source.

The repair changes one existing workflow sentence and nothing else in the product. Its final words are:

> Every criterion's evidence command runs once on it, recording command, exit and output path per criterion, provenance included; unrunnable: `Not provable now`.

The sentence is 22 words, replacing 22. The approved checker's phrase is verbatim and contiguous even in the raw file. The workflow remains 6099 words. Ideation SKILL.md, principles.md, its Pilot profile and the shared Pilot profile contain no second version of the command/exit/output-ledger instruction. Their current-evidence and Probe provenance duties are complementary and unchanged; exact hashes are in skill-profile-review.json.

The first authorized wording was committed locally as 8fd752939e85b07a095d950ba68fb27c0e004abe and made the original AC-1 checker fail because its searched phrase was removed. FO declined an evidence-procedure change and replaced the wording assignment with message-3. The replacement commit 45d5ebb9 is on top, as directed. The original failed attempt is retained separately in attempt-1; none of its results is used as proof of the final candidate. No checker was edited or replaced. approved-procedures.json verifies the original evidence procedures' bytes.

All approved runnable acceptance evidence commands pass unchanged on the new candidate: AC-1, AC-2, AC-4, AC-5, AC-6, AC-7 and AC-10. AC-10 is the fresh-id replacement under Captain amendment 2, and still executes the corrected accept.sh AC-3 command. Exact environment, argv, exits and outputs are in check-results.json; acceptance.json maps commands to current criterion IDs. Both candidate native dispatches carry all five required properties, and both base arms are ban-only. The native suite is model-free; it does not prove the repaired wording changes a worker's behavior.

The four disposable-copy falsifiers return the expected failing exit 1 for an outside-ideation POC change, a copied ban, a removed raise and a 6100-word README (mutation-results.json). Substituting base as candidate also returns 1 (mutation-AC-1-result.json). They ran with python3 -B and bytecode disabled. All 47 lint tests pass at the final candidate; repository lint prints 6099/6099. AC-5 records the unchanged lifecycle word deltas against base.

Installed 0.41.0 ADR lint exits 0, requiring ADR 0084 against base; number guard exits 0 at the exact new head. Comment ratio exits 0 under its fewer-than-20-code-lines exemption: 4 code lines, 1 required ADR pointer, 25.0%; this is not a claim of a ratio below the 5% maximum. The same 11 document impacts retain their recorded dispositions (doc-impact-verdicts.json); no new document or product surface is needed for the clarification.

The real-task design-surfaces check initially returned 1 because amendment 2 reused the superseded AC-3 ID. FO corrected the form to fresh AC-10 and directed a pull. That unchanged command now exits 0 (design-surfaces-result.json); the earlier failure is preserved as design-surfaces-before-fo-correction.log. This worker edited no criterion. The statement and evidence procedure are the Captain's amended ones.

AC-8 remains unverified at this new head until the final independent live-worker observation; the earlier REJECTED verdict and its causal limits are preserved. AC-9 remains the accepted post-release obligation. RoboRev, hosted CI, product publication, final validation, merge and release are FO/Captain-owned and not run by this repair. One validation cycle remains. CI cost per PR was not measured; no CI trigger changed.
