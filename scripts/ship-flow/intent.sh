#!/usr/bin/env bash
# Durable dispatch intent on the state branch, written BEFORE any external call. Remote is the only authority.
# Usage:
#   intent.sh commit    <state-dir> <holder-id> <writer> <claim> <token>
#   intent.sh adopt     <state-dir> <holder-id> <writer> <claim> <workspace-id>   (fenced compare-and-swap: workspace must be null or this id)
#   intent.sh reconcile <state-dir> <holder-id> <writer>                            (adopt exactly one live workspace whose exact name is <claim>-<token>; else block)
#   intent.sh show      <state-dir> <claim>
# claim schema: ^[a-z0-9][a-z0-9.-]{2,63}$ (e.g. dev-84.g1). token: 32 hex (128-bit). All sync failures are fatal.
set -euo pipefail
cmd=${1:-}; state=${2:-}; branch=spacedock-state/dev; dir="$state/_intents"; here=$(cd "$(dirname "$0")" && pwd)
die() { echo "intent: $1" >&2; exit "${2:-1}"; }
ts() { date -u +%FT%TZ; }
sync_in() { [ -z "$(git -C "$state" status --porcelain)" ] || die "state checkout dirty" 6; git -C "$state" fetch -q origin "$branch" || die "fetch failed" 6; git -C "$state" merge -q --ff-only FETCH_HEAD || die "state branch diverged" 6; }
commit_push() { git -C "$state" add _intents; git -C "$state" -c user.name=intent -c user.email=intent@local commit -q -m "$1"; git -C "$state" push -q origin HEAD:"$branch" || die "push rejected; another writer moved the branch" 6; }
check_claim() { [[ "$1" =~ ^[a-z0-9][a-z0-9.-]{2,63}$ ]] || die "claim must match ^[a-z0-9][a-z0-9.-]{2,63}$" 2; }
check_token() { [[ "$1" =~ ^[0-9a-f]{32}$ ]] || die "token must be 32 hex" 2; }
fence() { "$here/holder.sh" check "$state" "$1" "$2" || die "fenced" 3; }
case "$cmd" in
  commit)
    holder=$3; writer=$4; claim=$5; token=$6; check_claim "$claim"; check_token "$token"; sync_in; fence "$holder" "$writer"; mkdir -p "$dir"; f="$dir/$claim.json"
    [ -f "$f" ] && die "intent exists for $claim ($(python3 -c "import json;print(json.load(open('$f')).get('workspace') or 'unresolved')")); reconcile, do not create" 4
    python3 -c "import json,sys;json.dump({'claim':sys.argv[1],'token':sys.argv[2],'writer':int(sys.argv[3]),'holder':sys.argv[4],'workspace':None,'committed_at':sys.argv[5]},open(sys.argv[6],'w'),indent=1)" "$claim" "$token" "$writer" "$holder" "$(ts)" "$f"
    commit_push "intent: $claim token=$token writer=$writer"; echo "committed $claim" ;;
  adopt)
    holder=$3; writer=$4; claim=$5; wid=$6; check_claim "$claim"; [[ "$wid" =~ ^[0-9a-f-]{36}$ ]] || die "workspace id must be a uuid" 2; sync_in; fence "$holder" "$writer"; f="$dir/$claim.json"; [ -f "$f" ] || die "no intent for $claim" 1
    cur=$(python3 -c "import json;print(json.load(open('$f')).get('workspace') or '')"); [ -z "$cur" ] || [ "$cur" = "$wid" ] || die "intent already adopted $cur; refusing to overwrite with $wid" 5
    python3 -c "import json,sys;d=json.load(open(sys.argv[1]));d['workspace']=sys.argv[2];d['adopted_at']=sys.argv[3];d['adopted_by']=sys.argv[4];d['adopted_writer']=int(sys.argv[5]);json.dump(d,open(sys.argv[1],'w'),indent=1)" "$f" "$wid" "$(ts)" "$holder" "$writer"
    commit_push "intent: $claim adopted $wid by $holder#$writer"; echo "adopted $claim -> $wid" ;;
  reconcile)
    holder=$3; writer=$4; sync_in; fence "$holder" "$writer"; rc=0
    for f in "$dir"/*.json; do [ -f "$f" ] || continue
      read claim token wid < <(python3 -c "import json;d=json.load(open('$f'));print(d['claim'],d['token'],d.get('workspace') or '-')")
      [ "$wid" != "-" ] && { echo "$(ts) $claim: resolved ($wid)"; continue; }
      name="$claim-$token"; ids=$(conductor workspace list --name "$name" --limit 100 --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(' '.join(w['id'] for w in d['data'] if w['state']!='archived' and w['name']=='$name'))")
      n=$(echo $ids | wc -w | tr -d ' ')
      case "$n" in
        1) "$0" adopt "$state" "$holder" "$writer" "$claim" "$ids" >/dev/null && echo "$(ts) $claim: adopted $ids (exact name match)" || { echo "$(ts) $claim: adopt failed"; rc=1; } ;;
        0) echo "$(ts) $claim: unresolved intent, no live workspace named $name; BLOCK (do not create)"; rc=4 ;;
        *) echo "$(ts) $claim: ambiguous intent, $n live workspaces named $name: $ids; BLOCK"; rc=5 ;;
      esac
    done; exit $rc ;;
  show) claim=$3; check_claim "$claim"; sync_in; cat "$dir/$claim.json" 2>/dev/null || die "no intent for $claim" 1 ;;
  *) die "usage: intent.sh commit|adopt|reconcile|show ..." 2 ;;
esac
