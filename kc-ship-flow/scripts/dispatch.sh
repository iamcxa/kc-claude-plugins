#!/usr/bin/env bash
# One Conductor workspace + first-officer boot per ready docs/dev task sharing a sprint.
# Usage: dispatch.sh <sprint> [--dry-run] --conn-quote QUOTE --conn-source SOURCE
#          [--workflow-dir DIR] [--state-dir DIR]
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
# --conn-quote/--conn-source carry the Captain's verbatim batch approval into every
# worker's boot message (round 1's batch showed a worker refuse `git push` under the
# pr-merge mod until the Captain typed the conn into the session by hand); both are
# required, since a dispatch with no conn to quote is the same failure mode again.
#
# No `spacedock dispatch build` here: the message this station writes is a fixed
# first-officer boot (run the whole docs/dev route to a prepared validation gate), not
# an ensign single-stage envelope, so there is no per-stage artifact to build.
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
repo_root=$(cd "$here/../.." && pwd)
contract_file="$here/../pins/conductor-cli.contract"

die() { echo "$1" >&2; exit "${2:-1}"; }

sprint=""
DRYRUN=0
workflow_dir="$repo_root/docs/dev"
state_dir="$repo_root/docs/ship/.spacedock-state"
project_id=""
conn_quote=""
conn_source=""
# Both defaults are listed by `conductor model` (agent claude) as of the pinned CLI version;
# "sonnet" alone is not a valid model id there.
model="${SHIP_DISPATCH_MODEL:-sonnet-5-1m}"
effort="${SHIP_DISPATCH_EFFORT:-medium}"

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRYRUN=1 ;;
    --workflow-dir) workflow_dir=$2; shift ;;
    --state-dir) state_dir=$2; shift ;;
    --project-id) project_id=$2; shift ;;
    --model) model=$2; shift ;;
    --effort) effort=$2; shift ;;
    --conn-quote) conn_quote=$2; shift ;;
    --conn-source) conn_source=$2; shift ;;
    -*) die "unknown flag $1" 2 ;;
    *) [ -z "$sprint" ] || die "unexpected argument $1" 2; sprint=$1 ;;
  esac
  shift
done
[ -n "$sprint" ] || die "usage: dispatch.sh <sprint> [--dry-run] --conn-quote QUOTE --conn-source SOURCE [--workflow-dir DIR] [--state-dir DIR]" 2

# The Captain's batch approval must reach every worker's boot message; a dispatch run
# carrying nothing to quote reproduces the exact failure round 1 hit (a worker refusing
# `git push` until the Captain typed the conn in by hand). Checked before any network
# call -- this is a local usage error, not a Conductor-availability one.
[ -n "$conn_quote" ] || die "conn required" 2
[ -n "$conn_source" ] || die "conn required" 2

# Used-surface contract: the argv shapes this script and watch.sh actually call, one per
# line in $contract_file. The installed CLI's version is printed (never gated on); every
# shape is checked against live `conductor --help` and a missing one refuses by name, since
# a version drift is only safe to ignore when the surface this script depends on is intact.
check_contract() {
  [ -f "$contract_file" ] || die "conductor cli contract missing: $contract_file" 2
  local version help_text line cmd tok ok missing
  version=$(conductor --version 2>&1) || die "conductor unavailable: $version" 2
  help_text=$(conductor --help 2>&1) || die "conductor unavailable: $help_text" 2
  missing=""
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    cmd=""
    ok=1
    for tok in $line; do
      case "$tok" in
        --*)
          case "$help_text" in
            *"$tok"*) : ;;
            *) ok=0 ;;
          esac
          ;;
        *)
          cmd="${cmd:+$cmd }$tok"
          ;;
      esac
    done
    case "$help_text" in
      *"$cmd"*) : ;;
      *) ok=0 ;;
    esac
    if [ "$ok" != 1 ]; then
      missing="$cmd"
      break
    fi
  done < "$contract_file"
  if [ -n "$missing" ]; then
    die "conductor cli used-surface changed: missing shape '$missing' (re-check $contract_file against \`conductor --help\`)" 5
  fi
  echo "conductor $version: used surface unchanged"
}
check_contract

