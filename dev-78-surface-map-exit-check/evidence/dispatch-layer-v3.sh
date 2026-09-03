#!/usr/bin/env bash
# dispatch-layer.sh <ISSUE_ID> <DISPATCH_DIR> -> claim first, carrier branch, workspace, wait ready+idle, send task with token, require token read-back
set -euo pipefail; ID=$1; D=$2; R=$(git rev-parse --show-toplevel); CAR=poc/dispatch-carrier-$(echo $ID | tr 'A-Z' 'a-z'); TOKEN=$(python3 -c "import secrets; print(secrets.token_hex(8))")
mkdir -p /tmp/poc3/claims; printf 'issue=%s token=%s claimed_at=%s\n' "$ID" "$TOKEN" "$(date -u +%FT%TZ)" > /tmp/poc3/claims/$ID
sed "s/__TOKEN__/$TOKEN/" "$D/dispatch.md" > "$D/dispatch.tok.md"
WT=$(mktemp -d /tmp/poc3/carrier-XXXX); git -C "$R" worktree add -q "$WT" -b "$CAR" origin/main; cp "$D/dispatch.tok.md" "$WT/DISPATCH.md"; git -C "$WT" add DISPATCH.md; git -C "$WT" -c user.name=Kent -c user.email=duckbaseco@gmail.com commit -q -m "chore(poc): dispatch carrier for $ID (throwaway)"; git -C "$WT" push -q origin "$CAR"; git -C "$R" worktree remove --force "$WT"
PID=$(conductor project list --limit 100 --json | python3 -c "import json,sys; print(next(p['id'] for p in json.load(sys.stdin)['data'] if (p.get('gitRemote') or '').endswith('/iamcxa/kc-claude-plugins')))")
printf '%s' 'Wait for the next message before doing anything. Reply only: ready' > "$D/hello.txt"
conductor workspace create --project-id "$PID" --branch main --name "worker $ID" --agent claude --model sonnet-5-1m --effort high --message-file "$D/hello.txt" --json > "$D/create.json"
WID=$(python3 -c "import json; print(json.load(open('$D/create.json'))['workspaceId'])"); SID=$(python3 -c "import json; print(json.load(open('$D/create.json'))['sessionId'])")
printf 'workspace=%s session=%s carrier=%s dispatched_at=%s\n' "$WID" "$SID" "$CAR" "$(date -u +%FT%TZ)" >> /tmp/poc3/claims/$ID
for i in $(seq 1 30); do sleep 10; W=$(conductor workspace status "$WID" --json | python3 -c "import json,sys; print(json.load(sys.stdin).get('status'))"); S=$(conductor session status "$SID" --json | python3 -c "import json,sys; print(json.load(sys.stdin)['status'])"); [ "$W" = ready ] && [ "$S" = idle ] && break; done
printf 'DISPATCH_TOKEN %s\n\nYour full task is committed on a branch. Run exactly:\n\ngit fetch origin %s && git show origin/%s:DISPATCH.md\n\nThen follow DISPATCH.md from Step 1 to Step 5 exactly as written. Do not open a pull request. Do not push to any branch other than the one DISPATCH.md names. Your final message must be only the Evidence block DISPATCH.md specifies, and its DISPATCH_TOKEN line must repeat the token above.\n' "$TOKEN" "$CAR" "$CAR" > "$D/go.txt"
conductor message create --session "$SID" --message-file "$D/go.txt" --json > "$D/go.json"; printf 'task_sent_at=%s\n' "$(date -u +%FT%TZ)" >> /tmp/poc3/claims/$ID
# token read-back: the task text must appear in the transcript
for i in $(seq 1 12); do sleep 10; if conductor sql "SELECT transcript FROM session_transcripts_view WHERE session_id='$SID'" --json 2>/dev/null | grep -q "DISPATCH_TOKEN $TOKEN"; then printf 'task_acked_at=%s\n' "$(date -u +%FT%TZ)" >> /tmp/poc3/claims/$ID; echo "ACKED"; break; fi; done
grep -q task_acked_at /tmp/poc3/claims/$ID || { echo "NOT ACKED after 120s: resend once"; conductor message create --session "$SID" --message-file "$D/go.txt" --json > "$D/go2.json"; printf 'task_resent_at=%s\n' "$(date -u +%FT%TZ)" >> /tmp/poc3/claims/$ID; }
cat /tmp/poc3/claims/$ID
