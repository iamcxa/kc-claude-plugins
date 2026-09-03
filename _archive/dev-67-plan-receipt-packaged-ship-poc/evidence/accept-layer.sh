#!/usr/bin/env bash
# accept-layer.sh <ISSUE_ID> <EXPECTED_BASE_SHA> -> pins remote head == CANDIDATE_SHA, runs worker's WITHOUT_IT verbatim (retained/removed), contract test, writes receipt. Exit 0 = pass.
set -uo pipefail; ID=$1; EXPBASE=$2; D=/tmp/poc2/$ID; R=$(git rev-parse --show-toplevel); EV=$D/evidence.txt
val(){ grep -E "^$1:" "$EV" | head -1 | sed -E "s/^$1:[[:space:]]*//"; }
SHA=$(val CANDIDATE_SHA); BR=$(val BRANCH); BASE=$(val BASE_SHA); WI=$(val WITHOUT_IT_COMMAND); WR=$(val WITHOUT_IT_REMOVED_VARIANT)
echo "candidate=$SHA branch=$BR base=$BASE"
[[ "$SHA" =~ ^[0-9a-f]{40}$ ]] || { echo "FAIL sha"; exit 10; }
[ "$BASE" = "$EXPBASE" ] || { echo "FAIL base: worker reported $BASE, dispatched on $EXPBASE"; exit 15; }
git -C "$R" fetch -q origin "$BR" || { echo "FAIL branch not on remote"; exit 11; }
HEAD=$(git -C "$R" rev-parse "origin/$BR"); [ "$HEAD" = "$SHA" ] || { echo "FAIL remote head $HEAD != $SHA"; exit 12; }
git -C "$R" merge-base --is-ancestor "$BASE" "$SHA" || { echo "FAIL base not ancestor"; exit 13; }
WT=$D/wt; rm -rf "$WT"; git -C "$R" worktree prune; git -C "$R" worktree add -q --detach "$WT" "$SHA" || exit 14
cd "$WT"
echo "== files"; git diff --name-only "$BASE" "$SHA" | tee "$D/files.txt"
echo "== without-it (worker's line, verbatim) retained:"; ( env -u LINEAR_API_KEY -u GH_TOKEN -u GITHUB_TOKEN -u CONDUCTOR_API_KEY -u ANTHROPIC_API_KEY -u OPENAI_API_KEY bash -c "$WI" ); RET=$?; echo "retained_exit=$RET"
echo "== removed variant:"; ( bash -c "$WR" ) && ( env -u LINEAR_API_KEY -u GH_TOKEN -u GITHUB_TOKEN -u CONDUCTOR_API_KEY -u ANTHROPIC_API_KEY -u OPENAI_API_KEY bash -c "$WI" ); REM=$?; echo "removed_exit=$REM"; git checkout -q "$SHA" -- . ; git clean -fdq
python3 - "$ID" "$SHA" "$RET" "$REM" <<'PY2'
import json,sys; a=sys.argv[1:]; json.dump({"issue":a[0],"candidate":a[1],"partial":True,"without_it":{"retained_exit":int(a[2]),"removed_exit":int(a[3])}}, open(f"/tmp/poc2/{a[0]}/receipt-partial.json","w"))
PY2
echo "== contract test"; python3 scripts/kc-dev-flow-contract-test.py > "$D/contract.log" 2>&1; CT=$?; echo "contract_exit=$CT $(tail -1 $D/contract.log)"
echo "== preflight merge-tree vs current origin/main"; MAIN=$(git -C "$R" rev-parse origin/main); git merge-tree --write-tree "$MAIN" "$SHA" >/dev/null && PF=0 || PF=1; echo "preflight_exit=$PF main=$MAIN"
cd "$R"
OK=0; [ "$RET" = 0 ] && [ "$REM" != 0 ] && [ "$CT" = 0 ] && [ "$PF" = 0 ] && OK=1
python3 - "$ID" "$SHA" "$BR" "$BASE" "$HEAD" "$RET" "$REM" "$CT" "$PF" "$OK" "$WI" "$WR" "$MAIN" <<'PY'
import json,sys; a=sys.argv[1:]
json.dump({"issue":a[0],"candidate":a[1],"branch":a[2],"base":a[3],"remote_head":a[4],"without_it":{"command":a[10],"removed_variant":a[11],"retained_exit":int(a[5]),"removed_exit":int(a[6])},"contract_test_exit":int(a[7]),"preflight_exit":int(a[8]),"preflight_main":a[12],"pass":a[9]=="1"}, open(f"/tmp/poc2/{a[0]}/receipt.json","w"), indent=1)
PY
echo "RECEIPT /tmp/poc2/$ID/receipt.json pass=$OK"; [ $OK = 1 ]
