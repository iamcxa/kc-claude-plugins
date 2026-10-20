#!/usr/bin/env bash
# Check AC-11 from GitHub's side with the App token: one ops/* branch, one new task, one Draft PR, default branch untouched.
set -uo pipefail
: "${OWNER_REPO:?}" "${SLUG:?}" "${GH_TOKEN:=${OPS_APP_TOKEN:?}}"
API=${API_URL:-https://api.github.com}
get() { curl -sS -H "Authorization: Bearer $GH_TOKEN" -H "Accept: application/vnd.github+json" "$API/repos/$OWNER_REPO$1"; }
fails=0
chk() { if [ "$1" = ok ]; then echo "PASS AC-11 $2"; else echo "FAIL AC-11 $2"; fails=$((fails + 1)); fi; }
get "/pulls?state=open&head=${OWNER_REPO%%/*}:ops/$SLUG" | python3 -I -c '
import json,sys
p=json.load(sys.stdin)
print(len(p), p[0]["number"] if p else "", p[0]["draft"] if p else "", p[0]["user"]["login"] if p else "")' > /tmp/verify.$$
read -r COUNT NUM DRAFT AUTHOR < /tmp/verify.$$; rm -f /tmp/verify.$$
[ "$COUNT" = 1 ] && [ "$DRAFT" = True ] && chk ok "one open Draft PR #$NUM from ops/$SLUG by $AUTHOR" || chk bad "open PRs from ops/$SLUG: count=$COUNT draft=$DRAFT"
get "/compare/master...ops/$SLUG" | python3 -I -c '
import json,sys
d=json.load(sys.stdin)
print(" ".join(f["filename"] for f in d.get("files",[])))' > /tmp/verify.$$
FILES=$(cat /tmp/verify.$$); rm -f /tmp/verify.$$
TASKS=0; OUTSIDE=0
for f in $FILES; do
  case "$f" in "docs/ops/$SLUG.md") TASKS=$((TASKS + 1)) ;; docs/ops/*) ;; *) OUTSIDE=$((OUTSIDE + 1)) ;; esac
done
if [ "$TASKS" = 1 ] && [ "$OUTSIDE" = 0 ]; then chk ok "exactly one task file docs/ops/$SLUG.md, nothing outside docs/ops/ ($(echo $FILES | wc -w | tr -d ' ') files)"; else chk bad "task files=$TASKS outside=$OUTSIDE :: $FILES"; fi
exit $((fails > 0))
