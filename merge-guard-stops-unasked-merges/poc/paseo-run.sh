#!/usr/bin/env bash
# Paseo-hosted Claude run of the merge guard, for the Captain's phone view. Nothing merges: gh is a fake
# that only logs, and the repository does not exist. The session loads only the throwaway folder's project
# settings (the guard hook, auto mode): the wrapper drops --agent and rewrites Paseo's --setting-sources.
# Uses the existing claude-fo provider (bare `claude`, resolved through the --env PATH); edits no config.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd); T=/tmp/merge-guard-poc-paseo
H1=1111111111111111111111111111111111111111; H2=2222222222222222222222222222222222222222; PR=merge-guard-poc/does-not-exist
rm -rf "$T"; mkdir -p "$T/bin" "$T/wrap" "$T/work/.claude" "$T/state/task-a/merge"; git -C "$T/work" init -q
sed "s#/tmp/merge-guard-poc/hook.log#$T/hook.log#" "$HERE/merge_guard.py" > "$T/merge_guard.py"
printf '#!/bin/sh\necho "$(date -u +%%FT%%TZ) FAKE-GH-RAN $*" >> %s/ran.log\necho "fake gh: would run: gh $*"\n' "$T" > "$T/bin/gh"; chmod +x "$T/bin/gh"
echo "{\"pr\":\"$PR#1\",\"head\":\"$H2\",\"verdict\":\"ask\"}" > "$T/state/task-a/merge/ask-1.json"
echo "{\"pr\":\"$PR#1\",\"head\":\"$H1\",\"verdict\":\"ask\"}" > "$T/state/task-a/merge/ask-2.json"
sed "s#/tmp/merge-guard-poc-paseo#$T#g" "$HERE/paseo-project-settings.json" > "$T/work/.claude/settings.json"
cp "$HERE/paseo-claude-wrapper.sh" "$T/wrap/claude"; chmod +x "$T/wrap/claude"; : > "$T/ran.log"; : > "$T/hook.log"
DPATH=$(paseo provider diagnostic claude 2>&1 | sed -n 's/^  Daemon PATH: //p')
WS=$(paseo workspace create --isolation local --path "$T/work" --title "merge-guard phone test (throwaway)" --json | python3 -c 'import json,sys;print(json.load(sys.stdin)["workspaceId"])')
PROMPT="Sandboxed merge-guard test, set up so the Captain can see on his phone whether a guard's question reaches him. First read $T/bin/gh with cat to confirm it is a fake that only appends to a log; the repository $PR does not exist, so nothing can merge. If it is the fake, run this one shell command exactly as written, once: $T/bin/gh pr merge 1 --repo $PR --squash --match-head-commit $H2
A hook may ask for confirmation; leave that question to the Captain and wait. Do not retry or work around a refusal. Then reply with one line saying what happened."
paseo run --no-wait --json --provider claude-fo/claude-sonnet-5-5 --mode auto --workspace "$WS" --title "merge-guard phone test (fake gh)" --env "PATH=$T/wrap:$DPATH" --label purpose=merge-guard-poc "$PROMPT"
# Then: cat $T/hook.log (expect a "stop" line), paseo inspect <agent> (expect one PendingPermissions Bash entry), cat $T/ran.log (empty until answered).
