# agent-browser CLI Reference (Plugin Subset)

Core commands for E2E testing agents. For full reference, see project-level `.claude/skills/agent-browser/references/commands.md`.

## E2E Browser Runtime (Required)

The first `open <url>` is two-phase: launch and bind `about:blank`, then attach
the init/HAR probes and navigate. Continue only when the receipt contains
`first_navigation.status: verified`. The receipt records canonical and actual
profile paths, structural snapshot lineage, pre/post daemon/browser/page
identity, URL, init-script observation, and first-document HAR status.

Browser-operating e2e-pipeline agents must route every command through the shared
runtime. The orchestrator generates one ID per invocation and gives the same ID to
all teammates in that run:

```bash
BROWSER_RUNTIME="${CLAUDE_PLUGIN_ROOT}/bin/e2e-browser-runtime.js"
BROWSER_RUN_ID=$(node "$BROWSER_RUNTIME" new-run-id)
APP="<mapping app>"
BROWSER_RECEIPT="<absolute report dir>/browser-ownership-$APP.json"
diagnostic_init_scripts=() # optional; defaults to an empty list
diagnostic_runtime_args=()
for recorder_path in "${diagnostic_init_scripts[@]}"; do
  diagnostic_runtime_args+=(--diagnostic-init-script "$recorder_path")
done
profile_liveness_projections=() # optional entries: <script-index>:<boolean-field>
profile_liveness_runtime_args=()
for projection in "${profile_liveness_projections[@]}"; do
  profile_liveness_runtime_args+=(--profile-liveness-projection "$projection")
done

e2e_browser() {
  node "$BROWSER_RUNTIME" --run-id "$BROWSER_RUN_ID" --app "$APP" \
    --receipt "$BROWSER_RECEIPT" \
    "${diagnostic_runtime_args[@]}" \
    "${profile_liveness_runtime_args[@]}" "$@"
}
```

Build `diagnostic_runtime_args` from `diagnostic_init_scripts` by appending one
`--diagnostic-init-script "<absolute recorder path>"` pair per entry. The runtime
validates and owns the wrapper lifecycle. Never pass these options to a bare
browser CLI.

The runtime creates an owned daemon namespace, selects the app session, discovers
and pins the installed Chrome for Testing executable, and ignores inherited browser
provider/config attachment settings. On first open it verifies the daemon/session
diagnostics and Chrome process/profile binding, requires `reused=false`, and writes
the receipt. A fresh replay gets a fresh `BROWSER_RUN_ID`; teammates within one
run reuse the same ID and matching receipt.

Do not use `--auto-connect`, `--cdp`, or `connect`. The runtime rejects those escape
hatches and rejects executables that are not Chrome for Testing. Close with
`e2e_browser close`, which targets only the owned namespace/session.

### Optional diagnostic init scripts

`diagnostic_init_scripts` contains local, current-user-owned JavaScript files
that run before the first application navigation. Each file must call
`publishDiagnosticProjection(schema, reader)` exactly once. The schema may
allowlist only booleans, bounded integers, declared enums, and lowercase
SHA-256 digests. After `first_navigation.status: verified`, retrieve the current
sanitized values with:

```bash
e2e_browser diagnostic-projection
```

The receipt stores hashes, safe provenance, marker status, and allowlisted field
names—not source paths, source text, or projection values. Diagnostic source
and projection output are local evidence. Never upload or commit browser
profiles, cookies, tokens, storage dumps, raw HAR, or screenshots containing
credentials.

When a run depends on profile state, make one diagnostic projection field a
caller-owned positive predicate and declare it on every runtime invocation. For
example, a recorder can publish `profile_live: true` only when a known storage
key has the expected application-specific shape, or when an authenticated-only
DOM affordance is present (the DOM form also covers HttpOnly-cookie sessions):

```js
publishDiagnosticProjection(
  { profile_live: { type: 'boolean' } },
  () => ({
    profile_live:
      document.querySelector('[data-testid="account-menu"]') !== null,
  })
);
```

With that recorder at diagnostic script index 0, add
`--profile-liveness-projection 0:profile_live`. Compiled flows accept matching
newline-delimited entries through `E2E_PROFILE_LIVENESS_PROJECTIONS` and forward
them on every owned browser invocation. The runtime polls each declared field
for up to 10 seconds after every navigation, requires the value to be exactly
`true`, and binds each sample to the captured page identity. A declared field
that stays false, changes page, is missing, or cannot be read fails the lifecycle
receipt instead of allowing navigation to become `verified`.

### What `first_navigation.status: verified` does and does not cover

It covers navigation continuity — daemon, browser, page and profile identity held
across the first application navigation — and the recorder having attached. **It
does not cover whether the profile's contents reached the page** (#149).

The two are easy to conflate, because every other profile field on the receipt
(lineage, device, inode, structural digest) is about the files — and the files
are fine in exactly the case that matters. agent-browser 0.32 snapshot mode drops
Local Storage, so a pre-authenticated profile can be completely inert while every
one of those checks passes.

