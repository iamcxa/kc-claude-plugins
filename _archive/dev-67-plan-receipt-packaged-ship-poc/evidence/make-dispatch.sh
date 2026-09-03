#!/usr/bin/env bash
# make-dispatch.sh <ISSUE_ID> <BASE_SHA> <BASE_BRANCH_OR_EMPTY> -> writes /tmp/poc2/<id>/dispatch.md and work-item.md from the plan receipt
set -euo pipefail; ID=$1; BASE=$2; BASEBR=${3:-main}; D=/tmp/poc2/$ID; mkdir -p "$D"
python3 - "$ID" "$D" <<'PY'
import json,sys; ID,D=sys.argv[1],sys.argv[2]; r=json.load(open('/tmp/poc2/plan-receipt.json')); i=r['issues'][ID]
open(f"{D}/brief.md","w").write(i['description']); open(f"{D}/branch.txt","w").write(i['branch']); open(f"{D}/close_line.txt","w").write(i['close_line'])
title=i["title"]
t=open('/tmp/poc2/work-item-template.md').read().replace('__TITLE__', ID+': '+title.replace('"',"'")).replace('__ID__', ID); open(f"{D}/work-item.md","w").write(t)
PY
BR=$(cat "$D/branch.txt")
{
cat <<EOT
You are a kc-dev-flow build-stage worker in a disposable cloud workspace. Plugins kc-dev-flow and spacedock are expected to be preinstalled; if \`claude plugin list\` does not show kc-dev-flow, install it with: claude plugin marketplace add iamcxa/kc-claude-plugins && claude plugin install kc-dev-flow@kc-claude-plugins -y. Do not ask questions; if blocked, stop and report the blocker in the Evidence block.

## Step 1 — work item and Brief (standalone Pilot; you have no Linear access and need none)

Write this file byte-for-byte to \`.context/$ID-work-item.md\` (create \`.context/\`; it is gitignored):

\`\`\`markdown
EOT
cat "$D/work-item.md"
cat <<EOT
\`\`\`

The Brief this item executes (Linear Issue $ID, mirrored):

\`\`\`markdown
EOT
cat "$D/brief.md"
cat <<EOT
\`\`\`

## Step 2 — load the build contract

Run: python3 kc-dev-flow/scripts/profile-contract-loader.py --work-item .context/$ID-work-item.md --local-profile docs/dev/README.md --format text
Follow the emitted shared core, Pilot base, and build contract. The item is standalone: skip provider-reconcile steps; the Brief above is the planning authority.

## Step 3 — implement

- git fetch origin $BASEBR && git checkout -b $BR $BASE
- Satisfy every AC in the Brief; respect every Non-goal. Create scripts under scripts/ship-flow/ as the Brief names them; edit docs/dev/README.md only in a \`## Ship-flow runtime\` section (create it if absent, after \`## Task template\`).
- Run python3 scripts/kc-dev-flow-contract-test.py and record the exit code.
- Commit with a Conventional Commit scoped fix(kc-dev-flow): or docs(kc-dev-flow): as appropriate. One commit.
- RoboRev implementation-exit observation: record ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace) and continue.

## Step 4 — push the branch only. Do NOT open a pull request. Do NOT write to Linear.

git push origin HEAD:refs/heads/$BR

## Step 5 — final reply: exactly one fenced block, no prose before or after

\`\`\`
## Evidence
CANDIDATE_SHA: <full 40-hex sha of the pushed commit>
BRANCH: $BR
BASE_SHA: $BASE
FILES: <comma-separated changed files>
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit <code>
WITHOUT_IT_COMMAND: <ONE self-contained shell line, no reference to any file outside the committed tree, that exits 0 on this candidate and non-zero after WITHOUT_IT_REMOVED_VARIANT is applied>
WITHOUT_IT_REMOVED_VARIANT: <one git command that removes your change in a worktree at CANDIDATE_SHA, e.g. git checkout $BASE -- <files>>
WITHOUT_IT_OBSERVED: retained -> exit <code>; removed -> exit <code>
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: <evidence>
AC-2: <evidence>
AC-3: <evidence>
BLOCKER: none | <what stopped you and at which step>
\`\`\`
EOT
} > "$D/dispatch.md"
wc -c "$D/dispatch.md"; grep -c "curl\|tar -x" "$D/dispatch.md" || true
