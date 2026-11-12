#!/usr/bin/env bash
set -euo pipefail
REPO="$1"
SPACEDOCK_BIN="$2"
RUN="$3"
OUTPUT="$4"
EVIDENCE="$(cd -- "$(dirname -- "$0")" && pwd)"
# Step 1: Export the pinned candidate to a new, caller-owned scratch directory.
test ! -e "$RUN"
mkdir -p "$RUN/candidate" "$RUN/tmp" "$OUTPUT"
git -C "$REPO" archive d4fe39e54dc7069b099d61c4b0e3fa2e5aecd8c6 | tar -x -C "$RUN/candidate"
export SPACEDOCK_BIN TMPDIR="$RUN/tmp" PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$EVIDENCE/trace" SCRATCH_DIRECTORY_LOG="$OUTPUT/created-directories.jsonl"
printf 'Pinned candidate exported\n'
# Step 2: Run the original decisive checks; adapt only Package root fixture metadata.
python3 -B "$EVIDENCE/fixture_adapter.py" "$RUN/candidate/kc-dev-flow-2/scripts" "$EVIDENCE/reused/implementation-1/acceptance.py" "$RUN/candidate" "$SPACEDOCK_BIN" "$OUTPUT/checks"
printf 'Decisive checks: passed\n'
# Step 3: Build a native dispatch, close one of two owned fixtures, restore committed gzip.
python3 -B "$EVIDENCE/fixture_adapter.py" "$RUN/candidate/kc-dev-flow-2/scripts" "$EVIDENCE/reused/scope_and_privacy.py" "$RUN/candidate" "$OUTPUT/replay" > "$OUTPUT/replay.log"
printf 'Private-evidence instruction, own-root close, peer survival, committed restore: passed\n'
# Step 4: Execute the acceptance criterion's exact record count command.
grep -c '^Scratch: /tmp/dev2/' "$OUTPUT/replay/emitted-record.md"
printf 'Acceptance: PASSED\n'
# Step 5: Remove this run's export after retaining its public evidence in OUTPUT.
rm -rf -- "$RUN"
test ! -e "$RUN"
printf 'Acceptance scratch export removed\n'
