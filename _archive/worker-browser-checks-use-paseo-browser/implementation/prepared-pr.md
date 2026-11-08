docs(kc-dev-flow-2): scope browser guidance to attended pages

Limit the Paseo browser guidance to attended pages, including a login where the Captain performs human verification, through the existing Human terminals and pages procedure. Repository instructions take precedence; unattended checks use the repository's supported adapter without a required Paseo attempt.

The conditional dispatch pointer adds 11 words over base. The 228-word guide keeps CI behavior, placement, cleanup, per-step fallback reporting and all five limits, including the four original workarounds. It contains no instruction to automate a human-verification challenge.

Validation evidence:
- All 26 existing package test/lint commands pass from the worktree root (1,182 unittest cases, 7 optional skips), including native dispatch and recovery checks. Local native checks used Spacedock 0.27.2 with the installed 0.27.3 plugin root; hosted CI remains separate.
- Amended acceptance exercises the exact pointer, four missing-workaround mutations, the word cap and a below-cap mutation requiring an unattended Paseo attempt. Its report checker rejects a claim that the historical runs tested an unattended default.
- The two existing browser runs remain at 20eb8255daf0f1267a8c0dd16daf0705a7cf82ba: the attended run records Paseo screenshots and a ref-based click; the background run records failures and per-step adapter fallback. Neither run establishes an unattended Paseo default. No new browser check ran.
- ADR lint, number guards, design-surfaces and comment-ratio checks are recorded; no other retained document is listed by doc_impact.py. Only the two approved product documents changed, with no version or CI-trigger edits.

FO owns publication of the local candidate, PR retitling/update, fresh review and CI. RoboRev and hosted CI were not run by this implementation worker. CI cost per PR was not measured.
