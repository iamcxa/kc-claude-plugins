#!/usr/bin/env python3
"""Independent contract-only reader. Python standard library; no product imports."""
import argparse
import copy
from datetime import datetime
import json
from pathlib import Path

KNOWN = {'ask', 'reask', 'revise', 'answer', 'acted', 'withdraw'}

def instant(value):
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')

def read_inputs(root):
    return [(p.relative_to(root).as_posix(), [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()])
            for p in sorted(root.glob('*/asks.jsonl'))]

def at_clock(files, clock):
    now = instant(clock)
    questions = []
    diagnostics = []
    for filename, events in files:
        states = {}
        for number, event in enumerate(events, 1):
            if instant(event['at']) > now:
                continue
            if 'v' not in event:
                diagnostics.append({'file': filename, 'line': number, 'state': 'unknown', 'reason': 'legacy record'})
                continue
            key = event.get('key')
            if event['v'] > 1:
                # Unknown future version must not be guessed open or answered.
                states[key] = {'state': 'unknown'}
                diagnostics.append({'file': filename, 'line': number, 'key': key, 'state': 'unknown', 'reason': 'future version'})
                continue
            kind = event.get('event')
            if kind not in KNOWN:
                continue
            prior = states.get(key)
            if kind == 'ask':
                if prior is None:
                    states[key] = {'state': 'open', 'ask': event, 'holds': event['holds'], 'interruptions': 1}
                continue
            if prior is None or prior['state'] == 'unknown':
                continue
            if prior['state'] != 'open':
                if kind == 'acted' and prior['state'] == 'answered':
                    prior['state'] = 'done'
                else:
                    diagnostics.append({'file': filename, 'line': number, 'key': key, 'reason': 'ignored event after closure'})
                continue
            if kind == 'reask':
                prior['interruptions'] += 1
            elif kind == 'revise':
                prior['holds'] = event['holds']
            elif kind == 'answer':
                prior['state'] = 'answered'
            elif kind == 'withdraw':
                prior['state'] = 'withdrawn'
            elif kind == 'acted':
                diagnostics.append({'file': filename, 'line': number, 'key': key, 'reason': 'acted without answer ignored'})
        for key, record in states.items():
            if record['state'] != 'open':
                continue
            ask = record['ask']
            since = ask['asked_at']
            elapsed = (now - instant(since if since is not None else ask['at'])).total_seconds() / 60
            questions.append({'key': key, 'by': ask['by'], 'waiting_since': since,
                              'waiting_min': elapsed, 'waiting_bound': 'exact' if since is not None else 'at least',
                              'holds': record['holds'], 'interruptions': record['interruptions'], 'state': 'open'})
    return sorted(questions, key=lambda q: q['key']), diagnostics

def compare_lists(expected, actual):
    """Exact field comparison, plus missing/extra/duplicate key detection."""
    def keyed(rows):
        result = {}
        duplicates = []
        for row in rows:
            key = row['key']
            if key in result:
                duplicates.append(key)
            result[key] = row
        return result, duplicates
    left, ld = keyed(expected)
    right, rd = keyed(actual)
    differences = {'missing': sorted(left.keys() - right.keys()), 'unexpected': sorted(right.keys() - left.keys()),
                   'changed': sorted(k for k in left.keys() & right.keys() if left[k] != right[k]),
                   'expected_duplicates': ld, 'actual_duplicates': rd}
    return {'equal': not any(differences.values()), **differences}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    files = read_inputs(args.input)
    clocks = json.loads((args.input / 'clocks.json').read_text())
    snapshots = []
    for clock in clocks:
        questions, diagnostics = at_clock(files, clock)
        snapshots.append({'clock': clock, 'open': questions, 'diagnostics': diagnostics})
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'output.json').write_text(json.dumps(snapshots, indent=2, ensure_ascii=False) + '\n')
    # Both mutations are derived solely from fixture records and declared clocks.
    opening = next(s for s in snapshots if s['open'])
    removed = opening['open'][0]
    omission = [r for r in opening['open'] if r['key'] != removed['key']]
    closed_key = removed['key']
    answer_time = next(e['at'] for _, es in files for e in es if e.get('key') == closed_key and e.get('event') == 'answer')
    answered = next(s for s in snapshots if s['clock'] == answer_time)
    retention = copy.deepcopy(answered['open']) + [copy.deepcopy(removed)]
    cases = [
        {'name': 'open question omitted', 'clock': opening['clock'], 'mutated_key': closed_key,
         'expected': opening['open'], 'wrong': omission, 'comparison': compare_lists(opening['open'], omission)},
        {'name': 'answered question retained', 'clock': answered['clock'], 'mutated_key': closed_key,
         'expected': answered['open'], 'wrong': retention, 'comparison': compare_lists(answered['open'], retention)}
    ]
    control = compare_lists(opening['open'], copy.deepcopy(opening['open']))
    assert control['equal']
    assert all(not c['comparison']['equal'] for c in cases)
    evidence = {'control': control, 'cases': cases, 'passed': True}
    (args.output / 'counterexamples.json').write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'files': len(files), 'clocks': len(clocks), 'snapshots_with_open': sum(bool(s['open']) for s in snapshots),
                      'open_rows': sum(len(s['open']) for s in snapshots), 'counterexamples_detected': len(cases)}))

if __name__ == '__main__':
    main()
