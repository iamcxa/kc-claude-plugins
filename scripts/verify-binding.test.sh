#!/usr/bin/env bash
# Fail-closed contract for kc-dev-flow/scripts/verify-binding.py.
#
# Every case asserts the outcome token, the exit code, AND a substring of the
# reason. Asserting the token alone let four fixtures pass for a reason other
# than the guard they were written for, because any UNRESOLVABLE satisfied any
# UNRESOLVABLE expectation -- the same "green for the wrong reason" shape this
# checker exists to detect.
#
# The cases marked REGRESSION are defects this checker actually shipped.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
VERIFY="$ROOT/kc-dev-flow/scripts/verify-binding.py"
TEST_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/verify-binding.XXXXXX")
trap 'rm -rf "$TEST_ROOT"' EXIT

fail() { printf 'verify-binding-contract:FAIL:%s\n' "$*" >&2; exit 1; }

# A cache root shaped like the real one: <marketplace>/<plugin>/<version>/...
CACHE="$TEST_ROOT/cache"
PLUGIN_ROOT="$CACHE/kc-claude-plugins/kc-dev-flow"
SOURCE="iamcxa/kc-claude-plugins/kc-dev-flow"
ENTRY="references/kernel.md"

release() { # 1=version 2=kernel-text [3=profile-text] [4=cache]
  local dir="${4:-$CACHE}/kc-claude-plugins/kc-dev-flow/$1"
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

check() { # 1=case 2=want 3=want_rc 4=want_detail 5=file [6=cache]
  local name=$1 want=$2 want_rc=$3 detail=$4 file=$5 cache=${6:-$CACHE} out rc
  set +e; out=$(python3 "$VERIFY" "$file" --cache-root "$cache" 2>&1); rc=$?; set -e
  grep -q "verify-binding:$want:" <<<"$out" || fail "$name expected $want, got: $(head -1 <<<"$out")"
  [[ "$rc" == "$want_rc" ]] || fail "$name expected exit $want_rc, got $rc"
  grep -qF -- "$detail" <<<"$out" || fail "$name expected reason containing '$detail', got: $(head -1 <<<"$out")"
}

expect() { # 1=case 2=want 3=want_rc 4=want_detail 5=body [6=extension] [7=cache]
  local name=$1 file
  file="$TEST_ROOT/$name.${6:-yaml}"; printf '%s\n' "$5" >"$file"
  check "$name" "$2" "$3" "$4" "$file" "${7:-$CACHE}"
}

release 1.0.0 "kernel text as of one-oh-oh"
V100=$(digest_of 1.0.0)
[[ -n "$V100" ]] || fail "the checker emitted no expected-digest for an installed release"

expect pass PASS 0 "is the newest installed" "$(binding 1.0.0 "$V100")"

# REGRESSION: a digest is a hex value, not a case-sensitive string. An earlier
# revision answered a correct binding with an expensive REBIND_REQUIRED.
expect uppercase_digest PASS 0 "is the newest installed" "$(binding 1.0.0 "$(tr 'a-f' 'A-F' <<<"$V100")")"

# --- The binding is not located inside a document -------------------------
# Four shipped variants of one defect: fields collected across Markdown blocks,
# an unclosed fence, a four-space-indented example, and then a shape filter that
# admitted any prose line of the form `Word: sentence`. The body below is the
# fourth: a document that says in its own words that it holds no binding.
PROSE=$(printf '# Dev flow\n\n## Kernel binding\n\nStatus: not adopted yet\nWarning: the block below is an EXAMPLE ONLY.\n\n%s\n' "$(binding 1.0.0 "$V100")")
expect prose_by_key UNRESOLVABLE 1 "is not a binding key" "$PROSE"
expect prose_no_suffix UNRESOLVABLE 1 "is not a binding key" "$PROSE" "noext"
expect fence_line UNRESOLVABLE 1 "is not a binding line" "$(printf '```yaml\n%s```\n' "$(binding 1.0.0 "$V100")")"
# A column-zero list item makes the document root a sequence, which cannot also
# carry the mapping keys a binding needs.
expect list_item UNRESOLVABLE 1 "is not a binding line" "$(printf -- '- copy this to your own file\n%s' "$(binding 1.0.0 "$V100")")"

# The suffix gate gets a body only it can refuse: a valid record in a .md file.
expect prose_suffix UNRESOLVABLE 1 "is a prose document" "$(binding 1.0.0 "$V100")" md
# ...and naming that same file through a symlink must refuse for the same reason.
ln -s "$TEST_ROOT/prose_suffix.md" "$TEST_ROOT/symlinked.yaml"
check symlinked_prose UNRESOLVABLE 1 "is a prose document" "$TEST_ROOT/symlinked.yaml"

# A binding file that does not exist is not an up-to-date one.
check absent UNRESOLVABLE 1 "is not a readable file" "$TEST_ROOT/absent.yaml"

# --- Field reading ---------------------------------------------------------
expect duplicate_field UNRESOLVABLE 1 "declared 2 times" "$(printf '%s\nkernel_version: 9.9.9\n' "$(binding 1.0.0 "$V100")")"
# Indented keys belong to some other mapping. The digest is present and valid,
# so indentation is the only reason this can fail.
expect indented_field UNRESOLVABLE 1 "binding omits kernel_source,kernel_version,kernel_entrypoint" \
  "$(printf 'authority:\n  kernel_source: %s\n  kernel_version: 1.0.0\n  kernel_entrypoint: %s\n  kernel_digest: %s\n' "$SOURCE" "$ENTRY" "$V100")"
expect partial     UNRESOLVABLE 1 "binding omits kernel_entrypoint" "$(printf 'kernel_source: %s\nkernel_version: 1.0.0\n' "$SOURCE")"
expect no_digest   UNRESOLVABLE 1 "binding omits kernel_digest" "$(printf 'kernel_source: %s\nkernel_version: 1.0.0\nkernel_entrypoint: %s\n' "$SOURCE" "$ENTRY")"
# The digest a first adoption needs is handed back, not hand-computed.
grep -q "verify-binding:expected-digest:$V100" \
  <<<"$(python3 "$VERIFY" "$TEST_ROOT/no_digest.yaml" --cache-root "$CACHE" 2>&1 || true)" \
  || fail "no_digest did not print the expected digest"

# --- Source resolution -----------------------------------------------------
expect bad_source    UNRESOLVABLE 1 "is not <owner>/<marketplace>/<plugin>" "$(binding 1.0.0 "$V100" "$ENTRY" "just-a-name")"
# A source that climbs out of the cache root would let the binding file choose
# the package, which is the caller-supplied-package failure by another route.
expect dotdot_source UNRESOLVABLE 1 "is not <owner>/<marketplace>/<plugin>" "$(binding 1.0.0 "$V100" "$ENTRY" "../forged")"
expect not_installed UNRESOLVABLE 1 "is not installed" "$(binding 9.9.9 "$V100")"

# --- Entrypoint ------------------------------------------------------------
# An existing file outside references/, so strict resolution succeeds and
# containment is the only thing that can refuse it.
printf 'outside the reference set\n' >"$PLUGIN_ROOT/1.0.0/AGENTS.md"
expect entrypoint_outside UNRESOLVABLE 1 "is not a file inside 1.0.0/references/" "$(binding 1.0.0 "$V100" "../1.0.0/AGENTS.md")"
expect entrypoint_escapes UNRESOLVABLE 1 "is not a file inside 1.0.0/references/" "$(binding 1.0.0 "$V100" "../../../../etc/hosts")"
expect entrypoint_is_dir  UNRESOLVABLE 1 "is not a file inside 1.0.0/references/" "$(binding 1.0.0 "$V100" "references")"

# REGRESSION: the binding disagrees with the release it names. An earlier
# revision could be pointed at a fabricated package where this agreed, and
# returned PASS forever.
expect lying_pin REBIND_REQUIRED 1 "but that release is" "$(binding 1.0.0 "$(printf 'a%.0s' {1..64})")"

# --- Release ranking -------------------------------------------------------
# An installer directory that is not a release must not be ranked as newest.
# `1.0.0.bak` is the case that matters: it sorts ABOVE 1.0.0 numerically.
mkdir -p "$PLUGIN_ROOT/1.0.0.bak/references"
printf 'a backup copy, not a release\n' >"$PLUGIN_ROOT/1.0.0.bak/$ENTRY"
expect ignores_non_version PASS 0 "is the newest installed" "$(binding 1.0.0 "$V100")"

# REGRESSION: a pre-release sorts below the version it precedes. An earlier
# revision ranked 1.0.0-rc1 above 1.0.0 and reported drift against it.
release 1.0.0-rc1 "kernel text as of the release candidate"
expect prerelease_is_not_newest PASS 0 "is the newest installed" "$(binding 1.0.0 "$V100")"

# --- Drift -----------------------------------------------------------------
release 1.1.0 "kernel text as of one-oh-oh"
expect stale STALE_COMPATIBLE 1 "no reference text changed" "$(binding 1.0.0 "$V100")"

# REGRESSION: a release that moves a reference other than the entrypoint moves
# an invariant. An entrypoint-only digest called this unchanged, and the skill
# then told the adopter to bump the version and read nothing.
release 1.2.0 "kernel text as of one-oh-oh" "profile with a new optional control"
expect non_entrypoint_reference_moved REBIND_REQUIRED 1 "its references differ" "$(binding 1.0.0 "$V100")"

release 1.3.0 "kernel text as of one-three-oh, materially different"
expect drifted REBIND_REQUIRED 1 "its references differ" "$(binding 1.0.0 "$V100")"
expect pass_newest PASS 0 "is the newest installed" "$(binding 1.3.0 "$(digest_of 1.3.0)")"

# 1.10.0 outranks 1.9.0; string order would not.
release 1.9.0 "kernel text as of one-nine-oh"
release 1.10.0 "kernel text as of one-ten-oh"
expect numeric_version_order PASS 0 "is the newest installed" "$(binding 1.10.0 "$(digest_of 1.10.0)")"

# --- Pathological reference sets, each in its own cache ---------------------
# A symlink under references/ is refused, not skipped: its bytes cannot be
# attributed to the release, and skipping it would let a release change what an
# adopter reads while the set reported unchanged.
SYM="$TEST_ROOT/cache-symlink"; release 1.0.0 "kernel" "profile" "$SYM"
printf 'content outside the set\n' >"$TEST_ROOT/outside-target.md"
ln -s "$TEST_ROOT/outside-target.md" "$SYM/kc-claude-plugins/kc-dev-flow/1.0.0/references/linked.md"
expect symlink_in_references UNRESOLVABLE 1 "carries a symlink under references/" "$(binding 1.0.0 "$V100")" yaml "$SYM"

EMPTY="$TEST_ROOT/cache-empty"
mkdir -p "$EMPTY/kc-claude-plugins/kc-dev-flow/1.0.0/references"
expect empty_references UNRESOLVABLE 1 "has an empty references/" "$(binding 1.0.0 "$V100")" yaml "$EMPTY"

NOREFS="$TEST_ROOT/cache-norefs"
mkdir -p "$NOREFS/kc-claude-plugins/kc-dev-flow/1.0.0"
expect no_references UNRESOLVABLE 1 "ships no references/ to digest" "$(binding 1.0.0 "$V100")" yaml "$NOREFS"

printf 'verify-binding-contract:PASS:all-outcomes\n'
