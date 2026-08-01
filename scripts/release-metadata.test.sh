#!/usr/bin/env bash

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
PARITY="$HERE/version-parity-check.sh"
CONFIG_CHECK="$HERE/release-please-config-check.sh"
REPO_ROOT="$(cd "$HERE/.." && pwd)"
RELEASE_ACTION_SHA="5c625bfb5d1ff62eadeeb3772007f7f66fdcf071"
RELEASE_PLEASE_VERSION="17.3.0"
RELEASE_RUNTIME_FIXTURE="$HERE/fixtures/release-please-runtime"
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

expect_success_contains() {
  local label="$1" needle="$2" output rc
  shift 2
  output="$("$@" 2>&1)"
  rc=$?
  if [[ "$rc" -eq 0 ]] && grep -qF -- "$needle" <<<"$output"; then
    pass "$label"
  else
    printf '  expected zero output containing: %s\n' "$needle"
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
  "initial-version": "0.1.0",
  "include-component-in-tag": true,
  "include-v-in-tag": true,
  "tag-separator": "-",
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
  git -C "$root" init -q
  git -C "$root" add release-please-config.json .release-please-manifest.json \
    .claude-plugin/marketplace.json alpha/.claude-plugin/plugin.json
}

probe_release_please_first_tag() {
  local fixture_root="$1" probe_dir="$TMP_DIR/release-please-probe"
  mkdir -p "$probe_dir"
  cp "$RELEASE_RUNTIME_FIXTURE/package.json" \
    "$RELEASE_RUNTIME_FIXTURE/package-lock.json" "$probe_dir/"
  (
    cd "$probe_dir" || exit 1
    npm ci --silent --ignore-scripts --no-audit --no-fund >/dev/null 2>&1
  ) || return 1

  (
    cd "$probe_dir" || exit 1
    node - "$fixture_root/release-please-config.json" \
      "$fixture_root/.release-please-manifest.json" <<'NODE'
const fs = require('fs');

// Load the public entrypoint first; release-please 17.3.0's CommonJS strategy
// modules otherwise form a circular load under newer Node runtimes.
const releasePlease = require('release-please');
const {Simple} = require('release-please/build/src/strategies/simple.js');
const {TagName} = require('release-please/build/src/util/tag-name.js');

const config = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const manifest = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const [path, packageConfig] = Object.entries(config.packages)[0];
if (manifest[path] !== '0.0.0') {
  console.error(`bootstrap fixture must seed ${path} at 0.0.0; got ${manifest[path]}`);
  process.exit(1);
}
const component = packageConfig.component || path;
const includeComponent = packageConfig['include-component-in-tag']
  ?? config['include-component-in-tag'];
const tagSeparator = packageConfig['tag-separator'] ?? config['tag-separator'];
const includeV = packageConfig['include-v-in-tag'] ?? config['include-v-in-tag'];
const initialVersion = packageConfig['initial-version'] ?? config['initial-version'];

const strategy = new Simple({
  github: {repository: {}},
  targetBranch: 'main',
  path,
  component,
  initialVersion,
  includeComponentInTag: includeComponent,
  tagSeparator,
});
const featureCommit = {type: 'feat', notes: [], breaking: false};

strategy.buildNewVersion([featureCommit], undefined).then(version => {
  const tag = new TagName(
    version,
    includeComponent ? component : undefined,
    tagSeparator,
    includeV,
  ).toString();
  console.log(`release-please ${releasePlease.VERSION}: ${tag}`);
  if (tag !== 'alpha-v0.1.0') process.exit(1);
}).catch(error => {
  console.error(error);
  process.exit(1);
});
NODE
  )
}

VALID="$TMP_DIR/valid"
write_valid_fixture "$VALID"

BOOTSTRAP="$TMP_DIR/bootstrap"
cp -R "$VALID" "$BOOTSTRAP"
python3 - "$BOOTSTRAP/.release-please-manifest.json" \
  "$BOOTSTRAP/alpha/.claude-plugin/plugin.json" \
  "$BOOTSTRAP/.claude-plugin/marketplace.json" <<'PY'
import json, sys
manifest_path, plugin_path, marketplace_path = sys.argv[1:]

json.dump({"alpha": "0.0.0"}, open(manifest_path, "w"))

plugin = json.load(open(plugin_path))
plugin["version"] = "0.0.0"
json.dump(plugin, open(plugin_path, "w"))

