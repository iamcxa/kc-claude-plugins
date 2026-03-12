# Common Browser Testing Patterns

Patterns and gotchas for E2E testing agents. For project-specific patterns, check `<project>/.claude/skills/agent-browser/references/`.

## SPA Navigation

- After `open <url>`, always `wait --load networkidle` before snapshot
- Client-side routing may not trigger network activity — verify URL after wait
- Some SPAs use infinite polling (websocket/SSE) — networkidle may hang. Use element wait as fallback
- Auth-protected apps redirect to login on first load — 3xx is normal, check URL after wait

## Authentication

- Auth profiles persist in `~/.agent-browser/<app>/`
- Profile MISSING on first run — open `--headed`, human logs in manually
- Verify auth: `get url` + check against known signin path (substring check)
- Auth expired: DON'T close browser — user re-logs in existing `--headed` window
- Clear auth state: `eval "localStorage.clear(); sessionStorage.clear();"` then `open <base_url>`
- If mapping has `auth.type: none` — skip all auth checks, profile auto-creates on first open

## Ant Design Components

- **Select**: click `.ant-select` -> wait `.ant-select-dropdown` -> snapshot scoped to dropdown -> click option @ref
- **Modal**: wait `.ant-modal` -> snapshot scoped to `.ant-modal` -> interact within modal
- **Table**: snapshot scoped to `.ant-table` to reduce noise (10+ rows = 100+ @refs)
- **Segmented control**: CSS-hidden radio inputs. `is visible` returns false. Verify via snapshot a11y tree instead
- **Popover/Tooltip**: wait for `.ant-popover` after hover trigger

## React Native Web (Expo)

- Text elements render TWICE in DOM (nth=0 hidden, nth=1 visible) — use `>> nth=1` for `text=` selectors
- `text=` does substring match — use `text="exact"` with quotes for exact match
- Tab bars get proper `role=tab[name="..."]` attributes — prefer over `text=`
- Multi-row table elements need `>> nth=0` for "at least one exists" assertion

## Repeated Elements (Tables, Lists)

- Multiple matches -> strict mode violation
- Use `>> nth=0` for "at least one exists" check
- Use `>> nth=N` for specific row/item
- Per-row buttons (edit, delete) all share same selector — must use nth or @ref

## Selector Priority (for mapping files)

1. `data-testid` — best stability, explicit test anchor
2. `role=button[name="..."]` — good, accessible, reliable
3. `role=button[name=/pattern/]` — regex partial match
4. `css=[aria-label="..."]` — semantic
5. NEVER use `css=...has-text('...')` — broken in agent-browser, times out

## Snapshot vs is visible

- Snapshot a11y tree does NOT expose `data-testid` or `aria-label` attributes
- Use `is visible "<selector>"` for DOM-level verification of attribute-based selectors
- Use snapshot for @ref extraction and text/role verification
- `is visible` returns text "true"/"false" but exit code is always 0

## Known Noise (filter before reporting)

- HMR websocket messages (hot module replacement)
- favicon 404 errors
- React DevTools warnings
- Browser extension background requests
- App-specific: check project's `health.known_noise` in mapping files

## Browser Crash / Hang Recovery

- **Detection**: If an `agent-browser` command hangs beyond the step timeout (or 60 seconds default), the browser process may be unresponsive.
- **Recovery sequence**: `agent-browser close` (force-close the context) → re-open with `agent-browser --profile <path> --headed open <url>` → re-authenticate if needed → resume from the failed step.
- **Save partial results**: Before retrying, write whatever report data was collected so far. A partial report is better than no report.
- **Max retries**: Attempt recovery once. If the browser crashes again on the same step, STOP and report: "Browser unresponsive on step `<id>`. Partial results saved to `<report_dir>`."
- **Common causes**: Memory-heavy pages, infinite redirect loops, unresponsive dev server, stale browser profiles.

## Trace Analysis

- `trace.zip` contains: `trace.network` (JSONL HAR), `trace.trace` (JSONL events), `resources/` (response bodies)
- View interactively: `npx playwright show-trace trace.zip`
- Response bodies in `resources/` are SHA1-referenced files
- Filter trace.network for `status >= 400` to find API failures
- Filter trace.trace for console errors (after noise removal)
