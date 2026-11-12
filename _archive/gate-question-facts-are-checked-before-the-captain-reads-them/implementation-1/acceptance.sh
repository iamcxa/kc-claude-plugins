#!/bin/sh
set -eu
TASK_CODE=$1
TASK_STATE=$2
TASK_PACKAGE=$3
TASK_OUTPUT=$4
TASK_BASE=d79053d0836c558a9269f9cf1ba222933935b820
TASK_HEAD=8d083d3b9b2c48c10e32cee3e5ef693b374c6183
TASK_ENTITY=gate-question-facts-are-checked-before-the-captain-reads-them
TASK_WORKFLOW=$(dirname "$TASK_STATE")
test "$(git -C "$TASK_CODE" rev-parse HEAD)" = "$TASK_HEAD"
test -z "$(git -C "$TASK_CODE" status --porcelain)"
git -C "$TASK_CODE" merge-base --is-ancestor "$TASK_BASE" HEAD
mkdir -p "$TASK_OUTPUT"
cd "$TASK_CODE"
export PYTHONDONTWRITEBYTECODE=1
python3 -B kc-dev-flow-2/scripts/test_delivery_gate.py > "$TASK_OUTPUT/delivery-tests.log" 2>&1
python3 -B kc-dev-flow-2/scripts/test_learning.py > "$TASK_OUTPUT/learning-tests.log" 2>&1
python3 -B kc-dev-flow-2/scripts/test_adr_doc_checks.py > "$TASK_OUTPUT/adr-doc-tests.log" 2>&1
python3 -B "$TASK_STATE/$TASK_ENTITY/implementation-1/run-evidence.py" --code "$TASK_CODE" --state "$TASK_STATE" > "$TASK_OUTPUT/replay.json"
python3 -B kc-dev-flow-2/scripts/lint-skills.py > "$TASK_OUTPUT/lint.log" 2>&1
python3 -B "$TASK_PACKAGE/scripts/adr_lint.py" docs/adr --since "$TASK_BASE" --require 0082 > "$TASK_OUTPUT/adr-lint.log" 2>&1
python3 -B "$TASK_PACKAGE/scripts/number_guards.py" check --repo "$TASK_CODE" --workflow-dir "$TASK_WORKFLOW" --task "$TASK_STATE/$TASK_ENTITY.md" --base "$TASK_BASE" > "$TASK_OUTPUT/number-guards.log" 2>&1
python3 -B "$TASK_PACKAGE/scripts/comment_ratio.py" "$TASK_BASE" HEAD --workflow-dir "$TASK_WORKFLOW" > "$TASK_OUTPUT/comments.log" 2>&1
python3 -B "$TASK_PACKAGE/scripts/design_surfaces.py" check "$TASK_STATE/$TASK_ENTITY.md" > "$TASK_OUTPUT/design-surfaces.log" 2>&1
git -C "$TASK_CODE" diff --check "$TASK_BASE" HEAD
