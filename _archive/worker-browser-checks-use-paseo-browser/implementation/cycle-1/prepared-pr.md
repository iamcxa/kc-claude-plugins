docs(kc-dev-flow-2): default worker browser checks to Paseo

Workers dispatched in workflows listing paseo now read a short browser guide before driving a local browser check. The guide defaults to Paseo tools, preserves repository instructions and CI behavior, and documents tool limitations, their workarounds, per-step fallback reporting and tab cleanup.

The scope-note quote gains 15 words while its original first sentence and existing dispatch-record enforcement stay unchanged. The 235-word worker guide also records the observed requirement to keep the tab visible for screenshots and clicks.

Validation:
- Existing dispatch-record suite: 115 tests, 1 optional skip; repository skill lint passed.
- Exact-revision acceptance: 27 checks passed, including both malformed scope-note placements, four missing workarounds, word overflow and browser-evidence falsifiers; fresh exports use python3 -B with caches cleared.
- Fresh Claude worker verified the real journey-map board, screenshot and ref-based minimap click entirely through Paseo with document.visibilityState visible. The earlier background run failed and used the documented fallback; both runs are retained.
- Fresh Codex worker confirmed browser_list_tabs exists and called it once successfully.
- ADR lint, number guards, design-surfaces and comment-ratio checks passed. doc_impact.py listed no other documents. Workflow README, word budget, versions and CI triggers are unchanged.

The browser runtime was exercised at 20eb8255daf0f1267a8c0dd16daf0705a7cf82ba; final candidate 90192bb64db4614de9a7a94cc782ee5fa44748db only adds the observed visibility instruction. The kc-journey-map tree is identical at both revisions.

RoboRev and CI are FO-owned and not run by the implementation worker. CI cost per PR was not measured.
