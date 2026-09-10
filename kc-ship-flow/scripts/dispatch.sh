#!/usr/bin/env bash
# One Conductor workspace + first-officer boot per ready docs/dev task sharing a sprint.
# Usage: dispatch.sh <sprint> [--dry-run] [--workflow-dir DIR] [--state-dir DIR]
#          [--project-id UUID] [--model NAME] [--effort LEVEL]
#
# <workflow-dir> defaults to the repo's docs/dev (the dev-flow tasks being wrapped).
# <state-dir> is ship's own split-root state checkout (default docs/ship/.spacedock-state)
# where the claim fence is committed; it does not need to exist yet for --dry-run.
#
# The claim fence records <slug> -> {workspace, session, message_sha256} in
# <state-dir>/_ship_fence/<sprint>.json before the create call; a slug already present
# there is reported already-recorded rather than re-created.
#
# No `spacedock dispatch build` here: the message this station writes is a fixed
# first-officer boot (run the whole docs/dev route to a prepared validation gate), not
# an ensign single-stage envelope, so there is no per-stage artifact to build.
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
repo_root=$(cd "$here/../.." && pwd)
pin_file="$here/../pins/conductor-cli.txt"

die() { echo "$1" >&2; exit "${2:-1}"; }

sprint=""
DRYRUN=0
workflow_dir="$repo_root/docs/dev"
state_dir="$repo_root/docs/ship/.spacedock-state"
project_id=""
model="${SHIP_DISPATCH_MODEL:-sonnet}"
effort="${SHIP_DISPATCH_EFFORT:-medium}"

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRYRUN=1 ;;
    --workflow-dir) workflow_dir=$2; shift ;;
    --state-dir) state_dir=$2; shift ;;
    --project-id) project_id=$2; shift ;;
    --model) model=$2; shift ;;
    --effort) effort=$2; shift ;;
    -*) die "unknown flag $1" 2 ;;
    *) [ -z "$sprint" ] || die "unexpected argument $1" 2; sprint=$1 ;;
  esac
  shift
done
[ -n "$sprint" ] || die "usage: dispatch.sh <sprint> [--dry-run] [--workflow-dir DIR] [--state-dir DIR]" 2

# Pin check first, before any other conductor call: a version drift means the flags below
# may no longer mean what this script assumes, so nothing else runs until it is re-pinned.
[ -f "$pin_file" ] || die "conductor cli pin missing: $pin_file" 2
pinned_version=$(head -n1 "$pin_file")
installed_version=$(conductor --version 2>&1) || die "conductor unavailable: $installed_version" 2
if [ "$installed_version" != "$pinned_version" ]; then
  diff <(tail -n +2 "$pin_file") <(conductor --help 2>&1) || true
  die "conductor cli changed: read the diff, then re-pin" 5
fi

conductor auth whoami >/dev/null 2>&1 || die "conductor unavailable" 2

trunk=$(sed -n 's/^trunk: *//p' "$workflow_dir/README.md" | head -n1)
trunk=${trunk:-main}

