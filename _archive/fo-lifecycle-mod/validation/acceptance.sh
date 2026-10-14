set -u
PKG=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1
SD=/Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.0
STATE_TASK=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/fo-lifecycle-mod.md
WF=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2
echo "STEP 1: check out PR #643 head d6a427aa (merge of origin/main 0cdb40a7) in a throwaway worktree"
cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo && C=$(mktemp -d)/pr643 && git worktree add --detach "$C" d6a427aa && cd "$C" && git log --oneline -1
echo "STEP 2: README stays at or under its word budget (5501)"
python3 -B kc-dev-flow-2/scripts/lint-skills.py; echo "exit $?"
echo "STEP 3: the README no longer names the three FO scripts; each name sits in a mod"
grep -c 'observer_check.py\|pr_watch.py\|delivery_gate.py' kc-dev-flow-2/references/sd/workflow.md
grep -o 'observer_check.py\|pr_watch.py\|delivery_gate.py' kc-dev-flow-2/references/sd/mods/*.md | sort -u
echo "STEP 4: mods sort around pr-merge, merge guard still arms pr-merge, and both Codex fixes hold (about 30 s)"
python3 -B kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root "$SD" > "$C/sd.out" 2>&1; echo "exit $?"
grep -o 'PASS: the two package mods.*' "$C/sd.out"
grep -o 'worker-opens-draft-pr\|learn-step-needs-learn' "$C/sd.out" | sort -u
echo "STEP 5: a copied mod must match the package byte for byte"
D=$(mktemp -d); cp kc-dev-flow-2/references/sd/mods/*.md "$D/"
cmp kc-dev-flow-2/references/sd/mods/watch-and-learn.md "$D/watch-and-learn.md"; echo "cmp exit $?"
echo x >> "$D/watch-and-learn.md"; cmp kc-dev-flow-2/references/sd/mods/watch-and-learn.md "$D/watch-and-learn.md"; echo "cmp exit $?"
echo "STEP 6: the new ADR is well formed and no number is taken twice"
python3 -B $PKG/scripts/adr_lint.py docs/adr --since 0cdb40a7 --require 0015; echo "adr_lint exit $?"
python3 -B $PKG/scripts/number_guards.py check --repo "$C" --workflow-dir "$WF" --base 0cdb40a7 --task "$STATE_TASK" --head d6a427aa; echo "number_guards exit $?"
cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo && git worktree remove --force "$C" && echo "cleanup done"
