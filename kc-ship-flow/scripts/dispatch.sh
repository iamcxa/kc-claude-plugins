#!/usr/bin/env bash
# Usage: dispatch.sh <sprint> [--dry-run] --conn-quote QUOTE --conn-source SOURCE
#          [--env-file PATH] [--workflow-dir DIR] [--state-dir DIR] [--project-id UUID]
#          [--model NAME] [--effort LEVEL]
#        dispatch.sh --resume SLUG [--dry-run] --conn-quote QUOTE --conn-source SOURCE
#          [--env-file PATH] [--workflow-dir DIR] [--state-dir DIR] [--project-id UUID]
#          [--model NAME] [--effort LEVEL]
# workflow-dir default: docs/dev. state-dir default: docs/ship/.spacedock-state.
# Claim fence: <state-dir>/_ship_fence/<sprint>.json maps slug -> {workspace, session,
#   message_sha256, history: [{round, workspace, session, archived}]}; `history` exists
#   only once a slug has been resumed. --env-file values are never printed, logged, or
#   fenced -- only key names appear, as `--env KEY=***`.
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
repo_root=$(cd "$here/../.." && pwd)
contract_file="$here/../pins/conductor-cli.contract"

die() { echo "$1" >&2; exit "${2:-1}"; }

sprint=""
resume_slug=""
env_file=""
DRYRUN=0
workflow_dir="$repo_root/docs/dev"
state_dir="$repo_root/docs/ship/.spacedock-state"
project_id=""
conn_quote=""
conn_source=""
# "sonnet" alone is not a valid model id for `conductor model` (agent claude); needs the full id.
model="${SHIP_DISPATCH_MODEL:-sonnet-5-1m}"
effort="${SHIP_DISPATCH_EFFORT:-medium}"

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRYRUN=1 ;;
    --resume) resume_slug=$2; shift ;;
    --env-file) env_file=$2; shift ;;
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
if [ -z "$resume_slug" ]; then
  [ -n "$sprint" ] || die "usage: dispatch.sh <sprint> [--dry-run] --conn-quote QUOTE --conn-source SOURCE [--env-file PATH] [--workflow-dir DIR] [--state-dir DIR]" 2
fi

[ -n "$conn_quote" ] || die "conn required" 2
[ -n "$conn_source" ] || die "conn required" 2

# contract_file: one argv shape per line; --flags checked against live --help output,
# the remaining command tokens checked as a literal substring.
check_contract() {
  [ -f "$contract_file" ] || die "conductor cli contract missing: $contract_file" 2
  local version help_text line cmd tok ok missing
  version=$(conductor --version 2>&1) || die "conductor unavailable: $version" 2
  help_text=$(conductor --help 2>&1) || die "conductor unavailable: $help_text" 2
  missing=""
  while IFS= read -r line; do
    line="${line%%#*}"
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

# conductor auth whoami has no --json output; sender id is parsed from its table.
whoami_out=$(conductor auth whoami 2>&1) || die "conductor unavailable" 2
sender_id=$(printf '%s\n' "$whoami_out" | sed -nE 's/^User ID[[:space:]]+//p' | head -n1)
[ -n "$sender_id" ] || die "conductor unavailable: no User ID in auth whoami output" 2
conductor workspace list --limit 1 >/dev/null 2>&1 || die "conductor unavailable: workspace list probe failed" 2
# sql is a degradable probe (pins/conductor-cli.contract): a failure here is a dated
# stderr notice, not fatal -- dispatch.sh itself never reads sql again after this.
sql_probe_out=$(conductor --json sql "SELECT 1" 2>&1) || \
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) degraded: conductor sql probe failed, continuing without it ($sql_probe_out)" >&2

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

env_args=()
env_display_args=()
check_env_file_perms() {
  local f="$1" perm other
  perm=$(stat -c '%a' "$f" 2>/dev/null) || perm=$(stat -f '%Lp' "$f" 2>/dev/null) || die "cannot stat env file: $f" 2
  other="${perm: -1}"
  [ $(( other & 4 )) -eq 0 ] || die "env file must not be world-readable: $f (chmod o-r it)" 2
}
if [ -n "$env_file" ]; then
  [ -f "$env_file" ] || die "env file not found: $env_file" 2
  check_env_file_perms "$env_file"
  while IFS= read -r line || [ -n "$line" ]; do
    [ -n "$line" ] || continue
    case "$line" in \#*) continue ;; esac
    key="${line%%=*}"
    val="${line#*=}"
    [ -n "$key" ] && [ "$key" != "$line" ] || die "malformed env-file line (expected KEY=VALUE): $line" 2
    env_args+=(--env "$key=$val")
    env_display_args+=(--env "$key=***")
  done < "$env_file"
