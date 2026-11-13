"""Rerun existing public evidence against an exported candidate."""
import json, os, pathlib, subprocess, sys, shutil
t=pathlib.Path(sys.argv[1]).resolve(); e=pathlib.Path(__file__).resolve().parent
r=e/'reused'; scripts=t/'candidate/kc-dev-flow-2/scripts'; old=t/'previous/kc-dev-flow-2/scripts'
env={**os.environ,'SPACEDOCK_BIN':'/Users/kent/.local/bin/spacedock','TMPDIR':str(t/'tmp'),'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(e/'trace'),'SCRATCH_DIRECTORY_LOG':str(e/'created-directories.jsonl')}
rows=[]
def run(name,args,expected=0,cwd=None):
    with (e/(name+'.log')).open('w') as f:
        done=subprocess.run(list(map(str,args)),cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT)
    rows.append(dict(name=name,command=list(map(str,args)),cwd=str(cwd) if cwd else None,exit=done.returncode,expected=expected))
    (e/'commands.json').write_text(json.dumps(rows,indent=2))
    print(name+': '+str(done.returncode),flush=True)
    return done.returncode
py=[sys.executable,'-B']; adapter=[*py,r/'fixture_adapter.py',scripts]
run('dispatch-native', [*py,r/'run_tests.py',scripts,'test_dispatch_stage',e/'dispatch-native.json'],expected=1)
run('dispatch-adapted', [*adapter,r/'run_tests.py',scripts,'test_dispatch_stage',e/'dispatch-adapted.json'])
run('watch', [*py,r/'run_tests.py',scripts,'test_pr_watch',e/'watch.json'])
run('scratch', [*py,r/'run_tests.py',scripts,'test_scratch',e/'scratch.json'])
run('dispatch-records', [*py,r/'run_tests.py',scripts,'test_dispatch_records',e/'dispatch-records.json'])
run('privacy-previous', [*py,r/'privacy_probe.py',t/'previous','/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1',e/'privacy-previous'],expected=1)
run('privacy-candidate', [*py,r/'privacy_probe.py',t/'candidate','/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1',e/'privacy-candidate'])
run('scope-privacy-cli',[*adapter,r/'scope_and_privacy.py',t/'candidate',e/'replay'])
for name,runner in [('mutations','mutate.py'),('repair-mutations','repair_mutations.py')]:
    out=t/name;out.mkdir()
    args=[*adapter,r/runner,scripts,out]
    if name=='mutations':args.append(r/'s4_repro.py')
    run(name,args)
    target=e/name;target.mkdir()
    for p in out.iterdir():
        if p.is_file() and p.suffix in ('.log','.json'):shutil.copyfile(p,target/p.name)
out=t/'collision';run('collision',[*py,r/'collision_replay.py',scripts,out])
(e/'collision').mkdir()
for name in ('results.json','commands.log'):shutil.copyfile(out/name,e/'collision'/name)
run('ac2',[*py,r/'s4_repro.py',scripts])
run('ac4',[*py,'-m','unittest','test_scratch.ScratchTests.test_close_keeps_another_dispatch_in_the_same_repository'],cwd=scripts)
run('ac1-grep',['grep','-c','^Scratch: /tmp/dev2/',e/'replay/emitted-record.md'])
print('All evidence commands completed',flush=True)
