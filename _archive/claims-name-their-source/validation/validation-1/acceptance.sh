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

# Step 4: regrade the frozen runs without starting a model or changing the rubric.
# Expected: candidate P 6/6 and K 6/6, base P 1/3 and K 3/3; 22 prior attempts, 0 new.
# The wrong-count control with a report title grades true; without that title it grades false.
# These outputs demonstrate the known defect. They do not prove K meets the accepted behavior.
python3 -B "$EVIDENCE/audit_replay.py" "$CHECKOUT" --check-only

# Step 5: check decision records, then expose the trunk-versus-stack reservation difference.
# Expected: 52 ADR records, 0 legacy; origin/main guard exit 1 naming only parent ADR 0054.
# The same check against the pinned stacked parent passes. No reservation or base is changed.
python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since e1bee223c47a1cd534a665a47776b683375b34fc --require 0055
set +e
python3 "$PACKAGE/scripts/number_guards.py" check --repo "$CHECKOUT" --workflow-dir "$STATE/.." --task "$STATE/claims-name-their-source.md" --base e1bee223c47a1cd534a665a47776b683375b34fc --head f79711ca8d6325c1c14781342cf23855dd62b10a
guard_exit=$?
set -e
test "$guard_exit" -eq 1
echo "origin/main number guard exit=$guard_exit (known stacked-parent hold)"
python3 "$PACKAGE/scripts/number_guards.py" check --repo "$CHECKOUT" --workflow-dir "$STATE/.." --task "$STATE/claims-name-their-source.md" --base 128fe3e3fed70fa64ded8657f5a1b36933af3ced --head f79711ca8d6325c1c14781342cf23855dd62b10a

# Step 6: verify clean bytes and remove only this disposable checkout.
# Expected: no status entries; cleanup verified. The known behavioral and trunk holds remain.
test -z "$(git -C "$CHECKOUT" status --porcelain)"
cd "$ROOT"
git -C "$ROOT" worktree remove "$CHECKOUT"
trap - EXIT
test ! -e "$CHECKOUT"
echo 'Disposable checkout removed; acceptance observations match, delivery remains held.'

