import importlib, io, json, os, pathlib, shutil, subprocess, sys, types, unittest
scripts=pathlib.Path(sys.argv[1]); base=pathlib.Path(sys.argv[2])
sys.path.insert(0,str(scripts))
import scratch, test_scratch, pr_watch, test_pr_watch, test_dispatch_stage
rows=[]
def probe(name, module, source, testmodule, target, original, replacement):
    if original not in source: raise RuntimeError("missing mutation target: "+name)
    mutant=types.ModuleType("mutant_"+module.__name__); mutant.__file__=module.__file__
    exec(compile(source.replace(original,replacement,1), module.__file__, "exec"),mutant.__dict__)
    old=getattr(testmodule,target); setattr(testmodule,target,mutant)
    output=io.StringIO()
    try:
        suite=unittest.defaultTestLoader.loadTestsFromName(name.split("|",1)[1],testmodule)
        result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
    finally: setattr(testmodule,target,old)
    (base/(name.split("|",1)[0]+".log")).write_text(output.getvalue())
    rows.append(dict(name=name.split("|",1)[0],status="passed" if not result.wasSuccessful() else "failed",message="mutation rejected" if not result.wasSuccessful() else "mutation survived"))
src=pathlib.Path(scratch.__file__).read_text()
probe("AC3-skip-worktree-remove|ScratchTests.test_dirty_registered_worktree_removed_and_external_worktree_survives",scratch,src,test_scratch,"scratch","git(folder, 'worktree', 'remove', '--force', str(path))","pass")
probe("threshold-disabled|ScratchTests.test_threshold_restore_and_idempotence",scratch,src,test_scratch,"scratch","len(data) > 256 * 1024","len(data) > 512 * 1024")
probe("size-cap-disabled|ScratchTests.test_evidence_size_limit_preserves_scratch_and_restorable_evidence",scratch,src,test_scratch,"scratch","size > 1024 * 1024","size > 1024 * 1024 * 100")
probe("root-mismatch-allowed|ScratchTests.test_mismatched_root_and_traversal_refuse",scratch,src,test_scratch,"scratch","if stated and (len(stated) != 1 or Path(stated[0]).resolve() != root):","if False:")
probe("symlink-follows-sentinel|ScratchTests.test_symlink_root_and_parent_leave_sentinel",scratch,src.replace("def safe_path(path):","def safe_path(path):\n    return",1),test_scratch,"scratch","root = root_for(folder, folder, name)","root = root_for(folder, folder, name).resolve()")
probe("truncated-gzip|ScratchTests.test_threshold_restore_and_idempotence",scratch,src,test_scratch,"scratch","gzip.compress(path.read_bytes(), mtime=0)","gzip.compress(path.read_bytes(), mtime=0)[:-8]")
probe("idle-sweep-disabled|TasksTests.test_scratch_sweep_prompts_old_and_archived_roots_and_leaves_current_and_unknown",pr_watch,pathlib.Path(pr_watch.__file__).read_text(),test_pr_watch,"watch","def scratch_lines(workflow, state, found, merged=()):","def scratch_lines(workflow, state, found, merged=()):\n    return []")
wrapper=base/'dispatch-mutant.py'
wrapper.write_text("import sys\nsys.path.insert(0,"+repr(str(scripts))+")\nimport dispatch_stage as s\ns.notes_for = lambda repo, folder, record, notes, package: notes\nsys.exit(s.main())\n")
old=test_dispatch_stage.WRAPPER; test_dispatch_stage.WRAPPER=wrapper
output=io.StringIO()
try:
    suite=unittest.defaultTestLoader.loadTestsFromName('DispatchStageTests.test_scratch_in_record_and_real_dispatch_artifact_without_changing_input',test_dispatch_stage)
    result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
