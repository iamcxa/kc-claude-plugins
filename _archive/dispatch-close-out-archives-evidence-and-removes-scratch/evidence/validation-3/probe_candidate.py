"""Public synthetic native-dispatch and close/retry probe. Usage: probe_candidate.py CODE OUTPUT."""
import gzip,hashlib,json,pathlib,subprocess,sys
code=pathlib.Path(sys.argv[1]).resolve();out=pathlib.Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=True)
scripts=code/'kc-dev-flow-2/scripts';sys.path.insert(0,str(scripts))
import scratch,test_dispatch_stage,test_scratch
owned=[]
d=test_dispatch_stage.DispatchStageTests('test_next_validation_accepts_its_own_scratch_path_and_retries');d.setUp()
try:
 d.set_stage('validation');flags=('--candidate','a'*40,'--symptom','none');d.build('validation',flags)
 before=d.record('validation').read_bytes();root=scratch.root_for(d.repo,d.folder,'validation-2')
 d.notes.write_text(d.notes.read_text()+f'Use {root}/checkout\n');result=d.build('validation',flags)
 record=d.record('validation',2).read_text();artifact=pathlib.Path(json.loads(result.stdout)['dispatch_file_path']).read_text()
 expected='Scratch: '+str(root).replace('/private/tmp/','/tmp/',1)
 assert record.splitlines().count(expected)==artifact.splitlines().count(expected)==1
 assert 'Never archive private repository evidence, secrets or personal data' in artifact
 assert d.record('validation').read_bytes()==before
 d.build('validation',flags);assert not d.record('validation',3).exists()
 (out/'validation-2-record.md').write_text(record);(out/'native-dispatch.md').write_text(artifact)
 dispatch={'second_validation_built_with_own_path':True,'identical_retry_reuses_second_record':True,'first_record_unchanged':True,'private_repository_rule_kept':True}
 owned += [str(scratch.BASE/d.scratch_namespace/d.slug),str(d.base)]
 owned += [str(p.resolve()) for p in pathlib.Path('/tmp/spacedock-dispatch').glob('*'+d.slug+'*') if p.is_file()]
finally:d.doCleanups()
c=test_scratch.ScratchTests('test_compression_collision_refuses_before_changes_and_retry_keeps_digests');c.setUp()
try:
 peer_root=scratch.claim_root(c.repo,c.folder,'validation-2');peer=peer_root/'peer';own=c.root/'own'
 c.git('worktree','add','--detach',peer);c.git('worktree','add','--detach',own)
 (own/'untracked').write_text('discard own fixture');(peer/'uncommitted').write_text('keep peer')
 originals={'a.txt':b'a'*(256*1024+1),'z.txt':b'z'*(256*1024+1)}
 for n,b in originals.items():(c.evidence/n).write_bytes(b)
 collision=c.evidence/'z.txt.gz';collision.write_bytes(b'occupied')
 before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in c.evidence.iterdir()}
 command=[sys.executable,'-B',str(scripts/'scratch.py'),'close',str(c.folder),'validation-1']
 refused=subprocess.run(command,env=c.env,capture_output=True,text=True)
 assert refused.returncode==1 and 'would overwrite' in refused.stderr
 assert {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in c.evidence.iterdir()}==before
 (out/'collision-refusal.log').write_text(refused.stdout+refused.stderr)
 collision.unlink();closed=subprocess.run(command,env=c.env,capture_output=True,text=True);assert closed.returncode==0,closed.stderr
 (out/'close-cli.log').write_text(closed.stdout+closed.stderr)
 listed=[pathlib.Path(line[9:]) for line in c.git('worktree','list','--porcelain').splitlines() if line.startswith('worktree ')]
 assert not c.root.exists() and sum(p.is_relative_to(c.root) for p in listed)==0
 assert sum(p.is_relative_to(peer_root) for p in listed)==1 and (peer/'uncommitted').read_text()=='keep peer'
 c.git('add','task/evidence');c.git('commit','-qm','test: public evidence')
 sums=(c.evidence/'SHA256SUMS').read_text()
 for n,b in originals.items():
  blob=subprocess.check_output(['git','-C',str(c.repo),'show','HEAD:task/evidence/validation-1/'+n+'.gz'])
  assert gzip.decompress(blob)==b
  assert hashlib.sha256(b).hexdigest()+'  '+n+'\n' in sums
  (out/(n+'.gz')).write_bytes(blob)
 (out/'fixture-SHA256SUMS.txt').write_text(sums)
 compression={'collision_refusal_changed_no_files':True,'retry_original_digests_correct':True,'committed_gzip_restores_originals':True,'own_root_absent':True,'own_registered_worktrees':0,'peer_registered_worktrees':1,'peer_uncommitted_preserved':True}
 owned += [str(c.root.parent.parent),str(c.repo)]
 c.git('worktree','remove','--force',peer)
finally:c.doCleanups()
assert all(not pathlib.Path(p).exists() for p in owned)
facts={'dispatch':dispatch,'compression':compression,'removed_fixture_paths':owned,'synthetic_only':True}
(out/'probe.json').write_text(json.dumps(facts,indent=1));print(json.dumps(facts,indent=1))
