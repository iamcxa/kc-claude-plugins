"""Independent merge falsifier: remove the internal observer README argument."""
import io,json,pathlib,sys,types,unittest
scripts=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);sys.path.insert(0,str(scripts))
import test_pr_watch
source=(scripts/'pr_watch.py').read_text()
old='str(state), slug,\n                                   "--readme", str(workflow / "README.md")],'
assert old in source
mutant=types.ModuleType('watch_missing_internal_readme');mutant.__file__=str(scripts/'pr_watch.py')
exec(compile(source.replace(old,'str(state), slug],',1),mutant.__file__,'exec'),mutant.__dict__)
original=test_pr_watch.watch;test_pr_watch.watch=mutant;log=io.StringIO()
try:
 result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('TasksTests.test_merged_scratch_prompt_precedes_merge_record',test_pr_watch))
finally:test_pr_watch.watch=original
(out/'internal-readme-falsifier.log').write_text(log.getvalue())
row={'name':'merged-internal-readme-lost','status':'passed' if not result.wasSuccessful() else 'failed','message':'mutation rejected' if not result.wasSuccessful() else 'mutation survived'}
(out/'internal-readme-falsifier.json').write_text(json.dumps(row,indent=2))
print(json.dumps(row));sys.exit(0 if row['status']=='passed' else 1)
