from pathlib import Path
import json
import investigate as p
p.RESULT_NAME='audit-results.json'
clean=[{'reviewer':'codex','head':p.HEAD,'exit':0,'outcome':'clean','evidence':'review:5','scope':'pr'},
       {'reviewer':'copilot','head':p.HEAD,'exit':0,'outcome':'answered','evidence':'review:2','scope':'pr'}]

def summary_edit(fn):
 def setup(root,task,q,s,c,route):
  s.write_text(fn(s.read_text()));c.write_text(q.read_text()+s.read_text())
 return setup

def task_edit(fn):return lambda text:fn(text)

def missing_observed(root,task,q,s,c,route):
 path=p.g.task_folder(task)/'captain-steps/1.md';path.write_text(path.read_text().replace('Observed: checks passed','Observed:'))

def bad_step_candidate(root,task,q,s,c,route):
 path=p.g.task_folder(task)/'captain-steps/1.md';path.write_text(path.read_text().replace(p.HEAD,'f'*40))

def no_steps(root,task,q,s,c,route):(p.g.task_folder(task)/'captain-steps/1.md').unlink()

def prod_setup(root,task,q,s,c,route):
 report=p.g.task_folder(task)/'security/validation-1.yaml';report.parent.mkdir(parents=True);report.write_text('tob_security_review:\n  pr: 9\n  findings: []\n')
 task.write_text(task.read_text()+f'\nSecurity review (validation): security/validation-1.yaml at {p.HEAD}\n')
 s.write_text(s.read_text().replace(p.DECL,'Second reviewer: not triggered.\n'));c.write_text(q.read_text()+s.read_text())

def merge_setup(exit,command='python3 -B demo.py'):
 def setup(root,task,q,s,c,route):
  folder=p.g.task_folder(task)/'merge';folder.mkdir();(folder/'result-1.json').write_text(json.dumps({'head':p.HEAD,'trunk':'b'*40,'command':command,'tree':'c'*40,'exit':exit}))
 return setup

def after_config(root,task,q,s,c,route,records):
 r=root/'README.md';r.write_text(r.read_text().replace('second-reviewer: copilot','second-reviewer: other'))

def after_steps(root,task,q,s,c,route,records):
 path=p.g.task_folder(task)/'captain-steps/1.md';path.write_text(path.read_text()+'\nChanged after check.\n')

def after_report(root,task,q,s,c,route,records):task.write_text(task.read_text()+'\nReport changed after check.\n')
def after_question(root,task,q,s,c,route,records):q.write_text(q.read_text()+'\nA changed question sentence.\n')

cases=[]
p.results=[]
def run(name,expected,**kw):
 got=p.run('audit-final-'+name,reviewer_rows=kw.pop('reviewer_rows',clean),**kw)
 actual={k:[v['check_exit'],v['question_exit']] for k,v in got.items()}
 cases.append({'case':name,'expected':expected,'actual':actual,'match':actual==expected})
 (p.S/'audit-assertions.json').write_text(json.dumps(cases,indent=2)+'\n')
 assert actual==expected,(name,actual,expected)

G={'legacy':[0,0],'record':[0,0]};B={'legacy':[1,1],'record':[1,1]};LOST={'legacy':[1,1],'record':[0,0]}
run('second-declaration-missing',LOST,setup=summary_edit(lambda s:s.replace(p.DECL,'')))
run('second-declaration-duplicate',LOST,setup=summary_edit(lambda s:s+p.DECL))
run('second-declaration-wrong-name',LOST,setup=summary_edit(lambda s:s.replace(p.DECL,'Second reviewer: codex because authority.\n')))
run('second-trigger-empty',LOST,setup=summary_edit(lambda s:s.replace(p.DECL,'Second reviewer: copilot because\n')))
pending=[clean[0],clean[1]|{'outcome':'pending','exit':4,'evidence':None}]
run('second-not-triggered-pilot',G,q_extra='Second reviewer: not triggered.\n',reviewer_rows=pending,setup=summary_edit(lambda s:s.replace(p.DECL,'Second reviewer: not triggered.\n')))
run('second-not-triggered-db',B,q_extra='Second reviewer: not triggered.\n',body_extra='\n## FO alignment\nSurfaces: db\n',reviewer_rows=pending,setup=summary_edit(lambda s:s.replace(p.DECL,'Second reviewer: not triggered.\n')))
for profile,expect in [('prod',B),('"prod"',LOST),("'prod'",LOST)]:
 run('second-not-triggered-profile-'+('plain' if profile=='prod' else 'double' if profile[0]=='"' else 'single'),expect,
     task_transform=lambda s,value=profile:s.replace('profile: pilot','profile: '+value),q_extra='Second reviewer: not triggered.\n',reviewer_rows=pending,setup=prod_setup)
