docs(kc-dev-flow-2): default worker browser checks to Paseo

In workflows listing paseo, dispatched workers now read a short browser guide before driving a local browser check. It defaults to Paseo tools, preserves repository instructions and CI behavior, and documents the four known limits, their workarounds, per-step fallback reporting and tab cleanup.

The existing dispatch scope-note quote gains 15 words; its first sentence, dispatch-record enforcement, workflow README and word budget remain unchanged. The worker-only guide is 222 words.

Validation:
- Existing dispatch-record suite: 115 tests, 1 optional skip; repository skill lint passed.
- Exact-head document/mutation checks: 23 of 24 passed, including both malformed scope-note placements, all four missing workarounds, word overflow and browser-evidence falsifiers.
- Fresh Codex worker: Paseo browser_list_tabs exists and one call succeeded.
- Fresh Claude worker followed the new guide, opened and snapshotted the candidate journey-map canvas on Paseo, but background screenshot calls returned screenshot_no_frame and screenshot/evaluate/click then timed out. It closed that tab and verified the real board and page-selector click using the documented repository adapter. All-Paseo end-to-end acceptance remains unproved; this is not a green browser result.
- ADR lint, number guards, design-surfaces check and comment-ratio check passed. No additional documents listed by doc_impact.py; no code or comments added.

No PR opened: no push grant. RoboRev and CI are FO-owned and not run by the implementation worker. CI cost per PR was not measured; no CI trigger changed.
