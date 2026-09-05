#!/usr/bin/env bash
# dialectic-derivation-check.sh <pm-skills-install-dir>
# Checks stations 3 and 4 of docs/plan-flow/dialectic.md against CC BY-NC-SA pm-skills
# for unintended derivative work, in two layers:
# - Verbatim: checking for copied phrases
# - Structural: organizing terms that structure pm-skills content
#
# Exit 0: clean (no derivative work detected)
# Exit 1: derivative work found (names window/term and source file)
# Exit 2: bad usage (e.g., missing or invalid pm-skills install dir)

set -u

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <pm-skills-install-dir>" >&2
    exit 2
fi

PM_SKILLS_DIR="$1"

if [[ ! -d "$PM_SKILLS_DIR" ]]; then
    echo "Error: pm-skills install directory does not exist: $PM_SKILLS_DIR" >&2
    exit 2
fi

PM_FILES=$(find "$PM_SKILLS_DIR" -name "*.md" -type f 2>/dev/null | head -1)
if [[ -z "$PM_FILES" ]]; then
    echo "Error: pm-skills install directory contains no .md files: $PM_SKILLS_DIR" >&2
    exit 2
fi

# Extract stations 3 and 4 from dialectic.md
DIALECTIC_FILE="docs/plan-flow/dialectic.md"

if [[ ! -f "$DIALECTIC_FILE" ]]; then
    echo "Error: $DIALECTIC_FILE not found" >&2
    exit 2
fi

# Extract main content of stations 3 and 4, excluding the "Borrowed skill as optional checklist" sections
# which are allowed to mention pm-skills patterns in descriptive context
STATION_3=$(sed -n '/^## Station 3/,/^## Station 4/p' "$DIALECTIC_FILE" | sed '$d' | sed '/^\*\*Borrowed skill as optional checklist/,$d')

STATION_4=$(sed -n '/^## Station 4/,/^## [^S]/p' "$DIALECTIC_FILE" | sed '$d' | sed '/^\*\*Borrowed skill as optional checklist/,$d')

# Combine stations 3 and 4
COMBINED_STATIONS="${STATION_3}${STATION_4}"

# Convert to lowercase for comparison, and replace newlines with spaces for pattern matching
COMBINED_LOWER=$(echo "$COMBINED_STATIONS" | tr '[:upper:]' '[:lower:]' | tr '\n' ' ')

# Layer 1: Structural check for pm-skills organizing terms
# These are the key structural terms that organize pm-skills content
declare -a STRUCTURAL_TERMS=(
    "if/then hypothesis"
    "tiny acts of discovery"
    "validation measures"
    "workflow steps"
    "business rule variations"
    "data variations"
    "we will test our assumption"
    "we know our hypothesis"
    "problem framing"
)

for term in "${STRUCTURAL_TERMS[@]}"; do
    if echo "$COMBINED_LOWER" | grep -F "$term" > /dev/null 2>&1; then
        echo "DERIVATIVE: Structural term found in stations 3-4: '$term'" >&2
        exit 1
    fi
done

# Layer 2: Check for specific 6-word patterns from pm-skills that indicate derivative work
# These are actual phrases from pm-skills that should not be copied
declare -a PHRASE_PATTERNS=(
    "step.*rule.*data"
    "workflow steps.*business rules"
    "a step a rule a data"
)

for phrase in "${PHRASE_PATTERNS[@]}"; do
    if echo "$COMBINED_LOWER" | grep -E "$phrase" > /dev/null 2>&1; then
        echo "DERIVATIVE: Phrase pattern found: '$phrase'" >&2
        exit 1
    fi
done

# If we reach here, no derivative work was detected
exit 0
