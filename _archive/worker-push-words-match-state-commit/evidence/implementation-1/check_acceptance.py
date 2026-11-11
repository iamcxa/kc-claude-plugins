import ast
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

OUT = Path(__file__).resolve().parent
WT = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-worker-push-words-match-state-commit')
TASK = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/worker-push-words-match-state-commit.md')
BASE = 'e8664a72b0f904e5dda3c391d52ab3abaca876b4'
EXPECTED = {'kc-dev-flow-2/references/sd/workflow.md', 'kc-dev-flow-2/scripts/lint-skills.py'}
BULLET = '- **Pushes:** the state-branch push that `spacedock state commit`, or the ensign contract\'s sync, makes for your report is yours and expected. Any other push or PR needs a grant your dispatch quotes; "do not push" means those.'
results = []

def git(*args):
    return subprocess.check_output(['git', '-C', str(WT), *args], text=True)

def section(readme):
    return re.search(r'^## Dispatch facts\n(.*?)(?=^## |\Z)', readme, re.M | re.S)[1]

def placement(readme, files):
    assert files == EXPECTED, files
    assert readme.count(BULLET) == 1, 'bullet count'
    assert section(readme).count(BULLET) == 1, 'outside Dispatch facts'

def budget_tree(text):
    tree = ast.parse(text)
    node = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'WORKFLOW_BUDGET_STEPS' for t in n.targets))
    steps = [{kw.arg: ast.literal_eval(kw.value) for kw in call.keywords} for call in node.value.elts]
    return tree, node, steps

def quote_matches(text):
    _, _, steps = budget_tree(text)
    amendment = TASK.read_text().split('### Amendment 1 — ', 1)[1]
    captain = amendment.split('\nCaptain: ', 1)[1].split(' (host ', 1)[0]
    asked = amendment.split('\nAsked: ', 1)[1].split('\n', 1)[0]
    assert captain in steps[-1]['captain'], 'Captain words differ from recorded amendment'
    assert asked in steps[-1]['captain'], 'bound question differs from recorded amendment'

def catches(name, check):
    try:
        check()
    except AssertionError as e:
        results.append(dict(name=name, status='passed', message='mutation rejected: ' + str(e)))
    else:
        raise AssertionError(name + ': mutation escaped')

def main():
    files = set(git('diff', '--name-only', BASE, 'HEAD').splitlines())
    readme = (WT / 'kc-dev-flow-2/references/sd/workflow.md').read_text()
    baseline = git('show', BASE + ':kc-dev-flow-2/references/sd/workflow.md')
    placement(readme, files)
    catches('base lacks the dispatch push explanation', lambda: placement(baseline, files))
    catches('remove bullet', lambda: placement(readme.replace(BULLET, ''), files))
    catches('duplicate bullet', lambda: placement(readme.replace(BULLET, BULLET + '\n' + BULLET), files))
    catches('move bullet outside dispatch facts', lambda: placement(readme.replace(BULLET + '\n', '') + '\n' + BULLET, files))
    catches('extra product path', lambda: placement(readme, files | {'kc-dev-flow-2/skills/implementation/principles.md'}))
    for stage in ['ideation', 'implementation', 'validation']:
        wf = OUT / 'replay-implementation-candidate-1/wf'
        p = subprocess.run(['/Users/kent/.local/bin/spacedock', 'dispatch', 'show-stage-def', '--workflow-dir', str(wf), '--stage', stage], capture_output=True, text=True)
        (OUT / (stage + '-stage-def.md')).write_text(p.stdout + p.stderr)
        assert p.returncode == 0 and p.stdout.count(BULLET) == 1, (stage, p.stdout, p.stderr)
    for name in ['implementation-candidate-1', 'implementation-candidate-2', 'validation-candidate-1', 'validation-candidate-2']:
        run = OUT / ('replay-' + name)
        p = subprocess.run(['/Users/kent/.local/bin/spacedock', 'dispatch', 'show-stage-def', '--workflow-dir', str(run / 'wf'), '--stage', name.split('-')[0]], capture_output=True, text=True)
        assert p.returncode == 0 and p.stdout.count(BULLET) == 1, name
        assert 'dispatch show-stage-def --workflow-dir' in (run / 'dispatch.md').read_text(), name
    for name in ['implementation-release', 'validation-release']:
        run = OUT / ('replay-' + name)
        p = subprocess.run(['/Users/kent/.local/bin/spacedock', 'dispatch', 'show-stage-def', '--workflow-dir', str(run / 'wf'), '--stage', name.split('-')[0]], capture_output=True, text=True)
        assert p.returncode == 0 and BULLET not in p.stdout, name
    candidate_script = (WT / 'kc-dev-flow-2/scripts/lint-skills.py').read_text()
    base_script = git('show', BASE + ':kc-dev-flow-2/scripts/lint-skills.py')
    tree, node, steps = budget_tree(candidate_script)
    base_tree, _, base_steps = budget_tree(base_script)
    assert steps[:-1] == base_steps and steps[-1]['delta'] == 38
    node.value.elts.pop()
    assert ast.dump(tree) == ast.dump(base_tree), 'lint changed beyond the appended step'
    assert len(baseline.split()) == 5939 and len(readme.split()) == 5977
    assert len(section(baseline).split()) + 3 == 300 and len(section(readme).split()) + 3 == 338
    quote_matches(candidate_script)
    catches('wrong gate quotation', lambda: quote_matches(candidate_script.replace('「核准，放派工單都帶的段落（建議）」', '「wrong quote」')))
    fixture = Path(tempfile.mkdtemp(prefix='budget-controls-', dir=OUT))
    shutil.copytree(WT / 'kc-dev-flow-2', fixture / 'kc-dev-flow-2', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (fixture / 'scripts').mkdir(); shutil.copy(WT / 'scripts/skill-frontmatter-lint.sh', fixture / 'scripts/skill-frontmatter-lint.sh')
    _, step_node, _ = budget_tree(candidate_script)
    last = step_node.value.elts[-1]; lines = candidate_script.splitlines(keepends=True)
    start = sum(map(len, lines[:last.lineno-1])); end = sum(map(len, lines[:last.end_lineno])); added = candidate_script[start:end]
    mutations = {'remove raise': candidate_script[:start] + candidate_script[end:],
                 'remove quoted words': candidate_script[:start] + added.replace('「', '[').replace('」', ']') + candidate_script[end:],
                 'remove loading moment': candidate_script[:start] + added.replace('loaded=', 'missing_loaded=') + candidate_script[end:]}
    for name, content in {'candidate lint': candidate_script, **mutations}.items():
        target = fixture / 'kc-dev-flow-2/scripts/lint-skills.py'; target.write_text(content)
        for cache in fixture.rglob('__pycache__'): shutil.rmtree(cache)
        p = subprocess.run([sys.executable, '-B', str(target)], capture_output=True, text=True)
        (OUT / (name.replace(' ', '-') + '.log')).write_text(p.stdout + p.stderr)
        assert p.returncode == (0 if name == 'candidate lint' else 1), (name, p.stdout, p.stderr)
        results.append(dict(name=name, status='passed', message=p.stdout.strip()))
    results.append(dict(name='candidate placement and actual dispatch context loading', status='passed', message='three native stage definitions and all four candidate dispatch context fetches contain one Pushes bullet; two release dispatch context fetches contain none'))
    (OUT / 'acceptance-tests.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(results, indent=2))

main()
