# Minimal acceptance — repaired head fef0ae5fa

No user-visible screen changes. Requires this local checkout at the named head, Python 3, Git and the installed package path specified below. Run these five steps together in a fresh shell with:

```bash
env -i PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/Users/kent/.local/bin PYTHONDONTWRITEBYTECODE=1 /bin/bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/worker-completion-reaches-fo-on-paseo/validation/acceptance-3.sh
```

Expected: step 1 confirms exact clean head and two changed files; step 2 reports four tests OK (including five mutation subcases); step 3 reports 819/5781 and unchanged workflow sources; step 4 reports 47 ADR files, 0 legacy; step 5 reports complete coverage and only the preserved historical diagnostic. Overall exit 0. Native callbacks, hosted checks, adoption and delivery are outside this script. Git on this clean macOS environment warns that DARWIN_USER_TEMP_DIR is unavailable and uses /tmp; the checks still exit 0.

## Exact five-step script

```bash
#!/usr/bin/env bash
set -euo pipefail

# Step 1: verify the exact candidate and the repair's two-file boundary.
WT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-worker-completion-reaches-fo-on-paseo'
TASK='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/worker-completion-reaches-fo-on-paseo'
PK='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0'
BASE=146727ded0d4ce8014ea0b41a45dc3409d6b269b
OLD=c129cb215c2630d08853eeffae0fd5a2ee7e40c6
HEAD_SHA=fef0ae5fa79a77315ce6fce069c0a3ddf06e2daf
test "$(git -C "$WT" rev-parse HEAD)" = "$HEAD_SHA"
git -C "$WT" diff --exit-code "$HEAD_SHA" -- .
test "$(git -C "$WT" diff --name-only "$OLD" "$HEAD_SHA")" = "$(printf '%s\n' kc-dev-flow-2/scripts/dispatch_records.py kc-dev-flow-2/scripts/test_dispatch_records.py)"
printf 'PASS: candidate %s; tracked product clean; only checker and tests changed since prior validation\n' "$HEAD_SHA"

# Step 2: exercise extension membership, instruction agreement and five mutations.
cd "$WT/kc-dev-flow-2/scripts"
python3 -B -m unittest \
  test_dispatch_records.DispatchRecordTests.test_paseo_completion_passes_only_with_the_listed_extension \
  test_dispatch_records.DispatchRecordTests.test_paseo_completion_requires_the_exact_line_inside_scope_notes \
  test_dispatch_records.DispatchRecordTests.test_paseo_extension_and_checker_share_the_completion_instruction \
  test_dispatch_records.PaseoCompletionMutationTests

# Step 3: recount the unchanged documentation and workflow sources.
cd "$WT"
python3 -B - "$BASE" <<'PY'
from pathlib import Path
import subprocess, sys
base = sys.argv[1]
extension = Path('kc-dev-flow-2/extensions/paseo/EXTENSION.md')
workflow = Path('kc-dev-flow-2/references/sd/workflow.md')
assert len(extension.read_text().split()) == 819
assert len(workflow.read_text().split()) == 5781
for name in (str(workflow), 'kc-dev-flow-2/scripts/lint-skills.py', 'kc-dev-flow-2/scripts/test_sd_dispatch.py'):
    assert Path(name).read_bytes() == subprocess.check_output(['git', 'show', base + ':' + name])
print('PASS: extension 819 words; workflow 5781; workflow, budget and dispatch pins unchanged')
PY

# Step 4: validate the required decision record.
python3 -B "$PK/scripts/adr_lint.py" docs/adr --since "$BASE" --require 0048

# Step 5: current dispatch passes; retain the known historical-record diagnostic.
python3 -B kc-dev-flow-2/scripts/dispatch_records.py --names --strict "$TASK/dispatch/validation-3.md"
python3 -B kc-dev-flow-2/scripts/dispatch_records.py --coverage "$TASK.md" --stage validation
RC=0
OUT="$(python3 -B kc-dev-flow-2/scripts/dispatch_records.py "$TASK")" || RC=$?
test "$RC" = 1
test "$OUT" = 'validation-1.md: needs a scope-notes line naming main as the completion recipient'
printf 'PASS: validation-3 complete; folder reports only the preserved validation-1 diagnostic (exit 1)\n'
```

## Observed output

```text
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
PASS: candidate fef0ae5fa79a77315ce6fce069c0a3ddf06e2daf; tracked product clean; only checker and tests changed since prior validation
....
----------------------------------------------------------------------
Ran 4 tests in 1.375s

OK
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
PASS: extension 819 words; workflow 5781; workflow, budget and dispatch pins unchanged
47 ADR file(s) checked, 0 legacy
dispatch coverage complete: validation
PASS: validation-3 complete; folder reports only the preserved validation-1 diagnostic (exit 1)
```

Observed exit: 0.
