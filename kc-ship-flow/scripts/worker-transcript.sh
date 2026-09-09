#!/usr/bin/env bash
# Print a cloud build worker's last fenced "## Evidence" block.
# Usage: worker-transcript.sh <session-id>
#
# Reads the transcript through `conductor sql` against
# `session_transcripts_view`, not `conductor session message --after`:
# that CLI truncates its JSON response at 64 KB and rejects a sent
# message's id as an --after cursor. One read per invocation; no polling
# loop, retry, or daemon.
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: worker-transcript.sh <session-id>" >&2
  exit 2
fi

session_id="$1"
escaped_id="${session_id//\'/\'\'}"

conductor --json sql "SELECT transcript FROM session_transcripts_view WHERE session_id = '${escaped_id}'" \
  | python3 -c "
import json
import re
import sys

rows = json.load(sys.stdin)['rows']
transcript = rows[0]['transcript'] if rows else ''
blocks = re.findall(r'\`\`\`[^\n]*\n(## Evidence\n.*?)\`\`\`', transcript, re.DOTALL)

if not blocks:
    print('no evidence block', file=sys.stderr)
    sys.exit(1)

print(blocks[-1].rstrip('\n'))
"
