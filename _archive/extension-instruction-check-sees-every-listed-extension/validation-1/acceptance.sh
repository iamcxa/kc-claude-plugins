#!/bin/bash
# Read-only acceptance of PR #787. Requires git, python3, bash and the declared local package/state checkouts.
# No graphical surface changes. Does not prove worker obedience, release-walk execution, adoption or delivery.
set -euo pipefail
SOURCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-extension-instruction-check-sees-every-listed-extension'
STATE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
PACKAGE='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0'
HEAD=272721000cce947c8f2dcdd3a40c22cdf11dee09
BASE=d37c6dc653e0f45d6ca630c2faa6121c0863a57e
SNAPSHOT=acb39aba17babc61ad66edb93d79d8a9f680bfaa
export PYTHONDONTWRITEBYTECODE=1

# 1. Inspect the exact candidate in a temporary detached checkout.
# Expected: Candidate 272721000cce947c8f2dcdd3a40c22cdf11dee09.
TMPROOT=$(mktemp -d "$SOURCE/.context/accept-pr787.XXXXXX")
CHECKOUT="$TMPROOT/code"
cleanup() {
  git -C "$SOURCE" worktree remove --force "$CHECKOUT"
  rmdir "$TMPROOT"
}
git -C "$SOURCE" worktree add --detach "$CHECKOUT" "$HEAD"
trap cleanup EXIT
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = "$HEAD"
test -z "$(git -C "$CHECKOUT" status --porcelain)"
echo "Candidate $HEAD"

# 2. Run the shipped instruction tests and the real history-law consumer.
# Expected: both unittest commands end OK.
cd "$CHECKOUT"
python3 -B kc-dev-flow-2/scripts/test_dispatch_records.py ExtensionInstructionTests
python3 -B kc-dev-flow-2/scripts/test_laws_check.py L2Test.test_a_missing_paseo_instruction_is_a_parseable_l2_violation

# 3. Exercise the CLI on a missing instruction, then a wrapped instruction.
# Expected: the missing record exits 1 with the paseo diagnostic; the repaired record exits 0.
python3 -B - "$CHECKOUT" <<'PY'
import pathlib,subprocess,sys
root=pathlib.Path(sys.argv[1])
p=root/".context/accept-record"
(p/"task/dispatch").mkdir(parents=True)
(p/"README.md").write_text("---\nentity-type: task\nextensions: [paseo]\n---\n")
record=p/"task/dispatch/ideation-1.md"
record.write_text("# ideation-1\n\nDispatched: 272721000cce947c8f2dcdd3a40c22cdf11dee09\nModel: sonnet (Claude via Paseo)\n\n## Checklist\n\nCheck the exact candidate.\n\n## Scope notes\n\nPackage root: /pkg\nSend your completion message to main.\n")
cmd=["python3","-B",str(root/"kc-dev-flow-2/scripts/dispatch_records.py"),"--readme",str(p/"README.md"),str(p/"task")]
bad=subprocess.run(cmd,capture_output=True,text=True)
print(bad.stdout,end="")
assert bad.returncode==1 and "ideation-1.md: paseo worker instruction is absent" in bad.stdout
with record.open("a") as f:f.write("Start in the assigned worktree;\n  verify pwd and git root before edits.\n")
good=subprocess.run(cmd,capture_output=True,text=True)
print(good.stdout,end="")
assert good.returncode==0 and good.stdout=="1 dispatch record(s) complete\n"
print("Missing instruction held; supplied instruction passed.")
PY

# 4. Replay the 12 archived task folders from the pinned state snapshot.
# Expected: paseo 30 (ideation 16, implementation 14), roborev 7; no validation/message extension errors.
python3 -B - "$CHECKOUT" "$STATE" "$SNAPSHOT" <<'PY'
import collections,io,pathlib,re,subprocess,sys,tarfile
root,state,rev=pathlib.Path(sys.argv[1]),sys.argv[2],sys.argv[3]
snap=root/".context/accept-state";snap.mkdir()
data=subprocess.check_output(["git","-C",state,"archive",rev])
with tarfile.open(fileobj=io.BytesIO(data)) as archive:archive.extractall(snap,filter="data")
tasks=["second-round-prompts-a-step-back","claims-name-their-source","release-walk-due-trigger","fo-tries-what-it-asks-the-captain","diagnosis-rounds-count-toward-step-back","fo-answers-own-worker-permissions-by-listed-id","model-roster-question-needs-both-families","release-walk-off-production-before-release","validation-gate-requires-the-question-check","rewritten-criteria-checked-against-captain-words","worker-completion-reaches-fo-on-paseo","special-roles-follow-the-model-table"]
lines=[]
for task in tasks:
 p=subprocess.run(["python3","-B",str(root/"kc-dev-flow-2/scripts/dispatch_records.py"),"--readme",str(root/"docs/dev2/README.md"),str(snap/"_archive"/task)],capture_output=True,text=True)
 assert p.returncode in [0,1],p
 lines.extend(l for l in p.stdout.splitlines() if " worker instruction " in l)
counts=collections.Counter(re.search(r": ([\w-]+) worker instruction",l)[1] for l in lines)
assert dict(counts)=={"paseo":30,"roborev":7},counts
assert not any(l.startswith("validation-") or "-message-" in l for l in lines)
assert sum(l.startswith("ideation-") and ": paseo " in l for l in lines)==16
assert sum(l.startswith("implementation-") and ": paseo " in l for l in lines)==14
print("paseo 30 (ideation 16, implementation 14); roborev 7; validation/message extension errors 0")
PY

# 5. Check detector-only scope, workflow word budget and decision records.
# Expected: exact three-file scope, lint exit 0, adr_lint exit 0, clean checkout.
python3 -B - "$CHECKOUT" "$BASE" "$HEAD" <<'PY'
import subprocess,sys
got=set(subprocess.check_output(["git","-C",sys.argv[1],"diff","--name-only",sys.argv[2],sys.argv[3]],text=True).splitlines())
assert got=={"kc-dev-flow-2/scripts/dispatch_records.py","kc-dev-flow-2/scripts/test_dispatch_records.py","kc-dev-flow-2/scripts/test_laws_check.py"},got
print("Only the three approved detector/test files changed.")
PY
python3 -B kc-dev-flow-2/scripts/lint-skills.py
python3 -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since "$BASE"
test -z "$(git -C "$CHECKOUT" status --porcelain)"
echo "Acceptance passed; cleanup follows."

