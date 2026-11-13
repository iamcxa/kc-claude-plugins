import contextlib,importlib.util,io,json,os,sys,tempfile
from pathlib import Path
wt,scratch=map(Path,sys.argv[1:])
sys.path.insert(0,str(wt/"kc-dev-flow-2/scripts"))
import test_design_surfaces as tests
ds=tests.ds
rows=[]
for name,runner,kwargs,plain,comment in [
 ("Prod security review",tests.SecurityReviewTests().run_check,dict(review="",report=None),"ideation","ideation # ready for review"),
 ("UI design review",tests.DesignReviewTests().run_check,dict(review="",report=None),"ideation","ideation # ready for review"),
 ("UI built-screen review",tests.BuiltScreenTests().run_check,dict(report=""),"validation","validation # ready for review")]:
    old=runner(status=plain,**kwargs)[0]
    new=runner(status=comment,**kwargs)[0]
    rows.append(dict(consumer=name,plain_errors=old,comment_errors=new,verdict_changed=bool(old)!=bool(new),product_changed=False))
scope=tests.ScopeCheckTests()
scope.setUp()
try:
    scope.add_line()
    old=ds.scope_hold(scope.task)
    scope.edit("status: ideation","status: ideation # ready for review")
    new=ds.scope_hold(scope.task)
    rows.append(dict(consumer="scope_hold",plain_verdict=old[0],comment_verdict=new[0],verdict_changed=old[0]!=new[0],product_changed=False))
finally:
    scope.doCleanups()
with tempfile.TemporaryDirectory() as directory:
    path=tests.write_task(directory,tests.GATED)
    out=io.StringIO()
    with contextlib.redirect_stdout(out): before=ds.main(["check",str(path)])
    plain=out.getvalue()
    path.write_text(path.read_text().replace("status: ideation","status: ideation # ready for review"))
    out=io.StringIO()
    with contextlib.redirect_stdout(out): after=ds.main(["check",str(path)])
    from delivery_gate import ASK_FORM
    rows.append(dict(consumer="main gate-question note",plain_exit=before,comment_exit=after,
                     plain_ask_form=ASK_FORM in plain,comment_ask_form=ASK_FORM in out.getvalue(),
                     verdict_changed=before!=after,output_changed=plain!=out.getvalue(),product_changed=False))
(scratch/"older-consumers.json").write_text(json.dumps(rows,indent=2))
for row in rows: print(row["consumer"],"verdict changed",row["verdict_changed"])
