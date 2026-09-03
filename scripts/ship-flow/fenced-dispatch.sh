#!/usr/bin/env bash
# One fenced external action: create a probe workspace only if holder.sh check passes.
# Usage: fenced-dispatch.sh <state-dir> <holder-id> <writer-number> <claim-name> [--no-fence] [--pause-before-persist]
# --pause-before-persist: after the create call returns, SIGSTOP self before writing the workspace id (the sleep-at-the-worst-moment falsifier).
set -uo pipefail
state=$1; holder=$2; num=$3; claim=$4; shift 4; FENCE=1; PAUSE=0
for a in "$@"; do [ "$a" = --no-fence ] && FENCE=0; [ "$a" = --pause-before-persist ] && PAUSE=1; done
here=$(dirname "$0"); log=/tmp/poc3/DEV-79/run-$holder.log; ts(){ date -u +%FT%TZ; }
echo "$(ts) $holder#$num: start fence=$FENCE" | tee -a "$log"
if [ $FENCE = 1 ]; then
  if ! "$here/holder.sh" check "$state" "$holder" "$num" 2>>"$log"; then echo "$(ts) $holder#$num: fenced, no external action" | tee -a "$log"; exit 3; fi
fi
PID=$(conductor project list --limit 100 --json | python3 -c "import json,sys; print(next(p['id'] for p in json.load(sys.stdin)['data'] if (p.get('gitRemote') or '').endswith('/iamcxa/kc-claude-plugins')))")
printf '%s' 'Reply only: ok' > /tmp/poc3/DEV-79/hello.txt
echo "$(ts) $holder#$num: conductor workspace create name=$claim" | tee -a "$log"
OUT=$(conductor workspace create --project-id "$PID" --branch main --name "$claim" --agent claude --model haiku-4-5 --effort low --message-file /tmp/poc3/DEV-79/hello.txt --json 2>&1)
WID=$(printf '%s' "$OUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['workspaceId'])" 2>/dev/null || echo "CREATE_FAILED")
echo "$(ts) $holder#$num: create returned $WID" | tee -a "$log"
if [ $PAUSE = 1 ]; then echo "$(ts) $holder#$num: SIGSTOP self before persisting id" | tee -a "$log"; kill -STOP $$; echo "$(ts) $holder#$num: resumed" | tee -a "$log"; fi
# persist is itself an external-ish action on the state branch: re-check the fence before writing the claim record
if [ $FENCE = 1 ] && ! "$here/holder.sh" check "$state" "$holder" "$num" 2>>"$log"; then echo "$(ts) $holder#$num: fenced after resume; NOT persisting $WID (orphan candidate: $WID)" | tee -a "$log"; echo "$WID" >> /tmp/poc3/DEV-79/orphans.txt; exit 3; fi
echo "workspace=$WID holder=$holder writer=$num at=$(ts)" >> "/tmp/poc3/DEV-79/claim-$claim.txt"
echo "$(ts) $holder#$num: persisted $WID" | tee -a "$log"; exit 0
