#!/usr/bin/env bash
set -euo pipefail
export PRODUCT_WT="${1:?producer worktree}" DEV2_WT="${2:?dev2 worktree}" RELAY_CLONE="${3:?relay clone}" QNOW_CLONE="${4:?qnow clone}" STAGE_PACKAGE="${5:?kc-dev-flow-2 0.38.1 package}"
export EVIDENCE_ROOT
EVIDENCE_ROOT="$(mktemp -d /tmp/story-progress-verify.XXXXXX)"
EVIDENCE_SCRIPTS="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
test "$(git -C "$PRODUCT_WT" rev-parse HEAD)" = fd1caa475f85483cf5c4031a1e58656ff5d3eaff
test "$(git -C "$DEV2_WT" rev-parse HEAD)" = fa485f008562f00ebf91deed19e58ea52bb4b4dc
test -z "$(git -C "$PRODUCT_WT" status --porcelain)"
test -z "$(git -C "$DEV2_WT" status --porcelain)"
test -d "$PRODUCT_WT/kc-journey-map/node_modules"
python3 -B "$EVIDENCE_SCRIPTS/replay_setup.py" > "$EVIDENCE_ROOT/setup.log" 2>&1
python3 -B "$EVIDENCE_SCRIPTS/replay_seed.py" > "$EVIDENCE_ROOT/seed-replay.log" 2>&1
python3 -B "$EVIDENCE_SCRIPTS/replay_progress.py" > "$EVIDENCE_ROOT/progress-replay.log" 2>&1
node --test "$PRODUCT_WT/kc-journey-map/lib/progress.test.mjs" "$PRODUCT_WT/kc-journey-map/lib/schemas.test.mjs" > "$EVIDENCE_ROOT/journey-tests.log" 2>&1
python3 -B "$DEV2_WT/kc-dev-flow-2/scripts/test_design_surfaces.py" > "$EVIDENCE_ROOT/design-tests.log" 2>&1
python3 -B "$DEV2_WT/kc-dev-flow-2/scripts/test_pr_watch.py" > "$EVIDENCE_ROOT/watch-tests.log" 2>&1
python3 -B "$DEV2_WT/kc-dev-flow-2/scripts/test_dispatch_records.py" > "$EVIDENCE_ROOT/dispatch-tests.log" 2>&1
python3 -B "$EVIDENCE_ROOT/integrated/kc-dev-flow-2/extensions/release-acceptance/test_release_acceptance.py" > "$EVIDENCE_ROOT/consumer-tests.log" 2>&1
python3 -B "$EVIDENCE_SCRIPTS/mutations.py" > "$EVIDENCE_ROOT/mutations.log" 2>&1
python3 -B "$EVIDENCE_SCRIPTS/remaining_mutations.py" > "$EVIDENCE_ROOT/remaining-mutations.log" 2>&1
(cd "$DEV2_WT" && python3 -B kc-dev-flow-2/scripts/lint-skills.py) > "$EVIDENCE_ROOT/lint.log" 2>&1
(cd "$DEV2_WT" && python3 -B "$STAGE_PACKAGE/scripts/adr_lint.py" docs/adr --since e8664a72b0f904e5dda3c391d52ab3abaca876b4 --require 0076) > "$EVIDENCE_ROOT/adr.log" 2>&1
printf '%s\n' "$EVIDENCE_ROOT"