if [ -z "$project_id" ]; then
  remote_url=$(git -C "$repo_root" remote get-url origin 2>&1) || die "conductor unavailable: no origin remote: $remote_url" 2
  remote_norm=${remote_url%.git}
  project_id=$(conductor project list --limit 100 --json 2>/dev/null | python3 -c "
import json, sys
remote = sys.argv[1]
data = json.load(sys.stdin)
for p in data.get('data', []):
    if p.get('gitRemote', '').rstrip('/').removesuffix('.git') == remote.rstrip('/'):
        print(p['id'])
        break
" "$remote_norm") || project_id=""
  [ -n "$project_id" ] || die "project id not resolved for remote $remote_norm" 6
fi

readiness_json=$(spacedock status --workflow-dir "$workflow_dir" \
  --where "sprint=$sprint" --where "sprint-readiness=ready" --fields slug --json) \
  || die "spacedock status failed for sprint=$sprint" 2

slugs=$(printf '%s' "$readiness_json" | python3 -c "
import json, sys
d = json.load(sys.stdin)
for e in d.get('entities', []):
    print(e['slug'])
")

run=$(mktemp -d "${TMPDIR:-/tmp}/ship-dispatch-XXXXXX"); chmod 700 "$run"
fence_file="$state_dir/_ship_fence/$sprint.json"
existing_copy="$run/existing.json"
if [ -f "$fence_file" ]; then
  cp "$fence_file" "$existing_copy"
else
  echo '{}' > "$existing_copy"
fi

if [ -z "$slugs" ]; then
  echo "no ready tasks in sprint=$sprint" >&2
  exit 0
fi

while IFS= read -r slug; do
  [ -n "$slug" ] || continue

  already=$(python3 -c "
import json
d = json.load(open('$existing_copy'))
print('yes' if '$slug' in d else 'no')
")
  if [ "$already" = yes ]; then
    echo "$slug already-recorded"
    continue
  fi

  resolved=$(spacedock status --workflow-dir "$workflow_dir" --resolve "$slug" --json) \
    || die "cannot resolve entity path for $slug" 2
  entity_path=$(printf '%s' "$resolved" | python3 -c "import json,sys; print(json.load(sys.stdin)['path'])")
  [ -f "$entity_path" ] || die "resolved entity path missing: $entity_path" 2

  msg="$run/$slug.boot.md"
  cat > "$msg" <<BOOTMSG
Boot as the docs/dev first officer for exactly one entity.

1. Become the first officer for the entity at slug \`$slug\` in workflow \`docs/dev\`
   (\`spacedock claude $slug\`; run \`spacedock state init\` first if this split-root
   checkout's state directory is absent).
2. Run that entity through its route to a prepared \`validation\` gate
   (\`spacedock gate prepare\`); deliver the Draft PR through the \`pr-merge\` mod as the
   Local Profile already requires.
3. Stop at the gate. Do not merge. Push every state change to the state branch.
BOOTMSG
  msg_sha=$(sha256sum "$msg" | cut -d' ' -f1)
  name="$sprint-$slug"

  if [ "$DRYRUN" = 1 ]; then
    printf 'conductor workspace create --project-id %s --branch %s --name %s --agent claude --model %s --effort %s --message-file %s --json\n' \
      "$project_id" "$trunk" "$name" "$model" "$effort" "$msg"
    printf 'message_sha256=%s\n' "$msg_sha"
    continue
  fi

  [ -d "$state_dir" ] || die "ship state dir missing (run: spacedock state init --workflow-dir docs/ship): $state_dir" 2
  mkdir -p "$state_dir/_ship_fence"
  fence_scratch="$run/$slug.fence.json"
  cp "$existing_copy" "$fence_scratch"
  python3 -c "
import json
p = '$fence_scratch'
d = json.load(open(p))
d['$slug'] = {'workspace': None, 'session': None, 'message_sha256': '$msg_sha'}
json.dump(d, open(p, 'w'), indent=1, sort_keys=True)
"
  cp "$fence_scratch" "$fence_file"
  cp "$fence_scratch" "$existing_copy"
  git -C "$state_dir" add "_ship_fence/$sprint.json"
  git -C "$state_dir" -c user.name=ship-dispatch -c user.email=ship-dispatch@local commit -q \
    -m "ship: claim fence for $slug" -- "_ship_fence/$sprint.json"

  out=$(conductor workspace create --project-id "$project_id" --branch "$trunk" --name "$name" \
    --agent claude --model "$model" --effort "$effort" --message-file "$msg" --json 2>&1) \
    || die "conductor workspace create failed for $slug: $out" 7
  wid=$(printf '%s' "$out" | python3 -c "import json,sys; print(json.load(sys.stdin)['workspaceId'])") \
    || die "conductor workspace create returned no workspace id for $slug" 7
  sid=$(printf '%s' "$out" | python3 -c "import json,sys; print(json.load(sys.stdin).get('sessionId') or '')")

  python3 -c "
import json
p = '$fence_file'
d = json.load(open(p))
d['$slug']['workspace'] = '$wid'
d['$slug']['session'] = ('$sid' or None)
json.dump(d, open(p, 'w'), indent=1, sort_keys=True)
"
  # Keep the loop's in-memory view of "already recorded" in sync with what was just
  # committed: the next slug's "already" check and its own fence_scratch base both read
  # existing_copy, and without this it would still see this slug's workspace as null.
  cp "$fence_file" "$existing_copy"
  git -C "$state_dir" add "_ship_fence/$sprint.json"
  git -C "$state_dir" -c user.name=ship-dispatch -c user.email=ship-dispatch@local commit -q \
    -m "ship: dispatch $slug -> $wid" -- "_ship_fence/$sprint.json"

  ref=$(git -C "$state_dir" symbolic-ref -q HEAD) || die "ship state checkout is not on a branch" 6
  remote=$(git -C "$state_dir" for-each-ref --format='%(upstream:remotename)' "$ref")
  branch=$(git -C "$state_dir" for-each-ref --format='%(upstream:strip=3)' "$ref")
  if [ -n "$remote" ] && [ -n "$branch" ]; then
    git -C "$state_dir" push -q "$remote" HEAD:"$branch" || die "ship state push rejected for $slug" 6
  fi
  echo "$slug $wid"
done <<< "$slugs"
