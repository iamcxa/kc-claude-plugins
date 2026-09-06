#!/usr/bin/env bash
# Open a Draft PR from a worker's accepted Evidence block.
# Usage: open-pr.sh <evidence-file>
#
# Title is the CANDIDATE_SHA commit's subject; body carries BASE_SHA,
# CANDIDATE_SHA, the WITHOUT_IT_COMMAND/WITHOUT_IT_REMOVED_VARIANT pair, and
# the block's own SELF_CHECK line (the accept station's verdict, carried
# rather than re-derived: this script trusts the block was already accepted
# by scripts/ship-flow/accept-evidence.sh before it runs). BRANCH is bound to
# CANDIDATE_SHA against origin before `gh pr create` runs, so a fork branch
# (`user:branch`) or a branch whose remote head differs from the reviewed
# commit is refused rather than opened under a misleading title. Progress is
# logged to stderr with timestamps; stdout carries exactly the opened PR
# number.
#
# Exit codes: 0 PR opened, number printed on stdout; 2 every other exit path
# -- a usage error; an evidence file that is missing, has no `## Evidence`
# heading, or has more than one; an Evidence block missing a required field;
# an unreachable CANDIDATE_SHA; a BRANCH containing `:` (fork syntax); a
# BRANCH that resolves to zero or more than one ref on origin; a BRANCH whose
# remote head does not equal CANDIDATE_SHA; a `gh pr create` failure; or a PR
# number that cannot be parsed from `gh pr create`'s stdout.
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

heading_count="$(grep -c '^## Evidence$' "$evidence_file" || true)"
[ "$heading_count" -le 1 ] || die "evidence file has $heading_count '## Evidence' headings, expected at most 1: $evidence_file"

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

# Bind BRANCH to CANDIDATE_SHA before ever calling `gh`: `gh pr create --head`
# accepts `user:branch` fork syntax, and a branch whose remote head differs
# from the reviewed commit would open a PR whose diff is not what was
# accepted. Fail closed on any ambiguity.
case "$BRANCH" in
  *:*) die "BRANCH contains ':' (fork syntax refused): $BRANCH" ;;
esac

branch_refs="$(git -C "$repo_root" ls-remote origin "refs/heads/$BRANCH" 2>/dev/null || true)"
branch_ref_count="$(printf '%s\n' "$branch_refs" | grep -c '^[0-9a-f]\{40\}[[:space:]]' || true)"
[ "$branch_ref_count" -eq 1 ] \
  || die "BRANCH $BRANCH resolved to $branch_ref_count refs on origin, expected exactly 1"
branch_sha="$(printf '%s\n' "$branch_refs" | awk '{print $1}')"
[ "$branch_sha" = "$CANDIDATE_SHA" ] \
  || die "BRANCH $BRANCH remote head $branch_sha does not match CANDIDATE_SHA $CANDIDATE_SHA"

title="$(git -C "$repo_root" log -1 --format=%s "$CANDIDATE_SHA")"

body_file="$(mktemp)"
stderr_file="$(mktemp)"
trap 'rm -f "$body_file" "$stderr_file"' EXIT
cat > "$body_file" <<BODY_EOF
Candidate: \`$CANDIDATE_SHA\`
Base: \`$BASE_SHA\`

Without-it: \`$WITHOUT_IT_COMMAND\`
Removed variant: \`$WITHOUT_IT_REMOVED_VARIANT\`

Accept station: $SELF_CHECK
BODY_EOF

log "opening Draft PR: branch=$BRANCH base=main title=$title"
set +e
pr_stdout="$(gh pr create --draft --base main --head "$BRANCH" --title "$title" --body-file "$body_file" 2>"$stderr_file")"
pr_status=$?
set -e
pr_stderr="$(cat "$stderr_file")"
[ -z "$pr_stderr" ] || log "gh pr create stderr: $pr_stderr"
if [ "$pr_status" -ne 0 ]; then
  die "gh pr create failed (exit $pr_status): $pr_stderr"
fi
log "gh pr create stdout: $pr_stdout"

# Parse the PR number from stdout only (`pull/<number>`); stderr is logged
# above, never scanned for digits, so a `gh` warning or notice on stderr
# cannot be mistaken for the PR number.
pr_number="$(printf '%s\n' "$pr_stdout" | grep -oE 'pull/[0-9]+' | grep -oE '[0-9]+' | tail -1)"
[ -n "$pr_number" ] || die "could not extract PR number from gh stdout: $pr_stdout"

echo "$pr_number"
