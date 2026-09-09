#!/usr/bin/env bash
set -euo pipefail
grep -q "absent (added by candidate)" "$(dirname "$0")/../accept-evidence.sh"