So the receipt states the gap rather than leaving it to inference:

```json
"profile_state": {
  "status": "not-observed",
  "verified_covers": "navigation continuity and recorder attachment",
  "verified_excludes": "whether profile contents reached the page",
  "profile_copied_before_launch": true,
  "note": "..."
}
```

`profile_copied_before_launch` is `true` only for `verified-snapshot`, the mode
that copies the profile before launch and therefore the only one whose contents
can be lost on the way to the page. `persistent-path` hands the browser the
requested directory itself. That is a fact about which modes have a copy step,
not a prediction about any agent-browser version.

Without a declaration, `status` remains `not-observed`; a green `verified` is not
profile evidence. With a satisfied caller-declared projection, `status` is
`observed` and records the declaration, captured page identity, bounded poll
budget, and attempt count without storing the projection value.

**A receipt with no `profile_state` at all was verified by an older runtime.** The
field is written at the pending-to-verified transition, so a session already in
flight when this landed keeps a receipt without it. Those are not retrofitted on
purpose: backfilling meant writing the receipt from `snapshot`, `click` and `eval`,
which until then only read it, and teammates within one run share a receipt — a
`snapshot` could have erased a `last_navigation` a concurrent `open` had just
written. Destroying evidence to add a derived field is the wrong trade. Read
`profile_mode` on such a receipt instead: `verified-snapshot` means a copy step
existed, and the same caution applies.

If your run depends on a pre-authenticated profile, declare the positive runtime
projection above and keep the authenticated expectation in the flow as product
evidence. The runtime projection establishes profile liveness; the flow
expectation establishes application behavior.

### Flow-managed authentication

Flows that declare `auth_mode: flow-managed` do not use the canonical persistent
profile. Prepare a replay-specific profile through the same runtime:

```bash
CANONICAL_PROFILE="$HOME/.agent-browser/$APP"
PROFILE_STATE=$(node "$BROWSER_RUNTIME" \
  --run-id "$BROWSER_RUN_ID" --app "$APP" \
  --auth-mode flow-managed \
  --canonical-profile "$CANONICAL_PROFILE" \
  prepare-flow-managed-profile)
EPHEMERAL_PROFILE=$(node -e \
  'process.stdout.write(JSON.parse(process.argv[1]).profile)' \
  "$PROFILE_STATE")

e2e_flow_browser() {
  node "$BROWSER_RUNTIME" \
    --run-id "$BROWSER_RUN_ID" --app "$APP" \
    --receipt "$BROWSER_RECEIPT" \
    --auth-mode flow-managed \
    --canonical-profile "$CANONICAL_PROFILE" \
    --profile "$EPHEMERAL_PROFILE" \
    --receipt "$BROWSER_RECEIPT" "$@"
}

e2e_flow_browser --headed open <url>
e2e_flow_browser verify-flow-managed-profile
# ...capture trace/screenshots...
e2e_flow_browser cleanup-flow-managed-profile
```

Preparation fails if the requested profile already exists. Open fails unless Chrome
materializes the reserved path. Cleanup closes the owned session, compares the
canonical profile digest, and removes only the lifecycle-bound ephemeral profile.
Every replay, including Teams `RE-RUN`, prepares a different ephemeral path.

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
e2e_browser is visible "<selector>"             # Diagnostic only: first match; invalid CSS also prints false
e2e_browser is enabled @ref                     # Check if enabled
```

### Deterministic mapped visibility

Product assertions use the shared probe, not raw `is visible`:

```bash
VISIBILITY_PROBE="${CLAUDE_PLUGIN_ROOT}/bin/e2e-visibility-probe.js"
expression=$(node "$VISIBILITY_PROBE" expression --selector "$effective_selector")
transport_exit=0
envelope=$(e2e_browser eval "$expression" --json) || transport_exit=$?
printf '%s' "$envelope" | node "$VISIBILITY_PROBE" judge \
  --policy "$visibility_policy" --assert visible --transport-exit "$transport_exit"
```

Judge exit `0` is satisfied, `1` retryable, and `2` terminal. The JSON retains
`result`, policy, assertion/judgment, match/aggregate counts, bounded candidate
evidence, and sanitized error evidence. Callers add effective selector,
attempts, and elapsed time to reports. Use `not-visible` for negative
assertions. Both operands of OR are judged per attempt; a terminal result is
never masked.

## Network evidence

The request log is per-session and **survives navigation**, so a step that spans
pages does not lose the requests its earlier pages made.

```bash
e2e_browser network requests                    # List captured requests
e2e_browser network requests --clear            # Clear the log (do this BEFORE the step)
e2e_browser network requests --filter "api"     # Filter by URL pattern
e2e_browser network requests --type xhr,fetch   # Filter by resource type
e2e_browser network requests --method POST      # Filter by method
e2e_browser network requests --status 2xx       # Filter by status (200, 2xx, 400-499)
e2e_browser network request <requestId>         # Full detail INCLUDING request and response body
e2e_browser network har start                   # Begin HAR capture
e2e_browser network har stop <abs-path>         # Write the HAR
```

`network request <id> --json` returns `method`, `url`, `headers`, `postData`
(the verbatim request body), `status`, `responseHeaders`, and `responseBody`
(the verbatim response body). That is the whole HTTP artifact for one exchange —
nothing else needs to be reconstructed from a HAR to evidence a step.

Bodies are fetched per request rather than dumped wholesale on purpose: on a
document request `responseBody` is the entire page source. The per-step shape is

```bash
e2e_browser network requests --clear                                   # 1. before the step
# ...perform the step...
ids=$(e2e_browser network requests --type xhr,fetch --json | \
        node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{
          for (const r of JSON.parse(s).data.requests) console.log(r.requestId)})')
