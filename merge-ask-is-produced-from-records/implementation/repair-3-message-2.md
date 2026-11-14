# Explicit public visibility repair

Candidate: `a5657edd6531916cd01f659b888feaa021219ead`, branch `spacedock-ensign/merge-ask-is-produced-from-records`.
Repair base: `4652caa3a2f2c28bf4e395f2473b6ca00786834a`.
Evidence: `evidence/implementation-3-message-2/`.

The record route now requests `gh repo view --json visibility` and saves a record only when that field equals `PUBLIC`. Every other value takes the existing exit-2/no-record branch; a missing field takes the existing unreadable-visibility exit-2/no-record branch. It no longer infers public visibility from isPrivate false. The contract's producer instructions and public field description now state that same criterion. There is no schema-field addition or legacy-route change.

The existing public fixture now returns visibility PUBLIC. The existing negative visibility test was adjusted to use PRIVATE and a missing field, with exactly one added INTERNAL/isPrivate=false subcase and no new test method. The added case fails on the prior implementation; after repair all three cases exit 2 and create no JSON record. The existing PUBLIC record/binding test passes. Restoring the old boolean criterion in memory makes the adjusted test fail with one failure and zero errors. These are real owned-handler tests with the existing gh double, not live provider observations.

All four requested commands pass at the exact candidate: repository lint, full delivery suite (244 cases, 243 pass and one optional skip), full POC suite (nine pass), and installed comment ratio (3/562 = 0.5%, maximum 5%). Workflow words/budget remain 5996/5996. Owned caches were cleared; checks use python3 -B, PYTHONDONTWRITEBYTECODE=1 and task-owned TMPDIR. Each command, candidate, exit and log is joined in checks.json. All seven doc-impact references have unaffected reasons, and the owning contract is updated.

Repair size: three product paths, +9/-7. No new ADR, version, workflow budget or CI-definition change; CI cost per PR was not measured. The four checks and reverse mutation are green; a full 29-command rerun, RoboRev, hosted CI and independent validation were not run for this repair and are not called clean. FO owns publication and subsequent checks; no push, PR write, review request, ready transition or merge was performed.

This complete report supersedes earlier implementation assurance for the delivered candidate while preserving prior run limits. implementation/pr.md names the current behavior/checks and preserves the separate pin-deletion experiment for the Captain's ruling. The new message evidence has its own 20-file manifest; canonical scratch close rechecks the earlier implementation-3 evidence and records its output in implementation/repair-3-message-2-close.txt.
