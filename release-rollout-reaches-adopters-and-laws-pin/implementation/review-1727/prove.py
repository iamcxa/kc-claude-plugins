from pathlib import Path
import ast
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile

WT=Path(sys.argv[1]).resolve()
OUT=Path(__file__).resolve().parent
PRIOR='ba98f3ca95c1f879bf460fbb08976f337e18c4c8'
source=(WT/'kc-dev-flow-2/scripts/package_version.py').read_text()
tests=(WT/'kc-dev-flow-2/scripts/test_package_version.py').read_text()
old=subprocess.check_output(['git','-C',str(WT),'show',PRIOR+':kc-dev-flow-2/scripts/package_version.py'],text=True)

def pkg(root,code):
    target=root/'kc-dev-flow-2'
    (target/'scripts').mkdir(parents=True)
    (target/'.claude-plugin').mkdir()
    (target/'references/sd').mkdir(parents=True)
    (target/'scripts/package_version.py').write_text(code)
    (target/'scripts/test_package_version.py').write_text(tests)
    for name in ['.claude-plugin/plugin.json','references/sd/workflow.md']:
        shutil.copyfile(WT/'kc-dev-flow-2'/name,target/name)
    return target

with tempfile.TemporaryDirectory() as temporary:
    prior=pkg(Path(temporary)/'prior',old)
    before=subprocess.run([sys.executable,'-B','scripts/test_package_version.py'],cwd=prior,capture_output=True,text=True)
    (OUT/'tests-before.log').write_text(before.stdout+before.stderr)
    assert before.returncode==1 and 'FAILED (failures=5)' in before.stderr,before.stdout+before.stderr
    (OUT/'tests-before.exit').write_text(str(before.returncode)+'\n')
    results=[]
    controls=[('search-pages','            if len(found) >= total:\n','            if page == 1 or len(found) >= total:\n','test_search_reads_the_next_page_before_reporting_unlisted'),
              ('search-incomplete','            if data["incomplete_results"]:\n','            if False:\n','test_search_reports_timeout_or_result_cap_without_changing_debt_exit'),
              ('search-cap','            if total > 1000:\n','            if False:\n','test_search_reports_timeout_or_result_cap_without_changing_debt_exit'),
              ('search-short-page','            if len(items) < 100:\n','            if len(items) < 100:\n                return found\n','test_search_missing_a_page_is_explicitly_unavailable'),
              ('omitted-content','            if not isinstance(data, dict) or data.get("encoding") != "base64":\n','            if False:\n','test_omitted_workflow_contents_are_unreadable_not_equal')]
    for name,before,after,method in controls:
        assert before in source,name
        mutant=pkg(Path(temporary)/name,source.replace(before,after,1))
        run=subprocess.run([sys.executable,'-B','-m','unittest','test_package_version.RolloutTest.'+method],cwd=mutant/'scripts',capture_output=True,text=True)
        (OUT/(name+'-mutation.log')).write_text(run.stdout+run.stderr)
        assert run.returncode==1 and 'AssertionError' in run.stderr,(name,run.stdout,run.stderr)
        results.append({'name':name+' control rejected','status':'passed','message':'mutation exit 1'})

def method(code,name):
    tree=ast.parse(code)
    cls=next(node for node in tree.body if isinstance(node,ast.ClassDef) and node.name=='Github')
    node=next(node for node in cls.body if isinstance(node,ast.FunctionDef) and node.name==name)
    return ast.get_source_segment(code,node)
assert method(old,'releases')==method(source,'releases')
results.append({'name':'matching-refs caller unchanged','status':'passed','message':'Github.releases source bytes unchanged; documented non-paginated call retained'})
large=json.loads((OUT/'large-content.json').read_text())
with tempfile.TemporaryDirectory() as temporary:
    for name,code in [('prior',old),('candidate',source)]:
        path=Path(temporary)/(name+'.py');path.write_text(code)
        spec=importlib.util.spec_from_file_location(name+'_pv',path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        client=module.Github();client.run=lambda *args:large
        if name=='prior':
            assert client.content('github/rest-api-description','descriptions/api.github.com/api.github.com.json','main')==''
        else:
            try:client.content('github/rest-api-description','descriptions/api.github.com/api.github.com.json','main')
            except module.Unreadable as error:assert 'content omitted' in str(error)
            else:raise AssertionError('omitted content accepted')
results.append({'name':'real large-content response','status':'passed','message':'public 14,216,605-byte file: prior returns empty text, candidate raises explicit unreadability'})
(OUT/'proof-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
