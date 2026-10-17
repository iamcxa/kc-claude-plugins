#!/bin/bash
# Usage: mutations.sh <patched design_surfaces.py> <fixture task .md> <fixture's security/ report dir>
# Applies each mutation to a copy of the fixture, runs `check`, prints exit status and first line.
CHK=$1; FX=$2; REP=$3; W=$(mktemp -d)
run() { n=$1; shift; mkdir -p "$W/$n"; cp -R "$REP" "$W/$n/security"; sed "$@" "$FX" > "$W/$n.md"
  out=$(python3 -I -B "$CHK" check "$W/$n.md"); printf '%-14s exit %s | %s\n' "$n" "$?" "$(echo "$out" | head -1)"; }
run baseline    -e 's/^$/\n/'
run no-line     -e '/^Security review:/d'
run not-run     -e 's#^Security review:.*#Security review: not run: kc-pr-flow not installed#'
run no-finding2 -e '/^Security finding 2:/d'
run undeclared  -e 's#finding 1: AC-5#finding 1: AC-99#'
run extra       -e '$a\
Security finding 7: declined: x'
run traversal   -e 's#^Security review:.*#Security review: ../x.yaml#'
run no-focus    -e '/^Security focus file:/d'
run pilot       -e 's#^profile: prod#profile: pilot#' -e '/^Security/d'
run empty-why   -e 's#declined: .*#declined:#'
run past-ideation -e 's#^status: ideation#status: implementation#' -e '/^Security/d'
run decline-high -e 's#^Security finding 1:.*#Security finding 1: declined: the design accepts it#'
