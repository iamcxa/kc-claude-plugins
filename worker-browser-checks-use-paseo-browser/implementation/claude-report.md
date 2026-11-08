# Claude worker canvas check — worker-browser-checks-use-paseo-browser

Candidate SHA: 20eb8255daf0f1267a8c0dd16daf0705a7cf82ba. URL: http://127.0.0.1:3900/?room=worker-browser-default-check

Result: board renders and the "Story map" page control responds to a real click — but only via the fallback adapter. The default Paseo browser path did NOT complete the check.

## Steps and tools
| Step | Tool | Outcome |
|---|---|---|
| Read extensions/paseo/browser.md | Read/Bash | done |
| Open tab | mcp__paseo__browser_new_tab | ok (tab 51fdd0f3-…, isActive=false) |
| Snapshot | mcp__paseo__browser_snapshot | ok: tldraw app, room worker-browser-default-check "Connected", "Story map" button ref @e4 expanded=false |
| Screenshot | mcp__paseo__browser_screenshot | FAILED 3x: `screenshot_no_frame` (x2, incl. after browser_wait on "Story map" matched), then fullPage `browser_timeout` 15s |
| Evaluate (DOM read) | mcp__paseo__browser_evaluate | FAILED: `browser_timeout` 15s |
| Click @e4 | mcp__paseo__browser_click | FAILED: `browser_timeout` 15s |
| Close tab | mcp__paseo__browser_close_tab | ok |
| Open, screenshot, click, screenshot, snapshot | agent-browser CLI (session wbc-claude) | all ok |

## Fallback reason
The Paseo tab stayed background/inactive (`isActive:false`) and never painted; after repeated failures it stopped answering evaluate and click. Not retried further (same approach failed twice). agent-browser is the CLI named in kc-journey-map/README.md as the repo's browser dependency. Note: this tab-never-paints behavior is a real limit of the Paseo default path in this session; the candidate doc does not list it.

## Observed (agent-browser)
- Before (claude-board-before.png, read before interacting): journey board with legend tiles EXISTS / GAP / UNVERIFIED, "Story status is not delivery acceptance.", PERSONA, ONE JOURNEY, a green sticky "讓學到的東西帶到下一件工作", UNASSIGNED lane with an orange/red sticky. Header "Room worker-…" with connected dot, page selector "Story map". Zoom 43%.
- Click: real click on the "Story map" page-selector button (@e14). Observed change: dropdown opened showing "Story map" and "建立新頁面 +"; accessibility state expanded=false → expanded=true (claude-board-after-click.png). No board content was modified.

## Evidence
- claude-board-before.png, claude-board-after-click.png (captured by agent-browser directly into this directory)
- No Paseo screenshot exists (all failed).

## Tabs
Opened: 1 Paseo tab (51fdd0f3-…), closed via browser_close_tab (ok). Opened: 1 agent-browser session wbc-claude, closed via `agent-browser close`.

## Limitations
- Paseo-driven screen read, screenshot and click: not run successfully (reported failed, not clean).
- Only one control (page selector) clicked; no board edit tested.
- Candidate-vs-served build not independently verified by me beyond the assignment's statement; see canvas-provenance.json from the implementer.

## Correction (appended; original report above unchanged)

The original report said the Paseo screenshot failed "3x". The actual count is four `mcp__paseo__browser_screenshot` calls, all failed, none produced an image:

| # | When | Params | Outcome |
|---|---|---|---|
| 1 | Initial, right after browser_snapshot | default | `screenshot_no_frame` |
| 2 | Retry | default | `screenshot_no_frame` |
| 3 | After `browser_wait` on text "Story map" matched | default | `screenshot_no_frame` |
| 4 | Next attempt | fullPage: true | `browser_timeout` after 15000ms |

The original table's "x2 ... after browser_wait" wording merged attempts 2 and 3 and undercounted. Source: my own tool results in this session, re-read; get_agent_activity matches.

Unchanged by this correction: no Paseo screenshot exists; screenshots in this directory were taken by agent-browser (fallback). This report does not claim AC-4 passed.
