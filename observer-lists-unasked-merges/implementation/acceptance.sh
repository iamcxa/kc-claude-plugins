#!/usr/bin/env bash
set -euo pipefail
code_root="$1"
state_root="$2"
package_root="$3"
output_root="$4"
proof_root="$state_root/observer-lists-unasked-merges/implementation"
mkdir -p "$output_root"
test "$(git -C "$code_root" rev-parse HEAD)" = "b36fbeeec3a6699c0a82a021dc4ee0142410f6c8"
export PYTHONDONTWRITEBYTECODE=1
python3 -B "$proof_root/mutate.py" "$code_root" "$state_root" "$output_root/fresh" > "$output_root/mutations.log" 2>&1
python3 -B "$proof_root/snapshot.py" "$code_root" "$state_root" "$output_root/snapshot" > "$output_root/snapshot.log" 2>&1
python3 -B "$proof_root/recount.py" "$code_root/kc-dev-flow-2/scripts/merge_audit.py" "$state_root" "$output_root/words" > "$output_root/words.log" 2>&1
cd "$code_root"
python3 -B kc-dev-flow-2/scripts/lint-skills.py > "$output_root/lint.log" 2>&1
python3 -B "$package_root/scripts/adr_lint.py" docs/adr --since 139feeaee7ce037a0c6535568cd6bd103155cbae > "$output_root/adr-lint.log" 2>&1
python3 -B "$package_root/scripts/number_guards.py" check --repo "$code_root" --workflow-dir "$state_root/.." --task "$state_root/observer-lists-unasked-merges.md" --base 139feeaee7ce037a0c6535568cd6bd103155cbae > "$output_root/number-guards.log" 2>&1
python3 -B "$package_root/scripts/comment_ratio.py" 139feeaee7ce037a0c6535568cd6bd103155cbae HEAD --workflow-dir "$state_root/.." > "$output_root/comment-ratio.log" 2>&1
python3 -B "$package_root/scripts/design_surfaces.py" check "$state_root/observer-lists-unasked-merges.md" > "$output_root/design-check.log" 2>&1
git -C "$code_root" diff --check 139feeaee7ce037a0c6535568cd6bd103155cbae HEAD
echo "PASS: candidate identity, fresh behavioral tests, all reverse mutations, saved-window replay, word recount and package guards."
