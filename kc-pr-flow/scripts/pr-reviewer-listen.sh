#!/bin/bash
# <bitbar.title>PR Review Listener</bitbar.title>
# <bitbar.version>v1</bitbar.version>
# <bitbar.author>kc-pr-flow</bitbar.author>
# <bitbar.desc>Watch GitHub for review requests and start a review for each one; read the result from the menu bar.</bitbar.desc>
# <bitbar.dependencies>gh,jq</bitbar.dependencies>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
#
# Menu-bar UI and listener in one script: the plugin refresh interval is the poll
# interval, so there is no daemon to supervise. Where a review actually runs is a
# backend's business — see scripts/backends/CONTRACT.md.

set -uo pipefail

GH="${GH:-gh}"
JQ="${JQ:-jq}"
OPEN=/usr/bin/open

# Menu callbacks re-enter through whatever the menu-bar host launched, which may be
# a wrapper that sets the environment this run depends on.
SELF="${PR_LISTEN_SELF:-${BASH_SOURCE[0]}}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backends"
PROMPT_TMPL="${PR_LISTEN_PROMPT:-$SCRIPT_DIR/../reference/reviewer-dispatch-prompt.md}"

CFG_DIR="${PR_LISTEN_CFG_DIR:-$HOME/.claude/kc-plugins-config/pr-flow}"
CONFIG="$CFG_DIR/reviewer-listen.config.json"
STATE="$CFG_DIR/reviewer-listen.state.json"
LOCKDIR="$CFG_DIR/.reviewer-listen.lock"
LOG="${PR_LISTEN_LOG:-$HOME/.claude/audit/pr-reviewer-listen.log}"

MAX_DISPATCH_PER_TICK=1
MAX_ATTEMPTS=3

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >>"$LOG"; }

# Config is intent and survives a wipe; state is derived and can be deleted.

init_files() {
  mkdir -p "$CFG_DIR" "$(dirname "$LOG")"
  [[ -s "$CONFIG" ]] || printf '%s\n' '{"master":true,"backend":"conductor","notify_via":"terminal-notifier","repos":{}}' >"$CONFIG"
  [[ -s "$STATE"  ]] || printf '%s\n' '{"seen":{},"open":[],"last_poll":null,"last_error":null}' >"$STATE"
}

edit_json() { # edit_json <file> [jq-args...]
  local f="$1"; shift
  local tmp="$f.tmp.$$"
  if "$JQ" "$@" "$f" >"$tmp" 2>>"$LOG"; then mv "$tmp" "$f"
  else rm -f "$tmp"; log "edit failed on $f: $*"; return 1; fi
}

cfg_edit() { edit_json "$CONFIG" "$@"; }
st_edit()  { edit_json "$STATE" "$@"; }
cfg_get()  { "$JQ" -r "$@" "$CONFIG" 2>/dev/null; }
st_get()   { "$JQ" -r "$@" "$STATE" 2>/dev/null; }

backend_path() {
  local b; b=$(cfg_get '.backend // "conductor"')
  printf '%s/%s.sh' "$BACKEND_DIR" "$b"
}

notify() { # notify <title> <subtitle> [open-target]
  local title="$1" sub="$2" target="${3:-}" via tn
  via=$(cfg_get '.notify_via // "terminal-notifier"')
  if [[ "$via" == "terminal-notifier" ]] && tn=$(command -v terminal-notifier); then
    # The only channel here whose banner opens the review on click.
    local args=(-title "$title" -message "$sub")
    [[ -n "$target" ]] && args+=(-open "$target")
    "$tn" "${args[@]}" >/dev/null 2>&1 || true
  else
    /usr/bin/osascript -e "display notification \"$sub\" with title \"$title\"" 2>/dev/null || true
  fi
}

mark_error() {
  st_edit --arg k "$1" --arg e "$2" \
    '.seen[$k] = ((.seen[$k] // {}) + {status:"error", error:$e, ts:(now|todate), attempts:(((.seen[$k].attempts) // 0) + 1)})'
}

