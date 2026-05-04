'use strict';

/**
 * selector-translate.js — Canonical selector → a11y tree pattern translator.
 *
 * This module is the single definition site for selectorToA11yPattern().
 * codegen.js and any future consumer must import from here.
 *
 * Supported input forms:
 *
 *   Playwright role-selector forms (backward compat):
 *     role=X[name="Y"]        → X "Y"          (exact name match)
 *     role=X[name=/Y/]        → Y              (regex literal prefix)
 *     role=X >> nth=N         → X              (role only)
 *     role=X                  → X              (bare role)
 *     css=...                 → null           (can't convert)
 *
 *   Canonical Cand 1 subcommand forms (T2.3):
 *     find role <r> --name "<v>"  → role="<r>" name=/<v>/i
 *     find role <r>               → role="<r>"
 *     find text "<v>"             → text=/<v>/i
 *
 * Returns: string pattern for a11y tree grep, or null if conversion not possible.
 */
function selectorToA11yPattern(selector) {
  if (typeof selector !== 'string') return null;

  // ------------------------------------------------------------------
  // Cand 1 subcommand forms
  // ------------------------------------------------------------------

  // find role <r> --name "<v>"  →  role="<r>" name=/<v>/i
  var findRoleName = selector.match(/^find\s+role\s+(\S+)\s+--name\s+"([^"]+)"$/);
  if (findRoleName) {
    return 'role="' + findRoleName[1] + '" name=/' + findRoleName[2] + '/i';
  }

  // find role <r>  →  role="<r>"
  var findRoleBare = selector.match(/^find\s+role\s+(\S+)$/);
  if (findRoleBare) {
    return 'role="' + findRoleBare[1] + '"';
  }

  // find text "<v>"  →  text=/<v>/i
  var findText = selector.match(/^find\s+text\s+"([^"]+)"$/);
  if (findText) {
    return 'text=/' + findText[1] + '/i';
  }

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

  // css= or other formats → can't convert
  return null;
}

module.exports = { selectorToA11yPattern };