# Read-only probes, run before the first mutating call (`workspace create`, below). Also
# recovers the sender identity (`workspace_creator_id`, from the human-readable table
# `conductor auth whoami` prints -- `--json` output for auth commands is not JSON; see
# `conductor --help`'s Global options note) that the boot message names, so every worker
# knows who its answers come back from.
whoami_out=$(conductor auth whoami 2>&1) || die "conductor unavailable" 2
sender_id=$(printf '%s\n' "$whoami_out" | sed -nE 's/^User ID[[:space:]]+//p' | head -n1)
[ -n "$sender_id" ] || die "conductor unavailable: no User ID in auth whoami output" 2
conductor workspace list --limit 1 >/dev/null 2>&1 || die "conductor unavailable: workspace list probe failed" 2
conductor --json sql "SELECT 1" >/dev/null 2>&1 || die "conductor unavailable: sql probe failed" 2

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

# A 12-hex-char token unique to this dispatch run, not per-slug: every worker booted by
# this invocation echoes the same token in its reports, so the sender above can tell a
# real report apart from anything else arriving in the session.
token=$(od -An -N6 -tx1 /dev/urandom | tr -d ' \n')

while IFS= read -r slug; do
  [ -n "$slug" ] || continue

  # Values reach Python only as argv, never interpolated into the source: a slug can
  # contain a quote (it comes off an adopter's state branch, not this repo).
  already=$(python3 -c '
import json, sys
path, slug = sys.argv[1], sys.argv[2]
d = json.load(open(path))
print("yes" if slug in d else "no")
' "$existing_copy" "$slug")
  if [ "$already" = yes ]; then
    echo "$slug already-recorded"
    continue
  fi

  resolved=$(spacedock status --workflow-dir "$workflow_dir" --resolve "$slug" --json) \
    || die "cannot resolve entity path for $slug" 2
  entity_path=$(printf '%s' "$resolved" | python3 -c "import json,sys; print(json.load(sys.stdin)['path'])")
  [ -f "$entity_path" ] || die "resolved entity path missing: $entity_path" 2

  msg="$run/$slug.boot.md"
  # Built with printf, not an unquoted heredoc: $conn_quote is Captain-typed text from the
  # batch approval and must never be re-interpreted by the shell (a literal $(...) or
  # backtick in a quote must land in the file as text, not run as a command).
  {
    printf 'Sender identity: workspace_creator_id=%s\n\n' "$sender_id"
    printf 'Answers to your questions arrive as further messages from this sender; no Captain message will appear in this session.\n\n'
    printf 'Dispatch token: %s\n' "$token"
    printf 'Echo this token in every report you send back, so the sender above can match your reports to this dispatch.\n\n'
    printf "Captain's batch approval (conn-quote): %s\n" "$conn_quote"
    printf 'conn-source: %s\n\n' "$conn_source"
    printf 'Sync state by merge, never rebase.\n\n'
    printf 'Boot as the docs/dev first officer for exactly one entity.\n\n'
    printf '1. Become the first officer for the entity at slug `%s` in workflow `docs/dev`\n' "$slug"
    printf '   (`spacedock claude %s`; run `spacedock state init` first if this split-root\n' "$slug"
    printf "   checkout's state directory is absent).\n"
    printf '2. Run that entity through its route to a prepared `validation` gate\n'
    printf '   (`spacedock gate prepare`); deliver the Draft PR through the `pr-merge` mod as the\n'
    printf '   Local Profile already requires.\n'
    printf '3. Stop at the gate. Do not merge. Push every state change to the state branch.\n'
  } > "$msg"
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
  python3 -c '
import json, sys
path, slug, msg_sha = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(path))
d[slug] = {"workspace": None, "session": None, "message_sha256": msg_sha}
json.dump(d, open(path, "w"), indent=1, sort_keys=True)
' "$fence_scratch" "$slug" "$msg_sha"
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

  python3 -c '
import json, sys
path, slug, wid, sid = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
d = json.load(open(path))
d[slug]["workspace"] = wid
d[slug]["session"] = sid or None
json.dump(d, open(path, "w"), indent=1, sort_keys=True)
' "$fence_file" "$slug" "$wid" "$sid"
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
