from pathlib import Path
import hashlib,json,re,subprocess
OUT=Path(__file__).resolve().parent
cases=[('component-default','repos/iamcxa/kc-claude-plugins/git/matching-refs/tags/kc-dev-flow-2-v',[]),('component-one-per-page','repos/iamcxa/kc-claude-plugins/git/matching-refs/tags/kc-dev-flow-2-v?per_page=1&page=2',[]),('component-paginate','repos/iamcxa/kc-claude-plugins/git/matching-refs/tags/kc-dev-flow-2-v',['--paginate','--slurp']),('all-tags-default','repos/iamcxa/kc-claude-plugins/git/matching-refs/tags/',[]),('all-tags-one-per-page','repos/iamcxa/kc-claude-plugins/git/matching-refs/tags/?per_page=1&page=2',[])]
rows=[]
for name,path,flags in cases:
    args=['gh','api',path,*flags]
    if not flags:args.append('--include')
    run=subprocess.run(args,capture_output=True,text=True,timeout=60)
    if run.returncode:raise RuntimeError(run.stderr)
    headers,body=run.stdout.split('\n\n',1) if not flags else ('',run.stdout)
    data=json.loads(body)
    if flags:
        data=[item for page in data for item in page]
    (OUT/(name+'.json')).write_text(json.dumps(data,indent=2))
    refs=sorted(x['ref'] for x in data)
    row={'case':name,'command':' '.join(args),'count':len(data),'link':[line for line in headers.splitlines() if line.lower().startswith('link:')],'refs_sha256':hashlib.sha256('\n'.join(refs).encode()).hexdigest(),'first':refs[0] if refs else None,'last':refs[-1] if refs else None}
    rows.append(row)
assert rows[0]['refs_sha256']==rows[1]['refs_sha256']==rows[2]['refs_sha256']
assert rows[3]['count']>100 and rows[3]['refs_sha256']==rows[4]['refs_sha256']
assert not any(row['link'] for row in rows)
(OUT/'refs-probe.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
