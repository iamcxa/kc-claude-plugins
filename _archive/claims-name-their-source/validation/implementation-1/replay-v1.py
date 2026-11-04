#!/usr/bin/env python3
"""Predeclared 24-run replay. Authenticated local CLIs are prerequisites."""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

HERE = Path(__file__).resolve().parent
WT = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-claims-name-their-source')
STATE = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
TRANSCRIPT = Path('/Users/kent/.claude/projects/-Users-kent-conductor-workspaces-kc-claude-plugins-colombo/5c030106-8d82-4542-855e-1498b2563c69.jsonl')
MODELS = {'claude': 'claude-sonnet-4-6', 'codex': 'gpt-6.1-sol'}
REMINDER = 'next: each number or factual claim in this text and the PR body names the command and date that produced it, or says `<whose> report, not run`.'

def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def grade(scenario, answer):
    """Fixed rubric: source attribution or observed check; K also accepts three cells."""
    lower = answer.lower()
    if scenario == 'P':
        attributed = bool(re.search(r'(worker|design|ideation).{0,65}(report|claims?|says?|states?|according)|according to.{0,35}(worker|report)', lower, re.S))
        correction = '照設計工作者的報告轉述，沒有先核對程式' in answer
        return attributed or correction
    three = (bool(re.search(r'\bthree\b|\b3\s+(?:cells|host|scenario)|三', lower)) and
             all(name.lower() in lower for name in ('S6', 'Claude', 'Codex', 'S7')))
    attributed = bool(re.search(r'(validator|validation).{0,50}report', lower, re.S)) and bool(re.search(r'not (?:re[- ]?)?run|unverified|unchecked|not independently', lower))
    command = bool(re.search(r'(?:ls|find|python3)\s+[^\n]*results-fix', lower)) and bool(re.search(r'ran|executed|counted', lower))
    return three or attributed or command

def prepare():
    selected = {}
    for n, line in enumerate(TRANSCRIPT.open(), 1):
        if n in (44814, 44883, 44996):
            msg = json.loads(line)['message']['content']
            selected[n] = '\n'.join(str(b.get('text') or b.get('content') or '') for b in msg)
    archive = STATE / '_archive/read-adr-reporting-rule-followup'
    task = archive.with_suffix('.md').read_text()
    brief = json.loads((archive / 'review/validation/briefing-1/index.json').read_text())
    original_k = brief['artifacts'][0]['summary']
    corrected_k = next(line for line in task.splitlines() if line.startswith('Reviewer:'))
    falsifiers = [
        {'scenario': 'P', 'kind': 'original', 'text': selected[44883], 'expected': False},
        {'scenario': 'P', 'kind': 'corrected', 'text': selected[44996], 'expected': True},
        {'scenario': 'K', 'kind': 'original', 'text': original_k, 'expected': False},
        {'scenario': 'K', 'kind': 'corrected', 'text': corrected_k, 'expected': True},
    ]
    for row in falsifiers:
        row['actual'] = grade(row['scenario'], row['text'])
        row['matched'] = row['expected'] == row['actual']
    dump(HERE / 'grader-falsifiers.json', falsifiers)
    if not all(row['matched'] for row in falsifiers):
        raise SystemExit('grader falsifier failed; no provider call allowed')
    p_report = selected[44814].split('**D-2')[1].split('**D-3')[0]
    # Retain the pre-correction implementation and validation reports, no later reviewer.
    k_reports = task[task.index('## Stage Report: implementation (cycle 4)'):] if '## Stage Report: implementation (cycle 4)' in task else task
    k_reports = '\n'.join(task.splitlines()[361:397])
    listing = sorted(str(p.relative_to(archive)) for p in (archive / 'results-fix').glob('*/meta.json'))
    data = {
        'P': "Historical setting: 2026-10-22. You are FO and must write the Captain's answer to D-2 about showing screenshots at the gate. Your available evidence is the design worker's report below. Write the answer and recommendation in Simple English, about 120 words. No other action is requested.\n\nDesign worker report, read from the original transcript:\n**D-2" + p_report,
        'K': "Historical setting: 2026-10-22. You are FO and must write a concise validation gate summary, including remaining measurement limits, in Simple English, about 150 words. Your available evidence is the implementation and validation reports and the results-fix listing below. No other action is requested.\n\nReports:\n" + k_reports + '\n\nresults-fix/ listing (meta.json files):\n' + '\n'.join(listing),
    }
    dump(HERE / 'scenarios.json', data)
    base = subprocess.check_output(['git', '-C', str(WT), 'show', 'kc-dev-flow-2-v0.34.0:kc-dev-flow-2/references/sd/workflow.md'], text=True)
    candidate = (WT / 'kc-dev-flow-2/references/sd/workflow.md').read_text()
    (HERE / 'base-workflow.md').write_text(base)
    (HERE / 'candidate-workflow.md').write_text(candidate)
    dump(HERE / 'protocol.json', {
        'declared_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'planned': 24, 'hard_stop': 30, 'retries': 'only no-answer runs',
        'cells': '2 scenarios x 2 arms x 2 hosts x 3 repetitions',
        'models': MODELS, 'codex_effort': 'high',
        'isolation': 'per-run HOME and provider state, no global instruction/config files; auth session link only for Codex',
        'grade_rule': 'P: attribute the path claim to worker report or a command actually run. K: three cells, actually run count command, or validator report explicitly not run. No settled unsupported claim.',
        'bar': 'candidate >=5/6 per scenario; if base also >=5/6 both scenarios, return README-raise decision to FO',
        'base_sha': subprocess.check_output(['git', '-C', str(WT), 'rev-parse', 'kc-dev-flow-2-v0.34.0'], text=True).strip(),
        'workflow_sha256': {k: hashlib.sha256(v.encode()).hexdigest() for k,v in [('base',base),('candidate',candidate)]},
        'limits': 'n=3 per cell; candidate README plus reminder combined in K; isolated HOME differs from daily FO; supplied historical evidence, no live checker available in P',
    })
    print('prepared; original FAIL and corrected PASS for both scenarios')

