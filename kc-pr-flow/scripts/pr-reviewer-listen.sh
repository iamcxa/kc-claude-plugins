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
LOCK_CLAIM_GRACE_SECONDS=10
DISPATCH_STALE_SECONDS=300

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >>"$LOG"; }

# Config is intent and survives a wipe; state is derived and can be deleted.

init_files() {
  mkdir -p "$CFG_DIR" "$(dirname "$LOG")"
  [[ -s "$CONFIG" ]] || printf '%s\n' '{"listening":false,"backend":"conductor","notify_via":"terminal-notifier","repos":{}}' >"$CONFIG"
  [[ -s "$STATE"  ]] || printf '%s\n' '{"seen":{},"open":[],"last_poll":null,"last_error":null}' >"$STATE"
}

edit_json() { # edit_json <file> [jq-args...]
  local f="$1"; shift
  local tmp="$f.tmp.$$"
  if "$JQ" "$@" "$f" >"$tmp" 2>>"$LOG"; then mv "$tmp" "$f"
  else rm -f "$tmp"; log "edit failed on $f: $*"; return 1; fi
}

# An earlier build named the listening switch `master`, which reads as a branch in
# a repository context. Rename in place so a config keeps working untouched.
migrate_config() {
  [[ "$(cfg_get 'has("master")')" == "true" ]] || return 0
  cfg_edit '.listening = (.listening // .master) | del(.master)'
}

# Every write here is read-modify-rename, so a menu click landing during a tick can
# silently undo it. A held lock is also a total outage — nothing polls, nothing
# completes, and the menu looks merely idle — so a lock nobody released expires.
lock_acquire() { # 0 = acquired, 1 = someone else holds it
  local owner
  if [[ -d "$LOCKDIR" ]]; then
    owner=$(cat "$LOCKDIR/pid" 2>/dev/null)
    # Age alone cannot distinguish a dead owner from a slow one, and evicting a
    # live owner is worse than waiting: its EXIT trap would then release the new
    # owner's lock. Only a process that no longer exists gets reaped.
    if [[ -n "$owner" ]] && kill -0 "$owner" 2>/dev/null; then
      return 1
    fi
    # No pid yet means the owner is between mkdir and its own first write.
    if [[ -z "$owner" ]]; then
      local age
      age=$(( $(date -u +%s) - $(stat -f %m "$LOCKDIR" 2>/dev/null || echo 0) ))
      (( age < LOCK_CLAIM_GRACE_SECONDS )) && return 1
    fi
    rm -rf "$LOCKDIR" 2>/dev/null && log "reaped a lock whose owner (${owner:-unknown}) is gone"
  fi
  mkdir "$LOCKDIR" 2>/dev/null || return 1
  printf '%s\n' "$$" >"$LOCKDIR/pid"
  # Release only what we still own.
  trap '[[ "$(cat "$LOCKDIR/pid" 2>/dev/null)" == "$$" ]] && rm -rf "$LOCKDIR" 2>/dev/null' EXIT
}

