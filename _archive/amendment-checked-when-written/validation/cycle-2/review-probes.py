import json,sys,tempfile
from pathlib import Path
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--candidate',type=Path,default=Path(__file__).resolve().parent/'candidate')
parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parent)
parser.add_argument('--acceptance',action='store_true')
args=parser.parse_args()
out=args.out
sys.path.insert(0,str(args.candidate/'kc-dev-flow-2/scripts'))
from test_laws_check import Repo,task,laws,git
from design_surfaces import move_defects
results=[]
def run(repo,before,after,readme,label):
 code,text=laws(repo.path,'--before',before,'--after',after,'--readme',readme)
 (out/(label+'.log')).write_text(text)
 row={'name':label,'exit':code,'before':before,'after':after,'log':label+'.log','L4_lines':[x for x in text.splitlines() if x.startswith(('L4 ','violation: L4 '))]}
 results.append(row)
 return code,text
with tempfile.TemporaryDirectory(prefix='pr828-review-probes-') as tmp:
 p=Path(tmp);readme=p/'README.md';readme.write_text('---\nextensions: []\n---\n')
 record=task(body='''## Acceptance criteria
**AC-2** old outcome.
## Captain amendments
### Amendment 1 — 2026-11-10, chat
Captain: replace old outcome
Supersedes: AC-2
''')
 moved=record.replace('**AC-2** old outcome.','**AC-5** new unmarked outcome.')+'\nSuperseded text:\n\n**AC-2** old outcome.\n'
 repo=Repo(p/'unreadable');before=repo.commit('record',a=record,z=task())
 event=repo.commit('move with no marker',a=moved)
 solo_code,solo=run(repo,before,event,readme,'review-unreadable-solo')
 (repo.path/'z.md').write_bytes(b'\xff');git(repo.path,'add','z.md');git(repo.path,'commit','-m','unreadable unrelated task');bad=git(repo.path,'rev-parse','HEAD')
 combo_code,combo=run(repo,before,bad,readme,'review-unreadable-combined')
 fixed=repo.commit('restore readable unrelated task',z=task())
 repair_code,repair=run(repo,bad,fixed,readme,'review-unreadable-repair')
 later=repo.commit('unrelated note on valid task',a=moved+'\n## Notes\nUnrelated note.\n')
 later_code,later_out=run(repo,fixed,later,readme,'review-unreadable-later')
 assert solo_code==1 and 'unmarked replacement' in solo
 missing='violation: L4 ' not in combo and 'violation: L4 ' not in repair and 'violation: L4 ' not in later_out
 assert combo_code==2,(combo,repair,later_out)
 tilde_results={}
 for fence in ('```','~~~'):
  label='backtick' if fence=='```' else 'tilde'
  example=f'{fence}md\n**AC-9** Amended by Captain, amendment 1: example only.\n{fence}\n'
  live=moved.replace('## Captain amendments',example+'## Captain amendments')
  repo=Repo(p/label);before=repo.commit('record',t=record);after=repo.commit('move with example',t=live)
  code,text=run(repo,before,after,readme,'review-example-'+label)
  tilde_results[label]={'exit':code,'defects':move_defects(live.splitlines())}
 assert tilde_results['backtick']['exit']==1,tilde_results
summary={'unreadable_discards_known_violation':missing,'tilde_example_hides_unmarked_move':tilde_results['tilde']['exit']==0,'runs':results,'example_helpers':tilde_results}
(out/'review-probes.json').write_text(json.dumps(summary,indent=2)+'\n')
if args.acceptance:
 print('Known move diagnostic retained:', not missing)
 print('Tilde-fenced example ignored:', tilde_results['tilde']['exit']==1)
 sys.exit(int(missing or tilde_results['tilde']['exit']!=1))
print(json.dumps(summary,indent=2))
