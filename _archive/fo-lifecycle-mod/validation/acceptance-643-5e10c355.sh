# Acceptance for PR #643 head 5e10c355 (kc-dev-flow-2 lifecycle mod, after Captain amendment 6).
# Run: env -i HOME="$HOME" PATH="$PATH" TERM=dumb bash --noprofile --norc <this file>      (about 3 minutes, changes nothing in any repository)
# Needs: the checkout /Users/kent/conductor/workspaces/kc-claude-plugins/colombo, the Spacedock 0.27.0 plugin cache, `spacedock` on PATH (no real gh or network: a stub is used), python3,
#        the installed kc-dev-flow-2 0.22.1 package, and the two helper scripts beside this file.
set -u
SD=/Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.0
PKG=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1
HERE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/fo-lifecycle-mod/validation
WF=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2
TASK=$WF/.spacedock-state/fo-lifecycle-mod.md
REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo
echo "STEP 1: check out the PR head 5e10c355 (base origin/main 0cdb40a7) in a throwaway worktree; the README is at its word budget and names only delivery_gate.py of the three FO scripts; the one mod is 48 words"
C=$(mktemp -d)/pr643 && git -C "$REPO" worktree add --detach "$C" 5e10c355 >/dev/null 2>&1 && git -C "$C" log --oneline -1 | cut -c1-70
cd "$C" && python3 -B kc-dev-flow-2/scripts/lint-skills.py | head -1
for n in pr_watch.py delivery_gate.py observer_check.py; do echo "$n named in the README: $(grep -c "$n" kc-dev-flow-2/references/sd/workflow.md)"; done
echo "mod words: $(wc -w < kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md)"
echo "STEP 2: the mod sorts before pr-merge, adds no merge hook, merge guard still arms pr-merge, and the mod names no missing script (about 30 s)"
python3 -B kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root "$SD" > "$C/../sd.out" 2>&1; echo "exit $?"; grep -o 'PASS: the package mod sorts.*' "$C/../sd.out" | cut -c1-200
echo "STEP 3: the unit suites for the scripts (pr_watch, delivery_gate, observer_check) pass"
for t in test_pr_watch test_delivery_gate test_observer_check; do echo "$t: $(python3 -B kc-dev-flow-2/scripts/$t.py 2>&1 | tail -3 | tr '\n' ' ')"; done
echo "STEP 4: pr_watch.py tasks prints facts and the kept steps and never a merge-ask or hold line (stub gh, scratch workflow)"
python3 -B "$HERE/probe-643-5e10c355.py" "$C/kc-dev-flow-2" 2>&1 | grep -E '^\[|^PASS|^FAIL'; echo "exit ${PIPESTATUS[0]}"
echo "STEP 5: FO reads fewer words than on origin/main at every moment (recount from the shipped scripts behind a stub gh)"
B=$(mktemp -d) && git -C "$REPO" archive 0cdb40a7 kc-dev-flow-2 | tar -x -C "$B" && python3 -B "$HERE/recount-643-5e10c355.py" "$C/kc-dev-flow-2" "$B/kc-dev-flow-2" | tail -8; echo "exit ${PIPESTATUS[0]}"
echo "STEP 6: a copied mod must match the package byte for byte; the ADR is well formed; no number is taken twice"
D=$(mktemp -d); cp kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md "$D/"
cmp kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md "$D/kc-dev-flow-2.md"; echo "cmp exit $?"
echo x >> "$D/kc-dev-flow-2.md"; cmp kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md "$D/kc-dev-flow-2.md" 2>/dev/null; echo "cmp exit $? (after one appended byte)"
python3 -B "$PKG/scripts/adr_lint.py" docs/adr --since 0cdb40a7 --require 0015 | tail -1; echo "adr_lint exit ${PIPESTATUS[0]}"
python3 -B "$PKG/scripts/number_guards.py" check --repo "$C" --workflow-dir "$WF" --base 0cdb40a7 --task "$TASK" --head 5e10c355 | grep PASS; echo "number_guards exit ${PIPESTATUS[0]}"
cd "$REPO" && git worktree remove --force "$C" && echo "cleanup done"
