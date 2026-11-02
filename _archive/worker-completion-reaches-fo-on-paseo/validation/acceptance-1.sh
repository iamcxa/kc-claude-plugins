#!/usr/bin/env bash
set -euo pipefail

# Step 1: pin the source and check that no tracked product changes exist.
WT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-worker-completion-reaches-fo-on-paseo'
BASE=146727ded0d4ce8014ea0b41a45dc3409d6b269b
HEAD_SHA=c129cb215c2630d08853eeffae0fd5a2ee7e40c6
test "$(git -C "$WT" rev-parse --show-toplevel)" = "$WT"
test "$(git -C "$WT" rev-parse HEAD)" = "$HEAD_SHA"
git -C "$WT" diff --exit-code "$HEAD_SHA" -- .
printf 'PASS: candidate %s; tracked product clean\n' "$HEAD_SHA"

# Step 2: exercise the extension boundary, exact instruction and agreement.
cd "$WT/kc-dev-flow-2/scripts"
python3 -B -m unittest -v \
  test_dispatch_records.DispatchRecordTests.test_paseo_completion_passes_only_with_the_listed_extension \
  test_dispatch_records.DispatchRecordTests.test_paseo_completion_requires_the_exact_line_inside_scope_notes \
  test_dispatch_records.DispatchRecordTests.test_paseo_extension_and_checker_share_the_completion_instruction

# Step 3: independently count words and compare the unchanged workflow sources.
cd "$WT"
python3 -B - <<'PY'
from pathlib import Path
import subprocess
base = "146727ded0d4ce8014ea0b41a45dc3409d6b269b"
extension = Path("kc-dev-flow-2/extensions/paseo/EXTENSION.md")
workflow = Path("kc-dev-flow-2/references/sd/workflow.md")
assert len(extension.read_text().split()) <= 819
assert len(workflow.read_text().split()) == 5781
for name in (str(workflow), "kc-dev-flow-2/scripts/lint-skills.py",
             "kc-dev-flow-2/scripts/test_sd_dispatch.py"):
    assert Path(name).read_bytes() == subprocess.check_output(["git", "show", base + ":" + name])
print("PASS: extension 819 words; workflow 5781; workflow, budget and dispatch pins unchanged")
PY

# Step 4: require the new architectural decision record and its required labels.
python3 -B '/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py' docs/adr --since "$BASE" --require 0048
