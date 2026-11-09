import contextlib, copy, datetime, hashlib, importlib.util, io, json, os, re, subprocess, sys, types, unittest
from pathlib import Path

WT = Path(sys.argv[1]).resolve()
STATE = Path(sys.argv[2]).resolve()
E = Path(sys.argv[3]).resolve()
E.mkdir(parents=True, exist_ok=True)
SD = sys.argv[4]
BASE = 'e7c9381f2ae7f11bc715a6f11a3e000b9b807e1e'
for cache in (WT/'kc-dev-flow-2/scripts/__pycache__').glob('*.pyc'):
    cache.unlink()
sys.path.insert(0, str(WT/'kc-dev-flow-2/scripts'))
spec = importlib.util.spec_from_file_location('tests', WT/'kc-dev-flow-2/scripts/test_delivery_gate.py')
t = importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
g = t.gate

def run(args, cwd=WT, expected=0):
    env = {k:v for k,v in os.environ.items() if k not in ('GIT_DIR','GIT_INDEX_FILE','GIT_WORK_TREE')}
    env.update(GIT_AUTHOR_NAME='Fixture', GIT_AUTHOR_EMAIL='fixture@example.invalid', GIT_COMMITTER_NAME='Fixture', GIT_COMMITTER_EMAIL='fixture@example.invalid')
    p = subprocess.run([str(x) for x in args], cwd=cwd, env=env, capture_output=True, text=True, timeout=60)
    with (E/'commands.jsonl').open('a') as f: f.write(json.dumps(dict(argv=list(map(str,args)),cwd=str(cwd),exit=p.returncode,stdout=p.stdout,stderr=p.stderr))+'\n')
    if expected is not None: assert p.returncode == expected, (args,p.returncode,p.stdout,p.stderr)
    return p

def git(repo, *args): return run(['git','-C',repo,*args]).stdout.strip()
def commit(repo, *paths):
    git(repo,'add','--',*paths)
    git(repo,'-c','core.hooksPath=/dev/null','-c','commit.gpgsign=false','commit','-m','test: synthetic delivery reference','--',*paths)

def invoke(module, fixture):
    out=io.StringIO()
    with contextlib.redirect_stdout(out):
        code=module.main(['question',str(fixture.task),'--text-file',str(fixture.message),'--summary-file',str(fixture.summary)])
    return code,out.getvalue()

def module(source):
    m=types.ModuleType('variant');m.__file__=g.__file__;exec(compile(source,g.__file__,'exec'),m.__dict__);return m

base_source=git(WT,'show',BASE+':kc-dev-flow-2/scripts/delivery_gate.py')
baseline=module(base_source)
fixture=t.DeliveryCheckBeforeQuestionTests();fixture.setUp()
try:
    before,after=invoke(baseline,fixture),invoke(g,fixture)
    assert before[0]==0 and after[0]==1,(before,after)
    (E/'baseline-control.json').write_text(json.dumps(dict(base=before,candidate=after),indent=2))
finally: fixture.doCleanups()

