#!/usr/bin/env bash
# Fail-closed contract for kc-dev-flow/scripts/verify-binding.py.
#
# The cases marked REGRESSION are defects this checker actually shipped, each
# pinned as a fixture rather than described. Three of them are the same defect:
# a repository with no binding reported PASS, because the checker looked for the
# binding inside a prose document. The fix is that it no longer reads one.
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
VERIFY="$ROOT/kc-dev-flow/scripts/verify-binding.py"
TEST_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/verify-binding.XXXXXX")
trap 'rm -rf "$TEST_ROOT"' EXIT

fail() { printf 'verify-binding-contract:FAIL:%s\n' "$*" >&2; exit 1; }

# A cache root shaped like the real one: <marketplace>/<plugin>/<version>/...
CACHE="$TEST_ROOT/cache"
PLUGIN_ROOT="$CACHE/kc-claude-plugins/kc-dev-flow"
SOURCE="iamcxa/kc-claude-plugins/kc-dev-flow"
ENTRY="references/kernel.md"

release() { # 1=version 2=kernel-text 3=profile-text
  local dir="$PLUGIN_ROOT/$1"
  mkdir -p "$dir/references" "$dir/.claude-plugin"
  printf '%s\n' "$2" >"$dir/$ENTRY"
  printf '%s\n' "${3:-profile as of first release}" >"$dir/references/work-control-profile.md"
  printf '{"version":"%s"}\n' "$1" >"$dir/.claude-plugin/plugin.json"
}

digest_of() { # 1=version -- the checker's own answer, read back from a probe run
  local probe="$TEST_ROOT/probe.yaml" out
  printf 'kernel_source: %s\nkernel_version: %s\nkernel_entrypoint: %s\n' "$SOURCE" "$1" "$ENTRY" >"$probe"
  # A digest-less binding is UNRESOLVABLE by design, so the probe exits non-zero.
  set +e; out=$(python3 "$VERIFY" "$probe" --cache-root "$CACHE" 2>&1); set -e
  sed -n 's/^verify-binding:expected-digest://p' <<<"$out"
}

binding() { # 1=version 2=digest [3=entrypoint] [4=source]
  printf 'kernel_source: %s\nkernel_version: %s\nkernel_entrypoint: %s\nkernel_digest: %s\n' \
    "${4:-$SOURCE}" "$1" "${3:-$ENTRY}" "$2"
}

expect() { # 1=case 2=want 3=want_rc 4=body [5=extension]
  local name=$1 want=$2 want_rc=$3 body=$4 ext=${5:-yaml} out rc file
  file="$TEST_ROOT/$name.$ext"; printf '%s\n' "$body" >"$file"
  set +e; out=$(python3 "$VERIFY" "$file" --cache-root "$CACHE" 2>&1); rc=$?; set -e
  grep -q "verify-binding:$want:" <<<"$out" || fail "$name expected $want, got: $(head -1 <<<"$out")"
  [[ "$rc" == "$want_rc" ]] || fail "$name expected exit $want_rc, got $rc"
}

release 1.0.0 "kernel text as of one-oh-oh"
V100=$(digest_of 1.0.0)
[[ -n "$V100" ]] || fail "the checker emitted no expected-digest for an installed release"

expect pass PASS 0 "$(binding 1.0.0 "$V100")"

# REGRESSION: a digest is a hex value, not a case-sensitive string. An earlier
# revision answered a correct binding with an expensive REBIND_REQUIRED.
expect uppercase_digest PASS 0 "$(binding 1.0.0 "$(tr 'a-f' 'A-F' <<<"$V100")")"

# REGRESSION (three shipped variants of one defect): the checker used to locate
# the binding inside a Markdown document. Fields collected from unrelated blocks,
# an unclosed fence, and a four-space-indented example each produced PASS for a
# repository that had no binding. A prose document is now refused outright.
PROSE=$(printf 'Quoting the upstream template, closing fence forgotten:\n\n```yaml\n%s\n## Appendix\n\nkernel_entrypoint: %s\nkernel_digest: %s\n```\n' \
  "$(printf 'kernel_source: %s\nkernel_version: 1.0.0' "$SOURCE")" "$ENTRY" "$V100")
