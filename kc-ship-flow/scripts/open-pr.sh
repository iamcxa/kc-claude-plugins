#!/usr/bin/env bash
# Open a Draft PR from a worker's accepted Evidence block, body per the
# pr-merge mod's PR body template (docs/dev/_mods/pr-merge.md § PR body
# template).
# Usage: open-pr.sh <evidence-file> <batch-dir> [--dry-run]
#
# <batch-dir> is a batch record directory: <batch-dir>/README.md (entity id
# is the directory's own basename, `batch-` prefix stripped) and
# <batch-dir>/receipt/plan-receipt.json (its `issues` map -- each entry's
# `branch`, `close_line`, and `body`'s `## The problem` paragraph). The
# audit link's owner/repo, ref, and path all come from the batch-dir's own
# git checkout (origin remote, current branch, `git ls-files`), never from
# CANDIDATE_SHA or cwd's repository -- the same rule pr-merge.md's
# split-root correction applies to a spacedock entity, applied here to this
# lighter batch-dir shape.
#
# Body order: a <=25-word motivation lead condensed from the matched
# issue's `## The problem`; `## What changed` (one bullet per top-level
# FILES entry, capped at 5); `## Evidence` (N/N passed, counted from
# TESTS's `-> exit` markers), omitted when TESTS is absent or has no such
# marker; `---`; the audit link; the issue's `close_line` verbatim.
#
# --dry-run prints the body to stdout and exits 0 without resolving
# CANDIDATE_SHA, binding BRANCH to origin, or calling gh. Every other exit
# path is unchanged from non-dry-run.
#
# Exit codes: 0 PR opened (number on stdout), or --dry-run body printed; 2
# every other exit path -- a usage error; an evidence or batch-dir argument
# that does not exist; an evidence file with no `## Evidence` heading or
# more than one; an Evidence block missing a required field; a BRANCH
# containing `:` (fork syntax); a batch-dir README.md untracked by its own
# checkout; a batch receipt missing or with zero or more than one issue
# whose `branch` equals BRANCH; an unreachable CANDIDATE_SHA; a BRANCH that
# resolves to zero or more than one ref on origin; a BRANCH whose remote
# head does not equal CANDIDATE_SHA; a `gh pr create` failure; or a PR
# number that cannot be parsed from `gh pr create`'s stdout.
set -euo pipefail

timestamp() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
log() { echo "$(timestamp) open-pr: $*" >&2; }
die() { log "$*"; exit 2; }

dry_run=0
args=()
for arg in "$@"; do
  case "$arg" in
    --dry-run) dry_run=1 ;;
    *) args+=("$arg") ;;
  esac
done
if [ "${#args[@]}" -ne 2 ]; then
  echo "usage: open-pr.sh <evidence-file> <batch-dir> [--dry-run]" >&2
  exit 2
fi
evidence_file="${args[0]}"
batch_dir="${args[1]}"

[ -f "$evidence_file" ] || die "evidence file not found: $evidence_file"
[ -d "$batch_dir" ] || die "batch dir not found: $batch_dir"

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
FILES="$(get_field FILES)"
TESTS="$(get_field TESTS)"
WITHOUT_IT_COMMAND="$(get_field WITHOUT_IT_COMMAND)"
WITHOUT_IT_REMOVED_VARIANT="$(get_field WITHOUT_IT_REMOVED_VARIANT)"
SELF_CHECK="$(get_field SELF_CHECK)"

for field_name in CANDIDATE_SHA BASE_SHA BRANCH WITHOUT_IT_COMMAND WITHOUT_IT_REMOVED_VARIANT SELF_CHECK; do
  [ -n "${!field_name}" ] || die "incomplete Evidence block: missing $field_name"
done

# Refuse cheap, string-only shapes before any git object lookup: a shallow
# clone (CI's actions/checkout@v4 default depth 1) may not have CANDIDATE_SHA
# as a local object, so the fork-syntax refusal below must fire first and for
# its own reason, not be masked by a SHA-lookup failure. `gh pr create --head`
# accepts `user:branch` fork syntax; refuse it outright.
case "$BRANCH" in
  *:*) die "BRANCH contains ':' (fork syntax refused): $BRANCH" ;;
esac