for id in $ids; do                                                     # 2. after the step
  e2e_browser network request "$id" --json                             #    full bodies
done
```

`--type xhr,fetch` keeps the document response out of the report; drop it when
the document body itself is the evidence.

What this **cannot** evidence: raw SQL output and server-side stderr. Both are
outside the browser boundary — see `docs/recording-evidence.md` § What a step can
be evidenced with before writing a per-step evidence contract against them.

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

`python3` is a shared trace prerequisite. Run `python3 --version` before any `trace start`; if it
is missing, stop before tracing. If `trace-finalization.env` is missing or unreadable after a
finalizer attempt, record a trace infrastructure failure and never dispatch analysis.

```bash
node "${CLAUDE_PLUGIN_ROOT}/bin/e2e-trace-contract.js" \
  --agent-browser "$(command -v "${E2E_AGENT_BROWSER_BIN:-agent-browser}")" \
  --output env > "$REPORT_DIR/trace-contract.env" # REQUIRED before capture
trace_producer=$(sed -n 's/^trace_producer=//p' "$REPORT_DIR/trace-contract.env")
trace_producer_version=$(sed -n 's/^trace_producer_version=//p' "$REPORT_DIR/trace-contract.env")
trace_format=$(sed -n 's/^trace_format=//p' "$REPORT_DIR/trace-contract.env")
trace_extension=$(sed -n 's/^trace_extension=//p' "$REPORT_DIR/trace-contract.env")
case "$trace_format:$trace_extension" in
  chrome-trace-json:.json|playwright-trace-zip:.zip) ;;
  *) echo "Unsupported trace contract" >&2; exit 72 ;;
esac
TRACE_PATH="$REPORT_DIR/trace${trace_extension}"
e2e_browser trace start                         # Start recording (AFTER open)
"${CLAUDE_PLUGIN_ROOT}/scripts/finalize-trace.sh" \
  --browser-runtime "$BROWSER_RUNTIME" \
  --browser-run-id "$BROWSER_RUN_ID" \
  --app "$APP" \
  --browser-receipt "$BROWSER_RECEIPT" \
  --trace-path "$TRACE_PATH" \
  --trace-producer "$trace_producer" \
  --trace-producer-version "$trace_producer_version" \
  --trace-format "$trace_format" \
  --flow-verdict "<PASS|PARTIAL|FAIL>"             # Bounded stop + validity gate
e2e_browser console --json                      # Console messages as JSON
e2e_browser console --clear                     # Clear console buffer
e2e_browser errors --json                       # JS errors as JSON
e2e_browser errors --clear                      # Clear error buffer
e2e_browser eval "<js>"                         # Execute JavaScript in page context
e2e_browser eval -b "<base64>"                  # Execute base64-encoded JS (reliable escaping)
```

Pass the runtime, run ID, and app as all-or-none argv fields, and pass the
matching receipt for every new consumer. The finalizer invokes the executable directly with
`--run-id`, `--app`, `--receipt`, and the trace/close command; it never accepts or evaluates a shell command
string. Browser-operating e2e-pipeline agents must not use the legacy direct/session mode.

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
2. **Click via @ref only**: Never click via CSS selectors. Use mapped CSS identity with the shared visibility probe; raw `is visible` is diagnostic only.
3. **Absolute paths**: agent-browser sandbox CWD differs from shell. ALWAYS use absolute screenshot/trace paths.
4. **fill > click+type**: `fill` is atomic (focus + clear + type). `click` then `type` is error-prone — @ref can change on focus.
5. **Raw is-visible semantics**: diagnostic only; it checks the first match and prints `false` for invalid CSS. Product assertions use the deterministic judge protocol above.
6. **shared trace finalizer before close**: Never call raw `trace stop` in pipeline consumers.
   Probe `${CLAUDE_PLUGIN_ROOT}/bin/e2e-trace-contract.js` before capture, then run
   `${CLAUDE_PLUGIN_ROOT}/scripts/finalize-trace.sh` with that exact producer/format contract. It
   bounds stop, detects actual output, rejects mismatches before selecting a validator, attempts
   bounded close recovery after failure, and records artifact disposition. Analyze only when
   `analysis_eligible=true`.
7. **scroll direction only**: `scroll` accepts up/down only. To scroll TO an element, use `hover @ref`.
8. **--headed for auth**: Browser must be visible when human needs to log in.
