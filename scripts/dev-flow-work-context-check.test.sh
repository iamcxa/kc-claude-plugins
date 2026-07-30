#!/usr/bin/env bash

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
CHECKER="$HERE/dev-flow-work-context-check.py"
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

expect_result() {
  local label="$1" expected_rc="$2" needle="$3" output rc
  shift 3
  output="$("$@" 2>&1)"
  rc=$?
  if [[ "$rc" -eq "$expected_rc" ]] && grep -qF -- "$needle" <<<"$output"; then
    pass "$label"
  else
    printf '  expected rc=%s and output containing: %s\n' "$expected_rc" "$needle"
    printf '  actual rc=%s output=%s\n' "$rc" "$output"
    fail "$label"
  fi
}

expect_bound_receipt() {
  local label="$1" task="$2" before after
  before="$(validate "$FIXTURE" "$task")"
  printf '\nreceipt mutation\n' >> "$task"
  after="$(validate "$FIXTURE" "$task")"
  if python3 - "$before" "$after" <<'PY'
import json
import re
import sys

before, after = (json.loads(value) for value in sys.argv[1:])
assert before["capability"] == "bound_field_validation"
assert before["mode"] == "required"
assert before["operation"] == "validate"
assert before["adapter"] == "scripts/dev-flow-work-context-check.py"
assert before["authority"] == "captain or designated state migration owner"
before_hash = before["input"]["task"]["sha256"]
after_hash = after["input"]["task"]["sha256"]
assert re.fullmatch(r"[0-9a-f]{64}", before_hash)
assert before_hash != after_hash
assert before["input_revision"] != after["input_revision"]
PY
  then
    pass "$label"
  else
    fail "$label"
  fi
}

expect_iteration_declaration_binding() {
  local label="$1" root="$2" advisory authoritative
  advisory="$(audit "$root")"
  authoritative="$(audit "$root" --iteration-migration-complete)"
  if python3 - "$advisory" "$authoritative" <<'PY'
import json
import sys

advisory, authoritative = (json.loads(value) for value in sys.argv[1:])
assert advisory["input"]["declaration"]["iteration_migration_complete"] is False
assert authoritative["input"]["declaration"]["iteration_migration_complete"] is True
assert advisory["input_revision"] != authoritative["input_revision"]
PY
  then
    pass "$label"
  else
    fail "$label"
  fi
}

write_providers() {
  local root="$1"
  mkdir -p "$root/.claude-plugin" "$root/docs/dev"
  cat > "$root/.claude-plugin/marketplace.json" <<'EOF'
{"plugins":[{"name":"alpha"},{"name":"beta"}]}
EOF
  cat > "$root/docs/dev/ROADMAP.md" <<'EOF'
# Roadmap

## `alpha`

### Sprint S1 — first

## `beta`

No sprint is scheduled.

## `repo-platform`

### Sprint S2 — shared
EOF
  printf '/state/\n/state-seed/\n' > "$root/.gitignore"
  git -C "$root" init -q
  git -C "$root" checkout -q -b main
  git -C "$root" config user.name "Dev Flow Fixture"
  git -C "$root" config user.email "dev-flow-fixture@example.invalid"
  git -C "$root" add .gitignore .claude-plugin/marketplace.json docs/dev/ROADMAP.md
  git -C "$root" commit -qm "fixture: providers"
}

write_task() {
  local path="$1" product_line="$2" sprint_line="$3"
  mkdir -p "$(dirname "$path")"
  cat > "$path" <<EOF
---
title: Fixture task
status: backlog
$product_line
$sprint_line
---

# Fixture
EOF
}

validate() {
  local root="$1" task="$2"
  python3 "$CHECKER" validate \
    --task "$task" \
    --marketplace "$root/.claude-plugin/marketplace.json" \
    --roadmap "$root/docs/dev/ROADMAP.md"
}

audit() {
  local root="$1"
  shift
  python3 "$CHECKER" audit \
    --state-dir "$root/state" \
    --marketplace "$root/.claude-plugin/marketplace.json" \
    --roadmap "$root/docs/dev/ROADMAP.md" \
    "$@"
}

seal_state() {
  local root="$1" seed="$1/state-seed"
  mv "$root/state" "$seed"
  git -C "$root" worktree add -q -b spacedock-state/dev "$root/state"
  cp -R "$seed/." "$root/state/"
  rm -rf "$seed"
  git -C "$root/state" add -A
  if ! git -C "$root/state" diff --cached --quiet; then
    git -C "$root/state" commit -qm "state: fixture"
  fi
}

