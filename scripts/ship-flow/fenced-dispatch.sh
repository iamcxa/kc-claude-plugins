#!/usr/bin/env bash
# One external action under the intent-commit order:
#   intent commit -> holder check -> conductor workspace create (once) -> token read-back -> holder check -> adopt/persist
# Usage: fenced-dispatch.sh <state-dir> <holder-id> <writer> <claim> [--no-intent] [--no-fence] [--pause-before-persist] [--delay-create N]
#   --no-intent           skip the intent commit (the without-it variant)
#   --no-fence            skip both holder checks
#   --pause-before-persist SIGSTOP self after create returns, before adopt (sleep-at-the-worst-moment)
#   --delay-create N      sleep N seconds before calling create (late-arrival variant)
set -uo pipefail
state=$1; holder=$2; num=$3; claim=$4; shift 4; INTENT=1; FENCE=1; PAUSE=0; DELAY=0
while [ $# -gt 0 ]; do case "$1" in --no-intent) INTENT=0;; --no-fence) FENCE=0;; --pause-before-persist) PAUSE=1;; --delay-create) DELAY=$2; shift;; esac; shift; done
here=$(dirname "$0"); mkdir -p /tmp/poc4/run; log=/tmp/poc4/run/$holder.log; ts(){ date -u +%FT%TZ; }
say(){ echo "$(ts) $holder#$num: $*" | tee -a "$log"; }
say "start intent=$INTENT fence=$FENCE claim=$claim"
TOKEN=$(python3 -c "import secrets; print(secrets.token_hex(6))")
if [ $INTENT = 1 ]; then
  "$here/intent.sh" commit "$state" "$claim" "$TOKEN" "$num" >>"$log" 2>&1 || { say "refused: intent exists for $claim (reconcile instead of create)"; exit 4; }
  say "intent committed token=$TOKEN"
else
  say "no-intent mode (without-it variant)"
fi
if [ $FENCE = 1 ]; then "$here/holder.sh" check "$state" "$holder" "$num" 2>>"$log" || { say "fenced before create, no external action"; exit 3; }; fi
[ "$DELAY" -gt 0 ] && { say "delaying create ${DELAY}s"; sleep "$DELAY"; }
PID=$(conductor project list --limit 100 --json | python3 -c "import json,sys; print(next(p['id'] for p in json.load(sys.stdin)['data'] if (p.get('gitRemote') or '').endswith('/iamcxa/kc-claude-plugins')))")
printf '%s' 'Reply only: ok' > /tmp/poc4/run/hello.txt
NAME="$claim-$TOKEN"; say "conductor workspace create name=$NAME"
OUT=$(conductor workspace create --project-id "$PID" --branch main --name "$NAME" --agent claude --model haiku-4-5 --effort low --message-file /tmp/poc4/run/hello.txt --json 2>&1)
WID=$(printf '%s' "$OUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['workspaceId'])" 2>/dev/null || echo CREATE_FAILED)
say "create returned $WID"
if [ $PAUSE = 1 ]; then say "SIGSTOP self before adopt"; kill -STOP $$; say "resumed"; fi
if [ $FENCE = 1 ]; then "$here/holder.sh" check "$state" "$holder" "$num" 2>>"$log" || { say "fenced after resume; NOT adopting $WID (intent stays unresolved for the new holder to reconcile)"; exit 3; }; fi
if [ $INTENT = 1 ]; then "$here/intent.sh" adopt "$state" "$claim" "$WID" >>"$log" 2>&1 && say "adopted $WID" || { say "adopt failed"; exit 1; }
else echo "workspace=$WID holder=$holder writer=$num" >> "/tmp/poc4/run/claim-$claim.txt"; say "persisted (no-intent) $WID"; fi
exit 0
