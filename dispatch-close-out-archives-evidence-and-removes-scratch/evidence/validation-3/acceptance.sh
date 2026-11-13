#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
SOURCE="$(git -C "$HERE" rev-parse --show-toplevel)"
SHA=c429ab1815a5fc5507056ee54f8005be024e1e69
export SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock
# Step 1: Export the pinned public candidate. No product worktree or earlier scratch is used.
BASE="${TMPDIR:-$PWD}"
case "$BASE" in /tmp|/tmp/*|/private/tmp|/private/tmp/*) BASE="$PWD";; esac
RUN="$(mktemp -d "$BASE/pr854-captain.XXXXXX")"
trap 'rm -rf -- "$RUN"' EXIT
mkdir -p "$RUN/code" "$RUN/tmp"
git -C "$SOURCE" archive "$SHA" | tar -x -C "$RUN/code"
export TMPDIR="$RUN/tmp" PYTHONDONTWRITEBYTECODE=1
"$SPACEDOCK_BIN" --version | head -1
echo "Step 1 PASS: exported $SHA"
# Step 2: Exercise the native second dispatch and actual close, collision retry, committed restore and peer preservation.
python3 -B "$HERE/probe_candidate.py" "$RUN/code" "$RUN/probe"
test "$(grep -c '^Scratch: /tmp/dev2/' "$RUN/probe/validation-2-record.md")" = 1
echo "Step 2 PASS: native record count 1; restore and peer preservation"
# Step 3: A removed report path passes; the same missing path in the Captain message fails.
PYTHONPATH="$RUN/code/kc-dev-flow-2/scripts" python3 -B "$HERE/s4_repro.py" "$RUN/code/kc-dev-flow-2/scripts"
echo "Step 3 PASS: report exit 0; missing message path exit 1"
# Step 4: Check owned cleanup, the role retry, later write recovery and both merged watcher behaviors.
PYTHONPATH="$RUN/code/kc-dev-flow-2/scripts" python3 -B -m unittest \
 test_scratch.ScratchTests.test_close_keeps_another_dispatch_in_the_same_repository \
 test_dispatch_stage.DispatchStageTests.test_next_role_accepts_its_own_scratch_path_and_retries \
 test_scratch.ScratchTests.test_later_gzip_write_failure_keeps_original_digests_for_retry \
 test_pr_watch.TasksTests.test_merged_scratch_prompt_precedes_merge_record
echo "Step 4 PASS: four regression tests"
# Step 5: Remove this script's export and fixtures, with no dependency on them after exit.
rm -rf -- "$RUN"
test ! -e "$RUN"
trap - EXIT
echo "Step 5 PASS: temporary export removed"
