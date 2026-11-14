from pathlib import Path
import ast, contextlib, io, json, os, sys, tempfile
R=Path(__file__).parent
sys.path.insert(0,str(R/'candidate/kc-dev-flow-2/scripts'))
import test_delivery_gate as tests
gate=tests.gate
read=json.loads((R/'blind-reader/result.json').read_text())
text="\n".join(read['lines'])+"\n"
with tempfile.TemporaryDirectory() as d:
 task=Path(d)/'task.md';task.write_text(tests.TASK);tests.captain_record(task)
 checks={'reviewer_declaration':gate.reviewer_problems(task,tests.TASK,text,'copilot',{'codex','copilot'})[0], 'reviewer_outcome':gate.unstated_second_reviewers(text), 'round_count':gate.summary_round_problems(text), 'Captain_steps':gate.captain_step_problems(task,'Review this candidate.',text)}
 assert not any(checks.values()),checks
rows=[]
for name,declaration in [('omitted',''),('blind reader',read['lines'][0]+'\n')]:
 pair=tests.RecordRouteParityTests().paired(declaration=declaration)
 result={route:{k:pair[route][k] for k in ('check','question')} for route in pair}
 expected=1 if name=='omitted' else 0
 assert all(code==expected for row in result.values() for code in row.values()),result
 rows.append(dict(case=name,routes=result))
source=(R/'candidate/kc-dev-flow-2/scripts/delivery_gate.py').read_text();tree=ast.parse(source)
qs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='question'];assert len(qs)==1
returns=sum(isinstance(n,ast.Return) for n in ast.walk(qs[0]));assert returns==1 and not any(isinstance(n,ast.FunctionDef) and n.name=='facts_question' for n in tree.body)
(R/'results/blind-guards.json').write_text(json.dumps(dict(literal_lines=read['lines'],checks=checks,paired=rows,question_functions=1,question_returns=returns),indent=2)+'\n')
print('Blind literal lines pass all four guards; declaration omitted holds 1/1, supplied passes 0/0 in both routes; one shared question return.')
