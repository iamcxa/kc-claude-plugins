#!/usr/bin/env bash
# Acceptance checks for pilot-ideation-runs-a-probe-before-the-design, run against a probe or candidate.
# usage: accept.sh <AC-id> <out dir>; env: REPO (package repo), CAND (candidate ref), BASE (base ref),
#        STATE (state checkout), SD (spacedock binary), SDROOT (spacedock plugin root), INPUTS (stripped trial inputs)
set -u
ac=$1; out=$2; mkdir -p "$out"
here=$(cd "$(dirname "$0")" && pwd)
pkg() { git -C "$REPO" show "$1:kc-dev-flow-2/$2"; }
case $ac in
AC-1)  # built dispatch carries permission, bounds and proof-run with no FO line; base carries the ban
  rc=0; tmp=$(mktemp -d); git -C "$REPO" show "$CAND:kc-dev-flow-2/scripts/replay_dispatch.py" > "$tmp/replay_dispatch.py"
  git -C "$REPO" show "$BASE:docs/dev2/README.md" > "$tmp/adopter-README.md"
  for t in pr-watch-tasks-foreign-worktree:08d61c3e48d7365f7e058d16bea85fd61906539a new-work-checks-what-exists-first:da987bc67ada9406bd45ea552e6ceafd8d1dd8b8; do
    slug=${t%%:*}; sc=${t##*:}
    for arm in candidate:$CAND control:$BASE; do
      name=${arm%%:*}; ref=${arm##*:}; run="$tmp/$slug-$name"
      python3 -B "$tmp/replay_dispatch.py" build --run-dir "$run" --package-repo "$REPO" --package-ref "$ref" \
        --adopter-readme "$tmp/adopter-README.md" --readme-base-ref "$BASE" --state-repo "$STATE" --state-commit "$sc" \
        --task "$slug" --code-repo "$REPO" --code-commit 8ce0eb6050c889b21baccf50fec35231bc888d66 --stage ideation \
        --checklist "$INPUTS/$slug.checklist.txt" --scope "$INPUTS/$slug.scope.txt" --spacedock "$SD" > /dev/null || { echo "$slug $name: build failed"; rc=1; continue; }
      fetch=$(awk '/^### Fetch commands/{f=1;next} f&&/^    /{sub(/^    /,"");print;exit}' "$run/dispatch.md")
      bash -c "$fetch" > "$run/stage-def.txt" || { echo "$slug $name: fetch failed"; rc=1; }
      cat "$run/dispatch.md" "$run/stage-def.txt" > "$out/$slug-$name.worker-sees.txt"
      cp "$run/checklist.txt" "$out/$slug-$name.checklist.txt"; cp "$run/scope.txt" "$out/$slug-$name.scope.txt"
      v=$(python3 -I "$here/dispatch_check.py" "$out/$slug-$name.worker-sees.txt" "$run/checklist.txt" "$run/scope.txt")
      echo "$slug $name $v"
      want=$([ "$name" = candidate ] && echo carries || echo ban-only)
      case "$v" in "$want "*) ;; *) rc=1;; esac
      python3 -B "$tmp/replay_dispatch.py" cleanup --run-dir "$run" > /dev/null
    done
  done; rm -rf "$tmp"; exit $rc;;
AC-2)  # POC workflow derived from the candidate equals the one derived from base
  tmp=$(mktemp -d); pkg "$CAND" scripts/poc_readme.py > "$tmp/poc_readme.py"
  pkg "$BASE" references/sd/workflow.md > "$tmp/base.md"; pkg "$CAND" references/sd/workflow.md > "$tmp/cand.md"
  python3 -I -c "import sys; sys.path.insert(0,sys.argv[1]); from poc_readme import derive; a=derive(open(sys.argv[2]).read()); b=derive(open(sys.argv[3]).read()); print('poc derived equal' if a==b else 'poc derived DIFFER'); sys.exit(a!=b)" "$tmp" "$tmp/base.md" "$tmp/cand.md"; rc=$?; rm -rf "$tmp"; exit $rc;;
AC-3)  # the ban has one home: lint reports no repeat, and principles.md no longer states it
  tmp=$(mktemp -d); git -C "$REPO" archive "$CAND" kc-dev-flow-2 scripts | tar -x -C "$tmp"
  python3 -B "$tmp/kc-dev-flow-2/scripts/lint-skills.py" --root "$tmp/kc-dev-flow-2"; echo "lint exit $?"
  n=$(grep -c "writes no repository file" "$tmp/kc-dev-flow-2/skills/ideation/principles.md"); k=$(grep -c "ideation writes no repository file" "$tmp/kc-dev-flow-2/scripts/lint-skills.py")
  echo "principles.md ban lines: $n; KNOWN_DUPLICATES ban entries: $k"
  rep=$(python3 -B "$tmp/kc-dev-flow-2/scripts/lint-skills.py" --root "$tmp/kc-dev-flow-2" | grep -c "^FAIL:.*repeats"); echo "repeat findings: $rep"
  rm -rf "$tmp"; [ "$n" = 0 ] && [ "$k" = 0 ] && [ "$rep" = 0 ];;
AC-4)  # workflow word budget passes with a raise step carrying the Captain's quote
  tmp=$(mktemp -d); git -C "$REPO" archive "$CAND" kc-dev-flow-2 scripts | tar -x -C "$tmp"
  python3 -B "$tmp/kc-dev-flow-2/scripts/lint-skills.py" --root "$tmp/kc-dev-flow-2"; rc=$?; rm -rf "$tmp"; exit $rc;;
AC-5)  # words per moment: FO startup rises by at most 66, FO-authored probe words fall to 0
  python3 -I "$here/words_by_moment.py" "$REPO" "$BASE" "$CAND" > "$out/words-by-moment.json" || exit 1
  python3 -I -c "import json,sys; d=json.load(open(sys.argv[1])); s=d['FO startup/resume (reads the whole adopted README)']['delta']; print('FO startup delta', s); sys.exit(s>66)" "$out/words-by-moment.json" || exit 1
  for f in "$INPUTS"/*.checklist.txt "$INPUTS"/*.scope.txt; do grep -H -c -E "throwaway probe|may write code only" "$f"; done | awk -F: '{s+=$NF} END{print "FO-authored probe lines in replay inputs:", s; exit s!=0}';;
AC-6)  # dispatch contract suite passes on the candidate (whole tree: the suite reads docs/adr)
  tmp=$(mktemp -d); git -C "$REPO" archive "$CAND" | tar -x -C "$tmp"
  timeout 900 python3 -B "$tmp/kc-dev-flow-2/scripts/test_sd_dispatch.py" --sd-plugin-root "$SDROOT" > "$out/test_sd_dispatch.log" 2>&1; rc=$?; tail -1 "$out/test_sd_dispatch.log"; rm -rf "$tmp"; exit $rc;;
AC-7)  # the released timeline helper times and counts each ideation round as a dispatch
  pkg "$BASE" scripts/task_timeline.py > /dev/null || exit 1
  tmp=$(mktemp -d); git -C "$REPO" archive "$BASE" kc-dev-flow-2/scripts | tar -x -C "$tmp"
  python3 -B "$tmp/kc-dev-flow-2/scripts/task_timeline.py" "$STATE" adr-reserved-when-design-names-one > "$out/timeline.txt"; rc=$?; rm -rf "$tmp"
  grep -E "^  ideation:" "$out/timeline.txt"; [ $rc = 0 ] && grep -qE "^  ideation: .*dispatches 2, repeats 1" "$out/timeline.txt";;
*) echo "unknown $ac"; exit 2;;
esac
