#!/usr/bin/env bash
# Fail-closed contract for kc-dev-flow/scripts/verify-binding.py.
#
# Two of these cases are regressions, not hypotheticals: an earlier revision
# returned PASS for a README with no binding (fields matched across unrelated
# blocks) and PASS for a fabricated stale package (the caller supplied the
# package path). Both are pinned here as fixtures rather than described.
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
VERIFY="$ROOT/kc-dev-flow/scripts/verify-binding.py"
SRC="$ROOT/kc-dev-flow"
TEST_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/verify-binding.XXXXXX")
trap 'rm -rf "$TEST_ROOT"' EXIT

fail() { printf 'verify-binding-contract:FAIL:%s\n' "$*" >&2; exit 1; }
sha() { python3 -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$1"; }

# A cache root shaped like the real one: <marketplace>/<plugin>/<version>/...
CACHE="$TEST_ROOT/cache"
SOURCE="iamcxa/kc-claude-plugins/kc-dev-flow"
ENTRY="references/kernel.md"

release() { # 1=version 2=kernel-text
  local dir="$CACHE/kc-claude-plugins/kc-dev-flow/$1"
  mkdir -p "$dir/references" "$dir/.claude-plugin"
  printf '%s\n' "$2" >"$dir/$ENTRY"
  printf '{"version":"%s"}\n' "$1" >"$dir/.claude-plugin/plugin.json"
}
release 1.0.0 "kernel text as of one-oh-oh"
V100=$(sha "$CACHE/kc-claude-plugins/kc-dev-flow/1.0.0/$ENTRY")

binding() { # 1=version 2=digest [3=entrypoint] [4=source]
  printf '# Adopter\n\n```yaml\nkernel_source: %s\nkernel_version: %s\nkernel_entrypoint: %s\nkernel_digest: %s\n```\n' \
    "${4:-$SOURCE}" "$1" "${3:-$ENTRY}" "$2"
}

expect() { # 1=case 2=want 3=want_rc 4=body
  local name=$1 want=$2 want_rc=$3 body=$4 out rc readme
  readme="$TEST_ROOT/$name.md"; printf '%s\n' "$body" >"$readme"
  set +e; out=$(python3 "$VERIFY" "$readme" --cache-root "$CACHE" 2>&1); rc=$?; set -e
  grep -q "verify-binding:$want:" <<<"$out" || fail "$name expected $want, got: $(head -1 <<<"$out")"
  [[ "$rc" == "$want_rc" ]] || fail "$name expected exit $want_rc, got $rc"
}

expect pass PASS 0 "$(binding 1.0.0 "$V100")"

# REGRESSION D1: a README with no binding, whose fields appear in unrelated
# blocks — a quoted example, an appendix, a changelog. An earlier revision
# assembled these into a binding and returned PASS.
expect frankenstein UNRESOLVABLE 1 "$(printf '# No binding here\n\n## Someone else'"'"'s example\n\n```yaml\nkernel_source: %s\nkernel_version: 1.0.0\n```\n\n## Unrelated appendix\n\n```yaml\nkernel_entrypoint: %s\n```\n\n## Changelog\n\n```\nkernel_digest: %s\n```\n' "$SOURCE" "$ENTRY" "$V100")"

# Two real-looking bindings: choosing between them would be a guess.
expect ambiguous UNRESOLVABLE 1 "$(printf '%s\n%s\n' "$(binding 1.0.0 "$V100")" "$(binding 1.0.0 "$V100")")"

expect no_fence     UNRESOLVABLE 1 "kernel_source: $SOURCE and kernel_version: 1.0.0 in prose"
expect partial      UNRESOLVABLE 1 "$(printf '```yaml\nkernel_source: %s\nkernel_version: 1.0.0\n```\n' "$SOURCE")"
expect bad_source   UNRESOLVABLE 1 "$(binding 1.0.0 "$V100" "$ENTRY" "just-a-name")"
expect not_installed UNRESOLVABLE 1 "$(binding 9.9.9 "$V100")"
expect traversal    UNRESOLVABLE 1 "$(binding 1.0.0 "$V100" "../../../etc/hosts")"

# REGRESSION D2: the binding disagrees with the release it names. An earlier
# revision could be pointed at a fabricated package where this agreed, and
# returned PASS forever.
expect lying_pin REBIND_REQUIRED 1 "$(binding 1.0.0 "$(printf 'a%.0s' {1..64})")"

# A newer release exists and the entrypoint is untouched.
release 1.1.0 "kernel text as of one-oh-oh"
expect stale STALE_COMPATIBLE 1 "$(binding 1.0.0 "$V100")"

# A newer release changed the entrypoint.
release 1.2.0 "kernel text as of one-two-oh, materially different"
expect drifted REBIND_REQUIRED 1 "$(binding 1.0.0 "$V100")"

# Pinning the newest again is green.
V120=$(sha "$CACHE/kc-claude-plugins/kc-dev-flow/1.2.0/$ENTRY")
expect pass_newest PASS 0 "$(binding 1.2.0 "$V120")"

printf 'verify-binding-contract:PASS:all-outcomes\n'
