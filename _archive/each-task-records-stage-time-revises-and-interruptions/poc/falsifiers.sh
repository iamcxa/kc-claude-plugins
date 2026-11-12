#!/bin/bash
# Runs each criterion's falsifier on a mutated copy of task_timeline.py beside its imports.
# Usage: bash falsifiers.sh <task_timeline.py> <package root> <state checkout> <poc folder>
set -uo pipefail
TT=$1; PKG=$2; S=$3; O=$4
D=$(mktemp -d /tmp/tt-falsify.XXXXXX); trap 'rm -rf "$D"; echo "removed $D"' EXIT
cp "$(dirname "$TT")"/{task_timeline,decision_ledger,role_triggers,count_tokens}.py "$D"/ 2>/dev/null; cp "$(dirname "$TT")"/*.py "$D"/
M=$D/task_timeline.py
mutate() { cp "$TT" "$M"; python3 - "$M" "$1" "$2" <<'PY'
import sys; p, old, new = sys.argv[1:]; s = open(p).read(); assert old in s, old; open(p, "w").write(s.replace(old, new))
PY
}
echo "== AC-1: drop the archive match"
mutate 'if ARCHIVE.match(subject) and done is None:' 'if False:'
python3 -B "$M" "$S" worth-questions-asked-only-before-the-design-gate | grep -E 'done:|validation:'
echo "== AC-1: committer date instead of author date"
mutate '%aI' '%cI'
python3 -B "$M" "$S" worth-questions-asked-only-before-the-design-gate | diff <(python3 -B "$TT" "$S" worth-questions-asked-only-before-the-design-gate) - >/dev/null && echo "no change on this task" || echo "output changed"
echo "== AC-2: count record files instead of the highest record number"
mutate 'n = max(len(starts.get(stage, [])), max(records.get(stage, {}), default=0))' 'n = len(starts.get(stage, []))'
python3 -B "$O/compare_spent.py" "$M" "$PKG" "$S" | tail -3; echo "exit ${PIPESTATUS[0]}"
echo "== AC-3: ignore asks.jsonl"
mutate 'asks_file = folder(task) / "asks.jsonl"' 'asks_file = folder(task) / "none.jsonl"'
bash "$O/ask_smoke.sh" "$M" 2>&1 | grep -E 'AssertionError|asks_outside_gate|accepted|refused'; echo "exit ${PIPESTATUS[0]}"
echo "== AC-5: running stage ends at its start"
mutate 'row["elapsed"] += mins(start, end or now) or 0' 'row["elapsed"] += mins(start, end) or 0'
python3 -B "$M" "$S" each-task-records-stage-time-revises-and-interruptions | grep ideation
