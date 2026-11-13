#!/usr/bin/env bash
set -euo pipefail
CODE="$1"
SPACEDOCK_BIN="$2"
S4_REPRO="$3"
OUTPUT="$4"
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
# Step 1: Confirm the pinned merged candidate; keep test fixtures in the caller-owned output.
test "$(git -C "$CODE" rev-parse HEAD)" = c429ab1815a5fc5507056ee54f8005be024e1e69
mkdir -p "$OUTPUT/tmp"
export SPACEDOCK_BIN TMPDIR="$OUTPUT/tmp" PYTHONDONTWRITEBYTECODE=1
# Step 2: Native second dispatch, unchanged collision refusal, retry/restore and owned cleanup.
python3 -B "$HERE/probe_candidate.py" "$CODE" "$OUTPUT/probe"
test "$(grep -c '^Scratch: /tmp/dev2/' "$OUTPUT/probe/validation-2-record.md")" = 1
# Step 3: AC-2: removed report paths pass; missing FO-message paths fail.
PYTHONPATH="$CODE/kc-dev-flow-2/scripts" python3 -B "$S4_REPRO" "$CODE/kc-dev-flow-2/scripts"
# Step 4: AC-4: close this dispatch while keeping another dispatch in the same repository.
PYTHONPATH="$CODE/kc-dev-flow-2/scripts" python3 -B -m unittest test_scratch.ScratchTests.test_close_keeps_another_dispatch_in_the_same_repository
