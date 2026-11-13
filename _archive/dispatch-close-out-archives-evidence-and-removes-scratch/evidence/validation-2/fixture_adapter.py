"""Adapt only Package root fixture metadata for an export under /tmp.
Candidate product code, every test assertion, and native Spacedock stay unchanged.
Usage: fixture_adapter.py SCRIPTS RUNNER [RUNNER_ARGS...]
"""
import importlib.util,pathlib,runpy,sys,types
scripts=pathlib.Path(sys.argv.pop(1)); runner=sys.argv.pop(1)
sys.path.insert(0,str(scripts))
p=scripts/'test_dispatch_stage.py'; source=p.read_text()
old='Package root: {ROOT}'
new='Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1'
assert source.count(old)==3
m=types.ModuleType('test_dispatch_stage');m.__file__=str(p);m.__spec__=importlib.util.spec_from_file_location(m.__name__,p)
exec(compile(source.replace(old,new),str(p),'exec'),m.__dict__)
sys.modules[m.__name__]=m
sys.argv=[runner,*sys.argv[1:]]
runpy.run_path(runner,run_name='__main__')
