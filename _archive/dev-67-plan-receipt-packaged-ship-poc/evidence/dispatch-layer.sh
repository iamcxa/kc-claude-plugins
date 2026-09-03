#!/usr/bin/env bash
# dispatch-layer.sh <ISSUE_ID> -> creates workspace with short hello, then sends "fetch carrier" message; carrier = committed branch poc/dev-67-carrier-<id>
set -euo pipefail; ID=$1; D=/tmp/poc2/$ID; R=$(git rev-parse --show-toplevel); CAR=poc/dev-67-carrier-$(echo $ID | tr 'A-Z' 'a-z')
# 1. claim first (durable, local)
mkdir -p /tmp/poc2/claims; printf 'issue=%s claimed_at=%s\n' "$ID" "$(date -u +%FT%TZ)" > /tmp/poc2/claims/$ID
# 2. carrier branch with the dispatch text
WT=$(mktemp -d /tmp/poc2/carrier-XXXX); git -C "$R" worktree add -q "$WT" -b "$CAR" origin/main; cp "$D/dispatch.md" "$WT/DISPATCH.md"; git -C "$WT" add DISPATCH.md; git -C "$WT" -c user.name=Kent -c user.email=duckbaseco@gmail.com commit -q -m "chore(poc): dev-67 dispatch carrier for $ID (throwaway)"; git -C "$WT" push -q origin "$CAR"; git -C "$R" worktree remove --force "$WT"
# 3. workspace
PID=$(conductor project list --limit 100 --json | python3 -c "import json,sys; print(next(p['id'] for p in json.load(sys.stdin)['data'] if (p.get('gitRemote') or '').endswith('/iamcxa/kc-claude-plugins')))")
printf '%s' 'Wait for the next message before doing anything. Reply only: ready' > "$D/hello.txt"
conductor workspace create --project-id "$PID" --branch main --name "dev-67 poc: worker $ID" --agent claude --model sonnet-5-1m --effort high --message-file "$D/hello.txt" --json > "$D/create.json"
WID=$(python3 -c "import json; print(json.load(open('$D/create.json'))['workspaceId'])"); SID=$(python3 -c "import json; print(json.load(open('$D/create.json'))['sessionId'])")
printf 'workspace=%s session=%s carrier=%s dispatched_at=%s\n' "$WID" "$SID" "$CAR" "$(date -u +%FT%TZ)" >> /tmp/poc2/claims/$ID
for i in $(seq 1 30); do sleep 10; W=$(conductor workspace status "$WID" --json | python3 -c "import json,sys; print(json.load(sys.stdin).get('status'))"); S=$(conductor session status "$SID" --json | python3 -c "import json,sys; print(json.load(sys.stdin)['status'])"); [ "$W" = ready ] && [ "$S" = idle ] && break; done; sleep 15
printf 'Your full task is committed on a branch. Run exactly:\n\ngit fetch origin %s && git show origin/%s:DISPATCH.md\n\nThen follow DISPATCH.md from Step 1 to Step 5 exactly as written. Do not open a pull request. Do not push to any branch other than the one DISPATCH.md names. Your final message must be only the Evidence block DISPATCH.md specifies.\n' "$CAR" "$CAR" > "$D/go.txt"
conductor message create --session "$SID" --message-file "$D/go.txt" --json > "$D/go.json"; printf 'task_sent_at=%s\n' "$(date -u +%FT%TZ)" >> /tmp/poc2/claims/$ID
cat /tmp/poc2/claims/$ID
