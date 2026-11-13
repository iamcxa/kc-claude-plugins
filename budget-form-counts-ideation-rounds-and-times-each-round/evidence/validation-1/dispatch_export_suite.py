"""Run unchanged dispatch tests except the declared package path in fixture notes.
The tested ROOT/WRAPPER/CHECKER remain in the candidate export.
"""
import sys
from pathlib import Path
p=Path(sys.argv.pop(1)).resolve()
declared=Path(sys.argv.pop(1))
source=(p/'test_dispatch_stage.py').read_text()
source=source.replace('Package root: {ROOT}', 'Package root: {DECLARED_ROOT}')
source=source.replace("str(ROOT / 'scripts/scratch.py')", "str(DECLARED_ROOT / 'scripts/scratch.py')")
sys.path.insert(0,str(p))
sys.argv[0]=str(p/'test_dispatch_stage.py')
globals().update(__file__=str(p/'test_dispatch_stage.py'),DECLARED_ROOT=declared)
exec(compile(source,str(p/'test_dispatch_stage.py'),'exec'),globals())
