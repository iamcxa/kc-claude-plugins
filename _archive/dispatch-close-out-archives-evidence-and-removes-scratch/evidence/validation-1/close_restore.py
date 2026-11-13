"""Run the actual close CLI only against a repository and root this script creates."""
import gzip,hashlib,json,os,pathlib,subprocess,sys,uuid
repo=pathlib.Path(sys.argv[2]).resolve()/'close-fixture';repo.mkdir()
scripts=pathlib.Path(sys.argv[1]).resolve()/'kc-dev-flow-2/scripts';sys.path.insert(0,str(scripts));import scratch
out=pathlib.Path(sys.argv[2]).resolve()
env={**os.environ,'GIT_AUTHOR_NAME':'Fixture','GIT_COMMITTER_NAME':'Fixture','GIT_AUTHOR_EMAIL':'fixture@example.invalid','GIT_COMMITTER_EMAIL':'fixture@example.invalid','GIT_CONFIG_COUNT':'2','GIT_CONFIG_KEY_0':'core.hooksPath','GIT_CONFIG_VALUE_0':'/dev/null','GIT_CONFIG_KEY_1':'commit.gpgsign','GIT_CONFIG_VALUE_1':'false'}
def git(*args):return subprocess.check_output(['git','-C',str(repo),*map(str,args)],env=env)
git('init','-q','-b','main');git('remote','add','origin','https://example.invalid/fixture/close-'+uuid.uuid4().hex+'.git')
(repo/'tracked').write_text('original');git('add','tracked');git('commit','-qm','test: seed')
folder=repo/'task';(folder/'dispatch').mkdir(parents=True)
root=scratch.claim_root(repo,folder,'validation-1')
record=folder/'dispatch/validation-1.md';record.write_text('Scratch: '+str(root)+'\n')
evidence=folder/'evidence/validation-1';evidence.mkdir(parents=True)
data=b'Public synthetic restoration evidence\n'*10000
(evidence/'public.txt').write_bytes(data)
checkout=root/'checkout';git('worktree','add','--detach',checkout)
(checkout/'tracked').write_text('changed');(checkout/'untracked').write_text('owned disposable work')
result=subprocess.run([sys.executable,'-B',str(scripts/'scratch.py'),'close',str(folder),'validation-1'],capture_output=True,text=True)
(out/'close-cli.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
assert not root.exists();assert str(root).encode() not in git('worktree','list','--porcelain')
assert 'uncommitted-files=2' in (folder/'scratch-removed.txt').read_text()
git('add','task');git('commit','-qm','test: evidence')
compressed=git('show','HEAD:task/evidence/validation-1/public.txt.gz')
assert gzip.decompress(compressed)==data
manifest=(evidence/'SHA256SUMS').read_text();assert hashlib.sha256(data).hexdigest()+'  public.txt' in manifest
try:gzip.decompress(compressed[:-8]);raise AssertionError('truncated archive unexpectedly restored')
except (EOFError,OSError):pass
(out/'public.txt.gz').write_bytes(compressed);(out/'SHA256SUMS').write_text(manifest)
namespace=root.parent.parent
if namespace.exists() and not any(namespace.iterdir()):namespace.rmdir()
(out/'close-restore.json').write_text(json.dumps(dict(root=str(root),namespace=str(namespace),root_absent=not root.exists(),namespace_absent=not namespace.exists(),worktrees_under_root=0,uncommitted_files_removed=2,restored_sha256=hashlib.sha256(data).hexdigest(),truncated_archive_rejected=True),indent=2))
print('close CLI: exit 0; owned root absent; registered worktrees 0; restored digest matches; truncated archive rejected')
