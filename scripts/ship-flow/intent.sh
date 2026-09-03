#!/usr/bin/env bash
# Durable dispatch intent on the state branch. Written BEFORE any external call.
# Usage:
#   intent.sh commit    <state-dir> <claim> <token> <writer>   -> create _intents/<claim>.json, commit, push; exit 1 if one exists
#   intent.sh adopt     <state-dir> <claim> <workspace-id>     -> persist the workspace id under the intent
#   intent.sh reconcile <state-dir> <holder-id> <writer>        -> for each unresolved intent: list Conductor by token, adopt exactly one, else block
#   intent.sh show      <state-dir> <claim>
# The remote record is the authority: every subcommand fetches and ff-merges first.
set -euo pipefail
cmd=$1; state=$2; branch=spacedock-state/dev; dir="$state/_intents"
sync_in() { git -C "$state" fetch -q origin "$branch" && git -C "$state" merge -q --ff-only FETCH_HEAD 2>/dev/null || true; }
commit_push() { git -C "$state" add _intents; git -C "$state" -c user.name=intent -c user.email=intent@local commit -q -m "$1"; git -C "$state" push -q origin HEAD:"$branch"; }
ts() { date -u +%FT%TZ; }
case "$cmd" in
  commit)
    claim=$3; token=$4; writer=$5; sync_in; mkdir -p "$dir"; f="$dir/$claim.json"
    if [ -f "$f" ]; then echo "intent exists for $claim: $(python3 -c "import json;print(json.load(open('$f')).get('workspace') or 'unresolved')")" >&2; exit 1; fi
    python3 -c "import json,sys;json.dump({'claim':sys.argv[1],'token':sys.argv[2],'writer':int(sys.argv[3]),'workspace':None,'committed_at':sys.argv[4]},open(sys.argv[5],'w'),indent=1)" "$claim" "$token" "$writer" "$(ts)" "$f"
    commit_push "intent: $claim token=$token writer=$writer"; echo "committed $claim $token" ;;
  adopt)
    claim=$3; wid=$4; sync_in; f="$dir/$claim.json"; [ -f "$f" ] || { echo "no intent for $claim" >&2; exit 1; }
    python3 -c "import json,sys;d=json.load(open(sys.argv[1]));d['workspace']=sys.argv[2];d['adopted_at']=sys.argv[3];json.dump(d,open(sys.argv[1],'w'),indent=1)" "$f" "$wid" "$(ts)"
    commit_push "intent: $claim adopted $wid"; echo "adopted $claim -> $wid" ;;
  reconcile)
    holder=$3; writer=$4; sync_in; here=$(dirname "$0")
    "$here/holder.sh" check "$state" "$holder" "$writer" || { echo "reconcile refused: fenced" >&2; exit 3; }
    rc=0
    for f in "$dir"/*.json; do [ -f "$f" ] || continue
      claim=$(python3 -c "import json;print(json.load(open('$f'))['claim'])"); wid=$(python3 -c "import json;print(json.load(open('$f')).get('workspace') or '')"); token=$(python3 -c "import json;print(json.load(open('$f'))['token'])")
      [ -n "$wid" ] && { echo "$(ts) $claim: resolved ($wid)"; continue; }
      ids=$(conductor workspace list --name "$token" --limit 20 --json | python3 -c "import json,sys; print(' '.join(w['id'] for w in json.load(sys.stdin)['data'] if w['state']!='archived' and '$token' in w['name']))")
      n=$(echo $ids | wc -w | tr -d ' ')
      case "$n" in
        1) "$0" adopt "$state" "$claim" "$ids" >/dev/null; echo "$(ts) $claim: adopted $ids (found by token)" ;;
        0) echo "$(ts) $claim: unresolved intent, no workspace carries token $token; BLOCK (do not create)"; rc=4 ;;
        *) echo "$(ts) $claim: ambiguous intent, $n workspaces carry token $token: $ids; BLOCK"; rc=5 ;;
      esac
    done; exit $rc ;;
  show) claim=$3; sync_in; cat "$dir/$claim.json" 2>/dev/null || { echo "no intent for $claim" >&2; exit 1; } ;;
  *) echo "usage: intent.sh commit|adopt|reconcile|show ..." >&2; exit 2 ;;
esac