run('decline-without-reason',B,q_extra='Declined: Deferred risk, synthetic finding.\n')
run('decline-short-reason',B,q_extra='Declined: Deferred risk, synthetic finding (no).\n')
run('decline-reason-control',G,q_extra='Declined: Deferred risk, synthetic finding (controlled fixture).\n')
run('validation-deferred-and-polish-unjoined',B,body_extra='\n- F1 Deferred risk: synthetic issue.\n- F2 Polish: another issue.\n')
run('validation-deferred-and-polish-one-missing',B,body_extra='\n- F1 Deferred risk: synthetic issue.\n- F2 Polish: another issue.\n',q_extra='Declined: Deferred risk, synthetic finding (controlled fixture).\n')
run('validation-deferred-and-polish-control',G,body_extra='\n- F1 Deferred risk: synthetic issue.\n- F2 Polish: another issue.\n',q_extra='Declined: Deferred risk, synthetic finding (controlled fixture); Polish, another issue (controlled fixture).\n')
run('validation-rejected-not-automatic-gate',G,task_transform=lambda s:s.replace('PASSED at','REJECTED at'))
run('validation-rounds-observed',G,setup=lambda root,task,q,s,c,route:(p.g.task_folder(task)/'dispatch/validation-2.md').write_text(p.t.record(p.HEAD)))
run('external-round-field-removed',LOST,rounds='')
run('external-round-field-malformed',LOST,rounds='External rounds: -1\n')
run('external-round-field-duplicate',LOST,rounds='External rounds: 1\nExternal rounds: 2\n')
run('sufficiency-necessity-labels-removed',LOST,setup=summary_edit(lambda s:s.replace(p.t.CLAUSES,'')))
run('captain-observation-empty',{'legacy':[0,1],'record':[1,1]},setup=missing_observed)
run('captain-step-candidate-differs',{'legacy':[0,1],'record':[1,1]},setup=bad_step_candidate)
run('captain-step-missing',{'legacy':[0,2],'record':[1,1]},setup=no_steps)
run('captain-step-mutated-after-check',{'legacy':[0,0],'record':[0,1]},after_check=after_steps)
run('validation-report-mutated-after-check',{'legacy':[0,0],'record':[0,1]},after_check=after_report)
run('question-mutated-after-check',{'legacy':[0,0],'record':[0,1]},after_check=after_question)
run('reviewer-config-invalid-before-check',{'legacy':[2,2],'record':[2,1]},config='extensions: [codex]\nsecond-reviewer: copilot\n')
run('reviewer-config-invalid-after-check',{'legacy':[0,2],'record':[0,0]},after_check=after_config)
run('unreadable-reviewer',{'legacy':[0,0],'record':[2,1]},reviewer_rows=[clean[0],clean[1]|{'outcome':'error','exit':2,'evidence':None}])
run('pending-primary-reviewer',{'legacy':[0,0],'record':[1,1]},reviewer_rows=[clean[0]|{'outcome':'pending','exit':4,'evidence':None},clean[1]])
mergeconfig='extensions: [codex, copilot]\nsecond-reviewer: copilot\nmerge-test: python3 -B demo.py\n'
run('moved-trunk-no-result',{'legacy':[1,1],'record':[1,1]},config=mergeconfig,trunk=('diverged','b'*40))
run('moved-trunk-failed-result',B,config=mergeconfig,trunk=('diverged','b'*40),setup=merge_setup(1))
run('moved-trunk-wrong-command',B,config=mergeconfig,trunk=('diverged','b'*40),setup=merge_setup(0,'not the configured command'))
run('moved-trunk-result-control',G,config=mergeconfig,trunk=('diverged','b'*40),setup=merge_setup(0))
run('moved-trunk-not-run-question-control',G,config=mergeconfig,trunk=('diverged','b'*40),q_extra='Merge result: not run: controlled fixture limit\n')
run('moved-trunk-not-run-summary-only',{'legacy':[0,1],'record':[1,1]},config=mergeconfig,trunk=('diverged','b'*40),summary_extra='Copilot review:2.\nMerge result: not run: controlled fixture limit\n')
run('count-warning-omitted',G,q_extra='There are 17 checks.\n')
run('scope-warning-omitted',G,q_extra='Existing tasks are not affected.\n')
print(json.dumps({'cases':len(cases),'expected_route_comparisons_match':all(r['match'] for r in cases)}))
