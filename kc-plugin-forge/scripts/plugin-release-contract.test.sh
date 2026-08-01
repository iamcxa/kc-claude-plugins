#!/usr/bin/env bash

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$HERE/.." && pwd)"
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
    printf '  actual output: %s\n' "$output"
    fail "$label"
  fi
}

INSTALLED="$TMP_DIR/installed/kc-plugin-forge"
mkdir -p "$(dirname "$INSTALLED")"
cp -R "$PLUGIN_ROOT" "$INSTALLED"

CHECK="$INSTALLED/scripts/plugin-release-contract-check.sh"
SYNC="$INSTALLED/scripts/post-release-sync.sh"
WATCH="$INSTALLED/scripts/watch-pr-checks.sh"

expect_success "clean installed plugin contains a complete release helper contract" \
  bash "$CHECK"

MISSING="$TMP_DIR/missing/kc-plugin-forge"
mkdir -p "$(dirname "$MISSING")"
cp -R "$PLUGIN_ROOT" "$MISSING"
rm -f "$MISSING/scripts/post-release-sync.sh"
expect_failure_contains "clean-install contract rejects a missing packaged helper" \
  "missing scripts/post-release-sync.sh" \
  bash "$MISSING/scripts/plugin-release-contract-check.sh"

LEGACY="$TMP_DIR/legacy/kc-plugin-forge"
mkdir -p "$(dirname "$LEGACY")"
cp -R "$PLUGIN_ROOT" "$LEGACY"
printf '\nLegacy path: ~/.Codex/kc-Codex\n' >> "$LEGACY/skills/kc-plugin-release/SKILL.md"
expect_failure_contains "contract rejects legacy host paths in maintained instructions" \
  "obsolete helper or path" \
  bash "$LEGACY/scripts/plugin-release-contract-check.sh"

SOURCE="$TMP_DIR/source"
mkdir -p "$SOURCE/.claude-plugin" "$SOURCE/alpha/.claude-plugin"
printf '{"plugins":[{"name":"alpha","source":"./alpha","version":"1.2.3"}]}\n' \
  > "$SOURCE/.claude-plugin/marketplace.json"
printf '{"name":"alpha","version":"1.2.3"}\n' \
  > "$SOURCE/alpha/.claude-plugin/plugin.json"
printf 'portable payload\n' > "$SOURCE/alpha/payload.txt"
git -C "$SOURCE" init -q -b main
git -C "$SOURCE" config user.name test
git -C "$SOURCE" config user.email test@example.com
git -C "$SOURCE" add .claude-plugin/marketplace.json alpha
git -C "$SOURCE" commit -qm 'fixture'

FIXTURE_HOME="$TMP_DIR/home"
mkdir -p "$FIXTURE_HOME"
SOURCE_STATUS_BEFORE="$(git -C "$SOURCE" status --porcelain=v1)"
SOURCE_TAGS_BEFORE="$(git -C "$SOURCE" tag)"

if HOME="$FIXTURE_HOME" bash "$SYNC" alpha --repo "$SOURCE" >/dev/null 2>&1 &&
   diff -qr "$SOURCE/alpha" "$FIXTURE_HOME/.claude/plugins/local/alpha" >/dev/null &&
   diff -qr "$SOURCE/alpha" "$FIXTURE_HOME/.codex/local-plugins/alpha" >/dev/null; then
  pass "post-release sync copies the released plugin to Claude and Codex local installs"
else
  fail "post-release sync copies the released plugin to Claude and Codex local installs"
fi

if [[ "$(git -C "$SOURCE" status --porcelain=v1)" == "$SOURCE_STATUS_BEFORE" ]] &&
   [[ "$(git -C "$SOURCE" tag)" == "$SOURCE_TAGS_BEFORE" ]]; then
  pass "post-release sync does not mutate source metadata or tags"
else
  fail "post-release sync does not mutate source metadata or tags"
fi

printf 'dirty\n' > "$SOURCE/alpha/unreleased.txt"
expect_failure_contains "post-release sync refuses an unreleased dirty source" \
  "source workspace must be clean" \
  env HOME="$FIXTURE_HOME" bash "$SYNC" alpha --repo "$SOURCE"
