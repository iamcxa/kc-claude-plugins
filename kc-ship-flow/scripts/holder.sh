#!/usr/bin/env bash
# Writer fence for ship-flow external actions. The remote state branch is the only authority.
# Usage:
#   holder.sh claim    <state-dir> <holder-id>
#   holder.sh handover <state-dir> <holder-id>
#   holder.sh check    <state-dir> <holder-id> <writer>
# Every subcommand syncs first and FAILS CLOSED on any fetch, non-fast-forward, dirty tree, or malformed record.
set -euo pipefail
cmd=${1:-}; state=${2:-}; holder=${3:-}; branch=spacedock-state/dev; rec="$state/_holder.json"
die() { echo "holder: $*" >&2; exit "${2:-1}"; }
sync_in() {
  [ -z "$(git -C "$state" status --porcelain)" ] || die "state checkout dirty; refusing" 6
  git -C "$state" fetch -q origin "$branch" || die "fetch failed; refusing to act on local state" 6
  git -C "$state" merge -q --ff-only FETCH_HEAD || die "state branch diverged (non-fast-forward); refusing" 6
}
read_rec() { [ -f "$rec" ] || { echo "0 none"; return; }; python3 -c "import json,sys;d=json.load(open('$rec'));w=d['writer'];h=d['holder'];assert isinstance(w,int) and w>0 and isinstance(h,str) and h;print(w,h)" 2>/dev/null || die "malformed holder record" 6; }
write_rec() { python3 -c "import json,sys,time;json.dump({'writer':int(sys.argv[1]),'holder':sys.argv[2],'at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())},open('$rec','w'),indent=1)" "$1" "$2"; git -C "$state" add _holder.json; git -C "$state" -c user.name=holder -c user.email=holder@local commit -q -m "holder: writer $1 -> $2"; git -C "$state" push -q origin HEAD:"$branch" || die "push rejected (someone else moved the writer); refusing" 6; }
[[ "$holder" =~ ^[a-z0-9][a-z0-9-]{0,39}$ ]] || die "holder id must match ^[a-z0-9][a-z0-9-]{0,39}$" 2
case "$cmd" in
  claim)    sync_in; read w h < <(read_rec); [ "$w" = 0 ] || die "held by $h at $w"; write_rec 1 "$holder"; echo 1 ;;
  handover) sync_in; read w h < <(read_rec); n=$((w+1)); write_rec "$n" "$holder"; echo "$n" ;;
  check)    num=${4:-}; [[ "$num" =~ ^[0-9]+$ ]] || die "writer must be an integer" 2; sync_in; read w h < <(read_rec); [ "$w" = "$num" ] && [ "$h" = "$holder" ] || die "fenced: current writer $w ($h), caller $num ($holder)" 1 ;;
  *) die "usage: holder.sh claim|handover|check <state-dir> <holder-id> [writer]" 2 ;;
esac
