#!/usr/bin/env bash
# dialectic-derivation-check.sh <pm-skills-install-dir>
# Checks stations 3 and 4 of docs/plan-flow/dialectic.md against CC BY-NC-SA pm-skills
# for unintended derivative work, in two layers:
# - Verbatim: extract every 6-word window from stations 3-4 and grep against all .md files
# - Structural: extract section headings and bold field labels from pm-skills SKILL.md files at runtime
#   and check if they appear in corresponding structural roles in stations 3-4
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

# Check that the three required SKILL.md files exist
PROBLEM_STATEMENT_SKILL="$PM_SKILLS_DIR/problem-statement/SKILL.md"
EPIC_HYPOTHESIS_SKILL="$PM_SKILLS_DIR/epic-hypothesis/SKILL.md"
USER_STORY_SPLITTING_SKILL="$PM_SKILLS_DIR/user-story-splitting/SKILL.md"

if [[ ! -f "$PROBLEM_STATEMENT_SKILL" ]] || [[ ! -f "$EPIC_HYPOTHESIS_SKILL" ]] || [[ ! -f "$USER_STORY_SPLITTING_SKILL" ]]; then
    echo "Error: pm-skills install directory missing required SKILL.md files" >&2
    exit 2
fi

DIALECTIC_FILE="docs/plan-flow/dialectic.md"

if [[ ! -f "$DIALECTIC_FILE" ]]; then
    echo "Error: $DIALECTIC_FILE not found" >&2
    exit 2
fi

# Extract stations 3 and 4 from dialectic.md, excluding optional checklist sections
STATION_3=$(sed -n '/^## Station 3/,/^## Station 4$/p' "$DIALECTIC_FILE" | sed '$d' | sed '/^\*\*Borrowed skill as optional checklist/,$d')
STATION_4=$(sed -n '/^## Station 4/,/^$/p' "$DIALECTIC_FILE" | sed '$d' | sed '/^\*\*Borrowed skill as optional checklist/,$d')

COMBINED_STATIONS="${STATION_3}${STATION_4}"

# ============================================================================
# LAYER 1: VERBATIM — 6-word windows
# ============================================================================
# Build corpus of all pm-skills .md files normalized
CORPUS=$(find "$PM_SKILLS_DIR" -name "*.md" -type f -print0 2>/dev/null | xargs -0 cat 2>/dev/null | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' ' ' | tr -s ' ')

# Tokenize stations 3-4 into lowercase words
NORMALIZED_TEXT=$(echo "$COMBINED_STATIONS" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' ' ' | tr -s ' ')
WORDS=($NORMALIZED_TEXT)
WINDOW_SIZE=6
WINDOWS_CHECKED=0

for ((i = 0; i <= ${#WORDS[@]} - WINDOW_SIZE; i++)); do
    WINDOW="${WORDS[i]} ${WORDS[i+1]} ${WORDS[i+2]} ${WORDS[i+3]} ${WORDS[i+4]} ${WORDS[i+5]}"
    WINDOWS_CHECKED=$((WINDOWS_CHECKED + 1))

    # Search the corpus for this window
    if echo "$CORPUS" | grep -F "$WINDOW" > /dev/null 2>&1; then
        # Find which file contains it
        HIT_FILE=$(find "$PM_SKILLS_DIR" -name "*.md" -type f -print0 2>/dev/null | xargs -0 grep -l "$WINDOW" 2>/dev/null | head -1)
        echo "DERIVATIVE: 6-word window found in stations 3-4: '$WINDOW' (source: $HIT_FILE)" >&2
        exit 1
    fi
done

# ============================================================================
# LAYER 2: STRUCTURAL — section headings and bold field labels
# ============================================================================
# Extract bold terms from stations 3-4 to check if they're derived from pm-skills field labels

DIALECTIC_BOLD=$(echo "$COMBINED_STATIONS" | grep -o '\*\*[^*]*\*\*' | sed 's/\*\*//g' | sort -u)

TERMS_DERIVED=0

for skill_file in "$PROBLEM_STATEMENT_SKILL" "$EPIC_HYPOTHESIS_SKILL" "$USER_STORY_SPLITTING_SKILL"; do
    # Extract bold field labels (bold text ending with :)
    while IFS= read -r bold_field; do
        [[ -z "$bold_field" ]] && continue
        field_lower=$(echo "$bold_field" | tr '[:upper:]' '[:lower:]' | sed 's/:$//')
        TERMS_DERIVED=$((TERMS_DERIVED + 1))

        # Check if this exact field (lowercased, without colon) appears in dialectic's bold terms
        while IFS= read -r dialectic_bold_term; do
            [[ -z "$dialectic_bold_term" ]] && continue
            dialectic_term_lower=$(echo "$dialectic_bold_term" | tr '[:upper:]' '[:lower:]' | sed 's/:$//')
            if [[ "$field_lower" == "$dialectic_term_lower" ]]; then
                echo "DERIVATIVE: Structural term from pm-skills found in stations 3-4: '$bold_field' (source: $skill_file)" >&2
                exit 1
            fi
        done <<< "$DIALECTIC_BOLD"
    done < <(grep -o '\*\*[^*]*:\*\*' "$skill_file" | sed 's/\*\*//g')

    # Extract section headings and check if they appear as headings in stations 3-4
    while IFS= read -r heading; do
        [[ -z "$heading" ]] && continue
        heading_lower=$(echo "$heading" | tr '[:upper:]' '[:lower:]')
        TERMS_DERIVED=$((TERMS_DERIVED + 1))

        # Check if this heading appears as a markdown heading in stations 3-4
        if echo "$COMBINED_STATIONS" | grep -E "^#+\s+.*$heading_lower" > /dev/null 2>&1; then
            echo "DERIVATIVE: Structural term from pm-skills found in stations 3-4: '$heading' (source: $skill_file)" >&2
            exit 1
        fi
    done < <(grep -E "^#+\s+" "$skill_file" | sed 's/^#+\s*//')
done

# If we reach here, no derivative work was detected
exit 0
