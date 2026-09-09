#!/usr/bin/env bash
# Prove a named CI check actually runs a monorepo package before a merge
# verdict is allowed to call that check the gate. See
# kc-ship-flow/references/stations/ci-covers.md.
#
# Usage: ci-covers.sh <repo-root> <package-path> <check-name>
#
# Text/grep match against .github/workflows/*.yml|*.yaml only -- no YAML
# parser, so this proves job/step naming and directory entry, not full
# workflow semantics.
#
# Exit codes: 0 one workflow both (a) names <check-name> as a job id, a
# job `name:`, or a step `name:`, and (b) that same workflow enters
# <package-path> (a `working-directory: <package-path>` line, a `cd
# <package-path>` line, a `--filter <manifest-name>` line using
# <package-path>/package.json's `name`, or a `paths:` filter entry
# matching `<package-path>/**`); 1 no workflow satisfies both, printing
# "<package-path> not run by <check-name>" naming which of (a)/(b) failed;
# 2 a usage error.
set -euo pipefail
shopt -s nullglob

die() {
  local code="$1"
  shift
  echo "$*" >&2
  exit "$code"
}

[ "$#" -eq 3 ] || die 2 "usage: ci-covers.sh <repo-root> <package-path> <check-name>"

repo_root="$1"
package_path="$2"
check_name="$3"

[ -d "$repo_root" ] || die 2 "usage: repo-root not a directory: $repo_root"

workflows_dir="$repo_root/.github/workflows"
[ -d "$workflows_dir" ] || die 1 "$package_path not run by $check_name (a: no .github/workflows/ directory under $repo_root)"

esc() { printf '%s' "$1" | sed -e 's/[.[\*^$/]/\\&/g'; }

manifest_name=""
manifest_file="$repo_root/$package_path/package.json"
if [ -f "$manifest_file" ]; then
  manifest_name="$(grep -m1 '"name"[[:space:]]*:' "$manifest_file" | sed -E 's/.*"name"[[:space:]]*:[[:space:]]*"([^"]*)".*/\1/')"
fi

escaped_check="$(esc "$check_name")"
escaped_package="$(esc "$package_path")"

name_matches_check() {
  local file="$1"
  grep -Eq "^[[:space:]]*-?[[:space:]]*name:[[:space:]]*[\"']?${escaped_check}[\"']?[[:space:]]*\$" "$file" && return 0
  grep -Eq "^[[:space:]]{2}${escaped_check}:[[:space:]]*\$" "$file" && return 0
  return 1
}

enters_package() {
  local file="$1"
  local matched=1
  grep -Eq "working-directory:[[:space:]]*[\"']?${escaped_package}[\"']?[[:space:]]*\$" "$file" && matched=0
  grep -Eq "[[:space:]]cd[[:space:]]+${escaped_package}([[:space:]/]|\$)" "$file" && matched=0
  if [ -n "$manifest_name" ]; then
    grep -Eq -- "--filter[[:space:]]+$(esc "$manifest_name")([[:space:]]|\$)" "$file" && matched=0
  fi
  grep -Eq "^[[:space:]]*-[[:space:]]*[\"']?${escaped_package}/\*\*[\"']?[[:space:]]*\$" "$file" && matched=0
  return "$matched"
}

found_name=0
found_covering=0
for wf in "$workflows_dir"/*.yml "$workflows_dir"/*.yaml; do
  [ -f "$wf" ] || continue
  if name_matches_check "$wf"; then
    found_name=1
    if enters_package "$wf"; then
      found_covering=1
      break
    fi
  fi
done

if [ "$found_covering" -eq 1 ]; then
  echo "$package_path run by $check_name"
  exit 0
fi

if [ "$found_name" -eq 0 ]; then
  die 1 "$package_path not run by $check_name (a: no job id, job name:, or step name: matches '$check_name' under $workflows_dir)"
fi

die 1 "$package_path not run by $check_name (b: '$check_name' named but no workflow step enters $package_path)"
