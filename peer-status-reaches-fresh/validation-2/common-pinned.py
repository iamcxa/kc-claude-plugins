import sys, importlib.util, subprocess, json, re
from pathlib import Path
P=Path(sys.argv[1]); SD=Path(sys.argv[2])
spec=importlib.util.spec_from_file_location('fixtures',P/'scripts/test_pr_watch.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
f=m.TasksTests();f.setUp()
out={}
try:
 f.readme('learn, peers, paseo');
 (f.workflow/'README.md').write_text((f.workflow/'README.md').read_text().replace('entity-type: task','entity-type: task\ntrunk: main'))
 f.task('some-task',pr='o/r#7')
 for label,args in [('tasks-pending',m.view()),('tasks-green',m.view())]:
  if label=='tasks-pending':args['statusCheckRollup']=[{'status':'IN_PROGRESS','conclusion':None}]
  code,lines=f.tasks({'pr view 7':args});assert code==0,(code,lines);out[label]='\n'.join(lines)
 wait=m.PrWatchTests()
 for label,snap in [('wait-green',m.snap()),('wait-merged',m.snap(state='MERGED'))]:
  wait.run_main(['add','o/r#1'],[m.snap(checks='pending')],f.root/(label+'.json'))
  code,o=wait.run_main(['wait','1'],[snap],f.root/(label+'.json'));assert code==0;out[label]=o
 code,lines=f.tasks({'pr view 7':m.view('MERGED')});assert code==0;out['tasks-missing']='\n'.join(lines)
 f.report('some-task');code,lines=f.tasks({'pr view 7':m.view('MERGED')});assert code==0;out['tasks-rerun']='\n'.join(lines)
 out['after-lines']='\n'.join(l for l in lines if l.startswith('after pr-merge:'))
 (f.state/'_archive').mkdir();f.git(f.state,'mv','some-task.md','_archive/some-task.md');f.git(f.state,'mv','some-task','_archive/some-task');f.git(f.state,'commit','-qm','archive')
 d=subprocess.run([sys.executable,'-B',str(P/'scripts/observer_check.py'),str(f.state),'some-task'],capture_output=True,text=True);assert d.returncode==0,d.stdout;out['observer-archived']=d.stdout
 gs=importlib.util.spec_from_file_location('gatefixtures',P/'scripts/test_delivery_gate.py')
 gm=importlib.util.module_from_spec(gs);gs.loader.exec_module(gm)
 code,o=gm.DeliveryGateTests().check()
 assert code==0,(code,o)
 out['gate']=o;out['gate-exit']=str(code)
 def sec(t,h):return h+t.split(h,1)[1].split('\n## ',1)[0]
 wf=(P/'references/sd/workflow.md').read_text();mod=(P/'references/sd/mods/kc-dev-flow-2.md').read_text();pm=(SD/'mods/pr-merge.md').read_text()
 stat={'startup-hook':sec(pm,'## Hook: startup'),'idle-hook':sec(pm,'## Hook: idle'),'mod':mod,'authority':sec(wf,'## Delivery authority'),'extensions':sec(wf,'## Extensions'),'learn':(P/'extensions/learn/EXTENSION.md').read_text()}
 w=lambda x:len(x.split())
 total=lambda st,ot:sum(w(stat[k]) for k in st)+sum(w(out[k]) for k in ot)
 rows={
 'startup':total(['startup-hook','mod'],['tasks-pending']),
 'idle-open':total(['idle-hook','mod','authority'],['tasks-green','wait-green']),
 'idle-merged':total(['idle-hook','mod','authority','learn'],['wait-merged','tasks-missing','tasks-rerun']),
 'after-archive':total(['mod','learn'],['after-lines','observer-archived']),
 'merge-ask':total(['authority','extensions'],['wait-green','gate']),
 }
 result={'static-words':{k:w(v) for k,v in stat.items()},'output-words':{k:w(v) for k,v in out.items() if k!='gate-exit'},'common-totals':rows,'outputs':out}
 # JSON is printed below; no persistent output path is required.
 print(json.dumps(result,indent=2))
finally:f.doCleanups()
