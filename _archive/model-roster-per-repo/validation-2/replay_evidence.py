import hashlib,json,os,pathlib,subprocess
v=pathlib.Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-per-repo/.validation-2');s=pathlib.Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state');out=pathlib.Path('/tmp/roster-validation2-a8536dc5')
def run(cmd,cwd=v):
 r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,check=True); return r.stdout
head='a8536dc5239edc3db6c1b76cb3bb7e1ce0433088';base='9f065b01f1c6d6561793a168f584075edb85bf1f'
allowed={'docs/adr/0047-repository-stage-model-rosters-keep-readme-defaults-when-absent.md','kc-dev-flow-2/extensions/paseo/EXTENSION.md','kc-dev-flow-2/references/model-roster-defaults.json','kc-dev-flow-2/references/model-roster.md','kc-dev-flow-2/references/sd/adoption.md','kc-dev-flow-2/references/sd/workflow.md','kc-dev-flow-2/scripts/model_roster.py','kc-dev-flow-2/scripts/test_sd_dispatch.py'}
changed=set(run(['git','-C',str(v),'diff','--name-only',base,head]).splitlines());assert changed==allowed,changed
assert not run(['git','-C',str(v),'diff',base,head,'--','.github','kc-dev-flow-2/agents','kc-dev-flow-2/skills','kc-dev-flow-2/scripts/laws_check.py','kc-dev-flow-2/scripts/dispatch_records.py'])
def blob(rev,path):return run(['git','-C',str(v),'show',rev+':kc-dev-flow-2/'+path])
def section(t,h):return t.split('## '+h+'\n',1)[1].split('\n## ',1)[0]
def count(rev):
 get=lambda p:blob(rev,p);w=get('references/sd/workflow.md');mod=get('references/sd/mods/kc-dev-flow-2.md');review=section(w,'FO steps: review findings');codex=get('extensions/codex/EXTENSION.md');copilot=get('extensions/copilot/EXTENSION.md');words=lambda *xs:sum(len(x.split()) for x in xs)
 result=dict(startup=words(get('README.md'),get('skills/dev/SKILL.md'),w,mod),idle_open=words(mod,review,codex,copilot),idle_merged_archive=words(mod,get('extensions/learn/EXTENSION.md')),merge_ask=words(section(w,'Delivery authority'),review,codex,copilot),workflow=words(w),dispatch=words(section(w,'Stages'),get('extensions/paseo/EXTENSION.md')),adoption=words(get('references/sd/adoption.md')))
 if rev==head:
  result.update(runtime=words(get('references/model-roster.md')),settings=words(get('references/model-roster-defaults.json')))
  result['configured_dispatch_static']=result['dispatch']+result['runtime']+result['settings'];result['absent_dispatch_static']=result['dispatch']+result['runtime'];result['adoption_with_reference_defaults']=result['adoption']+result['runtime']+result['settings']
 return result
words=dict(base=count(base),candidate=count(head)); print(json.dumps(words,indent=2))
questions=[json.loads(x) for x in (s/'model-roster-per-repo/adoption-trial/question-receipts.jsonl').read_text().splitlines()]; words['fo_record_questions']=[dict(time=x['ts'],words=len(json.dumps(x['asked'],ensure_ascii=False).split())) for x in questions if 'asked' in x];words['fo_record_answers']=[dict(time=x['ts'],words=len(str(x['result']).split())) for x in questions if 'result' in x and x['ts']]
(out/'words.json').write_text(json.dumps(words,indent=2));(out/'scope.json').write_text(json.dumps(sorted(changed),indent=2))
results=[]
for name in ('accept','customize'):
 root=pathlib.Path('/tmp/roster-validation2-a8536dc5')/('fo-'+name+'-replay');root.mkdir();run(['git','init','-q',str(root)])
 (root/'.dev2').mkdir(); original=(s/'model-roster-per-repo/adoption-trial'/f'{name}-model-roster.json').read_bytes();(root/'.dev2/model-roster.json').write_bytes(original)
 run(['git','-C',str(root),'add','--','.dev2/model-roster.json']);run(['git','-C',str(root),'-c','user.name=Validation','-c','user.email=validation@example.invalid','-c','commit.gpgsign=false','-c','core.hooksPath=/dev/null','commit','-qm','test: replay recorded choice'])
 for stage in ('ideation','implementation','validation','repair'):
  cmd=['python3','-B',str(v/'kc-dev-flow-2/scripts/model_roster.py'),'resolve','--code-root',str(root),'--stage',stage]
  if stage=='validation':
   for record in ('implementation-1.md','implementation-1-message-1.md','implementation-1-message-2.md','implementation-2.md','implementation-2-message-1.md'):cmd+=['--author-record',str(s/'model-roster-per-repo/dispatch'/record)]
  result=json.loads(run(cmd));results.append(dict(case=name,stage=stage,result=result));print(name,stage,result['tuple'],result.get('family'))
 assert (root/'.dev2/model-roster.json').read_bytes()==original
(out/'fo-data-replay.json').write_text(json.dumps(results,indent=2))
