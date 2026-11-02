# Five-step acceptance script

No changed graphical surface is claimed. This checks local roster behavior, merged-parent ancestry, literal origin/main workflow equality, package lint, ADR 0050 and release parity. It does not verify native child runtime/completion (AC-6), local RoboRev or release/adoption (AC-10).

Prerequisites: this repository clone containing the exact candidate and pinned main, Python 3, Git, Node/npm for the repository parity fixture, and the installed package at the absolute path below. The commands were run unchanged in a fresh bash with no startup files; exit 0. They do not write shared Git config or publish anything.

Run the following five steps together in a fresh bash shell:

```bash
#!/usr/bin/env bash
set -euo pipefail
# Step 1: create an isolated checkout of the reviewed head.
ROSTER_SOURCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-question-needs-both-families'
ROSTER_HEAD=52017322520dea243f982a015efa7747f8c05c9f
ROSTER_BASE=e891e83582ac10936ffd67fb083b530b009ad847
ROSTER_PACKAGE='/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0'
ROSTER_CHECK=$(mktemp -d "$ROSTER_SOURCE/.context/roster-acceptance.XXXXXX")
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
    check.exercise_model_roster(fixture / "roster")
finally:
    shutil.rmtree(fixture)
print("STEP 2 PASS: eight prerequisite combinations; three models and six efforts; wrong pairs refused; absent roster unchanged")
PY

# Step 3: check merged-parent ancestry, literal origin/main equality, lint and ADR 0050.
git -C "$ROSTER_CHECK" merge-base --is-ancestor 52e8eba7bf3746fd93d9132548a8163c66a7a26b "$ROSTER_BASE"
git -C "$ROSTER_CHECK" merge-base --is-ancestor "$ROSTER_BASE" "$ROSTER_HEAD"
test "$(git -C "$ROSTER_CHECK" rev-parse origin/main)" = "$ROSTER_BASE"
git -C "$ROSTER_CHECK" diff --exit-code origin/main "$ROSTER_HEAD" -- kc-dev-flow-2/references/sd/workflow.md
(cd "$ROSTER_CHECK" && python3 -B kc-dev-flow-2/scripts/lint-skills.py)
(cd "$ROSTER_CHECK" && python3 "$ROSTER_PACKAGE/scripts/adr_lint.py" docs/adr --since "$ROSTER_BASE" --require 0050)
printf 'STEP 3 PASS: merged parents; origin/main workflow unchanged; lint and ADR 0050 pass\n'

# Step 4: verify release metadata parity.
(cd "$ROSTER_CHECK" && bash scripts/version-parity-check.sh)
printf 'STEP 4 PASS: release metadata parity\n'

# Step 5: verify no tracked edits and remove this checkout.
test -z "$(git -C "$ROSTER_CHECK" status --porcelain)"
git -C "$ROSTER_SOURCE" worktree remove "$ROSTER_CHECK"
printf 'STEP 5 PASS: candidate unchanged; temporary checkout removed\n'

```

Expected: STEP 1 through STEP 5 each print PASS; all commands exit 0; the temporary checkout is removed. The script stops if origin/main changes, so a later candidate/base requires a fresh validation.

Observed output:

```text
Preparing worktree (detached HEAD 520173225)
HEAD is now at 520173225 Merge remote-tracking branch 'origin/main' into spacedock-ensign/model-roster-question-needs-both-families
STEP 1 PASS: exact candidate 52017322520dea243f982a015efa7747f8c05c9f
PASS: roster subprocess replay, absolute/split-root/linked roots, read-only repeatability, full schema/error controls, committed changes/deletion and candidate-author family evidence; legacy record checks do not establish roster use
STEP 2 PASS: eight prerequisite combinations; three models and six efforts; wrong pairs refused; absent roster unchanged
PASS: basic frontmatter, declared profile routes, role bindings and package script paths
references/sd/workflow.md: 5781 of 5781 words; no unlisted passage repeats it
Not checked: full Agent Skills conformance or host/workflow behavior
49 ADR file(s) checked, 0 legacy
STEP 3 PASS: merged parents; origin/main workflow unchanged; lint and ADR 0050 pass
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
STEP 4 PASS: release metadata parity
STEP 5 PASS: candidate unchanged; temporary checkout removed
```
