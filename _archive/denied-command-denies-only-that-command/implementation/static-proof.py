from pathlib import Path
import subprocess, tempfile, shutil, json, re, hashlib
wt=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-denied-command-denies-only-that-command')
out=Path('/tmp/denied-command-evidence'); pkg=wt/'kc-dev-flow-2'; base=json.loads((out/'pins.json').read_text())['base']; results=[]
sentence='A command refused by anyone, with or without a reason, is refused alone: do not work around it; continue the steps it does not block, and report it and what it left unchecked.'
def run(name,args,cwd=wt):
 p=subprocess.run(args,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 (out/(name+'.log')).write_text(p.stdout); return p
with tempfile.TemporaryDirectory(prefix='denied-static-') as tmp:
 root=Path(tmp); wf=root/'wf'; wf.mkdir(); original=(pkg/'references/sd/workflow.md').read_text(); (wf/'README.md').write_text(original)
 for stage in ('ideation','implementation','validation'):
  p=run('stage-'+stage,['/Users/kent/.local/bin/spacedock','dispatch','show-stage-def','--workflow-dir',str(wf),'--stage',stage]); count=' '.join(p.stdout.split()).count(sentence); assert p.returncode==0 and count==1,(stage,count,p.stdout)
  results.append({'name':'AC-1 '+stage,'status':'passed','evidence':'stage-'+stage+'.log; sentence count 1'})
 mutant=original.replace('    - name: ideation\n      model: opus\n      gate: true\n      context-sections:\n        - Dispatch facts','    - name: ideation\n      model: opus\n      gate: true')
 assert mutant!=original; (wf/'README.md').write_text(mutant)
 p=run('mutation-context',['/Users/kent/.local/bin/spacedock','dispatch','show-stage-def','--workflow-dir',str(wf),'--stage','ideation']); assert sentence not in ' '.join(p.stdout.split()); results.append({'name':'AC-1 context removal falsifier','status':'passed','evidence':'mutation-context.log; ideation loses sentence'})
 tree=root/'kc-dev-flow-2'; shutil.copytree(pkg,tree,ignore=shutil.ignore_patterns('__pycache__','*.pyc')); shutil.copytree(wt/'scripts',root/'scripts')
 workflow=tree/'references/sd/workflow.md'; lint=tree/'scripts/lint-skills.py'; script=lint.read_text()
 removed=re.sub(r'A command\s+refused by anyone, with or without a reason, is refused alone: do not work\s+around it; continue the steps it does not block, and report it and what it\s+left unchecked\. ', '',original)
 assert len(original.split())-len(removed.split())==33
 workflow.write_text(removed)
 p=run('mutation-sentence',['python3','-B',str(lint)],root); assert p.returncode==1 and '33' in p.stdout; results.append({'name':'AC-2 sentence removal falsifier','status':'passed','evidence':'mutation-sentence.log; lint exit 1, 33 words under budget'})
 workflow.write_text(original)
 cut=re.sub(r'    dict\(delta=33,.*?\n         loaded=.*?\),\n','',script,flags=re.S); assert cut!=script; lint.write_text(cut)
 p=run('mutation-budget-step',['python3','-B',str(lint)],root); assert p.returncode==1 and '33' in p.stdout; results.append({'name':'AC-2 budget-step removal falsifier','status':'passed','evidence':'mutation-budget-step.log; lint exit 1, 33 words over budget'})
basebytes=subprocess.check_output(['git','-C',str(wt),'show',base+':kc-dev-flow-2/references/sd/workflow.md'])
def secret(data):return data.split(b'- **Secrets:**',1)[1].split(b'\n\n',1)[0]
assert secret(basebytes)==secret((pkg/'references/sd/workflow.md').read_bytes())
results.append({'name':'AC-8 Secrets bullet bytes','status':'passed','evidence':'sha256 '+hashlib.sha256(secret(basebytes)).hexdigest()})
p=run('sentence-homes',['git','-C',str(wt),'grep','-c','is refused alone','--','kc-dev-flow-2/']); assert len(p.stdout.splitlines())==1
before=basebytes.decode(); after=(pkg/'references/sd/workflow.md').read_text()
ext=(pkg/'extensions/paseo/EXTENSION.md').read_text(); prevext=subprocess.check_output(['git','-C',str(wt),'show',base+':kc-dev-flow-2/extensions/paseo/EXTENSION.md'],text=True)
def section(text,title): return text.split('## '+title+'\n',1)[1].split('\n## ',1)[0]
counts={'startup_resume':[len(before.split()),len(after.split())], 'dispatch_facts':[len(section(before,'Dispatch facts').split()),len(section(after,'Dispatch facts').split())], 'permission_callback':[len(section(prevext,'Worker permission requests').split()),len(section(ext,'Worker permission requests').split())]}
(out/'word-counts.json').write_text(json.dumps(counts,indent=2)); (out/'static-results.json').write_text(json.dumps(results,indent=2)); print(json.dumps({'results':results,'word_counts':counts},indent=2))