marketplace = json.load(open(marketplace_path))
marketplace["plugins"][0]["version"] = "0.0.0"
json.dump(marketplace, open(marketplace_path, "w"))
PY
git -C "$BOOTSTRAP" add .release-please-manifest.json \
  alpha/.claude-plugin/plugin.json .claude-plugin/marketplace.json

if [[ -x "$CONFIG_CHECK" ]]; then
  pass "release-please config checker exists"
else
  fail "release-please config checker exists"
fi

expect_success "accepts package-relative and repo-root extra-file paths" \
  env REPO_DIR_OVERRIDE="$VALID" bash "$CONFIG_CHECK"

expect_success "repository release-please config resolves every extra file" \
  env REPO_DIR_OVERRIDE="$REPO_ROOT" bash "$CONFIG_CHECK"

expect_success_contains "new-component fixture resolves the declared first tag" \
  "First-release contract: alpha-v0.1.0" \
  env REPO_DIR_OVERRIDE="$BOOTSTRAP" bash "$CONFIG_CHECK"

expect_success "release-please probe has a committed dependency lock" \
  test -f "$RELEASE_RUNTIME_FIXTURE/package-lock.json"

expect_success_contains "release-please agrees on the first tag after a feature commit" \
  "release-please $RELEASE_PLEASE_VERSION: alpha-v0.1.0" \
  probe_release_please_first_tag "$BOOTSTRAP"

MISSING_INITIAL_VERSION="$TMP_DIR/missing-initial-version"
cp -R "$VALID" "$MISSING_INITIAL_VERSION"
python3 - "$MISSING_INITIAL_VERSION/release-please-config.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
data.pop("initial-version")
json.dump(data, open(path, "w"))
PY
expect_failure_contains "rejects an implicit first-release version" \
  "top-level initial-version must be '0.1.0'" \
  env REPO_DIR_OVERRIDE="$MISSING_INITIAL_VERSION" bash "$CONFIG_CHECK"

CHANGED_INITIAL_VERSION="$TMP_DIR/changed-initial-version"
cp -R "$VALID" "$CHANGED_INITIAL_VERSION"
python3 - "$CHANGED_INITIAL_VERSION/release-please-config.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
data["initial-version"] = "1.0.0"
json.dump(data, open(path, "w"))
PY
expect_failure_contains "rejects drift from the declared first-release version" \
  "top-level initial-version must be '0.1.0'" \
  env REPO_DIR_OVERRIDE="$CHANGED_INITIAL_VERSION" bash "$CONFIG_CHECK"

PACKAGE_OVERRIDE="$TMP_DIR/package-initial-version-override"
cp -R "$VALID" "$PACKAGE_OVERRIDE"
python3 - "$PACKAGE_OVERRIDE/release-please-config.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
data["packages"]["alpha"]["initial-version"] = "1.0.0"
json.dump(data, open(path, "w"))
PY
expect_failure_contains "rejects a package override of the shared first-release policy" \
  "must inherit top-level initial-version '0.1.0'" \
  env REPO_DIR_OVERRIDE="$PACKAGE_OVERRIDE" bash "$CONFIG_CHECK"

MISSING_INCLUDE_V="$TMP_DIR/missing-include-v"
cp -R "$VALID" "$MISSING_INCLUDE_V"
python3 - "$MISSING_INCLUDE_V/release-please-config.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
data.pop("include-v-in-tag")
json.dump(data, open(path, "w"))
PY
expect_failure_contains "rejects an implicit v-prefix policy" \
  "include-v-in-tag must be true for first-release tags" \
  env REPO_DIR_OVERRIDE="$MISSING_INCLUDE_V" bash "$CONFIG_CHECK"

PACKAGE_TAG_OVERRIDE="$TMP_DIR/package-tag-override"
cp -R "$VALID" "$PACKAGE_TAG_OVERRIDE"
python3 - "$PACKAGE_TAG_OVERRIDE/release-please-config.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
data["packages"]["alpha"]["include-v-in-tag"] = False
json.dump(data, open(path, "w"))
PY
expect_failure_contains "rejects a package override of the shared tag policy" \
  "must inherit top-level tag policy" \
  env REPO_DIR_OVERRIDE="$PACKAGE_TAG_OVERRIDE" bash "$CONFIG_CHECK"

expect_success "release workflow pins the tested release-please action" \
  grep -qF "googleapis/release-please-action@$RELEASE_ACTION_SHA" \
    "$REPO_ROOT/.github/workflows/release-please.yml"

