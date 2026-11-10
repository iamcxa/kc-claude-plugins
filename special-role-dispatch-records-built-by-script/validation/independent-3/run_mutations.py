import json, os, re, shutil, subprocess, sys
from pathlib import Path

home = Path('/tmp/pr827-independent-3')
source = home / 'candidate'
root = home / 'mutant'
out = home / 'evidence'
if not root.exists():
    shutil.copytree(source, root)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', SPACEDOCK_BIN='/Users/kent/.local/bin/spacedock')
script = Path('kc-dev-flow-2/scripts/dispatch_stage.py')
test = 'kc-dev-flow-2/scripts/test_dispatch_stage.py'
text = (source / script).read_text()
role_start = text.index('    if args.role:\n        slug =')
role_end = text.index('    command = [args.spacedock', role_start)
role = text[role_start:role_end]
mutations = [
 ('AC-1-no-commit', script, text.replace('commit = subprocess.run([args.spacedock, "state", "commit", slug, "--workflow-dir", str(args.workflow_dir)],\n                                    capture_output=True, text=True)', 'commit = subprocess.CompletedProcess([], 0, "", "")', 1), 'test_role_commits_complete_record_before_printing_exact_inputs'),
 ('AC-2-no-checks', script, text[:text.index('    checks = [subprocess.run')] + '    checks = []\n' + text[text.index('    if any(check.returncode'):], 'test_role_rejects_incomplete_scope_notes_without_prompt_or_record'),
 ('AC-3-early-prompt', script, text.replace('        if commit.returncode:', '        sys.stdout.write(path.read_text())\n        if commit.returncode:', 1), 'test_role_commit_failure_withholds_prompt_and_retry_reuses_committed_record'),
 ('AC-4-build-path', script, text[:role_start] + text[role_end:], 'test_role_skips_build_and_pending_hold_while_a_chief_engineer_call_is_owed'),
 ('AC-5-no-floor', script, text.replace('if args.role and rank(args.model) < rank("opus"):', 'if False:'), 'test_role_checks_the_opus_model_floor'),
 ('AC-6-allow-advance', script, text.replace('args.advance or args.bare_mode', 'args.bare_mode'), 'test_role_rejects_stage_only_flags_and_unknown_roles'),
 ('AC-7-global-numbers', script, text.replace('rf"{re.escape(args.stage)}-([1-9][0-9]*)\\.md"', 'r"[a-z_-]+-([1-9][0-9]*)\\.md"'), 'test_role_numbering_is_per_role_and_retries_reuse_the_latest_record'),
]
remaining = '--remaining' in sys.argv
rows = json.loads((out / 'mutations.json').read_text()) if remaining else []
def run(name, path, mutated, cmd, extra_env=None):
    before = (root / path).read_text()
    assert before != mutated, name
    (root / path).write_text(mutated)
    log = out / (name + '.log')
    try:
        with log.open('w') as stream:
            p = subprocess.run(cmd, cwd=root, env={**env, **(extra_env or {})}, stdout=stream, stderr=subprocess.STDOUT)
    finally:
        (root / path).write_text(before)
    rows.append(dict(name=name, exit=p.returncode, caught=p.returncode != 0, file=str(log)))
    (out / 'mutations.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(name, p.returncode, flush=True)
for name, path, changed, case in ([] if remaining else mutations):
    run(name, path, changed, [sys.executable, '-B', test, 'DispatchStageTests.' + case])
workflow = Path('kc-dev-flow-2/references/sd/workflow.md')
before = (root / workflow).read_text()
phrase = 'Build chief-engineer and engineering-reviewer calls with `<package>/scripts/dispatch_stage.py --role <agent>`; record each'
if not remaining:
    run('AC-8-no-instruction', workflow, before.replace(phrase, 'Record chief-engineer and engineering-reviewer calls'), [sys.executable, '-B', 'kc-dev-flow-2/scripts/test_sd_dispatch.py', '--sd-plugin-root', '/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3'])
lint = Path('kc-dev-flow-2/scripts/lint-skills.py')
before = (root / lint).read_text()
run('AC-8-no-budget', lint, re.sub(r'    dict\(delta=6, why="FO builds special-role[^\n]*\n[^\n]*\n[^\n]*\n', '', before), [sys.executable, '-B', str(lint)])
adr = Path('docs/adr/0074-special-role-calls-are-built-by-the-stage-dispatch-script.md')
before = (root / adr).read_text()
run('AC-9-no-words', adr, before.replace('**Words:**', '**Removed:**'), [sys.executable, '-B', '/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.37.0/scripts/adr_lint.py', 'docs/adr', '--since', 'd8dbfcb1051d7c696aca139ed9ade332ee85abaf', '--require', '0074'], {'GIT_DIR':'/Users/kent/Project/kc-claude-workspace/kc-claude-plugins/.git/worktrees/spacedock-ensign-special-role-dispatch-records-built-by-script', 'GIT_WORK_TREE':str(root)})
watch = Path('kc-dev-flow-2/scripts/pr_watch.py')
before = (root / watch).read_text()
run('AC-10-changed-idle', watch, before + '\nprint("unexpected extra reading")\n', [sys.executable, '-B', '-c', "from pathlib import Path; assert Path('kc-dev-flow-2/scripts/pr_watch.py').read_bytes() == Path('/tmp/pr827-independent-3/candidate/kc-dev-flow-2/scripts/pr_watch.py').read_bytes(), 'idle surface changed'"])
assert all(row['caught'] for row in rows)