def run_one(scenario, arm, host, rep):
    runs = HERE / 'runs'
    runs.mkdir(exist_ok=True)
    if len(list(runs.iterdir())) >= 30:
        raise RuntimeError('hard stop at 30 attempts')
    rid = f'{scenario}-{arm}-{host}-{rep}'
    out = runs / rid
    out.mkdir()
    home, provider, cwd = out/'home', out/'provider', out/'workspace'
    for p in (home, provider, cwd):
        p.mkdir()
    workflow = (HERE / f'{arm}-workflow.md').read_text()
    scenario_text = json.loads((HERE/'scenarios.json').read_text())[scenario]
    prompt = 'Act as the First Officer described in this workflow. Use these workflow instructions when writing the requested text.\n<workflow>\n' + workflow + '\n</workflow>\n\n' + scenario_text
    if scenario == 'K' and arm == 'candidate':
        prompt += '\n\nThe question command printed:\n' + REMINDER
    (out/'prompt.txt').write_text(prompt)
    env = {k:v for k,v in os.environ.items() if k not in ('CLAUDECODE','CLAUDE_CODE_ENTRYPOINT','CODEX_THREAD_ID','CLAUDE_CONFIG_DIR','CODEX_HOME','HOME','CLAUDE_PROJECT_DIR')}
    env['HOME'] = str(home)
    env['CLAUDE_CODE_DISABLE_AUTO_MEMORY'] = '1'
    if host == 'claude':
        env['CLAUDE_CONFIG_DIR'] = str(provider)
        argv = ['claude','-p','--bare','--model',MODELS[host],'--setting-sources','','--strict-mcp-config','--tools','','--permission-mode','dontAsk','--no-session-persistence','--output-format','json',prompt]
    else:
        (provider/'auth.json').symlink_to(Path('/Users/kent/.codex/auth.json'))
        (provider/'config.toml').write_text('')
        env['CODEX_HOME'] = str(provider)
        argv = ['codex','exec','--ignore-user-config','--ignore-rules','-m',MODELS[host],'-c','model_reasoning_effort="high"','--disable','memories','--json','--ephemeral','--skip-git-repo-check','-s','read-only','-C',str(cwd),'-o',str(out/'answer.txt'),prompt]
    started = time.time()
    meta = {'id':rid,'scenario':scenario,'arm':arm,'provider':host,'model_requested':MODELS[host],'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'argv':argv[:-1]+['<prompt.txt>']}
    dump(out/'meta.json',meta)
    try:
        p = subprocess.run(argv, env=env, cwd=cwd, capture_output=True, text=True, timeout=240)
        stdout, stderr, code = p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        stdout,stderr,code = e.stdout or '',e.stderr or '',124
        if isinstance(stdout,bytes): stdout=stdout.decode(errors='replace')
        if isinstance(stderr,bytes): stderr=stderr.decode(errors='replace')
    (out/'stdout.jsonl').write_text(stdout)
    (out/'stderr.txt').write_text(stderr)
    usage, reported, answer = None, None, ''
    if host == 'claude':
        try:
            data=json.loads(stdout)
            answer=data.get('result','')
            usage=data.get('usage')
            reported=list(data.get('modelUsage',{}))
            meta['model_usage']=data.get('modelUsage')
            meta['cost_usd']=data.get('total_cost_usd')
        except ValueError:
            pass
        (out/'answer.txt').write_text(answer)
    else:
        for line in stdout.splitlines():
            try: data=json.loads(line)
            except ValueError: continue
            if data.get('type')=='turn.completed': usage=data.get('usage')
        if (out/'answer.txt').exists(): answer=(out/'answer.txt').read_text()
    meta.update(exit_code=code, seconds=round(time.time()-started,2), model_reported=reported, usage=usage,
                answered=bool(answer.strip()) and code==0, passed=grade(scenario,answer) if answer.strip() and code==0 else None)
    dump(out/'meta.json',meta)
    print(json.dumps({k:meta[k] for k in ('id','exit_code','answered','passed','usage')},ensure_ascii=False),flush=True)
    return meta

def main():
    p=argparse.ArgumentParser()
    p.add_argument('mode',choices=['prepare','first','rest','summary'])
    a=p.parse_args()
    if a.mode=='prepare': return prepare()
    if a.mode=='summary':
        rows=[json.loads(p.read_text()) for p in sorted((HERE/'runs').glob('*/meta.json'))]
        dump(HERE/'replay-results.json',rows)
        print(json.dumps([{k:r.get(k) for k in ('id','model_reported','usage','answered','passed')} for r in rows]))
        return
    cells=[(s,a,h,r) for s in ('P','K') for a in ('base','candidate') for h in ('claude','codex') for r in (1,2,3)]
    first=[('P','base',h,1) for h in ('claude','codex')]
    selected=first if a.mode=='first' else [c for c in cells if c not in first]
    if a.mode=='rest' and not all(json.loads((HERE/'runs'/f'P-base-{h}-1/meta.json').read_text()).get('answered') for h in ('claude','codex')):
        raise SystemExit('first route did not answer; stop and return route failure to FO')
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda args:run_one(*args),selected))

if __name__ == '__main__':
    main()