mutations={
 'missing-hold': ('delivery_record = matching_delivery_record(task, gate_text)', 'delivery_record = matching_delivery_record(task, gate_text) or Path("missing-record.json")'),
 'oldest-record': ('path = max(records)[1]\n    try:\n        record = json.loads', 'path = min(records)[1]\n    try:\n        record = json.loads'),
 'skip-dispatch-head': ('not any(candidate.startswith(head) for candidate in candidates)', 'False'),
 'skip-question-head': ('not grants or not all(head.startswith(sha) for sha in grants)', 'False'),
 'skip-sufficiency': ('for label in CONFIRMATIONS):\n        return None', 'for label in ("Necessity",)):\n        return None'),
 'skip-necessity': ('for label in CONFIRMATIONS):\n        return None', 'for label in ("Sufficiency",)):\n        return None'),
 'omit-reference-line': ('if delivery_record is not None:', 'if False:'),
}
results=[]
for name,(old,new) in mutations.items():
    assert t.SOURCE.count(old)==1,(name,t.SOURCE.count(old))
    variant=module(t.SOURCE.replace(old,new))
    def run_question(self, variant=variant):
        code,out=invoke(variant,self)
        return subprocess.CompletedProcess([],code,out,'')
    cls=type('Mutation_'+name,(t.DeliveryCheckBeforeQuestionTests,),dict(run_question=run_question))
    stream=io.StringIO(); result=unittest.TextTestRunner(stream=stream,verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
    assert not result.wasSuccessful(),name
    (E/(name+'.log')).write_text(stream.getvalue())
    results.append(dict(name=name,status='passed',message=f'mutant rejected: {len(result.failures)} assertion failures, {len(result.errors)} errors'))
(E/'mutations.json').write_text(json.dumps(results,indent=2))

# A real split-root fixture; no production task or approval is modified.
if (E/'native-reference.json').exists():
    repo=E/'native';workflow=repo/'docs/dev2';state=workflow/'.spacedock-state'
    saved=json.loads((E/'native-reference.json').read_text());b=saved['briefing']
    record_path=state/'fixture/merge/ask-1.json';record=json.loads(record_path.read_text())
else:
    repo=E/'native'; workflow=repo/'docs/dev2'; state=workflow/'.spacedock-state'
    workflow.mkdir(parents=True)
    (workflow/'README.md').write_text((WT/'kc-dev-flow-2/references/sd/workflow.md').read_text())
    (repo/'.gitignore').write_text('**/.spacedock-state/\n')
    run(['git','init','--initial-branch=main',repo]);commit(repo,'.gitignore','docs/dev2/README.md')
    run(['git','-C',repo,'worktree','add','--detach',state]);git(state,'checkout','--orphan','spacedock-state/dev2')
    task=state/'fixture.md'
    task.write_text('---\ntitle: Synthetic delivery reference\nprofile: pilot\nstatus: validation\n---\n\n## Stage Report: validation\n\n- DONE: Synthetic reference fixture\n  No human approval or product delivery.\n\n### Summary\n\nSynthetic native reference test.\n')
    commit(state,'fixture.md')
    record_path=state/'fixture/merge/ask-1.json';record_path.parent.mkdir(parents=True)
    record=dict(time='2026-11-09T00:00:00Z',head=t.HEAD40,sufficiency=g.clause(t.CLAUSES,'Sufficiency'),necessity=g.clause(t.CLAUSES,'Necessity'))
    record_path.write_text(json.dumps(record,indent=2)+'\n')
    question=t.MERGE_ASK.format(tail=t.HOLD_OUT_TAIL['unless he says he merges or holds'])
    args=[SD,'gate','prepare','fixture','--workflow-dir',workflow,'--question',question,'--artifact',task,'--summary',t.CLAUSES,'--reference',record_path]
    uncommitted=run(args,cwd=repo,expected=None)
    assert uncommitted.returncode!=0,(uncommitted.stdout,uncommitted.stderr)
    run([SD,'state','commit','fixture','--workflow-dir',workflow],cwd=repo)
    commit_sha=git(state,'rev-parse','HEAD')
    assert git(state,'show',f'{commit_sha}:fixture/merge/ask-1.json')==record_path.read_text().strip()
    record_path.write_text(record_path.read_text()+' ')
    modified=run(args,cwd=repo,expected=None)
    assert modified.returncode!=0,(modified.stdout,modified.stderr)
    record_path.write_text(record_path.read_text()[:-1])
    prepared=run(args,cwd=repo)
    briefing_path=state/'fixture/review/validation/briefing-1/index.json'
    b=json.loads(briefing_path.read_text())
    ref=next(x for x in b['context'] if x['uri'].endswith('/merge/ask-1.json'))
    assert ref['rev']=='sha256:'+run(['shasum','-a','256',record_path]).stdout.split()[0],ref
    assert ref['uri']==f'git-root://state/{commit_sha}/fixture/merge/ask-1.json',ref
    (E/'native-reference.json').write_text(json.dumps(dict(version=run([SD,'--version']).stdout,uncommitted_exit=uncommitted.returncode,modified_exit=modified.returncode,reference=ref,briefing=b),ensure_ascii=False,indent=2))

def replay(briefing, read_record, rules, event_time=None, asks=(), fallback=True):
    sha=re.search(r'--match-head-commit\s+([0-9a-f]+)',briefing['question'])[1]
    refs=[x for x in briefing.get('context',[]) if re.search(r'/merge/ask-\d+\.json$',x.get('uri',''))]
    text=briefing['question']+'\n'+'\n'.join(x.get('summary','') for x in briefing.get('artifacts',[]))
    if refs:
        for ref in refs:
            raw=read_record(ref); rec=json.loads(raw)
            if ref['rev']!='sha256:'+hashlib.sha256(raw).hexdigest() or not rec['head'].startswith(sha): return 'violation'
            if any(rec[label.lower()]!=g.clean(g.clause(text,label) or '')[:200] for label in g.CONFIRMATIONS): return 'violation'
        return 'ok'
    if '`--reference <check record>`' in rules: return 'violation'
    if fallback and any(rec['head'].startswith(sha) and rec['time']<=event_time for rec in asks): return 'ok'
    return "can't tell"

def bound_bytes(ref):
    sha,path=ref['uri'].removeprefix('git-root://state/').split('/',1)
    return run(['git','-C',state,'show',sha+':'+path]).stdout.encode()
rules=(workflow/'README.md').read_text()
replays=[dict(name='bound reference',expected='ok',actual=replay(b,bound_bytes,rules))]
for name,changes in [('head',dict(head=t.S2)),('sufficiency',dict(sufficiency='changed')),('necessity',dict(necessity='changed'))]:
    altered={**record,**changes};raw=(json.dumps(altered)+'\n').encode();changed=copy.deepcopy(b)
    changed['context'][0]['rev']='sha256:'+hashlib.sha256(raw).hexdigest()
    replays.append(dict(name='mismatched '+name,expected='violation',actual=replay(changed,lambda _:raw,rules)))
replays.append(dict(name='digest mismatch',expected='violation',actual=replay(b,lambda _:b'{}',rules)))
missing=copy.deepcopy(b);missing['context']=[]
replays.append(dict(name='new rules without Reference',expected='violation',actual=replay(missing,bound_bytes,rules)))

slugs=['design-check-says-not-run-without-a-scope','adr-lint-tells-supersession-assertion-from-pointer','observer-lists-unasked-merges','worker-browser-checks-use-paseo-browser','dispatch-build-writes-the-dispatch-record','agent-reads-governing-adr']
for slug in slugs:
    path=STATE/'_archive'/slug/'review/validation/briefing-1/index.json'
    briefing=json.loads(path.read_text())
    original=f'{slug}/review/validation/briefing-1/index.json'
    sha=git(STATE,'log','--all','--diff-filter=A','--format=%H','--',original).splitlines()[-1]
    stamp=git(STATE,'show','-s','--format=%ct',sha)
    event_time=datetime.datetime.fromtimestamp(int(stamp),datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    revision=git(WT,'rev-list','-1','--before='+event_time,'origin/main')
    old_rules=git(WT,'show',revision+':docs/dev2/README.md')
    assert '`--reference <check record>`' not in old_rules
    asks=[json.loads(p.read_text()) for p in (STATE/'_archive'/slug/'merge').glob('ask-*.json')]
    expected='ok' if slug=='agent-reads-governing-adr' else "can't tell"
    actual=replay(briefing,None,old_rules,event_time,asks)
    replays.append(dict(name=slug,expected=expected,actual=actual,briefing_commit=sha,event_time=event_time,rules_commit=revision,records=asks))
    if expected=='ok':
        assert replay(briefing,None,old_rules,event_time,asks,fallback=False)=="can't tell"
for r in replays: assert r['actual']==r['expected'],r
(E/'observer-replay.json').write_text(json.dumps(replays,indent=2))

words=[]
for label,mod in [('base',baseline),('candidate',g)]:
    f=t.DeliveryCheckBeforeQuestionTests();f.setUp();f.save()
    try: code,out=invoke(mod,f)
    finally: f.doCleanups()
    assert code==0,out
    text=git(WT,'show',BASE+':kc-dev-flow-2/references/sd/workflow.md') if label=='base' else rules
    start=text.index('Before the validation `gate prepare`') if label=='base' else text.index('Before merging or asking, FO runs ')
    end=text.index('\n`merge guard --rework`',start)
    checked=t.run_variant(mod) if label=='base' else t.run_check()
    assert checked.code==0,checked.out
    words.append(dict(version=label,startup=len(text[start:end].split()),question=len(out.split()),check=len(checked.out.split()),question_output=out,check_output=checked.out))
assert [x['startup'] for x in words]==[80,80],words
assert [x['question'] for x in words]==[92,107],words
assert words[0]['check']==words[1]['check'],words
(E/'words.json').write_text(json.dumps(words,indent=2))
print('PASS: baseline missing-record control; seven rejected code mutations; native uncommitted/modified reference holds and committed digest; 12 observer replays and fallback mutation; lifecycle words 80/80, 92/107, check unchanged.')
