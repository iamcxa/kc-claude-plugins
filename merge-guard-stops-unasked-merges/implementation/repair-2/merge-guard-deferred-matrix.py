from pathlib import Path
import importlib.util
import json
import subprocess
import tempfile

wt = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-merge-guard-stops-unasked-merges')
current = wt / 'kc-dev-flow-2/scripts/merge_guard.py'
previous = subprocess.check_output(['git', '-C', str(wt), 'show', 'ebac86a561655d990d2fcd7ff3cd8dbb20e8eb65:kc-dev-flow-2/scripts/merge_guard.py'], text=True)
head = '1234567890abcdef1234567890abcdef12345678'
merge = f'gh pr merge 672 --repo owner/repo --squash --match-head-commit {head}'
forms = [(flag, merge + ' ' + flag, 'stop') for flag in ('--auto', '--auto=true', '--auto=1', '--auto=t', '--auto=false', '--auto=0', '--auto=', '--auto=unknown')]
forms += [('wrapped auto', f'command -p -- /opt/bin/gh -R owner/repo pr merge --auto 672 --match-head-commit {head}', 'stop')]
forms += [(f'REST async {action}', f'gh api -X PUT repos/owner/repo/pulls/672/merge-async -f sha={head} -f merge_action={action}', 'stop') for action in ('default', 'direct_merge', 'merge_queue')]
forms += [('encoded REST async', f'gh api -X PUT repos/owner/repo/pulls/672/%6derge%2dasync -f sha={head} -f merge_action=merge_queue', 'stop')]
forms += [(name, "gh api graphql -f 'query=mutation {" + name + '(input:{pullRequestId:"x"}){clientMutationId}}' + "'", 'stop') for name in ('enablePullRequestAutoMerge', 'enqueuePullRequest')]
forms += [('opaque GraphQL', 'gh api graphql --input request.json', 'stop'), ('unknown future flag', merge + ' --merge-when-ready', 'stop')]
forms += [('ordinary carried merge', merge, 'pass'), ('cancel auto-merge', merge + ' --disable-auto', 'pass'), ('subject text', merge + " --subject '--auto'", 'pass')]
with tempfile.TemporaryDirectory(prefix='merge-deferred-matrix-') as folder:
    root = Path(folder)
    record = root / 'task/merge/ask-1.json'
    record.parent.mkdir(parents=True)
    record.write_text(json.dumps({'pr': 'owner/repo#672', 'head': head}))
    old = root / 'previous.py'
    old.write_text(previous)
    modules = {}
    for key, path in [('previous', old), ('current', current)]:
        spec = importlib.util.spec_from_file_location(key, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules[key] = module
    results = []
    for name, command, expected in forms:
        verdicts = {key: module.verdict(command, root, [root]) for key, module in modules.items()}
        assert verdicts['current'][0] == expected, (name, verdicts)
        results.append({'name': name, 'command': command, 'matching_record': True, 'previous': verdicts['previous'][0], 'current': verdicts['current'][0], 'reason': verdicts['current'][1], 'status': 'passed'})
Path('/tmp/merge-guard-deferred-matrix.json').write_text(json.dumps(results, indent=2) + '\n')
print(len(results), 'command forms satisfy their expected verdict; no gh merge executed')