dispatch() { # dispatch <repo> <pr-number> <pr-url>
  local repo="$1" num="$2" url="$3" key="$1#$2"
  local be branch msg out job target

  be=$(backend_path)
  if [[ ! -x "$be" ]]; then
    mark_error "$key" "backend not executable: $be"; return 1
  fi

  branch=$("$GH" pr view "$num" --repo "$repo" --json headRefName --jq .headRefName 2>>"$LOG")
  if [[ -z "$branch" ]]; then
    mark_error "$key" "could not read head branch"; return 1
  fi

  # Claim the key before the backend call: a crash mid-create must not double-create.
  st_edit --arg k "$key" --arg u "$url" --arg b "$branch" \
    '.seen[$k] = ((.seen[$k] // {}) + {status:"dispatching", url:$u, branch:$b, ts:(now|todate), attempts:(((.seen[$k].attempts) // 0) + 1)})'

  msg=$(mktemp -t prreview)
  sed -e "s|__PR_URL__|$url|g" -e "s|__REPO__|$repo|g" -e "s|__BRANCH__|$branch|g" \
      "$PROMPT_TMPL" >"$msg"
  out=$("$be" create "$repo" "$num" "$url" "$branch" "$msg" 2>&1)
  local rc=$?
  rm -f "$msg"

  job=$(sed -n 's/^job_id=//p' <<<"$out" | head -1)
  target=$(sed -n 's/^open=//p' <<<"$out" | head -1)
  if [[ $rc -ne 0 || -z "$job" ]]; then
    mark_error "$key" "$(tail -2 <<<"$out" | tr '\n' ' ' | cut -c1-200)"
    log "dispatch $key FAILED: $out"; return 1
  fi

  st_edit --arg k "$key" --arg j "$job" --arg t "$target" \
    '.seen[$k] += {status:"running", job_id:$j, open:$t, error:null, ts:(now|todate)}'
  log "dispatch $key -> $job"
  [[ -n "$target" ]] && "$OPEN" -g "$target" 2>/dev/null || true
  notify "Review started" "$repo #$num — review running" "$target"
}

# A finished review cannot be read from the request list: GitHub drops the PR off
# review-requested the moment a review is submitted. Ask the backend instead.

check_completions() {
  local be key job verdict
  be=$(backend_path)
  [[ -x "$be" ]] || return 0
  while IFS=$'\t' read -r key job; do
    [[ -z "$job" ]] && continue
    verdict=$("$be" status "$job" 2>/dev/null) || continue
    case "$verdict" in
      done)
        st_edit --arg k "$key" '.seen[$k] += {status:"reviewed", finished:(now|todate)}'
        notify "Review ready" "$key — review finished, go read it" \
               "$(st_get --arg k "$key" '.seen[$k].open // empty')"
        log "completed $key" ;;
      error)
        mark_error "$key" "backend reported the job cannot finish" ;;
    esac
  done < <("$JQ" -r '.seen | to_entries[] | select(.value.status == "running") | select(.value.job_id) | [.key, .value.job_id] | @tsv' "$STATE" 2>/dev/null)
}

poll() {
  local prs repo num url draft enabled status attempts n=0
  prs=$("$GH" search prs --review-requested=@me --state open --limit 40 \
          --json repository,number,title,url,isDraft 2>>"$LOG")
  if [[ -z "$prs" ]]; then
    st_edit --arg e "gh search failed (auth or network)" '.last_error = $e'
    return 1
  fi
  st_edit --argjson p "$prs" '.open = $p | .last_poll = (now|todate) | .last_error = null'

  # Register any newly-seen repo, listening by default: a review request should
  # not need configuration before it is picked up.
  while IFS= read -r repo; do
    [[ -z "$repo" ]] && continue
    cfg_edit --arg r "$repo" 'if (.repos | has($r)) then . else .repos[$r] = {enabled:true} end'
  done < <("$JQ" -r '.open[].repository.nameWithOwner' "$STATE" 2>/dev/null)

  [[ "$(cfg_get '.master')" == "true" ]] || return 0

  while IFS=$'\t' read -r repo num url draft; do
    [[ -z "$repo" ]] && continue
    (( n >= MAX_DISPATCH_PER_TICK )) && break
    [[ "$draft" == "true" ]] && continue
    enabled=$(cfg_get --arg r "$repo" '.repos[$r].enabled // false')
    [[ "$enabled" == "true" ]] || continue
    status=$(st_get --arg k "$repo#$num" '.seen[$k].status // empty')
    attempts=$(st_get --arg k "$repo#$num" '.seen[$k].attempts // 0')
    [[ -n "$status" && "$status" != "error" ]] && continue
    (( attempts >= MAX_ATTEMPTS )) && continue
    dispatch "$repo" "$num" "$url"
    n=$((n+1))
  done < <("$JQ" -r '.open[] | [.repository.nameWithOwner, (.number|tostring), .url, (.isDraft|tostring)] | @tsv' "$STATE" 2>/dev/null)
}

menu_label() { printf '%s' "${1//|/／}"; }   # a literal pipe would end the SwiftBar line

