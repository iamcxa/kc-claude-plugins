'use strict';

/**
 * selector-translate.js — Canonical selector → a11y tree pattern translator.
 *
 * This module is the single definition site for selectorToA11yPattern().
 * codegen.js and any future consumer must import from here.
 *
 * REACHABILITY, as of #91. This function has exactly one emission site,
 * `codegen.js:1994`, and it sits in the `else` of `if (expect.cssSelector)`. Nothing
 * the compiler produces can land there:
 *
 *   1. `compiler.js:9` is the only non-test `require` of codegen.
 *   2. `compiler.js:395` calls `generate(resolveResult.resolved, …)`, and returns early
 *      at :233/:279 whenever resolve reported errors.
 *   3. `resolver.js:353` makes `resolveVisibilityElement` push an error and return null
 *      when the element has no `cssSelector`.
 *   4. Every producer of an `active` / `element-visible` / `element-not-visible` /
 *      `or-visible` expect goes through that one function (`resolver.js:514-571`).
 *
 * So the branch is live only for callers that hand-build resolved input, which today
 * means tests. That makes deleting it — and this module with it — available as a
 * follow-up; it is deliberately NOT done here, because #121 asked for the defect to be
 * closed and a deletion touching four test files is a separate change with its own
 * blast radius. What is done here is making the defect impossible to reintroduce, so
 * the deletion can happen later without racing a correctness fix.
 *
 * Output format note: agent-browser's snapshot output formats role+name
 * elements as literal lines like `textbox "Email" [ref=e7]`. The a11y-grep
 * pattern returned by this function is consumed by `_poll_snapshot_contains`
 * via `grep -F` (fixed-string), so the output MUST match the literal
 * snapshot line format `<role> "<name>"` — not `role="<r>" name="<v>"`.
 *
 * Supported input forms:
 *
 *   Canonical Cand 2 CSS attribute forms (post-issue-#7-fix):
 *     [role="X"][aria-label="Y"]     → X "Y"          (snapshot literal)
 *     [role="X"]                     → X              (role only)
 *     [data-testid="X"]              → null           (can't a11y-grep; runner uses CSS attr selector directly)
 *     [aria-label="X"]               → null           (no role context for a11y grep)
 *
 *   Playwright role-selector forms (backward compat — UNCHANGED):
 *     role=X[name="Y"]               → X "Y"          (exact name match)
 *     role=X[name=/Y/]               → Y              (regex literal prefix)
 *     role=X >> nth=N                → X              (role only)
 *     role=X                         → X              (bare role)
 *     css=...                        → null           (can't convert)
 *
 *   Native text form (e2e-selector-canon-review — largest codemod-spike refusal
 *   class, 83 of 452 corpus selectors, `text-engine-not-a-selector`):
 *     text=Y                         → "Y"            (role-agnostic snapshot-literal
 *                                                        match; role= forms above use
 *                                                        the same snapshot line, just
 *                                                        with the role prefixed)
 *     text=Y >> nth=N                → "Y"            (chord dropped, base translated)
 *     text=/Y/                       → null           (no fixed-string image of a regex)
 *
 * Returns: string pattern for a11y tree grep, or null if conversion not
 * possible (caller falls back to _poll_visible against the raw selector).
 *
 * NOTE: `find role <r> --name "<v>"` subcommand strings are NOT supported —
 * those are agent-browser CLI subcommand chains, not selector grammar; they
 * cannot appear in mapping yaml `selector:` fields. See
 * docs/ship-flow/001-selector-grammar-alignment/design.md (Cand 1 → Cand 2
 * course correction triggered by Copilot pre-merge review on PR #8).
 */
/**
 * The single authority for turning an accessible-name value into a snapshot pattern.
 *
 * Every branch below that emits a name calls this, so "how a value becomes a pattern"
 * is decided in one place (#121). The rule it enforces is one-directional: a non-null
 * return is a pattern that can actually match, and anything that cannot be given a
 * faithful fixed-string image returns null and takes the documented `_poll_visible`
 * fallback instead of a near-miss that would silently never hit — or, worse, hit
 * something else.
 *
 * Refused, both for the same reason:
 *
 *   `"` and `\`  agent-browser renders an accessible name into the snapshot with
 *                JSON-style escaping (`"` as \" and `\` as \\, verified live against
 *                0.32.0 — the byte-exact lines are in selector-translate.test.js
 *                SNAPSHOT_ESCAPING). Wrapping the raw value emits bytes the snapshot
 *                does not contain. Reproducing the escaping here would instead rest
 *                the invariant on a third-party rendering convention this module
 *                cannot pin, so it refuses. The corpus has no instance of either
 *                character, so refusing costs nothing today.
 *
 *   empty        nothing to match on.
 *
 * The returned pattern quotes the value, which anchors it to a name boundary in the
 * snapshot line. That anchoring is load-bearing: the predecessor's regex branch
 * returned a bare unquoted prefix, so `/holder.*X/` emitted `holder` and matched
 * inside `placeholder` — a false PASS on an element the author never named.
 */
function snapshotNamePattern(value) {
  if (typeof value !== 'string') return null;
  if (value === '') return null;
  if (value.indexOf('"') !== -1 || value.indexOf('\\') !== -1) return null;
  return '"' + value + '"';
}

