#!/usr/bin/env bash
# Run inside the container as the agent user, with the Hub-minted GH_TOKEN in the environment. Arg 1: the number of an open,
# non-draft pull request in the scratch repository. Prints status lines only, never the token.
set -uo pipefail
R=iamcxa/ops-inbox-probe-scratch
echo "== repositories the token reaches"; gh api /installation/repositories --jq '.repositories[].full_name'
echo "== another repository (expect 404 or 403)"; gh api repos/iamcxa/kc-claude-plugins --jq .full_name 2>&1 | head -2
echo "== push to the default branch (expect refusal)"
T=$(mktemp -d); gh repo clone "$R" "$T" -- -q && cd "$T" && git -c user.name=probe -c user.email=probe@example.invalid commit -q --allow-empty -m "ac2 default-branch probe" && git push origin HEAD:master 2>&1 | tail -3
echo "== merge pull request $1 (expect refusal)"; gh pr merge "$1" -R "$R" --squash 2>&1 | tail -3
