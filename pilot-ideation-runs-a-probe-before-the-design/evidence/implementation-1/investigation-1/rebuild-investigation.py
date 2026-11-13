from pathlib import Path
import hashlib, json, os, subprocess
s=Path('/tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/implementation-1')
w=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-pilot-ideation-runs-a-probe-before-the-design')
state=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
task=state/'pilot-ideation-runs-a-probe-before-the-design'
v=task/'evidence/validation-1'
head='f0e00d30ce00542b2895f13173bd41075cc8bfd4'; base='88f86f2749dadb6f4ef0cf9aa089c1827096865b'
(s/'tmp').mkdir()
env=dict(os.environ,TMPDIR=str(s/'tmp'),PYTHONDONTWRITEBYTECODE='1')
for source,dest in [(w,s/'code.git'),(state,s/'state.git')]:
    with (s/(dest.name+'.clone.log')).open('w') as log:
        subprocess.run(['git','clone','--bare','--shared',str(source),str(dest)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
replay=s/'replay_dispatch.py'
replay.write_bytes(subprocess.check_output(['git','-C',str(w),'show',head+':kc-dev-flow-2/scripts/replay_dispatch.py']))
readme=s/'adopter-README.md'
readme.write_bytes(subprocess.check_output(['git','-C',str(w),'show',base+':docs/dev2/README.md']))
cmd=['python3','-B',str(replay),'build','--run-dir',str(s/'live'),'--package-repo',str(s/'code.git'),'--package-ref',head,'--adopter-readme',str(readme),'--readme-base-ref',base,'--state-repo',str(s/'state.git'),'--state-commit','08d61c3e48d7365f7e058d16bea85fd61906539a','--task','pr-watch-tasks-foreign-worktree','--code-repo',str(s/'code.git'),'--code-commit',base,'--stage','ideation','--checklist',str(task/'evidence/ideation-1/inputs/pr-watch-tasks-foreign-worktree.checklist.txt'),'--scope',str(task/'evidence/ideation-1/inputs/pr-watch-tasks-foreign-worktree.scope.txt'),'--spacedock','/Users/kent/.local/bin/spacedock']
(s/'rebuild-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
with (s/'rebuild.log').open('w') as log:
    subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
seed=s/'live/wf/.spacedock-state/pr-watch-tasks-foreign-worktree.md'
remove=next(line[1:] for line in (v/'live-seed-adjustment.diff').read_text().splitlines() if line.startswith('-- Trial'))
original=seed.read_text(); assert original.count(remove)==1
seed.write_text(original.replace(remove+'\n','',1))
(s/'seed-adjustment-check.json').write_text(json.dumps(dict(removed_trial_paragraphs=1,source='validation-1/live-seed-adjustment.diff',scope_change_after_backlog=True),indent=2)+'\n')
# Regenerate the stage using the helper command emitted by this new dispatch.
text=(s/'live/dispatch.md').read_text(); block=text.split('### Fetch commands\n',1)[1]
fetch=next(line.strip() for line in block.splitlines() if line.startswith('    '))
with (s/'stage-def.regenerated.txt').open('w') as output:
    subprocess.run(['bash','-c',fetch],env=env,stdout=output,check=True)
expected=json.loads((v/'live/input-digests.json').read_text())
rows=[]
oldroot='/private/tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/validation-1'
for name,want in expected.items():
    p=s/'live'/name; raw=p.read_bytes(); digest=hashlib.sha256(raw).hexdigest()
    # Report an optional transparent relocation comparison, never call it a raw match.
    relocated=raw.replace(str(s).encode(),oldroot.encode())
    rows.append(dict(file=name,expected=want,regenerated_sha256=digest,raw_match=digest==want,relocation_only_sha256=hashlib.sha256(relocated).hexdigest(),relocation_only_match=hashlib.sha256(relocated).hexdigest()==want))
(s/'input-comparison.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
