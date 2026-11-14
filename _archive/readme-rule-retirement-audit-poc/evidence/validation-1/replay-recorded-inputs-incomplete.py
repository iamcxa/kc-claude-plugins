import json,os,subprocess,sys,shutil
E=sys.argv[1]; SC=os.getcwd()
runs=json.load(open(E+'/implementation-2/runs.json'))
base=SC+'/replay'; shutil.rmtree(base,ignore_errors=True); os.makedirs(base)
os.symlink(SC+'/kc-dev-flow-2', base+'/snapshot/kc-dev-flow-2'.replace('/snapshot/kc-dev-flow-2','')+'snapshot') if False else None
os.makedirs(base+'/snapshot'); os.symlink(SC+'/kc-dev-flow-2', base+'/snapshot/kc-dev-flow-2')
ok=bad=skip=0
for r in runs:
    if 'input_files' not in r or not r['input_files'] or any(k in r['command'] for k in ('number_guards','adr_lint','doc_impact','--since')):
        skip+=1; continue
    for f in r['input_files']:
        p=base+'/'+f['path']; os.makedirs(os.path.dirname(p),exist_ok=True)
        open(p,'w').write(f['text'])
    c=subprocess.run(r['command'],shell=True,cwd=base+'/'+r.get('cwd','.'),capture_output=True,text=True)
    m='OK ' if c.returncode==r['exit_code'] else 'DIFF'
    if m=='OK ': ok+=1
    else: bad+=1
    print(m,r['id'],'recorded',r['exit_code'],'mine',c.returncode)
print('ok',ok,'diff',bad,'skipped',skip)
