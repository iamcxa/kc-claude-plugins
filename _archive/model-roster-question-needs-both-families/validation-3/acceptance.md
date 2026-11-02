# Five-step acceptance — exact candidate c2643dae

Prerequisites: the assigned source checkout and candidate object, Python 3, Git, bash, the assigned 0.34.0 package, and this task native-runs/final/receipts.json. All paths are explicit below. No GUI changed. This script starts no agents and does not cover release, consumer adoption or local review.

Expected: STEP 1 through STEP 5 PASS; Opus/high, Opus/low, Sol/xhigh and Astra/xhigh each have a later finished receipt in FO records; lint and ADR output passes; release parity is consistent; the temporary checkout is removed.

## Exact commands

Run the full script as one fresh shell with bash --noprofile --norc acceptance.sh:

```bash
#!/usr/bin/env bash
set -euo pipefail
# Step 1: create an isolated checkout of the reviewed head.
ROSTER_SOURCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-question-needs-both-families'
ROSTER_HEAD=c2643dae831f9685166b7cd564d8d885e88a3f21
ROSTER_BASE=e891e83582ac10936ffd67fb083b530b009ad847
ROSTER_PACKAGE='/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0'
ROSTER_CHECK=$(mktemp -d "$ROSTER_SOURCE/.context/roster-acceptance3.XXXXXX")
git -C "$ROSTER_SOURCE" worktree add --detach "$ROSTER_CHECK" "$ROSTER_HEAD"
test "$(git -C "$ROSTER_CHECK" rev-parse HEAD)" = "$ROSTER_HEAD"
printf 'STEP 1 PASS: exact candidate %s\n' "$ROSTER_HEAD"

# Step 2: exercise question, committed resolution, effort mapping, and family cases.
python3 -B - "$ROSTER_CHECK" <<'PY'
import sys, tempfile, shutil
from pathlib import Path
root = Path(sys.argv[1])
sys.path.insert(0, str(root / "kc-dev-flow-2/scripts"))
import test_sd_dispatch as check
fixture = Path(tempfile.mkdtemp(prefix="roster-acceptance-fixtures-", dir=root.parent))
try:
    check.exercise_extension_lists(fixture / "extensions")
    check.exercise_model_roster(fixture / "roster")
finally:
    shutil.rmtree(fixture)
print("STEP 2 PASS: shared extension-list callers; eight prerequisite combinations; three models and six efforts; wrong pairs refused; absent roster unchanged")
PY

# Step 3: check merged-parent ancestry, literal origin/main equality, lint and ADR 0050.
git -C "$ROSTER_CHECK" merge-base --is-ancestor 52e8eba7bf3746fd93d9132548a8163c66a7a26b "$ROSTER_BASE"
git -C "$ROSTER_CHECK" merge-base --is-ancestor "$ROSTER_BASE" "$ROSTER_HEAD"
test "$(git -C "$ROSTER_CHECK" rev-parse origin/main)" = "$ROSTER_BASE"
git -C "$ROSTER_CHECK" diff --exit-code origin/main "$ROSTER_HEAD" -- kc-dev-flow-2/references/sd/workflow.md
(cd "$ROSTER_CHECK" && python3 -B kc-dev-flow-2/scripts/lint-skills.py)
(cd "$ROSTER_CHECK" && python3 "$ROSTER_PACKAGE/scripts/adr_lint.py" docs/adr --since "$ROSTER_BASE" --require 0050)
printf 'STEP 3 PASS: merged parents; origin/main workflow unchanged; lint and ADR 0050 pass\n'

# Step 4: inspect the retained FO native record and verify release metadata parity.
python3 - '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/model-roster-question-needs-both-families/native-runs/final/receipts.json' <<'PYRECEIPTS'
import json, sys
from datetime import datetime
rows = json.load(open(sys.argv[1]))
expected = {'8c33c57f': ('claude-opus-5-5', 'high'), '575a60c6': ('claude-opus-5-5', 'low'), '84db4474': ('gpt-6.1-sol', 'xhigh'), '45f8566a': ('gpt-6-astra', 'xhigh')}
assert set(rows) == set(expected)
for child, (model, effort) in expected.items():
    row = rows[child]
    assert model in row['models'] and row['efforts'] == [effort]
    assert row['send_tool_calls'] == 0
    assert any(e['event'] == 'finished' and datetime.fromisoformat(e['session_time']) > datetime.fromisoformat(row['last_transcript_time']) for e in row['inbound'])
    if model == 'claude-opus-5-5':
        assert row['process_flags'] == [f'--thinking adaptive --effort {effort} --model {model}']
    print(f'FO RECORD: {child} {model}/{effort}; later finished receipt; no child send')
print('FO RECORD PASS: high differs from low; all four later completions. This reads retained evidence; it does not spawn agents.')
PYRECEIPTS

(cd "$ROSTER_CHECK" && bash scripts/version-parity-check.sh)
printf 'STEP 4 PASS: retained FO record and release metadata parity\n'

# Step 5: verify no tracked edits and remove this checkout.
test -z "$(git -C "$ROSTER_CHECK" status --porcelain)"
git -C "$ROSTER_SOURCE" worktree remove "$ROSTER_CHECK"
printf 'STEP 5 PASS: candidate unchanged; temporary checkout removed\n'

```

