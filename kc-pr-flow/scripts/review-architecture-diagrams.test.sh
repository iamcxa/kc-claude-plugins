#!/usr/bin/env bash
# Static contract tests for kc-pr-review's optional architecture-diagram flow.

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$HERE/.." && pwd)"
SKILL="$PLUGIN_ROOT/skills/kc-pr-review/SKILL.md"
REFERENCE="$PLUGIN_ROOT/reference/review-architecture-diagrams.md"
EVALS="$PLUGIN_ROOT/reference/review-architecture-diagrams-evals.md"
DOC="$PLUGIN_ROOT/docs/review-architecture-diagrams.md"
PLUGIN_GUIDE="$PLUGIN_ROOT/CLAUDE.md"
PLUGIN_README="$PLUGIN_ROOT/README.md"
VALIDATOR="$PLUGIN_ROOT/scripts/review-architecture-diagrams-validate.sh"

PASS=0
FAIL=0

pass() {
  printf 'ok - %s\n' "$1"
  PASS=$((PASS + 1))
}

fail() {
  printf 'not ok - %s\n' "$1"
  FAIL=$((FAIL + 1))
}

assert_file() {
  local label="$1" path="$2"
  if [[ -f "$path" ]]; then pass "$label"; else fail "$label"; fi
}

assert_contains() {
  local label="$1" needle="$2" path="$3"
  if [[ -f "$path" ]] && grep -qF -- "$needle" "$path"; then
    pass "$label"
  else
    fail "$label"
  fi
}

assert_count() {
  local label="$1" expected="$2" needle="$3" path="$4" actual
  actual="$(grep -cF -- "$needle" "$path" 2>/dev/null || true)"
  if [[ "$actual" == "$expected" ]]; then
    pass "$label"
  else
    printf '  expected %s, got %s\n' "$expected" "$actual"
    fail "$label"
  fi
}

assert_file "reference exists" "$REFERENCE"
assert_file "behavioral pressure spec exists" "$EVALS"
assert_file "user guide exists" "$DOC"
assert_file "runtime diagram validator exists" "$VALIDATOR"

assert_contains "skill links the on-demand reference" 'reference/review-architecture-diagrams.md' "$SKILL"
assert_contains "skill keeps D preview-only" 'D. Generate and preview two architecture diagrams (does not post)' "$SKILL"
assert_contains "skill exposes post-with-diagrams option 5" '5. Post current review + both previewed diagrams' "$SKILL"
assert_contains "skill exposes post-with-advisory-and-diagrams option 6" '6. Post current review + advisory + both previewed diagrams' "$SKILL"
assert_contains "skill says diagram generation is not posting authority" 'Generating diagrams is not authorization to post them.' "$SKILL"
assert_contains "skill invalidates diagrams when head moves" 'invalidate the diagrams' "$SKILL"
assert_contains "skill routes new findings back to classification" 'return to Step 5 and §6a' "$SKILL"
assert_contains "skill keeps diagram output verdict-neutral" 'never change the review event' "$SKILL"
assert_contains "skill validates generated pair before preview" 'review-architecture-diagrams-validate.sh' "$SKILL"