expect prose_document UNRESOLVABLE 1 "$PROSE" md

# The suffix is the readable reason, not the enforcement. Renaming the same
# prose to a data suffix must not resurrect the defect: a fence line is not a
# record line, so the file is refused structurally.
expect prose_renamed UNRESOLVABLE 1 "$PROSE"

# A binding file that does not exist is not an up-to-date one.
set +e
python3 "$VERIFY" "$TEST_ROOT/absent.yaml" --cache-root "$CACHE" >/dev/null 2>&1; rc=$?
set -e
[[ "$rc" != 0 ]] || fail "an absent binding file passed"

# Two values for one field: resolving either would verify a binding the
# repository does not operate under.
expect duplicate_field UNRESOLVABLE 1 "$(printf '%s\nkernel_version: 9.9.9\n' "$(binding 1.0.0 "$V100")")"

# Indented keys belong to some other mapping, not to the binding.
expect indented_field UNRESOLVABLE 1 "$(printf 'example:\n  kernel_source: %s\n  kernel_version: 1.0.0\n  kernel_entrypoint: %s\n' "$SOURCE" "$ENTRY")"

expect partial       UNRESOLVABLE 1 "$(printf 'kernel_source: %s\nkernel_version: 1.0.0\n' "$SOURCE")"
expect bad_source    UNRESOLVABLE 1 "$(binding 1.0.0 "$V100" "$ENTRY" "just-a-name")"
expect not_installed UNRESOLVABLE 1 "$(binding 9.9.9 "$V100")"
expect traversal     UNRESOLVABLE 1 "$(binding 1.0.0 "$V100" "../../../etc/hosts")"

# Declared without a digest is unverifiable, which is not a lesser state than
# undeclared — but the checker still hands back the value needed to complete it.
expect no_digest UNRESOLVABLE 1 "$(printf 'kernel_source: %s\nkernel_version: 1.0.0\nkernel_entrypoint: %s\n' "$SOURCE" "$ENTRY")"

# REGRESSION: the binding disagrees with the release it names. An earlier
# revision could be pointed at a fabricated package where this agreed, and
# returned PASS forever.
expect lying_pin REBIND_REQUIRED 1 "$(binding 1.0.0 "$(printf 'a%.0s' {1..64})")"

# An installer directory that is not a release must not be ranked as the newest.
mkdir -p "$PLUGIN_ROOT/local"
expect ignores_non_version PASS 0 "$(binding 1.0.0 "$V100")"

# REGRESSION: a pre-release sorts below the version it precedes. An earlier
# revision ranked 1.0.0-rc1 above 1.0.0 and reported drift against it.
release 1.0.0-rc1 "kernel text as of the release candidate"
expect prerelease_is_not_newest PASS 0 "$(binding 1.0.0 "$V100")"

# A newer release, no reference text touched anywhere in the set.
release 1.1.0 "kernel text as of one-oh-oh"
expect stale STALE_COMPATIBLE 1 "$(binding 1.0.0 "$V100")"

# REGRESSION: a release that moves a reference other than the entrypoint moves
# an invariant. An entrypoint-only digest called this unchanged, and the skill
# then told the adopter to bump the version and read nothing.
release 1.2.0 "kernel text as of one-oh-oh" "profile with a new optional control"
expect non_entrypoint_reference_moved REBIND_REQUIRED 1 "$(binding 1.0.0 "$V100")"

# A newer release changed the entrypoint itself.
release 1.3.0 "kernel text as of one-three-oh, materially different"
expect drifted REBIND_REQUIRED 1 "$(binding 1.0.0 "$V100")"

# Pinning the newest again is green.
expect pass_newest PASS 0 "$(binding 1.3.0 "$(digest_of 1.3.0)")"

# 1.10.0 outranks 1.9.0; string order would not.
release 1.9.0 "kernel text as of one-nine-oh"
release 1.10.0 "kernel text as of one-ten-oh"
expect numeric_version_order PASS 0 "$(binding 1.10.0 "$(digest_of 1.10.0)")"

printf 'verify-binding-contract:PASS:all-outcomes\n'
