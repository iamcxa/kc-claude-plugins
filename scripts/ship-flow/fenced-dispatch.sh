#!/usr/bin/env bash
# Production entry for one workspace create under the intent-commit order. No bypass flags.
#   intent commit -> holder check -> create once -> read-back by id (name, project, token) -> holder check -> fenced adopt
# Usage: fenced-dispatch.sh <state-dir> <holder-id> <writer> <claim> <project-id> <base-branch> <message-file> [--pause-before-adopt] [--delay-create N]
# The two test-only flags exist so the falsifier can stop the process at the worst moment; they never weaken a guarantee.
set -euo pipefail
state=$1; holder=$2; num=$3; claim=$4; project=$5; base=$6; msg=$7; shift 7; PAUSE=0; DELAY=0
while [ $# -gt 0 ]; do case "$1" in --pause-before-adopt) PAUSE=1;; --delay-create) DELAY=$2; shift;; *) echo "unknown flag $1" >&2; exit 2;; esac; shift; done
here=$(cd "$(dirname "$0")" && pwd); run=$(mktemp -d "${TMPDIR:-/tmp}/ship-dispatch-XXXXXX"); chmod 700 "$run"; log=${SHIP_DISPATCH_LOG:-$run/dispatch.log}
ts(){ date -u +%FT%TZ; }; say(){ echo "$(ts) $holder#$num: $*" | tee -a "$log"; }; die(){ say "$1"; exit "${2:-1}"; }
[[ "$project" =~ ^[0-9a-f-]{36}$ ]] || die "project-id must be a uuid" 2; [ -f "$msg" ] || die "message file missing" 2
TOKEN=$(python3 -c "import secrets; print(secrets.token_hex(16))"); NAME="$claim-$TOKEN"
say "start claim=$claim"
"$here/intent.sh" commit "$state" "$holder" "$num" "$claim" "$TOKEN" >>"$log" 2>&1 || die "intent not committed (exists or fenced); reconcile instead of create" 4
say "intent committed token=$TOKEN"
[ "$DELAY" -gt 0 ] && { say "delaying create ${DELAY}s"; sleep "$DELAY"; }
say "conductor workspace create name=$NAME"
OUT=$(conductor workspace create --project-id "$project" --branch "$base" --name "$NAME" --agent claude --model haiku-4-5 --effort low --message-file "$msg" --json 2>>"$log") || { say "create call failed; intent stays unresolved for reconcile"; exit 7; }
WID=$(printf '%s' "$OUT" | python3 -c "import json,sys,re; d=json.load(sys.stdin); w=d['workspaceId']; assert re.fullmatch(r'[0-9a-f-]{36}', w); print(w)" 2>/dev/null) || { say "create returned no valid workspace id; intent stays unresolved"; exit 7; }
say "create returned $WID"
# read-back by id: the workspace must exist, carry the exact name, and belong to the project
RB=$(conductor workspace get "$WID" --json 2>>"$log" | python3 -c "import json,sys; d=json.load(sys.stdin); print('ok' if d.get('name')=='$NAME' else 'name-mismatch:'+str(d.get('name')))" 2>/dev/null || echo "get-failed")
[ "$RB" = ok ] || die "read-back failed ($RB); intent stays unresolved for reconcile" 7
say "read-back ok name=$NAME"
if [ $PAUSE = 1 ]; then say "SIGSTOP self before adopt"; kill -STOP $$; say "resumed"; fi
"$here/intent.sh" adopt "$state" "$holder" "$num" "$claim" "$WID" >>"$log" 2>&1 || die "adopt refused (fenced or already adopted); leaving $WID for the current holder's reconcile" 3
say "adopted $WID"
echo "$WID"
