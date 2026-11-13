from pathlib import Path
import contextlib, hashlib, importlib.util, io, json, os, re, shutil, subprocess, sys
from unittest import mock
WT=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/poc-merge-ask-is-produced-from-records')
SCR=Path(__file__).parent
STATE=WT.parents[1]/'docs/dev2/.spacedock-state'
spec=importlib.util.spec_from_file_location('delivery_tests',WT/'kc-dev-flow-2/scripts/test_delivery_gate.py');tests=importlib.util.module_from_spec(spec);spec.loader.exec_module(tests);gate=tests.gate
SD='/Users/kent/.local/bin/spacedock'
commands=[]

def save(p,j):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,indent=2)+'\n')

def run(cmd,cwd,log):
 p=subprocess.run([str(x) for x in cmd],cwd=cwd,capture_output=True,text=True);log.write_text(p.stdout+p.stderr);commands.append({'command':[str(x) for x in cmd],'exit':p.returncode,'output':str(log.relative_to(SCR))});return p

def git(repo,*args):
 return subprocess.run(['git','-C',str(repo),'-c','user.name=Probe Fixture','-c','user.email=fixture@example.invalid','-c','commit.gpgsign=false',*args],capture_output=True,text=True,check=True)

def setup(name,head,body):
 code=SCR/(os.environ.get('PROBE_RUN','')+name);workflow=code/'workflow';state=workflow/'.spacedock-state';state.mkdir(parents=True,exist_ok=True)
 text=(WT/'kc-dev-flow-2/references/sd/workflow.md').read_text();text=text.replace('extensions: [learn, peers]','extensions: [codex, copilot, roborev]');(workflow/'README.md').write_text(text)
 git(code,'init','--initial-branch=main');git(code,'add','workflow/README.md');git(code,'commit','-m','test: local workflow fixture')
 git(state,'init','--initial-branch=spacedock-state/probe');task=state/'task.md';task.write_text('---\ntitle: Local record binding probe, not product delivery\nvariant: kc-dev-flow-2\nprofile: pilot\nstatus: validation\nmerge: pr\n---\n'+body)
 folder=state/'task';(folder/'dispatch').mkdir(parents=True,exist_ok=True);(folder/'dispatch/validation-1.md').write_text(tests.record(head));q=code/'question.txt';q.write_text(f'Deliver the observed candidate? Squash merge with --match-head-commit {head}, and removing its clean, pushed worktree, unless he says he merges or holds.\n')
 git(state,'add','--','task.md','task');git(state,'commit','-m','test: committed source before observation')
 return code,workflow,state,task,q

