"""Two synthetic dispatches in one owned repo expose the whole-repo AC-3 wording."""
import contextlib,io,json,pathlib,sys
scripts=pathlib.Path(sys.argv[1])/'kc-dev-flow-2/scripts';sys.path.insert(0,str(scripts))
import scratch,test_scratch
out=pathlib.Path(sys.argv[2]);case=test_scratch.ScratchTests('test_missing_record_refuses_without_deletion');case.setUp()
log=io.StringIO();paths=[]
try:
 first=case.root;second=scratch.claim_root(case.repo,case.folder,'implementation-1')
 (case.folder/'dispatch/implementation-1.md').write_text('Scratch: '+str(second)+'\n')
 for root in [first,second]:
  wt=root/'checkout';case.git('worktree','add','--detach',wt);(wt/'uncommitted').write_text('owned fixture');paths.append(str(root))
 with contextlib.redirect_stdout(log):scratch.close(case.folder,'validation-1')
 listed=case.git('worktree','list','--porcelain');count=sum(x.startswith('worktree /private/tmp/dev2/') or x.startswith('worktree /tmp/dev2/') for x in listed.splitlines())
 assert not first.exists() and second.exists() and count==1
 (out/'ac3-scope.json').write_text(json.dumps(dict(closed_dispatch_root_absent=True,other_dispatch_root_survives=True,whole_repo_registered_dev2_worktrees=count,literal_AC3_pass=False,scoped_deletion_pass=True,owned_roots=paths),indent=2))
 with contextlib.redirect_stdout(log):scratch.close(case.folder,'implementation-1')
 assert not second.exists()
 (out/'ac3-scope.log').write_text(log.getvalue())
 print('Own dispatch removed; second active dispatch preserved; literal AC-3 global count =',count)
finally:case.doCleanups()
