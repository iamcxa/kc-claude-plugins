import ast, importlib.util, io, json, os, subprocess, sys, tarfile, tempfile, unittest
from pathlib import Path
root=Path(sys.argv[1]);out=Path(__file__).resolve().parent;out.mkdir(parents=True,exist_ok=True);scripts=root/'kc-dev-flow-2/scripts'
os.environ.update(SPACEDOCK_BIN='/Users/kent/.local/bin/spacedock',PYTHONDONTWRITEBYTECODE='1')
sys.path.insert(0,str(scripts))
import test_dispatch_stage as td
import test_design_surfaces as ts
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
def run(name,tests):
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.TestSuite(tests))
    (out/(name+'.log')).write_text(stream.getvalue())
    assert result.failures and not result.errors,(name,stream.getvalue())
    return dict(name=name,status='passed',assertion_failures=len(result.failures),errors=len(result.errors))
native='test_worth_requirement_uses_native_stage_for_yaml_status_values'
closed='test_unreadable_native_stage_does_not_make_design_presentable'
comments='test_html_comments_cannot_supply_the_worth_heading'
export=tempfile.TemporaryDirectory(prefix='worth-base-export-')
archive=subprocess.check_output(['git','-C','/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-budget-overrun-holds-and-findings-meet-non-goals','archive','5bf7cf78866a2f0f6376c15b59fc400519c5ffeb','kc-dev-flow-2'])
with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:bundle.extractall(export.name,filter='data')
baseline=Path(export.name)/'kc-dev-flow-2'
td.ROOT=baseline;ts.ds=load('baseline_design',baseline/'scripts/design_surfaces.py')
rows=[run('f1-base-export',[td.DispatchStageTests(native)]),run('f2-base-export',[ts.WorthQuestionsTests(comments)]),run('native-error-base-export',[td.DispatchStageTests(closed)])]
td.ROOT=root/'kc-dev-flow-2';ts.ds=load('candidate_design',scripts/'design_surfaces.py')
source=(scripts/'design_surfaces.py').read_text()
tree=ast.parse(source);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='worth_lines')
lines=source.splitlines(keepends=True)
blind=''.join(lines[:node.lineno-1])+"def worth_lines(text):\n    from role_triggers import outside_fences\n    yield from outside_fences(text)\n"+''.join(lines[node.end_lineno:])
cases=[('restore-raw-stage',source.replace('needed = worth_stage(path) == "ideation"','needed = bool(status and status[1] == "ideation")'),native),
       ('restore-comment-blind',blind,comments),
       ('ignore-native-error',source.replace('errors.append(f"{path.name}: cannot read stage for Worth questions: {exc}")','pass'),closed)]
start=source.index('    if data.get("command") != "read"')
end=source.index('    return fields.get("status")',start)
cases.append(('ignore-native-binding-and-type',source[:start]+source[end:],closed))
for name,mutant,method in cases:
    assert mutant!=source
    with tempfile.TemporaryDirectory(prefix='worth-mutant-') as temporary:
        package=Path(temporary);(package/'scripts').mkdir();(package/'references').symlink_to(root/'kc-dev-flow-2/references')
        for path in scripts.glob('*.py'):
            target=package/'scripts'/path.name
            if path.name=='design_surfaces.py':target.write_text(mutant)
            else:target.symlink_to(path)
        td.ROOT=package
        ts.ds=load('mutant_'+name.replace('-','_'),package/'scripts/design_surfaces.py')
        tests=[ts.WorthQuestionsTests(method)] if method==comments else [td.DispatchStageTests(method)]
        rows.append(run(name,tests))
td.ROOT=root/'kc-dev-flow-2';ts.ds=load('candidate_restored',scripts/'design_surfaces.py')
(out/'repair-proof.json').write_text(json.dumps(dict(baseline='5bf7cf78866a2f0f6376c15b59fc400519c5ffeb',results=rows),indent=2)+'\n')
print('PASS: 3 baseline failures and 4 repair mutations caught by assertion failures, zero errors')

export.cleanup()
