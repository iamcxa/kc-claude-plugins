#!/usr/bin/env bash
# kc-adr-copy-sync.sh sync|check
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
pairs=(
  "kc-adr/references/adr-template.md kc-dev-flow-2/references/adr-template.md"
  "kc-adr/scripts/adr_lint.py kc-dev-flow-2/scripts/adr_lint.py"
)
mode=${1:-check}
bad=0
for pair in "${pairs[@]}"; do
  read -r src dst <<<"$pair"
  case "$mode" in
    sync) cp "$root/$src" "$root/$dst" ;;
    check)
      if ! cmp -s "$root/$src" "$root/$dst"; then
        echo "$dst differs from $src. Edit $src (kc-adr is the source), run scripts/kc-adr-copy-sync.sh sync, and commit both files." >&2
        bad=1
      fi ;;
    *) echo "usage: kc-adr-copy-sync.sh sync|check" >&2; exit 2 ;;
  esac
done
exit $bad
