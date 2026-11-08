import hashlib,json,pathlib,re,subprocess
O=pathlib.Path('/tmp/observer-validation-a43b537c')
W=pathlib.Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-observer-lists-unasked-merges')
S=pathlib.Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
H='a43b537cd12d69a5ccfde38bf964c6ea35cb0de0'; P='b36fbeeec3a6699c0a82a021dc4ee0142410f6c8'; B='139feeaee7ce037a0c6535568cd6bd103155cbae'
def git(*args): return subprocess.check_output(['git','-C',str(W),*args])
def digest(b):return hashlib.sha256(b).hexdigest()
files=git('diff','--name-only',B,H).decode().splitlines()
expected=['.github/workflows/kc-dev-flow-2-tests.yml','kc-dev-flow-2/scripts/merge_audit.py','kc-dev-flow-2/scripts/test_merge_audit.py','kc-dev-flow-2/skills/observer/SKILL.md']
assert files==expected
changed=git('diff','--name-only',P,H).decode().splitlines()
assert changed==['kc-dev-flow-2/skills/observer/SKILL.md']
hashes={}
for f in files:
 data=(O/'candidate'/f).read_bytes()
 assert data==git('show',H+':'+f),f
 hashes[f]=digest(data)
for f in ['kc-dev-flow-2/references/sd/workflow.md','kc-dev-flow-2/scripts/lint-skills.py']:
 assert git('show',B+':'+f)==git('show',H+':'+f)
repair=S/'observer-lists-unasked-merges/implementation/repair-2026-11-08'
skill=(O/'candidate/kc-dev-flow-2/skills/observer/SKILL.md').read_text()
def block(t):return t[t.index('Run `python3 <package>/scripts/merge_audit.py'):t.index("audit's status.")+len("audit's status.")]
for f in ['skill-first-sample.md','skill-second-sample.md']:assert block((repair/f).read_text())==block(skill)
base_skill=pathlib.Path('/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/skills/observer/SKILL.md').read_bytes()
assert digest(base_skill)=='1f9bf48b899c246c472c575f828847ddf3a0c627389276fb3cc6a77d0130cd7f'
assert base_skill==git('show','kc-dev-flow-2-v0.35.0:kc-dev-flow-2/skills/observer/SKILL.md')
base_report=(S/'observer-lists-unasked-merges/validation/observer-base.md').read_text()
assert not re.search(r'carried:|no ask record:|release: #|sync: #|learning: #',base_report)
live=(O/'replay-live.log').read_text()
assert 'carried: 54 of 82' in live
gaps=set(map(int,re.findall(r'^no ask record: #(\d+)',live,re.M)))
assert gaps=={704,762,774,776,778,784,785,789}
for kind,nums in [('release',[707,717,723,731,739,746,752,760,768]),('sync',[715,718,725,733,741,747,753,761,781]),('learning',[726,782])]:
 assert f'{kind}: '+' '.join('#'+str(n) for n in nums) in live
assert 'no ask record: #785 head 0c38dd60b562' in live
native=json.loads((O/'native-execution.json').read_text())
cmd=native['tool_uses'][0]['input']['command']
audit_cmd=cmd[cmd.index('python3 -I $P/scripts/merge_audit.py'):cmd.index('python3 -I $P/scripts/role_triggers.py')]
assert '|' not in audit_cmd and '; echo "audit exit $?"; cat ' in audit_cmd
assert 'audit exit 1\n' in native['tool_results'][0]['content']
assert json.loads((O/'comparison-fresh.json').read_text())['exit_status_passed']
assert not json.loads((O/'comparison-original-control.json').read_text())['exit_status_passed']
for sample in ['repair-1','repair-2']:assert json.loads((O/('comparison-'+sample+'.json')).read_text())['exit_status_passed']
identity={'candidate':H,'base':B,'parent':P,'worktree':str(W),'export':str(O/'candidate'),'changed_files':files,'repair_changed_files':changed,'sha256':hashes,'exit_capture_block_identical_to_retained_samples':True,'native_agent':'a45b399f-c67f-489c-9298-bd6dd9029a15','native_session':'6e934fe0-9b8f-4a98-b22c-c4c8430e01b3','native_unpiped_immediate_status_verified':True,'base_control_carried_from_validation_1':{'agent':'3e58869e-4f45-437a-a99a-3428ed99482d','skill_sha256':digest(base_skill),'report_sha256':digest(base_report.encode())},'verdict':'PASSED'}
(O/'identity.json').write_text(json.dumps(identity,indent=2))
(O/'repair.diff').write_bytes(git('diff',P,H))
print('Exact candidate, repair-only diff, retained controls, live sets, and native immediate audit exit verified.')

