from pathlib import Path
import importlib.util,sys,unittest,tempfile
WT=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-562b1a87')
S=WT/'kc-dev-flow-2/scripts';sys.path.insert(0,str(S))
import test_poc_readme as test
source=(S/'poc_readme.py').read_text()
old='        if line == STATE:\n            i += 1'
new='        if line == STATE:\n            out.append(lines[i + 1])\n            i += 1'
assert old in source
with tempfile.TemporaryDirectory(prefix='poc-retained-model-') as d:
 p=Path(d)/'poc_readme.py';p.write_text(source.replace(old,new,1))
 assert not list(Path(d).rglob('__pycache__'))
 spec=importlib.util.spec_from_file_location('mutant_poc',p);mutant=importlib.util.module_from_spec(spec);spec.loader.exec_module(mutant)
 derived=mutant.derive(test.SOURCE)
 assert '    - name: ideation' not in derived and derived.split('---',2)[1].count('model: opus')==2
 test.poc=mutant
 suite=unittest.defaultTestLoader.loadTestsFromName('DeriveTests.test_only_the_ideation_entry_and_section_are_removed',test)
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 assert len(result.failures)==1 and not result.errors
 print('Expected failure: mutant retains the removed ideation model; real derivation test rejected it.')
