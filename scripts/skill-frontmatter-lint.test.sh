#!/usr/bin/env bash

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
LINT="$HERE/skill-frontmatter-lint.sh"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

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

expect_success() {
  local label="$1"
  shift
  if "$@" >/dev/null 2>&1; then pass "$label"; else fail "$label"; fi
}

expect_failure_contains() {
  local label="$1" needle="$2" output rc
  shift 2
  output="$("$@" 2>&1)"
  rc=$?
  if [[ "$rc" -ne 0 ]] && grep -qF -- "$needle" <<<"$output"; then
    pass "$label"
  else
    printf '  expected non-zero exit with output containing: %s\n' "$needle"
    fail "$label"
  fi
}

write_valid_skill() {
  local dir="$1"
  mkdir -p "$dir"
  cat > "$dir/SKILL.md" <<'EOF'
---
name: sample-skill
description: A valid sample skill for fixture testing.
---

# Sample Skill
EOF
}

if [[ -x "$LINT" ]]; then
  pass "skill frontmatter lint script exists and is executable"
else
  fail "skill frontmatter lint script exists and is executable"
fi

# (a) valid SKILL.md passes
VALID="$TMP_DIR/valid"
mkdir -p "$VALID/pluginA/skills"
write_valid_skill "$VALID/pluginA/skills/sample-skill"
expect_success "accepts a plugin with a well-formed SKILL.md" \
  env REPO_DIR_OVERRIDE="$VALID" bash "$LINT"

# (b) missing frontmatter block fails
NO_FM="$TMP_DIR/no-frontmatter"
mkdir -p "$NO_FM/pluginA/skills/broken-skill"
cat > "$NO_FM/pluginA/skills/broken-skill/SKILL.md" <<'EOF'
# Just a heading, no frontmatter at all
EOF
expect_failure_contains "rejects a SKILL.md with no frontmatter block" "missing frontmatter block" \
  env REPO_DIR_OVERRIDE="$NO_FM" bash "$LINT"

# (b-cont) unterminated frontmatter block (opening --- with no closing ---) fails
UNTERMINATED="$TMP_DIR/unterminated"
mkdir -p "$UNTERMINATED/pluginA/skills/broken-skill"
cat > "$UNTERMINATED/pluginA/skills/broken-skill/SKILL.md" <<'EOF'
---
name: broken-skill
description: never closed

# Broken Skill
EOF
expect_failure_contains "rejects a SKILL.md with an unterminated frontmatter block" "unterminated" \
  env REPO_DIR_OVERRIDE="$UNTERMINATED" bash "$LINT"

# (c) missing description fails
NO_DESC="$TMP_DIR/no-description"
mkdir -p "$NO_DESC/pluginA/skills/broken-skill"
cat > "$NO_DESC/pluginA/skills/broken-skill/SKILL.md" <<'EOF'
---
name: broken-skill
---

# Broken Skill
EOF
expect_failure_contains "rejects a SKILL.md missing the description field" "missing or empty 'description'" \
  env REPO_DIR_OVERRIDE="$NO_DESC" bash "$LINT"

# (d) missing name fails
NO_NAME="$TMP_DIR/no-name"
mkdir -p "$NO_NAME/pluginA/skills/broken-skill"
cat > "$NO_NAME/pluginA/skills/broken-skill/SKILL.md" <<'EOF'
---
description: Missing the name field.
---

# Broken Skill
EOF
expect_failure_contains "rejects a SKILL.md missing the name field" "missing or empty 'name'" \
  env REPO_DIR_OVERRIDE="$NO_NAME" bash "$LINT"

# (e) a skills/* dir with no SKILL.md fails
STUB_DIR="$TMP_DIR/stub-dir"
mkdir -p "$STUB_DIR/pluginA/skills/stub-skill"
# no SKILL.md written on purpose
expect_failure_contains "rejects a skills/* directory with no SKILL.md" "no SKILL.md found" \
  env REPO_DIR_OVERRIDE="$STUB_DIR" bash "$LINT"

# (f) a plugin with a skills/ dir absent entirely passes trivially (not every plugin has skills)
NO_SKILLS_DIR="$TMP_DIR/no-skills-dir"
mkdir -p "$NO_SKILLS_DIR/pluginA/commands"
expect_success "accepts a plugin with no skills/ directory at all" \
  env REPO_DIR_OVERRIDE="$NO_SKILLS_DIR" bash "$LINT"

# Multi-line block-scalar description (this repo's actual convention, e.g.
# kc-hyperfocus/skills/kc-statusline-setup/SKILL.md) must still pass.
BLOCK_DESC="$TMP_DIR/block-description"
mkdir -p "$BLOCK_DESC/pluginA/skills/block-skill"
cat > "$BLOCK_DESC/pluginA/skills/block-skill/SKILL.md" <<'EOF'
---
name: block-skill
description: >
  Multi-line description using a YAML block scalar,
  matching this repo's existing SKILL.md convention.
allowed-tools: Read, Edit
---

# Block Skill
EOF
expect_success "accepts a block-scalar (>) multi-line description" \
  env REPO_DIR_OVERRIDE="$BLOCK_DESC" bash "$LINT"

# A blank-but-present description field (only a block indicator, no content) fails.
EMPTY_BLOCK_DESC="$TMP_DIR/empty-block-description"
mkdir -p "$EMPTY_BLOCK_DESC/pluginA/skills/broken-skill"
cat > "$EMPTY_BLOCK_DESC/pluginA/skills/broken-skill/SKILL.md" <<'EOF'
---
name: broken-skill
description: >
---

# Broken Skill
EOF
expect_failure_contains "rejects a description block scalar with no content" "missing or empty 'description'" \
  env REPO_DIR_OVERRIDE="$EMPTY_BLOCK_DESC" bash "$LINT"

# Must inspect every plugin's skills, not a subset (multiple plugins, one broken)
MULTI_PLUGIN="$TMP_DIR/multi-plugin"
mkdir -p "$MULTI_PLUGIN/pluginA/skills" "$MULTI_PLUGIN/pluginB/skills/broken-skill"
write_valid_skill "$MULTI_PLUGIN/pluginA/skills/sample-skill"
cat > "$MULTI_PLUGIN/pluginB/skills/broken-skill/SKILL.md" <<'EOF'
---
name: broken-skill
---
EOF
expect_failure_contains "catches a broken SKILL.md in a second plugin, not just the first" \
  "pluginB/skills/broken-skill/SKILL.md" \
  env REPO_DIR_OVERRIDE="$MULTI_PLUGIN" bash "$LINT"

# Full repo tree: lint must run cleanly against this repo's actual 35 SKILL.md files
expect_success "lint passes cleanly against this repo's actual tree" \
  env REPO_DIR_OVERRIDE="$(cd "$HERE/.." && pwd)" bash "$LINT"

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[[ "$FAIL" -eq 0 ]]