function selectorToA11yPattern(selector) {
  if (typeof selector !== 'string') return null;

  // ------------------------------------------------------------------
  // Cand 2 CSS attribute forms (canonical post-issue-#7)
  // ------------------------------------------------------------------

  // [role="X"][aria-label="Y"]  →  X "Y"  (snapshot-literal format)
  var roleAriaLabel = selector.match(/^\[role="([^"]+)"\]\[aria-label="([^"]+)"\]$/);
  if (roleAriaLabel) {
    var roleAriaPattern = snapshotNamePattern(roleAriaLabel[2]);
    return roleAriaPattern && roleAriaLabel[1] + ' ' + roleAriaPattern;
  }

  // Permit reversed attribute order: [aria-label="Y"][role="X"]
  var ariaLabelRole = selector.match(/^\[aria-label="([^"]+)"\]\[role="([^"]+)"\]$/);
  if (ariaLabelRole) {
    var ariaRolePattern = snapshotNamePattern(ariaLabelRole[1]);
    return ariaRolePattern && ariaLabelRole[2] + ' ' + ariaRolePattern;
  }

  // [role="X"]  →  X  (role-only; falls back to count-by-role)
  var roleOnly = selector.match(/^\[role="([^"]+)"\]$/);
  if (roleOnly) {
    return roleOnly[1];
  }

  // [data-testid="X"] / [aria-label="X"] (no role) → null
  // Compiler falls back to _poll_visible (CSS attr selector resolves natively
  // in agent-browser; no a11y-grep equivalent worth asserting against snapshot).
  if (selector.match(/^\[data-testid="[^"]+"\]$/)) return null;
  if (selector.match(/^\[aria-label="[^"]+"\]$/)) return null;

  // ------------------------------------------------------------------
  // Playwright role-selector forms (backward compat — UNCHANGED)
  // ------------------------------------------------------------------

  // role=X[name="Y"] → X "Y"
  var exactMatch = selector.match(/^role=(\w+)\[name="([^"]+)"\]/);
  if (exactMatch) {
    var exactPattern = snapshotNamePattern(exactMatch[2]);
    return exactPattern && exactMatch[1] + ' ' + exactPattern;
  }

  // role=X[name=/Y/]
  //
  // A regex value with any metacharacter has no fixed-string image, so it is refused —
  // the same ruling `text=/Y/` below already carries. The predecessor emitted the
  // literal prefix before the first metacharacter, unquoted, which is the
  // `e2e-regex-prefix-false-match` defect: `/holder.*X/` became the bare pattern
  // `holder`, and `grep -F holder` matches `- button "placeholder text" [ref=e1]`. That
  // is the false-PASS direction — an assertion succeeding quietly on an element the
  // author never named — so it is worse than losing the check.
  //
  // A regex carrying no metacharacter at all is a literal, and translates to the same
  // anchored pattern the exact form above produces. Measured over the corpus that is 44
  // of 49 values, which keep working; the 5 with metacharacters take the _poll_visible
  // fallback instead of matching the wrong thing.
  var regexMatch = selector.match(/^role=(\w+)\[name=\/([^/]+)\/\]/);
  if (regexMatch) {
    if (/[.*+?[\](){}|\\^$]/.test(regexMatch[2])) return null;
    var regexPattern = snapshotNamePattern(regexMatch[2]);
    return regexPattern && regexMatch[1] + ' ' + regexPattern;
  }

  // role=X >> nth=N → X (role name only)
  var nthMatch = selector.match(/^role=(\w+)\s*>>/);
  if (nthMatch) return nthMatch[1];

  // role=X (bare role, no attributes) → X
  var bareMatch = selector.match(/^role=(\w+)$/);
  if (bareMatch) return bareMatch[1];

  // ------------------------------------------------------------------
  // Native text form (e2e-selector-canon-review)
  // ------------------------------------------------------------------

  // text=Y → "Y" (bare or quoted value; quotes stripped, then re-quoted to the
  // same snapshot-literal shape the role= forms above already produce, so
  // _poll_snapshot_contains greps it the same way)
  //
  // Invariant: a non-null return is a pattern that can actually match. Shapes that
  // cannot be faithfully translated return null and take the documented
  // _poll_visible fallback rather than a near-miss pattern that silently never hits.
  var textMatch = selector.match(/^text=(.+)$/);
  if (textMatch) {
    var textValue = textMatch[1].trim();

    // Split a trailing chord off the value. A quoted value may itself contain `>>`
    // (e.g. text="Next >> Step"), so only look for the chord past the closing quote.
    var textQuoted = textValue.match(/^"([^"]*)"/) || textValue.match(/^'([^']*)'/);
    if (textQuoted) {
      var textTrailer = textValue.slice(textQuoted[0].length).trim();
      // Anything other than a chord after the quote is unparseable — refuse.
      if (textTrailer !== '' && textTrailer.indexOf('>>') !== 0) return null;
      textValue = textQuoted[1];
    } else {
      var textChord = textValue.indexOf('>>');
      if (textChord !== -1) textValue = textValue.slice(0, textChord).trim();
    }

    // Regex value → null. Deliberately NOT the literal-prefix extraction the role=
    // branch uses above: that emits `^Save$` for /^Save$/ and `a` for /a|b/, which
    // grep -F can never match. There is no fixed-string image of a regex.
    if (/^\/.*\/$/.test(textValue)) return null;

    // Empty values and values carrying a quote or a backslash are refused by the shared
    // authority, which is also what the role= branches above call.
    return snapshotNamePattern(textValue);
  }

  // css= or other formats → can't convert
  return null;
}

module.exports = { selectorToA11yPattern };
