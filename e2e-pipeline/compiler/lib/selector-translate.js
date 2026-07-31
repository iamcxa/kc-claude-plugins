'use strict';

/**
 * selector-translate.js — Canonical selector → a11y tree pattern translator.
 *
 * This module is the single definition site for selectorToA11yPattern().
 * codegen.js and any future consumer must import from here.
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
function selectorToA11yPattern(selector) {
  if (typeof selector !== 'string') return null;

  // ------------------------------------------------------------------
  // Cand 2 CSS attribute forms (canonical post-issue-#7)
  // ------------------------------------------------------------------

  // [role="X"][aria-label="Y"]  →  X "Y"  (snapshot-literal format)
  var roleAriaLabel = selector.match(/^\[role="([^"]+)"\]\[aria-label="([^"]+)"\]$/);
  if (roleAriaLabel) {
    return roleAriaLabel[1] + ' "' + roleAriaLabel[2] + '"';
  }

  // Permit reversed attribute order: [aria-label="Y"][role="X"]
  var ariaLabelRole = selector.match(/^\[aria-label="([^"]+)"\]\[role="([^"]+)"\]$/);
  if (ariaLabelRole) {
    return ariaLabelRole[2] + ' "' + ariaLabelRole[1] + '"';
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
  if (exactMatch) return exactMatch[1] + ' "' + exactMatch[2] + '"';

  // role=X[name=/Y/] → extract longest literal prefix before first regex metachar
  var regexMatch = selector.match(/^role=\w+\[name=\/([^/]+)\/\]/);
  if (regexMatch) {
    // Strip regex metacharacters — take literal prefix up to first . * + ? [ ( { |
    var literal = regexMatch[1].replace(/[.*+?[\](){}|\\].*$/, '');
    return literal || regexMatch[1].replace(/[.*+?[\](){}|\\]/g, '');
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

    if (textValue === '') return null;

    // A value carrying a quote or a backslash → null, same reason as the regex case.
    // agent-browser renders an accessible name into the snapshot with JSON-style
    // escaping (`"` as \" and `\` as \\, verified live against 0.32.0 — the byte-exact
    // lines are in selector-translate.test.js SNAPSHOT_ESCAPING). Wrapping the raw
    // value would emit a pattern whose bytes differ from the snapshot's, so it would
    // never hit. Reproducing that escaping here would bet the invariant on a
    // third-party convention this module cannot pin, and the corpus has no instance
    // of either character inside a text= value, so refusing costs nothing today and
    // keeps "a non-null return can actually match" true by construction.
    if (textValue.indexOf('"') !== -1 || textValue.indexOf('\\') !== -1) return null;

    return '"' + textValue + '"';
  }

  // css= or other formats → can't convert
  return null;
}

module.exports = { selectorToA11yPattern };
