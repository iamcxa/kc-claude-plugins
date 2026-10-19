import subprocess, sys, shutil
from pathlib import Path
WT = Path(sys.argv[1]); SC = WT / "kc-dev-flow-2/scripts"; WF = WT / "kc-dev-flow-2/references/sd/workflow.md"
def clean():
    for d in WT.rglob("__pycache__"): shutil.rmtree(d, ignore_errors=True)
def sh(*cmd):
    clean()
    r = subprocess.run(["python3", "-B", *cmd], cwd=WT, capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout + r.stderr
def restore(): subprocess.run(["git", "-C", str(WT), "checkout", "--", "kc-dev-flow-2"], check=True)
def mutate(path, old, new, count=None):
    t = path.read_text(); assert old in t, old
    if count is not None: assert t.count(old) == count, (old, t.count(old))
    path.write_text(t.replace(old, new))
def failed(out):
    import re
    return sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+)", out, re.M)))
def report(name, code, out, only=None):
    print(f"## {name}: exit={code} failing={failed(out)}")
    return code, out
NG = SC / "number_guards.py"
# baseline
for t in ("test_number_guards.py", "test_poc_readme.py"):
    c, o = sh(f"kc-dev-flow-2/scripts/{t}"); print(f"baseline {t}: exit={c}")
c, o = sh("kc-dev-flow-2/scripts/lint-skills.py"); print("baseline lint exit=", c)
# AC-1: step left out
mutate(SC / "lint-skills.py", '    dict(delta=-55, why="number_guards.py prints the R2 and R6 next steps and --help lists the flags and rules; the README points to them"),\n', "", 1)
c, o = sh("kc-dev-flow-2/scripts/lint-skills.py"); print("## AC-1 step left out: exit=", c, [l for l in o.splitlines() if "under the budget" in l]); restore()
# AC-3: each message tail alone
mutate(NG, "revert it and add a new migration", "revert it", 2)
report("AC-3 R2 tail", *sh("kc-dev-flow-2/scripts/test_number_guards.py")); restore()
mutate(NG, "a POC task changes none of it", "a POC task is frozen", 1)
report("AC-3 R6 tail", *sh("kc-dev-flow-2/scripts/test_number_guards.py")); restore()
t = NG.read_text(); i = t.index("R1 a migration"); 
mutate(NG, "R6 a task whose frontmatter", "Rule-six a task whose frontmatter", 1)
report("AC-3 --help R6 rule item", *sh("kc-dev-flow-2/scripts/test_number_guards.py")); restore()
mutate(NG, "check   exit 0 clean, 1 findings, 2 misconfiguration. Rules: R1 a migration", "check   exit 0 clean, 1 findings, 2 misconfiguration. Rules: Rule-one a migration", 1)
report("AC-3 --help R1 rule item", *sh("kc-dev-flow-2/scripts/test_number_guards.py")); restore()
# AC-4: each kept phrase alone, inside the Number guards POC bullet / section
text = WF.read_text()
ng = text.index("\n## Number guards\n"); poc = text.index("- **POC.**", ng); end = text.index("\n## FO steps", poc)
bullet = text[poc:end]
for phrase in ("FAIL R6", "boundary-crossed: persistent-state", "not repaired in\n  place", "reserves no number"):
    assert bullet.count(phrase) == 1, phrase
    WF.write_text(text[:poc] + bullet.replace(phrase, "XX") + text[end:])
    report(f"AC-4 POC bullet without {phrase!r}", *sh("kc-dev-flow-2/scripts/test_poc_readme.py")); restore()
sec = text[ng:end]; ph = "(default `docs/adr`)"; assert sec.count(ph) == 1
WF.write_text(text[:ng] + sec.replace(ph, "") + text[end:])
report("AC-4 adr-path default", *sh("kc-dev-flow-2/scripts/test_poc_readme.py")); restore()
# AC-4 falsifier: the replaced pin at base
c, o = sh("-c", "print()")
print("done")
