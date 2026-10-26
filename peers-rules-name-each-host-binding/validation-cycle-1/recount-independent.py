from pathlib import Path
import re,json,subprocess
E=Path('/tmp/peers-validation-730-cycle1-evidence');m=json.loads((E/'reading-manifest.json').read_text());w=Path('/tmp/peers-validation-730-cycle1')
def section(t,title):
 lines=t.splitlines(keepends=True); start=lines.index('## '+title+'\n'); end=next((i for i in range(start+1,len(lines)) if lines[i].startswith('## ')),len(lines));return ''.join(lines[start:end])
for version in ('base','candidate'):
 for path,item in m[version]['inputs'].items():
  text=subprocess.check_output(['git','-C',str(w),'show',m['base_sha']+':kc-dev-flow-2/'+path],text=True) if version=='base' else (w/'kc-dev-flow-2'/path).read_text()
  assert len(re.findall(r'\S+',text))==item['words']
 for title,words in m[version]['sections'].items():
  text=subprocess.check_output(['git','-C',str(w),'show',m['base_sha']+':kc-dev-flow-2/references/sd/workflow.md'],text=True) if version=='base' else (w/'kc-dev-flow-2/references/sd/workflow.md').read_text()
  assert len(re.findall(r'\S+',section(text,title)))==words
for k in ['startup_without_exchange','idle_open','idle_merged','after_archive','merge_ask','warm_exchange','source_repair']:assert m['routes']['base'][k]==m['routes']['candidate'][k]
assert m['routes']['candidate']['native_claude']<=811
assert m['routes']['candidate']['proactive_paseo']<=2481
assert m['routes']['candidate']['unlisted_incoming']<=2191
print('Independent regex/line-index recount agrees; unaffected routes unchanged; new routes within approved ceilings.')
