#!/usr/bin/env bash
set -euo pipefail
REPOSITORY="${1:?Pass the repository checkout path}"
EVIDENCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CANDIDATE=ef9aaffcbc48d6f17dd2e1dd744c4ffb5862d0f8
BASE=8125e6d516d32abbf79c6772de10cde2c20900a8
ACCEPT_TMP="$(mktemp -d "${TMPDIR:-/tmp}/design-surfaces-acceptance.XXXXXX")"
trap 'rm -rf -- "$ACCEPT_TMP"' EXIT
export PYTHONDONTWRITEBYTECODE=1

# 1. Export the exact candidate. Expect the full recorded SHA.
git -C "$REPOSITORY" cat-file -e "$CANDIDATE^{commit}"
git -C "$REPOSITORY" archive "$CANDIDATE" | tar -x -C "$ACCEPT_TMP"
printf '1. candidate %s\n' "$CANDIDATE"

# 2. Exercise collisions, file priority and usage errors. Expect six tests, OK.
(cd "$ACCEPT_TMP" && python3 -B kc-dev-flow-2/scripts/test_design_surfaces.py \
    TaskArgumentTests SeedBoundsTests.test_unreadable_seed_is_a_diagnostic_and_nonzero_without_traceback)
printf '2. entrance tests PASS\n'

# 3. Exercise the real seed subprocess through PR-watch. Expect five passed cases.
python3 -B "$EVIDENCE_DIR/check_consumers.py" --source "$ACCEPT_TMP"
printf '3. exit-code consumer PASS\n'

# 4. Check decision records at the same candidate. Expect 73 checked, 0 legacy.
REPOSITORY_GIT_DIR="$(git -C "$REPOSITORY" rev-parse --absolute-git-dir)"
(cd "$ACCEPT_TMP" && GIT_DIR="$REPOSITORY_GIT_DIR" GIT_WORK_TREE="$ACCEPT_TMP" \
    python3 -B kc-dev-flow-2/scripts/adr_lint.py docs/adr --since "$BASE")
printf '4. ADR lint PASS\n'

# 5. Verify the export still has the candidate checker bytes. Expect PASS.
git -C "$REPOSITORY" show "$CANDIDATE:kc-dev-flow-2/scripts/design_surfaces.py" > "$ACCEPT_TMP/expected-checker.py"
cmp "$ACCEPT_TMP/expected-checker.py" "$ACCEPT_TMP/kc-dev-flow-2/scripts/design_surfaces.py"
printf '5. unchanged candidate PASS; acceptance PASS\n'
