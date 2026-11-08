# Instruction review at 90192bb64db4614de9a7a94cc782ee5fa44748db

The worker entry is the existing `Add to scope notes:` quote in `EXTENSION.md`.
Its original text is preserved and the new final sentence points at `browser.md`
under the dispatched Package root. The consumer still requires only the original
first sentence, following the approved D1 recommendation; this is not new
mechanical enforcement of the browser default.

`browser.md` maps the Scope's four reported limits to these worker actions:

- Captain keyboard/input method interference: native value setter, bubbling input event, value readback.
- React Native web button: fresh snapshot ref and browser_click.
- Evaluate's 15-second timeout: start, park on window, poll with short calls.
- Signature drawing untested: try browser_drag, then the repository adapter if unregistered.

FO's recorded follow-up required one fresh Claude run with the tab visible.
The background run failed screenshots and ref-click; the visible run succeeded
entirely on Paseo. The guide therefore adds one sentence to keep the tab visible
for screenshots and clicks, within the same approved file and word cap.

Repository instructions retain precedence. Missing tools or unsuccessful
workarounds use the repository's adapter per step with the reason recorded.
No executed browser step is reported as not run; a step no browser ran stays
not run. CI is unchanged. Each worker closes the tabs it opens.

The limits above are the Scope's earlier first-hand observations, not four new
runtime reproductions by this implementation. The current proof covers a real
local canvas and Codex tool reachability, not Clerk Turnstile or signature input.

`doc_impact.py` returned `[]`: no other retained document was listed.
The two changed documents are updated; the package README extension table,
workflow README, lint budget and dispatch checker remain unchanged. No new
ADR or durable decision was introduced beyond the accepted design.

Reading moments (`wc -w`): startup/resume, either PR-idle state, archive and merge
ask have no changed passage or script output. The listed Paseo dispatch reads
1,101 -> 1,116 words (+15); worker spawn receives that same added sentence.
Only the worker about to drive a browser reads the new 235-word guide.

Runtime provenance: both canvas runs used 20eb8255daf0f1267a8c0dd16daf0705a7cf82ba.
The final candidate adds only the visibility sentence; git diff of kc-journey-map
between that revision and the final candidate is empty (asserted by acceptance.py).
The successful run's tab and the two isolated canvas processes remain available
to the Captain as the FO follow-up requires; the first run closed its own tabs.
