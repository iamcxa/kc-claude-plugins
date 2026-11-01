from pathlib import Path
import json,re,copy
S=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/model-roster-per-repo')
O=Path('/tmp/roster-validation2-a8536dc5')
questions=[json.loads(x) for x in (S/'adoption-trial/question-receipts.jsonl').read_text().splitlines()]
commands=[json.loads(x) for x in (S/'adoption-trial/fo-commands.jsonl').read_text().splitlines()]
results=[]
def consent_before_write(qs,case):
 marker='="Accept"' if case=='accept' else '="Customize"'
 answers=[q['ts'] for q in qs if q.get('ts') and marker in q.get('result','') and not q.get('is_error')]
 writes=[x['ts'] for x in commands if f'n={case}; mkdir -p $T/$n/.dev2' in x['command']]
 assert answers and writes and min(answers)<min(writes),'explicit answer must precede write'
for c in ('accept','customize'):consent_before_write(questions,c)
try:
 consent_before_write([q for q in questions if 'result' not in q or '="Accept"' not in q['result']],'accept')
except AssertionError as e:results.append(dict(criterion='AC-7',mutation='keep displayed/preselected Accept and write, remove explicit answer',detected=True,reason=str(e),boundary='receipt audit only; no new host dialog'))
else:raise AssertionError('lost consent was accepted')
asked=[q for q in questions if 'asked' in q];assert len(asked)==7
assert any(q.get('is_error') and q.get('ts') for q in questions)
assert any('cancel unanswered' in x['command'] and 'cmp $T/$n.before $T/$n.after' in x['command'] and '[ -e $T/$n/.dev2 ]' in x['command'] for x in commands)
actual=(S/'adoption-trial/validation-2-spawn-command.txt').read_text()
def launch_matches(command,runtime):
 assert '--provider codex/gpt-6-astra --thinking high --mode auto-review' in command,'explicit effort/model/mode required'
 assert '--new-workspace local --cwd "$RW/.worktrees/spacedock-ensign-$v"' in command,'assigned workspace placement required'
 assert runtime['Provider']=='codex' and runtime['Model']=='gpt-6-astra' and runtime['Thinking']=='high' and runtime['Mode']=='auto-review'
 assert runtime['Cwd'].endswith('/.worktrees/spacedock-ensign-model-roster-per-repo')
 assert '> /tmp/v-$v.out 2>&1 && paseo agent run' in command,'successful build must lead directly to spawn'
 assert '"$(tail -1 /tmp/v-$v.out)"' in command,'forward generated prompt'
current=json.loads((O/'runtime-validation2.json').read_text());launch_matches(actual,current)
for name,changed in [('drop-explicit-effort',actual.replace('--thinking high ','')),('wrong-workspace',actual.replace('--new-workspace local --cwd','--new-workspace local --wrong-cwd')),('post-build-check',actual.replace('2>&1 && paseo agent run','2>&1 && grep -q FAIL /tmp/v-$v.out && paseo agent run'))]:
 try:launch_matches(changed,current)
 except AssertionError as e:results.append(dict(criterion='AC-8',mutation=name,detected=True,reason=str(e),boundary='saved invocation/runtime consistency audit; no child launched'))
 else:raise AssertionError(name)
for name,effort in [('runtime-astra-high.json','high'),('runtime-astra-xhigh.json','xhigh')]:
 r=json.loads((O/name).read_text());assert (r['Provider'],r['Model'],r['Thinking'],r['Mode'])==('codex','gpt-6-astra',effort,'auto-review')
record=(S/'dispatch/validation-2.md').read_text();assert 'Roster: absent; source README default' in record
assert 'implementation-1.md:' in record and 'implementation-2.md:' in record and 'family: same-family: openai' in record
prompt=Path('/tmp/v-model-roster-per-repo.out').read_text().splitlines()[-1]
expected='Skill(skill="spacedock:ensign"); then Read /tmp/spacedock-dispatch/5c030106-8d82-4542-855e-1498b2563c69-spacedock-ensign-model-roster-per-repo-validation.md and treat its content as your assignment.'
assert prompt==expected
results.append(dict(criterion='AC-8',check='retained builder output equals received initial pointer prompt',passed=True))
(O/'receipt-audit.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
