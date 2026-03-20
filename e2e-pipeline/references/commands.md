# agent-browser CLI Reference (Plugin Subset)

Core commands for E2E testing agents. For full reference, see project-level `.claude/skills/agent-browser/references/commands.md`.

## Session & Navigation

```bash
agent-browser open <url>                          # Navigate (auto-creates session)
agent-browser --session <name> open <url>         # Named session (multi-site)
agent-browser --profile <path> open <url>         # Persistent auth profile (NEW daemon only!)
# NOTE: --profile is silently ignored if daemon already running. Fix: `agent-browser close` → wait → re-open.
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
- Can be called before or after `open` — if called before `open`, it launches the daemon and creates the recording context automatically
- When called before `open`, the subsequent `open` navigates within the recording context (single window)
- Stop BEFORE `close` (or video file is truncated)
- Stop BEFORE `trace stop` (recording captures the trace-stop moment)
- Path must be absolute (same as screenshots/traces)
- Output format: WebM (VP8/VP9 codec)
- `--profile` is a daemon-level option and cannot be used with recording — handle auth via auto-login or manual login after `open`

**Recommended startup order (recording ON):**
```bash
agent-browser record start "<abs-path.webm>"    # 1. Start daemon + recording context
agent-browser --headed open <url>                # 2. Navigate in recording context
agent-browser wait --load networkidle            # 3. Wait for page load
agent-browser trace start                        # 4. Start tracing
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

## MP4 Video Conversion (from WebM recording)

> **Note:** MP4 conversion is handled by the `e2e-media-processor` agent. The agent trims the first 2 seconds (browser startup blank) and applies speed adjustment.

**Canonical command** (used by media agent, smart dedup enabled):
```bash
ffmpeg -i "$REPORT_DIR/full.webm" -ss 2 \
  -filter:v "mpdecimate=hi=64*12:lo=64*5:frac=0.33,setpts=N/FRAME_RATE/TB,setpts=PTS/2" \
  -r 30 -an -c:v libx264 -pix_fmt yuv420p -y "$REPORT_DIR/<output_name>.mp4"
```

- **Smart dedup** (`mpdecimate`): drops near-duplicate frames (loading spinners, idle waits) before speed-up
- **Default speed: 2x** (`setpts=PTS/2`). Override: 1.5x = `PTS/1.5`, 1x = `PTS/1`
- **Default trim: 2 seconds** (`-ss 2`). Skips browser startup blank frames.
- `-r 30` output framerate after dedup (ensures smooth playback)
- `-an` strips audio (browser recordings have no useful audio)
- `-pix_fmt yuv420p` ensures GitHub/browser/Slack compatibility
- Output name varies by skill: `test-run.mp4`, `verification.mp4`, `walkthrough.mp4`
- **Verify**: `test -s "$REPORT_DIR/<output_name>.mp4"` (exists and size > 0)

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
