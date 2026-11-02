from pathlib import Path
import os, subprocess, sys, tempfile
WT=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-562b1a87')
S=WT/'kc-dev-flow-2/scripts'
ENV={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}

def trial(name, filename, old, new, test, module):
    text=(S/filename).read_text(); assert old in text, name
    with tempfile.TemporaryDirectory(prefix='model-table-mutant-') as d:
        mutant=Path(d)/filename;mutant.write_text(text.replace(old,new,1))
        assert not list(Path(d).rglob('__pycache__'))
        if filename=='role_triggers.py':
            setup=f'import {module} as m; m.SCRIPT=Path({str(mutant)!r})'
        else:
            setup=f'import {module} as m; ns={{"__file__":{str(S/filename)!r}}}; exec(compile(Path({str(mutant)!r}).read_text(), {str(mutant)!r}, "exec"), ns); m.lint.lint_tree=ns["lint_tree"]'
        code='from pathlib import Path; import unittest; '+setup+f'; suite=unittest.defaultTestLoader.loadTestsFromName({test!r},m); result=unittest.TextTestRunner().run(suite); raise SystemExit(not result.wasSuccessful())'
        p=subprocess.run([sys.executable,'-B','-c',code],cwd=S,env=ENV,text=True,capture_output=True)
        print(f'{name}: exit={p.returncode}; '+p.stderr.strip().splitlines()[-1])
        (Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-evidence')/(name+'.log')).write_text(p.stdout+p.stderr)
        assert p.returncode==1, name
trial('AC1-no-astra','role_triggers.py',', "astra": 3','', 'RoleTriggersTest.test_a_call_below_the_required_model_does_not_clear','test_role_triggers')
trial('AC1-leading-word','role_triggers.py','    return next((RANK[word] for word in re.findall(r"[a-z]+", model.lower()) if word in RANK), -1)','    word = re.match(r"[a-z]+", model.lower())\n    return RANK.get(word.group(0), -1) if word else -1','RoleTriggersTest.test_a_call_below_the_required_model_does_not_clear','test_role_triggers')
trial('AC2-no-floor','role_triggers.py','        calls = [(model, made) for model, made in calls if rank(model) >= RANK["opus"]]\n','', 'RoleTriggersTest.test_chief_engineer_floor_applies_to_repairs_and_review_rounds','test_role_triggers')
trial('AC4-one-family','role_triggers.py','where = f"on {need} or gpt-6-astra','where = f"on {need}', 'RoleTriggersTest.test_a_replacing_amendment_names_the_model_the_profile_or_surface_requires','test_role_triggers')
trial('AC6-no-table-check','lint-skills.py','        if cells.get(role) != f"{policy[0].title()} / {policy[1]}":','        if False:', 'RouteMutationTests.test_model_table_cannot_drift_from_agent_policy','test_lint_skills')
print('All five code mutations were detected; -B, no cache directories in mutant inputs.')
