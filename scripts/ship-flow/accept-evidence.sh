#!/usr/bin/env bash
# Accept or refuse a worker's Evidence block by reading it, without re-running the worker.
# Usage: accept-evidence.sh <evidence-file> [--repo <repo-path>]
#
# Exits 0 if the Evidence block is accepted (no inconsistencies found).
# Exits non-zero if the Evidence block is refused (inconsistencies detected).
# Exit code 2 indicates usage errors or inability to parse.
set -euo pipefail

timestamp() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
die() { echo "$(timestamp) accept-evidence: $*" >&2; exit 2; }
refuse() { echo "$(timestamp) accept-evidence: REFUSE: $*"; exit 1; }

if [ "$#" -lt 1 ]; then
  echo "usage: accept-evidence.sh <evidence-file> [--repo <repo-path>]" >&2
  exit 2
fi

evidence_file="$1"
repo_root="$(git rev-parse --show-toplevel)"
if [ "$#" -ge 3 ] && [ "$2" = "--repo" ]; then
  repo_root="$3"
fi

if [ ! -f "$evidence_file" ]; then
  die "evidence file not found: $evidence_file"
fi

# Parse Evidence block
parse_evidence() {
  local file="$1"
  # Simple parsing: look for lines like "KEY: VALUE" or "KEY: value1; value2"
  sed -n '/^## Evidence$/,/^$/p' "$file"
}

get_field() {
  local text="$1"
  local key="$2"
  echo "$text" | grep "^${key}:" | head -1 | sed "s/^${key}: *//" || true
}

get_multiline_field() {
  local text="$1"
  local key="$2"
  echo "$text" | sed -n "/^${key}:/p" | sed "s/^${key}: *//" || true
}

evidence_text=$(parse_evidence "$evidence_file")
if [ -z "$evidence_text" ]; then
  die "no Evidence block found in $evidence_file"
fi

CANDIDATE_SHA=$(get_field "$evidence_text" "CANDIDATE_SHA")
BASE_SHA=$(get_field "$evidence_text" "BASE_SHA")
BRANCH=$(get_field "$evidence_text" "BRANCH")
FILES=$(get_field "$evidence_text" "FILES")
WITHOUT_IT_COMMAND=$(get_multiline_field "$evidence_text" "WITHOUT_IT_COMMAND")
WITHOUT_IT_REMOVED_VARIANT=$(get_multiline_field "$evidence_text" "WITHOUT_IT_REMOVED_VARIANT")
WITHOUT_IT_OBSERVED=$(get_field "$evidence_text" "WITHOUT_IT_OBSERVED")

if [ -z "$CANDIDATE_SHA" ] || [ -z "$BASE_SHA" ] || [ -z "$WITHOUT_IT_COMMAND" ] || [ -z "$WITHOUT_IT_REMOVED_VARIANT" ]; then
  die "incomplete Evidence block: missing required fields"
fi

echo "$(timestamp) checking Evidence block: CANDIDATE=$CANDIDATE_SHA BASE=$BASE_SHA"

# AC-4: Verify CANDIDATE_SHA is a valid commit
echo "$(timestamp) checking AC-4: CANDIDATE_SHA is valid"
if ! git -C "$repo_root" rev-parse --verify "${CANDIDATE_SHA}^{commit}" >/dev/null 2>&1; then
  refuse "CANDIDATE_SHA unreachable: $CANDIDATE_SHA"
fi
echo "$(timestamp) AC-4 PASS: CANDIDATE_SHA is valid and reachable"

# If BRANCH is specified, additionally verify it matches remote head (if branch exists)
if [ -n "$BRANCH" ]; then
  remote_head=$(git -C "$repo_root" ls-remote origin "$BRANCH" 2>/dev/null | awk '{print $1}' || true)
  if [ -n "$remote_head" ]; then
    if [ "$CANDIDATE_SHA" != "$remote_head" ]; then
      refuse "CANDIDATE_SHA $CANDIDATE_SHA does not match remote head $remote_head for branch $BRANCH"
    fi
    echo "$(timestamp) AC-4: branch $BRANCH HEAD is $remote_head (matches CANDIDATE_SHA)"
  else
    echo "$(timestamp) AC-4: branch $BRANCH not found on remote (likely deleted after merge)"
  fi
fi

