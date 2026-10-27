import importlib.util, json, re, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
WT=HERE.parents[1]
PKG=WT/'kc-dev-flow-2'
BASE='8bf4f3582411e8e4238f19fbadda8ddeca6767be'
def base(path): return subprocess.check_output(['git','-C',str(WT),'show',f'{BASE}:kc-dev-flow-2/{path}'],text=True)
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path); value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
baseline=HERE/'base_pr_watch.py';baseline.write_text(base('scripts/pr_watch.py'))
sys.path.insert(0,str(PKG/'scripts'))
tests=module('test_pr_watch',PKG/'scripts/test_pr_watch.py')
current=tests.watch
old=module('base_watch',baseline)
old.SCRIPTS=PKG/'scripts'
outputs={}
for version,watch in [('before',old),('after',current)]:
 tests.watch=watch
 for moment in ('open','merged','after_archive'):
  t=tests.TasksTests();t.setUp()
  try:
   t.readme('learn');t.task('one',pr='o/r#7',worktree=False);t.report('one')
   if moment=='after_archive':
    arc=t.state/'_archive';arc.mkdir();(t.state/'one.md').rename(arc/'one.md');(t.state/'one').rename(arc/'one')
    t.git(t.state,'add','-A');t.git(t.state,'commit','-qm','archive')
    done=subprocess.run([sys.executable,'-B',str(PKG/'scripts/observer_check.py'),str(t.state),'one'],capture_output=True,text=True)
    assert done.returncode==0,done.stdout
    text=done.stdout
   else:
    code,lines=t.tasks({'pr view 7':tests.view('OPEN' if moment=='open' else 'MERGED')})
    assert code==0,lines
    text='\n'.join(lines)+'\n'
   outputs[f'{version}:{moment}']={'words':len(text.split()),'stdout':text}
  finally:t.doCleanups()
def section(text,name): return re.search(r'^## '+name+r'\n(.*?)(?=^## |\Z)',text,re.M|re.S)[1]
count=lambda s:len(s.split())
values={}
for version in ('before','after'):
 read=lambda path:base(path) if version=='before' else (PKG/path).read_text()
 values[version]={'dev':count(read('skills/dev/SKILL.md')),'mod':count(read('references/sd/mods/kc-dev-flow-2.md')),
                  'learn':count(read('extensions/learn/EXTENSION.md')),'extensions':count(section(read('references/sd/workflow.md'),'Extensions')),
                  'delivery':count(section(read('references/sd/workflow.md'),'Delivery authority'))}
rows={}
for version,v in values.items():
 out=lambda moment:outputs[f'{version}:{moment}']['words']
 rows[version]={'startup':v['dev']+v['mod']+v['learn']+v['extensions']+out('open'),
 'idle_open':v['mod']+v['learn']+v['extensions']+v['delivery']+out('open'),
 'idle_merged':v['mod']+v['learn']+v['extensions']+out('merged'),
 'after_archive':v['mod']+v['learn']+out('after_archive'),
 'merge_ask':v['delivery']+v['extensions'],'recovery_idle':v['mod']+v['learn']+v['extensions']}
tests.watch=current
t=tests.TasksTests();t.setUp()
try:
 t.readme('learn');t.archive('missing')
 code,lines=t.tasks({});assert (code,lines)==(0,['next: run kc-dev-flow-2:learn for missing.'])
 missing={'stdout':'\n'.join(lines),'words':count('\n'.join(lines))}
 key=current.job_key({'workflow':'docs/dev2','task_id':'missing'})
 _,patch=t.notice_run({'notices':[{'job':key,'state':'uncertain'}]})
 with patch:code,lines=t.tasks({})
 uncertain={'stdout':'\n'.join(lines),'words':count('\n'.join(lines))}
 _,patch=t.notice_run({'notices':None})
 with patch:code,lines=t.tasks({})
 diagnostic={'stdout':'\n'.join(lines),'words':count('\n'.join(lines))}
finally:t.doCleanups()
expected={'startup':1342,'idle_open':1037,'idle_merged':570,'after_archive':356,'merge_ask':680,'recovery_idle':550}
assert rows['after']==expected,rows
result={'passages':values,'rows':rows,'outputs':outputs,'missing':missing,'uncertain':uncertain,'diagnostic':diagnostic,
'limits':'5 words per repeated missing name; 55 for 11, 145 for reconstructed 29, 90 for current-key model 18. A newly loaded learn skill plus framework may add 5985 words; task/provider evidence adds more. CI cost per PR not measured.'}
(HERE/'recount.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
