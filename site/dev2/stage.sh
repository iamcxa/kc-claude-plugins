#!/bin/bash
# usage: stage.sh <out-dir>   copies kc-dev-flow-2 (without tests) and this site's config into an empty <out-dir>
set -euo pipefail
OUT=${1:?out dir}
HERE=$(cd "$(dirname "$0")" && pwd)
PKG=$(cd "$HERE/../../kc-dev-flow-2" && pwd)
mkdir -p "$OUT"
[ -z "$(ls -A "$OUT")" ] || { echo "stage.sh: $OUT is not empty" >&2; exit 1; }
rsync -a --exclude tests/ --exclude __pycache__/ --exclude 'test_*.py' "$PKG/" "$OUT/"
rsync -a --exclude stage.sh --exclude build.sh --exclude crawl.py "$HERE/" "$OUT/"
# A page without front matter reaches the search index as raw Markdown, backticks included.
find "$OUT" -name '*.md' -print0 | while IFS= read -r -d '' f; do
  [ "$(head -n1 "$f")" = "---" ] || { printf -- '---\n---\n' | cat - "$f" > "$f.tmp" && mv "$f.tmp" "$f"; }
done