render() {
  local master n_on n_open n_done last err key status target title repo num fin on
  master=$(cfg_get '.master')
  n_on=$(cfg_get '[.repos | to_entries[] | select(.value.enabled == true)] | length')
  n_open=$(st_get '.open | length')
  last=$(st_get '.last_poll // "never"')
  err=$(st_get '.last_error // empty')

  if [[ "$master" != "true" ]]; then echo "👁 off"
  elif [[ -n "$err" ]];       then echo "👁 !"
  else                             echo "👁 $n_open"; fi
  echo "---"

  if [[ -n "$err" ]]; then
    echo "⚠️ $(menu_label "$err") | color=red"
    echo "---"
  fi

  echo "Review requests ($n_open)"
  if [[ "$n_open" == "0" ]]; then
    echo "-- none"
  else
    while IFS=$'\t' read -r repo num title url; do
      [[ -z "$repo" ]] && continue
      key="$repo#$num"
      status=$(st_get --arg k "$key" '.seen[$k].status // "new"')
      target=$(st_get --arg k "$key" '.seen[$k].open // empty')
      title=$(menu_label "${title:0:48}")
      case "$status" in
        reviewed|running)
          echo "-- $([[ $status == reviewed ]] && echo ✅ || echo ⏳) #$num $title | bash=\"$SELF\" param1=open param2=\"$target\" terminal=false" ;;
        error)
          echo "-- ❌ #$num $title | href=$url color=red"
          echo "-- -- $(menu_label "$(st_get --arg k "$key" '.seen[$k].error // ""')")"
          echo "-- -- retry | bash=\"$SELF\" param1=forget param2=\"$key\" terminal=false refresh=true" ;;
        *)
          echo "-- ○ #$num $title | href=$url" ;;
      esac
      echo "-- -- open PR on GitHub | href=$url"
    done < <("$JQ" -r '.open[] | [.repository.nameWithOwner, (.number|tostring), .title, .url] | @tsv' "$STATE" 2>/dev/null)
  fi

  echo "---"
  n_done=$(st_get '[.seen | to_entries[] | select(.value.status == "reviewed")] | length')
  echo "Finished reviews ($n_done)"
  while IFS=$'\t' read -r key target fin; do
    [[ -z "$key" ]] && continue
    echo "-- ✅ $(menu_label "${key##*/}") · ${fin:5:11} | bash=\"$SELF\" param1=open param2=\"$target\" terminal=false"
  done < <("$JQ" -r '[.seen | to_entries[] | select(.value.status == "reviewed")]
                     | sort_by(.value.finished) | reverse | .[:6][]
                     | [.key, (.value.open // ""), (.value.finished // "")] | @tsv' "$STATE" 2>/dev/null)

  echo "---"
  echo "Listening repos ($n_on)"
  while IFS=$'\t' read -r repo on; do
    [[ -z "$repo" ]] && continue
    if [[ "$on" == "true" ]]; then
      echo "-- ✓ $repo | bash=\"$SELF\" param1=toggle-repo param2=\"$repo\" terminal=false refresh=true"
    else
      echo "-- ✗ $repo | color=#888888 bash=\"$SELF\" param1=toggle-repo param2=\"$repo\" terminal=false refresh=true"
    fi
  done < <("$JQ" -r '.repos | to_entries[] | [.key, (.value.enabled|tostring)] | @tsv' "$CONFIG" 2>/dev/null)

  echo "---"
  if [[ "$master" == "true" ]]; then
    echo "Pause listening | bash=\"$SELF\" param1=toggle-master terminal=false refresh=true"
  else
    echo "Resume listening | bash=\"$SELF\" param1=toggle-master terminal=false refresh=true"
  fi
  echo "Refresh now | refresh=true"
  echo "Backend: $(cfg_get '.backend // "conductor"') · notify via $(cfg_get '.notify_via // "terminal-notifier"') | bash=\"$SELF\" param1=toggle-notify terminal=false refresh=true"
  echo "Open log | bash=\"$SELF\" param1=log terminal=false"
  echo "Last poll: $last | color=#888888"
}

init_files

case "${1:-}" in
  toggle-master) cfg_edit '.master = (.master | not)'; exit 0 ;;
  toggle-repo)   cfg_edit --arg r "$2" '.repos[$r].enabled = ((.repos[$r].enabled // false) | not)'; exit 0 ;;
  toggle-notify) cfg_edit '.notify_via = (if (.notify_via // "terminal-notifier") == "terminal-notifier" then "osascript" else "terminal-notifier" end)'; exit 0 ;;
  forget)        st_edit --arg k "$2" 'del(.seen[$k])'; exit 0 ;;
  open)          [[ -n "${2:-}" ]] && "$OPEN" "$2"; exit 0 ;;
  log)           "$OPEN" -t "$LOG"; exit 0 ;;
  poll-only)     check_completions; poll; exit $? ;;
esac

if mkdir "$LOCKDIR" 2>/dev/null; then
  trap 'rmdir "$LOCKDIR" 2>/dev/null' EXIT
  check_completions
  poll
fi
render
