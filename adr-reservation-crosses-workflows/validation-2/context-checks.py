import importlib.util
import json
import re
import subprocess
import tempfile
from pathlib import Path
WT = Path('/tmp/adr-reservation-validation-801-r2/candidate')
STATE = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
OUT = Path('/tmp/adr-reservation-validation-801-r2')
BASE = 'ba055b8a7a55a787ac989c4cef52d07dd75661ad'

def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

git = lambda root, *args: subprocess.check_output(['git', '-C', str(root), *args], text=True)
with tempfile.TemporaryDirectory(prefix='adr-context-') as tmp:
    old_path = Path(tmp) / 'old.py'
    old_path.write_text((OUT/'base/kc-dev-flow-2/scripts/number_guards.py').read_text())
    old = module(old_path, 'old_guard')
    new = module(WT / 'kc-dev-flow-2/scripts/number_guards.py', 'new_guard')
    files = git(STATE, 'ls-files', '*.md').splitlines()
    task = Path(tmp) / 'task.md'
    checked = []
    for name in files:
        text = git(STATE, 'show', 'HEAD:' + name)
        if '## Number guards' not in text:
            continue
        task.write_text(text)
        assert old.task_facts(task) == new.task_facts(task), name
        checked.append(name)
    (OUT / 'corpus.json').write_text(json.dumps({'state_sha': git(STATE, 'rev-parse', 'HEAD').strip(), 'matched_tasks': len(checked), 'paths': checked}, indent=2))
    print('Task parser equivalence:', len(checked), 'committed live/archive tasks')

    words = lambda t: re.findall(r'[a-z0-9<>/_.\-]+', t.lower().replace('`', ''))
    rel = 'kc-dev-flow-2/references/sd/workflow.md'
    before = (OUT/'base'/rel).read_text()
    after = (WT / rel).read_text()
    section = lambda t, title: re.search(r'^## ' + re.escape(title) + r'\n(.*?)(?=^## |\Z)', t, re.M | re.S).group(0)
    bullet = lambda t, title: re.search(r'^- \*\*' + title + r'\.\*\*(.*?)(?=^- \*\*|^## |\Z)', t, re.M | re.S).group(0)
    rows = [
      dict(name='FO startup, normalized words', before=len(words(before)), after=len(words(after))),
      dict(name='Workflow lint budget, whitespace words', before=len(before.split()), after=len(after.split())),
      dict(name='Worker Number guards, including heading', before=len(words(section(before, 'Number guards'))), after=len(words(section(after, 'Number guards')))),
      dict(name='Reserve bullet', before=len(words(bullet(before, 'Reserve'))), after=len(words(bullet(after, 'Reserve')))),
      dict(name='Check bullet', before=len(words(bullet(before, 'Check'))), after=len(words(bullet(after, 'Check')))),
      dict(name='Collision bullet', before=len(words(bullet(before, 'Collision'))), after=len(words(bullet(after, 'Collision')))),
    ]
    assert all(row['after'] <= row['before'] for row in rows)
    (OUT / 'words-context.json').write_text(json.dumps(rows, indent=2))
    print('Word recount:', rows)

    text = (STATE / 'adr-reservation-crosses-workflows.md').read_text()
    gate = re.findall(r"^\s+reason: '(.*)'$", text, re.M)[1].replace("''", "'")
    quote = re.search(r'The Captain chose (「.*?」)', gate).group(1)
    question = re.search(r'answering (「.*」)\. Recommendation:', gate).group(1)
    adr_path = WT / 'docs/adr/0002-applied-migrations-are-frozen-and-numbers-are-reserved.md'
    adr = adr_path.read_text()
    amendment = adr.split('Amended 2026-11-07', 1)[1]
    assert quote in amendment and question in amendment
    wrong = amendment.replace(quote, '「拒絕」')
    assert not (quote in wrong and question in wrong)
    print('ADR quote and bound question match gate; wrong-quote mutation refused')

    package = WT / 'kc-dev-flow-2'
    (Path(tmp) / 'scripts').mkdir()
    lint = Path(tmp) / 'scripts/lint-skills.py'
    lint.write_text((package / 'scripts/lint-skills.py').read_text().replace('    dict(delta=-6, why="number_guards.py help lists the rules and R8 prints the cross-workflow collision step"),\n', ''))
    lint_mod = module(lint, 'mutant_lint')
    defects = lint_mod.budget_errors(len(after.split()))
    assert defects and any('cut' in defect for defect in defects), defects
    print('AC7 missing budget step mutation refused:', defects)

    bad_dir = Path(tmp) / 'adr'
    bad_dir.mkdir()
    bad_adr = bad_dir / adr_path.name
    bad_adr.write_text(adr.replace('## Status\n\nAccepted', '## Status\n\nInvalid'))
    result = subprocess.run(['python3', '-B', '/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py', str(bad_dir), '--require', '0002'], capture_output=True, text=True)
    assert result.returncode == 1 and "status 'Invalid'" in result.stdout, result.stdout + result.stderr
    print('AC9 invalid status mutation refused:', result.stdout.strip())
