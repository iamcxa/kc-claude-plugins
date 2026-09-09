#!/usr/bin/env bash
# Production entry for one workspace create under the intent-commit order. No bypass flags.
#   intent commit -> holder check -> create once -> read-back by id (name, project, token) -> holder check -> fenced adopt
# Usage: fenced-dispatch.sh <state-dir> <holder-id> <writer> <claim> <project-id> <base-branch>
#          --entity-path <dev-task> --stage <stage> [--workflow-dir <dir>] [--dry-run]
#          [--pause-before-adopt] [--delay-create N]
# This station does not author the message: it obtains it by running `spacedock dispatch build`
# against the dev entity's stage and hashes the artifact `spacedock` already wrote to disk. When
# `--workflow-dir` is omitted it defaults to a sibling directory named after the entity's own
# basename (`<entity-dir>/<entity-stem>/`) so each fixture entity carries its own stage definition.
# The two test-only flags exist so the falsifier can stop the process at the worst moment; they
# never weaken a guarantee.
set -euo pipefail
state=$1; holder=$2; num=$3; claim=$4; project=$5; base=$6; shift 6
entity=""; stage=""; workflow_dir=""; DRYRUN=0; PAUSE=0; DELAY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --entity-path) entity=$2; shift ;;
    --stage) stage=$2; shift ;;
    --workflow-dir) workflow_dir=$2; shift ;;
    --dry-run) DRYRUN=1 ;;
    --pause-before-adopt) PAUSE=1 ;;
    --delay-create) DELAY=$2; shift ;;
    *) echo "unknown flag $1" >&2; exit 2 ;;
  esac
  shift
done
here=$(cd "$(dirname "$0")" && pwd); run=$(mktemp -d "${TMPDIR:-/tmp}/ship-dispatch-XXXXXX"); chmod 700 "$run"; log=${SHIP_DISPATCH_LOG:-$run/dispatch.log}
ts(){ date -u +%FT%TZ; }; say(){ echo "$(ts) $holder#$num: $*" | tee -a "$log"; }; die(){ say "$1"; exit "${2:-1}"; }
[[ "$project" =~ ^[0-9a-f-]{36}$ ]] || die "project-id must be a uuid" 2
[ -n "$entity" ] || die "--entity-path is required" 2
[ -n "$stage" ] || die "--stage is required" 2
[ -f "$entity" ] || die "entity file missing: $entity" 2
if [ -z "$workflow_dir" ]; then
  entity_dir=$(cd "$(dirname "$entity")" && pwd); entity_stem=$(basename "$entity" .md)
  workflow_dir="$entity_dir/$entity_stem"
fi
[ -d "$workflow_dir" ] || die "workflow-dir missing: $workflow_dir" 2

# The checklist is procedural (follow the stage's own instructions), never the message: the
# message body -- the dev entity's actual work -- comes entirely from `dispatch build`'s reading
# of the entity file and the stage's README section, never from this station.
checklist="$run/checklist"
printf 'DONE: complete stage %s per the workflow'\''s own stage contract.\n' "$stage" >"$checklist"
build_out="$run/build.json"
say "spacedock dispatch build entity=$entity stage=$stage workflow-dir=$workflow_dir"
if ! spacedock dispatch build --workflow-dir "$workflow_dir" --entity-path "$entity" --stage "$stage" --checklist-file "$checklist" --host claude >"$build_out" 2>>"$log"; then
  die "dispatch build failed" 4
fi
dispatch_file=$(python3 -c "import json,sys; print(json.load(open('$build_out'))['dispatch_file_path'])") || die "dispatch build failed" 4
[ -f "$dispatch_file" ] || die "dispatch build failed" 4
MODEL=$(python3 -c "import json; print(json.load(open('$build_out')).get('model') or '')")
EFFORT=$(python3 -c "import json; print(json.load(open('$build_out')).get('effort') or '')")

TOKEN=$(python3 -c "import secrets; print(secrets.token_hex(16))"); NAME="$claim-$TOKEN"
# Copy the message into this run's private temp dir first and hash that copy: the hash bound into the
# intent and the bytes handed to `conductor workspace create` are then provably the same file, immune to
# the dispatch artifact's path being edited between intent-commit and create.
cp "$dispatch_file" "$run/message"; MSG_SHA=$(sha256sum "$run/message" | cut -d' ' -f1); msg="$run/message"

model_args=()
[ -n "$MODEL" ] && model_args+=(--model "$MODEL")
[ -n "$EFFORT" ] && model_args+=(--effort "$EFFORT")

if [ "$DRYRUN" = 1 ]; then
  printf 'conductor workspace create --project-id %s --branch %s --name %s --agent claude' "$project" "$base" "$NAME"
  for a in "${model_args[@]+"${model_args[@]}"}"; do printf ' %s' "$a"; done
  printf ' --message-file %s --json\n' "$msg"
  printf 'message_sha256=%s\n' "$MSG_SHA"
  exit 0
fi

say "start claim=$claim message_sha256=$MSG_SHA model=${MODEL:-none} effort=${EFFORT:-none}"
"$here/intent.sh" commit "$state" "$holder" "$num" "$claim" "$TOKEN" "$project" "$base" "$MSG_SHA" >>"$log" 2>&1 || die "intent not committed (exists or fenced); reconcile instead of create" 4
say "intent committed token=$TOKEN"
[ "$DELAY" -gt 0 ] && { say "delaying create ${DELAY}s"; sleep "$DELAY"; }
say "conductor workspace create name=$NAME"
OUT=$(conductor workspace create --project-id "$project" --branch "$base" --name "$NAME" --agent claude "${model_args[@]+"${model_args[@]}"}" --message-file "$msg" --json 2>>"$log") || { say "create call failed; intent stays unresolved for reconcile"; exit 7; }
WID=$(printf '%s' "$OUT" | python3 -c "import json,sys,re; d=json.load(sys.stdin); w=d['workspaceId']; assert re.fullmatch(r'[0-9a-f-]{36}', w); print(w)" 2>/dev/null) || { say "create returned no valid workspace id; intent stays unresolved"; exit 7; }
say "create returned $WID"
# read-back by id: the workspace must exist, carry the exact name, AND belong to the project (both checked,
# not name alone: a project mismatch means this workspace answers someone else's intent).
RB=$(conductor workspace get "$WID" --json 2>>"$log" | python3 -c "
import json,sys
d=json.load(sys.stdin)
name_ok=d.get('name')=='$NAME'; proj_ok=d.get('projectId')=='$project'
if name_ok and proj_ok: print('ok')
elif not name_ok: print('name-mismatch:'+str(d.get('name')))
else: print('project-mismatch:'+str(d.get('projectId')))
" 2>/dev/null || echo "get-failed")
[ "$RB" = ok ] || die "read-back failed ($RB); intent stays unresolved for reconcile" 7
say "read-back ok name=$NAME"
if [ $PAUSE = 1 ]; then say "SIGSTOP self before adopt"; kill -STOP $$; say "resumed"; fi
"$here/intent.sh" adopt "$state" "$holder" "$num" "$claim" "$WID" >>"$log" 2>&1 || die "adopt refused (fenced, already adopted, or project mismatch); leaving $WID for the current holder's reconcile" 3
say "adopted $WID"
echo "$WID"
