import concurrent.futures,json,subprocess
from pathlib import Path
v=Path(__file__).parent
rows=json.loads(subprocess.check_output(['gh','pr','list','--repo','iamcxa/kc-claude-plugins','--state','merged','--limit','100','--search','sort:updated-desc','--json','number,mergedAt,mergeCommit,headRefOid'],text=True))
rows=sorted(rows,key=lambda r:r['mergedAt'],reverse=True)[:40]
assert len(rows)==40
def check(row):
 merge=json.loads(subprocess.check_output(['gh','api','repos/iamcxa/kc-claude-plugins/commits/'+row['mergeCommit']['oid']],text=True))
 parent=merge['parents'][0]['sha'];head=row['headRefOid']
 comparison=json.loads(subprocess.check_output(['gh','api','repos/iamcxa/kc-claude-plugins/compare/'+parent+'...'+head],text=True))
 return dict(row,trunk=parent,status=comparison['status'],fires=comparison['status'] in ('diverged','behind'))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(check,rows))
(v/'frequency-40.json').write_text(json.dumps({'method':'Last 40 merged PRs, all types, sorted by mergedAt from the 100 most recently updated merged PRs; compare landed commit first parent to PR head.','rows':results,'sample':len(results),'fired':sum(r['fires'] for r in results)},indent=2)+'\n')
print('Last 40 merged PRs:',sum(r['fires'] for r in results),'triggered of',len(results))
