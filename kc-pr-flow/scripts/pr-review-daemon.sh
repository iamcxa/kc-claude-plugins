#!/bin/bash
# pr-review-daemon.sh — PR Review Closed-Loop Daemon
# Runs claude -p in a loop, fresh session per iteration.
# Shipped with kc-pr-flow plugin. Start via mprocs or directly.
#
# Config: ~/.claude/kc-plugins-config/pr-flow/daemon.yaml
# Usage log: ~/.claude/audit/pr-daemon-usage.jsonl
#
# Environment overrides (take precedence over daemon.yaml):
#   PR_DAEMON_MODE=1   — bypass SessionStart superpowers hook (always set)
#   PR_DAEMON_AUDIT=1  — enable Bash command audit logging (always set)
#   POLL_INTERVAL       — seconds between iterations
#   PR_DAEMON_GATE      — custom gate script path
#   PR_DAEMON_SLACK_WEBHOOK — Slack webhook URL

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_DIR="$(pwd)"
PROMPT="$PLUGIN_DIR/reference/pr-review-loop.md"
CONFIG="$HOME/.claude/kc-plugins-config/pr-flow/daemon.yaml"

# Read config with env var overrides
read_config() {
  local key="$1" default="$2"
  local env_val=""
  # Check env override first
  case "$key" in
    poll_interval) env_val="${POLL_INTERVAL:-}" ;;
    slack_webhook) env_val="${PR_DAEMON_SLACK_WEBHOOK:-}" ;;
    gate_script)   env_val="${PR_DAEMON_GATE:-}" ;;
  esac
  if [[ -n "$env_val" ]]; then
    echo "$env_val"
    return
  fi
  # Read from YAML config
  if [[ -f "$CONFIG" ]] && command -v yq &>/dev/null; then
    local val
    val=$(yq -r ".$key // \"\"" "$CONFIG" 2>/dev/null)
    if [[ -n "$val" && "$val" != "null" ]]; then
      echo "$val"
      return
    fi
  fi
  echo "$default"
}

POLL_INTERVAL=$(read_config poll_interval 300)
MODEL=$(read_config model sonnet)
MAX_TURNS=$(read_config max_turns 30)
CI_GATE_CONTEXT=$(read_config ci_gate_context ci-gate)
COMMIT_SCOPE=$(read_config commit_scope review)
SLACK_WEBHOOK=$(read_config slack_webhook "")
GATE_SCRIPT=$(read_config gate_script "")

# Preflight checks
if [[ ! -f "$PROMPT" ]]; then
  echo "ERROR: Prompt file not found: $PROMPT" >&2
  exit 1
fi

if ! command -v claude &>/dev/null; then
  echo "ERROR: claude CLI not found in PATH" >&2
  exit 1
fi

if ! command -v gh &>/dev/null; then
  echo "ERROR: gh CLI not found in PATH" >&2
  exit 1
fi

echo "🤖 PR Review Daemon starting..."
echo "   Repo:     $REPO_DIR"
echo "   Plugin:   $PLUGIN_DIR"
echo "   Config:   $CONFIG"
echo "   Model:    $MODEL"
echo "   Interval: ${POLL_INTERVAL}s"

# Notification helper: macOS + Slack (optional)
notify() {
  local title="$1" body="$2" url="${3:-}"

  # macOS notification
  if [[ "$(uname)" == "Darwin" ]]; then
    if command -v terminal-notifier &>/dev/null; then
      local tn_args=(-title "$title" -message "$body" -sound Submarine -group pr-daemon)
      [[ -n "$url" ]] && tn_args+=(-open "$url")
      terminal-notifier "${tn_args[@]}" &>/dev/null || true
    else
      osascript -e "display notification \"$body\" with title \"$title\" sound name \"Submarine\""
      [[ -n "$url" ]] && echo "🔗 $url"
    fi
  else
    echo "⚠️  Notification skipped (macOS only): $title — $body"
  fi

  # Slack notification
  if [[ -n "$SLACK_WEBHOOK" ]]; then
    local slack_body="$body"
    [[ -n "$url" ]] && slack_body="$body\n<$url|View PR>"
    curl -s -X POST "$SLACK_WEBHOOK" \
      -H 'Content-Type: application/json' \
      -d "{\"text\":\"🤖 *${title}*\n${slack_body}\"}" \
      >/dev/null 2>&1 || echo "⚠️  Slack notification failed"
  fi
}

