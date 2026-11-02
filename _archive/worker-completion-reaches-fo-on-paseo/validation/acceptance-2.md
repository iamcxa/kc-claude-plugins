# Minimal acceptance, rerun — PR #763

No screen changes. This checks local dispatch policy, wording, reading budget, the decision record and this rerun's dispatch record. It does not exercise native callbacks, placement or hosted CI: the Codex and Claude receipts are in `native-runs/README.md`, and the Claude row exists only after the First Officer (FO) records this worker's finish. A green run is not proof of those.

Needs: the exact candidate checked out at the absolute worktree the script names, the state checkout beside it, Python 3, Git, and the installed kc-dev-flow-2 0.34.0 package. No credentials, agents or writes.

Run: `bash --noprofile --norc <task folder>/validation/acceptance-2.sh`, or paste the script below into a fresh `bash`. Expected output is below the script; test timing varies.

```bash
#!/usr/bin/env bash
set -euo pipefail

# Step 1: pin the candidate and check no tracked product file differs from it.
RW='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree'
WT="$RW/.worktrees/spacedock-ensign-worker-completion-reaches-fo-on-paseo"
TASK="$RW/docs/dev2/.spacedock-state/worker-completion-reaches-fo-on-paseo"
PK='/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0'
BASE=146727ded0d4ce8014ea0b41a45dc3409d6b269b
HEAD_SHA=c129cb215c2630d08853eeffae0fd5a2ee7e40c6
test "$(git -C "$WT" rev-parse HEAD)" = "$HEAD_SHA"
git -C "$WT" diff --exit-code "$HEAD_SHA" -- .
printf 'PASS: candidate %s; tracked product clean\n' "$HEAD_SHA"

# Step 2: the checker accepts the final-reply line only where paseo is listed, and it matches the extension.
cd "$WT/kc-dev-flow-2/scripts"
python3 -B -m unittest \
  test_dispatch_records.DispatchRecordTests.test_paseo_completion_passes_only_with_the_listed_extension \
  test_dispatch_records.DispatchRecordTests.test_paseo_completion_requires_the_exact_line_inside_scope_notes \
  test_dispatch_records.DispatchRecordTests.test_paseo_extension_and_checker_share_the_completion_instruction

# Step 3: word counts and the workflow sources that must not change.
cd "$WT"
python3 -B - "$BASE" <<'PY'
from pathlib import Path
import subprocess, sys
base = sys.argv[1]
extension = Path("kc-dev-flow-2/extensions/paseo/EXTENSION.md")
workflow = Path("kc-dev-flow-2/references/sd/workflow.md")
assert len(extension.read_text().split()) <= 819
assert len(workflow.read_text().split()) == 5781
for name in (str(workflow), "kc-dev-flow-2/scripts/lint-skills.py", "kc-dev-flow-2/scripts/test_sd_dispatch.py"):
    assert Path(name).read_bytes() == subprocess.check_output(["git", "show", base + ":" + name])
print("PASS: extension 819 words; workflow 5781; workflow, budget and dispatch pins unchanged")
PY

# Step 4: the new decision record exists and passes the lint.
python3 -B "$PK/scripts/adr_lint.py" docs/adr --since "$BASE" --require 0048

# Step 5: this rerun's dispatch record passes; the only remaining complaint is the first run's record.
python3 -B kc-dev-flow-2/scripts/dispatch_records.py --names --strict "$TASK/dispatch/validation-2.md"
python3 -B kc-dev-flow-2/scripts/dispatch_records.py --coverage "$TASK.md" --stage validation
OUT="$(python3 -B kc-dev-flow-2/scripts/dispatch_records.py "$TASK" || true)"
test "$OUT" = "validation-1.md: needs a scope-notes line naming main as the completion recipient"
printf 'PASS: validation-2 complete; folder reports only: %s\n' "$OUT"
```

Observed, 2026-11-02, `env -i HOME="$HOME" PATH="$PATH" bash --noprofile --norc acceptance-2.sh`, exit 0:

```text
PASS: candidate c129cb215c2630d08853eeffae0fd5a2ee7e40c6; tracked product clean
...
----------------------------------------------------------------------
Ran 3 tests in 0.015s

OK
PASS: extension 819 words; workflow 5781; workflow, budget and dispatch pins unchanged
47 ADR file(s) checked, 0 legacy
dispatch coverage complete: validation
PASS: validation-2 complete; folder reports only: validation-1.md: needs a scope-notes line naming main as the completion recipient
```
