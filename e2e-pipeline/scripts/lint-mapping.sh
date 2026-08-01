#!/usr/bin/env bash
# lint-mapping.sh — Validate a mapping YAML against the canonical agent-browser selector grammar.
#
# Usage: lint-mapping.sh <mapping-yaml-path>
#
# Exit codes:
#   0  — no banned tokens found in any selector value
#   1  — usage error (no arguments), file not found, or `node` unavailable
#   2  — banned tokens found
#
# THIS SCRIPT CARRIES NO SELECTOR PATTERNS OF ITS OWN. The banned-class table and the
# scan both live in `compiler/lib/selector-policy.js`, which this script execs and which
# the compiler also calls at compile/dry-run time (#88). Before that module existed the
# ban lived here as inline bash regexes that nothing on the compiled path could invoke,
# so a mapping carrying a banned form compiled green and failed only once a browser was
# already running.
#
# The claim "this script's verdicts track that table" has an enforcement point:
# `compiler/test/selector-lint-drift.test.js` perturbs the table in a scratch copy of the
# plugin and asserts this script's output changes to match. A regex re-added here would
# turn it red.
#
# Banned classes and their replacements are documented in the module. In short:
#   CLASS 2  >> nth=<N>                        -> :nth-of-type(N)
#   CLASS 4  :has-text(                        -> restructure (no direct replacement)
#   CLASS 5  find role|text|label|testid <..>  -> role=<r>[name="<v>"]
# CLASS 1 (role=<r>[name=...]) and CLASS 3 (bare text=) are RETIRED, not deferred —
# they are native forms. See `CLAUDE.md` § Selector Priority.
#
# Scope: only `selector:` field VALUES are scanned. Comments, descriptions, and migration
# notes that mention banned forms are documentation, not contract violations — a narrowing
# added in response to PR #8 Copilot review C2.
#
# Dependency note: this script now requires `node` on PATH. It was previously pure bash.
# A consumer wiring it into a `.githooks` without `npm install` is still fine — the policy
# module imports Node builtins only, asserted by `compiler/test/selector-policy.test.js` —
# but a machine with no Node at all fails closed here instead of linting.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
POLICY_MODULE="${SCRIPT_DIR}/../compiler/lib/selector-policy.js"

if ! command -v node > /dev/null 2>&1; then
  echo "Error: lint-mapping.sh requires 'node' on PATH (the selector policy lives in compiler/lib/selector-policy.js)" >&2
  exit 1
fi

if [[ ! -f "$POLICY_MODULE" ]]; then
  echo "Error: selector policy module not found: $POLICY_MODULE" >&2
  exit 1
fi

exec node "$POLICY_MODULE" "$@"