rm -f "$SOURCE/alpha/unreleased.txt"

SYMLINK_HOME="$TMP_DIR/symlink-home"
mkdir -p "$SYMLINK_HOME/.claude/plugins/local" "$SYMLINK_HOME/existing-alpha"
ln -s "$SYMLINK_HOME/existing-alpha" "$SYMLINK_HOME/.claude/plugins/local/alpha"
expect_failure_contains "post-release sync refuses to replace a live install symlink" \
  "refusing to replace symlink" \
  env HOME="$SYMLINK_HOME" bash "$SYNC" alpha --repo "$SOURCE"

PARTIAL_HOME="$TMP_DIR/partial-home"
mkdir -p "$PARTIAL_HOME/.claude/plugins/local/alpha" \
  "$PARTIAL_HOME/.codex/local-plugins" "$PARTIAL_HOME/existing-codex-alpha"
printf 'keep\n' > "$PARTIAL_HOME/.claude/plugins/local/alpha/existing.txt"
ln -s "$PARTIAL_HOME/existing-codex-alpha" \
  "$PARTIAL_HOME/.codex/local-plugins/alpha"
HOME="$PARTIAL_HOME" bash "$SYNC" alpha --repo "$SOURCE" >/dev/null 2>&1
PARTIAL_RC=$?
if [[ "$PARTIAL_RC" -ne 0 ]] &&
   [[ -f "$PARTIAL_HOME/.claude/plugins/local/alpha/existing.txt" ]] &&
   [[ ! -f "$PARTIAL_HOME/.claude/plugins/local/alpha/payload.txt" ]]; then
  pass "post-release sync preflights both destinations before copying either"
else
  fail "post-release sync preflights both destinations before copying either"
fi

FAKE_BIN="$TMP_DIR/bin"
mkdir -p "$FAKE_BIN"
cat > "$FAKE_BIN/gh" <<'EOF'
#!/usr/bin/env bash
set -u
if [[ "${1:-} ${2:-}" == "pr view" ]]; then
  count_file="${FAKE_GH_COUNT_FILE:?}"
  count=0
  [[ -f "$count_file" ]] && count="$(cat "$count_file")"
  count=$((count + 1))
  printf '%s\n' "$count" > "$count_file"
  if [[ "$count" -eq 1 ]]; then
    printf '%s\n' "${FAKE_GH_HEAD_BEFORE:-head-a}"
  else
    printf '%s\n' "${FAKE_GH_HEAD_AFTER:-head-a}"
  fi
  exit 0
fi
if [[ "${1:-} ${2:-}" == "pr checks" ]]; then
  [[ " $* " == *" --watch "* && " $* " == *" --fail-fast "* ]] || exit 96
  exit "${FAKE_GH_CHECKS_RC:-0}"
fi
exit 97
EOF
chmod +x "$FAKE_BIN/gh"

COUNT_FILE="$TMP_DIR/gh-count"
expect_success "CI watcher accepts successful checks on the exact PR head" \
  env PATH="$FAKE_BIN:$PATH" FAKE_GH_COUNT_FILE="$COUNT_FILE" \
  bash "$WATCH" 42 --repo example/repo

rm -f "$COUNT_FILE"
expect_failure_contains "CI watcher propagates a failed check gate" \
  "checks failed" \
  env PATH="$FAKE_BIN:$PATH" FAKE_GH_COUNT_FILE="$COUNT_FILE" FAKE_GH_CHECKS_RC=1 \
  bash "$WATCH" 42 --repo example/repo

rm -f "$COUNT_FILE"
expect_failure_contains "CI watcher rejects evidence after the PR head moves" \
  "PR head moved" \
  env PATH="$FAKE_BIN:$PATH" FAKE_GH_COUNT_FILE="$COUNT_FILE" \
    FAKE_GH_HEAD_BEFORE=head-a FAKE_GH_HEAD_AFTER=head-b \
  bash "$WATCH" 42 --repo example/repo

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[[ "$FAIL" -eq 0 ]]