FIXTURE="$TMP_DIR/fixture"
write_providers "$FIXTURE"

VALID_BLANK="$FIXTURE/valid-blank.md"
write_task "$VALID_BLANK" "product: alpha" "sprint:"
expect_result "accepts a registered scalar product with a blank sprint" 0 '"outcome":"PASS"' \
  validate "$FIXTURE" "$VALID_BLANK"

BOUND_RECEIPT="$FIXTURE/bound-receipt.md"
write_task "$BOUND_RECEIPT" "product: alpha" "sprint:"
expect_bound_receipt "receipt binds capability and exact input bytes" "$BOUND_RECEIPT"

MISSING_PRODUCT="$FIXTURE/missing-product.md"
write_task "$MISSING_PRODUCT" "source: fixture" "sprint:"
expect_result "rejects a missing product" 1 '"code":"product_missing"' \
  validate "$FIXTURE" "$MISSING_PRODUCT"

LIST_PRODUCT="$FIXTURE/list-product.md"
write_task "$LIST_PRODUCT" "product: [alpha, beta]" "sprint:"
expect_result "rejects a collection-shaped product" 1 '"code":"product_not_scalar"' \
  validate "$FIXTURE" "$LIST_PRODUCT"

UNKNOWN_PRODUCT="$FIXTURE/unknown-product.md"
write_task "$UNKNOWN_PRODUCT" "product: gamma" "sprint:"
expect_result "rejects an unregistered product" 1 '"code":"product_unknown"' \
  validate "$FIXTURE" "$UNKNOWN_PRODUCT"

VALID_SPRINT="$FIXTURE/valid-sprint.md"
write_task "$VALID_SPRINT" "product: alpha" "sprint: S1"
expect_result "accepts a registered product and roadmap sprint pair" 0 '"outcome":"PASS"' \
  validate "$FIXTURE" "$VALID_SPRINT"

MALFORMED_SPRINT="$FIXTURE/malformed-sprint.md"
write_task "$MALFORMED_SPRINT" "product: alpha" "sprint: sprint-1"
expect_result "rejects a malformed sprint scalar" 1 '"code":"sprint_malformed"' \
  validate "$FIXTURE" "$MALFORMED_SPRINT"

UNKNOWN_PAIR="$FIXTURE/unknown-pair.md"
write_task "$UNKNOWN_PAIR" "product: beta" "sprint: S1"
expect_result "rejects a product and sprint pair absent from the roadmap" 1 '"code":"sprint_unregistered"' \
  validate "$FIXTURE" "$UNKNOWN_PAIR"

DUPLICATE_PRODUCT="$FIXTURE/duplicate-product.md"
cat > "$DUPLICATE_PRODUCT" <<'EOF'
---
title: Duplicate
status: backlog
product: alpha
product: beta
sprint:
---
EOF
expect_result "rejects duplicate controlled frontmatter fields" 1 '"code":"controlled_field_duplicate"' \
  validate "$FIXTURE" "$DUPLICATE_PRODUCT"

MALFORMED_FRONTMATTER="$FIXTURE/malformed-frontmatter.md"
cat > "$MALFORMED_FRONTMATTER" <<'EOF'
---
title: Never closed
product: alpha
sprint:
EOF
expect_result "rejects malformed task frontmatter" 1 '"code":"frontmatter_unterminated"' \
  validate "$FIXTURE" "$MALFORMED_FRONTMATTER"

expect_result "missing provider input produces UNKNOWN, never PASS" 2 '"outcome":"UNKNOWN"' \
  python3 "$CHECKER" validate \
    --task "$VALID_BLANK" \
    --marketplace "$FIXTURE/missing-marketplace.json" \
    --roadmap "$FIXTURE/docs/dev/ROADMAP.md"

INCOMPLETE="$TMP_DIR/incomplete"
write_providers "$INCOMPLETE"
mkdir -p "$INCOMPLETE/state"
write_task "$INCOMPLETE/state/no-product.md" "source: fixture" "sprint:"
seal_state "$INCOMPLETE"
expect_result "audit reports incomplete live product coverage" 1 '"product_filter_authoritative":false' \
  audit "$INCOMPLETE"

COMPLETE="$TMP_DIR/complete"
write_providers "$COMPLETE"
mkdir -p "$COMPLETE/state"
write_task "$COMPLETE/state/valid.md" "product: alpha" "sprint:"
seal_state "$COMPLETE"
expect_result "audit makes product filtering authoritative only after complete coverage" 0 \
  '"product_filter_authoritative":true' audit "$COMPLETE"
