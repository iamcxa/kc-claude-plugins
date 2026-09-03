#!/usr/bin/env bash
# Durable dispatch intent on the state branch, written BEFORE any external call. Remote is the only authority.
# Usage:
#   intent.sh commit    <state-dir> <holder-id> <writer> <claim> <token> <project> <base> <message-sha256>
#   intent.sh adopt     <state-dir> <holder-id> <writer> <claim> <workspace-id>   (fenced compare-and-swap: workspace must be null or this id; blocks with "project mismatch" if the workspace's project differs from the intent's)
#   intent.sh reconcile <state-dir> <holder-id> <writer>                            (adopt exactly one live workspace whose exact name is <claim>-<token> and whose project matches the intent; else block)
#   intent.sh show      <state-dir> <claim>
# claim schema: ^[a-z0-9][a-z0-9.-]{2,63}$ (e.g. dev-84.g1). token: 32 hex (128-bit). project: uuid. message-sha256: 64 hex (sha256 of the exact message file handed to `conductor workspace create`). All sync failures are fatal.
# commit and adopt hold a portable mkdir-based lock at <state-dir>/.git/ship-lock.d across their whole sync -> write -> commit -> push sequence: two invocations on the same checkout serialize instead of racing `git add`/commit/push on the shared working tree. `mkdir` is the atomic acquire (POSIX-portable, no `flock`/`lockf`/GNU-only flags, so it works on the First Officer's macOS host too); the lock dir lives under .git (git metadata, not the working tree) so it never itself makes the checkout dirty. A trap removes the lock dir on every exit path (success, die, or an uncaught error under `set -e`), so a clean exit cannot leave it stuck; a lock dir older than 120s whose recorded pid is no longer alive is treated as abandoned by a crashed holder and is removed for one retry.
set -euo pipefail
cmd=${1:-}; state=${2:-}; branch=spacedock-state/dev; dir="$state/_intents"; here=$(cd "$(dirname "$0")" && pwd)
die() { echo "intent: $1" >&2; exit "${2:-1}"; }
ts() { date -u +%FT%TZ; }
lock() {
  # LOCK_DIR is deliberately a script-global, not a function-local: the EXIT trap below reads it by
  # name at trap-firing time, which can be well after this function has returned, and a `local` would
  # already be out of scope by then (an unbound-variable death under `set -u`, caught by the falsifier
  # that runs this with no `flock` on PATH).
  LOCK_DIR="$state/.git/ship-lock.d"
  local waited=0 since now age pid
  while ! mkdir "$LOCK_DIR" 2>/dev/null; do
    if [ -f "$LOCK_DIR/since" ]; then
      since=$(cat "$LOCK_DIR/since" 2>/dev/null || echo 0); now=$(date +%s); age=$((now - since))
      pid=$(cat "$LOCK_DIR/pid" 2>/dev/null || echo 0)
      if [ "$age" -gt 120 ] && ! kill -0 "$pid" 2>/dev/null; then
        rm -rf "$LOCK_DIR" 2>/dev/null
        mkdir "$LOCK_DIR" 2>/dev/null && break
      fi
    fi
    waited=$((waited + 1)); [ "$waited" -lt 150 ] || die "lock timeout on $LOCK_DIR" 6
    sleep 0.2
  done
  echo $$ >"$LOCK_DIR/pid"; date +%s >"$LOCK_DIR/since"
  trap 'rm -rf "$LOCK_DIR"' EXIT
}
sync_in() { [ -z "$(git -C "$state" status --porcelain)" ] || die "state checkout dirty" 6; git -C "$state" fetch -q origin "$branch" || die "fetch failed" 6; git -C "$state" merge -q --ff-only FETCH_HEAD || die "state branch diverged" 6; }
commit_push() { git -C "$state" add _intents; git -C "$state" -c user.name=intent -c user.email=intent@local commit -q -m "$1"; git -C "$state" push -q origin HEAD:"$branch" || die "push rejected; another writer moved the branch" 6; }
check_claim() { [[ "$1" =~ ^[a-z0-9][a-z0-9.-]{2,63}$ ]] || die "claim must match ^[a-z0-9][a-z0-9.-]{2,63}$" 2; }
check_token() { [[ "$1" =~ ^[0-9a-f]{32}$ ]] || die "token must be 32 hex" 2; }
check_uuid() { [[ "$1" =~ ^[0-9a-f-]{36}$ ]] || die "$2 must be a uuid" 2; }
check_sha256() { [[ "$1" =~ ^[0-9a-f]{64}$ ]] || die "message_sha256 must be 64 hex" 2; }
fence() { "$here/holder.sh" check "$state" "$1" "$2" || die "fenced" 3; }
workspace_project() { conductor workspace get "$1" --json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('projectId') or '')" 2>/dev/null || echo ""; }
case "$cmd" in
  commit)
    holder=$3; writer=$4; claim=$5; token=$6; project=$7; base=$8; msg_sha=$9
    check_claim "$claim"; check_token "$token"; check_uuid "$project" project; check_sha256 "$msg_sha"
    lock; sync_in; fence "$holder" "$writer"; mkdir -p "$dir"; f="$dir/$claim.json"
    [ -f "$f" ] && die "intent exists for $claim ($(python3 -c "import json;print(json.load(open('$f')).get('workspace') or 'unresolved')")); reconcile, do not create" 4
    python3 -c "import json,sys;json.dump({'claim':sys.argv[1],'token':sys.argv[2],'writer':int(sys.argv[3]),'holder':sys.argv[4],'project':sys.argv[5],'base':sys.argv[6],'message_sha256':sys.argv[7],'workspace':None,'committed_at':sys.argv[8]},open(sys.argv[9],'w'),indent=1)" "$claim" "$token" "$writer" "$holder" "$project" "$base" "$msg_sha" "$(ts)" "$f"
    commit_push "intent: $claim token=$token writer=$writer project=$project"; echo "committed $claim" ;;
  adopt)
    holder=$3; writer=$4; claim=$5; wid=$6; check_claim "$claim"; check_uuid "$wid" "workspace id"
    lock; sync_in; fence "$holder" "$writer"; f="$dir/$claim.json"; [ -f "$f" ] || die "no intent for $claim" 1
    cur=$(python3 -c "import json;print(json.load(open('$f')).get('workspace') or '')"); [ -z "$cur" ] || [ "$cur" = "$wid" ] || die "intent already adopted $cur; refusing to overwrite with $wid" 5
    iproj=$(python3 -c "import json;print(json.load(open('$f'))['project'])")
    wproj=$(workspace_project "$wid"); [ -n "$wproj" ] || die "could not read workspace $wid project; refusing to adopt" 7
    [ "$wproj" = "$iproj" ] || die "project mismatch: intent=$iproj workspace=$wproj; refusing to adopt $wid" 8
    python3 -c "import json,sys;d=json.load(open(sys.argv[1]));d['workspace']=sys.argv[2];d['adopted_at']=sys.argv[3];d['adopted_by']=sys.argv[4];d['adopted_writer']=int(sys.argv[5]);json.dump(d,open(sys.argv[1],'w'),indent=1)" "$f" "$wid" "$(ts)" "$holder" "$writer"
    commit_push "intent: $claim adopted $wid by $holder#$writer"; echo "adopted $claim -> $wid" ;;
  reconcile)
    holder=$3; writer=$4; sync_in; fence "$holder" "$writer"; rc=0
    for f in "$dir"/*.json; do [ -f "$f" ] || continue
      read claim token proj wid < <(python3 -c "import json;d=json.load(open('$f'));print(d['claim'],d['token'],d['project'],d.get('workspace') or '-')")
      [ "$wid" != "-" ] && { echo "$(ts) $claim: resolved ($wid)"; continue; }
      name="$claim-$token"
      name_ids=$(conductor workspace list --name "$name" --limit 100 --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(' '.join(w['id'] for w in d['data'] if w['state']!='archived' and w['name']=='$name'))")
      # Filter by project BEFORE counting: a same-name workspace in a different project must not make
      # this report "ambiguous intent" when exactly one live workspace actually matches this intent.
      ids=""
      for cid in $name_ids; do [ "$(workspace_project "$cid")" = "$proj" ] && ids="$ids $cid"; done
      ids=$(echo $ids)
      n=$(echo $ids | wc -w | tr -d ' ')
      case "$n" in
        1)
          errf=$(mktemp "${TMPDIR:-/tmp}/intent-reconcile-err-XXXXXX")
          if "$0" adopt "$state" "$holder" "$writer" "$claim" "$ids" >/dev/null 2>"$errf"; then
            echo "$(ts) $claim: adopted $ids (exact name match)"
          else
            arc=$?
            if [ "$arc" = 8 ]; then echo "$(ts) $claim: project mismatch on $ids ($(tail -1 "$errf")); BLOCK"; rc=8
            else echo "$(ts) $claim: adopt failed ($(tail -1 "$errf"))"; rc=1; fi
          fi
          rm -f "$errf" ;;
        0) echo "$(ts) $claim: unresolved intent, no live workspace named $name; BLOCK (do not create)"; rc=4 ;;
        *) echo "$(ts) $claim: ambiguous intent, $n live workspaces named $name: $ids; BLOCK"; rc=5 ;;
      esac
    done; exit $rc ;;
  show) claim=$3; check_claim "$claim"; sync_in; cat "$dir/$claim.json" 2>/dev/null || die "no intent for $claim" 1 ;;
  *) die "usage: intent.sh commit|adopt|reconcile|show ..." 2 ;;
esac
