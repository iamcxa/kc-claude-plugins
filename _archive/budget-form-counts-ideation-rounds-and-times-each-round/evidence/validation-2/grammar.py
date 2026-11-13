import importlib.util,sys
from pathlib import Path
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,Path(path)/'role_triggers.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
a,b=load(sys.argv[1],'base'),load(sys.argv[2],'candidate')
for value in ('ONE cycle per stage.', 'two implementation and three validation cycles', 'at most 5 dispatches total', '最多 5 次派工'):
 assert a.budget_bound(value)==b.budget_bound(value),(value,a.budget_bound(value),b.budget_bound(value))
 print(value, b.budget_bound(value))
for value in ('2 ideation, 1 implementation and 2 validation cycles','two ideation, one implementation and two validation cycles, in one package PR.'):
 assert b.budget_bound(value)==dict(ideation=2,implementation=1,validation=2)
print('PASS: four legacy forms unchanged; digits/words new form parsed')