expect_result "audit does not infer iteration completeness from a blank sprint" 0 \
  '"iteration_filter_authoritative":false' audit "$COMPLETE"
expect_result "declared iteration migration becomes authoritative only on a valid population" 0 \
  '"iteration_filter_authoritative":true' audit "$COMPLETE" --iteration-migration-complete
expect_iteration_declaration_binding \
  "iteration completeness declaration is part of the exact input revision" "$COMPLETE"

ARCHIVE="$TMP_DIR/archive"
write_providers "$ARCHIVE"
mkdir -p "$ARCHIVE/state/_archive"
write_task "$ARCHIVE/state/valid.md" "product: alpha" "sprint:"
write_task "$ARCHIVE/state/_archive/legacy.md" "source: legacy" "sprint:"
seal_state "$ARCHIVE"
expect_result "audit excludes archived entities from completeness" 0 '"live_items":1' \
  audit "$ARCHIVE"

INVALID_DECLARATION="$TMP_DIR/invalid-declaration"
write_providers "$INVALID_DECLARATION"
mkdir -p "$INVALID_DECLARATION/state"
write_task "$INVALID_DECLARATION/state/bad-pair.md" "product: beta" "sprint: S1"
seal_state "$INVALID_DECLARATION"
expect_result "iteration declaration cannot override invalid live fields" 1 \
  '"iteration_filter_authoritative":false' audit "$INVALID_DECLARATION" --iteration-migration-complete

DUPLICATE_AUDIT="$TMP_DIR/duplicate-audit"
write_providers "$DUPLICATE_AUDIT"
mkdir -p "$DUPLICATE_AUDIT/state"
cat > "$DUPLICATE_AUDIT/state/duplicate.md" <<'EOF'
---
title: Duplicate
status: backlog
product: alpha
product: beta
sprint:
---
EOF
seal_state "$DUPLICATE_AUDIT"
expect_result "duplicate product cannot leave product filtering authoritative" 1 \
  '"product_filter_authoritative":false' audit "$DUPLICATE_AUDIT"

EMPTY_STATE="$TMP_DIR/empty-state"
write_providers "$EMPTY_STATE"
mkdir -p "$EMPTY_STATE/state"
seal_state "$EMPTY_STATE"
expect_result "an empty state root is UNKNOWN unless separately proven intentional" 2 \
  '"outcome":"UNKNOWN"' audit "$EMPTY_STATE"

WRONG_STATE="$TMP_DIR/wrong-state"
write_providers "$WRONG_STATE"
mkdir -p "$WRONG_STATE/state"
write_task "$WRONG_STATE/state/looks-valid.md" "product: alpha" "sprint:"
expect_result "a nonempty directory that is not the state worktree is UNKNOWN" 2 \
  '"outcome":"UNKNOWN"' audit "$WRONG_STATE"

DIRTY_STATE="$TMP_DIR/dirty-state"
write_providers "$DIRTY_STATE"
mkdir -p "$DIRTY_STATE/state"
write_task "$DIRTY_STATE/state/valid.md" "product: alpha" "sprint:"
seal_state "$DIRTY_STATE"
printf '\ndirty\n' >> "$DIRTY_STATE/state/valid.md"
expect_result "a dirty state worktree is UNKNOWN" 2 '"outcome":"UNKNOWN"' \
  audit "$DIRTY_STATE"

UNRELATED_STATE="$TMP_DIR/unrelated-state"
write_providers "$UNRELATED_STATE"
mkdir -p "$UNRELATED_STATE/state"
write_task "$UNRELATED_STATE/state/valid.md" "product: alpha" "sprint:"
git -C "$UNRELATED_STATE/state" init -q
git -C "$UNRELATED_STATE/state" checkout -q -b spacedock-state/dev
git -C "$UNRELATED_STATE/state" config user.name "Dev Flow Fixture"
git -C "$UNRELATED_STATE/state" config user.email "dev-flow-fixture@example.invalid"
git -C "$UNRELATED_STATE/state" add -A
git -C "$UNRELATED_STATE/state" commit -qm "state: unrelated fixture"
expect_result "an unrelated Git repo with the expected branch is UNKNOWN" 2 \
  '"outcome":"UNKNOWN"' audit "$UNRELATED_STATE"

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[[ "$FAIL" -eq 0 ]]
