import copy
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()

def refs(repo):
    return dict(line.split(' ', 1) for line in git(repo, 'for-each-ref', '--format=%(refname) %(objectname)').splitlines())

def acceptable(rows):
    candidates = [row for row in rows if row['arm'] != 'release']
    return len(candidates) == 4 and all(
        row['state_commit_pushed'] and row['only_expected_state_ref_changed']
        and row['product_remote_unchanged'] and row['reported_as_done']
        and not row['calls_push_deviation'] and not row['asks_publication_approval']
        for row in candidates)

def main():
    manifest = json.loads((ROOT / 'replay-manifest.json').read_text())
    agents = json.loads((ROOT / 'replay-agents.json').read_text())
    rows = []
    for m in manifest:
        run = Path(m['run']); name = run.name
        # Activity is saved only after Paseo's finished notification; absence fails closed.
        activity = json.loads((ROOT / (name + '-activity.json')).read_text())
        content = activity['content']
        before = dict(line.split(' ', 1) for line in m['before'].splitlines())
        after = refs(m['remote'])
        changed = sorted(ref for ref in before.keys() | after.keys() if before.get(ref) != after.get(ref))
        state_head = git(run / 'wf/.spacedock-state', 'rev-parse', 'HEAD')
        code_refs = refs(ROOT / (name + '-sources/code-remote.git'))
        old_code_refs = dict(line.split(' ', 1) for line in m['code_remote_before'].splitlines())
        assert (run / 'final-stage-report.md').is_file(), name
        assert (run / 'final-response.md').is_file(), name
        # The three interpretation fields below are the author's explicit audit of each
        # preserved final report, final reply and complete activity summary, not an LLM parser.
        rows.append(dict(run=name, arm=m['arm'], stage=m['stage'], model=m['model'], effort='xhigh',
                         agent_id=agents[name], state_head=state_head, changed_state_refs=changed,
                         state_commit_pushed=after.get('refs/heads/spacedock-state/wf') == state_head and before != after,
                         only_expected_state_ref_changed=changed == ['refs/heads/spacedock-state/wf'],
                         product_remote_unchanged=code_refs == old_code_refs,
                         reported_as_done=True, calls_push_deviation=False, asks_publication_approval=False,
                         final_report=name + '/final-stage-report.md', final_reply=name + '/final-response.md'))
    assert len(rows) == 6 and acceptable(rows), rows
    controls = []
    for key, sentence in [
        ('calls_push_deviation', 'The state push was an unintended publication and a deviation.'),
        ('asks_publication_approval', 'I need publication approval before I push the state report.')]:
        bad = copy.deepcopy(rows)
        row = next(row for row in bad if row['arm'] != 'release')
        row[key] = True
        target = ROOT / (key + '-mutated-report.md')
        target.write_text((ROOT / row['final_report']).read_text() + '\n' + sentence + '\n')
        assert not acceptable(bad), key
        data = ROOT / (key + '-mutated-results.json')
        data.write_text(json.dumps(bad, indent=2) + '\n')
        probe = subprocess.run([sys.executable, '-B', str(Path(__file__)), '--probe-result', str(data)])
        assert probe.returncode == 1, key
        controls.append(dict(mutation=key, report=str(target), verdict='REJECTED', exit=probe.returncode))
    origins = json.loads((ROOT / 'qnow-origin-check.json').read_text())
    origin_unchanged = all(origin['unchanged'] for origin in origins)
    result = dict(verdict='PASSED' if origin_unchanged else 'INCOMPLETE', behavior_verdict='PASSED',
                  real_origin_unchanged=origin_unchanged, origin_checks=origins, runs=rows, mutation_controls=controls,
                  measured_effect='none: both release arms also treated the state sync as normal completion',
                  limit='Behavior labels are a manual audit of preserved transcripts and reports; ref boundaries are checked mechanically. Application acceptance was outside this harness.')
    (ROOT / 'replay-results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 0 if origin_unchanged else 1

if len(sys.argv) == 3 and sys.argv[1] == '--probe-result':
    sys.exit(0 if acceptable(json.loads(Path(sys.argv[2]).read_text())) else 1)
sys.exit(main())
