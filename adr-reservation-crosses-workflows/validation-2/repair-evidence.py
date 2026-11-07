import ast, hashlib, io, json, subprocess, types, unittest
from pathlib import Path
out=Path('/tmp/adr-reservation-validation-801-r2')
root=out/'candidate'
repo=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-adr-reservation-crosses-workflows')
state=repo.parents[1]/'docs/dev2/.spacedock-state'
parent='6a0a4aec60bb5900a0d363bae912acc5714f5974'
head='ef3ed3e05534e2a997acbdfb055a880fde1f484a'
git=lambda *args: subprocess.check_output(['git','-C',str(repo),*args],text=True)
changed=git('diff','--name-only',parent,head).splitlines()
assert changed==['kc-dev-flow-2/scripts/number_guards.py','kc-dev-flow-2/scripts/test_number_guards.py']
script=(root/changed[0]).read_text()
assert script.count('"--prune", ')==1
assert script.replace('"--prune", ','')==git('show',parent+':'+changed[0])
tree=ast.parse((root/changed[1]).read_text())
klass=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='CrossWorkflowTests')
newtest=next(n for n in klass.body if isinstance(n,ast.FunctionDef) and n.name=='test_deleted_origin_state_branch_releases_its_adr_number')
klass.body.remove(newtest)
assert ast.dump(tree)==ast.dump(ast.parse(git('show',parent+':'+changed[1])))
prior=json.loads((state/'adr-reservation-crosses-workflows/validation/doc-impact-disposition.json').read_text())
for row in prior:
    data=(root/row['doc']).read_bytes()
    assert hashlib.sha256(data).hexdigest()==row['reviewed_unchanged_bytes']
    assert data==subprocess.check_output(['git','-C',str(repo),'show',parent+':'+row['doc']])
(out/'doc-impact-disposition.json').write_text(json.dumps(prior,indent=2))
scope={'head':head,'parent':parent,'repair_files':changed,'single_fetch_argument_only':True,'single_test_only':True,
'unchanged_prior_evidence':['ADR quote and bound question','two workflow passages and word budget','parser APIs','sixth-file exact warning assertion','eight doc-impact dispositions','CI configuration'],
'carried_document_hashes':len(prior)}
(out/'scope.json').write_text(json.dumps(scope,indent=2))
testrel='kc-dev-flow-2/scripts/test_dispatch_records.py'
code=(out/'base'/testrel).read_text()
module=types.ModuleType('ac10_mutant')
module.__file__=str(root/testrel)
exec(compile(code,module.__file__,'exec'),module.__dict__)
suite=unittest.defaultTestLoader.loadTestsFromName('DesignAdrTests.test_raw_740_bytes_refuse_then_allocator_recovery_and_missing_line_controls',module)
stream=io.StringIO()
result=unittest.TextTestRunner(stream=stream).run(suite)
(out/'ac10-falsifier.log').write_text(stream.getvalue())
assert len(result.failures)==1 and not result.errors,stream.getvalue()
assert 'state checkout has no origin' in stream.getvalue()
print('Repair scope: one fetch argument and one test; eight unchanged documents independently hash-verified.')
print('AC10 restored empty-stderr assertion: one expected failure, zero runtime errors.')
