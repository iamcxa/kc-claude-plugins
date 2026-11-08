# Worker browser checks through Paseo (`mcp__paseo__browser_*`)

For attended pages, including logins where the Captain performs human verification, follow EXTENSION.md's Human terminals and pages. Repository instructions take precedence. Unattended checks use the repository's supported adapter without a required Paseo attempt. CI browser runs are unchanged. Tabs open in the background in your Paseo workspace on the most recently connected browser host; close tabs you open.

If tools are missing or a step fails after its workaround, use the repository's supported adapter for that step. Report which tool ran each step and why. A step no browser ran is not run, never clean.

Known limits:
- Keep the tab visible in the Paseo app for screenshots and clicks.
- The Captain's keyboard, including his input method, can reach a field `browser_type` is filling. Fill with `browser_evaluate` instead: set the value through the element's native value setter, dispatch a bubbling `input` event, and read the value back.
- Some React Native web buttons respond only to `browser_click` on a ref from the latest `browser_snapshot`. Refs expire when the page changes; snapshot again first.
- `browser_evaluate` fails with `browser_timeout` after 15 seconds. Start longer work in one call, park the result on `window`, and poll with short calls.
- Drawing on a signature canvas is untested. Try `browser_drag`; if the drawing does not register, use the repository's adapter for that step.
