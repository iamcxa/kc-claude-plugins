#!/usr/bin/env bash
set -eu
export PYTHONDONTWRITEBYTECODE=1
P=${1:?Pass the retained probe worktree path}
W=${2:?Pass the public workflow path holding both Scope cases}
SD=${3:?Pass the Spacedock executable path}
E=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
for criterion in AC-1 AC-2 AC-3 AC-4; do
    python3 -B "$E/probe_checks.py" "$criterion" --repo "$P" --workflow "$W" --sd-bin "$SD" > "$E/accept-$criterion.log" 2>&1
    echo "$criterion exit 0; output: $E/accept-$criterion.log"
done
