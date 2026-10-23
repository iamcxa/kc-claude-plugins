#!/usr/bin/env bash

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

PASS=0
FAIL=0

pass() { printf 'ok - %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf 'not ok - %s\n' "$1"; FAIL=$((FAIL + 1)); }

# A scratch tree holding only the script and the three kc-adr sources, synced.
fresh_tree() {
  rm -rf "$TMP_DIR/t"
  mkdir -p "$TMP_DIR/t/scripts" "$TMP_DIR/t/kc-adr/references" "$TMP_DIR/t/kc-adr/scripts" \
    "$TMP_DIR/t/kc-dev-flow-2/references" "$TMP_DIR/t/kc-dev-flow-2/scripts" "$TMP_DIR/t/kc-dev-flow-2/skills"
  cp "$HERE/kc-adr-copy-sync.sh" "$TMP_DIR/t/scripts/"
  cp "$REPO_ROOT/kc-adr/references/adr-template.md" "$TMP_DIR/t/kc-adr/references/"
  cp "$REPO_ROOT/kc-adr/scripts/adr_lint.py" "$TMP_DIR/t/kc-adr/scripts/"
  cp -R "$REPO_ROOT/kc-adr/skills" "$TMP_DIR/t/kc-adr/skills"
  "$TMP_DIR/t/scripts/kc-adr-copy-sync.sh" sync >/dev/null 2>&1
}

# expect_check LABEL EXPECTED_RC NEEDLE: run check on the scratch tree.
expect_check() {
  local label="$1" want="$2" needle="$3" output rc
  output="$("$TMP_DIR/t/scripts/kc-adr-copy-sync.sh" check 2>&1)"
  rc=$?
  if [[ "$rc" -eq "$want" ]] && { [[ -z "$needle" ]] || grep -qF -- "$needle" <<<"$output"; }; then
    pass "$label"
  else
    printf '  want rc=%s containing %q, got rc=%s: %s\n' "$want" "$needle" "$rc" "$output"
    fail "$label"
  fi
}

fresh_tree
expect_check "synced tree passes" 0 ""

fresh_tree; echo x >> "$TMP_DIR/t/kc-dev-flow-2/scripts/adr_lint.py"
expect_check "changed copy file fails naming kc-adr/scripts/adr_lint.py" 1 "Edit kc-adr/scripts/adr_lint.py (kc-adr is the source)"

fresh_tree; echo x >> "$TMP_DIR/t/kc-dev-flow-2/references/adr-template.md"
expect_check "changed copied template fails naming its source" 1 "Edit kc-adr/references/adr-template.md (kc-adr is the source)"

fresh_tree; echo x > "$TMP_DIR/t/kc-dev-flow-2/skills/read-adr/extra.md"
expect_check "extra file in the copied folder fails naming kc-adr/skills/read-adr" 1 "Edit kc-adr/skills/read-adr (kc-adr is the source)"

fresh_tree; rm "$TMP_DIR/t/kc-dev-flow-2/skills/read-adr/writing.md"
expect_check "deleted file in the copied folder fails" 1 "Edit kc-adr/skills/read-adr (kc-adr is the source)"

fresh_tree; rm -rf "$TMP_DIR/t/kc-dev-flow-2/skills/read-adr"
expect_check "deleted copied folder fails" 1 "Edit kc-adr/skills/read-adr (kc-adr is the source)"

fresh_tree; echo x >> "$TMP_DIR/t/kc-adr/skills/read-adr/SKILL.md"
expect_check "changed source file alone fails" 1 "kc-dev-flow-2/skills/read-adr differs from kc-adr/skills/read-adr"

fresh_tree; rm -rf "$TMP_DIR/t/kc-adr/skills/read-adr"
expect_check "deleted source folder fails" 1 "Edit kc-adr/skills/read-adr (kc-adr is the source)"

fresh_tree; echo x >> "$TMP_DIR/t/kc-adr/scripts/adr_lint.py"
"$TMP_DIR/t/scripts/kc-adr-copy-sync.sh" sync >/dev/null 2>&1
expect_check "sync after a source change passes" 0 ""

fresh_tree; echo x >> "$TMP_DIR/t/kc-adr/skills/read-adr/SKILL.md"; rm "$TMP_DIR/t/kc-adr/skills/read-adr/prefix.md"
"$TMP_DIR/t/scripts/kc-adr-copy-sync.sh" sync >/dev/null 2>&1
if [[ ! -e "$TMP_DIR/t/kc-dev-flow-2/skills/read-adr/prefix.md" ]]; then
  pass "sync drops a file deleted from the source folder"
else
  fail "sync drops a file deleted from the source folder"
fi

for mode in "" bogus; do
  "$HERE/kc-adr-copy-sync.sh" $mode >/dev/null 2>&1
  rc=$?
  if [[ "$rc" -eq 2 ]]; then pass "mode '${mode:-<none>}' exits 2"; else printf '  got rc=%s\n' "$rc"; fail "mode '${mode:-<none>}' exits 2"; fi
done

printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"
[[ "$FAIL" -eq 0 ]]
