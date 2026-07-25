#!/usr/bin/env bash
# lint-mapping.sh — Validate a mapping YAML against the canonical agent-browser selector grammar.
#
# Usage: lint-mapping.sh <mapping-yaml-path>
#
# Exit codes:
#   0  — no banned tokens found in any selector value
#   1  — usage error (no arguments) or file not found
#   2  — banned tokens found
#
# Scope: only `selector:` field VALUES are scanned. Comments, descriptions,
# and migration notes that mention banned forms (e.g., a `description:` field
# explaining what NOT to use) are deliberately ignored — those are documentation,
# not contract violations. This narrowing was added in response to PR #8 Copilot
# review C2 (line-by-line scan flagged comments as errors, unsafe as CI gate).
#
# Banned token classes:
#
#   CLASS 1 — RETIRED (e2e-selector-canon-review, see docs/dev/.spacedock-state/
#     e2e-selector-canon-review.md). Formerly banned `role=<word>[name=...]`
#     (Playwright role attr-style, e.g. `role=textbox[name="Email"]`) in favour of
#     `[role="<r>"][aria-label="<v>"]`. Measured over 32 real mapping files, the
#     "canonical" CSS form was emitted 0 times in three months and the "banned"
#     form 2,183 times — because `compiler/lib/selector-translate.js` translates
#     both to the identical a11y-grep pattern, and the CSS form alone requires
#     literal `role`/`aria-label` attributes present in only ~2.8% of components.
#     `role=<r>[name="<v>"]` is native, faithful to what the mapper's a11y
#     snapshot actually observes, and no longer banned.
#
#   CLASS 2 — Playwright nth chord:
#     regex:  >>\s*nth=<N>
#     example: .MuiButton-root >> nth=2
#     replace with: :nth-of-type(N) CSS pseudo-class
#
#   CLASS 3 — RETIRED (e2e-selector-canon-review). Formerly banned bare `text=`
#     at selector start and pointed authors at `find text "<v>"` — itself a CLASS
#     5-banned subcommand chain, an unresolvable contradiction. `text=V` is now
#     translated by `selector-translate.js` to the a11y-grep pattern `"V"` (same
#     shape the role= forms produce), so it is a supported native form.
#
#   CLASS 4 — Playwright has-text (broken in agent-browser, no equivalent):
#     regex:  :has-text\(
#     example: .MuiDialog >> :has-text("Confirm")
#     no direct replacement — restructure selector using data-testid or
#     role=/text= form
#
#   CLASS 5 — agent-browser find-subcommand string in selector value (post-PR-#8):
#     regex:  ^find\s+(role|text|label|testid)\b
#     example: find role button --name "Submit"
#     replace with: role=<r>[name="<v>"] or [role="<r>"][aria-label="<v>"]
#     reason: `find role|text|label|testid` is an agent-browser CLI SUBCOMMAND
#     CHAIN, not a selector grammar. Storing it as a `selector:` value and
#     passing it to `agent-browser is visible|click|fill '<value>'` makes
#     agent-browser try to parse the entire string as CSS and fail.
#     Caught by Copilot review on PR #8 (R1 finding) — the linter MUST gate
#     this form pre-merge or CI green-lights mappings the runner cannot consume.

set -euo pipefail

SCRIPT_NAME="$(basename "$0")"

usage() {
  echo "Usage: $SCRIPT_NAME <mapping-yaml-path>"
  echo ""
  echo "  mapping-yaml-path  Path to the e2e mapping YAML file to lint."
  echo ""
  echo "  Checks selector field values (only) for banned tokens:"
  echo "    - >> nth=<N>              (Playwright; use: :nth-of-type(N))"
  echo "    - :has-text(              (Playwright; no replacement — restructure)"
  echo "    - find role|text|label|testid <args>  (agent-browser subcommand chain;"
  echo "                                          NOT a selector grammar — use role=/CSS attr)"
  echo ""
  echo "  role=<word>[name=...] and bare text= are NATIVE forms (translated by"
  echo "  compiler/lib/selector-translate.js) and are no longer banned."
  echo ""
  exit 1
}

# Require exactly one argument
if [[ $# -lt 1 ]]; then
  usage
fi

MAPPING_FILE="$1"

if [[ ! -f "$MAPPING_FILE" ]]; then
  echo "Error: file not found: $MAPPING_FILE" >&2
  exit 1
fi

errors=0
lineno=0

# Strip surrounding quotes (single or double) from a YAML scalar value
strip_quotes() {
  local v="$1"
  # Single-quoted
  if [[ "$v" =~ ^\'(.*)\'$ ]]; then
    printf '%s' "${BASH_REMATCH[1]}"
    return
  fi
  # Double-quoted
  if [[ "$v" =~ ^\"(.*)\"$ ]]; then
    printf '%s' "${BASH_REMATCH[1]}"
    return
  fi
  printf '%s' "$v"
}

while IFS= read -r line; do
  lineno=$((lineno + 1))

  # Only scan lines that define a `selector:` field value.
  # YAML inline value form: `<indent>selector: <value>` (block scalars / multi-line not supported — rare for selectors).
  if [[ ! "$line" =~ ^[[:space:]]*selector:[[:space:]]*(.*)$ ]]; then
    continue
  fi

  selector_value="${BASH_REMATCH[1]}"

  # Strip trailing inline comment (YAML allows ` # comment` after the value)
  selector_value="$(printf '%s' "$selector_value" | sed -E 's/[[:space:]]+#.*$//')"

  # Trim trailing whitespace
  selector_value="$(printf '%s' "$selector_value" | sed -E 's/[[:space:]]+$//')"

  # Strip outer quotes if present
  selector_value="$(strip_quotes "$selector_value")"

  # Skip empty values (e.g., `selector:` with no inline value — block scalar follows)
  if [[ -z "$selector_value" ]]; then
    continue
  fi

  # CLASS 1 — RETIRED. role=<word>[name=...] is a native form; no longer scanned.

  # CLASS 2 — Playwright nth chord
  if echo "$selector_value" | grep -qE '>>[[:space:]]*nth=[0-9]+'; then
    echo "${MAPPING_FILE}:${lineno}: >>nth: ${line}" >&2
    errors=$((errors + 1))
  fi

  # CLASS 3 — RETIRED. bare text= is a native form (selector-translate.js
  # translates it to an a11y-grep pattern); no longer scanned.

  # CLASS 4 — Playwright has-text
  if echo "$selector_value" | grep -qE ':has-text\('; then
    echo "${MAPPING_FILE}:${lineno}: has-text: ${line}" >&2
    errors=$((errors + 1))
  fi

  # CLASS 5 — agent-browser find subcommand chain in selector value (PR #8 R1 fix)
  # Matches: find role button --name "Submit"  /  find text "Submit"  /  find testid "X"
  # `find <role|text|label|testid>` is a CLI subcommand chain, not selector grammar.
  if echo "$selector_value" | grep -qE '^find[[:space:]]+(role|text|label|testid)\b'; then
    echo "${MAPPING_FILE}:${lineno}: find-subcommand: ${line}" >&2
    errors=$((errors + 1))
  fi

done < "$MAPPING_FILE"

if [[ $errors -gt 0 ]]; then
  echo "lint-mapping: $MAPPING_FILE — FAIL ($errors banned token(s) found)" >&2
  exit 2
fi

echo "lint-mapping: $MAPPING_FILE — OK"
exit 0
