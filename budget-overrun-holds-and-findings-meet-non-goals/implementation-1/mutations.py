import importlib.util, io, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
root=Path(sys.argv[1]); scripts=root/'kc-dev-flow-2/scripts'; out=Path('/tmp/budget-implementation')
os.environ.update(PYTHONDONTWRITEBYTECODE='1', SPACEDOCK_BIN='/Users/kent/.local/bin/spacedock')
sys.path.insert(0,str(scripts))
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,file); value=importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value
tr=module('test_role_triggers',scripts/'test_role_triggers.py'); td=module('test_dispatch_stage',scripts/'test_dispatch_stage.py'); ts=module('test_design_surfaces',scripts/'test_design_surfaces.py')
cases=[
('forward-budget', 'dispatch_stage.py', '        sys.stderr.write("".join(line for line in roles.stdout.splitlines(keepends=True) if line.startswith("budget:")))', '        pass', td, 'DispatchStageTests', ['test_budget_line_and_spent_cycles_are_printed_before_build','test_uncountable_budget_stdout_is_forwarded']),
('off-by-one','role_triggers.py','count > bound[stage]','count >= bound[stage]',tr,'BudgetTest',['test_pending_overrun_holds_and_an_amendment_clears_it']),
('ignore-amendment','role_triggers.py','value = budget_text(text)\n','value = budget_text(text, amendments=False)\n',tr,'BudgetTest',['test_pending_overrun_holds_and_an_amendment_clears_it']),
('ignore-first-header','role_triggers.py','if admitted and over:','if over:',tr,'BudgetTest',['test_old_first_stage_record_never_opts_in_with_later_headers']),
('keep-countable-reminder','role_triggers.py','and not stepped and not bound else []','and not stepped else []',tr,'BudgetTest',['test_countable_budget_removes_advisory_but_preserves_role_calls']),
('lose-uncountable-reminder','role_triggers.py','and not stepped and not bound else []','and not stepped and bound else []',tr,'StepBackTest',['test_two_failed_reports_count_once_each_and_passing_reports_do_not_count']),
('invent-amendment-bound','role_triggers.py','and any(bound in entry.get(key, "") for key in ("Asked", "Captain"))','',tr,'BudgetTest',['test_amendment_needs_the_same_entry_verbatim_words']),
('optional-worth','design_surfaces.py','if (design is not None or (status and status[1] == "ideation"))','if False',ts,'WorthQuestionsTests',['test_design_without_worth_questions_is_refused_even_with_fenced_example']),
('optional-seed-bound','design_surfaces.py','if "Budget" in found and not budget_bound','if False and not budget_bound',ts,'WorthQuestionsTests',['test_new_seed_budget_needs_a_fixed_form_and_cannot_borrow_an_amendment']),
]
rows=[]
for name,file,old,new,testmod,cls,names in cases:
    with tempfile.TemporaryDirectory(prefix='budget-mutant-') as temp:
        dest=Path(temp); source=(scripts/file).read_text(); assert old in source,(name,old)
        target=dest/file; target.write_text(source.replace(old,new,1))
        for other in scripts.glob('*.py'):
            if other.name!=file: (dest/other.name).symlink_to(other)
        if file=='role_triggers.py': tr.SCRIPT=target
        if file=='dispatch_stage.py': td.WRAPPER=target
        if file=='design_surfaces.py':
            mutant=module('design_mutant_'+name.replace('-','_'),target)
            ts.ds=mutant
        suite=unittest.TestSuite(getattr(testmod,cls)(method) for method in names)
        buffer=io.StringIO(); result=unittest.TextTestRunner(stream=buffer,verbosity=2).run(suite)
        (out/('mutation-'+name+'.log')).write_text(buffer.getvalue())
        assert result.failures and not result.errors,(name,buffer.getvalue())
        rows.append(dict(name=name,status='passed',detail='mutant failed the named acceptance test',tests=names,failures=len(result.failures)))
        tr.SCRIPT=scripts/'role_triggers.py';td.WRAPPER=scripts/'dispatch_stage.py';ts.ds=module('restored_ds',scripts/'design_surfaces.py')
# Independent word-count falsifier, using the production arithmetic check.
lint=module('workflow_lint',scripts/'lint-skills.py'); count=len((root/'kc-dev-flow-2/references/sd/workflow.md').read_text().split())
assert not lint.budget_errors(count),lint.budget_errors(count)
for off in (-1,1):
    errors=lint.budget_errors(count+off);assert errors
    rows.append(dict(name=f'workflow-count-{off:+d}',status='passed',detail=errors[0]))
(out/'mutations.json').write_text(json.dumps(rows,indent=2)+'\n')
print(len(rows),'falsifiers caught')
