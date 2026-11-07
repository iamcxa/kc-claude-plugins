import datetime, json, os, pathlib, re, subprocess, sys
root = pathlib.Path(__file__).parent
meta = json.loads((root / 'meta.json').read_text())
candidate = root / 'candidate'
task = pathlib.Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/delivery-check-passes-a-skipped-by-design-run')
package = pathlib.Path('/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0')
workflow = pathlib.Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state').parent
logs = root / 'checks'
logs.mkdir(exist_ok=True)
results = []
def run(name, command, cwd=candidate, git=False):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    if git:
        env.update(GIT_DIR=meta['git_dir'], GIT_WORK_TREE=str(candidate))
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    output = result.stdout + result.stderr
    (logs / (name + '.log')).write_text(output)
    count = re.search(r'Ran (\d+) tests?', output)
    results.append(dict(name=name, command=command, exit=result.returncode, status='passed' if result.returncode == 0 else 'failed', cases=int(count[1]) if count else None, message=output[-1000:]))
    (logs / 'results.json').write_text(json.dumps(results, indent=2)+'\n')
    print(name, 'exit', result.returncode, count[0] if count else '', flush=True)
    return result
for name in ('base','candidate'):
    run(name+'-replay', [sys.executable, '-B', str(task/'ideation/replay.py'), str(root/name/'kc-dev-flow-2/scripts'), str(task/'ideation/pr1338.json')])
for test in ('delivery_gate','pr_watch','dispatch_records','validation_security','design_surfaces'):
    run(test, [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'kc-dev-flow-2/scripts', '-p', 'test_'+test+'.py'])
run('mutations', [sys.executable, '-B', str(task/'implementation/mutations.py'), str(candidate), str(logs)])
run('lint-skills', [sys.executable, '-B', 'kc-dev-flow-2/scripts/lint-skills.py'], git=True)
run('adr-lint', [sys.executable, '-B', str(package/'scripts/adr_lint.py'), 'docs/adr', '--since', meta['base']], git=True)
run('number-guards', [sys.executable, '-B', str(package/'scripts/number_guards.py'), 'check', '--repo', str(candidate), '--workflow-dir', str(workflow), '--task', str(task)+'.md', '--base',meta['base']], git=True)
run('comment-ratio', [sys.executable, '-B', str(package/'scripts/comment_ratio.py'), meta['base'], meta['candidate'], '--workflow-dir', str(workflow)], git=True)
doc = run('doc-impact', [sys.executable, '-B', str(package/'scripts/doc_impact.py'), meta['base'], meta['candidate'], '--json'], git=True)
(logs/'doc-impact.json').write_text(doc.stdout)
run('scope-proof', [sys.executable, '-B', str(task/'implementation/scope-proof.py'), str(candidate), str(logs)], git=True)
run('design-surfaces', [sys.executable, '-B', str(package/'scripts/design_surfaces.py'), 'check', str(task)+'.md'], git=True)
run('dispatch-records', [sys.executable, '-B', str(package/'scripts/dispatch_records.py'), str(task)], git=True)
run('fo-text-diff', ['git','-C',meta['wt'],'diff','--stat',meta['base']+'...'+meta['candidate'],'--','kc-dev-flow-2/references','kc-dev-flow-2/skills','kc-dev-flow-2/extensions','docs/dev2'])
print('ALL CHECKS COMPLETE', flush=True)
sys.exit(any(r['exit'] != 0 for r in results))
