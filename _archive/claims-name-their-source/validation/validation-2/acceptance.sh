#!/bin/bash
# Six local acceptance steps. Run unchanged with /bin/bash --noprofile --norc.
set -eu
export PYTHONDONTWRITEBYTECODE=1

# Step 1: create and verify the exact candidate in a disposable detached worktree.
# Expected: f79711ca8d6325c1c14781342cf23855dd62b10a, with no status entries.
ROOT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-claims-name-their-source'
STATE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
PACKAGE='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0'
EVIDENCE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKOUT="$(mktemp -d "$ROOT/.context/claims-acceptance.XXXXXX")"
git -C "$ROOT" worktree add --detach "$CHECKOUT" f79711ca8d6325c1c14781342cf23855dd62b10a
trap 'git -C "$ROOT" worktree remove "$CHECKOUT"' EXIT
cd "$CHECKOUT"
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = f79711ca8d6325c1c14781342cf23855dd62b10a
git -C "$CHECKOUT" rev-parse HEAD
test -z "$(git -C "$CHECKOUT" status --porcelain)"

# Step 2: lint the rule, observer list and word ledger.
# Expected: PASS and 5891 of 5891 words; exit 0.
python3 -B kc-dev-flow-2/scripts/lint-skills.py

# Step 3: exercise both gate entry points on pass, hold and missing-input paths.
# Expected: 2 tests, OK; the local pass output shows the source line before the final ask.
(
  cd "$CHECKOUT/kc-dev-flow-2/scripts"
  python3 -B -m unittest test_delivery_gate.DeliveryGateTests.test_claim_source_reminder_on_pass_hold_and_unreadable_input test_delivery_gate.QuestionTests.test_claim_source_reminder_on_pass_hold_and_unreadable_input
  python3 -B - <<'PY'
import test_delivery_gate as f
q=f.QuestionTests().ask("Admit it?")
c=f.run_check()
assert q[0]==c.code==0
print(q[1],end="")
print(c.out,end="")
PY
)

# Step 4: audit saved replay outputs and the Captain-accepted known limit.
# Expected: P 6/6 and K 6/6 by the old grader; K wrong-count control still false-passes.
# Independent reading stays K candidate 3/6, base 0/3; missing follow-up/hidden-limit controls reject.
python3 -B "$EVIDENCE/audit_replay.py" "$CHECKOUT" --check-only
python3 -B "$EVIDENCE/accepted_state.py"

# Step 5: verify ADR 0055, amended task form and the allowed stacked-parent number check.
# Expected: 52 ADRs, 0 legacy; design surfaces presentable; number guards pass.
# Parent PR #773 is still open. FO must repeat against fetched origin/main after it merges.
python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since 128fe3e3fed70fa64ded8657f5a1b36933af3ced --require 0055
python3 "$PACKAGE/scripts/design_surfaces.py" check "$STATE/claims-name-their-source.md"
python3 "$PACKAGE/scripts/number_guards.py" check --repo "$CHECKOUT" --workflow-dir "$STATE/.." --task "$STATE/claims-name-their-source.md" --base 128fe3e3fed70fa64ded8657f5a1b36933af3ced --head f79711ca8d6325c1c14781342cf23855dd62b10a

# Step 6: verify clean candidate bytes and remove this disposable checkout.
# Expected: no status entries; local acceptance observations match; cleanup verified.
test -z "$(git -C "$CHECKOUT" status --porcelain)"
cd "$ROOT"
git -C "$ROOT" worktree remove "$CHECKOUT"
trap - EXIT
test ! -e "$CHECKOUT"
echo 'Local acceptance matched; disposable checkout removed. Delivery and post-parent trunk recheck remain FO-owned.'
