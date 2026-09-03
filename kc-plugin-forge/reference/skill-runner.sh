#!/bin/bash
# Forge Phase 2 clean runner — the one interface Phase 2 calls for every
# RED/GREEN run. Never dispatches an in-session subagent; see
# reference/skill-scenarios.md for the scenario file format and the trap
# each runner closes.
#
# Usage: skill-runner.sh <cloud|bare> <scenario-file> <scenario-id> <red|green> <plugin-dir>
#
# Prints one line: outcome=<pass|fail|error> runner=<cloud|bare> model=<pin> scratch=<dir>
# Writes the full transcript to <scratch>/<scenario-id>-<variant>.json.
#
# The heavy lifting (YAML parsing, refusals, dispatch, paged transcript
# reading, assertion scoring) lives in skill-runner.py beside this file —
# this wrapper only pins the interpreter and forwards argv.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$HERE/skill-runner.py" "$@"
