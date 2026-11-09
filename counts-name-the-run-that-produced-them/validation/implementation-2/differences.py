"""Explain final-pattern replay differences from the original learn scanner."""
import hashlib
import json
from pathlib import Path
import re
import sys

worktree, replay_log = sys.argv[1:]
sys.path.insert(0, str(Path(worktree) / 'kc-dev-flow-2/scripts'))
from count_tokens import COUNT, count_sentences, numbers

old_units = r'(?:cells?|runs?|tests?|files?|findings?|words?|lines?|PRs?|tasks?|commits?|cases?|records?|steps?|rounds?|tokens?|briefings?|attempts?|skips?|passes|passed|failures?|comments?|items?|entries|sessions?|times)'
old_pattern = re.compile(rf'\b(\d[\d,]*)\s*(?:of|/)\s*(\d[\d,]*)\b|\b(\d[\d,]*)\s+(?:\w+\s)?{old_units}\b')
stores = [Path('/Users/kent/Project/kc-claude-workspace/kc-claude-plugins/.git'),
          *[Path('/Users/kent/conductor/repos') / repo / '.git' for repo in ('subspace-relay','subspace-web','qnow','subspace-v0')]]
differences = []
for store in stores:
    for path in sorted(store.glob('kc-dev-flow-2/learning/*/record.json')):
        record=json.loads(path.read_text())
        if record.get('state') != 'completed':
            continue
        for decision in record['evaluation']['decisions']:
            if decision['action'] != 'add':
                continue
            text=decision['entry']['Evidence']
            before=[m[0] for m in old_pattern.finditer(text)]
            after=[m[0] for sentence,_ in count_sentences(text) for m in COUNT.finditer(sentence)]
            assert not any('2, round' in token for token in after)
            refs=numbers('\n'.join(decision['evidence']))
            missing=[dict(sentence=s, missing=sorted(n-refs)) for s,n in count_sentences(text) if n-refs]
            if bool(before) != bool(after) or missing or any('2, round' in token for token in before):
                differences.append(dict(job=path.parent.name, record_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                        before=before, after=after, missing=missing))
print(json.dumps(dict(comma_defect_absent=True, differences=differences),indent=2))
