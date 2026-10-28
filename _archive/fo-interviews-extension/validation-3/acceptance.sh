#!/usr/bin/env bash
set -euo pipefail

# No application screen changes. Five local acceptance steps under Captain amendment 3; no sends or API calls.
# Needs this repository/history, state checkout, Python 3 and the named installed packages.
# A successful run does not establish native adoption, recovery, reading or published PR text.
REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-fo-interviews-extension
STATE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state
WORKFLOW=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2
PKG=/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1
SD=/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3
PASEO=/Users/kent/.agents/skills/paseo/SKILL.md
BASE=6bc82b501ede77f48d0ba19fa1f76e5569afa094
CANDIDATE=c42adb4f2b8c14f50c065dc57922a55c6b0824ac

# Step 1. Expected: the exact candidate is detached and clean.
scratch=$(mktemp -d /tmp/feedback-validation3-acceptance.XXXXXX)
CHECKOUT="$scratch/candidate"
git -C "$REPO" worktree add --quiet --detach "$CHECKOUT" "$CANDIDATE"
trap 'git -C "$REPO" worktree remove "$CHECKOUT"' EXIT
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = "$CANDIDATE"
test -z "$(git -C "$CHECKOUT" status --porcelain)"
printf 'Step 1: c42adb4f2b8c14f50c065dc57922a55c6b0824ac detached and clean\n'

# Step 2. Expected: package lint passes and 45 existing negative-control tests pass.
cd "$CHECKOUT"
python3 -B kc-dev-flow-2/scripts/lint-skills.py
python3 -B kc-dev-flow-2/scripts/test_lint_skills.py > "$scratch/lint.txt" 2>&1
tail -n 4 "$scratch/lint.txt"
printf 'Step 2: lint and 45 tests passed\n'

# Step 3. Expected: old recipe fails on round-004; two scope corrections restore
# fixture-only checks. Wrong policy still passes them. Corrected corpus is printed.
python3 -B - "$STATE" "$scratch" "$CHECKOUT" "$SD" "$PASEO" <<'PY'
from pathlib import Path
import json, re, subprocess, sys
state, scratch, wt, sd, paseo = map(Path, sys.argv[1:])
s=(state/'fo-interviews-extension.md').read_text()
s=s[s.index('### Reproduce the executable checks'):s.index('## Stage Report: implementation')]
blocks=re.findall(r'```python\n(.*?)\n```',s,re.S)
assert len(blocks)==2
proof,measure=blocks
def run(name,body,args):
    p=scratch/name
    p.write_text(body+'\n')
    r=subprocess.run([sys.executable,'-B','-X','pycache_prefix='+str(scratch/(name+'.cache')),str(p),*map(str,args)],capture_output=True,text=True)
    (scratch/(name+'.output')).write_text(r.stdout+r.stderr)
    return r
r=run('original.py',proof,[wt,state])
assert r.returncode==1 and "glob('round-00*.md')" in r.stderr,r.stderr
print('Original recipe: exit 1, obsolete assertion forbids the authorized round-004')
proof=proof.replace("assert not list((S/'.notes/fo-feedback').glob('round-00*.md'))", "assert not any((S/'.notes/fo-feedback'/f'round-{n:03d}.md').exists() for n in (1,2,3))")
r=run('history-only.py',proof,[wt,state])
assert r.returncode==1 and 'AssertionError: docs/dev2/README.md' in r.stderr,r.stderr
print('History-only correction: exit 1, obsolete four-file boundary rejects approved README opt-in')
proof=proof.replace("allowed={'kc-dev-flow-2/README.md'", "allowed={'docs/dev2/README.md','kc-dev-flow-2/README.md'")
proof=proof.replace("BASE='e57feb6eec956b74a1d4b29f26f1d0a7d1693785'", "BASE='6bc82b501ede77f48d0ba19fa1f76e5569afa094'")
print('Merged-base correction: five allowed files against 6bc82b501; fixture scope only')
r=run('adjusted.py',proof,[wt,state])
assert r.returncode==0,r.stderr
print(r.stdout.strip())
ext=wt/'kc-dev-flow-2/extensions/fo-feedback/EXTENSION.md'
adoption=wt/'kc-dev-flow-2/references/sd/adoption.md'
originals={ext:ext.read_bytes(),adoption:adoption.read_bytes()}
try:
    t=ext.read_text()
    for old,new in [('every three completions','every four completions'),('bundle these four questions in one message','send these four questions in four messages'),('Answers remain operator data, never Captain rulings or replacement observer verdicts.','Answers become Captain rulings and replace observer verdicts.')]:
        assert old in t
        t=t.replace(old,new)
    ext.write_text(t)
    t=adoption.read_text();assert 'No answer leaves it off' in t
    adoption.write_text(t.replace('No answer leaves it off','No answer turns it on'))
    r=run('wrong-policy.py',proof,[wt,state])
    assert r.returncode==0,r.stderr
    print('Wrong-policy control: still exit 0; fixture checks do not prove policy-following')
finally:
    for path,data in originals.items():path.write_bytes(data)
