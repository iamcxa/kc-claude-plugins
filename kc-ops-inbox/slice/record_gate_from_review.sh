#!/usr/bin/env bash
# Record the ops gate only from the Captain's own GitHub review of the current head commit.
# usage: OWNER_REPO=o/r PR=N CAPTAIN=login WORKFLOW_DIR=docs/ops GH_API_TOKEN=... record_gate_from_review.sh
# Run from a checkout of the pull request's ops/<slug> branch. Prints no token.
set -euo pipefail
: "${OWNER_REPO:?}" "${PR:?}" "${CAPTAIN:?}" "${WORKFLOW_DIR:?}" "${GH_API_TOKEN:?}"
SD=${SPACEDOCK_BIN:-spacedock}
API=${API_URL:-https://api.github.com}
get() { curl -sSf -H "Authorization: Bearer $GH_API_TOKEN" -H "Accept: application/vnd.github+json" "$API/repos/$OWNER_REPO$1"; }

BRANCH=$(git rev-parse --abbrev-ref HEAD)
case "$BRANCH" in ops/*) SLUG=${BRANCH#ops/} ;; *) echo "refuse: branch $BRANCH is not ops/*" >&2; exit 1 ;; esac
HEAD_SHA=$(git rev-parse HEAD)

"$SD" status --workflow-dir "$WORKFLOW_DIR" --next --json | grep -q "\"slug\":\"$SLUG\".*\"readiness\":\"awaiting-captain\"" \
  || { echo "no-op: gate for $SLUG is not awaiting the Captain"; exit 0; }

get "/pulls/$PR/reviews?per_page=100" | python3 -I -c '
import json, sys
captain, head = sys.argv[1], sys.argv[2]
rows = [r for r in json.load(sys.stdin)
        if r["user"]["login"] == captain and r.get("commit_id") == head
        and r["state"] in ("APPROVED", "CHANGES_REQUESTED")]
if not rows:
    sys.exit(3)
r = rows[-1]
body = " ".join((r.get("body") or "").split())
print(r["id"], {"APPROVED": "approve", "CHANGES_REQUESTED": "revise"}[r["state"]], body or "(no comment)")
' "$CAPTAIN" "$HEAD_SHA" > /tmp/review.$$ || { echo "no-op: no review by $CAPTAIN on $HEAD_SHA"; rm -f /tmp/review.$$; exit 0; }
read -r RID DECISION WORDS < /tmp/review.$$; rm -f /tmp/review.$$

"$SD" gate record "$SLUG" --workflow-dir "$WORKFLOW_DIR" --decision "$DECISION" --actor person:captain \
  --reason "GitHub review $RID by $CAPTAIN on $HEAD_SHA: $WORDS"
"$SD" state commit "$SLUG" --workflow-dir "$WORKFLOW_DIR"
