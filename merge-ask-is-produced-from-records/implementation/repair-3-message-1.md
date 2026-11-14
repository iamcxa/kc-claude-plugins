# Validation-1 F1 repair

Candidate: `4652caa3a2f2c28bf4e395f2473b6ca00786834a`, on `spacedock-ensign/merge-ask-is-produced-from-records`.
Repair base: `5e9afd496a6901cc788252a77d84f355acbf0015`; product commits `8dde371dd` and `4652caa3a`.
Evidence: `evidence/implementation-3-message-1/`.

F1 is repaired in the owning contract. It defines exactly one `Second reviewer: <name> because <trigger>` declaration when configured, the matching configured name, FO's nonempty trigger judgment, placement outside fences in the record question or legacy summary/combined input, and a working positive example. The workflow copy is not restored.

The recheck compares all 20 groups in implementation-2's immutable rule-moves.json with the contract, the actual source deletions and the real guards. It found two additional missing legacy literal forms: `External rounds: N` and `Captain steps: captain-steps/<N>.md`. The contract now gives their count/path/candidate requirements, the legacy separate-summary command and a concrete configured-reviewer outcome sentence. Every other moved rule or sentence remains in the contract or its retained owner; the bounded recheck found no further missing removed guard-required form. Per-rule dispositions are in `rule-moves-recheck.json`.

One cheap test was added. It reads the contract's examples and feeds them into the existing declaration, reviewer-outcome, round-count and Captain-step guards. It failed before the contract edit and passes now; removing each of the four required form lines makes that same test fail with zero errors. A separate reuse of the existing paired fixture reproduces both routes holding 1/1 without the declaration and passing 0/0 with the actual contract example. No new guard behavior or further test method was added.

All four requested commands pass at this exact candidate: repository lint, complete delivery suite (244 cases, 243 passes and one optional skip), complete POC suite (nine passes), and installed comment-ratio check (3/562 = 0.5%, maximum 5%). Workflow words and budget remain 5996/5996. Package caches were cleared and checks use python3 -B, PYTHONDONTWRITEBYTECODE=1 and task-owned TMPDIR. doc_impact.py lists no additional document; the contract is updated, while reference-only workflow/observer/Copilot consumers remain valid and unchanged.

The initial mutation harness exposed an empty-fence extraction error in the one new test; that test was fixed to handle an empty example without reading the intervening prose as example input. The preliminary four-command run refused completion because HEAD changed during this correction; the complete final-candidate rerun passes. Both earlier outputs and the final results are retained.

Repair size: two product paths, +43/-1 relative to the rejected candidate. delivery_gate.py, workflow, observer and Copilot bytes are unchanged. No new ADR, version, budget raise or CI-definition change; CI cost per PR was not measured. The prior 29-command suite belongs to 5e9afd496; no whole-suite rerun, RoboRev, hosted CI or independent revalidation is claimed for this repair. FO owns those later steps and publication; nothing was pushed and no progress message was sent through the FO messaging tool. The pin-deletion experiment remains its own PR-text paragraph for the Captain's ruling.

This complete repair report supersedes earlier implementation assurance for this delivered candidate while retaining all prior validation and its stated limits. Scratch-close output is in `implementation/repair-3-message-1-close.txt`; the new 28-file evidence manifest is separate from the canonical prior implementation-3 evidence rechecked by close.
