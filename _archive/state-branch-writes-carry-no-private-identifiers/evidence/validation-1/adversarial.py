"""Independent boundary probes; CODE OUT_DIR. Uses invented identifiers and local remotes."""
from pathlib import Path
import contextlib,gzip,json,os,subprocess,sys,tempfile,traceback
code,out=map(Path,sys.argv[1:3]);out.mkdir(parents=True,exist_ok=True)
tempfile.tempdir=str(out)
sys.path.insert(0,str(code/'kc-dev-flow-2/scripts'))
import state_guard
from test_state_guard import StateGuardTests
rows=[];commands=[]
class Fixture(StateGuardTests):
    def run_command(self,args,expected=0,data=None,env=None):
        result=super().run_command(args,expected=None,data=data,env=env)
        def safe(v):
            return str(v).replace(str(code),'$CODE').replace(str(self.base),'$CASE').replace(str(Path.home()),'~').replace('fixture'+chr(64)+'example.invalid','[synthetic-email]')
        commands.append(dict(case=current,argv=[safe(v) for v in args],exit=result.returncode,stdout=safe(result.stdout),stderr=safe(result.stderr)))
        (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
        if expected is not None: self.assertEqual(result.returncode,expected,result.stdout+result.stderr)
        return result

def attempt(kind):
    f=Fixture();f.setUp()
    try:
        token=f.slug;name='payload.txt'
        if kind=='no-hunk-old-binary':
            (f.state/name).write_bytes(b'old\x00binary\n');f.commit(name)
        if kind=='no-hunk-size':
            (f.state/name).write_text('old '+'.'*1024+'\n');f.commit(name)
            f.git(f.repo,'config','core.bigFileThreshold','64')
        if kind=='no-hunk-global-attributes':
            (f.state/name).write_text('old\n');f.commit(name)
            attr=f.base/'attributes';attr.write_text('* -diff\n')
            f.git(f.repo,'config','core.attributesFile',str(attr))
        if kind in ('same-blob-rename','case-folded-folder'):
            (f.state/'old.txt').write_text('public\n');f.commit('old.txt')
        f.install('--refuse',','.join(state_guard.CLASSES))
        old=f.git(f.remote,'rev-parse','spacedock-state/test').stdout.strip()
        if kind=='folder': name=f.slug+'/record.md'
        elif kind=='basename': name=f.slug+'.md'
        elif kind=='newline-name': name='prefix\n'+f.slug+'.md'
        elif kind=='case-folded-folder': name=f.slug.upper()+'/record.md'
        elif kind=='same-blob-rename': name=f.slug+'/renamed.md'
        elif kind=='nested-gzip': name='payload.gz'
        elif kind=='symlink-target': name='evidence-link'
        elif kind=='binary': name='payload.bin'
        target=f.state/name;target.parent.mkdir(parents=True,exist_ok=True)
        if kind in ('same-blob-rename','case-folded-folder'):
            f.git(f.state,'mv','old.txt',name)
        elif kind=='symlink-target': target.symlink_to('../'+token+'/absent')
        elif kind=='nested-gzip': target.write_bytes(gzip.compress(gzip.compress(token.encode(),mtime=0),mtime=0))
        elif kind=='binary': target.write_bytes(b'\x00\xff'+token.encode()+b'\x00')
        elif kind in ('folder','basename','newline-name'): target.write_text('public\n')
        elif kind=='no-hunk-size': target.write_text(token+' '+'.'*1024+'\n')
        else: target.write_text(token+'\n')
        refused=f.commit(name,expected=1)
        f.assert_private_output_absent(refused.stdout+refused.stderr)
        assert 'private-slug identifier' in refused.stderr
        f.install('--warn',','.join(state_guard.CLASSES));f.commit(name)
        if kind=='transient-deletion':
            target.write_text('public\n');f.commit(name)
        f.install('--refuse',','.join(state_guard.CLASSES))
        push=f.git(f.state,'push','origin','spacedock-state/test',expected=1)
        f.assert_private_output_absent(push.stdout+push.stderr)
        assert 'private-slug identifier' in push.stderr
        assert f.git(f.remote,'rev-parse','spacedock-state/test').stdout.strip()==old
        rows.append(dict(name=kind,status='passed',commit_exit=refused.returncode,push_exit=push.returncode,remote_unchanged=True,matched_text_absent=True))
    finally: f.doCleanups()

def merge_attempt():
    f=Fixture();f.setUp()
    try:
        f.install('--refuse',','.join(state_guard.CLASSES))
        before=f.git(f.remote,'rev-parse','spacedock-state/test').stdout.strip()
        f.git(f.state,'checkout','-b','synthetic-side')
        (f.state/'merge.txt').write_text(f.slug+'\n');f.commit('merge.txt')
        f.git(f.state,'checkout','spacedock-state/test')
        merge=f.git(f.state,'merge','--no-ff','synthetic-side','-m','test: merge')
        push=f.git(f.state,'push','origin','spacedock-state/test',expected=1)
        f.assert_private_output_absent(push.stdout+push.stderr)
        assert f.git(f.remote,'rev-parse','spacedock-state/test').stdout.strip()==before
        rows.append(dict(name='merge-commit',status='passed',merge_exit=merge.returncode,push_exit=push.returncode,remote_unchanged=True,matched_text_absent=True,limit='Git merge creates a local commit without pre-commit; pre-push refuses both incoming and merge commits.'))
    finally: f.doCleanups()

for current in ['folder','basename','newline-name','case-folded-folder','same-blob-rename','no-hunk-old-binary','no-hunk-size','no-hunk-global-attributes','binary','nested-gzip','symlink-target','transient-deletion','merge-commit']:
    try:
        merge_attempt() if current=='merge-commit' else attempt(current)
    except Exception as e:
        rows.append(dict(name=current,status='failed',message=type(e).__name__))
        print(current+': '+type(e).__name__,flush=True)
    (out/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2));sys.exit(any(row['status']=='failed' for row in rows))
