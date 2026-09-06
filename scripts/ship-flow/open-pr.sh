#!/usr/bin/env bash
# Open a Draft PR from a worker's accepted Evidence block.
# Usage: open-pr.sh <evidence-file>
#
# Title is the CANDIDATE_SHA commit's subject; body carries BASE_SHA,
# CANDIDATE_SHA, the WITHOUT_IT_COMMAND/WITHOUT_IT_REMOVED_VARIANT pair, and
# the block's own SELF_CHECK line (the accept station's verdict, carried
# rather than re-derived: this script trusts the block was already accepted
# by scripts/ship-flow/accept-evidence.sh before it runs). Progress is logged
# to stderr with timestamps; stdout carries exactly the opened PR number.
#
# Exit codes: 0 PR opened, number printed on stdout; 1 `gh pr create` failed;
# 2 usage error or an incomplete Evidence block (missing a required field).
set -euo pipefail

timestamp() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
log() { echo "$(timestamp) open-pr: $*" >&2; }
die() { log "$*"; exit 2; }

if [ "$#" -ne 1 ]; then
  echo "usage: open-pr.sh <evidence-file>" >&2
  exit 2
fi

evidence_file="$1"
[ -f "$evidence_file" ] || die "evidence file not found: $evidence_file"

repo_root="$(git rev-parse --show-toplevel)"

parse_evidence() {
  sed -n '/^## Evidence$/,/^$/p' "$evidence_file"
}

get_field() {
  local key="$1"
  echo "$evidence_text" | grep "^${key}:" | head -1 | sed "s/^${key}: *//" || true
}

evidence_text="$(parse_evidence)"
[ -n "$evidence_text" ] || die "no Evidence block found in $evidence_file"

CANDIDATE_SHA="$(get_field CANDIDATE_SHA)"
BASE_SHA="$(get_field BASE_SHA)"
BRANCH="$(get_field BRANCH)"
WITHOUT_IT_COMMAND="$(get_field WITHOUT_IT_COMMAND)"
WITHOUT_IT_REMOVED_VARIANT="$(get_field WITHOUT_IT_REMOVED_VARIANT)"
SELF_CHECK="$(get_field SELF_CHECK)"

for field_name in CANDIDATE_SHA BASE_SHA BRANCH WITHOUT_IT_COMMAND WITHOUT_IT_REMOVED_VARIANT SELF_CHECK; do
  [ -n "${!field_name}" ] || die "incomplete Evidence block: missing $field_name"
done

git -C "$repo_root" rev-parse --verify "${CANDIDATE_SHA}^{commit}" >/dev/null 2>&1 \
  || die "CANDIDATE_SHA unreachable: $CANDIDATE_SHA"

title="$(git -C "$repo_root" log -1 --format=%s "$CANDIDATE_SHA")"

body_file="$(mktemp)"
trap 'rm -f "$body_file"' EXIT
cat > "$body_file" <<BODY_EOF
Candidate: \`$CANDIDATE_SHA\`
Base: \`$BASE_SHA\`

Without-it: \`$WITHOUT_IT_COMMAND\`
Removed variant: \`$WITHOUT_IT_REMOVED_VARIANT\`

Accept station: $SELF_CHECK
BODY_EOF

log "opening Draft PR: branch=$BRANCH base=main title=$title"
set +e
pr_output="$(gh pr create --draft --base main --head "$BRANCH" --title "$title" --body-file "$body_file" 2>&1)"
pr_status=$?
set -e
if [ "$pr_status" -ne 0 ]; then
  die "gh pr create failed (exit $pr_status): $pr_output"
fi
log "gh pr create output: $pr_output"

pr_number="$(echo "$pr_output" | grep -oE '[0-9]+' | tail -1)"
[ -n "$pr_number" ] || die "could not extract PR number from gh output: $pr_output"

echo "$pr_number"
