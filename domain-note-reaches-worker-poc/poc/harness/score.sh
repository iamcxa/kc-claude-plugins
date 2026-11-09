#!/usr/bin/env bash
# Usage: score.sh <run-dir>. Reads transcript.jsonl and answer.md written by run.sh.
# read:    the transcript shows docs/domain/netlify.md being opened (any tool call or command naming it).
# applied: the answer names both address families for the browser cases.
set -euo pipefail
r="$1"
read=0; applied=0
if grep -q 'docs/domain/netlify\.md' "$r/transcript.jsonl" 2>/dev/null; then read=1; fi
a="$r/answer.md"
v4=0; v6=0
grep -q -E '127\.0\.0\.1|IPv4' "$a" && v4=1
grep -q -E '\[?::1\]?|IPv6' "$a" && v6=1
if [ "$v4" = 1 ] && [ "$v6" = 1 ]; then applied=1; fi
printf '%s\tread=%s\tapplied=%s\n' "$(basename "$r")" "$read" "$applied"
