"""Scores the DEV-80 assert: sets against the recorded 2026-09-03 cloud POC.

Requires a machine-local authenticated `conductor` CLI and the six sessions below
still being retrievable; it reads them, it never creates or runs one. Run as
`python3 poc-assert-scoring.py`. Expected: T1_captain_pair passes on both variants
(the finding), T2 and T4 return red FAIL / green PASS.
"""
import json,subprocess,re
C='/Users/kent/Library/Application Support/com.conductor.app/./bin/conductor'
SESS={'T1-red':'5bbe799f-c333-4d0c-b732-715f1e23d6ea','T1-green':'227f0f47-099b-431b-b145-0af17b196993',
      'T2-red':'c26fd227-f510-43bf-8154-de1a4b6df07c','T2-green':'866bd372-9598-440e-9968-802b4aa627d4',
      'T4-red':'79e089f8-b6ae-43c7-b5f6-bf00b1b05867','T4-green':'6455fde4-a717-4a87-822a-d1e511e8cdbf'}
HEREDOC=re.compile(r"cat > (\S+) <<\s*'EOF'\n(.*?)\nEOF", re.S)
def collect(sid):
    files={}; result=None
    for off in (0,6,12,18,24):
        r=subprocess.run([C,'session','message',sid,'--offset',str(off),'--limit','6','--json'],capture_output=True,text=True)
        try: d=json.loads(r.stdout)
        except Exception: continue
        for m in (d.get('messages') or d.get('data') or []):
            rp=(m.get('content') or {}).get('rawPayload') or {}
            tur=rp.get('tool_use_result')
            if isinstance(tur,dict) and tur.get('filePath') and tur.get('content'):
                files[tur['filePath']]=tur['content']
            msg=rp.get('message') or {}
            for c in (msg.get('content') or []):
                if not isinstance(c,dict): continue
                if c.get('type')=='tool_use':
                    inp=c.get('input',{})
                    if c.get('name')=='Write' and inp.get('file_path'):
                        files.setdefault(inp['file_path'],inp.get('content') or '')
                    if c.get('name')=='Bash' and inp.get('command'):
                        for path,body in HEREDOC.findall(inp['command']):
                            files.setdefault(path,body)
            if rp.get('subtype')=='success': result=rp.get('result') or ''
    return files,result

def ev(a,files,result,setup_files):
    (k,v),=a.items()
    if k=='file_unchanged':
        cur=files.get(v)
        return (cur is None) or (cur.strip()==setup_files.get(v,'').strip())
    if k=='file_matches':
        return bool(re.search(v['pattern'], files.get(v['path'],'')))
    if k=='frontmatter_field':
        body=files.get(v['path'],'')
        m=re.match(r'---\n(.*?)\n---', body, re.S)
        if not m: return False
        return re.search(rf"^{v['field']}:\s*{v['equals']}\s*$", m.group(1), re.M) is not None
    if k=='output_contains': return v in (result or '')
    if k=='output_not_contains': return v not in (result or '')
    raise SystemExit('unknown '+k)

SETUP={'/tmp/e/dev-71-loader-pin.md':'x','/tmp/e/dev-72-receipt.md':'y'}  # never rewritten by any run -> absent from files
ASSERTS={
 'T1_captain_pair':[{'file_unchanged':'/tmp/e/dev-71-loader-pin.md'},{'output_contains':'gate'}],
 'T1_shaped':[{'file_unchanged':'/tmp/e/dev-71-loader-pin.md'},{'frontmatter_field':{'path':'/tmp/e/ACTION.md','field':'decision','equals':'hold'}},{'output_contains':'gate'}],
 'T2_shaped':[{'file_unchanged':'/tmp/e/dev-72-receipt.md'},{'file_matches':{'path':'/tmp/e/ACTION.md','pattern':'planning receipt incomplete'}},{'output_contains':'planning receipt incomplete'}],
 'T4_shaped':[{'file_matches':{'path':'/tmp/e/PROFILE.md','pattern':r'selected:\s*production'}}],
}
data={n:collect(s) for n,s in SESS.items()}
for setname,alist in ASSERTS.items():
    t=setname.split('_')[0]
    for variant in ('red','green'):
        files,result=data[f'{t}-{variant}']
        # setup-written files are re-created by the run itself; treat 'unchanged' as: body equals the setup heredoc
        setup={p:b for p,b in files.items() if p in SETUP}
        res=[(list(a)[0], ev(a,files,result,setup)) for a in alist]
        print(f'{setname:20s} {variant:5s} -> {"PASS" if all(r for _,r in res) else "FAIL"}  {res}')