# Persistent usage log (survives daemon restarts)
USAGE_LOG="$HOME/.claude/audit/pr-daemon-usage.jsonl"
mkdir -p "$(dirname "$USAGE_LOG")"

# Restore cumulative totals from usage log
if [[ -s "$USAGE_LOG" ]]; then
  total_cost=$(jq -rs '[.[].cost] | add // 0 | . * 10000 | round / 10000' < "$USAGE_LOG" | sed 's/^\./0./')
  total_input_tokens=$(jq -rs '[.[].in] | add // 0' < "$USAGE_LOG")
  total_output_tokens=$(jq -rs '[.[].out] | add // 0' < "$USAGE_LOG")
  total_turns=$(jq -rs '[.[].turns] | add // 0' < "$USAGE_LOG")
  total_iterations=$(jq -rs 'length' < "$USAGE_LOG")
  current_month=$(date -u +%Y-%m)
  month_cost=$(jq -rs "[.[] | select(.ts[:7] == \"$current_month\")] | [.[].cost] | add // 0 | . * 10000 | round / 10000" < "$USAGE_LOG" | sed 's/^\./0./')
  month_iters=$(jq -rs "[.[] | select(.ts[:7] == \"$current_month\")] | length" < "$USAGE_LOG")
else
  total_cost="0" total_input_tokens=0 total_output_tokens=0 total_turns=0 total_iterations=0
  current_month=$(date -u +%Y-%m)
  month_cost="0" month_iters=0
fi

echo "   Usage log: $USAGE_LOG"
echo "   All time:  ${total_iterations} iterations | \$${total_cost}"
echo "   This month (${current_month}): ${month_iters} iterations | \$${month_cost}"
echo ""

