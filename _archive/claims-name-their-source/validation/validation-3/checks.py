import datetime, json, os, pathlib, shlex, subprocess
C=pathlib.Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-claims-name-their-source/.context/claims-validation-3")
E=pathlib.Path("/tmp/opencode/claims-validation-3")
P=pathlib.Path("/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0")
S=pathlib.Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state")
WF="/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2"
env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
jobs=[
('lint',['python3','-B','kc-dev-flow-2/scripts/lint-skills.py']),
('adr-lint',['python3',str(P/'scripts/adr_lint.py'),'docs/adr','--since','origin/main','--require','0055']),
('doc-impact',['python3',str(P/'scripts/doc_impact.py'),'origin/main','69f4988612d17c5524887f99c872a0ef384d05c9']),
('comment-ratio',['python3',str(P/'scripts/comment_ratio.py'),'origin/main','69f4988612d17c5524887f99c872a0ef384d05c9','--workflow-dir',WF]),
('number-guards-main',['python3',str(P/'scripts/number_guards.py'),'check','--repo',str(C),'--workflow-dir',WF,'--task',str(S/'claims-name-their-source.md'),'--base','2bda2e98304261d46b0ae7205a29ddc9038d2b4d','--head','69f4988612d17c5524887f99c872a0ef384d05c9']),
('design-surfaces',['python3',str(P/'scripts/design_surfaces.py'),'check',str(S/'claims-name-their-source.md')]),
('dispatch-records',['python3',str(P/'scripts/dispatch_records.py'),str(S/'claims-name-their-source')]),
('focused-tests',['python3','-B','-m','unittest','test_delivery_gate.DeliveryGateTests.test_claim_source_reminder_on_pass_hold_and_unreadable_input','test_delivery_gate.QuestionTests.test_claim_source_reminder_on_pass_hold_and_unreadable_input']),
]
rows=[]
for name,cmd in jobs:
    cwd=C/'kc-dev-flow-2/scripts' if name=='focused-tests' else C
    p=subprocess.run(cmd,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (E/(name+'.log')).write_text(p.stdout)
    row=dict(name=name,argv=cmd,command=shlex.join(cmd),cwd=str(cwd),date=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit=p.returncode)
    rows.append(row)
    print(name,p.returncode,flush=True)
(E/'checks.json').write_text(json.dumps(rows,indent=2)+'\n')

