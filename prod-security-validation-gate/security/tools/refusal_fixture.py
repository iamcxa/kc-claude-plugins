import sys,tempfile,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('ds','/tmp/psvg-tools/pkg/kc-dev-flow-2/scripts/design_surfaces.py'); ds=importlib.util.module_from_spec(spec); spec.loader.exec_module(ds)
sys.path.insert(0,'/tmp/psvg-tools/pkg/kc-dev-flow-2/scripts')
src=open('/tmp/psvg-tools/pkg/kc-dev-flow-2/scripts/test_design_surfaces.py').read()
PROD=src.split('PROD = """')[1].split('"""')[0]
def run(review,report):
    with tempfile.TemporaryDirectory() as d:
        f=Path(d,'task','security'); f.mkdir(parents=True)
        if report is not None: f.joinpath('ideation-1.yaml').write_text(report)
        p=Path(d,'task.md'); p.write_text(PROD.format(review=review))
        return ds.check_task(p,notes=[])
cases={
 'refusal text saved as the report (cyber category prose, no root line)':("Security review: security/ideation-1.yaml\nSecurity focus file: none\n","I can't help with this request. This looks like it could facilitate a cyberattack."),
 'empty report saved':("Security review: security/ideation-1.yaml\nSecurity focus file: none\n",""),
 'worker writes no review line, no file':("",None),
 'worker writes "not run: reviewer refused"':("Security review: not run: reviewer refused (cyber)\nSecurity focus file: none\n",None),
 'worker writes valid zero-finding report fabricated':("Security review: security/ideation-1.yaml\nSecurity focus file: none\n","tob_security_review:\n  pr: none\n  findings: []\n"),
}
for k,(rev,rep) in cases.items():
    print('CASE',k); 
    for e in run(rev,rep): print('   ',e[:200])
    if not run(rev,rep): print('    (no errors: passes)')