finally: test_dispatch_stage.WRAPPER=old
(base/'AC1-paragraph-removed.log').write_text(output.getvalue())
rows.append(dict(name='AC1-paragraph-removed',status='passed' if not result.wasSuccessful() else 'failed',message='mutation rejected' if not result.wasSuccessful() else 'mutation survived'))
wrapper=base/'scope-mutant.py'
source=src.replace("raise ValueError(f'scope notes name a /tmp path outside {root}: {raw}')", "pass",1)
wrapper.write_text("import sys, types\nsys.path.insert(0,"+repr(str(scripts))+")\nimport dispatch_stage as s\nm=types.ModuleType('scratch_mutant'); m.__file__="+repr(str(scripts/'scratch.py'))+"\nexec("+repr(source)+",m.__dict__)\ns.notes_for=m.notes_for\nsys.exit(s.main())\n")
old=test_dispatch_stage.WRAPPER; test_dispatch_stage.WRAPPER=wrapper
output=io.StringIO()
try:
    suite=unittest.defaultTestLoader.loadTestsFromName('DispatchStageTests.test_scope_notes_outside_scratch_refuse_before_record_and_build',test_dispatch_stage)
    result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
finally: test_dispatch_stage.WRAPPER=old
(base/'outside-scope-notes-allowed.log').write_text(output.getvalue())
rows.append(dict(name='outside-scope-notes-allowed',status='passed' if not result.wasSuccessful() else 'failed',message='mutation rejected' if not result.wasSuccessful() else 'mutation survived'))
copy=base/'s4-scripts'; shutil.copytree(scripts,copy,ignore=shutil.ignore_patterns('__pycache__'))
p=copy/'delivery_gate.py'; text=p.read_text(); old='for path in absolute_paths(asked_paths):'
assert old in text; p.write_text(text.replace(old,'for path in absolute_paths(asked_paths + "\\n" + evidence):',1))
repro=pathlib.Path(sys.argv[3])
done=subprocess.run([sys.executable,'-B',str(repro),str(copy)],capture_output=True,text=True)
(base/'AC2-reports-scanned.log').write_text(done.stdout+done.stderr)
rows.append(dict(name='AC2-reports-scanned',status='passed' if done.returncode else 'failed',message='mutation rejected' if done.returncode else 'mutation survived'))
probe("AC4-own-worktree-left|ScratchTests.test_close_keeps_another_dispatch_in_the_same_repository",scratch,src,test_scratch,"scratch","git(folder, 'worktree', 'remove', '--force', str(path))","pass")
probe("AC4-peer-root-deleted|ScratchTests.test_close_keeps_another_dispatch_in_the_same_repository",scratch,src,test_scratch,"scratch","    if not any(root.parent.iterdir()):", "    for peer in root.parent.iterdir():\n        if peer != root and peer.is_dir():\n            shutil.rmtree(peer)\n    if not any(root.parent.iterdir()):")
wrapper=base/'privacy-mutant.py'
wrapper.write_text("import sys\nsys.path.insert(0,"+repr(str(scripts))+")\nimport dispatch_stage as s\noriginal=s.notes_for\ns.notes_for=lambda *a: original(*a).replace('private repository evidence, ', '')\nsys.exit(s.main())\n")
old=test_dispatch_stage.WRAPPER;test_dispatch_stage.WRAPPER=wrapper
output=io.StringIO()
try:
    suite=unittest.defaultTestLoader.loadTestsFromName('DispatchStageTests.test_scratch_in_record_and_real_dispatch_artifact_without_changing_input',test_dispatch_stage)
    result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
finally:test_dispatch_stage.WRAPPER=old
(base/'F1-private-repository-ban-removed.log').write_text(output.getvalue())
rows.append(dict(name='F1-private-repository-ban-removed',status='passed' if not result.wasSuccessful() else 'failed',message='mutation rejected' if not result.wasSuccessful() else 'mutation survived'))
(base/'mutations.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows))
sys.exit(any(r['status']!='passed' for r in rows))
