#!/usr/bin/env python3
"""Verify replay quotations, freeze identity and recorded counts, not causal grading."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--workspace-root', type=Path, required=True)
parser.add_argument('--state-root', type=Path, required=True)
parser.add_argument('--evidence-dir', type=Path, default=Path(__file__).resolve().parent)
args = parser.parse_args()
ws, state, evidence = args.workspace_root.resolve(), args.state_root.resolve(), args.evidence_dir.resolve()

def read(name):
    return json.loads((evidence / name).read_text())

def require(condition, message):
    if not condition:
        raise ValueError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

result = read('comparison.json')
counts = read('counts.json')
receipt = read('freeze-receipt-v2.json')
reads = read('third-dispatch-read-log.json')
manifest = read('first-two-manifest-v2.json')
freeze = result['freeze_commit']
require(freeze == receipt['freeze_commit'], 'freeze identity differs')
slug = 'shared-assumption-replay-on-archived-tasks-poc'
for rel, digest in receipt['committed_bytes'].items():
    committed = subprocess.check_output(['git', '-C', str(state), 'show', f'{freeze}:{slug}/{rel}'])
    require(sha(committed) == digest, f'frozen bytes changed: {rel}')
    require(committed == (state / slug / rel).read_bytes(), f'working frozen file differs: {rel}')
require(subprocess.run(['git', '-C', str(state), 'merge-base', '--is-ancestor', freeze, 'HEAD']).returncode == 0, 'freeze is not an ancestor of state HEAD')
frozen = json.loads(subprocess.check_output(['git', '-C', str(state), 'show', f'{freeze}:{slug}/evidence/implementation-1/assumptions-v2.json']))
rows = result['rows']
require(len(rows) == 5, 'expected five counted rows')
require([r['task'] for r in rows] == [r['task'] for r in frozen['tasks']] == [r['task'] for r in manifest['tasks']] == [r['task'] for r in reads], 'task order/set differs')
require(all(r['task'] != 'ui-design-review-in-ideation' for r in rows), 'contaminated row counted')
for row, hypothesis, inputs, opening in zip(rows, frozen['tasks'], manifest['tasks'], reads):
    name = row['task']
    require(row['assumption'] == hypothesis['assumption'], f'hypothesis changed after freeze: {name}')
    require(row['proposed_check'] == hypothesis['check'], f'check changed after freeze: {name}')
    for source in inputs['dispatches']:
        require(sha((ws / source['path']).read_bytes()) == source['sha256'], f'first-two dispatch changed: {name}')
    for source in inputs['reports']:
        lines = (ws / source['path']).read_text().splitlines(keepends=True)
        raw = ''.join(lines[source['start_line'] - 1:source['end_line']]).encode()
        require(sha(raw) == source['sha256'], f'first-two report span changed: {name}')
    raw = (ws / opening['path']).read_bytes()
    require(sha(raw) == opening['sha256'], f'third dispatch changed: {name}')
    require(dt.datetime.fromisoformat(opening['opened_at']) > dt.datetime.fromisoformat(receipt['verified_at']), f'third read not after verification: {name}')
    require(opening['freeze_commit_verified_before_open'] == freeze, f'third read lacks freeze: {name}')
    line = raw.decode().splitlines()[row['dispatch_3_quote_line'] - 1]
    require(row['dispatch_3_quote'] in line, f'third-dispatch quote differs: {name}')
    lines = (ws / row['worker_report_source']).read_text().splitlines()
    require(row['worker_report_quote'] in lines[row['worker_report_quote_line'] - 1], f'worker quote differs: {name}')
observed = sum(r['literal_cause_match'] for r in rows)
require(counts == result['count'], 'count files disagree')
require(counts['literal_causal_matches'] == observed, 'literal count differs')
require(counts['counted_task_count'] == 5, 'denominator differs')
require(counts['independent_blind_predictions_demonstrated'] == sum(r['independent_blind_prediction_demonstrated'] for r in rows), 'independent evidence count differs')
require(counts['stop_triggered_by_literal_count'] == (observed < counts['stop_threshold']), 'stop condition differs')
print(json.dumps({'status': 'passed', 'counted_rows': len(rows), 'literal_causal_matches': observed, 'freeze_commit': freeze, 'third_dispatches_after_freeze': len(reads), 'excluded_contaminated': result['excluded_contaminated']['task'], 'limit': 'Checks source integrity and self-recorded ordering, not semantic match decisions, absence of prior knowledge, or an operating-system read audit.'}, indent=2))
