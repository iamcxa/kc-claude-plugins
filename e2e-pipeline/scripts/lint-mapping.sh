#!/usr/bin/env bash
# lint-mapping.sh — Validate a mapping YAML against the canonical agent-browser selector grammar.
#
# Usage: lint-mapping.sh <mapping-yaml-path>
#
# Exit codes:
#   0  — no banned tokens found (or skeleton mode: always 0 before T1.1)
#   1  — usage error (no arguments)
#   2  — banned tokens found (after T1.1 implements the matcher)
#
# FIX-ME T1.1: implement matcher
# ─────────────────────────────────────────────────────────────────────────────
# Add four grep passes over the selector values extracted from the YAML.
# Each pass targets one banned token class:
#
#   CLASS 1 — Playwright role attr-style:
#     regex:  role=[A-Za-z]+\[name=
#     example: role=textbox[name="Email"]
#     replace with: find role <r> --name "<v>"
#     (agent-browser's `find role` subcommand; WAI-ARIA accessible-name aware)
#
#   CLASS 2 — Playwright nth chord:
#     regex:  >>\s*nth=[0-9]+
#     example: .MuiButton-root >> nth=2
#     replace with: :nth-of-type(N) CSS pseudo-class
#     (e.g., .MuiButton-root:nth-of-type(3))
#
#   CLASS 3 — Playwright text engine (bare text= at start of selector):
#     regex:  (^|['"])\s*text=
#     example: text=Submit, "text=Cancel"
#     replace with: find text "<v>" subcommand
#     (agent-browser's `find text` subcommand)
#
#   CLASS 4 — Playwright has-text (broken in agent-browser, no equivalent):
#     regex:  :has-text\(
#     example: .MuiDialog >> :has-text("Confirm")
#     note: no direct replacement — restructure selector using data-testid or find role/text
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_NAME="$(basename "$0")"

usage() {
  echo "Usage: $SCRIPT_NAME <mapping-yaml-path>"
  echo ""
  echo "  mapping-yaml-path  Path to the e2e mapping YAML file to lint."
  echo ""
  echo "  Checks selector values for banned Playwright-style token classes:"
  echo "    - role=<word>[name=...]  (use: find role <r> --name \"<v>\")"
  echo "    - >> nth=<N>             (use: :nth-of-type(N))"
  echo "    - text= (bare prefix)    (use: find text \"<v>\")"
  echo "    - :has-text(             (no replacement — restructure selector)"
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

while IFS= read -r line; do
  lineno=$((lineno + 1))

  # CLASS 1 — Playwright role attr-style: role=<word>[name=...]
  # Matches: role=textbox[name="Email"]
  # Does NOT match: find role tab --name "Lineage"  (no '=' adjacent to role name)
  if echo "$line" | grep -qE 'role=[A-Za-z]+\[name='; then
    echo "${MAPPING_FILE}:${lineno}: role-attr: ${line}" >&2
    errors=$((errors + 1))
  fi

  # CLASS 2 — Playwright nth chord: >> nth=<N>
  # Matches: .MuiButton-root >> nth=2
  if echo "$line" | grep -qE '>>[[:space:]]*nth=[0-9]+'; then
    echo "${MAPPING_FILE}:${lineno}: >>nth: ${line}" >&2
    errors=$((errors + 1))
  fi

  # CLASS 3 — Playwright text engine: bare text= at start of selector value
  # Matches: 'text=Submit'  "text=Cancel"  (text= immediately after a quote)
  # Does NOT match: find text "value"  (text= not preceded by quote)
  if echo "$line" | grep -qE "['\"]text="; then
    echo "${MAPPING_FILE}:${lineno}: text=: ${line}" >&2
    errors=$((errors + 1))
  fi

  # CLASS 4 — Playwright has-text: :has-text(
  if echo "$line" | grep -qE ':has-text\('; then
    echo "${MAPPING_FILE}:${lineno}: has-text: ${line}" >&2
    errors=$((errors + 1))
  fi

done < "$MAPPING_FILE"

if [[ $errors -gt 0 ]]; then
  echo "lint-mapping: $MAPPING_FILE — FAIL ($errors banned token(s) found)" >&2
  exit 2
fi

echo "lint-mapping: $MAPPING_FILE — OK"
exit 0
