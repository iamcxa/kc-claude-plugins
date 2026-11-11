from pathlib import Path
import subprocess,shlex,os,re,json,time,sys,hashlib
WT=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-story-done-reports-release-remaining-dev2');OUT=Path('/tmp/opencode-story-done-round5');SD=Path('/tmp/opencode-story-done-round4/.sd-plugin-root');PIN='4d158a484ec73e184861067f8ed1e20087fdc26a';HEAD='01d23393ebe5bfd63d8bcafc01859c3b146021d2'
assert subprocess.check_output(['git','-C',str(WT),'rev-parse','HEAD'],text=True).strip()==HEAD
assert subprocess.check_output(['git','-C',str(SD),'rev-parse','HEAD'],text=True).strip()==PIN
workflow=WT/'.github/workflows/kc-dev-flow-2-tests.yml';source=workflow.read_text();commands=[m[1] for line in source.splitlines() if (m:=re.match(r'\s+run: (.*python3 kc-dev-flow-2/.*)',line))]
assert len(commands)==28,len(commands)
binary=subprocess.check_output(['which','spacedock'],text=True).strip()
info={'head':HEAD,'workflow_sha256':hashlib.sha256(workflow.read_bytes()).hexdigest(),'spacedock_root':PIN,'spacedock':subprocess.check_output([binary,'--version'],text=True),'python':sys.version,'platform':sys.platform,'suite_count':len(commands),'scope':'local replay of hosted Python commands; not a hosted CI run'};(OUT/'runtime.json').write_text(json.dumps(info,indent=2)+'\n')
results=[]
for n,command in enumerate(commands,1):
 argv=shlex.split(command);env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
 if argv[0].startswith('SPACEDOCK_BIN='):env['SPACEDOCK_BIN']=binary;argv=argv[1:]
 argv=[str(SD) if a=='$GITHUB_WORKSPACE/.sd-plugin-root' else a for a in argv]
 log=OUT/(f'{n:02d}-'+Path(argv[1]).stem+'.log');start=time.monotonic()
 with log.open('w') as f:
  try:p=subprocess.run(argv,cwd=WT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900);code=p.returncode
  except subprocess.TimeoutExpired:code=124;f.write('\nRunner timeout after 900 seconds\n')
 content=log.read_text();count=re.search(r'Ran (\d+) tests? in',content);skip=re.search(r'OK \(skipped=(\d+)\)',content)
 result={'name':Path(argv[1]).name,'status':'passed' if code==0 else 'failed','file':str(log),'message':f'exit {code}'+(f'; {count[1]} tests' if count else '')+(f'; {skip[1]} skipped' if skip else ''),'command':command,'argv':argv,'exit':code,'seconds':round(time.monotonic()-start,3)}
 results.append(result);(OUT/'hosted-suites.json').write_text(json.dumps(results,indent=2)+'\n');print(f'{n}/{len(commands)} {result["name"]}: {result["message"]}',flush=True)
assert subprocess.check_output(['git','-C',str(WT),'rev-parse','HEAD'],text=True).strip()==HEAD
assert not subprocess.check_output(['git','-C',str(WT),'status','--porcelain'],text=True).strip()
failed=[r for r in results if r['exit']];print(f'{len(results)-len(failed)}/{len(results)} local workflow commands passed',flush=True);sys.exit(bool(failed))
