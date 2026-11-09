import importlib.util, json, sys, tempfile
from pathlib import Path
sys.path.insert(0,"/tmp/pr818-validation-pP1gbX/candidate/kc-dev-flow-2/scripts")
import test_delivery_gate as tests
q=tests.QuestionTests()
fixture=Path("/tmp/pr818-validation-pP1gbX/acceptance.sh").read_text().split("python3 -B - <<'PY'\n",1)[1].split("\nPY",1)[0]
# Reuse the already-run acceptance inputs; only the script called by its real CLI changes.
ctx={"__name__":"replay_cases"}
exec(fixture.split("for name,text,kw in cases:",1)[0],ctx)
rows=[]
for revision,script,want in [
    ("candidate","/tmp/pr818-validation-pP1gbX/candidate/kc-dev-flow-2/scripts/delivery_gate.py",0),
    ("base","/tmp/pr818-validation-pP1gbX/base/kc-dev-flow-2/scripts/delivery_gate.py",1)]:
    tests.gate.__file__=script
    for name,text,kw in ctx["cases"]:
        code,out=q.ask(text,cli=True,**kw)
        rows.append(dict(revision=revision,name=name,exit=code,output=out))
        assert code==want and ("gate text complete" if want==0 else "Captain steps record fails") in out,(revision,name,code,out)
        print(revision+" "+name+": exit "+str(code))
tests.gate.__file__="/tmp/pr818-validation-pP1gbX/candidate/kc-dev-flow-2/scripts/delivery_gate.py"
for name,text,kw,want in [
    ("Python fence in card accepted", "Review this candidate.", {"summary":"Read card.md","cards":{"card.md":"```python\nprint('unrecorded')\n```\n"}},0),
    ("PR attribution link retained", "Review this candidate.", {"summary":"Read review/pr-body.md","cards":{"review/pr-body.md":"https://claude.com/claude-code"}},1)]:
    code,out=q.ask(text,cli=True,**kw)
    rows.append(dict(revision="candidate",name=name,exit=code,output=out))
    assert code==want,(name,code,out)
    print(name+": exit "+str(code))
Path("/tmp/pr818-validation-pP1gbX/evidence/question-replay.json").write_text(json.dumps(rows,indent=2)+"\n")

