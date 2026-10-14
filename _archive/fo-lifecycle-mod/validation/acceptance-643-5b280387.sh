set -u
SD=/Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.0
STATE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state
WF=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2
echo "STEP 1: check out PR #643 head 5b280387 (base origin/main 0cdb40a7) in a throwaway worktree of the colombo checkout"
cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo && C=$(mktemp -d)/pr643 && git worktree add --detach "$C" 5b280387 && cd "$C" && git log --oneline -1
echo "STEP 2: the README is at its word budget (5476), names none of the three FO scripts, and the one mod is 48 words"
python3 -B kc-dev-flow-2/scripts/lint-skills.py; echo "exit $?"
grep -c 'observer_check.py\|pr_watch.py\|delivery_gate.py' kc-dev-flow-2/references/sd/workflow.md
wc -w < kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md
echo "STEP 3: the mod sorts before pr-merge and adds no merge hook, merge guard still arms pr-merge, the mod names no missing script (about 30 s)"
python3 -B kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root "$SD" > "$C/sd.out" 2>&1; echo "exit $?"
grep -o 'PASS: the package mod sorts.*' "$C/sd.out"
echo "STEP 4: the scripts print the next step (pr_watch tasks and wait, delivery_gate, observer_check)"
for t in test_pr_watch test_delivery_gate test_observer_check; do python3 -B kc-dev-flow-2/scripts/$t.py 2>&1 | tail -3 | tr '\n' ' '; echo; done
echo "STEP 5: FO reads fewer words at every moment than on origin/main (recount from the shipped scripts behind a stub gh)"
B=$(mktemp -d) && git archive 0cdb40a7 kc-dev-flow-2 | tar -x -C "$B" && python3 -B "$STATE/fo-lifecycle-mod/implementation/recount.py" "$C/kc-dev-flow-2" "$B/kc-dev-flow-2" | tail -8; echo "exit ${PIPESTATUS[0]}"
echo "STEP 6: a copied mod must match the package byte for byte; the ADR is well formed; no number is taken twice"
D=$(mktemp -d); cp kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md "$D/"
cmp kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md "$D/kc-dev-flow-2.md"; echo "cmp exit $?"
echo x >> "$D/kc-dev-flow-2.md"; cmp kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md "$D/kc-dev-flow-2.md"; echo "cmp exit $?"
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/adr_lint.py docs/adr --since 0cdb40a7 --require 0015; echo "adr_lint exit $?"
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/number_guards.py check --repo "$C" --workflow-dir "$WF" --base 0cdb40a7 --task "$STATE/fo-lifecycle-mod.md" --head 5b280387; echo "number_guards exit $?"
cd /Users/kent/conductor/workspaces/kc-claude-plugins/colombo && git worktree remove --force "$C" && echo "cleanup done"
