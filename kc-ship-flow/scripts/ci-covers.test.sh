#!/usr/bin/env bash
# Behavior contract for kc-ship-flow/scripts/ci-covers.sh, driven through
# synthetic fixtures under kc-ship-flow/scripts/fixtures/.
#
# Self-check -- prove this suite actually catches a broken check (manual,
# not one of the cases below, and not run by this file itself):
#   cp kc-ship-flow/scripts/ci-covers.sh /tmp/ci-covers.sh.orig
#   sed -i.bak 's/matched=1/matched=0/' kc-ship-flow/scripts/ci-covers.sh
#   bash kc-ship-flow/scripts/ci-covers.test.sh; echo "exit: $?"
#   cp /tmp/ci-covers.sh.orig kc-ship-flow/scripts/ci-covers.sh
#   rm -f kc-ship-flow/scripts/ci-covers.sh.bak
# Expect at least one "FAIL" line (case b) and a non-zero exit.

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
CI_COVERS="$HERE/ci-covers.sh"
FIXTURES="$HERE/fixtures"

PASS=0
FAIL=0

pass() { printf 'case %s: PASS - %s\n' "$1" "$2"; PASS=$((PASS + 1)); }
fail() { printf 'case %s: FAIL - %s\n' "$1" "$2"; FAIL=$((FAIL + 1)); }

# --- case (a): uncovered fixture -- check named but never enters the
# package -- exits 1 naming (b) ---
out_a="$(bash "$CI_COVERS" "$FIXTURES/monorepo-uncovered" experiments/island pr-test 2>&1)"
rc_a=$?
if [ "$rc_a" -eq 1 ] && grep -q "experiments/island not run by pr-test" <<<"$out_a" && grep -q "(b:" <<<"$out_a"; then
  pass a "uncovered fixture exits 1 naming (b)"
else
  printf '  out=%s\n' "$out_a"
  fail a "uncovered fixture exits 1 naming (b)"
fi

# --- case (b): covered fixture (working-directory: entry) -- exits 0 ---
out_b="$(bash "$CI_COVERS" "$FIXTURES/monorepo-covered" experiments/island pr-test 2>&1)"
rc_b=$?
if [ "$rc_b" -eq 0 ] && grep -q "experiments/island run by pr-test" <<<"$out_b"; then
  pass b "covered fixture (working-directory:) exits 0"
else
  printf '  out=%s\n' "$out_b"
  fail b "covered fixture (working-directory:) exits 0"
fi

# --- case (c): a workflow that never names the check at all -- exits 1
# naming (a) ---
TMP_C="$(mktemp -d)"
mkdir -p "$TMP_C/.github/workflows"
cat > "$TMP_C/.github/workflows/ci.yml" <<'EOF'
name: CI
on: push
jobs:
  other-check:
    runs-on: ubuntu-latest
    steps:
      - run: echo hi
EOF
out_c="$(bash "$CI_COVERS" "$TMP_C" experiments/island pr-test 2>&1)"
rc_c=$?
rm -rf "$TMP_C"
if [ "$rc_c" -eq 1 ] && grep -q "experiments/island not run by pr-test" <<<"$out_c" && grep -q "(a:" <<<"$out_c"; then
  pass c "no job/step named pr-test exits 1 naming (a)"
else
  printf '  out=%s\n' "$out_c"
  fail c "no job/step named pr-test exits 1 naming (a)"
fi

# --- case (d): a workflow entering the package via a bare `cd` line
# under the check's job -- exits 0 ---
TMP_D="$(mktemp -d)"
mkdir -p "$TMP_D/.github/workflows"
cat > "$TMP_D/.github/workflows/ci.yml" <<'EOF'
name: CI
on: push
jobs:
  pr-test:
    runs-on: ubuntu-latest
    steps:
      - run: |
          cd experiments/island
          npm test
EOF
out_d="$(bash "$CI_COVERS" "$TMP_D" experiments/island pr-test 2>&1)"
rc_d=$?
rm -rf "$TMP_D"
if [ "$rc_d" -eq 0 ] && grep -q "experiments/island run by pr-test" <<<"$out_d"; then
  pass d "cd experiments/island line exits 0"
else
  printf '  out=%s\n' "$out_d"
  fail d "cd experiments/island line exits 0"
fi

# --- case (e): a paths: filter matching <package-path>/** -- exits 0 ---
TMP_E="$(mktemp -d)"
mkdir -p "$TMP_E/.github/workflows"
cat > "$TMP_E/.github/workflows/ci.yml" <<'EOF'
name: CI
on:
  push:
    paths:
      - experiments/island/**
jobs:
  pr-test:
    runs-on: ubuntu-latest
    steps:
      - run: npm test
EOF
out_e="$(bash "$CI_COVERS" "$TMP_E" experiments/island pr-test 2>&1)"
rc_e=$?
rm -rf "$TMP_E"
if [ "$rc_e" -eq 0 ] && grep -q "experiments/island run by pr-test" <<<"$out_e"; then
  pass e "paths: filter matching experiments/island/** exits 0"
else
  printf '  out=%s\n' "$out_e"
  fail e "paths: filter matching experiments/island/** exits 0"
fi

# --- case (f): a --filter <manifest-name> line using the package's
# package.json name -- exits 0 ---
TMP_F="$(mktemp -d)"
mkdir -p "$TMP_F/.github/workflows" "$TMP_F/experiments/island"
cat > "$TMP_F/experiments/island/package.json" <<'EOF'
{"name": "island-experiment"}
EOF
cat > "$TMP_F/.github/workflows/ci.yml" <<'EOF'
name: CI
on: push
jobs:
  pr-test:
    runs-on: ubuntu-latest
    steps:
      - run: pnpm --filter island-experiment test
EOF
out_f="$(bash "$CI_COVERS" "$TMP_F" experiments/island pr-test 2>&1)"
rc_f=$?
rm -rf "$TMP_F"
if [ "$rc_f" -eq 0 ] && grep -q "experiments/island run by pr-test" <<<"$out_f"; then
  pass f "--filter island-experiment (manifest name) exits 0"
else
  printf '  out=%s\n' "$out_f"
  fail f "--filter island-experiment (manifest name) exits 0"
fi

# --- case (g): no .github/workflows/ directory at all -- exits 1 naming
# (a) ---
TMP_G="$(mktemp -d)"
out_g="$(bash "$CI_COVERS" "$TMP_G" experiments/island pr-test 2>&1)"
rc_g=$?
rm -rf "$TMP_G"
if [ "$rc_g" -eq 1 ] && grep -q "experiments/island not run by pr-test" <<<"$out_g" && grep -q "no .github/workflows" <<<"$out_g"; then
  pass g "missing .github/workflows/ directory exits 1"
else
  printf '  out=%s\n' "$out_g"
  fail g "missing .github/workflows/ directory exits 1"
fi

# --- case (h): a usage error (wrong arg count) exits 2 ---
out_h="$(bash "$CI_COVERS" one two 2>&1)"
rc_h=$?
if [ "$rc_h" -eq 2 ] && grep -q "^usage:" <<<"$out_h"; then
  pass h "wrong arg count exits 2 with a usage line"
else
  printf '  out=%s\n' "$out_h"
  fail h "wrong arg count exits 2 with a usage line"
fi

printf '\nci-covers.test: %s passed, %s failed\n' "$PASS" "$FAIL"
if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
exit 0