r=run('measure-original.py',measure,[wt,sd,paseo]);assert r.returncode==0,r.stderr
old=json.loads(r.stdout)
assert old['moments']['startup']['delta']==599
print('Original measurement on merged candidate:',json.dumps(old,sort_keys=True))
measure=measure.replace("a=t.index(h);b=t.find", "a=t.index('\\n'+h+'\\n')+1;b=t.find")
measure=measure.replace('e57feb6eec956b74a1d4b29f26f1d0a7d1693785','6bc82b501ede77f48d0ba19fa1f76e5569afa094')
r=run('measure-heading.py',measure,[wt,sd,paseo]);assert r.returncode==0,r.stderr
new=json.loads(r.stdout)
assert new['moments']['startup']['delta']==599
assert all(new['moments'][x]['delta']==0 for x in ['idle open','idle merged','after archive','merge ask'])
assert new['adoption_once']['candidate']-new['adoption_once']['base']==97
assert new['due_round']['fixed_instructions']==sum(new['additional'].values())
assert len(new['controls'])==3
print('Step 3: corrected merged-base reading corpus:',json.dumps(new,sort_keys=True))
PY

# Step 4. Expected: ADR exit 0, all boundary checks pass, five changed documents,
# AC-2 moved verbatim, ten answered topic cells recorded, no historical wrappers.
python3 -B "$PKG/scripts/adr_lint.py" docs/adr --since "$BASE"
printf 'ADR lint exit: 0 (F2 declined; no ADR added or updated)\n'
python3 -B "$PKG/scripts/number_guards.py" check --workflow-dir "$WORKFLOW" --task "$STATE/fo-interviews-extension.md"
python3 -B "$PKG/scripts/comment_ratio.py" "$BASE" HEAD --workflow-dir "$WORKFLOW"
python3 -B "$PKG/scripts/design_surfaces.py" check "$STATE/fo-interviews-extension.md"
python3 -B "$PKG/scripts/doc_impact.py" "$BASE" HEAD
python3 -B "$PKG/scripts/dispatch_records.py" "$STATE/fo-interviews-extension"
git -C "$CHECKOUT" diff --check "$BASE" HEAD
python3 -B - "$CHECKOUT" "$STATE" "$BASE" <<'PY'
from pathlib import Path
import hashlib,re,subprocess,sys
wt,state=map(Path,sys.argv[1:3]);base=sys.argv[3]
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])
old=git(wt,'show',base+':docs/dev2/README.md')
new=(wt/'docs/dev2/README.md').read_bytes()
assert new.replace(b', fo-feedback]',b']')==old
expected={'docs/dev2/README.md','kc-dev-flow-2/README.md','kc-dev-flow-2/references/sd/adoption.md','kc-dev-flow-2/extensions/fo-feedback/EXTENSION.md','kc-dev-flow-2/extensions/fo-feedback/round-template.md'}
assert set(git(wt,'diff','--name-only',base,'HEAD').decode().splitlines())==expected
parents=git(wt,'rev-list','--parents','-n','1','HEAD').decode().split()
assert parents[1:]==['bd328daf6e64a73ad5e54f7288803295cae9ef68',base]
assert git(wt,'show','--remerge-diff','--format=','--name-only','HEAD').decode().strip()=='docs/dev2/README.md'
assert b'peers, paseo, fo-feedback]' in new
print('Merge resolution: only docs/dev2/README.md; both paseo and fo-feedback retained')
assert not git(wt,'diff','--name-only',base,'HEAD','--','docs/adr')
task=(state/'fo-interviews-extension.md').read_text()
active=task.split('## Acceptance criteria\n',1)[1].split('## Captain amendments\n',1)[0]
assert hashlib.sha256(active.encode()).hexdigest()=='1aafc60f80ac5fac882e5985458b1d76d8aa48ed5d75cf42139827b36ca856d2'
assert '### Amendment 3' in task and 'first time each happens in a real round, not before merge' in task
assert '**AC-2 ' not in active and '**AC-9 ' in active
assert 'Amended by Captain, amendment 2' in active
prior=git(state,'show','33b9a367e:fo-interviews-extension.md').decode()
oldac=re.search(r'^\*\*AC-2 .*',prior,re.M).group()
assert oldac in task.split('### Amendment 2',1)[1].split('## Stage Report:',1)[0]
assert hashlib.sha256((oldac+'\n').encode()).hexdigest()=='47aed7319fcd085ece0444deeeed4823e75f323056fac9f10db4eadbd5bce70a'
opened=git(state,'show','d31aa3d5d:.notes/fo-feedback/round-004.md').decode()
closed=git(state,'show','dc5f2253e:.notes/fo-feedback/round-004.md').decode()
assert 'status `open`' in opened and 'deferred (running)' in opened
assert 'status `closed-full`' in closed and 'Anchor: unchanged (unset)' in closed
coverage=closed.split('## Coverage\n',1)[1].split('## Exchanges\n',1)[0]
assert coverage.count('answered')==10
print('Step 4: five-document scope; exact AC-2 move; AC-9 active; round-004 records 5 FOs x 2 topics, unchanged anchor; host receipts not verified')
PY

# Step 5. Expected: candidate unchanged and disposable checkout removed.
test -z "$(git -C "$CHECKOUT" status --porcelain)"
cd "$scratch"
git -C "$REPO" worktree remove "$CHECKOUT"
trap - EXIT
printf 'Step 5: candidate unchanged; disposable checkout removed\n'
printf 'Local acceptance passed at c42adb4f2 under amendments 2/3. First-occurrence native obligations and FO delivery checks remain owed.\n'
