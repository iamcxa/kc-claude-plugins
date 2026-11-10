from pathlib import Path
import hashlib,json,re,shutil,subprocess
p=Path(__file__).parent
required=['suite-candidate','suite-merged','lint','adr','comments','design','dispatch','numbers-refreshed','words','mutations','learn-replay','gate-replay','probes','extra-falsifiers-corrected','acceptance-published-path','github-pr-refreshed','github-comments-refreshed']
checks=[]
for name in required:
 d=json.loads((p/(name+'.json')).read_text())
 assert d['exit']==0,(name,d['exit'])
 assert hashlib.sha256((p/d['log']).read_bytes()).hexdigest()==d['sha256'],name
 checks.append(dict(name=name,exit=d['exit'],log=d['log'],started=d['started'],ended=d['ended'],sha256=d['sha256']))
suites={}
for name in ['suite-candidate','suite-merged']:
 text=(p/(name+'.log')).read_text()
 suites[name]=dict(tests=int(re.findall(r'Ran (\d+) tests?',text)[-1]),skipped=int(re.findall(r'OK \(skipped=(\d+)\)',text)[-1]))
wt='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-counts-name-the-run-that-produced-them'
ident=json.loads((p/'identity.json').read_text())
assert subprocess.check_output(['git','-C',wt,'rev-parse','HEAD'],text=True).strip()==ident['head']
assert not subprocess.check_output(['git','-C',wt,'status','--porcelain'],text=True)
for entry in subprocess.check_output(['git','-C',wt,'ls-tree','-rz',ident['head'],'kc-dev-flow-2','docs/adr']).split(b'\0'):
 if not entry:continue
 meta,name=entry.split(b'\t');mode,kind,sha=meta.split()
 if kind!=b'blob':continue
 raw=(p/'candidate'/name.decode()).read_bytes()
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==sha.decode(),name
assert json.loads((p/'github-pr-refreshed.log').read_text())['headRefOid']==ident['head']
verification=dict(identity=ident,checks=checks,suites=suites,product_clean=True,candidate_bytes_unchanged=True,verdict='REJECTED pending F1 compatibility disposition',merge_main_repair='not needed for the inspected merged tree',findings='findings.json')
(p/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
a=suites['suite-candidate'];b=suites['suite-merged']
line=f"2026-11-10 UTC: SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p 'test_*.py' exits 0 on both exports: candidate Ran {a['tests']} tests, OK (skipped={a['skipped']}); merged Ran {b['tests']} tests, OK (skipped={b['skipped']}) (suite-candidate.json/.log, suite-merged.json/.log). merge-tree of current main {ident['main']} and the candidate exits 0, tree {ident['merge_tree']}; no merge-main repair is needed on these bytes."
r=p/'stage-report.md';r.write_text(r.read_text().replace('SUITE_UPDATE',line))
r=p/'README.md';r.write_text(r.read_text()+'\n## Final suite and verdict\n\n'+line+'\n\nREJECTED pending F1 compatibility disposition. All current mechanical acceptance checks pass; the formal verdict holds the unaccepted ordinal-reference compatibility cost. verification.json checks every accepted producer exit and output hash, the unchanged product branch and exported source bytes.\n')
f=p/'acceptance-results.json';rows=json.loads(f.read_text());rows[3].update(status='passed',note='Both full suites exit 0; no merge-main repair indicated',evidence='suite-candidate.json/.log; suite-merged.json/.log');f.write_text(json.dumps(rows,indent=2)+'\n')
target=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/counts-name-the-run-that-produced-them/validation/validation-1')
for f in p.iterdir():
 if f.is_file() and f.suffix in {'.py','.sh','.md','.log','.json','.patch'} and not f.name.endswith('-running.json'):
  shutil.copy2(f,target/f.name)
manifest={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(target.iterdir()) if f.is_file() and f.name!='evidence-manifest.json'}
(target/'evidence-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(verification))