expect_success "adopter guidance requires an actually published tag" \
  grep -qF "pin only an actually published tag" "$REPO_ROOT/CLAUDE.md"

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

ILLEGAL_PATH="$TMP_DIR/illegal-path"
cp -R "$VALID" "$ILLEGAL_PATH"
python3 - "$ILLEGAL_PATH/release-please-config.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
data["packages"]["alpha"]["extra-files"][0]["path"] = "nested/../.claude-plugin/plugin.json"
json.dump(data, open(path, "w"))
PY
expect_failure_contains "rejects path segments that release-please treats as illegal" "illegal path segment" \
  env REPO_DIR_OVERRIDE="$ILLEGAL_PATH" bash "$CONFIG_CHECK"

DOT_PATH="$TMP_DIR/dot-path"
cp -R "$VALID" "$DOT_PATH"
python3 - "$DOT_PATH/release-please-config.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
data["packages"]["alpha"]["extra-files"][0]["path"] = "./.claude-plugin/plugin.json"
json.dump(data, open(path, "w"))
PY
expect_failure_contains "rejects current-directory path segments" "illegal path segment" \
  env REPO_DIR_OVERRIDE="$DOT_PATH" bash "$CONFIG_CHECK"

TILDE_PATH="$TMP_DIR/tilde-path"
cp -R "$VALID" "$TILDE_PATH"
mkdir -p "$TILDE_PATH/alpha/~cache"
cat > "$TILDE_PATH/alpha/~cache/version.json" <<'EOF'
{"version":"1.0.0"}
EOF
python3 - "$TILDE_PATH/release-please-config.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
data["packages"]["alpha"]["extra-files"].append(
    {"type": "json", "path": "~cache/version.json", "jsonpath": "$.version"}
)
json.dump(data, open(path, "w"))
PY
expect_success "accepts package-relative tilde paths allowed by release-please" \
  env REPO_DIR_OVERRIDE="$TILDE_PATH" bash "$CONFIG_CHECK"

ROOT_TILDE="$TMP_DIR/root-tilde"
cp -R "$VALID" "$ROOT_TILDE"
rm -rf "$ROOT_TILDE/alpha"
mkdir -p "$ROOT_TILDE/~"
cat > "$ROOT_TILDE/.claude-plugin/plugin.json" <<'EOF'
{"name":".","version":"1.0.0"}
EOF
cat > "$ROOT_TILDE/~/version.json" <<'EOF'
{"version":"1.0.0"}
EOF
python3 - "$ROOT_TILDE/release-please-config.json" "$ROOT_TILDE/.claude-plugin/marketplace.json" <<'PY'
import json, sys
config_path, marketplace_path = sys.argv[1:]
config = {
    "packages": {
        ".": {
            "release-type": "simple",
            "extra-files": [
                {"type": "json", "path": ".claude-plugin/plugin.json", "jsonpath": "$.version"},
                {"type": "json", "path": "/.claude-plugin/marketplace.json", "jsonpath": "$.plugins[?(@.name==\".\")].version"},
                {"type": "json", "path": "~/version.json", "jsonpath": "$.version"},
            ],
        }
    }
}
json.dump(config, open(config_path, "w"))
json.dump({"plugins": [{"name": ".", "version": "1.0.0"}]}, open(marketplace_path, "w"))
PY
expect_failure_contains "rejects root-package tilde paths rejected by release-please" "illegal path segment" \
  env REPO_DIR_OVERRIDE="$ROOT_TILDE" bash "$CONFIG_CHECK"

UNKNOWN_TYPE="$TMP_DIR/unknown-type"
cp -R "$VALID" "$UNKNOWN_TYPE"
python3 - "$UNKNOWN_TYPE/release-please-config.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
data["packages"]["alpha"]["extra-files"][0]["type"] = "jsoon"
json.dump(data, open(path, "w"))
PY
expect_failure_contains "rejects unsupported extra-file types" "unsupported extra-file type" \
  env REPO_DIR_OVERRIDE="$UNKNOWN_TYPE" bash "$CONFIG_CHECK"

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

MISSING_CLAUDE="$TMP_DIR/missing-claude"
cp -R "$VALID" "$MISSING_CLAUDE"
python3 - "$MISSING_CLAUDE/release-please-config.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
data["packages"]["alpha"]["extra-files"].pop(0)
json.dump(data, open(path, "w"))
PY
expect_failure_contains "requires every package's Claude manifest target" "missing required Claude manifest target" \
  env REPO_DIR_OVERRIDE="$MISSING_CLAUDE" bash "$CONFIG_CHECK"

