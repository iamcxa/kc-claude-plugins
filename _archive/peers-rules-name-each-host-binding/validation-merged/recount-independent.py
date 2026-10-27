from pathlib import Path
import subprocess,re,json,hashlib
E=Path('/tmp/peers-validation-730-merge-evidence');W=Path('/tmp/peers-validation-730-merge');M=json.loads((E/'reading-manifest.json').read_text());SD=Path('/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3')
def count(t):return len(re.findall(r'\S+',t))
def section(t,title):
 lines=t.splitlines(keepends=True);start=lines.index('## '+title+'\n');end=next((i for i in range(start+1,len(lines)) if lines[i].startswith('## ')),len(lines));return ''.join(lines[start:end])
startup=count(section((SD/'skills/first-officer/references/first-officer-shared-core.md').read_text(),'Startup'));idle=count(section((SD/'skills/first-officer/references/claude-fo-dispatch.md').read_text(),'Awaiting Completion'));own=count(Path('/Users/kent/.agents/skills/paseo/SKILL.md').read_text())
for arm in ['base','candidate']:
 values={}
 for path,item in M[arm]['inputs'].items():
  text=subprocess.check_output(['git','-C',str(W),'show',M['base_sha']+':kc-dev-flow-2/'+path],text=True) if arm=='base' else (W/'kc-dev-flow-2'/path).read_text();values[path]=count(text)
  assert values[path]==item['words'] and hashlib.sha256(text.encode()).hexdigest()==item['sha256']
  if path=='references/sd/workflow.md':workflow=text
 parts={title:count(section(workflow,title)) for title in ['Delivery authority','Extensions']};assert parts==M[arm]['sections']
 outputs={key:count((E/arm/file).read_text()) for key,file in [('OPEN','watch-OPEN.txt'),('MERGED','watch-MERGED.txt'),('archive','archive.txt'),('merge','merge.txt')]};assert outputs==M[arm]['outputs']
 mod=values['references/sd/mods/kc-dev-flow-2.md'];learn=values['extensions/learn/EXTENSION.md'];learnskill=values['skills/learn/SKILL.md'];peers=values['extensions/peers/EXTENSION.md'];candidate=arm=='candidate'
 expected={'startup_without_exchange':values['references/sd/workflow.md']+mod+startup+outputs['OPEN'],'idle_open':mod+idle+parts['Delivery authority']+outputs['OPEN'],'idle_merged':mod+idle+parts['Delivery authority']+learn+outputs['MERGED'],'after_archive':mod+learn+learnskill+outputs['archive'],'merge_ask':sum(parts.values())+outputs['merge'],'native_claude':peers,'unsupported':peers,'first_task_opening':peers if candidate else 0,'proactive_paseo':peers+values.get('extensions/paseo/EXTENSION.md',0)+own if candidate else peers,'unlisted_incoming':peers+own if candidate else peers,'gate_reply':peers+own if candidate else peers,'warm_exchange':0,'source_repair':0};assert expected==M['routes'][arm]
for k in ['startup_without_exchange','idle_open','idle_merged','after_archive','merge_ask','warm_exchange','source_repair']:assert M['routes']['base'][k]==M['routes']['candidate'][k]
for k,ceiling in [('native_claude',811),('unsupported',811),('first_task_opening',811),('proactive_paseo',2481),('unlisted_incoming',2191),('gate_reply',2191)]:assert M['routes']['candidate'][k]<=ceiling
previous=json.loads(Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/peers-rules-name-each-host-binding/validation-cycle-1/reading-manifest.json').read_text());changes={k:{'previous':previous['routes']['candidate'][k],'now':v,'delta':v-previous['routes']['candidate'][k]} for k,v in M['routes']['candidate'].items() if v!=previous['routes']['candidate'][k]}
print('Independent full-bundle recount agrees; base/candidate unchanged lifecycle rows equal; all peer routes within accepted ceilings.');print(json.dumps(changes,indent=2));(E/'count-changes.json').write_text(json.dumps(changes,indent=2)+'\n')
