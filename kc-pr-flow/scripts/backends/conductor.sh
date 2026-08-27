#!/bin/bash
# Review backend: Conductor cloud workspace. See CONTRACT.md.
#
# One workspace per PR, checked out at the PR head branch, with the review prompt
# as the first session message. job_id is the session id; `open` is the
# session-scoped deep link, so a click lands on the review itself.

set -uo pipefail

CONDUCTOR="${CONDUCTOR:-$HOME/Library/Application Support/com.conductor.app/bin/conductor}"
GH="${GH:-gh}"
JQ="${JQ:-jq}"
CFG_DIR="${PR_LISTEN_CFG_DIR:-$HOME/.claude/kc-plugins-config/pr-flow}"
PROJECT_CACHE="$CFG_DIR/conductor-projects.json"

die() { printf '%s\n' "$*" >&2; exit 1; }

# A Conductor API token is scoped to one organization and the CLI takes no
# organization argument, so a repo outside the keychain token's org needs its own
# token file. Absent a file, the keychain token stands.
load_org_token() {
  local org f
  org=$(printf '%s' "${1%%/*}" | tr '[:upper:]' '[:lower:]')
  f="$CFG_DIR/orgs/$org.env"
  [[ -f "$f" ]] || return 0
  set -a; . "$f"; set +a
}

refresh_project_cache() {
  local out uuid remote slug tmp
  out=$("$CONDUCTOR" project list --limit 100 2>/dev/null) || return 1
  [[ -f "$PROJECT_CACHE" ]] || printf '{}\n' >"$PROJECT_CACHE"
  while IFS= read -r line; do
    uuid=$(grep -oE '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' <<<"$line") || true
    [[ -z "$uuid" ]] && continue
    remote=$(grep -oE 'https?://[^[:space:]]+' <<<"$line" | head -1) || true
    [[ -z "$remote" ]] && continue
    slug=$(sed -E 's#^https?://[^/]+/##; s#\.git$##' <<<"$remote" | tr '[:upper:]' '[:lower:]')
    tmp="$PROJECT_CACHE.tmp.$$"
    "$JQ" --arg s "$slug" --arg id "$uuid" '.[$s] = $id' "$PROJECT_CACHE" >"$tmp" && mv "$tmp" "$PROJECT_CACHE"
  done <<<"$out"
}

project_id_for() {
  local slug id
  slug=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')
  id=$("$JQ" -r --arg s "$slug" '.[$s] // empty' "$PROJECT_CACHE" 2>/dev/null)
  if [[ -z "$id" ]]; then
    refresh_project_cache
    id=$("$JQ" -r --arg s "$slug" '.[$s] // empty' "$PROJECT_CACHE" 2>/dev/null)
  fi
  printf '%s' "$id"
}

cmd_create() {
  local repo="${1:-}" num="${2:-}" url="${3:-}" branch="${4:-}" prompt="${5:-}"
  [[ -n "$repo" && -n "$num" && -n "$url" && -n "$branch" && -n "$prompt" ]] \
    || die "usage: conductor.sh create <repo> <pr> <url> <branch> <prompt-file>"
  [[ -r "$prompt" ]] || die "prompt file not readable: $prompt"
  command -v "$JQ" >/dev/null 2>&1 || die "jq not found"
  [[ -x "$CONDUCTOR" ]] || die "conductor CLI not found at $CONDUCTOR"

  mkdir -p "$CFG_DIR"
  load_org_token "$repo"

  local pid
  pid=$(project_id_for "$repo")
  [[ -n "$pid" ]] || die "no Conductor project for $repo in this token's organization"

  local out ws wsid sess
  out=$("$CONDUCTOR" workspace create \
          --project-id "$pid" \
          --branch "$branch" \
          --name "review PR #$num" \
          --session-name "pr-review #$num" \
          --agent claude \
          --message-file "$prompt" 2>&1) \
    || die "workspace create failed: $(tail -2 <<<"$out" | tr '\n' ' ')"

  ws=$(grep -oE 'conductor://workspace\?id=[0-9a-f-]+' <<<"$out" | head -1) || true
  [[ -n "$ws" ]] || die "workspace create returned no deep link: $(tail -2 <<<"$out" | tr '\n' ' ')"
  wsid="${ws##*id=}"

  sess=$("$CONDUCTOR" workspace session "$wsid" 2>/dev/null \
         | grep -oE 'conductor://workspace\?id=[0-9a-f-]+&session=[0-9a-f-]+' | head -1) || true
  [[ -n "$sess" ]] || die "workspace $wsid has no session yet"

  printf 'job_id=%s\n' "${sess##*session=}"
  printf 'open=%s\n' "$sess"
}

# A session reports `idle` before its first message is delivered, and also after
# dying without ever answering — so idle alone is not completion. Completion
# requires assistant output in the transcript; idle without output is a failure
# once the session has stopped changing.
IDLE_GRACE_SECONDS=180

session_has_output() {
  local out
  out=$("$CONDUCTOR" sql \
    "select (transcript like '%## Assistant%') as has_out from session_transcripts_view where session_id='$1'" 2>/dev/null) || return 1
  grep -qw true <<<"$out"
}

epoch_of() { # ISO-8601, fractional seconds optional
  local t="${1%%.*}"; t="${t%Z}"
  date -j -u -f '%Y-%m-%dT%H:%M:%S' "$t" +%s 2>/dev/null
}

cmd_status() {
  local sid="${1:-}" out st upd age
  [[ -n "$sid" ]] || die "usage: conductor.sh status <job_id>"
  [[ -x "$CONDUCTOR" ]] || die "conductor CLI not found at $CONDUCTOR"

  out=$("$CONDUCTOR" session status "$sid" 2>&1)
  st=$(awk '/^Status/{print $2}' <<<"$out")
  case "$st" in
    idle)
      if session_has_output "$sid"; then echo done; return; fi
      upd=$(awk '/^Updated/{print $2}' <<<"$out")
      age=$(( $(date -u +%s) - $(epoch_of "$upd") ))
      if (( age > IDLE_GRACE_SECONDS )); then
        printf 'session stopped without producing any output\n' >&2
        echo error
      else
        echo running
      fi ;;
    working)  echo running ;;
    "")
      # A missing session is terminal; anything else is undetermined, and the
      # listener must re-ask rather than read silence as completion.
      if grep -qiE 'not found|404' <<<"$out"; then echo error
      else die "cannot determine status: $(head -1 <<<"$out")"; fi ;;
    *)        echo running ;;
  esac
}

case "${1:-}" in
  create) shift; cmd_create "$@" ;;
  status) shift; cmd_status "$@" ;;
  *) die "usage: conductor.sh {create|status} ..." ;;
esac
