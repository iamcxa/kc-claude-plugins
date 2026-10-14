set -u
echo "STEP 1: check out PR #643 head 33295355 in a throwaway worktree"
cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo && C=$(mktemp -d)/pr643 && git worktree add --detach "$C" 33295355 && cd "$C" && git log --oneline -1
echo "STEP 2: README stays under its word budget"
python3 -B kc-dev-flow-2/scripts/lint-skills.py; echo "exit $?"
echo "STEP 3: the README no longer names the three FO scripts; each name sits in a mod"
grep -c 'observer_check.py\|pr_watch.py\|delivery_gate.py' kc-dev-flow-2/references/sd/workflow.md
grep -o 'observer_check.py\|pr_watch.py\|delivery_gate.py' kc-dev-flow-2/references/sd/mods/*.md | sort -u
echo "STEP 4: the mods sort around pr-merge and merge guard still arms pr-merge (about 30 s)"
python3 -B kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root /Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.0 | grep 'PASS: the two package mods'; echo "exit ${PIPESTATUS[0]}"
echo "STEP 5: a copied mod must match the package byte for byte"
D=$(mktemp -d); cp kc-dev-flow-2/references/sd/mods/*.md "$D/"
cmp kc-dev-flow-2/references/sd/mods/watch-and-learn.md "$D/watch-and-learn.md"; echo "cmp exit $?"
echo x >> "$D/watch-and-learn.md"; cmp kc-dev-flow-2/references/sd/mods/watch-and-learn.md "$D/watch-and-learn.md"; echo "cmp exit $?"
echo "STEP 6: the new ADR is well formed"
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/adr_lint.py docs/adr --since 656543f4; echo "exit $?"
cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo && git worktree remove --force "$C" && echo "cleanup done"
