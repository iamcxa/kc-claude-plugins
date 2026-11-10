import concurrent.futures, json, os, pathlib, subprocess
out=pathlib.Path(__file__).parent
i=json.loads((out/'identity.json').read_text()); root=out/'candidate'
pkg=pathlib.Path(i['package']); wt=pathlib.Path(i['worktree']); state=wt.parent.parent/'docs/dev2/.spacedock-state'; task=state/'counts-name-the-run-that-produced-them.md'
gdir=subprocess.check_output(['git','-C',str(wt),'rev-parse','--absolute-git-dir'],text=True).strip()
base=i['base']; head=i['head']
checks=[
 ('lint',['python3','-B',str(root/'kc-dev-flow-2/scripts/lint-skills.py')],False),
 ('adr',['python3','-B',str(pkg/'scripts/adr_lint.py'),'docs/adr','--since',base,'--require','0072'],True),
 ('comments',['python3','-B',str(pkg/'scripts/comment_ratio.py'),base,head,'--workflow-dir',str(state.parent)],True),
 ('doc-impact',['python3','-B',str(pkg/'scripts/doc_impact.py'),base,head],True),
 ('design',['python3','-B',str(pkg/'scripts/design_surfaces.py'),'check',str(task)],True),
 ('dispatch',['python3','-B',str(pkg/'scripts/dispatch_records.py'),str(task.with_suffix(''))],False),
 ('words',['python3','-B',str(out/'words.py'),str(root),base,str(out)],False),
 ('extra-falsifiers',['python3','-B',str(out/'extra-falsifiers.py')],False),
 ('github-pr',['gh','pr','view','822','--repo','iamcxa/kc-claude-plugins','--json','number,state,isDraft,headRefOid,baseRefOid,mergeable,mergeStateStatus,statusCheckRollup,reviews,comments'],False),
 ('github-review-comments',['gh','api','--paginate','repos/iamcxa/kc-claude-plugins/pulls/822/comments'],False),
]
def run(c):
 name,argv,metadata=c
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',SPACEDOCK_BIN='/Users/kent/.local/bin/spacedock')
 if metadata: env.update(GIT_DIR=gdir,GIT_WORK_TREE=str(root))
 p=subprocess.run(['python3','-B',str(out/'run.py'),name,str(root),*argv],env=env,capture_output=True,text=True)
 return dict(name=name,exit=p.returncode,receipt=str(out/(name+'.json')))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for result in pool.map(run,checks): print(json.dumps(result),flush=True)
