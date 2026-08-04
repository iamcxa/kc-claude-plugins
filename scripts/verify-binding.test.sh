#!/usr/bin/env bash
# Fail-closed contract for kc-dev-flow/scripts/verify-binding.py.
# Each case asserts one closed outcome and its exit code; a verifier that cannot
# report every outcome is not a verifier, so all four are exercised.
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
VERIFY="$ROOT/kc-dev-flow/scripts/verify-binding.py"
PKG="$ROOT/kc-dev-flow"
TEST_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/verify-binding.XXXXXX")
trap 'rm -rf "$TEST_ROOT"' EXIT

fail() { printf 'verify-binding-contract:FAIL:%s\n' "$*" >&2; exit 1; }

# Args: 1=case 2=expected outcome 3=expected exit 4=readme body
expect() {
  local name=$1 want=$2 want_rc=$3 body=$4 out rc readme
  readme="$TEST_ROOT/$name.md"
  printf '%s\n' "$body" >"$readme"
  set +e
  out=$(python3 "$VERIFY" "$readme" --package "$PKG" 2>&1)
  rc=$?
  set -e
  grep -q "verify-binding:$want:" <<<"$out" ||
    fail "$name expected $want, got: $(head -1 <<<"$out")"
  [[ "$rc" == "$want_rc" ]] || fail "$name expected exit $want_rc, got $rc"
}

KERNEL_REL="references/kernel.md"
DIGEST=$(python3 -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$PKG/$KERNEL_REL")
VERSION=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['version'])" "$PKG/.claude-plugin/plugin.json")

binding() { # 1=version 2=digest 3=entrypoint
  printf '# Adopter\n\n```yaml\nkernel_source: iamcxa/kc-claude-plugins/kc-dev-flow\nkernel_version: %s\nkernel_digest: %s\nkernel_entrypoint: %s\n```\n' "$1" "$2" "$3"
}

expect pass             PASS             0 "$(binding "$VERSION" "$DIGEST" "$KERNEL_REL")"
expect stale            STALE_COMPATIBLE 1 "$(binding "0.0.1" "$DIGEST" "$KERNEL_REL")"
expect drifted          REBIND_REQUIRED  1 "$(binding "$VERSION" "$(printf 'a%.0s' {1..64})" "$KERNEL_REL")"
expect no_binding       UNRESOLVABLE     1 "# Adopter with no binding at all"
expect partial_binding  UNRESOLVABLE     1 "$(printf '```yaml\nkernel_source: x\nkernel_version: 1.0.0\n```\n')"
expect missing_entry    UNRESOLVABLE     1 "$(binding "$VERSION" "$DIGEST" "references/does-not-exist.md")"
expect traversal        UNRESOLVABLE     1 "$(binding "$VERSION" "$DIGEST" "../../README.md")"

# A digest that matches must not be reachable by pointing at a different file.
OTHER_REL="references/work-control-profile.md"
expect wrong_file       REBIND_REQUIRED  1 "$(binding "$VERSION" "$DIGEST" "$OTHER_REL")"

printf 'verify-binding-contract:PASS:all-outcomes\n'
