# Four-step acceptance

No changed screen. Requires Git, Python 3, the named local clone containing the pinned head/base, and the declared installed dev2 0.33.0 package. Runs in under five minutes. Does not cover source authenticity, semantic coverage of a ruling, historical enforcement, hosted checks, merge, or adoption.

Run exactly in a fresh shell:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/validation-rerun-waits-for-captain-ruling/validation/acceptance.sh
```

The four steps and expected observations (complete script):

```bash
#!/usr/bin/env bash
set -euo pipefail
# Prerequisites: Git, Python 3, the named repository and installed dev2 0.33.0 package.
# No changed screen. This checks local CLI behavior, not source authenticity or delivery.

# Step 1: isolate the exact candidate. Expected: b8a66e826c7524fa944a7165296acba94b3f5e13.
REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-validation-rerun-waits-for-captain-ruling
AC_WT=$(mktemp -d /tmp/pr750-accept.XXXXXX)
git -C "$REPO" worktree add --detach "$AC_WT" b8a66e826c7524fa944a7165296acba94b3f5e13
trap 'cd /tmp; git -C "$REPO" worktree remove "$AC_WT"' EXIT
cd "$AC_WT"
git -C "$AC_WT" rev-parse HEAD

# Step 2: before/after a ruling, fresh/follow-up records and free-form recovery. Expected: 2 tests, OK.
python3 -B kc-dev-flow-2/scripts/test_dispatch_records.py LiveValidationRulingTests.test_fresh_followup_and_filename_one_hold_then_native_ruling_clears_without_input_edits LiveValidationRulingTests.test_freeform_then_on_touch_amendment_and_partial_supported_ruling

# Step 3: pinned incident and compatibility cases. Expected: 2 tests, OK (15 predicate passes / 12 refusals; incident 4 refuse / 2 pass; 3 legacy CLI refusals and supported-form passes).
python3 -B kc-dev-flow-2/scripts/test_dispatch_records.py SavedValidationRulingTests

# Step 4: required decision record. Expected: 43 ADR file(s) checked, 0 legacy; exit 0.
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0/scripts/adr_lint.py docs/adr --since da5053febb546b2a7cf6ffe676b0d5a8b7e338a4 --require 0045
```

Observed output, exit 0 (2026-10-29):

```text
Preparing worktree (detached HEAD b8a66e826)
HEAD is now at b8a66e826 test(kc-dev-flow-2): retain exact saved validation dispatches
b8a66e826c7524fa944a7165296acba94b3f5e13
..
----------------------------------------------------------------------
Ran 2 tests in 2.815s

OK
..
----------------------------------------------------------------------
Ran 2 tests in 26.818s

OK
43 ADR file(s) checked, 0 legacy
```

The first sandbox attempt could not create the Git administration directory; the exact unchanged script passed with authorized filesystem access. Its EXIT trap removed the temporary checkout.