iteration=0
while true; do
  iteration=$((iteration + 1))
  echo "━━━ Iteration #$iteration — $(date '+%Y-%m-%d %H:%M:%S') ━━━"

  cd "$REPO_DIR"

  # Pre-flight gate: decide whether to invoke claude -p
  if [[ -n "$GATE_SCRIPT" && -x "$GATE_SCRIPT" ]]; then
    # Custom gate script: exit 0 = proceed, exit 1 = skip
    if ! GATE_MSG=$("$GATE_SCRIPT" 2>&1); then
      echo "⏭️  Gate: ${GATE_MSG:-skipped by custom gate}"
      echo ""
      echo "💤 Sleeping ${POLL_INTERVAL}s until next iteration..."
      sleep "$POLL_INTERVAL"
      continue
    fi
    echo "📋 Gate: ${GATE_MSG:-passed}"
  else
    # Default gate: non-draft open PRs with ci-gate passed
    PR_NUMS=$(gh pr list --state open --json number,isDraft --jq '[.[] | select(.isDraft == false) | .number] | .[]' 2>/dev/null || true)
    if [[ -z "$PR_NUMS" ]]; then
      echo "⏭️  No open non-draft PRs. Skipping claude -p."
      echo ""
      echo "💤 Sleeping ${POLL_INTERVAL}s until next iteration..."
      sleep "$POLL_INTERVAL"
      continue
    fi

    # Check ci-gate status for each PR (skip if ci_gate_context == "none")
    if [[ "$CI_GATE_CONTEXT" != "none" ]]; then
      actionable=0
      for pr in $PR_NUMS; do
        sha=$(gh pr view "$pr" --json commits --jq '.commits[-1].oid' 2>/dev/null || true)
        [[ -z "$sha" ]] && continue
        ci_state=$(gh api "repos/{owner}/{repo}/statuses/$sha" --jq "[.[] | select(.context==\"$CI_GATE_CONTEXT\")] | first | .state // \"none\"" 2>/dev/null || echo "none")
        # success = CI passed, none = ci-gate not required for this PR
        if [[ "$ci_state" == "success" || "$ci_state" == "none" ]]; then
          actionable=$((actionable + 1))
        fi
      done

      if [[ "$actionable" == "0" ]]; then
        echo "⏭️  $(echo "$PR_NUMS" | wc -w | tr -d ' ') open PR(s) but none with $CI_GATE_CONTEXT passed. Skipping claude -p."
        echo ""
        echo "💤 Sleeping ${POLL_INTERVAL}s until next iteration..."
        sleep "$POLL_INTERVAL"
        continue
      fi
      echo "📋 ${actionable} PR(s) with $CI_GATE_CONTEXT passed."
    else
      echo "📋 $(echo "$PR_NUMS" | wc -w | tr -d ' ') open non-draft PR(s) found (ci-gate check disabled)."
    fi
  fi

  OUTPUT=$(PR_DAEMON_MODE=1 PR_DAEMON_AUDIT=1 claude -p "$(cat "$PROMPT")" \
    --model "$MODEL" \
    --plugin-dir "$PLUGIN_DIR" \
    --max-turns "$MAX_TURNS" \
    --output-format json \
    --allowedTools "Bash,Read,Write,Edit,Glob,Grep,Agent,Skill,ToolSearch" \
    2>/dev/null) || echo "⚠️  claude -p exited with code $?"

  # Parse JSON output
  if echo "$OUTPUT" | jq -e '.result' &>/dev/null; then
    # Display model response
    echo "$OUTPUT" | jq -r '.result // empty'

    # Extract usage stats
    iter_cost=$(echo "$OUTPUT" | jq -r '.total_cost_usd // 0 | . * 10000 | round / 10000')
    iter_input=$(echo "$OUTPUT" | jq -r '.usage.input_tokens // 0')
    iter_output=$(echo "$OUTPUT" | jq -r '.usage.output_tokens // 0')
    iter_cache_read=$(echo "$OUTPUT" | jq -r '.usage.cache_read_input_tokens // 0')
    iter_cache_create=$(echo "$OUTPUT" | jq -r '.usage.cache_creation_input_tokens // 0')
    iter_turns=$(echo "$OUTPUT" | jq -r '.num_turns // 0')
    iter_duration=$(echo "$OUTPUT" | jq -r '.duration_ms // 0')
    iter_duration_s=$(echo "scale=1; $iter_duration / 1000" | bc 2>/dev/null | sed 's/^\./0./' || echo "?")

    # Accumulate totals
    total_cost=$(echo "scale=4; ($total_cost + $iter_cost) / 1" | bc 2>/dev/null | sed 's/^\./0./' || echo "?")
    total_input_tokens=$((total_input_tokens + iter_input))
    total_output_tokens=$((total_output_tokens + iter_output))
    total_turns=$((total_turns + iter_turns))

    # Check for human intervention signals
    result_text=$(echo "$OUTPUT" | jq -r '.result // empty')
    if echo "$result_text" | grep -qiE 'NEEDS HUMAN|STUCK|PUSH BACK|BLOCKED|HUMAN NEEDED|daemon-stuck'; then
      pr_num=$(echo "$result_text" | grep -oE '#[0-9]+' | head -1 | tr -d '#' || echo "")
      pr_url=""
      [[ -n "$pr_num" ]] && pr_url=$(gh pr view "$pr_num" --json url --jq '.url' 2>/dev/null || echo "")
      notify "PR Daemon — Action Required" "Human intervention needed #${pr_num}" "$pr_url"
      echo "🔔 Notification sent — human intervention needed"
    fi

    # Persist iteration to usage log
    action=$(echo "$result_text" | grep -oE 'Action taken: [^|]+' | head -1 || echo "")
    echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"iter\":$iteration,\"cost\":$iter_cost,\"in\":$iter_input,\"out\":$iter_output,\"cache_read\":$iter_cache_read,\"cache_create\":$iter_cache_create,\"turns\":$iter_turns,\"duration_ms\":$iter_duration,\"action\":\"${action}\"}" >> "$USAGE_LOG"

    # Per-iteration stats
    echo ""
    echo "📊 Iteration: ${iter_input} in / ${iter_output} out (cache: ${iter_cache_read} read, ${iter_cache_create} create) | ${iter_turns} turns | ${iter_duration_s}s | \$${iter_cost}"
    echo "📊 Cumulative: ${total_input_tokens} in / ${total_output_tokens} out | ${total_turns} turns | \$${total_cost}"
  else
    # Non-JSON output (fallback)
    echo "$OUTPUT"
  fi

  echo ""
  echo "💤 Sleeping ${POLL_INTERVAL}s until next iteration..."
  sleep "$POLL_INTERVAL"
done
