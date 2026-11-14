"""AC-1 probe on the throwaway: one task per case; real steps CLI, the question path's inspect_steps with the
validation report, the Asked command in fresh bash and zsh, a guarded state commit, and a byte scan.
usage: ac1.py OVERLAY_SCRIPTS CASE(tilde|absolute|mixed)   (run with HOME and KC_DEV2_IDENTIFIERS of setup.sh)"""
import json, os, subprocess, sys
from pathlib import Path
pkg, case = Path(sys.argv[1]), sys.argv[2]
sys.path.insert(0, str(pkg)); import delivery_gate as dg
home = Path.home(); state = home / 'ws/state'; task = 'tw-' + case; folder = state / task
def form(p, tilde): return '~/' + str(p.relative_to(home)) if tilde else str(p)
script = folder / 'evidence/validation-1/acceptance.py'
report_tilde = case == 'tilde'; asked_tilde = case in ('tilde', 'mixed')
cmd = lambda tilde: f'python3 {form(script, tilde)} {form(home / "ws/repo", tilde)}'
script.parent.mkdir(parents=True)
script.write_text('import sys, pathlib\nassert pathlib.Path(sys.argv[1]).is_dir()\nprint("1 PASS")\n')
(folder / 'captain-steps').mkdir()
(state / f'{task}.md').write_text(f'---\ntitle: tw\nstatus: validation\n---\n\n## Stage Report: validation\n\n- DONE: acceptance script\n\n```sh\n{cmd(report_tilde)}\n```\n')
message = f'Decide: merge? Run this first:\n\n```sh\n{cmd(asked_tilde)}\n```\n\nCaptain steps: captain-steps/1.md\n'
(home / f'question-{case}.md').write_text(message)
rec = folder / 'captain-steps/1.md'
rec.write_text(f'Candidate: none\n\n### Step 1\nAsked: {cmd(asked_tilde)}\nRan: that command exactly, a fresh shell, 2026-11-14T10:00:00Z, exit 0\nObserved: 1 PASS; output in captain-steps/1-output.log\nOnly he can: the merge decision — his delivery approval\n')
(folder / 'captain-steps/1-output.log').write_text('1 PASS\n')
out = {}
p = subprocess.run([sys.executable, '-B', str(pkg / 'delivery_gate.py'), 'steps', str(rec), '--text-file', str(home / f'question-{case}.md')], capture_output=True, text=True)
out['steps_cli_exit'] = p.returncode; out['steps_cli_last'] = (p.stdout + p.stderr).strip().splitlines()[-1][:120]
report = (dg.VALIDATION_SECTION.findall((state / f'{task}.md').read_text()) or [''])[-1]
problems, *_ = dg.inspect_steps(rec, message, folder, report)
out['question_path_problems'] = [x[:90] for x in problems]
asked = cmd(asked_tilde)
for shell in (['bash', '--noprofile', '--norc', '-c'], ['zsh', '-f', '-c']):
    r = subprocess.run(['env', '-i', f'HOME={home}', 'PATH=/usr/bin:/bin', *shell, asked], capture_output=True, text=True)
    out[shell[0] + '_fresh_exit'] = r.returncode
briefing = folder / 'review/validation/briefing-1/index.json'; briefing.parent.mkdir(parents=True)
briefing.write_text(json.dumps({'question': message}, ensure_ascii=False) + '\n')  # stands in for the stored question bytes
subprocess.run(['git', '-C', str(state), 'add', f'{task}.md', task], check=True)
c = subprocess.run(['git', '-C', str(state), 'commit', '-q', '-m', f'state: {task}', '--', f'{task}.md', task], capture_output=True, text=True)
out['commit_exit'] = c.returncode
out['guard_lines'] = [l.replace(str(home), '<HOME>')[:110] for l in c.stderr.splitlines() if 'state guard' in l]
blob = subprocess.run(['git', '-C', str(state), 'grep', '-c', '-F', str(home), 'HEAD', '--', task, f'{task}.md'], capture_output=True, text=True)
out['home_hits_at_HEAD'] = blob.stdout.strip().count('\n') + (1 if blob.stdout.strip() else 0)
out['HEAD_subject'] = subprocess.run(['git', '-C', str(state), 'log', '-1', '--format=%s'], capture_output=True, text=True).stdout.strip()
if c.returncode:
    subprocess.run(['git', '-C', str(state), 'reset', '-q', '--', f'{task}.md', task])
print(json.dumps({'case': case, **out}, indent=1, ensure_ascii=False))