# --- resolve the batch entity from batch-dir's own git checkout ---
batch_readme_relpath="$(git -C "$batch_dir" ls-files --full-name -- README.md)"
[ -n "$batch_readme_relpath" ] || die "batch-dir README.md is untracked by its own checkout: $batch_dir"
batch_origin_url="$(git -C "$batch_dir" remote get-url origin)"
batch_owner_repo="$(printf '%s\n' "$batch_origin_url" | sed -E 's#\.git$##; s#^git@[^:]+:##; s#^https?://[^/]+/##')"
batch_ref="$(git -C "$batch_dir" rev-parse --abbrev-ref HEAD)"
batch_entity_id="$(basename "$batch_dir")"
case "$batch_entity_id" in batch-*) batch_entity_id="${batch_entity_id#batch-}" ;; esac

plan_receipt="$batch_dir/receipt/plan-receipt.json"
[ -f "$plan_receipt" ] || die "batch receipt not found: $plan_receipt"

# --- match BRANCH to exactly one issue in the batch receipt, then build the
# pr-merge-shaped body from that issue, FILES, TESTS, and the batch entity ---
body_tmp="$(mktemp)"
body_err_tmp="$(mktemp)"
trap 'rm -f "$body_tmp" "$body_err_tmp"' EXIT
set +e
python3 - "$plan_receipt" "$BRANCH" "$FILES" "$TESTS" "$batch_owner_repo" "$batch_ref" "$batch_readme_relpath" "$batch_entity_id" \
  >"$body_tmp" 2>"$body_err_tmp" <<'PY'
import json
import re
import sys

receipt_path, branch, files_field, tests_field, owner_repo, ref, readme_path, entity_id = sys.argv[1:9]

with open(receipt_path, encoding="utf-8") as f:
    receipt = json.load(f)

matches = [v for v in receipt.get("issues", {}).values() if v.get("branch") == branch]
if len(matches) != 1:
    print(
        f"{len(matches)} issues in {receipt_path} match BRANCH {branch}, expected exactly 1",
        file=sys.stderr,
    )
    sys.exit(1)
issue = matches[0]


def cap_words(text: str, n: int) -> str:
    return " ".join(text.split()[:n])


def lead_from_problem(body_text: str) -> str:
    m = re.search(r"##\s*The problem\s*\n+(.*?)(?:\n\s*\n|\n##|\Z)", body_text, re.S)
    para = (m.group(1) if m else body_text).strip()
    para = re.sub(r"\s+", " ", para)
    sentence_match = re.search(r"^(.*?[.!?])(\s|$)", para)
    sentence = sentence_match.group(1) if sentence_match else para
    return cap_words(sentence, 25)


def split_top_level(field: str) -> list[str]:
    # Split on top-level commas only -- a `{a,b,c}` brace group in FILES
    # (this repo's convention for a shared-directory file group) stays one
    # token, one bullet, not three.
    tokens: list[str] = []
    depth = 0
    current: list[str] = []
    for ch in field:
        if ch == "{":
            depth += 1
            current.append(ch)
        elif ch == "}":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            tokens.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        tokens.append("".join(current).strip())
    return [t for t in tokens if t]


lines = [lead_from_problem(issue.get("body", "")), "", "## What changed"]
for token in split_top_level(files_field)[:5]:
    lines.append("- " + cap_words(f"Update `{token}`", 15))

if tests_field:
    exits = re.findall(r"->\s*exit\s*(\d+)", tests_field)
    if exits:
        total = len(exits)
        passed = sum(1 for e in exits if e == "0")
        lines += ["", "## Evidence", f"- {passed}/{total} passed"]

lines += ["", "---", f"[{entity_id}](/{owner_repo}/blob/{ref}/{readme_path})"]
close_line = issue.get("close_line", "")
if close_line:
    lines.append(close_line)

print("\n".join(lines))
PY
body_status=$?
set -e
[ "$body_status" -eq 0 ] || die "$(cat "$body_err_tmp")"
body="$(cat "$body_tmp")"

if [ "$dry_run" -eq 1 ]; then
  printf '%s\n' "$body"
  exit 0
fi

git -C "$repo_root" rev-parse --verify "${CANDIDATE_SHA}^{commit}" >/dev/null 2>&1 \
  || die "CANDIDATE_SHA unreachable: $CANDIDATE_SHA"

# Bind BRANCH to CANDIDATE_SHA before ever calling `gh`: a branch whose remote
# head differs from the reviewed commit would open a PR whose diff is not
# what was accepted. Fail closed on any ambiguity.
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
trap 'rm -f "$body_tmp" "$body_err_tmp" "$body_file" "$stderr_file"' EXIT
printf '%s\n' "$body" >"$body_file"

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
