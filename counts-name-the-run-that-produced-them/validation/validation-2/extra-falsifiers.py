import importlib.util,json,pathlib,re,shutil,subprocess,sys,tempfile
out=pathlib.Path(__file__).parent;root=out/'candidate'
sys.path.insert(0,str(root/'kc-dev-flow-2/scripts'))
import count_tokens as count
sample='cycle 2, round 2'
old=re.compile(rf'\b(\d[\d,]*)\s*(?:of|/)\s*(\d[\d,]*)\b|\b(\d[\d,]*)\s+(?:\w+\s+)?{count.NOUN}\b',re.I)
assert not count.count_sentences(sample)
assert old.search(sample) and old.search(sample).group(0)=='2, round'
print(json.dumps(dict(criterion='AC-4',falsifier='restore comma-swallowing number grammar',candidate=count.count_sentences(sample),mutant=old.search(sample).group(0))))
with tempfile.TemporaryDirectory(prefix='count-budget-',dir=out) as d:
 d=pathlib.Path(d)
 shutil.copytree(root/'kc-dev-flow-2',d/'kc-dev-flow-2')
 shutil.copytree(root/'scripts',d/'scripts')
 f=d/'kc-dev-flow-2/references/sd/workflow.md'
 before=len(f.read_text().split());f.write_text(f.read_text()+'\nextra\n');after=len(f.read_text().split())
 assert after==before+1
 p=subprocess.run(['python3','-B','kc-dev-flow-2/scripts/lint-skills.py'],cwd=d,capture_output=True,text=True)
 (out/'budget-mutant.log').write_text(p.stdout+p.stderr)
 assert p.returncode==1 and '5932 words exceeds the budget of 5931' in p.stdout+p.stderr,(p.returncode,p.stdout,p.stderr)
 print(json.dumps(dict(criterion='AC-5/AC-6',falsifier='one unapproved startup word',before=before,mutated=after,lint_exit=p.returncode)))