MISSING_MARKETPLACE="$TMP_DIR/missing-marketplace"
cp -R "$VALID" "$MISSING_MARKETPLACE"
python3 - "$MISSING_MARKETPLACE/release-please-config.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
data["packages"]["alpha"]["extra-files"].pop(1)
json.dump(data, open(path, "w"))
PY
expect_failure_contains "requires every package's marketplace target" "missing required marketplace target" \
  env REPO_DIR_OVERRIDE="$MISSING_MARKETPLACE" bash "$CONFIG_CHECK"

MISSING_CODEX="$TMP_DIR/missing-codex"
cp -R "$VALID" "$MISSING_CODEX"
mkdir -p "$MISSING_CODEX/alpha/.codex-plugin"
cat > "$MISSING_CODEX/alpha/.codex-plugin/plugin.json" <<'EOF'
{"name":"alpha","version":"1.0.0"}
EOF
git -C "$MISSING_CODEX" add alpha/.codex-plugin/plugin.json
expect_failure_contains "requires a target for every tracked Codex manifest" "missing required Codex manifest target" \
  env REPO_DIR_OVERRIDE="$MISSING_CODEX" bash "$CONFIG_CHECK"

CROSSWIRED="$TMP_DIR/crosswired"
cp -R "$VALID" "$CROSSWIRED"
python3 - "$CROSSWIRED/release-please-config.json" "$CROSSWIRED/.claude-plugin/marketplace.json" <<'PY'
import json, sys
config_path, marketplace_path = sys.argv[1:]
config = json.load(open(config_path))
config["packages"]["alpha"]["extra-files"][1]["jsonpath"] = "$.plugins[?(@.name==\"beta\")].version"
json.dump(config, open(config_path, "w"))
marketplace = json.load(open(marketplace_path))
marketplace["plugins"].append({"name": "beta", "version": "1.0.0"})
json.dump(marketplace, open(marketplace_path, "w"))
PY
expect_failure_contains "rejects a marketplace selector wired to another plugin" "marketplace selector must target package 'alpha'" \
  env REPO_DIR_OVERRIDE="$CROSSWIRED" bash "$CONFIG_CHECK"

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

# --- Fail-closed plugin-directory enumeration --------------------------------
# The plugin set must come from BOTH marketplace.json AND a filesystem scan of
# */.claude-plugin/plugin.json — an on-disk directory with no marketplace
# entry (or vice versa) must fail loudly, never silently pass through unchecked.

UNLISTED_DIR="$TMP_DIR/unlisted-dir"
cp -R "$VALID" "$UNLISTED_DIR"
mkdir -p "$UNLISTED_DIR/beta/.claude-plugin"
cat > "$UNLISTED_DIR/beta/.claude-plugin/plugin.json" <<'EOF'
{"name":"beta","version":"1.0.0"}
EOF
git -C "$UNLISTED_DIR" add beta/.claude-plugin/plugin.json
expect_failure_contains "rejects an on-disk plugin directory with no marketplace.json entry" \
  "UNLISTED on-disk plugin director" \
  env REPO_DIR_OVERRIDE="$UNLISTED_DIR" bash "$PARITY"
expect_failure_contains "names the specific unlisted directory (beta)" "  - beta" \
  env REPO_DIR_OVERRIDE="$UNLISTED_DIR" bash "$PARITY"

ORPHANED_ENTRY="$TMP_DIR/orphaned-entry"
cp -R "$VALID" "$ORPHANED_ENTRY"
python3 - "$ORPHANED_ENTRY/.claude-plugin/marketplace.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
data["plugins"].append({"name": "gamma", "version": "1.0.0"})
json.dump(data, open(path, "w"))
PY
expect_failure_contains "rejects a marketplace.json entry with no matching on-disk plugin directory" \
  "ORPHANED marketplace.json entr" \
  env REPO_DIR_OVERRIDE="$ORPHANED_ENTRY" bash "$PARITY"
expect_failure_contains "names the specific orphaned entry (gamma), not a raw traceback" "  - gamma" \
  env REPO_DIR_OVERRIDE="$ORPHANED_ENTRY" bash "$PARITY"

expect_success "enumeration passes when on-disk directories and marketplace entries match 1:1" \
  env REPO_DIR_OVERRIDE="$VALID" bash "$PARITY"

printf '\n%s passed, %s failed\n' "$PASS" "$FAIL"
[[ "$FAIL" -eq 0 ]]
