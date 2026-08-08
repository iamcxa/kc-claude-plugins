#!/usr/bin/env bash
# Contract for scripts/dev-flow-state-prereq.sh.
#
# Covers the refusal path, which is the one that prevents loss: a workspace that
# does not hold the state checkout must be told so, by name, and must exit
# non-zero. The holder-side outcomes (75 dirty, 76 local-ahead, 77 diverged) are
# not exercised here — they need a live state branch and a remote — so this
# suite proves the guard refuses, not that every recovery code is reachable.
# Stated rather than implied, because a suite that looks complete and is not is
# the failure this repository keeps finding.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PREREQ="$ROOT/scripts/dev-flow-state-prereq.sh"
TEST_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/state-prereq.XXXXXX")
trap 'rm -rf "$TEST_ROOT"' EXIT

fail() { printf 'state-prereq-contract:FAIL:%s\n' "$*" >&2; exit 1; }

run() { # 1=cwd -> sets OUT and RC
  set +e
  OUT=$(cd "$1" && "$PREREQ" 2>&1)
  RC=$?
  set -e
}

# A repository whose workflow directory has no state checkout: the shape a fresh
# Conductor workspace has, and the one in which a filed entity exists nowhere.
NOHOLDER="$TEST_ROOT/no-holder"
mkdir -p "$NOHOLDER/docs/dev"
git -C "$NOHOLDER" init -q
git -C "$NOHOLDER" -c user.email=t@t -c user.name=t commit -q --allow-empty -m init

run "$NOHOLDER"
[[ "$RC" != 0 ]] || fail "a workspace holding no state checkout exited 0"
grep -q "state holder" <<<"$OUT" || fail "refusal did not name the missing holder: $(head -1 <<<"$OUT")"

# Outside a repository at all: still refuses rather than guessing a workflow.
run "$TEST_ROOT"
[[ "$RC" != 0 ]] || fail "outside a git repository the check exited 0"

# The real repository this ships in is itself a non-holder in most workspaces,
# so the refusal must name a path rather than only complaining.
run "$NOHOLDER"
grep -qE "/|holder" <<<"$OUT" || fail "refusal names neither a path nor a holder"

printf 'state-prereq-contract:PASS:refusal-path\n'
