from pathlib import Path
import subprocess, re, json, hashlib, sys, importlib.util
sys.dont_write_bytecode=True
W=Path('/tmp/peers-validation-730-cycle1')
B='c70f1b22cb1e4a66fd15c617647c778d54c59ec9'
E=Path('/tmp/peers-validation-730-cycle1-evidence')
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
SD=Path('/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3')
# Pin the actual startup/idle passages, rather than matching inline mentions.
fo=(SD/'skills/first-officer/references/first-officer-shared-core.md').read_text()
def section(text,name):
    match=re.search(r'^## '+re.escape(name)+r'\n',text,re.M);assert match,name
    tail=text[match.start():];end=re.search(r'^## ',tail[4:],re.M)
    return tail[:end.start()+4] if end else tail
startup=section(fo,'Startup')
idle=section((SD/'skills/first-officer/references/claude-fo-dispatch.md').read_text(),'Awaiting Completion')
texts={}
for variant in ('base','candidate'):
    def read(p):return subprocess.check_output(['git','-C',str(W),'show',f'{B}:kc-dev-flow-2/{p}'],text=True) if variant=='base' else (W/'kc-dev-flow-2'/p).read_text()
    texts[variant]={p:read(p) for p in ['references/sd/workflow.md','references/sd/mods/kc-dev-flow-2.md','extensions/learn/EXTENSION.md','skills/learn/SKILL.md','extensions/peers/EXTENSION.md']}
    if variant=='candidate':texts[variant]['extensions/paseo/EXTENSION.md']=read('extensions/paseo/EXTENSION.md')
upstream=Path('/Users/kent/.agents/skills/paseo/SKILL.md').read_text()
manifest={'base_sha':B,'upstream_paseo':{'words':len(upstream.split()),'sha256':hashlib.sha256(upstream.encode()).hexdigest()},'outputs':{k:len(v.split()) for k,v in outputs.items()},'routes':{},'sd_inputs':{name:{'words':len(text.split()),'sha256':hashlib.sha256(text.encode()).hexdigest()} for name,text in [('first-officer-shared-core.md#Startup',startup),('claude-fo-dispatch.md#Awaiting Completion',idle)]}}
for variant,files in texts.items():
    counts={p:len(txt.split()) for p,txt in files.items()}
    manifest[variant]={'inputs':{p:{'words':counts[p],'sha256':hashlib.sha256(txt.encode()).hexdigest()} for p,txt in files.items()},'sections':{name:len(section(files['references/sd/workflow.md'],name).split()) for name in ['Delivery authority','Extensions']}}
    c=manifest[variant];workflow=counts['references/sd/workflow.md'];mod=counts['references/sd/mods/kc-dev-flow-2.md'];learn=counts['extensions/learn/EXTENSION.md'];skill=counts['skills/learn/SKILL.md'];peers=counts['extensions/peers/EXTENSION.md']
    # Stable SD pieces are counted separately below, retaining exact source paths.
    manifest['routes'][variant]={'startup_without_exchange':workflow+mod+len(startup.split())+len(outputs['OPEN'].split()),'idle_open':mod+len(idle.split())+c['sections']['Delivery authority']+len(outputs['OPEN'].split()),'idle_merged':mod+len(idle.split())+c['sections']['Delivery authority']+learn+len(outputs['MERGED'].split()),'after_archive':mod+learn+skill+len(outputs['archive'].split()),'merge_ask':sum(c['sections'].values())+len(outputs['merge'].split()),'native_claude':peers,'unsupported':peers,'first_task_opening':peers if variant=='candidate' else 0,'proactive_paseo':peers+counts.get('extensions/paseo/EXTENSION.md',0)+len(upstream.split()) if variant=='candidate' else peers,'unlisted_incoming':peers+len(upstream.split()) if variant=='candidate' else peers,'gate_reply':peers+len(upstream.split()) if variant=='candidate' else peers,'warm_exchange':0,'source_repair':0}
(E/'reading-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest['routes'],indent=2))
