#!/usr/bin/env bash
set -euo pipefail
# Prerequisites: bash, gh authenticated for GitHub, tar, rg, python3 and PyYAML.
# No UI changed. This checks the instruction and its local tests, not live review delivery.
# 1. Download the exact public candidate; no product checkout is needed.
validation_tmp=$(mktemp -d "${TMPDIR:-/tmp}/codex-ready-acceptance.XXXXXX")
trap 'rm -rf "$validation_tmp"' EXIT
gh api repos/iamcxa/kc-claude-plugins/tarball/1c8a29faf402ef6d7018c298f59bad58d38cfb1d > "$validation_tmp/candidate.tgz"
tar -xzf "$validation_tmp/candidate.tgz" -C "$validation_tmp" --strip-components=1
cd "$validation_tmp"
export PYTHONDONTWRITEBYTECODE=1
# 2. Expected: the ready rule followed by the existing repair rule.
rg -n -A 2 -F -- 'when FO marks a PR ready, it comments `@codex review` on the PR once.' kc-dev-flow-2/extensions/codex/EXTENSION.md
# 3. Remove only the new sentence from a temporary copy; expected: search exit 1.
python3 -B - <<'PY'
from pathlib import Path
p=Path('kc-dev-flow-2/extensions/codex/EXTENSION.md')
s='when FO marks a PR ready, it comments `@codex review` on the PR once.'
Path('without-sentence.md').write_text(''.join(l for l in p.read_text().splitlines(keepends=True) if s not in l))
PY
set +e
rg -n -F -- 'when FO marks a PR ready, it comments `@codex review` on the PR once.' without-sentence.md
search_exit=$?
set -e
test "$search_exit" -eq 1
printf 'Falsifier PASS: removed sentence returns exit %s\n' "$search_exit"
# 4. Expected: lint exit 0, all Codex extension tests pass, ACCEPTANCE PASS.
python3 -B kc-dev-flow-2/scripts/lint-skills.py
python3 -B kc-dev-flow-2/extensions/codex/test_codex_review.py
printf 'ACCEPTANCE PASS: 1c8a29faf402ef6d7018c298f59bad58d38cfb1d\n'

