from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,tarfile,io,re,json,hashlib,sys
E=Path('/tmp/peers-validation-730-merge-evidence');W=Path('/tmp/peers-validation-730-merge');B='b8ce84e584cf5c5cb482009d9d08d7316ce2a6ac';BASE=E/'base-source';BASE.mkdir()
archive=subprocess.check_output(['git','-C',str(W),'archive',B,'kc-dev-flow-2','scripts','docs/adr','learning.md'])
with tarfile.open(fileobj=io.BytesIO(archive)) as t:t.extractall(BASE,filter='data')
def run(case):
 name,root=case;done=subprocess.run(['python3','-B',str(E/'fixture-outputs.py'),str(root),str(E/name)],capture_output=True,text=True,cwd=W);(E/(name+'-fixture-run.txt')).write_text(done.stdout+done.stderr);assert done.returncode==0,done.stdout+done.stderr
with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,[('base',BASE),('candidate',W)]))
SD=Path('/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3');startup_text=(SD/'skills/first-officer/references/first-officer-shared-core.md').read_text();idle_text=(SD/'skills/first-officer/references/claude-fo-dispatch.md').read_text()
def section(text,name):
 match=re.search(r'^## '+re.escape(name)+r'\n',text,re.M);assert match,name;tail=text[match.start():];end=re.search(r'^## ',tail[4:],re.M);return tail[:end.start()+4] if end else tail
sd={'startup':section(startup_text,'Startup'),'idle':section(idle_text,'Awaiting Completion')};upstream=Path('/Users/kent/.agents/skills/paseo/SKILL.md').read_text();sha=lambda t:hashlib.sha256(t.encode()).hexdigest()
manifest={'base_sha':B,'head_sha':subprocess.check_output(['git','-C',str(W),'rev-parse','HEAD'],text=True).strip(),'sd_inputs':{k:{'words':len(t.split()),'sha256':sha(t)} for k,t in sd.items()},'upstream_paseo':{'words':len(upstream.split()),'sha256':sha(upstream)},'routes':{}}
paths=['references/sd/workflow.md','references/sd/mods/kc-dev-flow-2.md','extensions/learn/EXTENSION.md','skills/learn/SKILL.md','extensions/peers/EXTENSION.md']
for name,root in [('base',BASE),('candidate',W)]:
 texts={p:(root/'kc-dev-flow-2'/p).read_text() for p in paths}
 if name=='candidate':texts['extensions/paseo/EXTENSION.md']=(root/'kc-dev-flow-2/extensions/paseo/EXTENSION.md').read_text()
 words={p:len(t.split()) for p,t in texts.items()};parts={k:len(section(texts['references/sd/workflow.md'],k).split()) for k in ['Delivery authority','Extensions']};out=json.loads((E/name/'output-words.json').read_text());manifest[name]={'inputs':{p:{'words':words[p],'sha256':sha(t)} for p,t in texts.items()},'sections':parts,'outputs':out};workflow=words['references/sd/workflow.md'];mod=words['references/sd/mods/kc-dev-flow-2.md'];learn=words['extensions/learn/EXTENSION.md'];skill=words['skills/learn/SKILL.md'];peers=words['extensions/peers/EXTENSION.md'];is_new=name=='candidate'
 manifest['routes'][name]={'startup_without_exchange':workflow+mod+len(sd['startup'].split())+out['OPEN'],'idle_open':mod+len(sd['idle'].split())+parts['Delivery authority']+out['OPEN'],'idle_merged':mod+len(sd['idle'].split())+parts['Delivery authority']+learn+out['MERGED'],'after_archive':mod+learn+skill+out['archive'],'merge_ask':sum(parts.values())+out['merge'],'native_claude':peers,'unsupported':peers,'first_task_opening':peers if is_new else 0,'proactive_paseo':peers+words.get('extensions/paseo/EXTENSION.md',0)+len(upstream.split()) if is_new else peers,'unlisted_incoming':peers+len(upstream.split()) if is_new else peers,'gate_reply':peers+len(upstream.split()) if is_new else peers,'warm_exchange':0,'source_repair':0}
assert manifest['base']['inputs']['references/sd/workflow.md']['words']==5565
assert manifest['candidate']['inputs']['references/sd/workflow.md']['words']==5565
(E/'reading-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest['routes'],indent=2))