# A menu click is a person waiting. Toggles are idempotent single-field writes, so
# after waiting they apply anyway; work that dispatches must not.
lock_wait() {
  local i
  for i in $(seq 1 20); do
    lock_acquire && return 0
    sleep 0.3
  done
  log "applied a menu action while a tick held the lock"
  return 1
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
    # The only channel here whose banner opens the review on click. -ignoreDnD is
    # deliberate: this notification exists because the user asked to be told, and a
    # review that lands during Do Not Disturb is exactly the one they would miss.
    local args=(-title "$title" -message "$sub" -ignoreDnD)
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

dispatch() { # dispatch <repo> <pr-number> <pr-url> <head-branch> <head-sha>
  local repo="$1" num="$2" url="$3" branch="$4" sha="$5" key="$1#$2"
  local be msg out job target

  be=$(backend_path)
  if [[ ! -x "$be" ]]; then
    mark_error "$key" "backend not executable: $be"; return 1
  fi

  # Claim the key before the backend call: a crash mid-create must not double-create.
  # An unwritten claim is no claim, so the backend must not run without it.
  if ! st_edit --arg k "$key" --arg u "$url" --arg b "$branch" --arg s "$sha" \
       '.seen[$k] = ((.seen[$k] // {}) + {status:"dispatching", url:$u, branch:$b, head_sha:$s, ts:(now|todate)})'; then
    log "dispatch $key aborted: could not record the claim"; return 1
  fi

  # Substituted in the shell, not through sed: a branch name may contain the
  # delimiter or an ampersand, which sed would treat as syntax.
  # One pass over the template: chained replacements would let an inserted value
  # (a branch legally named after a later placeholder) be substituted again.
  msg=$(mktemp -t prreview)
  if ! "$JQ" -rn --rawfile t "$PROMPT_TMPL" \
        --arg url "$url" --arg repo "$repo" --arg branch "$branch" --arg sha "$sha" \
        '$t | [splits("(__PR_URL__|__REPO__|__BRANCH__|__HEAD_SHA__)"; "g")] as $parts
         | ($t | [match("(__PR_URL__|__REPO__|__BRANCH__|__HEAD_SHA__)"; "g").string]) as $keys
         | reduce range(0; ($parts|length)) as $i ("";
             . + $parts[$i]
               + (if $i < ($keys|length)
                  then {"__PR_URL__":$url,"__REPO__":$repo,"__BRANCH__":$branch,"__HEAD_SHA__":$sha}[$keys[$i]]
                  else "" end))' >"$msg" 2>>"$LOG"; then
    rm -f "$msg"; mark_error "$key" "cannot render the dispatch prompt"; return 1
  fi
  out=$("$be" create "$repo" "$num" "$url" "$branch" "$msg" "$sha" 2>&1)
  local rc=$?
  rm -f "$msg"

  job=$(sed -n 's/^job_id=//p' <<<"$out" | head -1)
  target=$(sed -n 's/^open=//p' <<<"$out" | head -1)
  if [[ $rc -eq 3 ]]; then
    # The backend already produced a side effect it could not finish. Retrying
    # would create a second one, so this waits for a person.
    st_edit --arg k "$key" --arg e "$(tail -2 <<<"$out" | tr '\n' ' ' | cut -c1-200)" \
      '.seen[$k] += {status:"unconfirmed", error:$e, ts:(now|todate)}'
    notify "Review needs a look" "$key — $(tail -1 <<<"$out" | cut -c1-90)" "$url"
    log "dispatch $key UNCONFIRMED: $out"; return 1
  fi
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
  local be key job verdict errf reason
  be=$(backend_path)
  [[ -x "$be" ]] || return 0

  # A create whose result was never written stays "dispatching", where completion
  # never looks and polling refuses to re-run it. Reopen it for a retry.
  # Ambiguous, not failed: the backend may well have created the review. Retrying
  # from age alone would duplicate it, so this waits for a person.
  while IFS= read -r key; do
    [[ -z "$key" ]] && continue
    st_edit --arg k "$key" --arg e "the dispatch never confirmed a job — check the backend before retrying" \
      '.seen[$k] += {status:"unconfirmed", error:$e, ts:(now|todate)}'
    notify "Review needs a look" "$key — dispatch never confirmed" \
           "$(st_get --arg k "$key" '.seen[$k].url // empty')"
    log "unconfirmed dispatch $key"
  done < <("$JQ" -r --argjson max "$DISPATCH_STALE_SECONDS" \
            '.seen | to_entries[] | select(.value.status == "dispatching")
             | select(.value.ts != null) | select((now - (.value.ts|fromdate)) > $max) | .key' \
            "$STATE" 2>/dev/null)

  errf=$(mktemp)
  while IFS=$'\t' read -r key job; do
    [[ -z "$job" ]] && continue
    verdict=$("$be" status "$job" 2>"$errf") || continue
    case "$verdict" in
      done)
        st_edit --arg k "$key" '.seen[$k] += {status:"reviewed", finished:(now|todate)}'
        notify "Review ready" "$key — review finished, go read it" \
               "$(st_get --arg k "$key" '.seen[$k].open // empty')"
        log "completed $key"
        # The review skill covers whatever head it finds, so if the head moved after
        # dispatch this record names the wrong commit. Drop it and let GitHub — which
        # records the commit each review actually covered — answer next tick.
        local dispatched current
        dispatched=$(st_get --arg k "$key" '.seen[$k].head_sha // empty')
        current=$("$GH" pr view "${key#*#}" --repo "${key%#*}" --json headRefOid --jq .headRefOid 2>>"$LOG")
        if [[ -n "$dispatched" && -n "$current" && "$dispatched" != "$current" ]]; then
          # Dropping the record here would dispatch again whenever the finished
          # session posted nothing, so this holds for a person instead.
          st_edit --arg k "$key" --arg e "the head moved while this review ran — confirm which commit it covered" \
            '.seen[$k] += {status:"unconfirmed", error:$e, ts:(now|todate)}'
          notify "Review needs a look" "$key — the head moved while it ran" \
                 "$(st_get --arg k "$key" '.seen[$k].url // empty')"
          log "head moved during $key; holding as unconfirmed"
        fi ;;
      error)
        reason=$(tr '\n' ' ' <"$errf" | cut -c1-160)
        mark_error "$key" "${reason:-the backend reported this job cannot finish}"
        notify "Review failed" "$key — ${reason:-the backend gave no reason}" \
               "$(st_get --arg k "$key" '.seen[$k].url // empty')"
        log "failed $key: $reason" ;;
    esac
  done < <("$JQ" -r '.seen | to_entries[] | select(.value.status == "running") | select(.value.job_id) | [.key, .value.job_id] | @tsv' "$STATE" 2>/dev/null)
  rm -f "$errf"
}

