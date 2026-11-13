#!/usr/bin/env bash
# Verify the pinned public candidate without any product worktree.
set -euo pipefail
evidence_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
run_root="$(mktemp -d /tmp/observer-learn-acceptance.XXXXXX)"
trap 'rm -rf -- "$run_root"; printf "Removed scratch: %s\n" "$run_root"' EXIT
export PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH PYTHONHOME
candidate=97fe3d6ff9f9afe220b463c71ac428e380fc4dc5

printf 'Step 1/4: download pinned candidate and verify seven file hashes\n'
curl --fail --silent --show-error --location --max-time 90 "https://codeload.github.com/iamcxa/kc-claude-plugins/tar.gz/$candidate" -o "$run_root/source.tar.gz"
mkdir "$run_root/source"
tar -xzf "$run_root/source.tar.gz" --strip-components=1 -C "$run_root/source"
cd "$run_root/source"
shasum -a 256 -c "$evidence_dir/code-files.sha256"

printf 'Step 2/4: three readers agree on eight independently selected configurations\n'
python3 -B "$evidence_dir/cross-reader-probe.py" --code "$run_root/source"

printf 'Step 3/4: observer reports, historical revisions and selection errors\n'
python3 -B kc-dev-flow-2/scripts/test_observer_check.py

printf 'Step 4/4: laws and watcher callers, including detached archive commands\n'
python3 -B kc-dev-flow-2/scripts/test_laws_check.py
python3 -B kc-dev-flow-2/scripts/test_pr_watch.py
printf 'PASS: candidate %s; 8/8 parity cases; 245 focused tests, 244 passed and 1 optional replay skipped\n' "$candidate"

