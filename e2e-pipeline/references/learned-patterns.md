# Learned Patterns

Accumulated cross-project E2E testing patterns. Auto-read during skill execution, auto-appended after skill completion.

**Source**: Skills with self-improvement capability (e2e-test, e2e-flow, e2e-skill-ops, e2e-walkthrough, e2e-map).

**Format**: Each entry follows D1 entry format from `knowledge-capture.md`.

**PR-back**: Curate locally accumulated patterns → PR to plugin origin repo → all users benefit.

---

## agent-browser headless CI: snapshot works, locators don't (2026-03-18)

On GitHub Actions Linux runners, Playwright's actionability checks fail for ALL interaction commands (`fill`, `click`, `is visible`) even though `snapshot` correctly shows the full a11y tree. Root cause undetermined — macOS headless works fine. **Workarounds**: (1) Visibility checks: `_poll_snapshot_contains` grepping a11y tree replaces `_poll_visible` with Playwright locator. (2) Fill: `agent-browser eval` with IIFE + `nativeInputValueSetter` for React controlled inputs. (3) Click: `agent-browser eval` with `querySelector.click()`. Applied to e2e-compile codegen: `selectorToA11yPattern()` converts `role=X[name="Y"]` → `X "Y"` for grep.

## Regex selector → literal prefix for grep -F (2026-03-18)

When converting `role=X[name=/pattern/]` to a grep pattern, extract the longest literal prefix before the first regex metacharacter. E.g., `/切換為.*模式/` → `切換為`. Using the full regex string with `grep -F` (fixed string) causes false negatives because `.*` is treated literally. Alternative: use `grep -q` (regex mode) but that risks unintended matches.

## Ant Design Input.Password drops name attribute (2026-03-18)

`Input.Password` does not pass the `name` prop to the inner `<input>` element. `querySelector('input[name="password"]')` returns null. Use `input[type="password"]` instead. Discovered when email eval fill succeeded but password eval fill failed in CI.

## agent-browser eval shares global scope (2026-03-18)

Consecutive `agent-browser eval` calls share the same JavaScript global scope. Declaring `const el` in two consecutive evals causes `SyntaxError: Identifier 'el' has already been declared`. Fix: wrap each eval in an IIFE `(()=>{...})()`.

## CLI-only flow recording: asciinema + agg + ffmpeg (2026-03-20)

Cross-boundary flows with zero browser steps (only `Execute external` + `Verify external`) cannot use the browser-based media pipeline (screenshots + WebM). **Pipeline**: `asciinema rec --cols 120 --rows 35 -c "<cmd>" recording.cast` → `agg --speed 2 --theme monokai` → GIF → `ffmpeg -pix_fmt yuv420p` → MP4. Media processor dispatched with `cast_path` instead of `recording_path`/`screenshots_pattern`. Headless mode (no TTY) works — asciinema outputs cast file correctly. `scale=trunc(iw/2)*2:trunc(ih/2)*2` filter required for ffmpeg libx264 even-dimension constraint. Draft release upload pattern still applies for PR posting.

## Doc scanner misses behavioral branches — snapshot-based detection gap (2026-03-21)

`e2e-doc-scanner` extracts features via surface artifacts: `--flags`, `## headings`, phase definitions, new files. Features implemented as **conditional branches within existing steps** (auto-detect logic, skip conditions, new optional agent fields) are invisible to this model. CLI-only flow support was missed because it had no flag, no heading, no new phase — just a conditional in Discover Mapping step 4. **Fix**: add diff-aware scan mode that compares `git diff` against last version tag. Any new content in SKILL.md or agent .md files gets flagged for doc coverage check, regardless of structural form. Surface extraction remains useful for full audits; diff-aware is essential for incremental doc sync after feature changes.

## React 18 _valueTracker suppresses nativeInputValueSetter onChange (2026-03-20)

`nativeInputValueSetter.call(el, value)` sets the DOM value but React 18's internal `el._valueTracker` can suppress the subsequent `input`/`change` event if the tracked value matches. Result: `dispatchEvent` fires, React sees "no change", `onChange` never called, Ant Design Form store stays empty. **Fix**: clear the tracker before dispatching: `const t=el._valueTracker;if(t)t.setValue('');`. Also add `el.focus()` before setting value to ensure React's event system is attached. Applied to e2e-compile codegen `case 'fill'` in `codegen.js`. **Silent failure**: no error thrown, no visible symptom — form just submits with empty values. Only detectable by checking the a11y tree post-fill (values missing) or observing the form stays on the same page.

## CDP resource contention: trace + record causes instability (2026-03-24)

Running `agent-browser trace start` and `record start` simultaneously causes extreme browser instability — timeouts, disconnects, truncated recordings. Root cause: both use the single CDP WebSocket. `record` fires `Page.captureScreenshot` at 10fps (every 100ms), competing with `Tracing.start(recordContinuously)` event stream. **Fix**: remove `record start/stop` entirely. Generate MP4 post-hoc from step screenshots via `e2e-media-processor` (ffmpeg concat, 2s per step). Benefits: (1) stable single CDP channel, (2) `--profile` now works with video (was incompatible with recording contexts), (3) step-paced MP4 is more useful for review than 10fps continuous capture. Trade-off: no real-time video of transitions between steps — but step screenshots capture the meaningful state, and trace.zip has the full interaction timeline for debugging.