# Extract paths that WITHOUT_IT_COMMAND reads
# Look for file paths in the command that look like they exist in the repo
extract_command_paths() {
  local cmd="$1"
  local repo_root="$2"

  # Extract paths from common patterns:
  # - grep/test/find <path>
  # - git show <sha>:<path>
  # - Explicit file paths

  local paths=()

  # Extract git show <sha>:<path> patterns
  while read -r path; do
    [ -n "$path" ] && paths+=("$path")
  done < <(echo "$cmd" | grep -oE 'git show [^:]+:([^ ]+)' | sed 's/git show [^:]*://g' || true)

  # Extract grep/test/find file arguments
  # Look for patterns like: grep "pattern" file.txt
  while read -r path; do
    [ -n "$path" ] && [ "$path" != "-q" ] && paths+=("$path")
  done < <(echo "$cmd" | grep -oE '(grep|test|find) [^&|;]*' | sed 's/^grep[^"]* \|^test[^"]*[)]//' | tr ' ' '\n' | grep -E '\.(py|md|sh|json|yaml|yml|txt)$' || true)

  # Print unique paths
  printf '%s\n' "${paths[@]}" | sort -u
}

# Extract paths that WITHOUT_IT_REMOVED_VARIANT restores
extract_variant_paths() {
  local variant="$1"

  # Look for git show <sha>:<path> or git rm patterns
  local paths=()

  while read -r path; do
    [ -n "$path" ] && paths+=("$path")
  done < <(echo "$variant" | grep -oE 'git show [^:]+:([^ ]+)' | sed 's/git show [^:]*://g' || true)

  while read -r path; do
    [ -n "$path" ] && paths+=("$path")
  done < <(echo "$variant" | grep -oE 'git rm[^&|;]*' | grep -oE '[^ ]+$' || true)

  printf '%s\n' "${paths[@]}" | sort -u
}

echo "$(timestamp) checking AC-3: static path consistency"
command_paths=$(extract_command_paths "$WITHOUT_IT_COMMAND" "$repo_root")
variant_paths=$(extract_variant_paths "$WITHOUT_IT_REMOVED_VARIANT")

if [ -z "$command_paths" ]; then
  echo "$(timestamp) AC-3 SKIP: cannot extract paths from WITHOUT_IT_COMMAND"
else
  # Check that every path the command reads is restored by the variant
  unrestored_paths=()
  while read -r path; do
    if ! echo "$variant_paths" | grep -q "^${path}$"; then
      unrestored_paths+=("$path")
    fi
  done < <(echo "$command_paths")

  if [ "${#unrestored_paths[@]}" -gt 0 ]; then
    refuse "AC-3: WITHOUT_IT_COMMAND reads paths not restored by WITHOUT_IT_REMOVED_VARIANT: $(IFS=, ; echo "${unrestored_paths[*]}")"
  fi
  echo "$(timestamp) AC-3 PASS: all command paths are restored by variant"
fi

# AC-1: Run WITHOUT_IT_COMMAND at BASE_SHA and verify it exits non-zero
echo "$(timestamp) checking AC-1: WITHOUT_IT_COMMAND exits non-zero at BASE_SHA $BASE_SHA"

# Verify BASE_SHA exists
if ! git -C "$repo_root" rev-parse --verify "${BASE_SHA}^{commit}" >/dev/null 2>&1; then
  refuse "BASE_SHA unreachable: $BASE_SHA"
fi

# Create temporary worktree
worktree_dir=$(mktemp -d)
cleanup() {
  git -C "$repo_root" worktree remove --force "$worktree_dir" >/dev/null 2>&1 || true
  rm -rf "$worktree_dir" >/dev/null 2>&1 || true
}
trap cleanup EXIT

git -C "$repo_root" worktree add --detach --quiet "$worktree_dir" "$BASE_SHA"
echo "$(timestamp) created worktree at $worktree_dir for BASE_SHA"

# Run the command at BASE_SHA
set +e
(cd "$worktree_dir" && bash -c "$WITHOUT_IT_COMMAND" >/dev/null 2>&1)
base_exit_code=$?
set -e

echo "$(timestamp) WITHOUT_IT_COMMAND at BASE_SHA exited $base_exit_code"

if [ "$base_exit_code" -eq 0 ]; then
  refuse "AC-1: WITHOUT_IT_COMMAND already exits 0 at BASE_SHA $BASE_SHA - pair cannot fail"
fi

echo "$(timestamp) AC-1 PASS: WITHOUT_IT_COMMAND exits non-zero at BASE_SHA (exit code $base_exit_code)"

# If all checks pass, accept
echo "$(timestamp) accept-evidence: ACCEPT"
exit 0
