import base64
import importlib.util
import io
import contextlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

WT = Path(sys.argv[1]).resolve()
OUT = Path(__file__).resolve().parent
BASE = 'e8664a72b0f904e5dda3c391d52ab3abaca876b4'
source = (WT / 'kc-dev-flow-2/scripts/package_version.py').read_text()
tests = (WT / 'kc-dev-flow-2/scripts/test_package_version.py').read_text()

def package(root, text):
    target = root / 'kc-dev-flow-2'
    (target / 'scripts').mkdir(parents=True)
    (target / '.claude-plugin').mkdir()
    (target / 'references/sd').mkdir(parents=True)
    (target / 'scripts/package_version.py').write_text(text)
    (target / 'scripts/test_package_version.py').write_text(tests)
    for path in ('.claude-plugin/plugin.json', 'references/sd/workflow.md'):
        shutil.copyfile(WT / 'kc-dev-flow-2' / path, target / path)
    return target

results=[]
mutations = [
    ('AC-1 drop a listed row', 'for repo, directory, *state in rows:', 'for repo, directory, *state in rows[:-1]:', 'test_each_row_keeps_its_own_release_sync_and_laws_status'),
    ('AC-2 failed README read becomes nothing owed', 'print(f"{repo} {directory} unreadable: {diagnostic(error)}")\n            failed = True', 'print(f"{repo} {directory} no sync owed")\n            continue', 'test_unreadable_readme_quotes_error_and_fails_without_hiding_other_rows'),
    ('AC-3 compare release markers too', 'return "".join(line for line in text.splitlines(keepends=True) if not MARK.search(line))', 'return text', 'test_release_line_only_does_not_owe_sync_but_a_changed_sentence_does'),
    ('AC-4 pin equality replaces laws-content comparison', 'owed = any(gh.content(UPSTREAM, path, sha) != gh.content(UPSTREAM, path, released) for path in LAWS)', 'owed = sha != released', 'test_each_laws_file_change_owes_pin_and_identical_laws_do_not'),
    ('AC-6 silence failed search', 'print(f"search: unavailable {diagnostic(error)}")', 'pass', 'test_search_reports_unlisted_and_failed_search_without_changing_exit'),
    ('AC-11 missing list becomes nothing owed', 'print(f"rollout: unreadable {diagnostic(error)}")\n        return 1', 'print("no sync owed")\n        return 0', 'test_missing_or_unreadable_local_list_fails'),
]
for index,(name, before, after, method) in enumerate(mutations):
    assert before in source, name
    with tempfile.TemporaryDirectory() as d:
        p=package(Path(d), source.replace(before, after, 1))
        run=subprocess.run([sys.executable, '-B', '-m', 'unittest', 'test_package_version.RolloutTest.'+method], cwd=p/'scripts', capture_output=True,text=True)
        (OUT/f'mutation-{index+1}.log').write_text(run.stdout+run.stderr)
        assert run.returncode == 1, (name, run.returncode,run.stdout,run.stderr)
        results.append({'name':name,'status':'passed','message':f'mutation rejected, exit {run.returncode}; mutation-{index+1}.log'})

base=subprocess.check_output(['git','-C',str(WT),'show',BASE+':kc-dev-flow-2/scripts/package_version.py'],text=True)
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m);return m
with tempfile.TemporaryDirectory() as d:
    root=Path(d)
    oldpkg=package(root/'base',base)
    newpkg=package(root/'candidate',source)
    old=module(oldpkg/'scripts/package_version.py','oldpv')
    new=module(newpkg/'scripts/package_version.py','newpv')
    cases=[('older','0.18.1',(0,17,0)),('numeric-newer','0.9.0',(0,10,0)),('numeric-older','0.10.0',(0,9,0)),('match','0.18.1',(0,18,1)),('behind','0.18.0',(0,18,1)),('missing-marker',None,(0,18,1)),('usage',None,None),('missing-file',None,None)]
    for name,version,loaded in cases:
        readme=root/'README.md'
        readme.write_text(f'# Development workflow\n<!-- kc-dev-flow-2 {version} x-release-please-version -->\n' if version else '# Development workflow\n')
        pair=[]
        for label,m in [('base',old),('candidate',new)]:
            m.loaded=lambda:loaded
            args=[] if name=='usage' else ['/no/such/README.md'] if name=='missing-file' else [str(readme)]
            out=io.StringIO()
            with contextlib.redirect_stdout(out):
                code=m.main(args)
            target=OUT/f'legacy-{name}-{label}.txt';target.write_bytes(out.getvalue().encode())
            pair.append((code,target))
        assert pair[0][0]==pair[1][0]
        subprocess.run(['cmp',str(pair[0][1]),str(pair[1][1])],check=True)
    mutantpkg=package(root/'mutant',source.replace('matches the README")','matches the README!")'))
    mutant=module(mutantpkg/'scripts/package_version.py','mutantpv')
    mutant.loaded=lambda:(0,18,1)
    readme.write_text('<!-- kc-dev-flow-2 0.18.1 x-release-please-version -->\n')
    out=io.StringIO()
    with contextlib.redirect_stdout(out):mutant.main([str(readme)])
    (OUT/'legacy-match-mutant.txt').write_text(out.getvalue())
    run=subprocess.run(['cmp',str(OUT/'legacy-match-base.txt'),str(OUT/'legacy-match-mutant.txt')],capture_output=True,text=True)
    assert run.returncode==1
    (OUT/'mutation-legacy.log').write_text(run.stdout+run.stderr)
    results.append({'name':'AC-5 original mode stdout bytes','status':'passed','message':'8 base/candidate cases cmp equal; changed matching output rejected by cmp exit 1'})

with tempfile.TemporaryDirectory() as d:
    root=Path(d)
    shutil.copytree(WT/'kc-dev-flow-2',root/'kc-dev-flow-2',ignore=shutil.ignore_patterns('__pycache__'))
    (root/'scripts').mkdir()
    shutil.copyfile(WT/'scripts/skill-frontmatter-lint.sh',root/'scripts/skill-frontmatter-lint.sh')
    workflow=(root/'kc-dev-flow-2/references/sd/workflow.md').read_text()
    paragraph=' '.join(workflow.splitlines()[100:103])
    target=root/'kc-dev-flow-2/skills/maintain-flow/SKILL.md'
    target.write_text(target.read_text()+'\n'+paragraph+'\n')
    run=subprocess.run([sys.executable,'-B','kc-dev-flow-2/scripts/lint-skills.py'],cwd=root,capture_output=True,text=True)
    (OUT/'mutation-lint.log').write_text(run.stdout+run.stderr)
    assert run.returncode==1 and 'repeats' in run.stdout,run.stdout+run.stderr
    results.append({'name':'AC-10 repeated workflow passage','status':'passed','message':'12-word repeat mutation rejected by repository linter exit 1'})
(OUT/'proof-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