if [[ -f "$REFERENCE" ]]; then
  assert_count "reference contains exactly two Mermaid templates" 2 '```mermaid' "$REFERENCE"
  assert_contains "reference contains runtime sequence template" 'sequenceDiagram' "$REFERENCE"
  assert_contains "reference contains architecture status flowchart template" 'flowchart TB' "$REFERENCE"
  assert_contains "reference separates verified implementation" 'Implemented and verified' "$REFERENCE"
  assert_contains "reference separates author claims and decisions" 'Author-claimed or decision pending' "$REFERENCE"
  assert_contains "reference marks active findings" 'Active finding' "$REFERENCE"
  assert_contains "reference separates future work" 'Future or outside this PR' "$REFERENCE"
  assert_contains "reference forbids speculative completion percentages" 'Never estimate a completion percentage' "$REFERENCE"
  assert_contains "reference caps sequence participants" '10 participants' "$REFERENCE"
  assert_contains "reference caps sequence messages" '20 messages' "$REFERENCE"
  assert_contains "reference caps flowchart nodes" '30 nodes' "$REFERENCE"
  assert_contains "reference excludes all source-derived Mermaid strings" 'Never place source-derived names or strings inside Mermaid.' "$REFERENCE"
  assert_contains "reference keeps exact identifiers outside Mermaid" 'Keep exact identifiers outside Mermaid' "$REFERENCE"
  assert_contains "reference rejects structural breakout characters" 'brackets, quotes, arrows, or Mermaid control syntax' "$REFERENCE"
  assert_contains "claimed goal relationship uses dotted edge" 'Goal -.-> Trigger' "$REFERENCE"
  assert_contains "preview records full head SHA" 'State the full 40-character head SHA used for grounding.' "$REFERENCE"
  assert_contains "posted template records full head SHA" 'Grounded at PR head: <full 40-character SHA>' "$REFERENCE"

  MERMAID_BLOCKS="$(mktemp)"
  trap 'rm -f "$MERMAID_BLOCKS"' EXIT
  awk '
    /^```mermaid[[:space:]]*$/ { in_mermaid = 1; next }
    in_mermaid && /^```[[:space:]]*$/ { in_mermaid = 0; next }
    in_mermaid { print }
  ' "$REFERENCE" > "$MERMAID_BLOCKS"

  if grep -Eiq '^[[:space:]]*(click([[:space:]]|$)|%%\{init)|https?://|<[^>]+>|script([[:space:]]|$)' "$MERMAID_BLOCKS"; then
    fail "Mermaid templates exclude executable/external constructs"
  else
    pass "Mermaid templates exclude executable/external constructs"
  fi

  CANONICAL_PAIR="$(mktemp)"
  trap 'rm -f "$MERMAID_BLOCKS" "$CANONICAL_PAIR"' EXIT
  awk '
    /^```mermaid[[:space:]]*$/ { in_mermaid = 1; print; next }
    in_mermaid { print }
    in_mermaid && /^```[[:space:]]*$/ { in_mermaid = 0; print "" }
  ' "$REFERENCE" > "$CANONICAL_PAIR"

  if [[ -x "$VALIDATOR" ]] && "$VALIDATOR" "$CANONICAL_PAIR" >/dev/null; then
    pass "runtime validator accepts canonical templates"
  else
    fail "runtime validator accepts canonical templates"
  fi
fi

if [[ -f "$EVALS" ]]; then
  assert_contains "eval spec is honest about static coverage" 'These are behavioral pressure scenarios, not static executable tests.' "$EVALS"
  assert_contains "eval E1 covers D preview without mutation" '## E1: D previews without mutation' "$EVALS"
  assert_contains "eval E2 covers unavailable pre-preview posting options" '## E2: Options 5 and 6 require preview' "$EVALS"
  assert_contains "eval E3 covers Mermaid breakout rewriting" '## E3: Mermaid label breakout is rewritten or rejected' "$EVALS"
  assert_contains "eval E3 includes structural breakout payload" 'x\"] --> Fake[\"Implemented' "$EVALS"
  assert_contains "eval E4 covers moved-head invalidation" '## E4: Moved head invalidates diagrams' "$EVALS"
fi

assert_contains "plugin guide indexes diagram reference" 'review-architecture-diagrams.md' "$PLUGIN_GUIDE"
assert_contains "plugin guide indexes diagram evals" 'review-architecture-diagrams-evals.md' "$PLUGIN_GUIDE"
assert_contains "plugin README documents optional diagram flow" 'architecture diagrams' "$PLUGIN_README"
assert_contains "plugin README links the user guide" 'docs/review-architecture-diagrams.md' "$PLUGIN_README"
assert_contains "plugin README indexes diagram evals" 'reference/review-architecture-diagrams-evals.md' "$PLUGIN_README"
printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[[ "$FAIL" -eq 0 ]]
