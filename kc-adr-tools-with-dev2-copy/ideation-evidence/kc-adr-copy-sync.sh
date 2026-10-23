#!/usr/bin/env bash
# kc-adr-copy-sync.sh sync|check
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
pairs=(
  "kc-adr/references/adr-template.md kc-dev-flow-2/references/adr-template.md"
  "kc-adr/scripts/adr_lint.py kc-dev-flow-2/scripts/adr_lint.py"
  "kc-adr/skills/read-adr kc-dev-flow-2/skills/read-adr"
)
mode=${1:-check}
bad=0
for pair in "${pairs[@]}"; do
  read -r src dst <<<"$pair"
  case "$mode" in
    sync) rm -rf "${root:?}/$dst"; cp -R "$root/$src" "$root/$dst" ;;
    check)
      if [ ! -e "$root/$src" ] || [ ! -e "$root/$dst" ] || ! diff -rq "$root/$src" "$root/$dst" >/dev/null 2>&1; then
        echo "$dst differs from $src. Edit $src (kc-adr is the source), run scripts/kc-adr-copy-sync.sh sync, and commit both plugins' files." >&2
        bad=1
      fi ;;
    *) echo "usage: kc-adr-copy-sync.sh sync|check" >&2; exit 2 ;;
  esac
done
exit $bad
