#!/usr/bin/env bash
# Re-run every acceptance-criterion command of the ideation proof of concept.
# Usage: run-evidence.sh <POC worktree> <state checkout>
# Deterministic: no model call, no network. Writes logs into ./evidence next to this script.
set -u
POC=${1:?POC worktree}; STATE=${2:?state checkout}
HERE=$(cd "$(dirname "$0")" && pwd); Q=$HERE/questions; OUT=$HERE/evidence
mkdir -p "$OUT"
GF=$POC/kc-dev-flow-2/scripts/gate_facts.py
echo "poc head: $(git -C "$POC" rev-parse HEAD)" > "$OUT/identity.txt"
run() { local name=$1; shift; python3 -B "$@" > "$OUT/$name.log" 2>&1; echo "exit $?" >> "$OUT/$name.log"; echo "$name: $(tail -1 "$OUT/$name.log")"; }

run ac1-case3 "$GF" state --state "$STATE" --question "$Q/case3-five-tasks.json"
run ac1-control "$GF" state --state "$STATE" --question "$Q/control-five-new-tasks.json"
for n in case1-843 case2-841 control-839 control-849 control-849-cited control-849-badcite case2-841-marked; do
  run "ac2-scope-$n" "$GF" scope --state "$STATE" --question "$Q/$n.json"
done
run ac3-corpus "$GF" scope --question "$Q/corpus-fo-session-8fcbee7d.jsonl"

# Falsifiers: each mutant must change the result the criterion asserts.
MUT=$(mktemp -d /tmp/gqf-mutants.XXXXXX)
sed 's/STOP_DECISIONS = {"hold", /STOP_DECISIONS = {/' "$GF" > "$MUT/no_hold.py"
run falsifier-ac1-no-hold "$MUT/no_hold.py" state --state "$STATE" --question "$Q/case3-five-tasks.json"
sed 's/if EXISTING.search(s) and EFFECT.search(s)/if EFFECT.search(s) and re.search(r"\\bexisting\\b", s)/' "$GF" > "$MUT/english_only.py"
run falsifier-ac2-english-only "$MUT/english_only.py" scope --state "$STATE" --question "$Q/case1-843.json"
sed 's/if exists is None or exists(c)/if True/' "$GF" > "$MUT/no_exists.py"
run falsifier-ac2-no-exists "$MUT/no_exists.py" scope --state "$STATE" --question "$Q/control-849-badcite.json"
rm -rf "$MUT"; echo "removed $MUT"
