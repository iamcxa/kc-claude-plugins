"""Synthetic native-dispatch and isolated-close replay; no private repository input.
Usage: scope_and_privacy.py CODE_WORKTREE OUTPUT_DIRECTORY
Requires SPACEDOCK_BIN; CODE_WORKTREE must be outside /tmp (scope-note boundary).
"""
import gzip,hashlib,json,os,pathlib,subprocess,sys
repo=pathlib.Path(sys.argv[1]).resolve();out=pathlib.Path(sys.argv[2]).resolve()
out.mkdir(parents=True,exist_ok=True)
scripts=repo/'kc-dev-flow-2/scripts';sys.path.insert(0,str(scripts))
import scratch,test_dispatch_stage,test_scratch
case=test_dispatch_stage.DispatchStageTests('test_scratch_in_record_and_real_dispatch_artifact_without_changing_input')
case.setUp()
try:
 result=case.build()
 artifact=pathlib.Path(json.loads(result.stdout)['dispatch_file_path']).read_text()
 record=case.record().read_text()
 rule='Never archive private repository evidence, secrets or personal data'
 assert rule in record and rule in artifact
 assert 'Not archived (private): <what>; reproduce: <command>' in artifact
 (out/'emitted-record.md').write_text(record)
 (out/'emitted-dispatch.md').write_text(artifact)
 privacy={'synthetic_only':True,'record_and_native_artifact_keep_private_repository_ban':True,'reproduction_instruction_kept':True}
finally:case.doCleanups()
case=test_scratch.ScratchTests('test_close_keeps_another_dispatch_in_the_same_repository');case.setUp()
try:
 peer_root=scratch.claim_root(case.repo,case.folder,'validation-2')
 peer=peer_root/'peer';own=case.root/'own'
 case.git('worktree','add','--detach',own)
 case.git('worktree','add','--detach',peer)
 (own/'tracked').write_text('changed')
 (own/'untracked').write_text('discard own scratch')
 (peer/'uncommitted').write_text('preserve peer')
 public=b'public synthetic evidence\n'*14000
 (case.evidence/'public.txt').write_bytes(public)
 command=[sys.executable,'-B',str(scripts/'scratch.py'),'close',str(case.folder),'validation-1']
 closed=subprocess.run(command,capture_output=True,text=True,env=case.env)
 (out/'close-cli.log').write_text(closed.stdout+closed.stderr)
 assert closed.returncode==0,closed.stderr
 listed=[pathlib.Path(line[9:]) for line in case.git('worktree','list','--porcelain').splitlines() if line.startswith('worktree ')]
 facts={'own_root':str(case.root),'peer_root':str(peer_root),'own_root_absent':not case.root.exists(),'own_registered_worktrees':sum(p.is_relative_to(case.root) for p in listed),'repository_registered_under_dev2':sum(p.is_relative_to(scratch.BASE) for p in listed),'peer_still_registered':peer in listed,'peer_uncommitted_preserved':(peer/'uncommitted').read_text()=='preserve peer'}
 assert facts['own_root_absent'] and facts['own_registered_worktrees']==0
 assert facts['repository_registered_under_dev2']==1 and facts['peer_still_registered'] and facts['peer_uncommitted_preserved']
 case.git('add','task/evidence')
 case.git('commit','-qm','test: public retained evidence')
 blob=subprocess.run(['git','-C',str(case.repo),'show','HEAD:task/evidence/validation-1/public.txt.gz'],capture_output=True,check=True).stdout
 assert gzip.decompress(blob)==public
 assert hashlib.sha256(public).hexdigest()+'  public.txt' in (case.evidence/'SHA256SUMS').read_text()
 try:gzip.decompress(blob[:-8])
 except (EOFError,OSError):truncated_refused=True
 else:truncated_refused=False
 assert truncated_refused
 for filename,data in [('public.txt.gz',blob),('SHA256SUMS',(case.evidence/'SHA256SUMS').read_bytes()),('scratch-removed.txt',(case.folder/'scratch-removed.txt').read_bytes())]:
  (out/filename).write_bytes(data)
 facts.update(committed_gzip_restores_original=True,truncated_gzip_refused=True)
 case.git('worktree','remove','--force',peer)
finally:case.doCleanups()
summary={'privacy':privacy,'scope':facts}
(out/'replay.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
