# agent-browser CLI Reference (Plugin Subset)

Core commands for E2E testing agents. For full reference, see project-level `.claude/skills/agent-browser/references/commands.md`.

## E2E Browser Runtime (Required)

Browser-operating e2e-pipeline agents must route every command through the shared
runtime. The orchestrator generates one ID per invocation and gives the same ID to
all teammates in that run:

```bash
BROWSER_RUNTIME="${CLAUDE_PLUGIN_ROOT}/bin/e2e-browser-runtime.js"
BROWSER_RUN_ID=$(node "$BROWSER_RUNTIME" new-run-id)
APP="<mapping app>"

e2e_browser() {
  node "$BROWSER_RUNTIME" --run-id "$BROWSER_RUN_ID" --app "$APP" "$@"
}
```

The runtime creates an owned daemon namespace, selects the app session, discovers
and pins the installed Chrome for Testing executable, and ignores inherited browser
provider/config attachment settings. A fresh replay gets a fresh `BROWSER_RUN_ID`;
teammates within one run reuse the same ID.

Do not use `--auto-connect`, `--cdp`, or `connect`. The runtime rejects those escape
hatches and rejects executables that are not Chrome for Testing. Close with
`e2e_browser close`, which targets only the owned namespace/session.

## Session & Navigation

```bash
e2e_browser open <url>                          # Navigate (auto-creates session)
e2e_browser --profile <path> open <url>         # Persistent auth profile
e2e_browser --headed open <url>                 # Visible browser (required for auth)
e2e_browser close                               # Close current session
e2e_browser back                                # Go back
e2e_browser reload                              # Reload page
```

For multi-site work, set `APP` to the site mapping's `app` value before invoking
`e2e_browser`; do not add `--session` manually.

## Observation

```bash
e2e_browser snapshot                            # Full accessibility tree with @ref tags
e2e_browser snapshot -i                         # Interactive elements only (recommended)
e2e_browser snapshot -s "#selector"             # Scope to CSS selector (reduces noise)
e2e_browser screenshot <abs-path>               # Save screenshot (MUST use absolute paths)
e2e_browser screenshot --annotate <abs-path>    # Labeled screenshot (fall back to plain if fails)
e2e_browser screenshot --full <abs-path>        # Full page screenshot
e2e_browser get url                             # Current page URL
e2e_browser get text @ref                       # Get element text
e2e_browser get count ".selector"               # Count matching elements
e2e_browser is visible "<selector>"             # Returns "true"/"false" TEXT (exit code always 0!)
e2e_browser is enabled @ref                     # Check if enabled
```

## Interaction (ALWAYS use @ref from latest snapshot)

```bash
e2e_browser click @ref                          # Click element
e2e_browser fill @ref "<text>"                  # Focus + clear + type (PREFERRED over click+type)
e2e_browser type @ref "<text>"                  # Type without clearing
e2e_browser select @ref "<value>"               # Select dropdown option
e2e_browser hover @ref                          # Hover (also scrolls element into view)
e2e_browser press "<key>"                       # Keyboard (Enter, Tab, Escape, etc.)
e2e_browser press "Control+a"                   # Key combination
e2e_browser scroll down                         # Scroll page down (NOT to element — use hover)
e2e_browser scroll up                           # Scroll page up
e2e_browser check @ref                          # Check checkbox
e2e_browser uncheck @ref                        # Uncheck checkbox
```

## Waiting

```bash
e2e_browser wait --load networkidle             # Wait for network idle (after navigation)
e2e_browser wait "<selector>"                   # Wait for element to appear
e2e_browser wait "<selector>" --timeout <ms>    # With timeout in milliseconds
e2e_browser wait --text "Success"               # Wait for text on page
e2e_browser wait --url "**/dashboard"           # Wait for URL pattern
e2e_browser wait 2000                           # Wait fixed milliseconds
```

## Tracing & Health

```bash
e2e_browser trace start                         # Start recording (AFTER open)
e2e_browser trace stop "<abs-path>"             # Save trace.zip (BEFORE close!)
e2e_browser console --json                      # Console messages as JSON
e2e_browser console --clear                     # Clear console buffer
e2e_browser errors --json                       # JS errors as JSON
e2e_browser errors --clear                      # Clear error buffer
e2e_browser eval "<js>"                         # Execute JavaScript in page context
e2e_browser eval -b "<base64>"                  # Execute base64-encoded JS (reliable escaping)
```

