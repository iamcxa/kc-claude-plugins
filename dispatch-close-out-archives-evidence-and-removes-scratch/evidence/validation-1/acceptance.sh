#!/usr/bin/env bash
set -euo pipefail
# Step 1: Export the pinned candidate; all temporary repositories belong to this run.
REPO="$1"
SPACEDOCK_BIN="$2"
PACKAGE="$3"
OUTPUT="$4"
EVIDENCE="$(cd -- "$(dirname -- "$0")" && pwd)"
RUN="$(mktemp -d /tmp/close-854-accept.XXXXXX)"
mkdir -p "$RUN/candidate" "$RUN/tmp" "$OUTPUT"
trap 'rm -rf -- "$RUN"; printf "%s\n" "$RUN" > "$OUTPUT/acceptance-removed.txt"' EXIT
git -C "$REPO" archive 223dbb6d1b5e895a45d11537b9494aa08610c8f8 | tar -x -C "$RUN/candidate"
export SPACEDOCK_BIN TMPDIR="$RUN/tmp" PYTHONDONTWRITEBYTECODE=1
# Step 2: Existing native tests with only Package root fixture metadata adapted for /tmp.
python3 -B "$EVIDENCE/fixture_adapter.py" "$RUN/candidate/kc-dev-flow-2/scripts" "$EVIDENCE/implementation-1/acceptance.py" "$RUN/candidate" "$SPACEDOCK_BIN" "$OUTPUT/checks"
printf 'Existing decisive checks: passed\n'
# Step 3: Exercise the close CLI, committed gzip restoration, and truncation falsifier.
python3 -B "$EVIDENCE/close_restore.py" "$RUN/candidate" "$RUN" > "$OUTPUT/close-summary.txt"
cp "$RUN/close-cli.log" "$RUN/close-restore.json" "$RUN/public.txt.gz" "$RUN/SHA256SUMS" "$OUTPUT/"
cat "$OUTPUT/close-summary.txt"
# Step 4: Check the Captain's all-private-repository instruction (expected exit 1 on this head).
python3 -B "$EVIDENCE/privacy_probe.py" "$RUN/candidate" "$PACKAGE" "$OUTPUT"
