#!/usr/bin/env bash

# Validate path/session identifiers and reject filesystem/shell normalization collisions.
# Compatible with Bash 3.2 shipped by macOS.

set -u
export LC_ALL=C

if [ "$#" -eq 0 ]; then
  printf '%s\n' 'At least one trace identifier is required' >&2
  exit 64
fi

seen_canonical='|'
for identifier in "$@"; do
  case "$identifier" in
    ''|[!A-Za-z0-9]*|*[!A-Za-z0-9._-]*)
      printf 'Unsafe trace identifier: %s\n' "$identifier" >&2
      exit 64
      ;;
  esac
  if [ "${#identifier}" -gt 64 ]; then
    printf 'Trace identifier exceeds 64 bytes: %s\n' "$identifier" >&2
    exit 64
  fi

  # macOS filesystems are commonly case-insensitive. Treat dot/dash/underscore
  # as one separator class so later variable/path normalization cannot collide.
  canonical=$(printf '%s' "$identifier" | tr '[:upper:].-' '[:lower:]__')
  case "$seen_canonical" in
    *"|$canonical|"*)
      printf 'Trace identifier normalization collision: %s\n' "$identifier" >&2
      exit 65
      ;;
  esac
  seen_canonical="${seen_canonical}${canonical}|"
done

exit 0
