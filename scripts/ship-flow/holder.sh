#!/usr/bin/env bash
# Writer fence for ship-flow external actions.
# Usage:
#   holder.sh claim    <state-dir> <holder-id>    -> become writer if none, print number
#   holder.sh handover <state-dir> <holder-id>    -> increment writer number, become writer, push
#   holder.sh check    <state-dir> <holder-id> <number>  -> exit 0 iff <number> is current AND holder matches; else exit 1 "fenced"
# The record is docs/dev/.spacedock-state/_holder.json committed on the state branch. A check always fetches first;
# the remote record is the authority, never the local file, so a resumed stale holder cannot pass on its own copy.
set -euo pipefail
cmd=$1; state=$2; holder=$3; rec="$state/_holder.json"; branch=spacedock-state/dev
sync_in() { git -C "$state" fetch -q origin "$branch" && git -C "$state" merge -q --ff-only FETCH_HEAD 2>/dev/null || true; }
read_rec() { [ -f "$rec" ] && python3 -c "import json;d=json.load(open('$rec'));print(d['writer'],d['holder'])" || echo "0 none"; }
write_rec() { python3 -c "import json,sys,time;json.dump({'writer':int(sys.argv[1]),'holder':sys.argv[2],'at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())},open('$rec','w'),indent=1)" "$1" "$2"; git -C "$state" add _holder.json; git -C "$state" -c user.name=holder -c user.email=holder@local commit -q -m "holder: writer $1 -> $2"; git -C "$state" push -q origin HEAD:"$branch"; }
case "$cmd" in
  claim)    sync_in; read w h < <(read_rec); if [ "$w" = 0 ]; then write_rec 1 "$holder"; echo 1; else echo "held by $h at $w" >&2; exit 1; fi ;;
  handover) sync_in; read w h < <(read_rec); n=$((w+1)); write_rec "$n" "$holder"; echo "$n" ;;
  check)    num=$4; sync_in; read w h < <(read_rec); if [ "$w" = "$num" ] && [ "$h" = "$holder" ]; then exit 0; else echo "fenced: current writer $w ($h), caller $num ($holder)" >&2; exit 1; fi ;;
  *) echo "usage: holder.sh claim|handover|check <state-dir> <holder-id> [number]" >&2; exit 2 ;;
esac