# Has this account already submitted a review of exactly this commit?
# 0 = yes, 1 = no, 2 = could not ask. A failed lookup must not read as "no": that
# would dispatch a second review of a commit already reviewed.
# The filter emits one line per match rather than a per-page count, because
# --paginate runs --jq once per page and would print "0" for each of them.
# A commit this account pushed is part of the review it came from — the auto-fix
# path would otherwise treat its own fix as new code and review it again.
head_is_ours() { # <repo> <sha> <login>
  local who
  who=$("$GH" api "repos/$1/commits/$2" --jq '.author.login' 2>>"$LOG") || return 1
  [[ -n "$who" && "$who" == "$3" ]]
}

already_reviewed() { # <repo> <pr> <sha> <login>
  local found
  found=$("$GH" api "repos/$1/pulls/$2/reviews" --paginate \
            --jq ".[] | select(.user.login == \"$4\") | select(.commit_id == \"$3\") | .id" 2>>"$LOG") || return 2
  [[ -n "$found" ]]
}

poll() {
  local prs repo num url draft enabled status attempts fork n=0
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

  [[ "$(cfg_get '.listening')" == "true" ]] || return 0

  local me head branch sha seen_sha
  me=$("$GH" api user --jq .login 2>>"$LOG")
  # An empty login would make "has this account reviewed it" trivially false.
  if [[ -z "$me" ]]; then
    st_edit --arg e "could not resolve the GitHub identity" '.last_error = $e'
    return 1
  fi

  while IFS=$'\t' read -r repo num url draft; do
    [[ -z "$repo" ]] && continue
    (( n >= MAX_DISPATCH_PER_TICK )) && break
    [[ "$draft" == "true" ]] && continue
    enabled=$(cfg_get --arg r "$repo" '.repos[$r].enabled // false')
    [[ "$enabled" == "true" ]] || continue

    # What was reviewed is a commit, not a number: a re-request after a push has to
    # run again, and a re-request without one must not.
    head=$("$GH" pr view "$num" --repo "$repo" --json headRefName,headRefOid,isCrossRepository \
             --jq '[.headRefName, .headRefOid, (.isCrossRepository|tostring)] | @tsv' 2>>"$LOG")
    IFS=$'\t' read -r branch sha fork <<<"$head"
    if [[ -z "$branch" || -z "$sha" ]]; then
      mark_error "$repo#$num" "could not read the pull request head"; continue
    fi

    # A fork head is not a branch of this repository. Dispatching it would review
    # whatever a same-named local branch happens to hold, so refuse it visibly.
    if [[ "$fork" == "true" ]]; then
      mark_error "$repo#$num" "the head is in a fork, which this backend cannot check out"
      continue
    fi

    status=$(st_get --arg k "$repo#$num" '.seen[$k].status // empty')
    seen_sha=$(st_get --arg k "$repo#$num" '.seen[$k].head_sha // empty')
    attempts=$(st_get --arg k "$repo#$num" '.seen[$k].attempts // 0')
    if [[ "$seen_sha" == "$sha" ]]; then
      [[ -n "$status" && "$status" != "error" ]] && continue
      (( attempts >= MAX_ATTEMPTS )) && continue
    else
      # The head moved. Let the job already in flight finish rather than running two
      # reviews of the same pull request at once.
      [[ "$status" == "dispatching" || "$status" == "running" ]] && continue
      if [[ -n "$seen_sha" ]] && head_is_ours "$repo" "$sha" "$me"; then
        st_edit --arg k "$repo#$num" --arg s "$sha" '.seen[$k] += {head_sha:$s}'
        log "adopted our own follow-up commit on $repo#$num @ ${sha:0:8}"
        continue
      fi
      already_reviewed "$repo" "$num" "$sha" "$me"
      case $? in
        0) st_edit --arg k "$repo#$num" --arg u "$url" --arg s "$sha" \
             '.seen[$k] = {status:"reviewed", url:$u, head_sha:$s, finished:(now|todate), source:"github"}'
           log "already reviewed on GitHub $repo#$num @ ${sha:0:8}"
           continue ;;
        2) log "skipped $repo#$num: could not check GitHub for an existing review"
           continue ;;
      esac
    fi

    dispatch "$repo" "$num" "$url" "$branch" "$sha"
    n=$((n+1))
  done < <("$JQ" -r '.open[] | [.repository.nameWithOwner, (.number|tostring), .url, (.isDraft|tostring)] | @tsv' "$STATE" 2>/dev/null)
}

