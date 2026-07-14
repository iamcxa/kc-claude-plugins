#!/usr/bin/env bash

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
PARITY="$HERE/version-parity-check.sh"
CONFIG_CHECK="$HERE/release-please-config-check.sh"
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
    printf '  expected non-zero output containing: %s\n' "$needle"
    fail "$label"
  fi
}

write_valid_fixture() {
  local root="$1"
  mkdir -p "$root/alpha/.claude-plugin" "$root/.claude-plugin"
  cat > "$root/alpha/.claude-plugin/plugin.json" <<'EOF'
{"name":"alpha","version":"1.0.0"}
EOF
  cat > "$root/.claude-plugin/marketplace.json" <<'EOF'
{"plugins":[{"name":"alpha","version":"1.0.0"}]}
EOF
  cat > "$root/.release-please-manifest.json" <<'EOF'
{"alpha":"1.0.0"}
EOF
  cat > "$root/release-please-config.json" <<'EOF'
{
  "packages": {
    "alpha": {
      "release-type": "simple",
      "extra-files": [
        {"type":"json","path":".claude-plugin/plugin.json","jsonpath":"$.version"},
        {"type":"json","path":"/.claude-plugin/marketplace.json","jsonpath":"$.plugins[?(@.name==\"alpha\")].version"}
      ]
    }
  }
}
EOF
}

VALID="$TMP_DIR/valid"
write_valid_fixture "$VALID"

if [[ -x "$CONFIG_CHECK" ]]; then
  pass "release-please config checker exists"
else
  fail "release-please config checker exists"
fi

expect_success "accepts package-relative and repo-root extra-file paths" \
  env REPO_DIR_OVERRIDE="$VALID" bash "$CONFIG_CHECK"

expect_success "repository release-please config resolves every extra file" \
  env REPO_DIR_OVERRIDE="$(cd "$HERE/.." && pwd)" bash "$CONFIG_CHECK"

DOUBLED="$TMP_DIR/doubled"
cp -R "$VALID" "$DOUBLED"
python3 - "$DOUBLED/release-please-config.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
data["packages"]["alpha"]["extra-files"][0]["path"] = "alpha/.claude-plugin/plugin.json"
json.dump(data, open(path, "w"))
PY
expect_failure_contains "rejects a package path duplicated inside extra-files" "resolved path does not exist" \
  env REPO_DIR_OVERRIDE="$DOUBLED" bash "$CONFIG_CHECK"

NESTED_ROOT="$TMP_DIR/nested-root"
cp -R "$VALID" "$NESTED_ROOT"
python3 - "$NESTED_ROOT/release-please-config.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
data["packages"]["alpha"]["extra-files"][1]["path"] = ".claude-plugin/marketplace.json"
json.dump(data, open(path, "w"))
PY
expect_failure_contains "rejects a repo-root file without a leading slash" "resolved path does not exist" \
  env REPO_DIR_OVERRIDE="$NESTED_ROOT" bash "$CONFIG_CHECK"

BAD_JSONPATH="$TMP_DIR/bad-jsonpath"
cp -R "$VALID" "$BAD_JSONPATH"
python3 - "$BAD_JSONPATH/release-please-config.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
data["packages"]["alpha"]["extra-files"][1]["jsonpath"] = "$.plugins[?(@.name==\"missing\")].version"
json.dump(data, open(path, "w"))
PY
expect_failure_contains "rejects a JSONPath that matches no marketplace entry" "matches 0 fields" \
  env REPO_DIR_OVERRIDE="$BAD_JSONPATH" bash "$CONFIG_CHECK"

MANIFEST_DRIFT="$TMP_DIR/manifest-drift"
cp -R "$VALID" "$MANIFEST_DRIFT"
cat > "$MANIFEST_DRIFT/.release-please-manifest.json" <<'EOF'
{"alpha":"1.1.0"}
EOF
expect_failure_contains "parity checker rejects release manifest drift" "release-manifest=1.1.0" \
  env REPO_DIR_OVERRIDE="$MANIFEST_DRIFT" bash "$PARITY"

if grep -qF 'release-please-config-check.sh' "$PARITY"; then
  pass "parity gate invokes the release-please config checker"
else
  fail "parity gate invokes the release-please config checker"
fi

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[[ "$FAIL" -eq 0 ]]
