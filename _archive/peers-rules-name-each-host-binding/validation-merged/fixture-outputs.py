from pathlib import Path
import subprocess,re,json,hashlib,sys,importlib.util
sys.dont_write_bytecode=True
W=Path(sys.argv[1]);E=Path(sys.argv[2]);E.mkdir(parents=True,exist_ok=True)
def load(name):
    sys.path.insert(0,str(W/'kc-dev-flow-2/scripts'))
    spec=importlib.util.spec_from_file_location(name,W/'kc-dev-flow-2/scripts'/f'{name}.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
watch=load('test_pr_watch')
outputs={}
for state in ('OPEN','MERGED'):
    t=watch.TasksTests();t.setUp()
    try:
        t.readme('learn, peers');t.task('some-task',pr='o/r#7')
        if state=='MERGED': t.report('some-task')
        code,lines=t.tasks({'pr view 7':watch.view(state)})
        assert code==0
        outputs[state]='\n'.join(lines)+'\n'
        (E/f'watch-{state}.txt').write_text(outputs[state])
        if state=='OPEN':
            note=t.state/'.notes/peer-exchanges.md';note.parent.mkdir();note.write_text('---\ntitle: peer note\nstatus: validation\npr: o/r#9\n---\npeer, date, question, answer, checked source\n')
            code,lines=t.tasks({'pr view 7':watch.view(state)})
            assert code==0 and list(t.watched())==['o/r#7']
            (t.workflow/'README.md').write_text((W/'kc-dev-flow-2/references/sd/workflow.md').read_text())
            # The real discovery CLI reads the same disposable state, without hooks.
            sd=subprocess.run(['/Users/kent/.local/bin/spacedock','status','--workflow-dir',str(t.workflow),'--json'],capture_output=True,text=True)
            (E/'discovery.json').write_text(sd.stdout+sd.stderr)
            assert sd.returncode==0,sd.stdout+sd.stderr
            parsed=json.loads(sd.stdout)
            assert 'peer note' not in sd.stdout and 'some-task' in sd.stdout
    finally: t.doCleanups()
obs=load('test_observer_check');t=obs.ObserverCheckTest();t.setUp()
try:
    t.write_report('ok | rule: x\n');t.commit('report');t.archive()
    code,outputs['archive']=obs.check(t.state,obs.SLUG);assert code==0
    (E/'archive.txt').write_text(outputs['archive'])
finally:t.doCleanups()
dg=load('test_delivery_gate');t=dg.DeliveryGateTests()
code,outputs['merge']=t.check(text='Deliver this change. Codex review:1 clean.',front='extensions: []\n');assert code==0
(E/'merge.txt').write_text(outputs['merge'])

(E/'output-words.json').write_text(json.dumps({k:len(v.split()) for k,v in outputs.items()},indent=2)+'\n')
