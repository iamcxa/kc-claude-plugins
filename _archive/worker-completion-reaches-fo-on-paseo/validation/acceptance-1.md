# Minimal acceptance — PR #763

No user-visible screen changes. This checks local dispatch policy, wording, reading budget and the architectural decision record. It does not exercise native delivery, permission/cancellation events, live placement, hosted CI or the saved dispatch record; a green run does not resolve this validation's rejection.

Prerequisites: the exact candidate remains checked out at the absolute WT below; Python 3, Git and the named installed kc-dev-flow-2 0.34.0 package exist. These paths are declared dependencies, not portable defaults. No credentials, agents, repository configuration writes or product mutation are needed.

Run the four steps together in a fresh shell:

```bash
bash --noprofile --norc <<'ACCEPTANCE'
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
ACCEPTANCE
```

The executed file `acceptance-1.sh` contains exactly the script above (inside ACCEPTANCE). Validator ran `bash --noprofile --norc /tmp/validation-worker-completion-acceptance.sh`, unchanged, against c129cb215c2630d08853eeffae0fd5a2ee7e40c6; exit 0, under two seconds.

| Step | Expected and observed |
| --- | --- |
| 1 | PASS: candidate c129cb215c2630d08853eeffae0fd5a2ee7e40c6; tracked product clean |
| 2 | All three named tests `ok`; `Ran 3 tests in 0.016s`, `OK` (elapsed time varies). |
| 3 | PASS: extension 819 words; workflow 5781; workflow, budget and dispatch pins unchanged |
| 4 | 47 ADR file(s) checked, 0 legacy; exit 0 |

FO must rerun the full four steps before the gate and present each command with its observed output.
