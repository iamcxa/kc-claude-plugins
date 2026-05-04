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

# FIX-ME T1.1: Replace this skeleton body with the actual 4-class matcher.
# The skeleton always exits 0 so T1.1's GREEN test can fail against the
# legacy-playwright-mapping.yaml fixture (which should exit 2 after T1.1 lands).

echo "lint-mapping: $MAPPING_FILE — OK (skeleton, no checks yet)"
exit 0
