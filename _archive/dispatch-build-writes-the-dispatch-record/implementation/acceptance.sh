#!/usr/bin/env bash
set -euo pipefail
CODE_ROOT="${1:?absolute code worktree}"
REVISION="${2:?full candidate SHA}"
OUTPUT="${3:?absolute output directory}"
EVIDENCE_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE=334d91e3165953b2ca7191e3308d80b6c02c4a99
PACKAGE=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0
WORKFLOW=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2
: "${SPACEDOCK_BIN:?set to the real Spacedock 0.27.2 binary}"
: "${SD_PLUGIN_ROOT:?set to the Spacedock source at 4d158a484ec73e184861067f8ed1e20087fdc26a}"
test "$(git -C "$CODE_ROOT" rev-parse HEAD)" = "$REVISION"
test -f "$SD_PLUGIN_ROOT/mods/pr-merge.md"
mkdir -p "$OUTPUT"
EXPORT="$(mktemp -d /tmp/dispatch-stage-acceptance.XXXXXX)"
git -C "$CODE_ROOT" archive "$REVISION" | tar -x -C "$EXPORT"
GIT_METADATA="$(git -C "$CODE_ROOT" rev-parse --absolute-git-dir)"
export PYTHONDONTWRITEBYTECODE=1
cd "$EXPORT"
"$SPACEDOCK_BIN" --version > "$OUTPUT/spacedock-version.txt"
rg '^spacedock 0\.27\.2$' "$OUTPUT/spacedock-version.txt" > /dev/null
python3 -B kc-dev-flow-2/scripts/lint-skills.py > "$OUTPUT/lint-skills.log" 2>&1
python3 -B "$EVIDENCE_DIR/test_json.py" "$EXPORT/kc-dev-flow-2/scripts/test_dispatch_stage.py" "$OUTPUT/dispatch-stage.json" > "$OUTPUT/dispatch-stage.log" 2>&1
python3 -B "$EVIDENCE_DIR/test_json.py" "$EXPORT/kc-dev-flow-2/scripts/test_lint_skills.py" "$OUTPUT/test-lint-skills.json" > "$OUTPUT/test-lint-skills.log" 2>&1
python3 -B "$EVIDENCE_DIR/test_json.py" "$EXPORT/kc-dev-flow-2/scripts/test_dispatch_records.py" "$OUTPUT/dispatch-records.json" > "$OUTPUT/dispatch-records.log" 2>&1
python3 -B kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root "$SD_PLUGIN_ROOT" > "$OUTPUT/sd-dispatch.log" 2>&1
env GIT_DIR="$GIT_METADATA" GIT_WORK_TREE="$EXPORT" python3 -B kc-dev-flow-2/scripts/adr_lint.py docs/adr --since "$BASE" --require 0070 > "$OUTPUT/adr-lint.log" 2>&1
python3 -B "$PACKAGE/scripts/number_guards.py" check --repo "$CODE_ROOT" --base "$BASE" --workflow-dir "$WORKFLOW" --task "$WORKFLOW/.spacedock-state/dispatch-build-writes-the-dispatch-record.md" > "$OUTPUT/number-guards.log" 2>&1
python3 -B "$PACKAGE/scripts/comment_ratio.py" "$BASE" "$REVISION" --repo "$CODE_ROOT" --workflow-dir "$WORKFLOW" > "$OUTPUT/comment-ratio.log" 2>&1
python3 -B "$EVIDENCE_DIR/falsifiers.py" --code-root "$CODE_ROOT" --output-dir "$OUTPUT/falsifiers" > "$OUTPUT/falsifiers.log" 2>&1
git -C "$CODE_ROOT" diff --check "$BASE" "$REVISION" > "$OUTPUT/diff-check.log" 2>&1
test "$(git -C "$CODE_ROOT" rev-parse HEAD)" = "$REVISION"
printf '%s\n' "$REVISION" > "$OUTPUT/candidate.txt"
printf '%s\n' "$EXPORT" > "$OUTPUT/export.txt"
