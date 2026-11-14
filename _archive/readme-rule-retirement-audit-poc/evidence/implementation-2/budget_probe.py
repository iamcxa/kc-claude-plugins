import importlib.util,sys
s=importlib.util.spec_from_file_location('lint_tree',sys.argv[1])
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
errors=m.budget_errors(m.workflow_budget()+int(sys.argv[2]))
print('\n'.join(errors) or 'budget exact')
sys.exit(bool(errors))
