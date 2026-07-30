#!/usr/bin/env bash

# Add every generated E2E artifact rule without trusting one rule as a sentinel.
# Compatible with Bash 3.2 shipped by macOS.

set -u

usage() {
  printf '%s\n' \
    'Usage: ensure-e2e-gitignore.sh --project-root <absolute-directory>' \
    '   or: ensure-e2e-gitignore.sh --report-dir <absolute-report-directory>'
}

if [ "$#" -ne 2 ]; then
  usage >&2
  exit 64
fi

case "$1" in
  --project-root)
    project_root=$2
    ;;
  --report-dir)
    report_dir=$2
    case "$report_dir" in
      /*/.claude/e2e/reports/*)
        candidate_root=${report_dir%/.claude/e2e/reports/*}
        ;;
      *)
        printf 'Report directory must be absolute and below .claude/e2e/reports: %s\n' "$report_dir" >&2
        exit 64
        ;;
    esac
    if [ -z "$candidate_root" ]; then
      printf 'Cannot derive project root from report directory: %s\n' "$report_dir" >&2
      exit 64
    fi
    if git_root=$(git -C "$candidate_root" rev-parse --show-toplevel 2>/dev/null); then
      project_root=$git_root
    else
      project_root=$candidate_root
    fi
    ;;
  *)
    usage >&2
    exit 64
    ;;
esac

case "$project_root" in
  /*) ;;
  *)
    printf 'Project root must be absolute: %s\n' "$project_root" >&2
    exit 64
    ;;
esac
if [ ! -d "$project_root" ]; then
  printf 'Project root must be an existing directory: %s\n' "$project_root" >&2
  exit 64
fi

gitignore_path="$project_root/.gitignore"
if [ -L "$gitignore_path" ] ||
   { [ -e "$gitignore_path" ] && [ ! -f "$gitignore_path" ]; }; then
  printf 'Gitignore destination must be absent or a regular file: %s\n' "$gitignore_path" >&2
  exit 64
fi

if [ ! -e "$gitignore_path" ]; then
  : > "$gitignore_path" || exit 70
fi

needs_separator=0
if [ -s "$gitignore_path" ]; then
  last_byte=$(
    tail -c 1 "$gitignore_path" 2>/dev/null |
      od -An -tu1 |
      tr -d '[:space:]'
  )
  if [ "$last_byte" != "10" ]; then
    needs_separator=1
  fi
fi

while IFS= read -r artifact_pattern; do
  if ! grep -Fqx -- "$artifact_pattern" "$gitignore_path" 2>/dev/null; then
    if [ "$needs_separator" -eq 1 ]; then
      printf '\n' >> "$gitignore_path" || exit 70
      needs_separator=0
    fi
    printf '%s\n' "$artifact_pattern" >> "$gitignore_path" || exit 70
  fi
done <<'PATTERNS'
.claude/e2e/reports/**/*.webm
.claude/e2e/reports/**/*.mp4
.claude/e2e/reports/**/trace.zip
.claude/e2e/reports/**/trace.json
.claude/e2e/reports/**/trace.invalid-*.zip
.claude/e2e/reports/**/trace.invalid-*.json
.claude/e2e/reports/**/*.gif
PATTERNS
