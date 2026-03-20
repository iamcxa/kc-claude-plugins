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

## React 18 _valueTracker suppresses nativeInputValueSetter onChange (2026-03-20)

`nativeInputValueSetter.call(el, value)` sets the DOM value but React 18's internal `el._valueTracker` can suppress the subsequent `input`/`change` event if the tracked value matches. Result: `dispatchEvent` fires, React sees "no change", `onChange` never called, Ant Design Form store stays empty. **Fix**: clear the tracker before dispatching: `const t=el._valueTracker;if(t)t.setValue('');`. Also add `el.focus()` before setting value to ensure React's event system is attached. Applied to e2e-compile codegen `case 'fill'` in `codegen.js`. **Silent failure**: no error thrown, no visible symptom — form just submits with empty values. Only detectable by checking the a11y tree post-fill (values missing) or observing the form stays on the same page.
