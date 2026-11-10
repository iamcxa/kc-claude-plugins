import ast
import difflib
from pathlib import Path
import types


def proposed_source(wt):
    path = Path(wt) / 'kc-dev-flow-2/scripts/design_surfaces.py'
    source = path.read_text()
    old = '''    moved = [declarations(entry.moved) for entry in entries]
    live = declarations(section(unfenced(lines), AC_HEADING) or [])
    declared = {ident for ident, _ in live}
'''
    new = '''    moved = [declarations(entry.moved) for entry in entries]
    visible, fence = [], None
    for line in lines:
        marker = AMENDMENT_FENCE.match(line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
        elif marker:
            fence = marker[1]
        else:
            visible.append(line)
    live = declarations(section(visible, AC_HEADING) or [])
    declared = {ident for ident, _ in live}
'''
    assert source.count(old) == 1
    changed = source.replace(old, new)
    before, after = ast.parse(source), ast.parse(changed)
    shape = lambda tree: [ast.dump(n, include_attributes=False) for n in tree.body
                          if not isinstance(n, ast.FunctionDef) or n.name != 'move_defects']
    assert shape(before) == shape(after), 'only the L4-only helper may differ'
    return source, changed


def load_proposal(wt):
    _, source = proposed_source(wt)
    module = types.ModuleType('design_surfaces_proposal')
    module.__file__ = str(Path(wt) / 'kc-dev-flow-2/scripts/design_surfaces.py')
    exec(compile(source, '<unapplied L4 input proposal>', 'exec'), module.__dict__)
    return module


def write_diff(wt, out):
    before, after = proposed_source(wt)
    Path(out, 'proposed-input.diff').write_text(''.join(difflib.unified_diff(
        before.splitlines(keepends=True), after.splitlines(keepends=True),
        fromfile='a/kc-dev-flow-2/scripts/design_surfaces.py',
        tofile='b/kc-dev-flow-2/scripts/design_surfaces.py')))
