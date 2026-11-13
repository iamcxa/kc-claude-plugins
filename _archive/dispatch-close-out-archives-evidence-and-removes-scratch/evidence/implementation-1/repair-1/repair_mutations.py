import io,json,pathlib,sys,types,unittest
scripts=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);sys.path.insert(0,str(scripts))
import scratch,test_scratch,test_dispatch_stage
src=pathlib.Path(scratch.__file__).read_text();rows=[]
def probe(name,original,replacement,test):
    assert original in src,name
    m=types.ModuleType('mutant_scratch');m.__file__=scratch.__file__
    exec(compile(src.replace(original,replacement,1),m.__file__,'exec'),m.__dict__)
    old=test_scratch.scratch;test_scratch.scratch=m;log=io.StringIO()
    try:result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName(test,test_scratch))
    finally:test_scratch.scratch=old
    (out/(name+'.log')).write_text(log.getvalue());rows.append(dict(name=name,status='passed' if not result.wasSuccessful() else 'failed',message='mutation rejected' if not result.wasSuccessful() else 'mutation survived'))
probe('namespace-basename-only',"return name + '-' + digest[:16]","return name",'ScratchTests.test_same_basename_repositories_and_clones_keep_foreign_dirty_worktrees')
probe('close-ownership-bypassed',"root = root_for(folder, folder, name)\n    safe_path(root)\n    if root.exists():\n        check_owner(root, owner_for(folder, folder, name))","root = root_for(folder, folder, name)\n    safe_path(root)",'ScratchTests.test_foreign_or_unowned_root_refuses_notes_reuse_and_close')
wrapper=out/'build-mutant.py'
wrapper.write_text('import sys\nsys.path.insert(0,'+repr(str(scripts))+')\nimport scratch,dispatch_stage\nscratch.check_owner=lambda *args: None\nsys.exit(dispatch_stage.main())\n')
old=test_dispatch_stage.WRAPPER;test_dispatch_stage.WRAPPER=wrapper;log=io.StringIO()
try:result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('DispatchStageTests.test_foreign_root_owner_refuses_before_build_or_notes_write',test_dispatch_stage))
finally:test_dispatch_stage.WRAPPER=old
(out/'build-ownership-bypassed.log').write_text(log.getvalue());rows.append(dict(name='build-ownership-bypassed',status='passed' if not result.wasSuccessful() else 'failed',message='mutation rejected' if not result.wasSuccessful() else 'mutation survived'))
(out/'repair-mutations.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows));sys.exit(any(r['status']!='passed' for r in rows))