## Observed output

Exit 0. Elapsed upper bound from script creation to final log write: 78.71 seconds.

```text
Preparing worktree (detached HEAD c2643dae8)
HEAD is now at c2643dae8 fix(kc-dev-flow-2): share workflow extension list parsing
STEP 1 PASS: exact candidate c2643dae831f9685166b7cd564d8d885e88a3f21
PASS: shared extension-list callers handle inline/block forms, quotes, comments, exact names, empty/no-key controls and unchanged manifests
PASS: roster subprocess replay, absolute/split-root/linked roots, read-only repeatability, full schema/error controls, committed changes/deletion and candidate-author family evidence; legacy record checks do not establish roster use
STEP 2 PASS: shared extension-list callers; eight prerequisite combinations; three models and six efforts; wrong pairs refused; absent roster unchanged
PASS: basic frontmatter, declared profile routes, role bindings and package script paths
references/sd/workflow.md: 5781 of 5781 words; no unlisted passage repeats it
Not checked: full Agent Skills conformance or host/workflow behavior
49 ADR file(s) checked, 0 legacy
STEP 3 PASS: merged parents; origin/main workflow unchanged; lint and ADR 0050 pass
FO RECORD: 8c33c57f claude-opus-5-5/high; later finished receipt; no child send
FO RECORD: 575a60c6 claude-opus-5-5/low; later finished receipt; no child send
FO RECORD: 84db4474 gpt-6.1-sol/xhigh; later finished receipt; no child send
FO RECORD: 45f8566a gpt-6-astra/xhigh; later finished receipt; no child send
FO RECORD PASS: high differs from low; all four later completions. This reads retained evidence; it does not spawn agents.
PACKAGE            CONFIGURED PATH                                      RESULT    EFFECTIVE PATH
e2e-pipeline       .claude-plugin/plugin.json                           ok        e2e-pipeline/.claude-plugin/plugin.json
e2e-pipeline       .codex-plugin/plugin.json                            ok        e2e-pipeline/.codex-plugin/plugin.json
e2e-pipeline       /.claude-plugin/marketplace.json                     ok        .claude-plugin/marketplace.json
kc-plugin-forge    .claude-plugin/plugin.json                           ok        kc-plugin-forge/.claude-plugin/plugin.json
kc-plugin-forge    .codex-plugin/plugin.json                            ok        kc-plugin-forge/.codex-plugin/plugin.json
kc-plugin-forge    /.claude-plugin/marketplace.json                     ok        .claude-plugin/marketplace.json
kc-nightwatch      .claude-plugin/plugin.json                           ok        kc-nightwatch/.claude-plugin/plugin.json
kc-nightwatch      /.claude-plugin/marketplace.json                     ok        .claude-plugin/marketplace.json
kc-hyperfocus      .claude-plugin/plugin.json                           ok        kc-hyperfocus/.claude-plugin/plugin.json
kc-hyperfocus      /.claude-plugin/marketplace.json                     ok        .claude-plugin/marketplace.json
kc-team-ops        .claude-plugin/plugin.json                           ok        kc-team-ops/.claude-plugin/plugin.json
kc-team-ops        .codex-plugin/plugin.json                            ok        kc-team-ops/.codex-plugin/plugin.json
kc-team-ops        /.claude-plugin/marketplace.json                     ok        .claude-plugin/marketplace.json
kc-journey-map     .claude-plugin/plugin.json                           ok        kc-journey-map/.claude-plugin/plugin.json
kc-journey-map     .codex-plugin/plugin.json                            ok        kc-journey-map/.codex-plugin/plugin.json
kc-journey-map     /.claude-plugin/marketplace.json                     ok        .claude-plugin/marketplace.json
kc-pr-flow         .claude-plugin/plugin.json                           ok        kc-pr-flow/.claude-plugin/plugin.json
kc-pr-flow         .codex-plugin/plugin.json                            ok        kc-pr-flow/.codex-plugin/plugin.json
kc-pr-flow         /.claude-plugin/marketplace.json                     ok        .claude-plugin/marketplace.json
kc-dev-flow        .claude-plugin/plugin.json                           ok        kc-dev-flow/.claude-plugin/plugin.json
kc-dev-flow        .codex-plugin/plugin.json                            ok        kc-dev-flow/.codex-plugin/plugin.json
kc-dev-flow        plugin.json                                          ok        kc-dev-flow/plugin.json
kc-dev-flow        /.claude-plugin/marketplace.json                     ok        .claude-plugin/marketplace.json
kc-ship-flow       .claude-plugin/plugin.json                           ok        kc-ship-flow/.claude-plugin/plugin.json
kc-ship-flow       .codex-plugin/plugin.json                            ok        kc-ship-flow/.codex-plugin/plugin.json
kc-ship-flow       /.claude-plugin/marketplace.json                     ok        .claude-plugin/marketplace.json
kc-dev-flow-2      .claude-plugin/plugin.json                           ok        kc-dev-flow-2/.claude-plugin/plugin.json
kc-dev-flow-2      .codex-plugin/plugin.json                            ok        kc-dev-flow-2/.codex-plugin/plugin.json
kc-dev-flow-2      /.claude-plugin/marketplace.json                     ok        .claude-plugin/marketplace.json
kc-dev-flow-2      references/sd/workflow.md                            ok        kc-dev-flow-2/references/sd/workflow.md
kc-adr             .claude-plugin/plugin.json                           ok        kc-adr/.claude-plugin/plugin.json
kc-adr             .codex-plugin/plugin.json                            ok        kc-adr/.codex-plugin/plugin.json
kc-adr             /.claude-plugin/marketplace.json                     ok        .claude-plugin/marketplace.json

Release-please config: all extra-file paths and JSONPath selectors are valid
First-release contract: e2e-pipeline-v0.1.0, kc-plugin-forge-v0.1.0, kc-nightwatch-v0.1.0, kc-hyperfocus-v0.1.0, kc-team-ops-v0.1.0, kc-journey-map-v0.1.0, kc-pr-flow-v0.1.0, kc-dev-flow-v0.1.0, kc-ship-flow-v0.1.0, kc-dev-flow-2-v0.1.0, kc-adr-v0.1.0
Plugin directory enumeration: on-disk plugin directories and marketplace.json entries match 1:1

PLUGIN             release   plugin.json market    codex     hermes    RESULT
e2e-pipeline       3.3.5     3.3.5     3.3.5     3.3.5     -         ok
kc-plugin-forge    1.10.0    1.10.0    1.10.0    1.10.0    -         ok
kc-nightwatch      0.5.1     0.5.1     0.5.1     -         -         ok
kc-hyperfocus      1.6.4     1.6.4     1.6.4     -         -         ok
kc-team-ops        1.8.0     1.8.0     1.8.0     1.8.0     -         ok
kc-journey-map     1.8.0     1.8.0     1.8.0     1.8.0     -         ok
kc-pr-flow         1.12.0    1.12.0    1.12.0    1.12.0    -         ok
kc-dev-flow        4.6.0     4.6.0     4.6.0     4.6.0     4.6.0     ok
kc-ship-flow       0.3.0     0.3.0     0.3.0     0.3.0     -         ok
kc-dev-flow-2      0.34.0    0.34.0    0.34.0    0.34.0    -         ok
kc-adr             0.2.1     0.2.1     0.2.1     0.2.1     -         ok

Version parity: all plugins consistent
STEP 4 PASS: retained FO record and release metadata parity
STEP 5 PASS: candidate unchanged; temporary checkout removed
```
