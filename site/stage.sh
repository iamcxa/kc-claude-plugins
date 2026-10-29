#!/bin/bash
# usage: stage.sh <out-dir>   copies every plugin with a site/<plugin>/nav.yml (without its tests) and this site's config into an empty <out-dir>
set -euo pipefail
OUT=${1:?out dir}
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)
mkdir -p "$OUT"
[ -z "$(ls -A "$OUT")" ] || { echo "stage.sh: $OUT is not empty" >&2; exit 1; }

PLUGINS=()
for nav in "$HERE"/*/nav.yml; do
  p=$(basename "$(dirname "$nav")")
  [ -f "$ROOT/$p/.claude-plugin/plugin.json" ] || { echo "stage.sh: site/$p has no plugin $p" >&2; exit 1; }
  grep -qF "\"$p/**\"" "$ROOT/.github/workflows/docs-site.yml" || { echo "stage.sh: docs-site.yml paths do not list $p/**" >&2; exit 1; }
  PLUGINS+=("$p")
done

cp "$HERE/_config.yml" "$OUT/"
rsync -a "$HERE/_sass" "$OUT/"
{
  echo "collections:"
  for p in "${PLUGINS[@]}"; do printf '  %s:\n    output: true\n    permalink: /:collection/:path:output_ext\n' "$p"; done
  echo "just_the_docs:"
  echo "  collections:"
  for p in "${PLUGINS[@]}"; do printf '    %s:\n      name: %s\n' "$p" "$p"; done
  echo "defaults:"
  printf '  - scope: { path: "" }\n    values: { layout: default }\n'
  for p in "${PLUGINS[@]}"; do sed -e "s#path: \"#path: \"_$p/#" -e 's/^/  /' "$HERE/$p/nav.yml"; done
} >> "$OUT/_config.yml"

for p in "${PLUGINS[@]}"; do
  rsync -a --exclude tests/ --exclude __pycache__/ --exclude 'test_*.py' "$ROOT/$p/" "$OUT/_$p/"
  rsync -a --exclude nav.yml "$HERE/$p/" "$OUT/_$p/"
done

python3 - "$ROOT" "${PLUGINS[@]}" > "$OUT/index.md" <<'EOF'
import json, sys
root, plugins = sys.argv[1], sys.argv[2:]
print("---\ntitle: Home\nnav_order: 1\npermalink: /\n---\n\n# kc-claude-plugins\n")
for p in plugins:
    desc = json.load(open(f"{root}/{p}/.claude-plugin/plugin.json")).get("description", "")
    print(f"- [{p}]({p}/) — {desc}")
EOF

# A page without front matter reaches the search index as raw Markdown, backticks included.
# kramdown swallows a table or list that touches a comment-only line; GitHub does not.
find "$OUT" -name '*.md' -print0 | while IFS= read -r -d '' f; do
  [ "$(head -n1 "$f")" = "---" ] || { printf -- '---\n---\n' | cat - "$f" > "$f.tmp" && mv "$f.tmp" "$f"; }
  awk '/^<!--.*-->$/ { print ""; print; print ""; next } { print }' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
done
