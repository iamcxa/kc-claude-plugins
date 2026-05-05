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
# Banned token classes (each replaces with a Cand 2 native form):
#
#   CLASS 1 — Playwright role attr-style:
#     regex:  role=<word>[name=...]
#     example: role=textbox[name="Email"]
#     replace with: [role="<r>"][aria-label="<v>"] CSS attribute selector
#     (Cand 2 canonical per docs/ship-flow/001-selector-grammar-alignment/design.md)
#
#   CLASS 2 — Playwright nth chord:
#     regex:  >>\s*nth=<N>
#     example: .MuiButton-root >> nth=2
#     replace with: :nth-of-type(N) CSS pseudo-class
#
#   CLASS 3 — Playwright text engine (bare text= at start of selector value):
#     regex:  ^text=
#     example: text=Submit  (or 'text=Submit' / "text=Submit" — quotes stripped)
#     replace with: data-testid attribute or [role="..."][aria-label="..."]
#
#   CLASS 4 — Playwright has-text (broken in agent-browser, no equivalent):
#     regex:  :has-text\(
#     example: .MuiDialog >> :has-text("Confirm")
#     no direct replacement — restructure selector using data-testid or
#     CSS attribute form
#
#   CLASS 5 — agent-browser find-subcommand string in selector value (post-PR-#8):
#     regex:  ^find\s+(role|text|label|testid)\b
#     example: find role button --name "Submit"
#     replace with: [role="<r>"][aria-label="<v>"] CSS attribute selector
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
  echo "    - role=<word>[name=...]   (Playwright; use: [role=\"<r>\"][aria-label=\"<v>\"] CSS attr)"
  echo "    - >> nth=<N>              (Playwright; use: :nth-of-type(N))"
  echo "    - text= (bare prefix)     (Playwright; use: data-testid or CSS attr)"
  echo "    - :has-text(              (Playwright; no replacement — restructure)"
  echo "    - find role|text|label|testid <args>  (agent-browser subcommand chain;"
  echo "                                          NOT a selector grammar — use CSS attr)"
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

  # CLASS 1 — Playwright role attr-style
  if echo "$selector_value" | grep -qE 'role=[A-Za-z]+\[name='; then
    echo "${MAPPING_FILE}:${lineno}: role-attr: ${line}" >&2
    errors=$((errors + 1))
  fi

  # CLASS 2 — Playwright nth chord
  if echo "$selector_value" | grep -qE '>>[[:space:]]*nth=[0-9]+'; then
    echo "${MAPPING_FILE}:${lineno}: >>nth: ${line}" >&2
    errors=$((errors + 1))
  fi

  # CLASS 3 — bare text= at start of selector value (post quote-strip)
  if echo "$selector_value" | grep -qE '^text='; then
    echo "${MAPPING_FILE}:${lineno}: text=: ${line}" >&2
    errors=$((errors + 1))
  fi

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