def bind(code,workflow,state,task,q,path,inspection=False):
 out=io.StringIO()
 with contextlib.redirect_stdout(out):exit=gate.main(['question',str(task),'--text-file',str(q),'--facts-record',str(path),'--workflow-dir',str(workflow)])
 (code/'question-check.log').write_text(out.getvalue());assert exit==(1 if inspection else 0),out.getvalue()
 git(state,'add','--','task.md','task');git(state,'commit','-m','test: immutable local facts source')
 record_bytes=path.read_text();cmd=[SD,'gate','prepare','task','--question',q.read_text(),'--artifact',str(task),'--summary',record_bytes,'--reference',str(path),'--workflow-dir',str(workflow)];p=run(cmd,code,code/'prepare.log')
 if p.returncode:raise AssertionError(p.stdout+p.stderr)
 brief=list((state/'task/review/validation').glob('briefing-*/index.json'))[-1];data=json.loads(brief.read_text());assert data['artifacts'][0]['summary']==record_bytes
 return {'question_exit':exit,'prepare_exit':p.returncode,'bound_summary_sha256':hashlib.sha256(data['artifacts'][0]['summary'].encode()).hexdigest(),'record_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'reference_count':len(data.get('context',[]))}

def replay():
 rows=[]
 for name in ['design-surfaces-task-dir-crash','held-and-closed-tasks-leave-the-design-queue']:
  source=STATE/'_archive'/name;record=max(source.glob('merge/ask-*.json'),key=lambda p:int(p.stem.split('-')[-1]));old=json.loads(record.read_text());head=old['head'];raw=(STATE/'_archive'/(name+'.md')).read_text();body=raw.split('\n---\n',1)[1]
  code,workflow,state,task,q=setup('replay-complete-'+name,head,body)
  shutil.copytree(source/'dispatch',state/'task/dispatch',dirs_exist_ok=True)
  shutil.copytree(source/'captain-steps',state/'task/captain-steps',dirs_exist_ok=True)
  brief=json.loads(next(source.glob('review/validation/briefing-*/index.json')).read_text());line=next(x for x in brief['artifacts'][0]['summary'].splitlines() if x.startswith('External round sources:'));ident=re.search(r'evidence=((?:summary|review|comment):\d+(?:@[0-9a-f]+)?)',line)[1]
  reviewers=[dict(reviewer='codex',head=head,scope='pr',outcome='clean',evidence=ident,exit=0),dict(reviewer='copilot',head=head,scope='pr',outcome='not-run',evidence=None,exit=5),dict(reviewer='roborev',head=head,scope='local',outcome='not-observed',evidence=None)]
  files=[re.search(r"'([^']+)'",x)[1] for x in old['points'] if x.startswith('point: path:')]
  before=q.read_bytes();out=io.StringIO()
  with tests.stubbed(code,head=head,files=files,pr=tests.pr_json(head=head,files=len(files)),adr=[p.name for p in (WT/'docs/adr').glob('*.md')]),tests.quiet_roles(),mock.patch.object(gate,'reviewer_facts',return_value=reviewers),contextlib.redirect_stdout(out):
   exit=gate.main(['check',str(task),'--pr',old['pr'],'--text-file',str(q),'--record-facts','--workflow-dir',str(workflow)])
  (code/'check.log').write_text(out.getvalue());assert exit==0,out.getvalue();assert q.read_bytes()==before
  path=next((state/'task/merge').glob('ask-*.json'));observed=json.loads(path.read_text());bound=bind(code,workflow,state,task,q,path);rows.append(dict(task=name,head=head,check_exit=exit,question_unchanged=True,validation=observed['validation'],**bound))
 save(SCR/'replays.json',{'cases':rows,'limit':'Public archived task/report inputs; package gh test doubles and controlled reviewer/role observations. Native gate prepare executed in isolated local repositories, no real gate or approval.'})

def rounds():
 audit=json.loads((STATE/'merge-ask-is-produced-from-records/evidence/ideation-1/audit/audit.json').read_text());rows=[]
 for source in audit['cases']:
  if source['declared_rounds']==source['remote_rounds_from_control']:continue
  root=SCR/('rounds-'+source['task']);root.mkdir(exist_ok=True);task=root/'task.md';task.write_text(tests.TASK);folder=root/'task/merge';folder.mkdir(parents=True,exist_ok=True);remote=[dict(reviewer='codex',head=source['head'],scope='pr',outcome='clean',evidence=e) for e in source['remote_ids_from_fo_control']];local=[dict(reviewer='roborev',head=source['head'],scope='local',outcome='clean',evidence='roborev:1810')];save(folder/'ask-1.json',dict(schema='delivery-facts/v1',reviewers=remote+local));count=gate.saved_rounds(task,remote+local);assert count==source['remote_rounds_from_control'];rows.append(dict(pr=source['pr'],before=source['declared_rounds'],after=count,duplicate_read_unchanged=True))
 save(SCR/'rounds.json',{'cases':rows,'rule':'distinct (reviewer, head, evidence) among saved scope=pr outcomes clean/answered/findings; local jobs/refusals excluded','limit':'Historical remote ids are FO-recorded inputs; calculation does not authenticate their old API origin.'})

def live():
 head=gate.run_gh('iamcxa/kc-claude-plugins','865')
 body='\n## Scope\nLocal read-only observation, not an independent validation of this PR.\n\n## Acceptance criteria\n**AC-1** Bind recorded observations.\n\n## Stage Report: validation\n\n- DONE: Capture a public live observation without changing the PR.\n  Fixture report, not a product verdict.\n\n### Summary\nValidation not observed for this local inspection.\n'
 code,workflow,state,task,q=setup('live-complete-state',head,body);q.write_text('Inspect the public PR observations and their limitations?\n')
 before=q.read_bytes();out=io.StringIO()
 with contextlib.redirect_stdout(out):
  exit=gate.main(['check',str(task),'--pr','iamcxa/kc-claude-plugins#865','--text-file',str(q),'--record-facts','--workflow-dir',str(workflow)])
 (code/'check.log').write_text(out.getvalue());paths=list((state/'task/merge').glob('*.json'))
 assert paths,out.getvalue()
 path=paths[-1];data=json.loads(path.read_text());assert q.read_bytes()==before
 bound=bind(code,workflow,state,task,q,path,inspection=exit!=0)
 save(SCR/'live.json',dict(pr=865,head=data['head'],check_exit=exit,question_unchanged=True,record=data,**bound,limit='Actual unmocked read-only public GitHub calls. Nonzero check/question hold the delivery route. Native prepare was called directly only as a local JSON-binding experiment, not a passing delivery preflight or real gate. No product validation or approval is claimed.'))


if __name__=='__main__':
 try:
  {'replay':replay,'rounds':rounds,'live':live}[sys.argv[1]]()
 finally:save(SCR/('commands-'+sys.argv[1]+'.json'),commands)
