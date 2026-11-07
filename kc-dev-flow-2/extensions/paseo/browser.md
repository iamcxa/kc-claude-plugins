# Worker browser checks through Paseo

For a local browser check you drive yourself, use Paseo's browser tools (`mcp__paseo__browser_*`) unless the repository's own instructions name another tool for that check. CI browser runs are unchanged. Tabs open in the background in your Paseo workspace on the most recently connected browser host; close the tabs you open.

If the tools are missing from your session, or cannot perform a step after the workaround below, use the repository's supported adapter for that step and record in your report which tool ran each step and why. A step no browser ran is reported as not run, never clean.

Known limits:
- The Captain's keyboard, including his input method, can reach a field `browser_type` is filling. Fill with `browser_evaluate` instead: set the value through the element's native value setter, dispatch a bubbling `input` event, and read the value back.
- Some React Native web buttons respond only to `browser_click` on a ref from the latest `browser_snapshot`. Refs expire when the page changes, so snapshot again first.
- `browser_evaluate` fails with `browser_timeout` after 15 seconds. For longer work, start it in one call, park the result on `window`, and poll it with short calls.
- Drawing on a signature canvas is untested. Try `browser_drag`; if the drawing does not register, use the repository's adapter for that step.
