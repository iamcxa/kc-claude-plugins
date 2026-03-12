# agent-browser CLI Reference (Plugin Subset)

Core commands for E2E testing agents. For full reference, see project-level `.claude/skills/agent-browser/references/commands.md`.

## Session & Navigation

```bash
agent-browser open <url>                          # Navigate (auto-creates session)
agent-browser --session <name> open <url>         # Named session (multi-site)
agent-browser --profile <path> open <url>         # Persistent auth profile
agent-browser --headed open <url>                 # Visible browser (required for auth)
agent-browser close                               # Close current session
agent-browser --session <name> close              # Close named session
agent-browser back                                # Go back
agent-browser reload                              # Reload page
```

## Observation

```bash
agent-browser snapshot                            # Full accessibility tree with @ref tags
agent-browser snapshot -i                         # Interactive elements only (recommended)
agent-browser snapshot -s "#selector"             # Scope to CSS selector (reduces noise)
agent-browser screenshot <abs-path>               # Save screenshot (MUST use absolute paths)
agent-browser screenshot --annotate <abs-path>    # Labeled screenshot (fall back to plain if fails)
agent-browser screenshot --full <abs-path>        # Full page screenshot
agent-browser get url                             # Current page URL
agent-browser get text @ref                       # Get element text
agent-browser get count ".selector"               # Count matching elements
agent-browser is visible "<selector>"             # Returns "true"/"false" TEXT (exit code always 0!)
agent-browser is enabled @ref                     # Check if enabled
```

## Interaction (ALWAYS use @ref from latest snapshot)

```bash
agent-browser click @ref                          # Click element
agent-browser fill @ref "<text>"                  # Focus + clear + type (PREFERRED over click+type)
agent-browser type @ref "<text>"                  # Type without clearing
agent-browser select @ref "<value>"               # Select dropdown option
agent-browser hover @ref                          # Hover (also scrolls element into view)
agent-browser press "<key>"                       # Keyboard (Enter, Tab, Escape, etc.)
agent-browser press "Control+a"                   # Key combination
agent-browser scroll down                         # Scroll page down (NOT to element — use hover)
agent-browser scroll up                           # Scroll page up
agent-browser check @ref                          # Check checkbox
agent-browser uncheck @ref                        # Uncheck checkbox
```

## Waiting

```bash
agent-browser wait --load networkidle             # Wait for network idle (after navigation)
agent-browser wait "<selector>"                   # Wait for element to appear
agent-browser wait "<selector>" --timeout <ms>    # With timeout in milliseconds
agent-browser wait --text "Success"               # Wait for text on page
agent-browser wait --url "**/dashboard"           # Wait for URL pattern
agent-browser wait 2000                           # Wait fixed milliseconds
```

## Tracing & Health

```bash
agent-browser trace start                         # Start recording (AFTER open)
agent-browser trace stop "<abs-path>"             # Save trace.zip (BEFORE close!)
agent-browser console --json                      # Console messages as JSON
agent-browser console --clear                     # Clear console buffer
agent-browser errors --json                       # JS errors as JSON
agent-browser errors --clear                      # Clear error buffer
agent-browser eval "<js>"                         # Execute JavaScript in page context
agent-browser eval -b "<base64>"                  # Execute base64-encoded JS (reliable escaping)
```

## Recording

```bash
agent-browser record start "<abs-path.webm>"        # Start viewport recording (WebM)
agent-browser record stop                            # Stop recording and save file
agent-browser record restart "<abs-path.webm>"       # Stop current + start new recording
```

**Rules:**
- Start AFTER `open` (browser must be active)
- Stop BEFORE `close` (or video file is truncated)
- Stop BEFORE `trace stop` (recording captures the trace-stop moment)
- Path must be absolute (same as screenshots/traces)
- Output format: WebM (VP8/VP9 codec)
- Creates a fresh browser context but preserves cookies and localStorage
- If no URL provided to `start`, records current page

**Known limitation (v0.16.x):** `record start` is incompatible with `--profile` sessions. When the browser was opened with `--profile`, `record start` fails with "Browser not launched." **Workaround:** Open without `--profile` and handle auth manually (auto-login via fill commands or manual prompt). See walkthrough reference.md and test-runner agent for recording-aware startup procedures.

## GIF Generation (from per-step screenshots)

```bash
ffmpeg -framerate 1 -pattern_type glob -i "$REPORT_DIR/step-*.png" \
  -vf "scale=800:-1:flags=lanczos" -loop 0 -y "$REPORT_DIR/steps.gif"
```

- Framerate 1 = each screenshot holds 1 second
- Width 800px, height auto-scaled with lanczos filter
- `-loop 0` = infinite loop
- If ffmpeg fails (no screenshots, missing binary), warn but continue — GIF is optional
- **Verify**: `test -s "$REPORT_DIR/steps.gif"` (exists and size > 0)

## MP4 Video Conversion (from WebM recording)

```bash
ffmpeg -i "$REPORT_DIR/full.webm" -filter:v "setpts=PTS/1.5" \
  -an -c:v libx264 -pix_fmt yuv420p -y "$REPORT_DIR/walkthrough.mp4"
```

- **Default speed: 1.5x** (`setpts=PTS/1.5`). Override: 2x = `PTS/2`, 1x = `PTS/1`
- `-an` strips audio (browser recordings have no useful audio)
- `-pix_fmt yuv420p` ensures GitHub/browser/Slack compatibility
- If ffmpeg fails, warn but continue — MP4 is optional (WebM still available)
- **Verify**: `test -s "$REPORT_DIR/walkthrough.mp4"` (exists and size > 0)
- For test runner: output name is `test-run.mp4` instead of `walkthrough.mp4`

## Semantic Locators (alternative to @ref)

```bash
agent-browser find role button click --name "Submit"   # By ARIA role
agent-browser find text "Sign In" click                # By text content
agent-browser find testid "submit-btn" click           # By data-testid
agent-browser find label "Email" fill "user@test.com"  # By label
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