## Recording (DEPRECATED)

> **Video is now generated from step screenshots by the `e2e-media-processor` agent.**
> The `record start/stop` commands are no longer used in the pipeline — they caused instability when running simultaneously with `trace start/stop`. If you need raw WebM recording for debugging, the commands still exist in agent-browser but are not part of the standard pipeline.

**Recommended startup order:**
```bash
e2e_browser --profile <auth_profile> --headed open <url>   # 1. Open with auth profile
e2e_browser wait --load networkidle                         # 2. Wait for page load
e2e_browser trace start                                     # 3. Start tracing
```

## GIF Generation (from per-step screenshots)

> **Note:** GIF generation is handled by the `e2e-media-processor` agent, dispatched by skills after browser agents return. The agent performs blank frame detection (skipping leading/trailing white/black frames) before generating the GIF. Manual GIF generation is no longer needed in browser agents.

**Canonical command** (used by media agent):
```bash
ffmpeg -f concat -safe 0 -r 1 -i "$REPORT_DIR/gif-frames.txt" \
  -vf "scale=800:-1:flags=lanczos" -loop 0 -y "$REPORT_DIR/steps.gif"
```

- `gif-frames.txt` contains only non-blank screenshot paths (blank = pixel value >250 or <5)
- Framerate 1 = each screenshot holds 1 second
- Width 800px, height auto-scaled with lanczos filter
- `-loop 0` = infinite loop
- **Verify**: `test -s "$REPORT_DIR/steps.gif"` (exists and size > 0)

## MP4 Video Generation (from step screenshots)

> **Note:** MP4 generation is handled by the `e2e-media-processor` agent. It uses the same non-blank screenshots as GIF generation, with configurable duration per step (default: 2 seconds).

**Canonical command** (used by media agent):
```bash
# mp4-frames.txt has "file 'path'" + "duration 2" per frame
ffmpeg -f concat -safe 0 -i "$REPORT_DIR/mp4-frames.txt" \
  -vf "scale=800:-1:flags=lanczos,pad=ceil(iw/2)*2:ceil(ih/2)*2" \
  -c:v libx264 -pix_fmt yuv420p -y "$REPORT_DIR/<output_name>.mp4"
```

- **Step-paced**: Each screenshot holds for `step_duration` seconds (default: 2s)
- Uses same non-blank frame set as GIF (blank detection already done)
- `pad=ceil(...)` ensures even dimensions (required by libx264)
- `-pix_fmt yuv420p` ensures GitHub/browser/Slack compatibility
- Output name varies by skill: `test-run.mp4`, `verification.mp4`, `walkthrough.mp4`
- **Verify**: `test -s "$REPORT_DIR/<output_name>.mp4"` (exists and size > 0)

## Semantic Locators (alternative to @ref)

```bash
e2e_browser find role button click --name "Submit"   # By ARIA role
e2e_browser find text "Sign In" click                # By text content
e2e_browser find testid "submit-btn" click           # By data-testid
e2e_browser find label "Email" fill "user@test.com"  # By label
```

## Critical Rules

1. **@ref scope**: Refs invalidate after ANY DOM change (click, fill, navigate, even snapshot on dynamic pages). ALWAYS re-snapshot before using @ref.
2. **Click via @ref only**: Never click via CSS selectors. Use selectors only for `is visible` checks.
3. **Absolute paths**: agent-browser sandbox CWD differs from shell. ALWAYS use absolute screenshot/trace paths.
4. **fill > click+type**: `fill` is atomic (focus + clear + type). `click` then `type` is error-prone — @ref can change on focus.
5. **is visible exit code**: Always 0. Check stdout text "true"/"false", NOT exit code. Don't chain with `&&`.
6. **trace before close**: Always `trace stop` before `close` or trace data is lost.
7. **scroll direction only**: `scroll` accepts up/down only. To scroll TO an element, use `hover @ref`.
8. **--headed for auth**: Browser must be visible when human needs to log in.
