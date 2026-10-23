#!/usr/bin/env bash
# Open the setup Draft PR in the project repository: ops-gate.yml pinned to a kc-claude-plugins commit, and the ops workflow README.
# usage: make-setup-pr.sh <owner/name> <kc-claude-plugins commit, 40 hex> <captain GitHub login>
# env: OPS_GIT_BASE overrides https://github.com; OPS_NO_PR=1 pushes the branch and skips `gh pr create`.
set -euo pipefail
P=${1:?usage: make-setup-pr.sh <owner/name> <sha> <captain-login>}
SHA=${2:?}
CAPTAIN=${3:?}
[[ "$SHA" =~ ^[0-9a-f]{40}$ ]] || { echo "the commit must be 40 hex characters" >&2; exit 2; }
HERE=$(cd "$(dirname "$0")/.." && pwd)
BASE=${OPS_GIT_BASE:-https://github.com}
T=$(mktemp -d)
git clone -q --depth 1 "$BASE/$P.git" "$T/p"
cd "$T/p"
git switch -q -c ops-inbox-setup
mkdir -p .github/workflows docs/ops
sed "s/__KC_OPS_INBOX_SHA__/$SHA/" "$HERE/gate/ops-gate.yml" > .github/workflows/ops-gate.yml
cp "$HERE/ops-workflow/README.md" docs/ops/README.md
git add .github/workflows/ops-gate.yml docs/ops/README.md
git commit -q -m "chore(ops): connect the ops inbox"
git push -q origin ops-inbox-setup
if [ -z "${OPS_NO_PR:-}" ]; then
  gh variable set OPS_CAPTAIN_LOGIN -R "$P" --body "$CAPTAIN"
  gh pr create -R "$P" --draft --head ops-inbox-setup --title "chore(ops): connect the ops inbox" \
    --body "Adds the ops-gate workflow (pinned to kc-claude-plugins $SHA) and the ops workflow README. Merge it before any ops pull request opens."
fi