fi

boot_gate_line='Gate decisions are recorded by the ship first officer with the Captain'"'"'s words. Sync state by merge, never rebase. Never record a gate decision.'

# Asks the worktree itself rather than comparing paths against `git worktree list`,
# whose paths are physical (symlinks resolved) and would miss a symlinked checkout.
resolve_branch_for_worktree() {
  git -C "$1" symbolic-ref --short HEAD 2>/dev/null
}

do_resume() {
  local slug="$1" resolved entity_path entity_sprint entity_status entity_pr latest_attempt
  local wt_field wt_path branch candidate_sha fence_file run msg msg_sha name
  local display_args create_args out wid sid status_out

  resolved=$(spacedock status --workflow-dir "$workflow_dir" --resolve "$slug" --json) \
    || die "cannot resolve entity path for $slug" 2
  entity_path=$(printf '%s' "$resolved" | python3 -c "import json,sys; print(json.load(sys.stdin)['path'])")
  [ -f "$entity_path" ] || die "resolved entity path missing: $entity_path" 2

  entity_sprint=$(sed -n 's/^sprint: *//p' "$entity_path" | head -n1)
  [ -n "$entity_sprint" ] || die "entity has no sprint field, cannot locate its fence file: $entity_path" 2
  fence_file="$state_dir/_ship_fence/$entity_sprint.json"
  [ -f "$fence_file" ] || die "no fence entry for $slug (nothing to resume): $fence_file" 2
  python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
sys.exit(0 if sys.argv[2] in d else 1)
" "$fence_file" "$slug" || die "no fence entry for $slug (nothing to resume): $fence_file" 2

  entity_status=$(sed -n 's/^status: *//p' "$entity_path" | head -n1)
  entity_pr=$(sed -n 's/^pr: *//p' "$entity_path" | head -n1)
  [ -n "$entity_pr" ] || entity_pr="none"
  latest_attempt=$(grep -oE 'id: gate-attempt:[^[:space:]]+' "$entity_path" | tail -n1 | sed 's/^id: //')
  [ -n "$latest_attempt" ] || latest_attempt="none"

  wt_field=$(sed -n 's/^worktree: *//p' "$entity_path" | head -n1)
  [ -n "$wt_field" ] || die "entity has no worktree field to resolve a resume branch from: $entity_path" 2
  wt_path="$repo_root/$wt_field"
  branch=$(resolve_branch_for_worktree "$wt_path")
  [ -n "$branch" ] || die "no git worktree found at $wt_path; cannot resolve resume branch" 2
  candidate_sha=$(git -C "$wt_path" rev-parse HEAD 2>&1) || die "cannot resolve candidate SHA at $wt_path: $candidate_sha" 2

  run=$(mktemp -d "${TMPDIR:-/tmp}/ship-resume-XXXXXX"); chmod 700 "$run"
  token=$(od -An -N6 -tx1 /dev/urandom | tr -d ' \n')
  msg="$run/$slug.resume-boot.md"
  {
    printf 'Sender identity: workspace_creator_id=%s\n\n' "$sender_id"
    printf 'Answers to your questions arrive as further messages from this sender; no Captain message will appear in this session.\n\n'
    printf 'Dispatch token: %s\n' "$token"
    printf 'Echo this token in every report you send back, so the sender above can match your reports to this dispatch.\n\n'
    printf "Captain's batch approval (conn-quote): %s\n" "$conn_quote"
    printf 'conn-source: %s\n\n' "$conn_source"
    printf '%s\n\n' "$boot_gate_line"
    printf 'Resume boot for entity `%s` (workflow `docs/dev`).\n\n' "$slug"
    printf 'Entity status: %s\n' "$entity_status"
    printf 'Latest gate attempt: %s\n' "$latest_attempt"
    printf 'PR: %s\n' "$entity_pr"
    printf 'Candidate SHA: %s\n\n' "$candidate_sha"
    printf '1. Resume the first officer for slug `%s` in workflow `docs/dev` (`spacedock claude %s`).\n' "$slug" "$slug"
    printf '2. Continue this entity through its route from status `%s`; do not repeat a completed stage.\n' "$entity_status"
    printf '3. Push every state change to the state branch.\n'
  } > "$msg"
  msg_sha=$(sha256sum "$msg" | cut -d' ' -f1)
  name="resume-$slug"

  if [ "$DRYRUN" = 1 ]; then
    display_args=(conductor workspace create --project-id "$project_id" --branch "$branch" --name "$name" \
      --agent claude --model "$model" --effort "$effort" "${env_display_args[@]}" --message-file "$msg" --json)
    printf '%s\n' "${display_args[*]}"
    printf 'message_sha256=%s\n' "$msg_sha"
    return 0
  fi

  create_args=(conductor workspace create --project-id "$project_id" --branch "$branch" --name "$name" \
    --agent claude --model "$model" --effort "$effort" "${env_args[@]}" --message-file "$msg" --json)
  out=$("${create_args[@]}" 2>&1) || die "conductor workspace create failed for $slug: $out" 7
  wid=$(printf '%s' "$out" | python3 -c "import json,sys; print(json.load(sys.stdin)['workspaceId'])") \
    || die "conductor workspace create returned no workspace id for $slug" 7
  sid=$(printf '%s' "$out" | python3 -c "import json,sys; print(json.load(sys.stdin).get('sessionId') or '')")

  # Single probe, not a poll loop; not-yet-ready just leaves the prior round unarchived.
  status_out=$(conductor workspace status "$wid" 2>&1) || status_out=""
  ready=0
  case "$status_out" in *[Rr][Ee][Aa][Dd][Yy]*) ready=1 ;; esac

  python3 -c '
