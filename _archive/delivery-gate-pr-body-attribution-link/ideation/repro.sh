#!/usr/bin/env bash
# Reproduce repro-matrix.log. Usage: repro.sh <kc-claude-plugins checkout> [ref, default origin/main]
# Builds base (ref) and proto (ref + prototype.diff) package trees, then runs cases A-H through `steps`.
set -u
REPO=$1; REF=${2:-origin/main}; HERE=$(cd "$(dirname "$0")" && pwd); W=$(mktemp -d)
for v in base proto; do mkdir -p "$W/$v"; git -C "$REPO" archive "$REF" kc-dev-flow-2 | tar -x -C "$W/$v"; done
(cd "$W/proto/kc-dev-flow-2" && patch -s -p2 < "$HERE/prototype.diff")
T=$W/case/task; mkdir -p "$T/captain-steps" "$T/review"
printf 'Candidate: none\n\n### Step 1\nAsked: Review the candidate.\nRan: fresh shell, 2026-11-10T00:00:00Z\nObserved: worked\n' > "$T/captain-steps/record.md"
ATT='🤖 Generated with [Claude Code](https://claude.com/claude-code)'
NAMED='Review the candidate. PR body: review/pr-body.md'; RUN='Review the candidate. Run the steps in review/pr-body.md'
declare -A body msg
body[A]="## Summary\n\nFixes the hold.\n\n$ATT\n"; msg[A]=$NAMED
body[C]="Open https://preview.example.test/owner\n"; msg[C]=$RUN
body[D]="Repairs https://github.com/iamcxa/kc-claude-plugins/pull/773.\n\n$ATT\n"; msg[D]=$NAMED
body[E]="Open https://claude.com/claude-code\n"; msg[E]=$RUN
body[F]="$ATT then open https://preview.example.test/x\n"; msg[F]=$NAMED
body[G]="  $ATT   \n"; msg[G]=$NAMED
body[H]=""; msg[H]="Review the candidate. Open https://claude.com/claude-code"
for k in A C D E F G H; do
  printf "${body[$k]}" > "$T/review/pr-body.md"; printf '%s\n' "${msg[$k]}" > "$W/case/msg.txt"
  for v in base proto; do
    python3 -B "$W/$v/kc-dev-flow-2/scripts/delivery_gate.py" steps "$T/captain-steps/record.md" --text-file "$W/case/msg.txt" > "$W/out.txt"; e=$?
    echo "$k $v exit=$e :: $(grep -o "S5: unrecorded command or link '[^']*'" "$W/out.txt" | tr '\n' ' ')$(grep -o 'captain steps complete.*' "$W/out.txt")"
  done
done
echo "suite: cd $W/<base|proto>/kc-dev-flow-2/scripts && python3 -B -m pytest -q -p no:cacheprovider test_delivery_gate.py"