# The menu-bar host's own "start at login" setting is not scriptable, so autostart
# is driven through the login-item list instead. Reading or changing it needs
# Automation permission for System Events, which macOS prompts for on first use and
# which the menu reports as "unknown" if refused.
HOST_APP="${PR_LISTEN_HOST_APP:-/Applications/SwiftBar.app}"

login_state() { # on | off | unknown
  local names
  names=$(/usr/bin/osascript -e 'tell application "System Events" to get the name of every login item' 2>/dev/null) \
    || { echo unknown; return; }
  if grep -qF "$(basename "$HOST_APP" .app)" <<<"$names"; then echo on; else echo off; fi
}

login_toggle() {
  if [[ "$(login_state)" == "on" ]]; then
    /usr/bin/osascript -e "tell application \"System Events\" to delete login item \"$(basename "$HOST_APP" .app)\"" >/dev/null 2>&1
  else
    /usr/bin/osascript -e "tell application \"System Events\" to make login item at end with properties {path:\"$HOST_APP\", hidden:false}" >/dev/null 2>&1
  fi
}

menu_label() { printf '%s' "${1//|/／}"; }   # a literal pipe would end the SwiftBar line

render() {
  local listening n_on n_open n_todo n_done last err key status target title repo num fin on
  listening=$(cfg_get '.listening')
  n_on=$(cfg_get '[.repos | to_entries[] | select(.value.enabled == true)] | length')
  n_open=$(st_get '.open | length')
  # The badge counts what still wants attention, not what GitHub still lists: a
  # request stays open there until a review is submitted, long after this has
  # reviewed the commit.
  n_todo=$(st_get '. as $r | [$r.open[] | select(.isDraft != true)
             | ($r.seen[(.repository.nameWithOwner + "#" + (.number|tostring))].status // "new")
             | select(. != "reviewed")] | length')
  last=$(st_get '.last_poll // "never"')
  err=$(st_get '.last_error // empty')

  if [[ "$listening" != "true" ]]; then echo "👁 off"
  elif [[ -n "$err" ]];       then echo "👁 !"
  else                             echo "👁 $n_todo"; fi
  echo "---"

  if [[ -n "$err" ]]; then
    echo "⚠️ $(menu_label "$err") | color=red"
    echo "---"
  fi

  echo "Review requests ($n_open) | refresh=true"
  if [[ "$n_open" == "0" ]]; then
    echo "-- none"
  else
    while IFS=$'\t' read -r repo num title url; do
      [[ -z "$repo" ]] && continue
      key="$repo#$num"
      status=$(st_get --arg k "$key" '.seen[$k].status // "new"')
      # An entry adopted from GitHub has no review environment to open, so the
      # click falls back to the pull request itself.
      target=$(st_get --arg k "$key" '.seen[$k].open // .seen[$k].url // empty')
      title=$(menu_label "${title:0:48}")
      case "$status" in
        reviewed|running)
          echo "-- $([[ $status == reviewed ]] && echo ✅ || echo ⏳) #$num $title | bash=\"$SELF\" param1=open param2=\"$target\" terminal=false" ;;
        unconfirmed)
          echo "-- ⚠️ #$num $title | href=$url color=orange"
          echo "-- -- $(menu_label "$(st_get --arg k "$key" '.seen[$k].error // ""')")"
          echo "-- -- retry after checking the backend | bash=\"$SELF\" param1=forget param2=\"$key\" terminal=false refresh=true" ;;
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
  echo "Finished reviews ($n_done) | refresh=true"
  while IFS=$'\t' read -r key target fin; do
    [[ -z "$key" ]] && continue
    echo "-- ✅ $(menu_label "${key##*/}") · ${fin:5:11} | bash=\"$SELF\" param1=open param2=\"$target\" terminal=false"
  done < <("$JQ" -r '[.seen | to_entries[] | select(.value.status == "reviewed")]
                     | sort_by(.value.finished) | reverse | .[:6][]
                     | [.key, (.value.open // .value.url // ""), (.value.finished // "")] | @tsv' "$STATE" 2>/dev/null)

  echo "---"
  echo "Listening repos ($n_on) | refresh=true"
  while IFS=$'\t' read -r repo on; do
    [[ -z "$repo" ]] && continue
    if [[ "$on" == "true" ]]; then
      echo "-- ✓ $repo | bash=\"$SELF\" param1=toggle-repo param2=\"$repo\" terminal=false refresh=true"
    else
      echo "-- ✗ $repo | color=#888888 bash=\"$SELF\" param1=toggle-repo param2=\"$repo\" terminal=false refresh=true"
    fi
  done < <("$JQ" -r '.repos | to_entries[] | [.key, (.value.enabled|tostring)] | @tsv' "$CONFIG" 2>/dev/null)

  echo "---"
  if [[ "$listening" == "true" ]]; then
    echo "Pause listening | bash=\"$SELF\" param1=toggle-listening terminal=false refresh=true"
  else
    echo "Resume listening | bash=\"$SELF\" param1=toggle-listening terminal=false refresh=true"
  fi
  echo "Refresh now | refresh=true"
  echo "Backend: $(cfg_get '.backend // "conductor"') · notify via $(cfg_get '.notify_via // "terminal-notifier"') | bash=\"$SELF\" param1=toggle-notify terminal=false refresh=true"
  echo "Open log | bash=\"$SELF\" param1=log terminal=false"
  echo "Start at login: $(login_state) | bash=\"$SELF\" param1=toggle-login terminal=false refresh=true"
  echo "Last poll: $last | color=#888888"
}

init_files
migrate_config

case "${1:-}" in
  toggle-listening) lock_wait; cfg_edit '.listening = (.listening | not)'; exit 0 ;;
  toggle-repo)   lock_wait; cfg_edit --arg r "$2" '.repos[$r].enabled = ((.repos[$r].enabled // false) | not)'; exit 0 ;;
  toggle-notify) lock_wait; cfg_edit '.notify_via = (if (.notify_via // "terminal-notifier") == "terminal-notifier" then "osascript" else "terminal-notifier" end)'; exit 0 ;;
  forget)        lock_wait || { log "retry not applied: a tick holds the lock — click again"; exit 0; }
                 st_edit --arg k "$2" 'del(.seen[$k])'; exit 0 ;;
  open)          [[ -n "${2:-}" ]] && "$OPEN" "$2"; exit 0 ;;
  log)           "$OPEN" -t "$LOG"; exit 0 ;;
  toggle-login)  login_toggle; exit 0 ;;
  poll-only)     lock_wait || { log "poll-only skipped: a tick holds the lock"; exit 0; }
                 check_completions; poll; exit $? ;;
esac

if lock_acquire; then
  check_completions
  poll
fi
render