import json, sys
path, slug, wid, sid, ready, msg_sha = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] == "1", sys.argv[6]
d = json.load(open(path))
entry = d[slug]
history = entry.get("history", [])
history.append({
    "round": "r%d" % (len(history) + 1),
    "workspace": entry.get("workspace"),
    "session": entry.get("session"),
    "archived": ready,
})
entry["history"] = history
entry["workspace"] = wid
entry["session"] = sid or None
entry["message_sha256"] = msg_sha
json.dump(d, open(path, "w"), indent=1, sort_keys=True)
' "$fence_file" "$slug" "$wid" "$sid" "$ready" "$msg_sha"
  git -C "$state_dir" add "_ship_fence/$entity_sprint.json"
  git -C "$state_dir" -c user.name=ship-dispatch -c user.email=ship-dispatch@local commit -q \
    -m "ship: resume $slug -> $wid" -- "_ship_fence/$entity_sprint.json"

  ref=$(git -C "$state_dir" symbolic-ref -q HEAD) || die "ship state checkout is not on a branch" 6
  remote=$(git -C "$state_dir" for-each-ref --format='%(upstream:remotename)' "$ref")
  remote_branch=$(git -C "$state_dir" for-each-ref --format='%(upstream:strip=3)' "$ref")
  if [ -n "$remote" ] && [ -n "$remote_branch" ]; then
    git -C "$state_dir" push -q "$remote" HEAD:"$remote_branch" || die "ship state push rejected for $slug" 6
  fi
  echo "$slug $wid"
}

if [ -n "$resume_slug" ]; then
  do_resume "$resume_slug"
  exit 0
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

token=$(od -An -N6 -tx1 /dev/urandom | tr -d ' \n')

while IFS= read -r slug; do
  [ -n "$slug" ] || continue

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
  {
    printf 'Sender identity: workspace_creator_id=%s\n\n' "$sender_id"
    printf 'Answers to your questions arrive as further messages from this sender; no Captain message will appear in this session.\n\n'
    printf 'Dispatch token: %s\n' "$token"
    printf 'Echo this token in every report you send back, so the sender above can match your reports to this dispatch.\n\n'
    printf "Captain's batch approval (conn-quote): %s\n" "$conn_quote"
    printf 'conn-source: %s\n\n' "$conn_source"
    printf '%s\n\n' "$boot_gate_line"
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
    display_args=(conductor workspace create --project-id "$project_id" --branch "$trunk" --name "$name" \
      --agent claude --model "$model" --effort "$effort" "${env_display_args[@]}" --message-file "$msg" --json)
    printf '%s\n' "${display_args[*]}"
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

  create_args=(conductor workspace create --project-id "$project_id" --branch "$trunk" --name "$name" \
    --agent claude --model "$model" --effort "$effort" "${env_args[@]}" --message-file "$msg" --json)
  out=$("${create_args[@]}" 2>&1) || die "conductor workspace create failed for $slug: $out" 7
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
